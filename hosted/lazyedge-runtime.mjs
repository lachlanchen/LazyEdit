// Uses the existing pinned LazyEdge APIs; no shared gateway/library upgrade.
import { pathToFileURL } from 'node:url';
const [role,packageRoot,manifestFile,bindingsFile]=process.argv.slice(2);
const load=name=>import(pathToFileURL(`${packageRoot}/src/${name}.js`).href);
const {loadManifest}=await load('config');
const {loadBindings,readPrivateText}=await load('runtime-config');
const {constantTimeEqual,getBearerFromRequest,RELAY_HEADER}=await load('security');
const {attachDesktopUpgrade}=await import('./desktop-upgrade.mjs');
const manifest=await loadManifest(manifestFile);
if(!['edge','worker'].includes(role)||manifest.spec.services.length!==1)throw Error('Studio single-service runtime required');
const service=manifest.spec.services[0];
if(service.id!=='studio'||service.domains.length!==1||service.public.routes.length!==1||service.public.routes[0].path!=='/studio/bridge')throw Error('Studio bridge manifest required');
const bindings=await loadBindings(bindingsFile,{role,declaredServiceIds:['studio']});
const binding=bindings.get('studio');
const relay=await readPrivateText(binding.relaySecretFile);
let handle,authorize,headers,target;
if(role==='edge'){
  const {TokenStore}=await load('token-store');
  const store=await TokenStore.open({filePath:binding.clientTokenStore});
  const {startEdgeServer}=await load('edge-server');
  handle=await startEdgeServer({manifest,tokenStore:store,relayToken:relay});
  authorize=req=>store.verify(getBearerFromRequest(req,'authorization'),{tokenSet:service.public.tokenSet,
    context:{serviceId:'studio',host:service.domains[0],method:'GET',path:'/studio/bridge'}});
  headers={[RELAY_HEADER]:`Bearer ${relay}`};target=service.edge.upstream;
}else{
  const upstream=await readPrivateText(binding.upstreamAuthorizationFile);
  const {startWorkerServer}=await load('worker-server');
  handle=await startWorkerServer({manifest,relayToken:relay,upstreamToken:upstream});
  authorize=req=>{const supplied=getBearerFromRequest(req,RELAY_HEADER);return supplied!==null&&constantTimeEqual(supplied,relay);};
  headers={authorization:`Bearer ${upstream}`};target=service.worker.target;
}
attachDesktopUpgrade(handle.server,{host:service.domains[0],target,authorize,headers});
console.log(`Studio LazyEdge ${role} ready (private desktop upgrades enabled)`);
for(const signal of ['SIGTERM','SIGINT'])process.once(signal,()=>handle.close().then(()=>process.exit(0)));
