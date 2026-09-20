// Same-origin owner session only; never persist API credentials in browser storage.
const nativeFetch = window.fetch.bind(window);
const readWaiters = [];
let activeReads = 0;
async function acquireRead() {
  if (activeReads < 4) activeReads += 1;
  else await new Promise(resolve => readWaiters.push(resolve));
}
function releaseRead() {
  const next = readWaiters.shift();
  if (next) next();
  else activeReads -= 1;
}
function errorMessage(value, fallback) {
  if (typeof value === 'string' && value.trim()) return value;
  if (value && typeof value === 'object') {
    if (typeof value.message === 'string' && value.message.trim()) return value.message;
    if (typeof value.code === 'string') {
      if (value.code === 'too_many_requests') return 'Studio is busy. Please try again shortly.';
      if (value.code === 'upstream_unavailable') return 'Studio is temporarily unavailable. Please try again.';
      return value.code.replace(/_/g, ' ');
    }
  }
  return fallback;
}
window.fetch = async (...args) => {
  const input = args[0];
  const target = new URL(input?.url || String(input), location.href);
  const sameOrigin = target.origin === location.origin;
  const method = String(args[1]?.method || input?.method || 'GET').toUpperCase();
  const read = sameOrigin && method === 'GET' && /^\/(api|v1)\//.test(target.pathname);
  if (read) await acquireRead();
  try {
    let response;
    for (let attempt = 0; ; attempt += 1) {
      response = await nativeFetch(...args);
      if (!read || attempt >= 2 || ![429, 502, 503, 504].includes(response.status)) break;
      // Drain the rejected GET before retrying. Never replay a mutation/upload.
      await response.arrayBuffer();
      const seconds = Number(response.headers.get('retry-after')) || attempt + 1;
      await new Promise(resolve => setTimeout(resolve, Math.min(5, Math.max(1, seconds)) * 1000));
    }
    if (sameOrigin && response.status === 401) location.assign('/login');
    if (read && response.headers.get('content-type')?.includes('application/json')) {
      // fetch resolves at headers; hold the permit until the JSON body arrives.
      await response.clone().arrayBuffer();
    }
    if (sameOrigin && !response.ok) {
      const parse = response.json.bind(response);
      response.json = async () => {
        const payload = await parse();
        if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
          return { error: errorMessage(payload, `Request failed (HTTP ${response.status}).`) };
        }
        // LazyEdge returns {error:{code:...}}. Legacy views expect a string.
        return { ...payload, error: errorMessage(payload.error, errorMessage(payload.message, `Request failed (HTTP ${response.status}).`)),
          ...(payload.details && typeof payload.details !== 'string'
            ? { details: errorMessage(payload.details, '') } : {}) };
      };
    }
    return response;
  } finally {
    if (read) releaseRead();
  }
};
window.addEventListener('DOMContentLoaded', () => {
  const loading = document.getElementById('studio-loading');
  const root = document.getElementById('root');
  if (loading && root) {
    const reload = document.getElementById('studio-reload');
    if (reload) reload.addEventListener('click', () => location.reload());
    const timer = setTimeout(() => {
      const actions = document.getElementById('studio-loading-actions');
      if (actions) actions.hidden = false;
    }, 15000);
    const ready = () => {
      if (!root.childElementCount) return;
      loading.remove();
      clearTimeout(timer);
      observer.disconnect();
    };
    const observer = new MutationObserver(ready);
    observer.observe(root, { childList: true });
    ready();
  }
  const link = document.createElement('a');link.href='/connect';link.textContent='Account · Connect';
  link.style.cssText='position:fixed;right:12px;bottom:72px;z-index:9999;padding:8px 12px;background:#102d29;color:white;border-radius:20px;font:13px system-ui;text-decoration:none';document.body.append(link);
});
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(()=>{});
