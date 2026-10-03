import http from 'node:http';
import { readFileSync } from 'node:fs';
import { Registry } from './store.mjs';
import { fail } from '../studio/auth.mjs';
import { validPath, json, readJSON } from '../studio/transport.mjs';
import { forward } from './proxy.mjs';

export function createGateway(config) {
  const registry = new Registry(config.database, config.domain, config.capacity || 3);
  const origin = `https://${config.domain}`;
  function principal(req) {
    const token = (req.headers.cookie || '').split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-hosted='))?.slice(14);
    return registry.principal(token);
  }
  function session(res, owner) {
    const t = registry.issue(owner, undefined, 'Hosted Studio', 'browser');
    json(res,200,{ok:true},{'set-cookie':`__Host-hosted=${t.access_token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200`});
  }
  async function route(req, res, head) {
    if (!validPath(req.url)) fail(400,'Invalid path');
    const host = String(req.headers.host || '').toLowerCase().replace(/:443$/, '');
    const w = registry.route(host);
    if (w) {
      const headers = {host,'x-studio-path':req.url,'x-studio-access':req.headers.authorization || '',
        'x-studio-client':req.socket.remoteAddress, authorization:`Bearer ${w.transport}`};
      if (req.url.startsWith('/hosted-entry?')) {
        if (head !== undefined || req.method !== 'GET' || !registry.consume(new URL(req.url,origin).searchParams.get('ticket'),w.id)) fail(401,'Entry link expired; return to the account page');
        headers['x-hosted-owner'] = w.owner;
      }
      forward(req,res,{hostname:config.workerHost?.(w) || `le-${w.id}-worker`,port:config.workerPort || 18080,path:'/studio/bridge',headers,head});return;
    }
    if (host !== config.domain) fail(404,'Workspace unavailable');
    if (head !== undefined) fail(404,'WebSocket unavailable');
    if (req.method === 'POST' && req.headers.origin !== origin) fail(403,'Same-origin request required');
    const path = req.url.split('?')[0];
    if (req.method==='GET' && path==='/healthz') return json(res,200,{status:'ok'});
    if (req.method==='GET' && (path==='/' || path==='/index.js')) {
      res.writeHead(200,{'content-type':path==='/'?'text/html; charset=utf-8':'text/javascript',
        'content-security-policy':"default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        'cache-control':'no-store','referrer-policy':'no-referrer'});
      res.end(readFileSync(new URL(path==='/'?'./web/index.html':'./web/index.js',import.meta.url)));return;
    }
    if (req.method==='POST' && path==='/register') return session(res,registry.register(await readJSON(req,4096),req.socket.remoteAddress));
    if (req.method==='POST' && path==='/login') {
      const d=await readJSON(req,4096);return session(res,registry.login(String(d.username||''),String(d.password||''),req.socket.remoteAddress));
    }
    const p = principal(req);
    if (req.method==='GET' && path==='/account') {
      const w=registry.workspace(p.owner);return json(res,200,{username:registry.db.prepare('SELECT username FROM users WHERE id=?').get(p.owner).username,status:w.status,workspace:`https://${registry.host(w)}`});
    }
    if (req.method==='POST' && path==='/enter') return json(res,200,{url:registry.enter(p.owner)});
    if (req.method==='POST' && path==='/logout') {
      registry.revoke(p.owner,p.id);return json(res,200,{ok:true},{'set-cookie':'__Host-hosted=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'});
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
