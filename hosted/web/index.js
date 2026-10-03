const $=id=>document.getElementById(id);
const base=location.pathname.startsWith('/accounts')?'/accounts':'';
async function api(path,data){const r=await fetch(base+path,data?{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(data)}:{});const d=await r.json();if(!r.ok)throw Error(d.error);return d;}
let poll;
async function refresh(){
  clearTimeout(poll);
  try{
    const d=await api('/account');
    $('login').hidden=true;$('signup').hidden=true;$('account').hidden=false;$('admin').hidden=d.role!=='admin';
    $('deletion').hidden=d.role==='admin';$('oauth-login').hidden=true;await providerControls(true);
    const messages={ready:'Your private Studio is ready',not_created:'Private workspace has not been created',pending:'Preparing your private workspace',provisioning:'Preparing your private workspace',failed:'Workspace could not start. Please contact the administrator.',suspended:'Workspace paused. Please contact the administrator.'};
    $('who').textContent=`${d.username} · ${d.role==='admin'?'Administrator · ':''}${messages[d.status]||'Workspace unavailable'}`;
    $('enter').disabled=d.status!=='ready';$('docker').disabled=['pending','provisioning'].includes(d.status);
    if(['pending','provisioning'].includes(d.status))poll=setTimeout(refresh,5000);
  }catch(e){$('status').textContent=e.message;}
}
for(const id of ['login','register'])$(id).onsubmit=async e=>{e.preventDefault();try{await api('/'+id,Object.fromEntries(new FormData(e.target)));e.target.reset();$('status').textContent='';await refresh();}catch(e){$('status').textContent=e.message;}};
$('enter').onclick=async()=>{try{location.assign((await api('/enter',{})).url);}catch(e){$('status').textContent=e.message;}};
$('docker').onclick=async()=>{try{await api('/docker',{});await refresh();}catch(e){$('status').textContent=e.message;}};
$('owner').onclick=async()=>{try{await api('/owner',{});location.assign('/');}catch(e){$('status').textContent=e.message;}};
$('invite').onclick=async()=>{try{const d=await api('/invite',{});$('invitation').hidden=false;$('invitation-link').href=d.url;$('invitation-link').textContent=d.url;}catch(e){$('status').textContent=e.message;}};
$('copy-invitation').onclick=async()=>{try{await navigator.clipboard.writeText($('invitation-link').href);$('status').textContent='Invitation copied';}catch{$('status').textContent='Copy the invitation link above.';}};
$('logout').onclick=async()=>{await api('/logout',{});location.reload();};
$('delete').onsubmit=async e=>{e.preventDefault();try{await api('/delete',Object.fromEntries(new FormData(e.target)));e.target.reset();location.reload();}catch(e){$('status').textContent=e.message;}};
const invitation=new URL(location.href).searchParams.get('invitation');
if(invitation){$('signup').open=true;$('register').elements.invitation.value=invitation;history.replaceState(null,'',location.pathname);}
async function startProvider(provider,link=false){
  try{
    const bytes=crypto.getRandomValues(new Uint8Array(32));
    const encode=value=>btoa(String.fromCharCode(...value)).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');
    const verifier=encode(bytes),challenge=encode(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(verifier))));
    const d=await api('/oauth/start',{provider,challenge,target:'web',...(link?{link:true,password:$('oauth-password').value}:{})});
    const url=new URL(d.url);if(url.protocol!=='https:'||!['appleid.apple.com','accounts.google.com'].includes(url.host))throw Error('Invalid provider link');
    sessionStorage.setItem('studio-oauth-verifier',verifier);$('oauth-password').value='';location.assign(url.href);
  }catch(e){$('status').textContent=e.message;}
}
async function providerControls(link=false){
  const d=await api('/oauth/providers'),container=$(link?'oauth-links':'oauth-login');
  container.replaceChildren();container.hidden=!d.providers.length;$('oauth-account').hidden=!link||!d.providers.length;
  const linked=link?(await api('/oauth/links')).providers:[];
  for(const provider of d.providers){
    const button=document.createElement('button');button.type='button';button.textContent=(link?'Link ':'Continue with ')+(provider==='apple'?'Apple':'Google');button.onclick=()=>startProvider(provider,link);container.append(button);
    if(linked.includes(provider)){const remove=document.createElement('button');remove.type='button';remove.textContent=provider==='apple'?'Unlink Apple account':'Unlink Google account';remove.onclick=async()=>{try{await api('/oauth/unlink',{provider,password:$('oauth-password').value});$('oauth-password').value='';await providerControls(true);}catch(e){$('status').textContent=e.message;}};container.append(remove);}
  }
}
async function initialize(){
  const recovery=new URLSearchParams(location.search).get('oauth_error');
  const reasons={expired:'Sign-in expired. Choose Apple or Google again to start a fresh secure login.',cancelled:'Sign-in cancelled. You can try again when ready.',unlinked:'Create an invited Studio account first, then link this provider in Account.',provider:'The provider could not finish sign-in. Please start again.'};
  if(recovery){history.replaceState(null,'',location.pathname);sessionStorage.removeItem('studio-oauth-verifier');$('oauth-password').value='';}
  const ticket=new URLSearchParams(location.hash.slice(1)).get('ticket');
  if(ticket){history.replaceState(null,'',location.pathname);const verifier=sessionStorage.getItem('studio-oauth-verifier');sessionStorage.removeItem('studio-oauth-verifier');try{await api('/oauth/redeem',{ticket,verifier});}catch(e){$('status').textContent=e.message;}}
  await providerControls().catch(()=>{});await refresh();
  if(reasons[recovery])$('status').textContent=reasons[recovery];
}
initialize();
