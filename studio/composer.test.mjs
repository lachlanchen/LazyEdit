import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import http from 'node:http';
import {createWorker} from './server.mjs';
import {SCOPES} from './auth.mjs';
import {composerDefaults, composeOptions, validateForm, reuseOptions, checkPublicationJobs} from './composer.mjs';

const settings={logo_settings:{enabled:true,logoPath:'/configured/existing-logo.png',position:'top-right'},
 burn_layout:{rows:4,liftRatio:0,slots:[{language:'ja',romaji:false}],fontColor:'#FFFFFF',portraitBlurFill:{enabled:true,mode:'lalachan',bottomSpaceRatio:0.4}},
 publish_platforms:{shipinhao:true,instagram:true,youtube:true},translation_languages:['zh-Hant','ja','en']};
test('one-shot choices preserve defaults, corrected context, subtitle order and pronunciation',()=>{
 const snapshot=JSON.stringify(settings),f=composerDefaults(settings);f.context='飞飞和心遥讨论 X-Fusion';f.languages=['fr','zh-Hant','ja','en'];
 const o=composeOptions(f,settings,{portrait:false});
 assert.equal(JSON.stringify(settings),snapshot);assert.equal(o.publicationMode,'new');assert.equal(o.subtitleSourceVersion,'polished');
 assert.deepEqual(o.burnLayout.slots.map(s=>s.language),['en','ja','zh-Hant','fr']);
 assert.equal(o.burnLayout.slots.find(s=>s.language==='ja').romaji,true);assert.equal(o.burnLayout.pinyinEnabled,true);
 assert.match(o.autoCorrectPrompt,/Preserve every cue/);assert.match(o.metadataPrompt,/Background is evidence/);assert.match(o.metadataPrompt,/飞飞/);
 assert.equal(o.logo.logoPath,settings.logo_settings.logoPath);
 f.contextForMetadata=false;assert.doesNotMatch(composeOptions(f,settings,{portrait:false}).metadataPrompt,/飞飞/);
 f.burnSubtitles=false;const silent=composeOptions(f,settings,{portrait:true});assert.equal(silent.logo.enabled,true);assert.equal(silent.burnSubtitles,false);assert.equal(silent.burnLayout.portraitBlurFill.enabled,false);
 f.logo=false;assert.equal(composeOptions(f,settings,{portrait:true}).logo.enabled,false);
});
test('invalid ranges and orders fail; reuse uses the saved output without recorrection',()=>{
 for(const edit of [{lift:-0.1},{rows:1},{fontScale:0.5},{fontScale:2.6},{languages:['ja','ja']},{platforms:['shell']},{context:23},{extra:'x'}]) assert.throws(()=>validateForm({...composerDefaults(settings),...edit}));
 const o=reuseOptions({id:7,config:{autoCorrectSubtitles:true,metadataPrompt:'old'}},{status:'completed',output_url:'/media/ready.mp4',config:{burnSubtitles:false,slots:[],logo:{enabled:true,position:'top-right'}}},{ready_for_publish:true});
 assert.equal(o.publicationSessionId,7);assert.equal(o.publicationMode,'override');assert.equal(o.autoCorrectSubtitles,false);assert.equal(o.metadataPrompt,'');assert.equal(o.burnSubtitles,false);
 assert.throws(()=>reuseOptions(null,{status:'processing'},{}));
 assert.throws(()=>checkPublicationJobs([{video_id:1,status:'failed',platforms:['youtube']}],1,['youtube'],true));
 assert.doesNotThrow(()=>checkPublicationJobs([{video_id:1,status:'done',platforms:['youtube']}],1,['shipinhao'],true));
 assert.throws(()=>checkPublicationJobs([{video_id:1,status:'running',platforms:['youtube']}],1,['shipinhao'],true));
});

test('native requests use existing pipeline once, hide is reversible, linked permissions stay isolated',async t=>{
 const dir=mkdtempSync(join(tmpdir(),'studio-composer-')),calls=[],jobs=[];
 let failPublish=false;
 const backend=http.createServer(async(req,res)=>{
  const chunks=[];for await(const c of req)chunks.push(c);
  const data=chunks.length?JSON.parse(Buffer.concat(chunks)):null;
  calls.push({url:req.url,method:req.method,data});
  let out={};
  if(req.url.startsWith('/api/ui-settings/'))out={value:settings[req.url.split('/').at(-1)]};
  else if(req.url.startsWith('/api/videos?')||req.url==='/api/videos')out={videos:[{id:1,title:'Fixture'}]};
  else if(req.url==='/api/videos/1')out={id:1,file_path:'/fixture.mp4'};
  else if(req.url==='/api/videos/1/publication-sessions')out={sessions:[]};
  else if(req.url==='/api/videos/1/process-status')out={steps:{},ready_for_publish:true};
  else if(req.url==='/api/autopublish/queue')out={jobs};
  else if(req.url.endsWith('/publish')) {out={job_id:10};if(failPublish){res.statusCode=502;out={error:'Unknown upstream result'};}}
  else if(req.url.endsWith('/process'))out={status:'processing',publication_session_id:3};
  res.setHeader('content-type','application/json');res.end(JSON.stringify(out));
 });
 await new Promise(r=>backend.listen(0,'127.0.0.1',r));
 writeFileSync(join(dir,'key'),'private-test-transport');
 const worker=createWorker({database:join(dir,'accounts.db'),host:'studio.test',upstreamSecretFile:join(dir,'key'),dataRoot:dir,backendPort:backend.address().port,webRoot:dir,staticRoot:dir,
  geometry:async()=>({width:1080,height:1920,portrait:true,fill:false})});
 await new Promise(r=>worker.server.listen(0,'127.0.0.1',r));
 t.after(async()=>{await new Promise(r=>worker.server.close(r));await new Promise(r=>backend.close(r));worker.auth.db.close();rmSync(dir,{recursive:true,force:true});});
 const owner=worker.auth.addOwner('owner','private-test-password'),token=worker.auth.issue(owner,SCOPES,'native','browser');
 const request=(path,method='GET',data,extra={})=>fetch(`http://127.0.0.1:${worker.server.address().port}/studio/bridge`,{method,headers:{authorization:'Bearer private-test-transport','x-studio-path':path,cookie:'__Host-studio='+token.access_token,origin:'https://studio.test','content-type':'application/json',...extra},body:data?JSON.stringify(data):undefined});
 const form=composerDefaults(settings),prefix='/v1/studio/videos/1';
 assert.equal((await request(prefix+'/composer')).status,200);
 const before=calls.length;
 const plan=await request(prefix+'/plan','POST',form);assert.equal(plan.status,200);const planResult=await plan.json();assert.equal(planResult.geometry.portrait,true);
 assert.equal(calls.slice(before).filter(c=>c.method==='POST').length,0);
 const body={action:'publish',confirmation:'PUBLISH',form,planDigest:planResult.planDigest};
 assert.equal((await request(prefix+'/submit','POST',body,{'idempotency-key':'test-one'})).status,200);
 assert.equal((await request(prefix+'/submit','POST',body,{'idempotency-key':'test-one'})).status,200);
 const publishes=calls.filter(c=>c.url.endsWith('/publish'));assert.equal(publishes.length,1);
 assert.equal(publishes[0].data.persistSettings,false);assert.equal(publishes[0].data.wait,false);assert.equal(publishes[0].data.options.burnLayout.portraitBlurFill.enabled,false);
 assert.equal((await request(prefix+'/submission?key=test-one').then(r=>r.json())).result.job_id,10);
 assert.equal((await request(prefix+'/submit','POST',{action:'prepare',form,planDigest:planResult.planDigest},{'idempotency-key':'prep-one'})).status,200);
 assert.equal(calls.filter(c=>c.url.endsWith('/process')).length,1);
 assert.equal((await request(prefix+'/visibility','POST',{hidden:true})).status,200);
 assert.deepEqual((await request('/api/videos').then(r=>r.json())).videos,[]);
 assert.equal((await request('/api/videos?hidden=true').then(r=>r.json())).videos.length,1);
 await request(prefix+'/visibility','POST',{hidden:false});assert.equal((await request('/api/videos').then(r=>r.json())).videos.length,1);
 assert.equal(calls.filter(c=>c.method==='DELETE').length,0);
 jobs.push({video_id:1,status:'done',platforms:['youtube']});
 assert.equal((await request(prefix+'/submit','POST',body,{'idempotency-key':'test-two'})).status,409);
 assert.equal(calls.filter(c=>c.url.endsWith('/publish')).length,1);
 const changed=await request(prefix+'/submit','POST',{...body,form:{...form,lift:0.1,platforms:['instagram']}},{'idempotency-key':'changed-plan'});
 assert.equal(changed.status,409);assert.equal((await changed.json()).submissionState,'rejected');
 jobs.length=0;failPublish=true;
 assert.equal((await request(prefix+'/submit','POST',body,{'idempotency-key':'uncertain'})).status,502);
 assert.equal((await request(prefix+'/submission?key=uncertain').then(r=>r.json())).state,'submitting');
 assert.equal((await request(prefix+'/submit','POST',body,{'idempotency-key':'uncertain'})).status,409);
 assert.equal(calls.filter(c=>c.url.endsWith('/publish')).length,2,'unknown publication is not submitted twice');
 const linked=worker.auth.issue(owner,SCOPES);
 assert.equal((await request(prefix+'/composer','GET',null,{'x-studio-access':'Bearer '+linked.access_token})).status,403);
 assert.equal((await request(prefix+'/visibility','POST',{hidden:true},{origin:'https://foreign.test'})).status,403);
});
