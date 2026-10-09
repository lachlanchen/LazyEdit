import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync,symlinkSync,mkdirSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {AuthStore} from '../studio/auth.mjs';
import {ProcessingMeter,processingPeriod,processingLimit} from './processing.mjs';

function fixture(t,seconds=180){
  const dir=mkdtempSync(join(tmpdir(),'studio-processing-')),root=join(dir,'data');
  mkdirSync(root);const file=join(root,'source.mp4');writeFileSync(file,'fixture');
  const auth=new AuthStore(join(dir,'auth.sqlite'));
  t.after(()=>{auth.db.close();rmSync(dir,{recursive:true,force:true});});
  const meter=new ProcessingMeter(auth.db,root,async()=>seconds);
  let calls=0,ready=false,rejection;
  const dispatch=async(path,method)=>{
    if(path.endsWith('/processing-quote'))return {requiresProcessing:!ready};
    if(method==='GET')return {file_path:file};
    calls++;if(rejection)throw rejection;return {status:'started',job_id:calls};
  };
  return {dir,root,file,auth,meter,dispatch,calls:()=>calls,ready:()=>{ready=true;},reject:value=>{rejection=value;}};
}

import http from 'node:http';
import {createGateway} from './gateway.mjs';
import {createCell} from './cell.mjs';
const listen=server=>new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const request=(port,host,path,method='GET',body,headers={})=>new Promise((resolve,reject)=>{
  const req=http.request({hostname:'127.0.0.1',port,path,method,headers:{host,origin:`https://${host}`,'content-type':'application/json',...headers}},res=>{
    let value='';res.on('data',v=>value+=v);res.on('end',()=>resolve({status:res.statusCode,body:JSON.parse(value)}));
  });req.on('error',reject);req.end(body===undefined?undefined:JSON.stringify(body));
});

test('gateway-derived allowance covers browser and linked-app requests; forged owner bypass is stripped',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-quota-transport-')),config={database:join(dir,'registry.sqlite'),domain:'studio.test',workerHost:()=> '127.0.0.1'};
  const gateway=createGateway(config),owner=gateway.registry.register({username:'member',password:'test-only-long-password',invitation:gateway.registry.invite()},'test');
  const w=gateway.registry.workspace(owner),host=gateway.registry.host(w),file=join(dir,'source.mp4');
  writeFileSync(file,'fixture');writeFileSync(join(dir,'transport'),w.transport);
  let dispatches=0,seconds=720;
  const backend=http.createServer((req,res)=>{res.setHeader('content-type','application/json');
    if(req.url.endsWith('/processing-quote'))return res.end(JSON.stringify({requiresProcessing:true}));
    if(req.method==='GET')return res.end(JSON.stringify({id:1,file_path:file}));
    dispatches++;res.end(JSON.stringify({status:'started'}));
  });await listen(backend);
  const cell=createCell({host,database:join(dir,'cell.sqlite'),upstreamSecretFile:join(dir,'transport'),dataRoot:dir,
    backendPort:backend.address().port,webRoot:dir,staticRoot:dir,processingQuotas:true,durationProbe:async()=>seconds},
    {...w,username:'member',password:gateway.registry.db.prepare('SELECT password FROM users WHERE id=?').get(owner).password});
  await listen(cell.server);config.workerPort=cell.server.address().port;
  gateway.registry.db.prepare("UPDATE workspaces SET status='ready' WHERE id=?").run(w.id);
  await listen(gateway.server);
  t.after(()=>{for(const s of [gateway.server,cell.server,backend]){s.closeAllConnections();s.close();}cell.auth.db.close();gateway.registry.db.close();rmSync(dir,{recursive:true,force:true});});
  cell.auth.db.prepare('INSERT INTO media VALUES(?,?,?,?)').run(1,owner,'a'.repeat(64),'source.mp4');
  const port=gateway.server.address().port,browser=cell.auth.issue(owner,undefined,'test','browser'),device=cell.auth.issue(owner);
  const forged={'x-studio-processing-minutes':'owner'},cookie={...forged,cookie:`__Host-studio=${browser.access_token}`};
  assert.equal((await request(port,host,'/api/videos/1/process','POST',{},forged)).status,401);
  assert.equal((await request(port,host,'/api/videos/1/process','POST',{},cookie)).status,429);
  assert.equal(dispatches,0);
  const native={...forged,authorization:`Bearer ${device.access_token}`,'idempotency-key':'linked-app-processing'};
  assert.equal((await request(port,host,'/api/videos/1/process','POST',{steps:['transcribe']},native)).status,429);
  assert.equal(cell.auth.db.prepare('SELECT count(*) n FROM intents').get().n,0,'quota rejection occurs before any uncertain intent');
  seconds=60;
  assert.equal((await request(port,host,'/api/videos/1/process','POST',{steps:['transcribe']},native)).status,200);
  assert.equal((await request(port,host,'/api/videos/1/process','POST',{steps:['transcribe']},native)).status,200);
  assert.equal(dispatches,1,'same linked-app intent is accepted and charged only once');
  const usage=await request(port,host,'/v1/studio/usage','GET',undefined,cookie);
  assert.equal(usage.body.limitMinutes,10);assert.equal(usage.body.usedMinutes,1);
});

test('source-minute reservations block exhaustion, replay safely, and allow completed-run reuse',async t=>{
  const f=fixture(t),context={limit:'10',key:'first-request'};
  const run=key=>f.meter.run('/api/videos/1/process','POST',{steps:['transcribe']},f.dispatch,{...context,key});
  const first=await run('first-request');assert.equal(f.meter.usage(10).usedMinutes,3);
  assert.deepEqual(await run('first-request'),first);assert.equal(f.calls(),1);
  await assert.rejects(f.meter.run('/api/videos/1/process','POST',{steps:['burn']},f.dispatch,context),{status:409});
  await run('second-request');await run('third-request');
  await assert.rejects(run('fourth-request'),{status:429,quotaRejected:true});assert.equal(f.calls(),3);
  assert.equal(f.meter.usage(10).usedMinutes,9);
  f.ready();await f.meter.run('/api/videos/1/publish','POST',{platforms:['youtube']},f.dispatch,{limit:'0'});
  assert.equal(f.calls(),4);assert.equal(f.meter.usage(10).usedMinutes,9);
  await f.meter.run('/api/videos/1/process','POST',{},f.dispatch,{limit:'owner'});
  assert.equal(f.meter.usage(10).usedMinutes,9,'operator bypass does not consume member quota');
  assert.throws(()=>processingLimit('999999'),{status:503});
  assert.equal(processingPeriod(Date.UTC(2026,11,31)).resetsAt,Date.UTC(2027,0,1));
});

test('definite rejections release minutes; ambiguous dispatch cannot silently run again',async t=>{
  const f=fixture(t),context={limit:'10',key:'uncertain-run'};
  f.reject(Object.assign(Error('invalid options'),{status:400}));
  await assert.rejects(f.meter.run('/api/videos/1/process','POST',{},f.dispatch,context),{status:400});
  assert.equal(f.meter.usage(10).usedMinutes,0);
  f.reject(Object.assign(Error('upstream timeout'),{status:504}));
  await assert.rejects(f.meter.run('/api/videos/1/process','POST',{},f.dispatch,context),{status:504});
  assert.equal(f.meter.usage(10).usedMinutes,3);
  await assert.rejects(f.meter.run('/api/videos/1/process','POST',{},f.dispatch,context),{status:409});
  assert.equal(f.calls(),2,'unknown dispatch remains held instead of duplicated');
});

test('meter rejects a symlinked outside source and never trusts a client duration',async t=>{
  const f=fixture(t),outside=join(f.dir,'private.mp4');writeFileSync(outside,'private');
  rmSync(f.file);symlinkSync(outside,f.file);
  await assert.rejects(f.meter.run('/api/videos/1/process','POST',{duration:0},f.dispatch,{limit:'10'}),{status:403});
  assert.equal(f.calls(),0);assert.equal(f.meter.usage(10).usedMinutes,0);
});

test('chat inherits the gateway allowance, strips forged quota bypass, and charges a retry once',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-agent-quota-'));
  const config={database:join(dir,'registry.sqlite'),domain:'chat.test',workerHost:()=> '127.0.0.1'};
  const gateway=createGateway(config),owner=gateway.registry.register({username:'chatmember',password:'test-only-long-password',invitation:gateway.registry.invite()},'test');
  const w=gateway.registry.workspace(owner),host=gateway.registry.host(w),file=join(dir,'source.mp4');
  writeFileSync(file,'fixture');writeFileSync(join(dir,'transport'),w.transport);let dispatches=0,seconds=720;
  const backend=http.createServer(async(req,res)=>{
    let input='';for await(const bytes of req)input+=bytes;
    let value={};
    if(req.url.endsWith('/processing-quote'))value={requiresProcessing:true};
    else if(req.url.startsWith('/api/ui-settings/'))value={value:req.url.endsWith('logo_settings')?{enabled:true,logoPath:'existing-logo.png'}:req.url.endsWith('translation_languages')?['zh-Hant','ja','en']:{}};
    else if(req.url==='/api/languages')value={codes:JSON.parse(input).languages};
    else if(req.url==='/api/videos/1')value={id:1,title:'Fixture',file_path:file};
    else if(req.url.endsWith('/publication-sessions'))value={sessions:[]};
    else if(req.url.includes('/process-status'))value={steps:{}};
    else if(req.url.endsWith('/process')){dispatches++;value={status:'processing',publication_session_id:1};}
    res.setHeader('content-type','application/json');res.end(JSON.stringify(value));
  });await listen(backend);
  const cell=createCell({host,database:join(dir,'cell.sqlite'),upstreamSecretFile:join(dir,'transport'),dataRoot:dir,backendPort:backend.address().port,
    webRoot:dir,staticRoot:dir,processingQuotas:true,durationProbe:async()=>seconds,geometry:async()=>({portrait:true}),
    agentPlanner:async()=>({decision:'run',message:'Prepare',changes:{}})},
    {...w,username:'chatmember',password:gateway.registry.db.prepare('SELECT password FROM users WHERE id=?').get(owner).password});
  await listen(cell.server);config.workerPort=cell.server.address().port;
  gateway.registry.db.prepare("UPDATE workspaces SET status='ready' WHERE id=?").run(w.id);await listen(gateway.server);
  t.after(()=>{for(const s of [gateway.server,cell.server,backend]){s.closeAllConnections();s.close();}cell.auth.db.close();gateway.registry.db.close();rmSync(dir,{recursive:true,force:true});});
  const port=gateway.server.address().port,browser=cell.auth.issue(owner,undefined,'native','browser');
  const headers={cookie:`__Host-studio=${browser.access_token}`,'x-studio-processing-minutes':'owner'};
  const chat=(await request(port,host,'/v1/studio/agent/chats','POST',{videoId:1},headers)).body.id;
  const send=id=>request(port,host,`/v1/studio/agent/chats/${chat}/messages`,'POST',{id,action:'prepare',message:'Prepare the video',language:'en'},
    {...headers,'idempotency-key':'agent-'+id});
  const denied=await send('denied-message-00001');assert.equal(denied.body.messages[0].state,'rejected');assert.match(denied.body.messages[0].error,/Monthly processing allowance exceeded/);
  assert.equal(dispatches,0);assert.equal(cell.auth.db.prepare('SELECT COUNT(*) n FROM intents').get().n,0);
  seconds=60;
  const accepted=await send('allowed-message-00001');assert.equal(accepted.body.messages.at(-1).state,'submitted',JSON.stringify(accepted));
  await send('allowed-message-00001');assert.equal(dispatches,1);
  const usage=await request(port,host,'/v1/studio/usage','GET',undefined,headers);assert.equal(usage.body.limitMinutes,10);assert.equal(usage.body.usedMinutes,1);
});
