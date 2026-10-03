import http from 'node:http';
import { readFileSync, mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { timingSafeEqual } from 'node:crypto';
import { createWorker } from '../studio/server.mjs';
import { SCOPES, fail } from '../studio/auth.mjs';
import { json, readJSON, validPath } from '../studio/transport.mjs';
import { forward } from './proxy.mjs';
import { assertWorkspaceIdle } from './lifecycle.mjs';
import { privateMusicInput } from './music-input.mjs';
import { AsyncLocalStorage } from 'node:async_hooks';
import { ProcessingMeter, processingLimit } from './processing.mjs';

export function createCell(config, seed) {
  const worker = createWorker(config), db = worker.auth.db;
  const requests = new AsyncLocalStorage();
  if(config.processingQuotas){
    const meter=new ProcessingMeter(db,config.dataRoot,config.durationProbe);
    config.processingRequest=(path,method,data,dispatch)=>meter.run(path,method,data,dispatch,requests.getStore());
    config.processingUsage=()=>meter.usage(processingLimit(requests.getStore()?.limit));
  }
  let desktopSocket;
  let closed = false;
  const exists = db.prepare('SELECT id FROM users').all();
  if (exists.some(r=>r.id!==seed.owner)) throw Error('Workspace already belongs to a different owner');
  db.prepare('INSERT OR IGNORE INTO users VALUES(?,?,?)').run(seed.owner,seed.username,seed.password);
  if(config.sampleMappingFile&&existsSync(config.sampleMappingFile)) {
    const sample=JSON.parse(readFileSync(config.sampleMappingFile));
    if(!Number.isSafeInteger(sample.videoId)||sample.videoId<1||sample.sha256!==config.sampleSha256||sample.filename!=='vancouver.mp4')throw Error('Authorized sample mapping mismatch');
    db.prepare('INSERT OR IGNORE INTO media VALUES(?,?,?,?)').run(sample.videoId,seed.owner,sample.sha256,sample.filename);
  }
  const token = readFileSync(config.upstreamSecretFile,'utf8').trim();
  const origin = `https://${config.host}`;
  function transport(req) {
    const supplied = Buffer.from(String(req.headers.authorization||'')), expected=Buffer.from(`Bearer ${token}`);
    if (supplied.length!==expected.length || !timingSafeEqual(supplied,expected)) fail(401,'Invalid transport');
    if (req.url!=='/studio/bridge') fail(404,'Not found');
    const raw=String(req.headers['x-studio-path']||'');if(!validPath(raw))fail(400,'Invalid path');return raw;
  }
  function browser(req) {
    const value=(req.headers.cookie||'').split(';').map(s=>s.trim()).find(s=>s.startsWith('__Host-studio='))?.slice(14);
    const p=worker.auth.principal(value);
    if(p.kind!=='browser'||p.owner!==seed.owner)fail(403,'Sign in to your Studio first');
    return p;
  }
  async function route(req,res,head) {
    if(req.url==='/healthz'&&req.method==='GET'&&head===undefined) return json(res,200,{status:'ok'});
    const raw=transport(req), path=raw.split('?')[0];
    if (['/hosted-close', '/hosted-check-idle'].includes(path) && req.method === 'POST' && head === undefined) {
      if (req.headers['x-hosted-owner'] !== seed.owner) fail(403, 'Operator transport required');
      await assertWorkspaceIdle(config.backendPort, config.publisherPort);
      if (path === '/hosted-check-idle') return json(res, 200, {ok: true});
      closed = true; desktopSocket?.destroy();
      db.prepare('UPDATE grants SET revoked=1').run();
      return json(res, 200, {ok: true});
    }
    if (closed) fail(401, 'Workspace closed');
    if(path==='/hosted-entry'&&req.method==='GET'&&head===undefined) {
      if(req.headers['x-hosted-owner']!==seed.owner)fail(401,'Entry link required');
      const t=worker.auth.issue(seed.owner,SCOPES,'Studio browser','browser');
      res.writeHead(303,{location:'/', 'cache-control':'no-store','referrer-policy':'no-referrer',
        'set-cookie':`__Host-studio=${t.access_token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200`});res.end();return;
    }
    if(path.startsWith('/platforms')) {
      browser(req);
      if(head!==undefined || req.method==='POST')if(req.headers.origin!==origin)fail(403,'Same-origin request required');
      if(['/platforms/open','/platforms/close'].includes(path)&&req.method==='POST'&&head===undefined) {
        const d=await readJSON(req,1024);
        if(!['shipinhao','instagram','youtube','douyin','xiaohongshu','bilibili'].includes(d.platform))fail(400,'Invalid platform');
        const r=await fetch(`http://127.0.0.1:${config.publisherPort||8081}/platform-login`,{method:path==='/platforms/close'?'DELETE':'POST',headers:{'content-type':'application/json'},body:JSON.stringify({platform:d.platform}),signal:AbortSignal.timeout(45000)});
        return json(res,r.status,await r.json());
      }
      if(path.startsWith('/platforms/desktop/')&&req.method==='GET'){
        if(head!==undefined){
          if(desktopSocket&&!desktopSocket.destroyed)fail(429,'Close the other desktop viewer first');
          desktopSocket=res;res.once('close',()=>{if(desktopSocket===res)desktopSocket=undefined;});
          res.setTimeout(300000,()=>res.destroy());
        }
        forward(req,res,{hostname:'127.0.0.1',port:config.desktopPort||6080,path:raw.slice('/platforms/desktop'.length),head});return;
      }
      if(head!==undefined)fail(404,'Not found');
      if(path==='/platforms'&&req.method==='GET'){
        res.writeHead(200,{'content-type':'text/html; charset=utf-8','cache-control':'no-store','x-frame-options':'SAMEORIGIN','referrer-policy':'no-referrer'});
        res.end(readFileSync(new URL('./web/platforms.html',import.meta.url)));return;
      }
      if(path==='/platforms/viewer.js'&&req.method==='GET'){
        res.writeHead(200,{'content-type':'text/javascript; charset=utf-8','cache-control':'private, max-age=300','x-content-type-options':'nosniff'});
        res.end(readFileSync(new URL('./web/viewer.js',import.meta.url)));return;
      }
      fail(404,'Not found');
    }
    if(path==='/api/music/package'&&req.method==='POST'&&head===undefined){
      browser(req);if(req.headers.origin!==origin)fail(403,'Same-origin request required');
      const input = privateMusicInput(await readJSON(req, 1024 * 1024), config.dataRoot);
      const reply = await fetch(`http://127.0.0.1:${config.backendPort}/api/music/package`, {
        method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify(input),
        signal:AbortSignal.timeout(600000), redirect:'error',
      });
      return json(res, reply.status, await reply.json());
    }
    if(head!==undefined)fail(404,'Not found');
    worker.server.emit('request',req,res);
  }
  const server=http.createServer((req,res)=>requests.run({limit:req.headers['x-studio-processing-minutes'],key:req.headers['idempotency-key']},
    ()=>route(req,res).catch(e=>{if(!res.headersSent)json(res,e.status||502,{error:e.status?e.message:'Workspace temporarily unavailable'});else res.destroy();})));
  server.on('upgrade',(req,socket,head)=>route(req,socket,head).catch(e=>socket.end(`HTTP/1.1 ${e.status||403} Forbidden\r\nConnection: close\r\n\r\n`)));
  server.on('close',()=>{desktopSocket?.destroy();worker.server.emit('close');});
  server.requestTimeout=900000;
  return {server,auth:worker.auth};
}
if(process.argv[1]===new URL(import.meta.url).pathname){
  const seed=JSON.parse(readFileSync('/bootstrap/account.json'));
  mkdirSync('/state/studio',{recursive:true});
  writeFileSync('/state/studio/transport',seed.transport,{mode:0o600});
  createCell({host:seed.host,database:'/state/studio/accounts.sqlite',upstreamSecretFile:'/state/studio/transport',
    dataRoot:'/state/data',backendPort:18787,webRoot:'/opt/lazyedit/studio/web',staticRoot:'/opt/lazyedit/webdist',python:'/opt/venv/bin/python',sourceRoot:'/opt/lazyedit',processingQuotas:true,
    ...(process.env.LAZYEDIT_SAMPLE_SHA256?{sampleMappingFile:'/state/studio/sample.json',sampleSha256:process.env.LAZYEDIT_SAMPLE_SHA256}:{})},seed).server.listen(18080,'0.0.0.0');
}
