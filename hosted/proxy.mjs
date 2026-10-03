import http from 'node:http';
import { pipeline } from 'node:stream';
import { json } from '../studio/transport.mjs';

// Whitelist headers: client-supplied internal identities must never reach a worker.
const allowed = ['content-type','content-length','range','if-range','cookie','origin','accept',
  'upload-offset','x-content-sha256','idempotency-key','sec-websocket-key','sec-websocket-version','sec-websocket-protocol'];
export function forward(req, output, { hostname, port, path, headers = {}, head }) {
  const h = Object.fromEntries(allowed.filter(k=>req.headers[k]).map(k=>[k, req.headers[k]]));
  const websocket = head !== undefined;
  if (websocket) Object.assign(h, { connection:'Upgrade', upgrade:'websocket' });
  Object.assign(h, headers);
  const up = http.request({ hostname, port, path, method:req.method, headers:h });
  up.setTimeout(900000, ()=>up.destroy());
  up.on('response', r=>{
    if (websocket) { output.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n'); r.resume(); return; }
    const out = Object.fromEntries(Object.entries(r.headers).filter(([k])=>!['connection','transfer-encoding','authorization'].includes(k)));
    output.writeHead(r.statusCode, {...out,'cache-control':'no-store','referrer-policy':'no-referrer','x-content-type-options':'nosniff'});
    pipeline(r, output, ()=>{});
  });
  up.on('upgrade',(r,socket,upHead)=>{
    if (!websocket) { socket.destroy(); return; }
    output.write(`HTTP/1.1 101 Switching Protocols\r\n${Object.entries(r.headers).map(([k,v])=>`${k}: ${v}`).join('\r\n')}\r\n\r\n`);
    if (upHead.length) output.write(upHead);
    if (head.length) socket.write(head);
    socket.on('error', ()=>output.destroy()); output.on('error', ()=>socket.destroy());
    output.on('close', ()=>socket.destroy()); socket.on('close', ()=>output.destroy());
    socket.pipe(output); output.pipe(socket);
  });
  up.on('error',()=>{
    if (websocket) output.destroy();
    else if (!output.headersSent) json(output,503,{error:'Workspace is starting; try again shortly'});
    else output.destroy();
  });
  output.on('close', ()=>up.destroy());
  if (websocket) up.end(); else pipeline(req, up, ()=>{});
}
