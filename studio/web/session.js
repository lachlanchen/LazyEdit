// Same-origin owner session only; never persist API credentials in browser storage.
const nativeFetch = window.fetch.bind(window);
window.fetch = async (...args) => {
  const response = await nativeFetch(...args);
  const target = new URL(typeof args[0] === 'string' ? args[0] : args[0].url, location.href);
  if (target.origin === location.origin && response.status === 401) location.assign('/login');
  return response;
};
window.addEventListener('DOMContentLoaded', () => {
  const link = document.createElement('a');link.href='/connect';link.textContent='Account · Connect';
  link.style.cssText='position:fixed;right:12px;bottom:72px;z-index:9999;padding:8px 12px;background:#102d29;color:white;border-radius:20px;font:13px system-ui;text-decoration:none';document.body.append(link);
});
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(()=>{});
