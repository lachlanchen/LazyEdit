for(const [port,path] of [[18080,'/healthz'],[18787,'/api/videos'],[8081,'/publish/queue']]){
  const r=await fetch(`http://127.0.0.1:${port}${path}`,{signal:AbortSignal.timeout(1200)});
  if(!r.ok)process.exit(1);
}
