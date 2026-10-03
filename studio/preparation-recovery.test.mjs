import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import http from 'node:http';
import {AuthStore} from './auth.mjs';
import {createWorker} from './server.mjs';
import {PreparationRecovery} from './preparation-recovery.mjs';

const finished = created => ({status:'done',updated_at:new Date(created + 1000).toISOString()});

test('recovery persists identity and settings, ignores old artifacts, and holds ambiguous dispatch',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-recovery-'));
  const auth=new AuthStore(join(dir,'auth.sqlite'));
  t.after(()=>{auth.db.close();rmSync(dir,{recursive:true,force:true});});
  const first=new PreparationRecovery(auth.db,'worker-before'),created=Date.now();
  const request={async:true,steps:['keyframes','transcribe','polish','translate','burn'],
    autoCorrectSubtitles:true,autoCorrectPrompt:'original context',logo:{logoPath:'/private/logo.png'},publicationMode:'new'};
  first.register('original-operation','owner',2,request,'a'.repeat(64),created);
  first.accepted('original-operation',{video_id:2,publication_session_id:7,status:'started'});
  const next=new PreparationRecovery(auth.db,'worker-after'),row=next.owned('original-operation','owner');
  assert.throws(()=>next.owned(row.id,'another-owner'),{status:404});
  const state={pipeline:null,steps:{keyframes:finished(created),polish:finished(created),
    // A render from before this request must not be treated as its checkpoint.
    burn:{status:'done',updated_at:new Date(created-1000).toISOString()}}};
  assert.equal(next.describe(row,state).state,'interrupted');
  let calls=0;
  const recovery={status:async()=>state,verifySource:async()=>{},publicationJobs:async()=>[],dispatch:async(_row,data)=>{
    calls++;assert.deepEqual(data.steps,['transcribe','translate','burn']);
    assert.equal(data.autoCorrectSubtitles,false);assert.equal(data.autoCorrectPrompt,'original context');
    assert.equal(data.publicationMode,'override');assert.equal(data.publicationSessionId,7);
    assert.equal(data.operationId,row.id);assert.equal(data.logo.logoPath,'/private/logo.png');
    throw Object.assign(Error('unknown upstream dispatch'),{status:502});
  }};
  await assert.rejects(next.resume(row,{...recovery,publicationJobs:async()=>[{video_id:2,status:'failed'}]}),{status:409});
  assert.equal(calls,0);
  await assert.rejects(next.resume(row,recovery),{status:502});
  assert.equal(next.owned(row.id,'owner').state,'unknown');
  await assert.rejects(next.resume(next.owned(row.id,'owner'),recovery),{status:409});
  assert.equal(calls,1,'uncertain resume cannot silently duplicate');
});

test('fresh durable checkpoints prove completion; implicit cover and translation work cannot disappear',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-recovery-checkpoints-'));
  const auth=new AuthStore(join(dir,'auth.sqlite'));
  t.after(()=>{auth.db.close();rmSync(dir,{recursive:true,force:true});});
  const old=new PreparationRecovery(auth.db,'worker-before'),created=Date.now();
  old.register('original-operation','owner',2,{async:true,steps:['metadata_zh','burn'],burnSubtitles:true},'a'.repeat(64),created);
  old.accepted('original-operation',{video_id:2,publication_session_id:null,status:'started'});
  const next=new PreparationRecovery(auth.db,'worker-after'),row=next.owned('original-operation','owner');
  const status={pipeline:null,steps:{metadata_zh:finished(created),burn:finished(created)}};
  assert.equal(next.describe(row,status).state,'interrupted','metadata implies cover and a subtitle burn implies translation');
  status.steps.cover=finished(created);status.steps.translate=finished(created);
  assert.equal(next.describe(row,status).state,'done');
  const result=await next.resume(row,{status:async()=>status,dispatch:async()=>assert.fail('completed work must not be dispatched')});
  assert.equal(result.state,'done');
});

test('simulated worker replacement resumes the same linked preparation once, never posts or charges another run',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-recovery-api-')),root=join(dir,'data');mkdirSync(root);
  const source=join(root,'fixture.mp4');writeFileSync(source,'harmless fixture');
  const sha=createHash('sha256').update('harmless fixture').digest('hex');
  writeFileSync(join(dir,'transport'),'test-transport');
  let status={pipeline:null,steps:{}},metered=0;
  const posts=[];
  const backend=http.createServer(async(req,res)=>{
    let body='';for await(const b of req)body+=b;
    let reply;
    if(req.method==='POST'){
      const data=JSON.parse(body);posts.push({path:req.url,data});
      status={pipeline:{status:'working',operation_id:data.operationId,updated_at:new Date().toISOString()},steps:{transcribe:{status:'working'}}};
      reply={video_id:2,publication_session_id:null,status:'started'};
    }else if(req.url==='/api/videos/2')reply={id:2,file_path:source};
    else if(req.url==='/api/videos/2/process-status')reply=status;
    else if(req.url==='/api/autopublish/queue')reply={jobs:[]};
    else if(req.url==='/api/ui-settings/logo_settings')reply={value:{enabled:true,logoPath:'/configured/logo.png'}};
    else throw Error('Unexpected backend request '+req.url);
    res.setHeader('content-type','application/json');res.end(JSON.stringify(reply));
  });
  await new Promise(r=>backend.listen(0,'127.0.0.1',r));
  const config={database:join(dir,'auth.sqlite'),dataRoot:root,host:'studio.test',upstreamSecretFile:join(dir,'transport'),
    backendPort:backend.address().port,webRoot:dir,staticRoot:dir,publishingEnabled:()=>false,
    processingRequest:async(path,method,data,dispatch)=>{if(method==='POST'&&path.endsWith('/process'))metered++;return dispatch(path,method,data);}};
  let worker=createWorker(config);await new Promise(r=>worker.server.listen(0,'127.0.0.1',r));
  t.after(async()=>{worker.server.closeAllConnections();await new Promise(r=>worker.server.close(r));worker.auth.db.close();backend.closeAllConnections();await new Promise(r=>backend.close(r));rmSync(dir,{recursive:true,force:true});});
  const owner=worker.auth.addOwner('reviewer','private-test-password'),token=worker.auth.issue(owner,['media.read','edit.submit','jobs.read','publication.prepare']);
  worker.auth.db.prepare('INSERT INTO media VALUES(?,?,?,?)').run(2,owner,sha,'fixture.mp4');
  const call=async(path,body,key='original-key',access=token.access_token)=>{
    const r=await fetch(`http://127.0.0.1:${worker.server.address().port}/studio/bridge`,{method:body?'POST':'GET',
      headers:{authorization:'Bearer test-transport','x-studio-access':'Bearer '+access,'x-studio-path':path,
        'content-type':'application/json','idempotency-key':key},body:body?JSON.stringify(body):undefined});
    return {code:r.status,body:await r.json()};
  };
  const brief={preparationPreset:'lightmind-capture.v1',background:'Harmless fixture, no social post',requirements:''};
  const accepted=await call('/api/videos/2/process',brief);assert.equal(accepted.code,200);
  const operation=accepted.body.operation_id;assert.ok(operation);
  const intentBefore=worker.auth.db.prepare('SELECT * FROM intents WHERE key=?').get('original-key');
  status={pipeline:null,steps:{keyframes:finished(intentBefore.created),caption:finished(intentBefore.created)}};
  // Stop only this test fixture, not any real worker or client acceptance runtime.
  worker.server.closeAllConnections();await new Promise(r=>worker.server.close(r));worker.auth.db.close();
  worker=createWorker(config);await new Promise(r=>worker.server.listen(0,'127.0.0.1',r));
  const read=await call(`/v1/studio/preparations/${operation}`);assert.equal(read.body.state,'interrupted');
  const processStatus=await call('/api/videos/2/process-status');assert.equal(processStatus.body.pipeline.status,'interrupted');
  assert.deepEqual((await call('/api/videos/2/process',brief)).body,accepted.body);
  assert.equal(posts.length,1,'cached original acceptance does not restart work');
  const other=worker.auth.addOwner('other','private-other-password'),otherToken=worker.auth.issue(other,['media.read','edit.submit','jobs.read']);
  assert.equal((await call(`/v1/studio/preparations/${operation}`,null,'read',otherToken.access_token)).code,404);
  const readOnly=worker.auth.issue(owner,['media.read','jobs.read']);
  assert.equal((await call(`/v1/studio/preparations/${operation}/resume`,{},'read',readOnly.access_token)).code,403);
  assert.equal((await call(`/v1/studio/preparations/${operation}/resume`,{platforms:['youtube']})).code,400);
  const superseding=new PreparationRecovery(worker.auth.db,'later-test-instance');
  const newer='superseding-operation-for-test';
  const originalCreated=worker.auth.db.prepare('SELECT created FROM studio_preparations WHERE id=?').get(operation).created;
  // Two intents accepted within the same millisecond still have a definite order.
  superseding.register(newer,owner,2,{async:true,steps:['transcribe']},sha,originalCreated);
  superseding.accepted(newer,{video_id:2,status:'started'});
  assert.equal((await call(`/v1/studio/preparations/${operation}/resume`,{})).code,409);
  worker.auth.db.prepare('DELETE FROM studio_preparations WHERE id=?').run(newer);
  writeFileSync(source,'changed');
  assert.equal((await call(`/v1/studio/preparations/${operation}/resume`,{})).code,409);
  writeFileSync(source,'harmless fixture');
  const resumed=await call(`/v1/studio/preparations/${operation}/resume`,{});
  assert.equal(resumed.code,200);assert.equal(resumed.body.operation_id,operation);assert.equal(resumed.body.recoveries,1);
  assert.ok(!resumed.body.resumed_steps.includes('caption'));assert.ok(!resumed.body.resumed_steps.includes('keyframes'));
  assert.equal((await call(`/v1/studio/preparations/${operation}/resume`,{})).code,200);
  assert.equal(posts.length,2);assert.equal(metered,1,'recovery reuses the initial run reservation');
  assert.ok(posts.every(p=>p.path==='/api/videos/2/process'));
  assert.equal(worker.auth.db.prepare('SELECT count(*) n FROM intents').get().n,1);
  assert.deepEqual(worker.auth.db.prepare('SELECT * FROM intents WHERE key=?').get('original-key'),intentBefore);
});
