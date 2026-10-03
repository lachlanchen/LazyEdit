import {randomUUID} from 'node:crypto';
import {realpathSync} from 'node:fs';
import {sep} from 'node:path';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {digest, fail} from '../studio/auth.mjs';

const exec = promisify(execFile);
const actions = new Set(['process','publish','proxy','transcribe','polish-subtitles',
  'subtitle-correction','caption','metadata','cover','keyframes','translate','burn-subtitles']);
export const processingAction = (path,method) => {
  const m = /^\/api\/videos\/(\d+)\/([a-z-]+)$/.exec(path.split('?')[0]);
  return method==='POST' && m && actions.has(m[2]) ? {videoId:Number(m[1]),action:m[2]} : null;
};
export function processingLimit(value) {
  if(value==='owner')return null;
  if(!['0','10','60','150'].includes(value))fail(503,'Processing allowance unavailable');
  return Number(value);
}
export function processingPeriod(now=Date.now()) {
  const d=new Date(now),year=d.getUTCFullYear(),month=d.getUTCMonth();
  return {id:`${year}-${String(month+1).padStart(2,'0')}`,resetsAt:Date.UTC(year,month+1,1)};
}

// One private workspace ledger; no client duration, plan or entitlement is used.
export class ProcessingMeter {
  constructor(db,root,probe) {
    this.db=db;this.root=realpathSync(root);this.busy=new Set();
    this.probe=probe|| (async path=> {
      const {stdout}=await exec('ffprobe',['-v','error','-show_entries','format=duration',
        '-of','default=noprint_wrappers=1:nokey=1',path],{timeout:30000,maxBuffer:4096});
      return Number(stdout.trim());
    });
    db.exec(`CREATE TABLE IF NOT EXISTS processing_usage (
      id TEXT PRIMARY KEY, period TEXT, fingerprint TEXT, milliseconds INTEGER,
      state TEXT, response TEXT, created INTEGER)`);
  }
  usage(limit,now=Date.now()) {
    const period=processingPeriod(now),used=this.db.prepare('SELECT coalesce(sum(milliseconds),0) n FROM processing_usage WHERE period=?').get(period.id).n;
    return {period:period.id,resetsAt:period.resetsAt,limitMinutes:limit,usedMinutes:used/60000,
      remainingMinutes:limit===null?null:Math.max(0,limit-used/60000),basis:'source duration per requested processing run'};
  }
  async run(path,method,data,dispatch,context) {
    const operation=processingAction(path,method);
    if(!operation)return dispatch(path,method,data);
    const limit=processingLimit(context?.limit);
    if(limit===null)return dispatch(path,method,data);
    const key=context.key;
    if(key!==undefined&&(typeof key!=='string'||!key||key.length>128))fail(400,'Invalid Idempotency-Key');
    const id=key?digest(key+'\n'+path):randomUUID(), fingerprint=digest(JSON.stringify({path,data}));
    const prior=this.db.prepare('SELECT * FROM processing_usage WHERE id=?').get(id);
    if(prior){
      if(prior.fingerprint!==fingerprint)fail(409,'Idempotency conflict');
      if(prior.response)return JSON.parse(prior.response);
      fail(409,'Processing submission requires reconciliation; check Activity before retrying');
    }
    // Serialize quote + dispatch for the same video so a second publish sees
    // the accepted queue entry and cannot reserve it twice under another key.
    if(this.busy.has(operation.videoId))fail(409,'This video is being submitted. Check Activity');
    this.busy.add(operation.videoId);
    let dispatched=false;
    try {
      const quote=await dispatch(`/api/videos/${operation.videoId}/processing-quote`,'POST',{action:operation.action,request:data||{}});
      if(quote.requiresProcessing===false){dispatched=true;return await dispatch(path,method,data);}
      if(quote.requiresProcessing!==true)fail(502,'Processing estimate unavailable');
      const video=await dispatch(`/api/videos/${operation.videoId}`,'GET');
      let file;
      try {file=realpathSync(video.file_path);}catch{fail(409,'Source video unavailable');}
      if(!file.startsWith(this.root+sep))fail(403,'Source must belong to this workspace');
      const seconds=await this.probe(file);
      if(!Number.isFinite(seconds)||seconds<=0)fail(409,'Source duration unavailable');
      const milliseconds=Math.ceil(seconds*1000),period=processingPeriod();
      this.db.exec('BEGIN IMMEDIATE');
      try {
        const used=this.db.prepare('SELECT coalesce(sum(milliseconds),0) n FROM processing_usage WHERE period=?').get(period.id).n;
        if(used+milliseconds>limit*60000) {
          throw Object.assign(Error(`Monthly processing allowance exceeded (${limit} source-video minutes). Reuse a finished run or wait for the next UTC month.`),{status:429,quotaRejected:true});
        }
        this.db.prepare('INSERT INTO processing_usage VALUES(?,?,?,?,?,?,?)').run(id,period.id,fingerprint,milliseconds,'dispatching',null,Date.now());
        this.db.exec('COMMIT');
      }catch(error){this.db.exec('ROLLBACK');throw error;}
      try {
        dispatched=true;
        const result=await dispatch(path,method,data);
        this.db.prepare('UPDATE processing_usage SET state=?,response=? WHERE id=?').run('accepted',JSON.stringify(result),id);
        return result;
      }catch(error){
        // A definite upstream rejection did not start work. Timeouts/5xx may
        // have started it: keep the reservation, never blindly replay them.
        if(error.status>=400&&error.status<500)this.db.prepare('DELETE FROM processing_usage WHERE id=?').run(id);
        else this.db.prepare('UPDATE processing_usage SET state=? WHERE id=?').run('unknown',id);
        throw error;
      }
    } catch(error){if(!dispatched)error.quotaRejected=true;throw error;}
    finally {this.busy.delete(operation.videoId);}
  }
}
