// Existing LazyEdge worker target: owner requests keep their original adapter.
import http from 'node:http';
import { readFileSync } from 'node:fs';
import { timingSafeEqual } from 'node:crypto';
import { createWorker } from '../studio/server.mjs';
import { json, validPath } from '../studio/transport.mjs';
import { fail } from '../studio/auth.mjs';
import { forward } from './proxy.mjs';

export function createIngress(config) {
  const owner=createWorker(config);
  const expected=Buffer.from(`Bearer ${readFileSync(config.upstreamSecretFile,'utf8').trim()}`);
  const gatewayToken=readFileSync(config.hostedIngressSecretFile,'utf8').trim();
  function route(req,res,head){
    try{
      if(req.url==='/healthz'&&head===undefined)return json(res,200,{status:'ok'});
      const supplied=Buffer.from(req.headers.authorization||'');
      if(req.url!=='/studio/bridge'||supplied.length!==expected.length||!timingSafeEqual(supplied,expected))fail(401,'Invalid transport');
      const raw=String(req.headers['x-studio-path']||'');if(!validPath(raw))fail(400,'Invalid path');
      const path=raw.split('?')[0];
      const hosted=path==='/accounts'||path.startsWith('/accounts/')||path.startsWith('/workspaces/')||
        (req.headers.cookie||'').split(';').some(c=>c.trim().startsWith('__Host-hosted='));
      if(hosted){
        forward(req,res,{hostname:'127.0.0.1',port:config.hostedPort||18980,path:raw,head,headers:{
          host:config.host,authorization:`Bearer ${gatewayToken}`,'x-studio-access':req.headers['x-studio-access']||'',
          'x-studio-client':req.headers['x-studio-client']||''}});return;
      }
      if(head!==undefined)fail(403,'Sign in to your private workspace');
      owner.server.emit('request',req,res);
    }catch(e){if(head!==undefined)res.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n');else json(res,e.status||500,{error:e.status?e.message:'Request failed'});}
  }
  const server=http.createServer((req,res)=>route(req,res));
  server.on('upgrade',(req,socket,head)=>route(req,socket,head));
  server.on('close',()=>{owner.server.emit('close');owner.auth.db.close();});
  server.requestTimeout=900000;
  return {server,owner};
}
if(process.argv[1]===new URL(import.meta.url).pathname){
  const config=JSON.parse(readFileSync(process.argv[2]));
  createIngress(config).server.listen(config.port,'127.0.0.1');
}
