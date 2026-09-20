import http from 'node:http';
import { readFileSync } from 'node:fs';
import { pipeline } from 'node:stream';
import { isIP } from 'node:net';

export function json(res,status,value,headers={}) {
  const body=Buffer.from(JSON.stringify(value));res.writeHead(status,{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff','content-length':body.length,...headers});res.end(body);
}
export async function body(req,max=262144) {
  let size=0;const chunks=[];
  for await(const c of req) {size+=c.length;if(size>max)throw Object.assign(new Error('Request too large'),{status:413});chunks.push(c);}
  return Buffer.concat(chunks);
}
export async function readJSON(req,max=262144) {
  try { return JSON.parse((await body(req,max)).toString()||'{}'); } catch(e){if(e.status)throw e;throw Object.assign(new Error('Invalid JSON'),{status:400});}
}
export function validPath(raw) {
  if(!raw.startsWith('/')||raw.startsWith('//')||raw.length>8192||/[\\\x00-\x1f]/.test(raw)||/%(?:2f|5c|00|25)/i.test(raw.split('?')[0]))return false;
  try {const p=decodeURIComponent(raw.split('?')[0]);return !p.split('/').some(s=>s==='..'||s==='.')&&!p.includes('//');}catch{return false;}
}
const pass=['content-type','range','if-range','if-none-match','content-length','cookie','origin','x-content-sha256','upload-offset','idempotency-key','accept','content-range'];
export function proxy(req,res,{port,path,headers={},max=268435456}) {
  return new Promise(resolve=>{
    if(Number(req.headers['content-length']||0)>max){json(res,413,{error:'Request too large'});resolve();return;}
    const h={};for(const k of pass)if(req.headers[k])h[k]=req.headers[k];Object.assign(h,headers);
    const up=http.request({hostname:'127.0.0.1',port,path,method:req.method,headers:h},ur=>{
      const out={};for(const [k,v]of Object.entries(ur.headers))if(!['connection','transfer-encoding','authorization','x-lazyedge-relay-token','access-control-allow-origin','access-control-allow-credentials'].includes(k))out[k]=v;
      out['cache-control']='no-store';out['x-content-type-options']='nosniff';res.writeHead(ur.statusCode,out);pipeline(ur,res,()=>resolve());
    });
    up.setTimeout(900000,()=>up.destroy(new Error('Upstream timeout')));
    up.on('error',()=>{if(!res.headersSent)json(res,503,{error:'Studio worker unavailable'});else res.destroy();resolve();});
    res.on('close',()=>up.destroy());let size=0;
    req.on('data',c=>{size+=c.length;if(size>max)up.destroy();});pipeline(req,up,()=>{});
  });
}
export function startEdge(config) {
  const token=readFileSync(config.clientTokenFile,'utf8').trim();
  return http.createServer((req,res)=>{
    if(req.headers.host!==config.host && req.headers.host!==`${config.host}:443`){json(res,421,{error:'Unknown host'});return;}
    if(!validPath(req.url)){json(res,400,{error:'Invalid path'});return;}
    // Strip all caller-supplied internal identity/path headers. Only the worker authenticates the user's credential.
    // This listener is loopback-only. Caddy overwrites X-Studio-Peer with its
    // actual socket peer; never trust the public caller's forwarding headers.
    const peer=String(req.headers['x-studio-peer']||'');
    if(!isIP(peer)){json(res,400,{error:'Ingress identity unavailable'});return;}
    proxy(req,res,{port:config.gatewayPort,path:'/studio/bridge',headers:{host:config.host,'x-studio-path':req.url,'x-studio-access':String(req.headers.authorization||''),'x-studio-client':peer,authorization:`Bearer ${token}`}});
  });
}
