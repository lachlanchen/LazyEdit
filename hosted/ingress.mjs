// Existing LazyEdge worker target: owner requests keep their original adapter.
import http from 'node:http';
import { readFileSync } from 'node:fs';
import { timingSafeEqual } from 'node:crypto';
import { createWorker } from '../studio/server.mjs';
import { json, validPath } from '../studio/transport.mjs';
import { fail } from '../studio/auth.mjs';
import { forward } from './proxy.mjs';

export function createIngress(config) {
  const owner=createWorker({...config,ownerUsername:config.hostedAdminUsername});
  const expected=Buffer.from(`Bearer ${readFileSync(config.upstreamSecretFile,'utf8').trim()}`);
  const gatewayToken=readFileSync(config.hostedIngressSecretFile,'utf8').trim();
  function accountRequest(path,headers,method='GET') {
    return new Promise((resolve,reject)=>{
      const request=http.request({hostname:'127.0.0.1',port:config.hostedPort||18980,path,headers,method},response=>{
        let data='';response.on('data',chunk=>{data+=chunk;if(data.length>8192)request.destroy();});
        response.on('end',()=>{try{resolve({ok:response.statusCode===200,status:response.statusCode,data:JSON.parse(data)});}catch{reject(Object.assign(new Error('Invalid account response'),{status:503}));}});
      });
      request.setTimeout(10000,()=>request.destroy());request.on('error',()=>reject(Object.assign(new Error('Account service unavailable'),{status:503})));request.end();
    });
  }
  async function route(req,res,head){
    try{
      if(req.url==='/healthz'&&head===undefined)return json(res,200,{status:'ok'});
      const supplied=Buffer.from(req.headers.authorization||'');
      if(req.url!=='/studio/bridge'||supplied.length!==expected.length||!timingSafeEqual(supplied,expected))fail(401,'Invalid transport');
      const raw=String(req.headers['x-studio-path']||'');if(!validPath(raw))fail(400,'Invalid path');
      const path=raw.split('?')[0];
      let adminOwner='',adminGrant='';
      if(config.hostedAdminUsername&&path.startsWith('/accounts')){
        try{
          const cookie=(req.headers.cookie||'').split(';').map(c=>c.trim()).find(c=>c.startsWith('__Host-studio='))?.slice(14);
          const p=owner.auth.principal(cookie);
          if(p.kind==='browser'&&owner.auth.db.prepare('SELECT username FROM users WHERE id=?').get(p.owner)?.username===config.hostedAdminUsername){adminOwner=p.owner;adminGrant=p.id;}
        }catch{}
      }
      if(path==='/accounts/logout'&&req.method==='POST'&&head===undefined&&adminOwner&&!req.headers.cookie?.includes('__Host-hosted=')){
        if(req.headers.origin!==`https://${config.host}`)fail(403,'Same-origin request required');
        owner.auth.revoke(adminOwner,adminGrant);
        return json(res,200,{ok:true},{'set-cookie':['__Host-hosted=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0','__Host-studio=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0']});
      }
      if(path==='/accounts/owner'&&req.method==='POST'&&head===undefined){
        if(req.headers.origin!==`https://${config.host}`)fail(403,'Same-origin request required');
        const headers={host:config.host,authorization:`Bearer ${gatewayToken}`,cookie:req.headers.cookie||'','x-hosted-admin-owner':adminOwner};
        const response=await accountRequest('/accounts/account',headers);
        if(!response.ok)fail(response.status,'Sign in to your administrator account');
        const account=response.data;
        if(account.role!=='admin'||account.username!==config.hostedAdminUsername)fail(403,'Administrator required');
        if(owner.auth.db.prepare('SELECT username FROM users WHERE id=?').get(account.subject)?.username!==config.hostedAdminUsername)fail(403,'Owner identity mismatch');
        if(req.headers.cookie?.includes('__Host-hosted=')){
          const logout=await accountRequest('/accounts/logout',{...headers,origin:`https://${config.host}`},'POST');
          if(!logout.ok)fail(503,'Could not close the workspace session');
        }
        const token=owner.auth.issue(account.subject,undefined,'Studio browser','browser');
        return json(res,200,{ok:true},{'set-cookie':['__Host-hosted=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0',`__Host-studio=${token.access_token}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200`]});
      }
      const hosted=path==='/accounts'||path.startsWith('/accounts/')||path.startsWith('/workspaces/')||
        (req.headers.cookie||'').split(';').some(c=>c.trim().startsWith('__Host-hosted='));
      if(hosted){
        forward(req,res,{hostname:'127.0.0.1',port:config.hostedPort||18980,path:raw,head,headers:{
          host:config.host,authorization:`Bearer ${gatewayToken}`,'x-studio-access':req.headers['x-studio-access']||'',
          'x-hosted-admin-owner':adminOwner,
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
