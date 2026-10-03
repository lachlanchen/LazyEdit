import http from 'node:http';
import { readFileSync } from 'node:fs';
import { timingSafeEqual } from 'node:crypto';
import { Registry } from './store.mjs';
import { fail } from '../studio/auth.mjs';
import { validPath, json, readJSON } from '../studio/transport.mjs';
import { forward } from './proxy.mjs';

export function createGateway(config) {
  const registry = new Registry(config.database, config.domain, config.capacity || 3, config.sameHost);
  const origin = `https://${config.domain}`;
  const internal = config.ingressSecretFile && readFileSync(config.ingressSecretFile,'utf8').trim();
  const prefix = config.sameHost ? '/accounts' : '';
  const hostedCookie = req => (req.headers.cookie || '').split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-hosted='))?.slice(14);
  function principal(req) {
    const owner=internal&&req.headers['x-hosted-admin-owner'];
    if(!hostedCookie(req)&&owner&&registry.isAdmin(owner))return {owner,kind:'browser'};
    return registry.principal(hostedCookie(req));
  }
  function session(res, owner) {
    const t = registry.issue(owner, undefined, 'Hosted Studio', 'browser');
    json(res,200,{ok:true},{'set-cookie':`__Host-hosted=${t.access_token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200`});
  }
  async function route(req, res, head) {
    if(internal){const supplied=Buffer.from(req.headers.authorization||''),expected=Buffer.from(`Bearer ${internal}`);if(supplied.length!==expected.length||!timingSafeEqual(supplied,expected))fail(401,'Invalid ingress');}
    if (!validPath(req.url)) fail(400,'Invalid path');
    const host = String(req.headers.host || '').toLowerCase().replace(/:443$/, '');
    const access = internal ? String(req.headers['x-studio-access']||'') : String(req.headers.authorization||'');
    let raw=req.url, w=registry.route(host);
    if(config.sameHost){
      if(host!==config.domain)fail(404,'Workspace unavailable');
      const explicit=/^\/workspaces\/([a-f0-9]{24})(\/.*)$/.exec(raw);
      if(explicit){
        w=registry.db.prepare("SELECT * FROM workspaces WHERE id=? AND status='ready'").get(explicit[1]);raw=explicit[2];
        if(!w)fail(404,'Workspace unavailable');
        if(hostedCookie(req)&&principal(req).owner!==w.owner)fail(403,'Wrong workspace');
        const bootstrap=req.method==='POST'&&['/auth/login','/auth/token','/auth/device'].includes(raw.split('?')[0]);
        if(!access&&!bootstrap)fail(401,'Workspace API token required');
      }else if(!(raw.split('?')[0]===prefix||raw.startsWith(prefix+'/'))){
        w=registry.workspace(principal(req).owner);
        if(w?.status!=='ready')fail(409,'Workspace unavailable');
      }
    }
    if (w) {
      const headers = {host,'x-studio-path':raw,'x-studio-access':access,
        'x-studio-client':internal?req.headers['x-studio-client']:req.socket.remoteAddress, authorization:`Bearer ${w.transport}`};
      if (raw.startsWith('/hosted-entry?')) {
        if (head !== undefined || req.method !== 'GET' || !registry.consume(new URL(raw,origin).searchParams.get('ticket'),w.id)) fail(401,'Entry link expired; return to the account page');
        headers['x-hosted-owner'] = w.owner;
      }
      // In same-host mode signing out must also stop routing to this workspace.
      if(config.sameHost&&raw==='/auth/logout'&&req.method==='POST'&&hostedCookie(req)&&!access){
        if(req.headers.origin!==origin)fail(403,'Same-origin request required');
        const p=principal(req);registry.revoke(p.owner,p.id);
        return json(res,200,{ok:true},{'set-cookie':['__Host-hosted=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0','__Host-studio=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0']});
      }
      forward(req,res,{hostname:config.workerHost?.(w) || `le-${w.id}-worker`,port:typeof config.workerPort==='function'?config.workerPort(w):config.workerPort || 18080,path:'/studio/bridge',headers,head});return;
    }
    if (host !== config.domain) fail(404,'Workspace unavailable');
    if (head !== undefined) fail(404,'WebSocket unavailable');
    if (req.method === 'POST' && req.headers.origin !== origin) fail(403,'Same-origin request required');
    const path = req.url.split('?')[0].slice(prefix.length)||'/';
    const client=internal?req.headers['x-studio-client']:req.socket.remoteAddress;
    if (req.method==='GET' && path==='/healthz') return json(res,200,{status:'ok'});
    if(req.method==='GET'&&path==='/interface.js') {res.writeHead(200,{'content-type':'text/javascript','cache-control':'no-store'});res.end(readFileSync(new URL('../studio/web/interface.js',import.meta.url)));return;}
    if(req.method==='GET'&&/^\/locales\/(en|zh-Hans|zh-Hant|ja|ko|vi|ar|fr|es|de|ru)\.json$/.test(path)) {res.writeHead(200,{'content-type':'application/json','cache-control':'no-store'});res.end(readFileSync(new URL('../studio'+path,import.meta.url)));return;}
    if (req.method==='GET' && (path==='/' || path==='/index.js')) {
      res.writeHead(200,{'content-type':path==='/'?'text/html; charset=utf-8':'text/javascript',
        'content-security-policy':"default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        'cache-control':'no-store','referrer-policy':'no-referrer'});
      res.end(readFileSync(new URL(path==='/'?'./web/index.html':'./web/index.js',import.meta.url),'utf8').replaceAll('"/index.js"',`"${prefix}/index.js"`));return;
    }
    if (req.method==='POST' && path==='/register') return session(res,registry.register(await readJSON(req,4096),client));
    if (req.method==='POST' && path==='/login') {
      const d=await readJSON(req,4096);return session(res,registry.login(String(d.username||''),String(d.password||''),client));
    }
    const p = principal(req);
    if (req.method==='GET' && path==='/account') {
      const w=registry.workspace(p.owner);return json(res,200,{subject:p.owner,role:registry.isAdmin(p.owner)?'admin':'member',mode:hostedCookie(req)?'workspace':'owner',username:registry.db.prepare('SELECT username FROM users WHERE id=?').get(p.owner).username,status:w?.status||'not_created',workspace:w?`https://${registry.host(w)}`:null,apiBase:w?`https://${registry.host(w)}${config.sameHost?'/workspaces/'+w.id:''}`:null});
    }
    if(req.method==='POST'&&path==='/invite'){
      if(!registry.isAdmin(p.owner))fail(403,'Administrator required');
      registry.throttle(`invite:${p.owner}`);
      const token=registry.invite();return json(res,201,{url:`${origin}${prefix}?invitation=${token}`,expiresIn:72*3600});
    }
    if(req.method==='POST'&&path==='/docker'){
      registry.ensureWorkspace(p.owner);return session(res,p.owner);
    }
    if (req.method==='POST' && path==='/enter') return json(res,200,{url:registry.enter(p.owner)});
    if (req.method==='POST' && path==='/logout') {
      if(p.id)registry.revoke(p.owner,p.id);return json(res,200,{ok:true},{'set-cookie':['__Host-hosted=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0','__Host-studio=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0']});
    }
    fail(404,'Not found');
  }
  const server=http.createServer((req,res)=>route(req,res).catch(e=>{if(!res.headersSent)json(res,e.status||500,{error:e.status?e.message:'Request failed'});else res.destroy();}));
  server.on('upgrade',(req,socket,head)=>route(req,socket,head).catch(()=>socket.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n')));
  server.requestTimeout=900000;
  return {server,registry};
}
if (process.argv[1]===new URL(import.meta.url).pathname) {
  const config=JSON.parse(readFileSync(process.argv[2]));
  createGateway(config).server.listen(config.port || 8080,'0.0.0.0');
}
