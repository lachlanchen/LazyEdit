import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createGateway} from './gateway.mjs';
import {createCell} from './cell.mjs';
import {accountCapabilities} from './features.mjs';

const listen=server=>new Promise(r=>server.listen(0,'127.0.0.1',r));
test('publication is independently configured; invitations and subscriptions grant no publication rights',()=>{
  const registry={isAdmin:owner=>owner==='operator'};
  assert.equal(accountCapabilities({},registry,'operator').publishing,false);
  const config={publishing:{enabled:true,administrators:true,accountIds:['special']}};
  for(const owner of ['operator','special'])assert.equal(accountCapabilities(config,registry,owner).publishing,true);
  assert.deepEqual(accountCapabilities(config,registry,'reviewer'),{editing:true,publishing:false});
  config.publishing.enabled=false;
  assert.equal(accountCapabilities(config,registry,'operator').publishing,false);
});

test('editor member can prepare and preview; stale tokens and forged headers cannot post or open desktop',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-editor-capability-'));
  const config={database:join(dir,'registry.sqlite'),domain:'edit.test',workerHost:()=> '127.0.0.1',publishing:{enabled:true,accountIds:[]}};
  const gateway=createGateway(config);
  const owner=gateway.registry.register({username:'reviewer',password:'test-only-long-password',invitation:gateway.registry.invite()},'fixture');
  const w=gateway.registry.workspace(owner),host=gateway.registry.host(w),received=[];
  const backend=http.createServer(async(req,res)=>{
    let text='';for await(const bytes of req)text+=bytes;received.push({method:req.method,path:req.url});
    let reply={id:1,file_path:join(dir,'source.mp4')};
    if(req.url.startsWith('/api/ui-settings/'))reply={value:req.url.endsWith('/logo_settings')?{enabled:true,logoPath:'own-logo.png'}:req.url.endsWith('/translation_languages')?['zh-Hant','ja','en']:{}};
    if(req.url==='/api/languages')reply=req.method==='POST'?{codes:JSON.parse(text).languages,languages:JSON.parse(text).languages.map(code=>({code,name:code}))}:{languages:[]};
    if(req.url.endsWith('/publication-sessions'))reply={sessions:[]};
    if(req.url.endsWith('/process-status'))reply={steps:{},ready_for_publish:true};
    if(req.url.endsWith('/burn-subtitles'))reply={status:'completed',output_url:'/media/own-render.mp4'};
    if(req.url.endsWith('/process')||req.url.endsWith('/publish'))reply={status:'started'};
    res.setHeader('content-type','application/json');res.end(JSON.stringify(reply));
  });await listen(backend);writeFileSync(join(dir,'transport'),w.transport);
  const cell=createCell({host,database:join(dir,'cell.sqlite'),upstreamSecretFile:join(dir,'transport'),dataRoot:dir,backendPort:backend.address().port,
    publisherPort:backend.address().port,webRoot:dir,staticRoot:dir,geometry:async()=>({portrait:true,fill:false})},
    {...w,username:'reviewer',password:gateway.registry.db.prepare('SELECT password FROM users WHERE id=?').get(owner).password});
  await listen(cell.server);config.workerPort=cell.server.address().port;
  gateway.registry.db.prepare("UPDATE workspaces SET status='ready' WHERE id=?").run(w.id);await listen(gateway.server);
  t.after(()=>{for(const server of [gateway.server,cell.server,backend]){server.closeAllConnections();server.close();}cell.auth.db.close();gateway.registry.db.close();rmSync(dir,{recursive:true,force:true});});
  // Even a token issued before publication was disabled must be constrained now.
  const browser=cell.auth.issue(owner,undefined,'browser','browser'),device=cell.auth.issue(owner);
  cell.auth.db.prepare('INSERT INTO media VALUES(?,?,?,?)').run(1,owner,'a'.repeat(64),'source.mp4');
  async function request(path,body,token=false){
    return new Promise((resolve,reject)=>{
      const req=http.request({hostname:'127.0.0.1',port:gateway.server.address().port,path,method:body===undefined?'GET':'POST',headers:{host,origin:`https://${host}`,'content-type':'application/json',
        'x-studio-publishing':'1','idempotency-key':'fixture-'+path,...(token?{authorization:`Bearer ${device.access_token}`}:{cookie:`__Host-studio=${browser.access_token}`})}},res=>{
        let text='';res.on('data',v=>text+=v);res.on('end',()=>resolve({status:res.statusCode,body:JSON.parse(text)}));
      });req.on('error',reject);req.end(body===undefined?undefined:JSON.stringify(body));
    });
  }
  const me=await request('/auth/me');assert.equal(me.status,200,JSON.stringify(me.body));assert.equal(me.body.capabilities.publishing,false);assert.ok(!me.body.scopes.includes('publication.publish'));
  const composer=await request('/v1/studio/videos/1/composer');assert.equal(composer.status,200);assert.deepEqual(composer.body.defaults.platforms,[]);
  const form=composer.body.defaults,plan=await request('/v1/studio/videos/1/plan',form);
  const prepare={action:'prepare',form,planDigest:plan.body.planDigest};
  const prepared=await request('/v1/studio/videos/1/submit',prepare);assert.equal(prepared.status,200,JSON.stringify(prepared.body));
  assert.equal((await request('/api/videos/1/burn-subtitles')).body.output_url,'/media/own-render.mp4');
  assert.deepEqual((await request('/api/autopublish/queue')).body.jobs,[]);
  const count=received.length;
  for(const [path,body,token] of [
    ['/api/videos/1/publish',{platforms:['youtube']}],
    ['/api/videos/1/publish',{platforms:['youtube']},true],
    ['/v1/studio/videos/1/submit',{...prepare,action:'publish',confirmation:'PUBLISH'}],
    ['/api/music/package',{post:true,audio:'missing.mp3'}],
    ['/platforms/open',{platform:'shipinhao'}],['/platforms'],['/platforms/desktop/vnc.html'],
  ])assert.equal((await request(path,body,token)).status,403,path);
  assert.equal(received.length,count,'denied requests never reach processing, publisher or browser startup');
  assert.equal(cell.auth.db.prepare('SELECT count(*) n FROM intents').get().n,1,'no denied publication intent persisted');
  config.publishing.accountIds.push(owner);
  assert.equal((await request('/auth/me')).body.capabilities.publishing,true);
  assert.equal((await request('/api/videos/1/publish',{platforms:['youtube']})).status,200,'operator opt-in preserves the established publisher');
  config.publishing.enabled=false;
  assert.equal((await request('/api/videos/1/publish',{platforms:['youtube']})).status,403,'global pause applies even to an existing signed-in user');
});
