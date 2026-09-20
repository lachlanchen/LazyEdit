import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import http from 'node:http';
import {AuthStore,SCOPES} from './auth.mjs';
import {createWorker,safeFilename} from './server.mjs';
import {validPath} from './transport.mjs';
const dir=mkdtempSync(join(tmpdir(),'studio-test-'));process.on('exit',()=>rmSync(dir,{recursive:true,force:true}));
test('password authentication, scoped tokens, expiration, rotation and revocation',()=>{
 const a=new AuthStore(join(dir,'auth.db')),owner=a.addOwner('owner','private-test-password');
 assert.throws(()=>a.login('owner','bad','x'),/Invalid/);assert.equal(a.login('owner','private-test-password','x'),owner);
 const t=a.issue(owner,['media.read']);assert.deepEqual(a.principal(t.access_token).scopes,['media.read']);assert.throws(()=>a.principal('bad'),/expired/);
 const next=a.refresh(t.refresh_token);assert.throws(()=>a.principal(t.access_token),/expired/);assert.throws(()=>a.refresh(t.refresh_token),/expired/);
 a.revoke(owner,next.grant_id);assert.throws(()=>a.principal(next.access_token),/expired/);
 const expired=a.issue(owner,['media.read']);a.db.prepare('UPDATE tokens SET expires=0').run();assert.throws(()=>a.principal(expired.access_token),/expired/);
 assert.throws(()=>a.own({kind:'device',owner},4),/not owned/);a.db.close();
});
test('device consent binds requested scopes and consumes approval once',()=>{
 const a=new AuthStore(join(dir,'device.db')),owner=a.addOwner('owner','private-test-password'),d=a.device(['media.upload'],'Glasses','x');
 assert.throws(()=>a.poll(d.device_code),/authorization_pending/);a.approve(owner,d.user_code);a.db.prepare('UPDATE devices SET polled=0').run();
 const t=a.poll(d.device_code);assert.deepEqual(a.principal(t.access_token).scopes,['media.upload']);assert.throws(()=>a.poll(d.device_code),/expired_token/);a.db.close();
});
test('path traversal, encoded separators, filenames and scope escalation are rejected',()=>{
 for(const p of ['//example','/../x','/%2e%2e/x','/x%2fy','/x%252fy','/x\\y'])assert.equal(validPath(p),false,p);
 assert.equal(validPath('/api/videos/1?x=y'),true);for(const p of ['../v.mp4','v.exe','.secret.mp4'])assert.throws(()=>safeFilename(p));
});
test('HTTP transport authentication, CSRF, ownership, idempotency and anonymous API denial',async()=>{
 let calls=0;const backend=http.createServer((req,res)=>{calls++;res.setHeader('content-type','application/json');res.end(JSON.stringify({status:'processing',job_id:17}));});await new Promise(r=>backend.listen(0,'127.0.0.1',r));
 writeFileSync(join(dir,'secret'),'transport-test');const w=createWorker({database:join(dir,'http.db'),host:'studio.test',upstreamSecretFile:join(dir,'secret'),dataRoot:dir,backendPort:backend.address().port,webRoot:dir,staticRoot:dir});await new Promise(r=>w.server.listen(0,'127.0.0.1',r));
 const owner=w.auth.addOwner('owner','test-password');const token=w.auth.issue(owner,SCOPES);w.auth.db.prepare('INSERT INTO media VALUES(?,?,?,?)').run(1,owner,'hash','test.mp4');
 const url=`http://127.0.0.1:${w.server.address().port}/studio/bridge`;
 const request=(path,method='GET',data,extra={})=>fetch(url,{method,headers:{authorization:'Bearer transport-test','x-studio-path':path,'content-type':'application/json',...extra},body:data?JSON.stringify(data):undefined});
 try{
 assert.equal((await fetch(url)).status,401);assert.equal((await request('/api/videos')).status,401);
 assert.equal((await request('/api/videos/999','GET',null,{'x-studio-access':'Bearer '+token.access_token})).status,403);
 assert.equal((await request('/api/private','GET',null,{'x-studio-access':'Bearer '+token.access_token})).status,404);
 const browser=w.auth.issue(owner,SCOPES,'browser','browser');assert.equal((await request('/auth/logout','POST',{}, {cookie:'__Host-studio='+browser.access_token,origin:'https://evil.test'})).status,403);
 const h={'x-studio-access':'Bearer '+token.access_token,'idempotency-key':'job-one'};
 assert.equal((await request('/api/videos/1/process','POST',{steps:['keyframes']},h)).status,200);
 assert.equal((await request('/api/videos/1/process','POST',{steps:['keyframes']},h)).status,200);assert.equal(calls,1);
 assert.equal((await request('/api/videos/1/process','POST',{steps:['transcribe']},h)).status,409);
 assert.equal((await request('/api/videos/1/publish','POST',{platforms:['youtube']},h)).status,400);assert.equal(calls,1);
 }finally{await new Promise(r=>w.server.close(r));await new Promise(r=>backend.close(r));w.auth.db.close();}
});
