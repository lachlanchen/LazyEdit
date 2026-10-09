// Chat is a durable intent adapter, never a second processing/publication worker.
import {spawn} from 'node:child_process';
import {fail, digest, secret} from './auth.mjs';
import {validateForm} from './composer.mjs';

export function validateMessage(value) {
  if (!value || Object.keys(value).some(k=>!['id','message','action','language'].includes(k))) fail(400,'Invalid chat message');
  if (!/^[A-Za-z0-9_-]{16,80}$/.test(value.id||'')) fail(400,'A stable message ID is required');
  if (typeof value.message!=='string' || !value.message.trim() || value.message.length>16000) fail(400,'Write a message of up to 16000 characters');
  if (!['prepare','publish'].includes(value.action)) fail(400,'Choose prepare or publish');
  if (typeof value.language!=='string' || !/^[A-Za-z-]{2,20}$/.test(value.language)) fail(400,'Invalid interface language');
  return {...value,message:value.message.trim()};
}

export function validateDecision(value, defaults) {
  if (!value || Object.keys(value).some(k=>!['decision','message','changes'].includes(k)) || !['run','reply'].includes(value.decision)
      || typeof value.message!=='string' || !value.message.trim() || value.message.length>2000
      || !value.changes || Array.isArray(value.changes) || typeof value.changes!=='object') fail(502,'The agent returned an invalid plan; nothing was submitted');
  // The model cannot select a video, account, file, endpoint, tool or permission.
  const fields=Object.keys(defaults);
  if(Object.keys(value.changes).some(k=>!fields.includes(k))) fail(502,'The agent proposed an unsupported option; nothing was submitted');
  const form={...defaults,...value.changes};
  if(!Object.hasOwn(value.changes,'rows'))form.rows=Math.max(form.rows,form.languages?.length||0);
  return {...value,form:validateForm(form)};
}

export function planWithModel(config, input) {
  if(config.agentPlanner)return config.agentPlanner(input); // isolated contract tests
  return new Promise((resolve,reject)=>{
    const child=spawn(config.python||'python',[new URL('./agent_plan.py',import.meta.url).pathname,config.sourceRoot||'.'],
      {stdio:['pipe','pipe','pipe'],env:process.env});
    let output='',finished=false;
    const finish=(error,value)=>{if(finished)return;finished=true;clearTimeout(timer);error?reject(error):resolve(value);};
    const unavailable=()=>Object.assign(new Error('The chat planner is unavailable. Your video is saved; no task was submitted. Try again or use the editor.'),{status:503});
    const timer=setTimeout(()=>{child.kill('SIGKILL');finish(unavailable());},90000);
    child.stdout.on('data',chunk=>{output+=chunk;if(output.length>100000){child.kill('SIGKILL');finish(unavailable());}});
    // Never echo provider credentials, private context or raw model errors.
    child.stderr.resume();child.on('error',()=>finish(unavailable()));child.stdin.on('error',()=>{});
    child.on('close',code=>{try {if(code!==0)throw Error();finish(null,JSON.parse(output));}catch{finish(unavailable());}});
    child.stdin.end(JSON.stringify(input));
  });
}

export class AgentChats {
  constructor(db) {
    this.db=db;
    db.exec(`CREATE TABLE IF NOT EXISTS agent_chats(id TEXT PRIMARY KEY,owner TEXT NOT NULL,video_id INTEGER NOT NULL,title TEXT NOT NULL,created INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS agent_turns(id TEXT NOT NULL,chat TEXT NOT NULL,owner TEXT NOT NULL,fingerprint TEXT NOT NULL,request TEXT NOT NULL,
      plan TEXT,state TEXT NOT NULL,result TEXT,error TEXT,created INTEGER NOT NULL,PRIMARY KEY(owner,id));
      CREATE INDEX IF NOT EXISTS agent_chat_owner ON agent_chats(owner,created);
      CREATE INDEX IF NOT EXISTS agent_turn_chat ON agent_turns(owner,chat,created);`);
  }
  create(owner,videoId,title,id=secret()) {
    if(!/^[A-Za-z0-9_-]{16,80}$/.test(id))fail(400,'Invalid chat ID');
    const prior=this.db.prepare('SELECT * FROM agent_chats WHERE id=?').get(id);
    if(prior){if(prior.owner!==owner||prior.video_id!==videoId)fail(409,'Chat ID conflict');return prior;}
    this.db.prepare('INSERT INTO agent_chats VALUES(?,?,?,?,?)').run(id,owner,videoId,String(title||'Video').slice(0,240),Date.now());
    return this.owned(owner,id);
  }
  list(owner) {return this.db.prepare('SELECT id,video_id,title,created FROM agent_chats WHERE owner=? ORDER BY created DESC LIMIT 100').all(owner);}
  owned(owner,id) {const row=this.db.prepare('SELECT * FROM agent_chats WHERE id=? AND owner=?').get(id,owner);if(!row)fail(404,'Chat unavailable');return row;}
  turns(owner,chat) {return this.db.prepare('SELECT * FROM agent_turns WHERE owner=? AND chat=? ORDER BY created,rowid').all(owner,chat).map(r=>({...r,request:JSON.parse(r.request),plan:r.plan?JSON.parse(r.plan):null,result:r.result?JSON.parse(r.result):null}));}
  accept(owner,chat,request) {
    const fingerprint=digest(JSON.stringify({chat,request}));
    const prior=this.db.prepare('SELECT * FROM agent_turns WHERE owner=? AND id=?').get(owner,request.id);
    if(prior){if(prior.fingerprint!==fingerprint)fail(409,'Message ID conflict');return this.turns(owner,chat).find(t=>t.id===request.id);}
    if(this.turns(owner,chat).length>=100)fail(409,'Start a new chat for this video');
    const recent=this.db.prepare('SELECT COUNT(*) n FROM agent_turns WHERE owner=? AND created>?').get(owner,Date.now()-60000).n;
    if(recent>=6)fail(429,'Please wait before sending another message');
    this.db.prepare('INSERT INTO agent_turns(id,chat,owner,fingerprint,request,state,created) VALUES(?,?,?,?,?,?,?)')
      .run(request.id,chat,owner,fingerprint,JSON.stringify(request),'planning',Date.now());
    return this.turns(owner,chat).at(-1);
  }
  update(owner,id,state,{plan,result,error}={}) {
    this.db.prepare('UPDATE agent_turns SET state=?,plan=COALESCE(?,plan),result=COALESCE(?,result),error=? WHERE owner=? AND id=?')
      .run(state,plan?JSON.stringify(plan):null,result?JSON.stringify(result):null,error||null,owner,id);
  }
  assertResolved(owner,videoId,except='') {
    const row=this.db.prepare(`SELECT t.id FROM agent_turns t JOIN agent_chats c ON c.id=t.chat
      WHERE t.owner=? AND c.video_id=? AND t.id<>? AND t.state IN ('planning','planned','held') LIMIT 1`).get(owner,videoId,except);
    if(row)fail(409,'An earlier chat request needs reconciliation. Open that chat before submitting another task');
  }
  describe(owner,chat) {
    const c=this.owned(owner,chat);
    return {id:c.id,videoId:c.video_id,title:c.title,messages:this.turns(owner,chat).map(t=>({id:t.id,text:t.request.message,action:t.request.action,
      state:t.state,reply:t.plan?.message||'',form:t.plan?.form,summary:t.plan?.summary,receipt:t.result,error:t.error,created:t.created}))};
  }
}
