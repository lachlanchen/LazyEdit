import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createGateway } from './gateway.mjs';
import { createCell } from './cell.mjs';
import { workspaceCompose } from './compose.mjs';

const listen=s=>new Promise(r=>{s.testSockets=new Set();s.on('connection',socket=>{s.testSockets.add(socket);socket.on('close',()=>s.testSockets.delete(socket));});s.listen(0,'127.0.0.1',r);});
function request(port,host,path,body,cookie,extra={}){
  return new Promise((resolve,reject)=>{
    const req=http.request({hostname:'127.0.0.1',port,path,method:body===undefined?'GET':'POST',headers:{host,origin:`https://${host}`,...(body===undefined?{}:{'content-type':'application/json'}),...(cookie?{cookie}:{}),...extra}},res=>{
      let text='';res.on('data',c=>text+=c);res.on('end',()=>{let data;try{data=JSON.parse(text);}catch{data=text;}resolve({status:res.statusCode,data,cookie:res.headers['set-cookie']?.[0].split(';')[0],headers:res.headers});});
    });req.on('error',reject);req.end(body===undefined?undefined:JSON.stringify(body));
  });
}
function upgrade(port,host,path,cookie,origin=`https://${host}`){
  return new Promise((resolve,reject)=>{
    const req=http.request({hostname:'127.0.0.1',port,path,headers:{host,origin,cookie:cookie||'',connection:'Upgrade',upgrade:'websocket','sec-websocket-key':'dGhlIHNhbXBsZSBub25jZQ==','sec-websocket-version':'13'}});
    req.on('response',r=>{r.resume();resolve(r.statusCode);});req.on('upgrade',(r,s)=>{s.destroy();resolve(r.statusCode);});req.on('error',reject);req.end();
  });
}

test('invite → isolated workspaces → authenticated platform desktop',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'lazyedit-hosted-test-')),servers=[],cells=[];
  t.after(()=>{for(const s of servers){for(const socket of s.testSockets)socket.destroy();s.closeAllConnections();s.close();}for(const c of cells)c.auth.db.close();gateway.registry.db.close();rmSync(dir,{recursive:true,force:true});});
  const ports=new Map();
  const gateway=createGateway({database:join(dir,'registry.sqlite'),domain:'studio.test',capacity:2,workerHost:()=> '127.0.0.1'});
  // Assign test listener per workspace without changing production routing logic.
  const router=http.createServer((req,res)=>{
    const port=ports.get(req.headers.host);const up=http.request({host:'127.0.0.1',port,path:req.url,method:req.method,headers:req.headers},r=>{res.writeHead(r.statusCode,r.headers);r.pipe(res);});req.pipe(up);
  });
  router.on('upgrade',(req,socket,head)=>{
    const port=ports.get(req.headers.host);const up=http.request({host:'127.0.0.1',port,path:req.url,headers:req.headers});
    up.on('upgrade',(r,s,h)=>{socket.write(`HTTP/1.1 101 Switching Protocols\r\n${Object.entries(r.headers).map(([k,v])=>`${k}: ${v}`).join('\r\n')}\r\n\r\n`);if(h.length)socket.write(h);if(head.length)s.write(head);s.pipe(socket);socket.pipe(s);socket.on('close',()=>s.destroy());});
    up.on('response',r=>{socket.end(`HTTP/1.1 ${r.statusCode} Forbidden\r\n\r\n`);r.resume();});up.on('error',()=>socket.destroy());up.end();
  });
  await listen(router);servers.push(router);
  // Gateway config is captured by reference.
  gateway.server.close();gateway.registry.db.close();
  const config={database:join(dir,'registry.sqlite'),domain:'studio.test',capacity:2,workerHost:()=> '127.0.0.1',workerPort:router.address().port};
  const live=createGateway(config);
  gateway.server=live.server;gateway.registry=live.registry;
  await listen(gateway.server);servers.push(gateway.server);
  const port=gateway.server.address().port;
  const users=[];
  for(const name of ['alice','bravo']){
    const invitation=gateway.registry.invite();
    const registration=await request(port,'studio.test','/register',{username:name,password:'test-only-long-password',invitation});assert.equal(registration.status,200);
    assert.equal((await request(port,'studio.test','/register',{username:name+'x',password:'test-only-long-password',invitation})).status,400);
    const owner=gateway.registry.login(name,'test-only-long-password',name),w=gateway.registry.workspace(owner),host=gateway.registry.host(w);
    assert.equal((await request(port,'studio.test','/enter',{},registration.cookie)).status,409);
    const backend=http.createServer((req,res)=>{res.setHeader('content-type','application/json');res.end(JSON.stringify(req.url.startsWith('/api/videos')?{videos:[{id:1,title:name}]}:{jobs:[{id:1,owner:name}],opened:true}));});await listen(backend);servers.push(backend);
    const desktop=http.createServer((req,res)=>res.end(name+' desktop'));desktop.on('upgrade',(req,s)=>s.write('HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\n\r\n'));await listen(desktop);servers.push(desktop);
    writeFileSync(join(dir,name+'.secret'),w.transport);
    const cell=createCell({host,database:join(dir,name+'.sqlite'),upstreamSecretFile:join(dir,name+'.secret'),dataRoot:dir,backendPort:backend.address().port,desktopPort:desktop.address().port,publisherPort:backend.address().port,webRoot:dir,staticRoot:dir}, {...w,username:name,password:gateway.registry.db.prepare('SELECT password FROM users WHERE id=?').get(owner).password});
    cells.push(cell);await listen(cell.server);servers.push(cell.server);ports.set(host,cell.server.address().port);
    gateway.registry.db.prepare("UPDATE workspaces SET status='ready' WHERE id=?").run(w.id);
    const entry=await request(port,'studio.test','/enter',{},registration.cookie);assert.equal(entry.status,200);
    const url=new URL(entry.data.url),signed=await request(port,host,url.pathname+url.search);
    assert.equal(signed.status,303);assert.ok(signed.cookie.startsWith('__Host-studio='));
    assert.equal((await request(port,host,url.pathname+url.search)).status,401,'SSO ticket cannot be replayed');
    const videos=await request(port,host,'/api/videos',undefined,signed.cookie);assert.equal(videos.data.videos[0].title,name);
    assert.equal((await request(port,host,'/api/autopublish/queue',undefined,signed.cookie)).data.jobs[0].owner,name);
    assert.equal((await request(port,host,'/platforms/open',{platform:'youtube'},signed.cookie)).status,200);
    assert.equal((await request(port,host,'/platforms/open',{platform:'file:///etc/passwd'},signed.cookie)).status,400);
    assert.equal((await request(port,host,'/platforms/desktop/vnc.html',undefined,signed.cookie)).data,name+' desktop');
    assert.equal(await upgrade(port,host,'/platforms/desktop/websockify',signed.cookie),101);
    assert.equal(await upgrade(port,host,'/platforms/desktop/websockify',signed.cookie,'https://evil.test'),403);
    assert.equal(await upgrade(port,host,'/platforms/desktop/websockify'),403);
    users.push({host,cookie:signed.cookie,cell,w});
  }
  assert.equal((await request(port,users[1].host,'/api/videos',undefined,users[0].cookie)).status,401,'account A cannot read B');
  assert.equal((await request(port,users[1].host,'/platforms/open',{platform:'youtube'},users[0].cookie)).status,401);
  assert.equal((await request(port,users[0].host,'/hosted-entry',undefined,undefined,{'x-hosted-owner':users[0].w.owner})).status,401,'forged SSO header stripped');
  assert.equal((await request(port,'studio.test','/register',{username:'charlie',password:'test-only-long-password',invitation:gateway.registry.invite()})).status,503);
  assert.equal((await request(port,'unknown.studio.test','/')).status,404);
  assert.equal((await request(port,users[0].host,'/platforms/desktop/%2e%2e/secret',undefined,users[0].cookie)).status,400);
  assert.equal((await request(users[0].cell.server.address().port,users[0].host,'/studio/bridge',undefined,undefined,{'x-studio-path':'/api/videos'})).status,401,'worker cannot bypass transport');
  gateway.registry.db.prepare("UPDATE workspaces SET status='suspended' WHERE id=?").run(users[0].w.id);
  assert.equal((await request(port,users[0].host,'/api/videos',undefined,users[0].cookie)).status,404,'suspension blocks existing session');
});

test('workspace template has private volumes, loopback services and bounded resources',()=>{
  const a=workspaceCompose({id:'a'.repeat(24)},{},'/private/a'),b=workspaceCompose({id:'b'.repeat(24)},{},'/private/b');
  assert.notEqual(a.name,b.name);assert.equal(a.services.worker.ports,undefined);assert.equal(a.services.database.ports,undefined);
  assert.equal(a.services.worker.privileged,undefined);assert.equal(a.services.worker.user,'1000:1000');
  assert.equal(a.services.worker.environment.LAZYEDIT_BIND,'127.0.0.1');assert.equal(a.networks.private.internal,true);
  assert.ok(!JSON.stringify(a).includes('docker.sock'));assert.throws(()=>workspaceCompose({id:'../../evil'},{},'/x'));
});
