import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createGateway } from './gateway.mjs';
import { createCell } from './cell.mjs';
import { workspaceCompose } from './compose.mjs';
import { createIngress } from './ingress.mjs';
import { attachDesktopUpgrade } from './desktop-upgrade.mjs';
import { startEdge } from '../studio/transport.mjs';

const listen=s=>new Promise(r=>{s.testSockets=new Set();s.on('connection',socket=>{s.testSockets.add(socket);socket.on('close',()=>s.testSockets.delete(socket));});s.listen(0,'127.0.0.1',r);});
function request(port,host,path,body,cookie,extra={}){
  return new Promise((resolve,reject)=>{
    const req=http.request({hostname:'127.0.0.1',port,path,method:body===undefined?'GET':'POST',headers:{host,origin:`https://${host}`,...(body===undefined?{}:{'content-type':'application/json'}),...(cookie?{cookie}:{}),...extra}},res=>{
      let text='';res.on('data',c=>text+=c);res.on('end',()=>{let data;try{data=JSON.parse(text);}catch{data=text;}resolve({status:res.statusCode,data,cookie:res.headers['set-cookie']?.[0].split(';')[0],headers:res.headers});});
    });req.on('error',reject);req.end(body===undefined?undefined:JSON.stringify(body));
  });
}
function upgrade(port,host,path,cookie,origin=`https://${host}`,hold=false){
  return new Promise((resolve,reject)=>{
    const req=http.request({hostname:'127.0.0.1',port,path,headers:{host,origin,cookie:cookie||'',connection:'Upgrade',upgrade:'websocket','sec-websocket-key':'dGhlIHNhbXBsZSBub25jZQ==','sec-websocket-version':'13'}});
    req.on('response',r=>{r.resume();resolve(hold?{status:r.statusCode}:r.statusCode);});req.on('upgrade',(r,s)=>{if(hold)resolve({status:r.statusCode,socket:s});else{s.destroy();resolve(r.statusCode);}});req.on('error',reject);req.end();
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
    up.on('upgrade',(r,s,h)=>{socket.write(`HTTP/1.1 101 Switching Protocols\r\n${Object.entries(r.headers).map(([k,v])=>`${k}: ${v}`).join('\r\n')}\r\n\r\n`);if(h.length)socket.write(h);if(head.length)s.write(head);s.pipe(socket);socket.pipe(s);socket.on('close',()=>s.destroy());socket.on('end',()=>{s.destroy();socket.destroy();});});
    up.on('response',r=>{socket.end(`HTTP/1.1 ${r.statusCode} Forbidden\r\n\r\n`);r.resume();});up.on('error',()=>socket.destroy());up.end();
  });
  await listen(router);servers.push(router);
  // Gateway config is captured by reference.
  gateway.server.close();gateway.registry.db.close();
  const config={database:join(dir,'registry.sqlite'),domain:'studio.test',capacity:2,workerHost:()=> '127.0.0.1',workerPort:router.address().port,publishing:{enabled:true,accountIds:[]}};
  const live=createGateway(config);
  gateway.server=live.server;gateway.registry=live.registry;
  await listen(gateway.server);servers.push(gateway.server);
  const port=gateway.server.address().port;
  const users=[];
  for(const name of ['alice','bravo']){
    const invitation=gateway.registry.invite();
    const registration=await request(port,'studio.test','/register',{username:name,password:'test-only-long-password',invitation});assert.equal(registration.status,200);
    assert.equal((await request(port,'studio.test','/register',{username:name+'x',password:'test-only-long-password',invitation})).status,400);
    const owner=gateway.registry.login(name,'test-only-long-password',name);config.publishing.accountIds.push(owner);const w=gateway.registry.workspace(owner),host=gateway.registry.host(w);
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
    await new Promise(resolve=>setTimeout(resolve,20));
    const active=await upgrade(port,host,'/platforms/desktop/websockify',signed.cookie,`https://${host}`,true);
    assert.equal(active.status,101);
    assert.equal(await upgrade(port,host,'/platforms/desktop/websockify',signed.cookie),403,'a second desktop cannot stream concurrently');
    active.socket.destroy();
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

test('administrator invites and switches modes without granting members owner access',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-admin-')),servers=[],host='edit.test';
  const upstream=join(dir,'upstream'),capability=join(dir,'gateway');
  writeFileSync(upstream,'test-upstream');writeFileSync(capability,'test-gateway');
  const gateway=createGateway({database:join(dir,'registry.sqlite'),domain:host,sameHost:true,ingressSecretFile:capability});
  await listen(gateway.server);servers.push(gateway.server);
  const ingress=createIngress({host,database:join(dir,'owner.sqlite'),dataRoot:dir,webRoot:dir,staticRoot:dir,
    upstreamSecretFile:upstream,hostedIngressSecretFile:capability,hostedPort:gateway.server.address().port,hostedAdminUsername:'lachlanchen'});
  await listen(ingress.server);servers.push(ingress.server);
  t.after(()=>{for(const s of servers){for(const socket of s.testSockets)socket.destroy();s.closeAllConnections();s.close();}gateway.registry.db.close();rmSync(dir,{recursive:true,force:true});});
  const owner=ingress.owner.auth.addOwner('lachlanchen','test-only-long-password');
  gateway.registry.linkOwner(ingress.owner.auth.db.prepare('SELECT * FROM users WHERE id=?').get(owner));
  const port=ingress.server.address().port;
  const pub=(path,body,cookie,extra={})=>request(port,host,'/studio/bridge',body,cookie,{authorization:'Bearer test-upstream','x-studio-path':path,...extra});
  const login=await pub('/auth/login',{username:'lachlanchen',password:'test-only-long-password'});
  assert.equal(login.status,200);
  const legacyMember=ingress.owner.auth.addOwner('legacy-member','test-only-long-password');
  const legacyGrant=ingress.owner.auth.issue(legacyMember,undefined,'legacy fixture','browser');
  assert.equal((await pub('/auth/login',{username:'legacy-member',password:'test-only-long-password'})).status,403);
  assert.equal((await pub('/auth/me',undefined,'__Host-studio='+legacyGrant.access_token)).status,403,'old non-owner session cannot see the Pi');
  assert.equal((await pub('/auth/token',{grant_type:'refresh_token',refresh_token:legacyGrant.refresh_token})).status,403);
  const account=await pub('/accounts/account',undefined,login.cookie);
  assert.equal(account.data.role,'admin');assert.equal(account.data.status,'not_created');
  const invitation=await pub('/accounts/invite',{},login.cookie);assert.equal(invitation.status,201);
  const token=new URL(invitation.data.url).searchParams.get('invitation');assert.ok(token);
  const member=await pub('/accounts/register',{username:'member',password:'test-only-long-password',invitation:token});assert.equal(member.status,200);
  assert.equal((await pub('/accounts/invite',{},member.cookie)).status,403);
  assert.equal((await pub('/accounts/docker',{},member.cookie)).status,403);
  assert.equal((await pub('/accounts/owner',{},member.cookie)).status,403);
  assert.equal((await pub('/accounts/invite',{},undefined,{'x-hosted-admin-owner':owner})).status,401,'forged admin header cannot cross ingress');
  assert.equal((await pub('/accounts/invite',{},login.cookie,{origin:'https://evil.test'})).status,403);
  assert.equal((await pub('/accounts/owner',{},login.cookie,{origin:'https://evil.test'})).status,403);
  const docker=await pub('/accounts/docker',{},login.cookie);assert.equal(docker.status,200);
  const w=gateway.registry.workspace(owner);assert.equal(w.status,'pending');
  await pub('/accounts/docker',{},docker.cookie);assert.equal(gateway.registry.workspace(owner).id,w.id,'mode retries do not create a second workspace');
  assert.equal((await pub('/accounts/account',undefined,docker.cookie)).data.role,'admin');
  const back=await pub('/accounts/owner',{},docker.cookie);assert.equal(back.status,200);
  const restored=back.headers['set-cookie'].find(v=>v.startsWith('__Host-studio=')).split(';')[0];
  assert.equal((await pub('/auth/me',undefined,restored)).data.subject,owner);
  assert.equal((await pub('/accounts/account',undefined,docker.cookie)).status,401,'closed Docker session is revoked');
  assert.equal(gateway.registry.workspace(owner).id,w.id);
  assert.equal(ingress.owner.auth.db.prepare('SELECT id FROM users WHERE username=?').get('member'),undefined,'invited member never copied to owner database');
  assert.equal((await pub('/accounts/logout',{},restored,{origin:'https://evil.test'})).status,403);
  assert.equal((await pub('/accounts/logout',{},restored)).status,200);
  assert.equal((await pub('/auth/me',undefined,restored)).status,401,'account portal sign-out revokes the owner session too');
});

test('same domain preserves owner routes and isolates invite sessions and desktop relay',async t=>{
  const dir=mkdtempSync(join(tmpdir(),'studio-samehost-')),servers=[],cells=[],ports=new Map(),host='edit.test';
  const secretPath=join(dir,'upstream'),gatewayPath=join(dir,'gateway'),facadePath=join(dir,'facade');
  writeFileSync(secretPath,'test-upstream-capability');writeFileSync(gatewayPath,'test-gateway-capability');writeFileSync(facadePath,'test-facade-capability');
  const publishing={enabled:true,accountIds:[]};
  const gateway=createGateway({database:join(dir,'registry.sqlite'),domain:host,sameHost:true,ingressSecretFile:gatewayPath,publishing,
    workerHost:()=> '127.0.0.1',workerPort:w=>ports.get(w.id)});
  await listen(gateway.server);servers.push(gateway.server);
  const ingress=createIngress({host,database:join(dir,'owner.sqlite'),upstreamSecretFile:secretPath,hostedIngressSecretFile:gatewayPath,
    hostedPort:gateway.server.address().port,dataRoot:dir,webRoot:join(dir,'missing'),staticRoot:dir});
  await listen(ingress.server);servers.push(ingress.server);
  t.after(()=>{for(const s of servers){for(const socket of s.testSockets)socket.destroy();s.closeAllConnections();s.close();}for(const c of cells)c.auth.db.close();gateway.registry.db.close();rmSync(dir,{recursive:true,force:true});});
  const guard=http.createServer();attachDesktopUpgrade(guard,{host,target:`http://127.0.0.1:${ingress.server.address().port}`,
    authorize:r=>r.headers['x-studio-access']!=='bad',headers:{authorization:'Bearer test-upstream-capability'}});
  await listen(guard);servers.push(guard);
  // HTTP requests retain the same bridge capabilities as the production guard.
  guard.on('request',(req,res)=>{req.headers.authorization='Bearer test-upstream-capability';ingress.server.emit('request',req,res);});
  const facade=startEdge({host,clientTokenFile:facadePath,gatewayPort:guard.address().port});await listen(facade);servers.push(facade);
  const port=facade.address().port;
  const pub=(path,body,cookie,extra={})=>request(port,host,path,body,cookie,{'x-studio-peer':'127.0.0.1',...extra});
  assert.equal((await pub('/api/videos')).status,401,'legacy anonymous denial survives');
  assert.equal((await request(gateway.server.address().port,host,'/accounts')).status,401,'gateway requires ingress capability');
  const users=[],contexts=[];
  for(const name of ['alice','bravo']){
    const reg=await pub('/accounts/register',{username:name,password:'test-only-long-password',invitation:gateway.registry.invite()});assert.equal(reg.status,200);
    const w=gateway.registry.workspace(gateway.registry.login(name,'test-only-long-password',name));
    publishing.accountIds.push(w.owner);
    const backend=http.createServer((req,res)=>{res.setHeader('content-type','application/json');res.end(JSON.stringify({videos:[{id:1,title:name}]}));});await listen(backend);servers.push(backend);
    const desktop=http.createServer((req,res)=>res.end(name));desktop.on('upgrade',(req,s)=>s.write('HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\n\r\n'));await listen(desktop);servers.push(desktop);
    const key=join(dir,name+'.key');writeFileSync(key,w.transport);
    const cell=createCell({host,database:join(dir,name+'.sqlite'),upstreamSecretFile:key,dataRoot:dir,backendPort:backend.address().port,desktopPort:desktop.address().port,webRoot:dir,staticRoot:dir},
      {...w,username:name,password:gateway.registry.db.prepare('SELECT password FROM users WHERE id=?').get(w.owner).password});
    await listen(cell.server);servers.push(cell.server);cells.push(cell);ports.set(w.id,cell.server.address().port);
    gateway.registry.db.prepare("UPDATE workspaces SET status='ready' WHERE id=?").run(w.id);
    const entry=await pub('/accounts/enter',{},reg.cookie),url=new URL(entry.data.url);
    const signed=await pub(url.pathname+url.search,undefined,reg.cookie);assert.equal(signed.status,303);
    const cookie=reg.cookie+'; '+signed.cookie;
    assert.equal((await pub('/api/videos',undefined,cookie)).data.videos[0].title,name);
    const context=await pub('/studio-context.js',undefined,cookie);
    assert.equal(context.status,200);assert.equal(context.headers['cache-control'],'no-store');
    contexts.push(context.data);assert.match(context.data,/publicationOnly/);
    assert.equal((await pub('/platforms/desktop/vnc.html',undefined,cookie)).data,name);
    const token=cell.auth.issue(w.owner,['media.read'],'test API');
    assert.equal((await pub(`/workspaces/${w.id}/v1/studio/account`,undefined,undefined,{authorization:`Bearer ${token.access_token}`})).data.subject,w.owner);
    const linked=await pub(`/workspaces/${w.id}/auth/login`,{username:name,password:'test-only-long-password',mode:'token',scopes:['media.read']});
    assert.equal(linked.status,200);
    assert.equal((await pub(`/workspaces/${w.id}/v1/studio/account`,undefined,undefined,{authorization:`Bearer ${linked.data.access_token}`})).data.subject,w.owner);
    assert.equal((await pub(`/workspaces/${w.id}/api/videos`)).status,401);
    users.push({cookie,w});
  }
  assert.notEqual(contexts[0],contexts[1],'each account has a separate browser cache namespace');
  assert.equal((await pub(`/workspaces/${users[1].w.id}/api/videos`,undefined,users[0].cookie,{authorization:'Bearer bad'})).status,403);
  assert.equal((await pub('/api/videos',undefined,'__Host-hosted=expired')).status,401,'expired hosted cookie never falls through to owner');
  // Full facade → guarded upgrade → ingress → gateway → private desktop.
  const ws=http.request({host:'127.0.0.1',port,path:'/platforms/desktop/websockify',headers:{host,origin:`https://${host}`,cookie:users[0].cookie,
    'x-studio-peer':'127.0.0.1',connection:'Upgrade',upgrade:'websocket','sec-websocket-key':'dGhlIHNhbXBsZSBub25jZQ==','sec-websocket-version':'13'}});
  const code=await new Promise((resolve,reject)=>{ws.on('upgrade',(r,s)=>{s.destroy();resolve(r.statusCode);});ws.on('response',r=>{r.resume();resolve(r.statusCode);});ws.on('error',reject);ws.end();});assert.equal(code,101);
  assert.equal((await pub('/auth/logout',{},users[0].cookie)).status,200);
  assert.equal((await pub('/api/videos',undefined,users[0].cookie)).status,401);
});
