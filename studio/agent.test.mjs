import {test} from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createWorker} from './server.mjs';
import {SCOPES} from './auth.mjs';
import {composerDefaults} from './composer.mjs';
import {validateMessage,validateDecision} from './agent.mjs';

const settings={logo_settings:{enabled:true,logoPath:'/configured/logo.png',position:'top-right'},burn_layout:{rows:4,liftRatio:0,portraitBlurFill:{enabled:true}},translation_languages:['zh-Hant','ja','en'],publish_platforms:{shipinhao:true,youtube:true}};
async function fixture(t) {
 const dir=mkdtempSync(join(tmpdir(),'studio-agent-')),calls=[],jobs=[];
 const state={publishing:true,decisions:0,unknown:false,portrait:true,busy:false,decision:{decision:'run',message:'I will prepare the video.',changes:{context:'Lunch at 莲香西域. Only 你们这个很厉害啊 谢谢你们 is spoken.'}}};
 const upstream=http.createServer(async(req,res)=>{
  let text='';for await(const c of req)text+=c;
  const data=text?JSON.parse(text):null;calls.push({path:req.url,method:req.method,data});let out={};
  if(req.url.startsWith('/api/ui-settings/'))out={value:settings[req.url.split('/').at(-1)]};
  else if(req.url==='/api/languages')out={codes:data?.languages||[],languages:[]};
  else if(req.url==='/api/autopublish/queue')out={jobs};
  else if(req.url==='/api/videos/1')out={id:1,title:'Only this owned video',file_path:'/private/video.mp4'};
  else if(req.url.includes('/publication-sessions'))out={sessions:[{id:7,title:'Completed run'}]};
  else if(req.url.includes('/process-status'))out={ready_for_publish:true,steps:state.busy?{burn:{status:'working'}}:{},pipeline:null};
  else if(req.url.includes('/burn-subtitles'))out={status:'completed',output_url:'/media/edited.mp4',config:{slots:[],logo:{enabled:true},burnSubtitles:false}};
  else if(req.url.endsWith('/process'))out={status:'processing',publication_session_id:7};
  else if(req.url.endsWith('/publish')){
   if(state.unknown){res.statusCode=502;out={error:'Upstream connection lost'};}
   else out={job_id:42,publication_session_id:7,status:'queued'};
  }
  res.setHeader('content-type','application/json');res.end(JSON.stringify(out));
 });
 await new Promise(r=>upstream.listen(0,'127.0.0.1',r));writeFileSync(join(dir,'key'),'transport');
 const worker=createWorker({database:join(dir,'auth.db'),host:'studio.test',upstreamSecretFile:join(dir,'key'),dataRoot:dir,backendPort:upstream.address().port,webRoot:dir,staticRoot:dir,
  publishingEnabled:()=>state.publishing,geometry:async()=>({portrait:state.portrait}),agentPlanner:async input=>{state.decisions++;state.input=input;return state.decision;}});
 await new Promise(r=>worker.server.listen(0,'127.0.0.1',r));
 t.after(async()=>{await Promise.all([new Promise(r=>worker.server.close(r)),new Promise(r=>upstream.close(r))]);worker.auth.db.close();rmSync(dir,{recursive:true,force:true});});
 const owner=worker.auth.addOwner('owner','private-test-password'),token=worker.auth.issue(owner,SCOPES,'native','browser');
 const request=async(path,method='GET',data,headers={})=>{const r=await fetch(`http://127.0.0.1:${worker.server.address().port}/studio/bridge`,{method,headers:{authorization:'Bearer transport','x-studio-path':path,cookie:'__Host-studio='+token.access_token,origin:'https://studio.test','content-type':'application/json',...headers},body:data?JSON.stringify(data):undefined});return {status:r.status,...await r.json()};};
 const chat=(await request('/v1/studio/agent/chats','POST',{videoId:1,id:'chat-fixture-00000001'})).id;
 let counter=0;
 const send=(action='prepare',id='message-fixture-'+String(++counter).padStart(8,'0'),message='Please edit this video')=>request('/v1/studio/agent/chats/'+chat+'/messages','POST',{id,message,action,language:'en'},{'idempotency-key':'agent-'+id});
 return {state,worker,owner,request,send,calls,jobs,chat};
}
test('planner cannot add execution fields or invalid choices',()=>{
 const defaults=composerDefaults(settings),output={decision:'run',message:'Preparing',changes:{}};
 for(const changes of [{videoId:99},{command:'rm'},{logoPath:'/elsewhere'},{platforms:['shell']},{lift:-1},{languages:['ja','ja']},{sessionID:'7'}])assert.throws(()=>validateDecision({...output,changes},defaults));
 assert.deepEqual(validateDecision({...output,changes:{languages:['ko','vi','en','ja','zh-Hant']}},defaults).form.rows,5);
 assert.throws(()=>validateMessage({id:'short',action:'publish',message:'hi',language:'en'}));
});
test('chat uses polished context/ruby/portrait safeguards and the existing prepare operation exactly once',async t=>{
 const f=await fixture(t),first=await f.send('prepare','fixed-message-0000001');
 assert.equal(first.status,200);assert.equal(first.messages[0].state,'submitted');
 assert.equal(first.messages[0].reply,'','execution status never comes from model prose');
 assert.equal(first.preparation.state,'reconciliation_required','accepted is not completion');
 const process=f.calls.filter(c=>c.path.endsWith('/process'));assert.equal(process.length,1);
 const options=process[0].data;
 assert.equal(options.subtitleSourceVersion,'polished');assert.equal(options.autoCorrectSubtitles,true);
 assert.match(options.autoCorrectPrompt,/莲香西域/);assert.match(options.metadataPrompt,/莲香西域/);
 assert.deepEqual(options.burnLayout.slots.map(s=>s.language),['en','ja','zh-Hant']);
 assert.ok(options.burnLayout.slots.every(s=>s.romaji&&s.pinyin));assert.equal(options.burnLayout.portraitBlurFill.enabled,false);
 assert.equal(options.logo.logoPath,settings.logo_settings.logoPath);
 assert.ok(first.messages[0].receipt.operation_id);assert.equal(first.messages[0].receipt.publication_session_id,7);
 await f.send('prepare','fixed-message-0000001');assert.equal(f.state.decisions,1);assert.equal(f.calls.filter(c=>c.path.endsWith('/process')).length,1);
 assert.equal((await f.send('prepare','fixed-message-0000001','Different message')).status,409);
 assert.ok(!JSON.stringify(first).includes('/private/')&&!JSON.stringify(first).includes('/configured/'));
});
test('publication goes through the normal queue; status is its receipt, and subsequent duplicate posts are blocked',async t=>{
 const f=await fixture(t);f.state.decision.changes={burnSubtitles:false,logoPosition:'top-right',platforms:['youtube','instagram']};
 const first=await f.send('publish');assert.equal(first.messages[0].receipt.job_id,42);
 const c=f.calls.find(c=>c.path.endsWith('/publish'));assert.equal(c.data.wait,false);assert.equal(c.data.persistSettings,false);
 assert.equal(c.data.options.burnSubtitles,false);assert.equal(c.data.options.logo.enabled,true);
 f.jobs.push({id:42,video_id:1,status:'running',platforms:['youtube','instagram'],attention:{status:'required',message:'Please log in'}});
 const status=await f.request('/v1/studio/agent/chats/'+f.chat);assert.equal(status.job.status,'running');assert.equal(status.job.attention.status,'required');
 const again=await f.send('publish');assert.equal(again.messages.at(-1).state,'rejected');assert.match(again.messages.at(-1).error,/active task/);
 assert.equal(f.calls.filter(c=>c.path.endsWith('/publish')).length,1);
});
test('read-only questions do not process; invalid model plans cannot dispatch',async t=>{
 const f=await fixture(t);f.state.decision={decision:'reply',message:'Please clarify the subtitle order.',changes:{}};
 const reply=await f.send();assert.equal(reply.messages[0].state,'reply');
 f.state.decision={decision:'run',message:'Processing',changes:{command:'echo bad'}};
 assert.equal((await f.send()).messages.at(-1).state,'rejected');
 assert.equal(f.calls.filter(c=>/\/(process|publish)$/.test(c.path)).length,0);
});
test('ordinary member cannot enable publish via chat; linked devices do not bypass reviewed publish contract',async t=>{
 const f=await fixture(t);f.state.publishing=false;
 assert.equal((await f.send('publish')).status,403);assert.equal(f.state.decisions,0);
 assert.equal((await f.send('prepare')).messages[0].state,'submitted');
 const token=f.worker.auth.issue(f.owner,SCOPES,'linked');
 assert.equal((await f.request('/v1/studio/agent/chats','GET',null,{'x-studio-access':'Bearer '+token.access_token})).status,403);
 const other=f.worker.auth.addOwner('another','private-test-password'),session=f.worker.auth.issue(other,SCOPES,'browser','browser');
 assert.equal((await f.request('/v1/studio/agent/chats/'+f.chat,'GET',null,{cookie:'__Host-studio='+session.access_token})).status,404);
 assert.equal((await f.request('/v1/studio/agent/chats','POST',{videoId:1},{origin:'https://evil.test'})).status,403);
});
test('unknown dispatch survives retries, blocks another turn, and reconciles from durable receipt',async t=>{
 const f=await fixture(t);f.state.unknown=true;
 assert.equal((await f.send('publish','unknown-message-00001')).messages[0].state,'held');
 await f.send('publish','unknown-message-00001');assert.equal(f.calls.filter(c=>c.path.endsWith('/publish')).length,1);
 const again=await f.send('publish');assert.equal(again.messages.at(-1).state,'rejected');assert.match(again.messages.at(-1).error,/reconciliation/);
 f.worker.auth.db.prepare('UPDATE intents SET response=? WHERE owner=? AND key=?').run(JSON.stringify({job_id:42}),f.owner,'agent-unknown-message-00001');
 const checked=await f.request('/v1/studio/agent/chats/'+f.chat);assert.equal(checked.messages[0].state,'submitted');
 assert.equal(checked.messages[0].receipt.job_id,42);assert.equal(f.calls.filter(c=>c.path.endsWith('/publish')).length,1);
});
test('explicit reuse preserves a completed run without correction or rerendering',async t=>{
 const f=await fixture(t);f.state.decision.changes={mode:'reuse',sessionID:7,platforms:['douyin']};
 const result=await f.send('publish');assert.equal(result.messages[0].state,'submitted');
 const options=f.calls.find(c=>c.path.endsWith('/publish')).data.options;
 assert.equal(options.publicationSessionId,7);assert.equal(options.publicationMode,'override');assert.equal(options.autoCorrectSubtitles,false);
 assert.equal(f.calls.filter(c=>c.path.endsWith('/process')).length,0);
});
