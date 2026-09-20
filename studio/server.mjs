import http from 'node:http';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync, realpathSync, renameSync, unlinkSync, openSync, closeSync, writeSync, ftruncateSync } from 'node:fs';
import { createReadStream } from 'node:fs';
import { resolve, join, extname, basename, sep } from 'node:path';
import { createHash, timingSafeEqual } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { AuthStore, SCOPES, fail, secret, digest } from './auth.mjs';
import { json, body, readJSON, proxy, validPath, startEdge } from './transport.mjs';
process.umask(0o077);
const exec = promisify(execFile);
const MIME={'.html':'text/html; charset=utf-8','.js':'application/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.ico':'image/x-icon','.json':'application/json','.webmanifest':'application/manifest+json','.ttf':'font/ttf','.woff2':'font/woff2','.mp4':'video/mp4','.mov':'video/quicktime'};
export function safeFilename(value){
  const name=String(value||'video.mp4').normalize('NFC');
  if(name!==basename(name)||!name||name.length>180||/[\\\x00-\x1f]/.test(name)||name.startsWith('.')||!['.mp4','.mov','.m4v','.webm'].includes(extname(name).toLowerCase()))fail(400,'Invalid video filename');
  return name;
}
const numeric=v=>{if(!/^\d+$/.test(String(v))||Number(v)<1||!Number.isSafeInteger(Number(v)))fail(400,'Invalid video ID');return Number(v);};
const clean=value=>Array.isArray(value)?value.map(clean):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).filter(([k])=>!/password|secret|authorization|cookie|credential|file_path|zip_path|local_path|logoPath|source_video_path|output_path/i.test(k)).map(([k,v])=>[k,clean(v)])):value;
export function createWorker(config) {
 const auth=new AuthStore(config.database),db=auth.db, origin=`https://${config.host}`;
 const upstream=readFileSync(config.upstreamSecretFile,'utf8').trim();
 const root=resolve(config.dataRoot), incoming=join(root,'studio_uploads');mkdirSync(incoming,{recursive:true,mode:0o700});
 const locks=new Set();
 async function backend(path,method='GET',data){
  const r=await fetch(`http://127.0.0.1:${config.backendPort}${path}`,{method,headers:data?{'content-type':'application/json'}:{},body:data?JSON.stringify(data):undefined,signal:AbortSignal.timeout(600000)});
  const text=await r.text();let d;try{d=JSON.parse(text)}catch{fail(502,'Unexpected worker reply');}if(!r.ok)fail(r.status,d.error||'Worker request failed');return d;
 }
 function getPrincipal(req){
  let token=req.headers['x-studio-access'];let browser=false;
  if(token?.startsWith('Bearer '))token=token.slice(7);
  else{token=(req.headers.cookie||'').split(';').map(v=>v.trim()).find(v=>v.startsWith('__Host-studio='))?.split('=')[1];browser=true;}
  const p=auth.principal(token);
  if(browser&&p.kind!=='browser')fail(401,'Invalid browser session');
  if(browser&&!['GET','HEAD','OPTIONS'].includes(req.method)&&req.headers.origin!==origin)fail(403,'Same-origin browser request required');
  return p;
 }
 function scope(p,value){if(!p.scopes.includes(value))fail(403,'Required scope: '+value);}
 function publicJSON(res,value,status=200){json(res,status,clean(value));}
 function file(res,req,path){
  const stat=statSync(path);let start=0,end=stat.size-1,status=200;
  if(req.headers.range){const m=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);if(!m)fail(416,'Invalid range');if(!m[1])start=Math.max(0,stat.size-Number(m[2]));else{start=Number(m[1]);if(m[2])end=Number(m[2]);}if(start>end||end>=stat.size||start<0)fail(416,'Unsatisfiable range');status=206;}
  res.writeHead(status,{'content-type':MIME[extname(path).toLowerCase()]||'application/octet-stream','content-length':end-start+1,'cache-control':'no-store','accept-ranges':'bytes','x-content-type-options':'nosniff',...(status===206?{'content-range':`bytes ${start}-${end}/${stat.size}`}:{})});
  if(req.method==='HEAD'){res.end();return;}const stream=createReadStream(path,{start,end});res.on('close',()=>stream.destroy());stream.pipe(res);
 }
 function ownedUpload(id,p){const r=db.prepare('SELECT * FROM uploads WHERE id=? AND owner=?').get(id,p.owner);if(!r||r.expires<Date.now())fail(404,'Upload unavailable');return r;}
 async function allocate(p,d){
  scope(p,'media.upload');const filename=safeFilename(d.filename),size=Number(d.size);
  if(!Number.isSafeInteger(size)||size<1||size>10*1024**3)fail(413,'Video size must be between 1 byte and 10 GiB');
  if(d.sha256&&!/^[a-f0-9]{64}$/i.test(d.sha256))fail(400,'Invalid SHA-256');
  const count=db.prepare('SELECT count(*) n FROM uploads WHERE owner=? AND receipt IS NULL AND expires>?').get(p.owner,Date.now()).n;if(count>=10)fail(429,'Too many incomplete uploads');
  const {statfs}=await import('node:fs/promises');const s=await statfs(root);if(s.bavail*s.bsize < size+2*1024**3)fail(507,'Not enough local storage');
  const id=secret();writeFileSync(join(incoming,id+'.part'),'',{mode:0o600,flag:'wx'});
  db.prepare('INSERT INTO uploads(id,owner,filename,title,size,sha256,expires) VALUES(?,?,?,?,?,?,?)').run(id,p.owner,filename,String(d.title||filename).slice(0,240),size,(d.sha256||'').toLowerCase(),Date.now()+86400000);
  return {uploadId:id,offset:0,chunkBytes:8*1024**2,size,expiresIn:86400};
 }
 async function append(req,p,id,offset){
  const row=ownedUpload(id,p);if(row.receipt)fail(409,'Already finalized');if(offset!==row.offset)fail(409,'Wrong upload offset');if(locks.has(id))fail(409,'Upload is busy');locks.add(id);
  const path=join(incoming,id+'.part');let fd,position=offset,chunk=0;
  try{fd=openSync(path,'r+');for await(const c of req){chunk+=c.length;if(chunk>16*1024**2||position+c.length>row.size)fail(413,'Chunk exceeds upload limit');writeSync(fd,c,0,c.length,position);position+=c.length;}db.prepare('UPDATE uploads SET offset=? WHERE id=?').run(position,id);return {uploadId:id,offset:position,size:row.size};}
  catch(e){if(fd!==undefined)ftruncateSync(fd,offset);throw e;}finally{if(fd!==undefined)closeSync(fd);locks.delete(id);}
 }
 async function finalize(p,id){
  const row=ownedUpload(id,p);if(row.receipt)return JSON.parse(row.receipt);if(row.offset!==row.size)fail(409,'Upload incomplete');if(locks.has(id))fail(409,'Upload is busy');locks.add(id);
  try{
   const part=join(incoming,id+'.part'),dir=join(root,'studio_'+id),dest=join(dir,row.filename),src=existsSync(dest)?dest:part;
   const hash=createHash('sha256');for await(const c of createReadStream(src))hash.update(c);const sha=hash.digest('hex');
   if(row.sha256&&sha!==row.sha256)fail(422,'SHA-256 mismatch');
   let probe;try{probe=JSON.parse((await exec('ffprobe',['-v','error','-show_streams','-of','json',src],{timeout:30000,maxBuffer:1024**2})).stdout);}catch{fail(422,'Invalid video');}
   if(!probe.streams.some(s=>s.codec_type==='video'))fail(422,'No video stream');
   mkdirSync(dir,{recursive:true,mode:0o700});if(src===part)renameSync(part,dest);
   const b=await backend('/api/videos','POST',{file_path:dest,title:row.title,source:p.kind==='browser'?'upload':'api'});
   const videoId=Number(b.id||b.video_id);if(!videoId)fail(502,'Registration failed');
   db.prepare('INSERT OR REPLACE INTO media VALUES(?,?,?,?)').run(videoId,p.owner,sha,row.filename);
   const receipt={schemaVersion:'lazyedit_media_receipt.v1',videoId,video_id:videoId,id:videoId,filename:row.filename,sha256:sha,byteLength:row.size,media_url:b.media_url,preview_media_url:b.preview_media_url||b.media_url,rawMediaRetainedByBridge:false};
   db.prepare('UPDATE uploads SET receipt=? WHERE id=?').run(JSON.stringify(receipt),id);return receipt;
  }finally{locks.delete(id);}
 }
 async function directUpload(req,p,u){
  const sha=req.headers['x-content-sha256']||'';
  if(p.kind!=='browser'&&!sha)fail(400,'X-Content-SHA256 required');
  const a=await allocate(p,{filename:u.searchParams.get('filename'),title:u.searchParams.get('title'),size:req.headers['content-length'],sha256:sha});
  const fd=openSync(join(incoming,a.uploadId+'.part'),'r+');let n=0;
  try{for await(const c of req){n+=c.length;if(n>a.size)fail(413,'Declared size exceeded');writeSync(fd,c);}db.prepare('UPDATE uploads SET offset=? WHERE id=?').run(n,a.uploadId);}finally{closeSync(fd);}
  return finalize(p,a.uploadId);
 }
 async function once(p,req,payload,execute){
  const key=req.headers['idempotency-key'];if(typeof key!=='string'||!key||key.length>128)fail(400,'Idempotency-Key required');
  const fingerprint=digest(JSON.stringify(payload));const prior=db.prepare('SELECT * FROM intents WHERE owner=? AND key=?').get(p.owner,key);
  if(prior){if(prior.fingerprint!==fingerprint)fail(409,'Idempotency conflict');if(prior.response)return JSON.parse(prior.response);fail(409,'Submission pending reconciliation; do not retry with another key');}
  const id=secret();db.prepare('INSERT INTO intents VALUES(?,?,?,?,?,?,?)').run(id,p.owner,key,fingerprint,null,'submitting',Date.now());
  // Persist BEFORE dispatch. A crash or unknown timeout must not submit a second task.
  const result=await execute();db.prepare('UPDATE intents SET state=?,response=? WHERE id=?').run('submitted',JSON.stringify(clean(result)),id);return result;
 }
 async function route(req,res){
  if(req.url==='/healthz'&&req.method==='GET'){json(res,200,{status:'ok'});return;}
  const supplied=String(req.headers.authorization||'');const expected='Bearer '+upstream;
  if(supplied.length!==expected.length||!timingSafeEqual(Buffer.from(supplied),Buffer.from(expected)))fail(401,'Invalid transport credential');
  if(req.url==='/healthz'){json(res,200,{status:'ok'});return;}
  if(req.url!=='/studio/bridge')fail(404,'Route not exposed');
  const raw=String(req.headers['x-studio-path']||'');if(!validPath(raw))fail(400,'Invalid path');
  const u=new URL(raw,origin),path=u.pathname,method=req.method,client=String(req.headers['x-studio-client']||'unknown');
  if(path==='/v1/studio/health'&&method==='GET'){json(res,200,{status:'ok',service:'LazyEdit Studio',apiVersion:'1'});return;}
  if(path==='/auth/login'&&method==='POST'){
   if(req.headers.origin&&req.headers.origin!==origin)fail(403,'Invalid origin');const d=await readJSON(req,8192);const owner=auth.login(String(d.username||''),String(d.password||''),client);
   if(d.mode==='token'){json(res,200,auth.issue(owner,d.scopes||SCOPES,d.client_name||'LightMind'));return;}
   if(req.headers.origin!==origin)fail(403,'Browser login requires same origin');
   const t=auth.issue(owner,SCOPES,'Studio browser','browser');json(res,200,{ok:true},{'set-cookie':`__Host-studio=${t.access_token}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=43200`});return;
  }
  if(path==='/auth/token'&&method==='POST'){
   const d=await readJSON(req,8192);
   const t=d.grant_type==='refresh_token'?auth.refresh(d.refresh_token):d.grant_type==='urn:ietf:params:oauth:grant-type:device_code'?auth.poll(d.device_code):fail(400,'Unsupported grant_type');json(res,200,t);return;
  }
  if(path==='/auth/device'&&method==='POST'){
   const d=await readJSON(req,8192),r=auth.device(d.scopes||SCOPES.filter(s=>s!=='publication.publish'),d.client_name,client);json(res,200,{...r,verification_uri:origin+'/connect'});return;
  }
  if(['/login','/connect','/privacy','/studio-login.js','/studio-login.css','/studio-session.js','/manifest.webmanifest','/sw.js','/studio-icon.png'].includes(path)&&['GET','HEAD'].includes(method)){
   const files={'/login':'login.html','/connect':'login.html','/privacy':'privacy.html','/studio-login.js':'login.js','/studio-login.css':'login.css','/studio-session.js':'session.js','/manifest.webmanifest':'manifest.webmanifest','/sw.js':'sw.js','/studio-icon.png':'icon.png'};file(res,req,join(config.webRoot,files[path]));return;
  }
  let p;try{p=getPrincipal(req);}catch(e){if(method==='GET'&&!path.startsWith('/api/')&&!path.startsWith('/v1/')&&!path.startsWith('/auth/')&&!path.startsWith('/media/')){res.writeHead(302,{location:'/login','cache-control':'no-store'});res.end();return;}throw e;}
  if(path==='/auth/me'&&method==='GET'||path==='/v1/studio/account'&&method==='GET'){json(res,200,{subject:p.owner,username:db.prepare('SELECT username FROM users WHERE id=?').get(p.owner).username,scopes:p.scopes,issuer:origin,audience:'lazyedit-studio',limits:{maxVideoBytes:10*1024**3,chunkBytes:8*1024**2}});return;}
  if(path==='/auth/logout'&&method==='POST'){auth.revoke(p.owner,p.id);json(res,200,{ok:true},{'set-cookie':'__Host-studio=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0'});return;}
  if(path==='/auth/approve'&&method==='POST'){if(p.kind!=='browser')fail(403,'Browser consent required');const d=await readJSON(req,8192);auth.approve(p.owner,String(d.user_code||'').toUpperCase());json(res,200,{ok:true});return;}
  if(path==='/auth/device-info'&&method==='GET'){if(p.kind!=='browser')fail(403,'Browser consent required');const d=db.prepare('SELECT code,label,scopes FROM devices WHERE code=? AND expires>? AND approved=0').get(u.searchParams.get('code'),Date.now());if(!d)fail(404,'Code unavailable');json(res,200,{...d,scopes:JSON.parse(d.scopes)});return;}
  if(path==='/auth/grants'&&method==='GET'){json(res,200,{grants:db.prepare('SELECT id,label,scopes,kind,created FROM grants WHERE owner=? AND revoked=0').all(p.owner).map(g=>({...g,scopes:JSON.parse(g.scopes)}))});return;}
  if(path==='/auth/revoke'&&method==='POST'){const d=await readJSON(req,8192);auth.revoke(p.owner,String(d.grant_id));json(res,200,{ok:true});return;}
  if(path==='/v1/studio/uploads'&&method==='POST'){json(res,201,await allocate(p,await readJSON(req)));return;}
  if(path==='/v1/studio/upload'&&method==='GET'){const r=ownedUpload(u.searchParams.get('uploadId'),p);json(res,200,{uploadId:r.id,offset:r.offset,size:r.size,receipt:r.receipt?JSON.parse(r.receipt):null});return;}
  if(path==='/v1/studio/upload'&&method==='DELETE'){const r=ownedUpload(u.searchParams.get('uploadId'),p);if(r.receipt)fail(409,'Completed media is retained');if(locks.has(r.id))fail(409,'Upload busy');try{unlinkSync(join(incoming,r.id+'.part'))}catch{}db.prepare('DELETE FROM uploads WHERE id=?').run(r.id);json(res,200,{ok:true});return;}
  if(path==='/v1/studio/upload-part'&&method==='PUT'){scope(p,'media.upload');json(res,200,await append(req,p,u.searchParams.get('uploadId'),Number(req.headers['upload-offset'])));return;}
  if(path==='/v1/studio/upload-complete'&&method==='POST'){scope(p,'media.upload');json(res,200,await finalize(p,(await readJSON(req)).uploadId));return;}
  if(['/upload-stream','/v1/studio/media'].includes(path)&&method==='PUT'){json(res,200,await directUpload(req,p,u));return;}
  if(path==='/v1/studio/capabilities'&&method==='GET'){json(res,200,{apiVersion:'1',legacyBridgeCompatible:true,resumableUpload:true,accountLink:'device-authorization',publicRegistration:false,platforms:['shipinhao','instagram','youtube','douyin','xiaohongshu','bilibili'],scopes:p.scopes});return;}
  if(path==='/v1/studio/artifact'&&method==='GET'){
   scope(p,'publication.prepare');const id=numeric(u.searchParams.get('videoId'));auth.own(p,id);
   const b=await backend(`/api/videos/${id}/burn-subtitles`);if(b.status!=='completed'||!b.output_path)fail(409,'Render incomplete');
   const target=realpathSync(b.output_path);if(!target.startsWith(realpathSync(root)+sep))fail(409,'Render outside data root');
   const h=createHash('sha256');for await(const c of createReadStream(target))h.update(c);
   json(res,200,{videoId:id,sha256:h.digest('hex'),byteLength:statSync(target).size,media_url:b.output_url,config:clean(b.config)});return;
  }
  // Owner browser uses the established editor. Linked applications have explicit object/scope checks.
  if(path==='/api/videos'&&method==='GET'){
   scope(p,'media.read');const d=await backend(raw);if(p.kind!=='browser')d.videos=d.videos.filter(v=>db.prepare('SELECT 1 FROM media WHERE video_id=? AND owner=?').get(v.id,p.owner));if(p.kind==='browser')json(res,200,d);else publicJSON(res,d);return;
  }
  if(path==='/api/autopublish/queue'&&method==='GET'){
   scope(p,'jobs.read');const d=await backend(raw);if(p.kind!=='browser')d.jobs=d.jobs.filter(j=>db.prepare('SELECT 1 FROM media WHERE video_id=? AND owner=?').get(j.video_id,p.owner));if(p.kind==='browser')json(res,200,d);else publicJSON(res,d);return;
  }
  const videoMatch=/^\/api\/videos\/(\d+)(?:\/(proxy|transcribe|transcription|polish-subtitles|subtitle-correction|import-subtitles|publication-sessions(?:\/\d+)?|caption|captions|metadata|cover|keyframes|translate|translation|translations|burn-subtitles|process|process-status|publish))?$/.exec(path);
  if(videoMatch){
   const id=numeric(videoMatch[1]),action=videoMatch[2];auth.own(p,id);scope(p,method==='GET'?'media.read':action==='publish'?'publication.publish':'edit.submit');
   if(!['GET','POST','DELETE'].includes(method)||method==='DELETE'&&p.kind!=='browser')fail(405,'Method not allowed');
   let d=method==='POST'?await readJSON(req,1024**2):undefined;
   if(p.kind!=='browser'&&method==='POST'){
    if(d.publicationSessionId||u.searchParams.has('publicationSessionId'))fail(400,'Native API uses current output; select historical runs in Studio');
    if(!['process','publish','subtitle-correction'].includes(action))fail(403,'Operation reserved for Studio owner UI');
    if(action==='process'){const allowed=['steps','translationLanguages','translation_languages','burnSubtitles','usePolishedSubtitles','subtitleSourceVersion','notes','polish_notes','async','burnLayout','publicationSessionId','autoCorrectSubtitles','autoCorrectPrompt'];if(Object.keys(d).some(k=>!allowed.includes(k)))fail(400,'Unsupported process option');d.async=true;d.publicationMode='override';return void publicJSON(res,await once(p,req,{path,data:d},()=>backend(raw,'POST',d)));}
    if(action==='publish'){
     if(d.reviewApproved!==true||Number(d.reviewedVideoId)!==id||d.confirmation!=='PUBLISH_REVIEWED_MEDIA'||d.productionConfirmation!=='PUBLISH_REVIEWED_MEDIA_PRODUCTION')fail(400,'Explicit reviewed-media production approval required');
     const status=await backend(`/api/videos/${id}/process-status`);if(!status.ready_for_publish)fail(409,'Media is not ready for publication');
     if(!/^[a-f0-9]{64}$/.test(d.reviewedSha256||''))fail(400,'reviewedSha256 required');
     const burn=await backend(`/api/videos/${id}/burn-subtitles`);const target=burn.output_path||burn.outputPath;
     if(burn.status!=='completed'||!target||!realpathSync(target).startsWith(realpathSync(root)+sep))fail(409,'Rendered artifact unavailable');
     const h=createHash('sha256');for await(const c of createReadStream(target))h.update(c);if(h.digest('hex')!==d.reviewedSha256)fail(409,'Reviewed render has changed');
     if(d.options && Object.keys(d.options).some(k=>k!=='publishCategory'))fail(400,'Rendering changes require processing and another review');
     if(!Array.isArray(d.platforms)||!d.platforms.length||d.platforms.some(k=>!['shipinhao','instagram','youtube','douyin','xiaohongshu','bilibili'].includes(k)))fail(400,'Invalid platforms');
     const render=burn.config||{};
     const options={...d.options,burnSubtitles:render.burnSubtitles!==false,translationLanguages:(render.slots||[]).map(s=>s.language).filter(Boolean),usePolishedSubtitles:render.usePolishedSubtitles!==false,burnLayout:render,logo:render.logo||{enabled:false},publicationMode:'override',autoCorrectSubtitles:false,metadataPrompt:'',useCorrectionPromptForMetadata:false};
     const result=await once(p,req,{path,data:d},()=>backend(path,'POST',{platforms:d.platforms,options,persistSettings:false,wait:false}));publicJSON(res,result);return;
    }
   }
   const result=await backend(raw,method,d);if(p.kind==='browser')json(res,200,result);else publicJSON(res,result);return;
  }
  if(path.startsWith('/media/')&&['GET','HEAD'].includes(method)){
   scope(p,'media.read');const target=resolve(root,decodeURIComponent(path.slice(7)));if(!target.startsWith(root+sep)||!existsSync(target)||!realpathSync(target).startsWith(root+sep))fail(404,'Media unavailable');
   if(p.kind!=='browser'){const items=db.prepare('SELECT video_id FROM media WHERE owner=?').all(p.owner);let allowed=false;for(const item of items){const v=await backend('/api/videos/'+item.video_id);if(v.file_path&&target.startsWith(resolve(v.file_path,'..')+sep))allowed=true;}if(!allowed)fail(403,'Media unavailable');}
   file(res,req,target);return;
  }
  if(p.kind==='browser'){
   if(/^\/api\/(languages|video-specs|video-prompts|grammar-palettes\/[A-Za-z_-]+|ui-settings\/[A-Za-z_-]+)$/.test(path)&&['GET','POST'].includes(method)) {const result=await backend(raw,method,method==='POST'?await readJSON(req,1024**2):undefined);json(res,200,result);return;}
   if(/^\/api\/autopublish\/jobs\/[^/]+\/attention\/\d+$/.test(path)&&method==='GET'){await proxy(req,res,{port:config.backendPort,path:raw});return;}
   if(['/upload-image','/upload-logo','/upload'].includes(path)&&method==='POST'){await proxy(req,res,{port:config.backendPort,path:raw});return;}
   if(['GET','HEAD'].includes(method)&&!path.startsWith('/api/')&&!path.startsWith('/v1/')&&!path.startsWith('/auth/')){
    const relative=decodeURIComponent(path),candidate=resolve(config.staticRoot,'.'+relative);if(!candidate.startsWith(resolve(config.staticRoot)+sep)&&candidate!==resolve(config.staticRoot))fail(404,'Not found');
    if(existsSync(candidate)&&statSync(candidate).isFile()){file(res,req,candidate);return;}if(extname(path))fail(404,'Not found');file(res,req,join(config.staticRoot,'index.html'));return;
   }
  }
  fail(404,'Route not exposed');
 }
 const cleanup=setInterval(()=>{for(const r of db.prepare('SELECT id FROM uploads WHERE expires<? AND receipt IS NULL').all(Date.now())){if(locks.has(r.id))continue;try{unlinkSync(join(incoming,r.id+'.part'));}catch{}db.prepare('DELETE FROM uploads WHERE id=?').run(r.id);}},3600000);cleanup.unref();
 const server=http.createServer((req,res)=>{route(req,res).catch(e=>{if(res.headersSent){res.destroy();return;}json(res,e.status||500,{error:e.status?e.message:'Studio request failed'});});});
 server.on('close',()=>clearInterval(cleanup));server.requestTimeout=900000;
 return {server,auth,backend};
}
if(process.argv[1]===new URL(import.meta.url).pathname){
 const config=JSON.parse(readFileSync(process.argv[2],'utf8'));
 if(config.role==='edge')startEdge(config).listen(config.port,'127.0.0.1');
 else createWorker(config).server.listen(config.port,'127.0.0.1');
 console.log('LazyEdit Studio',config.role,'listening on loopback port',config.port);
}
