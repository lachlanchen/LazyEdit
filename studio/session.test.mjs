import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import vm from 'node:vm';

const source = readFileSync(new URL('./web/session.js', import.meta.url), 'utf8');
const require = createRequire(new URL('../app/package.json', import.meta.url));
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
function browser(fetch) {
  const redirects = [];
  const window = { fetch, addEventListener() {} };
  vm.runInNewContext(source, {
    window, URL, navigator: {}, location: {
      href: 'https://studio.test/editor', origin: 'https://studio.test',
      assign: url => redirects.push(url),
    }, setTimeout: fn => setTimeout(fn, 0),
  });
  return { fetch: window.fetch, redirects };
}
const json = (value, status = 200) => Response.json(value, { status });

test('LazyEdge structured rejection displays text instead of React error 31', async () => {
  const error = { code: 'too_many_requests' };
  assert.throws(() => renderToStaticMarkup(React.createElement('span', null, error)), /Objects are not valid/);
  let requests = 0;
  const b = browser(async () => { requests++; return json({ error }, 429); });
  const response = await b.fetch('/api/videos/573/process-status');
  const payload = await response.json();
  assert.equal(response.status, 429);
  assert.equal(requests, 3, 'bounded read retries');
  assert.match(renderToStaticMarkup(React.createElement('span', null, payload.error)), /Studio is busy/);
});

test('temporary read failures recover without replaying mutations', async () => {
  let requests = 0;
  const b = browser(async () => ++requests === 1 ? json({ error: { code: 'too_many_requests' } }, 429) : json({ steps: {} }));
  assert.deepEqual(await (await b.fetch('/api/videos/1/process-status')).json(), { steps: {} });
  assert.equal(requests, 2);
  for (const method of ['POST', 'PUT', 'DELETE']) {
    let mutations = 0;
    const m = browser(async () => { mutations++; return json({ error: { message: 'Try later' } }, 503); });
    const response = await m.fetch('/api/videos/1/publish', { method });
    assert.equal((await response.json()).error, 'Try later');
    assert.equal(mutations, 1);
  }
});

test('API read slots cover slow bodies, not just response headers', async () => {
  let active = 0, peak = 0;
  const b = browser(async () => {
    active++; peak = Math.max(peak, active);
    return new Response(new ReadableStream({ start(controller) {
      setTimeout(() => { controller.enqueue(new TextEncoder().encode('{"ok":true}')); controller.close(); active--; }, 10);
    } }), { headers: { 'content-type': 'application/json' } });
  });
  const values = await Promise.all(Array.from({ length: 20 }, async () => (await b.fetch('/api/videos')).json()));
  assert.equal(peak, 4);
  assert.equal(active, 0);
  assert.equal(values.length, 20);
});

test('failed fetch releases read slot; unknown structured errors still render safely', async () => {
  let requests = 0;
  const b = browser(async () => {
    if (++requests <= 4) throw new Error('Network unavailable');
    return json({ error: { unexpected: true }, message: { code: 'bad_gateway' }, details: [{ message: 'invalid' }] }, 400);
  });
  await Promise.allSettled(Array.from({ length: 4 }, () => b.fetch('/api/videos')));
  const payload = await (await b.fetch('/api/videos')).json();
  assert.equal(payload.error, 'bad gateway');
  assert.equal(typeof payload.details, 'string');
});

test('401 redirects once; external replies and successful JSON are unchanged', async () => {
  const b = browser(async () => json({ error: { code: 'unauthorized' } }, 401));
  await b.fetch(new URL('https://studio.test/api/videos'));
  assert.deepEqual(b.redirects, ['/login']);
  const external = await b.fetch('https://other.test/api/videos');
  assert.deepEqual(await external.json(), { error: { code: 'unauthorized' } });
  assert.deepEqual(b.redirects, ['/login']);
  const success = { status: 'queued', job: { id: 5 }, error: null };
  assert.deepEqual(await (await browser(async () => json(success)).fetch('/api/videos')).json(), success);
});

test('loading screen stays until React mounts, then clears its recovery timer', () => {
  let callback, mutation, removed = false, cleared = false, disconnected = false;
  const root = { childElementCount: 0 };
  const actions = { hidden: true };
  const nodes = { root, 'studio-loading': { remove() { removed = true; } }, 'studio-loading-actions': actions };
  let timer;
  const context = {
    window: { fetch: async () => json({}), addEventListener: (_, fn) => { callback = fn; } },
    URL, navigator: {}, location: { href: 'https://studio.test/editor', origin: 'https://studio.test' },
    document: { getElementById: id => nodes[id], createElement: () => ({ style: {} }), body: { append() {} } },
    setTimeout: fn => { timer = fn; return 1; }, clearTimeout: () => { cleared = true; },
    MutationObserver: class { constructor(fn) { mutation = fn; } observe() {} disconnect() { disconnected = true; } },
  };
  vm.runInNewContext(source, context); callback();
  assert.equal(removed, false);
  timer(); assert.equal(actions.hidden, false);
  root.childElementCount = 1; mutation();
  assert.equal(removed, true); assert.equal(cleared, true); assert.equal(disconnected, true);
});
