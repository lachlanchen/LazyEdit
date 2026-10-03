const $=id=>document.getElementById(id);
const base=location.pathname.startsWith('/accounts')?'/accounts':'';
async function api(path,data){const r=await fetch(base+path,data?{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(data)}:{});const d=await r.json();if(!r.ok)throw Error(d.error);return d;}
let poll;
async function refresh(){
  clearTimeout(poll);
  try{
    const d=await api('/account');
    $('login').hidden=true;$('signup').hidden=true;$('account').hidden=false;$('admin').hidden=d.role!=='admin';
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
const invitation=new URL(location.href).searchParams.get('invitation');
if(invitation){$('signup').open=true;$('register').elements.invitation.value=invitation;history.replaceState(null,'',location.pathname);}
refresh();
