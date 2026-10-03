// No network listener. Only this trusted controller can use the Docker socket.
import { spawn } from 'node:child_process';
const state=process.argv[2];
let stopped=false, child;
process.on('SIGTERM',()=>{stopped=true;child?.kill('SIGTERM');});
while(!stopped){
  await new Promise(resolve=>{
    child=spawn(process.execPath,[new URL('./admin.mjs',import.meta.url).pathname,'provision',state],{stdio:'inherit'});
    child.on('exit',resolve);child.on('error',resolve);
  });
  if(!stopped)await new Promise(resolve=>{const wake=()=>{clearTimeout(timer);process.removeListener('SIGTERM',wake);resolve();};const timer=setTimeout(wake,30000);process.once('SIGTERM',wake);});
}
