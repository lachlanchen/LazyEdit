// An opt-in Studio-only upgrade adapter for pinned LazyEdge 0.4 HTTP servers.
// HTTP policy remains in LazyEdge; WebSockets share the same declared bridge,
// separate transport capabilities, same-origin check, and a small live limit.
import { forward } from './proxy.mjs';
import { validPath } from '../studio/transport.mjs';

export function attachDesktopUpgrade(server,{host,target,authorize,headers={},limit=2,timeout=900000}){
  let active=0;
  const sockets=new Set();
  server.on('upgrade',async(req,socket,head)=>{
    const reject=status=>socket.end(`HTTP/1.1 ${status} Forbidden\r\nConnection: close\r\n\r\n`);
    try{
      const path=String(req.headers['x-studio-path']||'');
      if(req.headers.host!==host||req.method!=='GET'||req.url!=='/studio/bridge'||!validPath(path)||
        !/^\/platforms\/desktop\/websockify(?:\?.*)?$/.test(path)||
        req.headers.origin!==`https://${host}`||String(req.headers.upgrade).toLowerCase()!=='websocket'||
        req.headers['sec-websocket-version']!=='13'||
        !/^[A-Za-z0-9+/]{22}==$/.test(req.headers['sec-websocket-key']||''))return reject(403);
      if(!await authorize(req))return reject(401);
      if(active>=limit)return reject(429);
      active++;sockets.add(socket);
      socket.once('close',()=>{active--;sockets.delete(socket);});
      socket.setTimeout(timeout,()=>socket.destroy());
      const u=new URL(target);
      forward(req,socket,{hostname:u.hostname,port:u.port,path:'/studio/bridge',head,headers:{
        ...headers,host,'x-studio-path':path,'x-studio-access':req.headers['x-studio-access']||'',
        'x-studio-client':req.headers['x-studio-client']||''}});
    }catch{return reject(503);}
  });
  const close=server.close.bind(server);
  server.close=(...args)=>{for(const socket of sockets)socket.destroy();return close(...args);};
}
