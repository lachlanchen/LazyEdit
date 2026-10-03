// Bundle noVNC once: unbundled imports exceed the guarded ingress burst limit.
import RFB from '/usr/share/novnc/core/rfb.js';
const $ = id => document.getElementById(id);
let rfb, connectionTimer, idleTimer, opened = false;
const status = message => { $('status').textContent = message; };
function pause(message = 'Desktop paused. Your platform login is saved.') {
  clearTimeout(connectionTimer); clearTimeout(idleTimer);
  const old = rfb; rfb = undefined; if (old) old.disconnect();
  $('disconnect').disabled = true; $('freeze').disabled = true; $('connect').disabled = !opened;
  if (message) status(message);
}
function activity() {
  clearTimeout(idleTimer);
  if (rfb) idleTimer = setTimeout(() => pause('Desktop paused after five minutes without input. Tap Reconnect.'), 300000);
}
function connect() {
  pause('Connecting to your private desktop…'); $('desktop').replaceChildren();
  const surface=document.createElement('div');surface.id='surface';surface.style.cssText='width:100%;height:100%;min-height:320px';$('desktop').append(surface);
  const connection = new RFB(surface, `wss://${location.host}/platforms/desktop/websockify`, {shared:false});
  rfb = connection; connection.scaleViewport = true; connection.resizeSession = false;
  connection.compressionLevel = 8; connection.qualityLevel = 6;
  $('zoom').value='1';
  $('connect').disabled = true;
  connectionTimer = setTimeout(() => { if (rfb === connection) pause('Desktop did not respond within 20 seconds. Tap Reconnect to try again.'); }, 20000);
  connection.addEventListener('connect', () => {
    if (rfb !== connection) return;
    clearTimeout(connectionTimer); $('disconnect').disabled = false; $('freeze').disabled = false;
    status('Connected. Sign in using the private browser below.'); activity();
  });
  connection.addEventListener('disconnect', event => {
    if (rfb !== connection) return;
    pause(event.detail.clean ? 'Desktop disconnected. Tap Reconnect.' : 'Desktop connection ended. Another viewer may be open; close it and tap Reconnect.');
  });
  connection.addEventListener('securityfailure', () => pause('Desktop authentication failed. Return to Studio and sign in again.'));
}
const names = {shipinhao:'Shipinhao',instagram:'Instagram',youtube:'YouTube',douyin:'Douyin',xiaohongshu:'Xiaohongshu',bilibili:'Bilibili'};
for (const [platform,name] of Object.entries(names)) {
  const button = document.createElement('button'); button.textContent = name;
  button.onclick = async () => {
    const buttons = [...$('platforms').querySelectorAll('button')]; buttons.forEach(b => b.disabled = true);
    status('Opening '+name+'…');
    try {
      const response = await fetch('/platforms/open', {method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({platform}),signal:AbortSignal.timeout(45000)});
      const data = await response.json(); if (!response.ok) throw Error(data.error || 'Browser could not open.');
      opened = true; if (!rfb) connect(); else {status('Sign in to '+name+' below.');activity();}
    } catch (error) { status(error.name === 'TimeoutError' ? 'Browser startup timed out. Tap the platform to try again.' : error.message); }
    finally { buttons.forEach(b => b.disabled = false); }
  };
  $('platforms').append(button);
}
$('connect').onclick = connect; $('disconnect').onclick = () => pause();
$('zoom').onchange=()=>{
  const surface=$('surface');if(!surface)return;
  const factor=Number($('zoom').value);surface.style.width=100*factor+'%';surface.style.height=100*factor+'%';
  $('desktop').style.overflow=factor===1?'hidden':'auto';
};
$('desktop').addEventListener('pointerdown', activity); $('desktop').addEventListener('keydown', activity);
$('freeze').onclick = () => {
  const canvas = $('desktop').querySelector('canvas'); if (!canvas || !rfb) return;
  const image = new Image(); image.id = 'snapshot'; image.alt = 'Paused login desktop. Reconnect to refresh an expired QR.'; image.src = canvas.toDataURL('image/png');
  const original = new Image(); original.src = image.src; let focused = false;
  image.onclick = event => {
    if (focused) { image.src = original.src; focused = false; return; }
    if (!original.complete || !original.naturalWidth) return;
    const rect = image.getBoundingClientRect(), size = Math.min(original.naturalWidth, original.naturalHeight) * .4;
    const x = Math.max(0, Math.min(original.naturalWidth-size, (event.clientX-rect.left)/rect.width*original.naturalWidth-size/2));
    const y = Math.max(0, Math.min(original.naturalHeight-size, (event.clientY-rect.top)/rect.height*original.naturalHeight-size/2));
    const crop = document.createElement('canvas'); crop.width = crop.height = Math.round(size);
    crop.getContext('2d').drawImage(original, x, y, size, size, 0, 0, size, size);
    image.src = crop.toDataURL('image/png'); focused = true;
  };
  pause('QR image kept visible. Tap the image to enlarge a QR area; tap again to restore. No live traffic. Reconnect to refresh.'); $('desktop').append(image);
};
// Send Unicode via keysyms, without a server-side clipboard endpoint.
$('send').onclick = () => {
  if (!rfb) return status('Connect the desktop first.');
  const value = $('input').value; $('input').value = '';
  for (const char of value) { const code = char.codePointAt(0); rfb.sendKey(code > 255 ? 0x01000000 | code : code); }
  activity();
};
$('paste').onclick = () => { if (rfb) {rfb.clipboardPasteFrom($('input').value);$('input').value='';activity();status('Clipboard sent. Use Paste in the remote browser.');} };
$('enter').onclick = () => { if (rfb) {rfb.sendKey(0xff0d);activity();} };
document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
window.addEventListener('pagehide', () => pause());
