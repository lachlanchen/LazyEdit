import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, symlinkSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import http from 'node:http';
import {createWorker} from './server.mjs';

async function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), 'studio-media-test-'));
  const root = join(dir, 'data');
  mkdirSync(join(root, 'owned'), {recursive: true});
  mkdirSync(join(root, 'other'));
  const bytes = Buffer.from('0123456789-preview-fixture');
  writeFileSync(join(root, 'owned', 'clip.mp4'), bytes);
  writeFileSync(join(root, 'other', 'clip.mp4'), 'not owned');
  writeFileSync(join(dir, 'outside.mp4'), 'outside data root');
  symlinkSync(join(dir, 'outside.mp4'), join(root, 'owned', 'escape.mp4'));
  writeFileSync(join(dir, 'transport'), 'test-transport');
  const calls = [];
  const replies = new Map();
  const backend = http.createServer((req, res) => {
    const id = Number(req.url.split('/').at(-1));
    calls.push(id);
    const [status, data] = replies.get(id) || [404, {error: 'Video not found'}];
    res.writeHead(status, {'content-type': 'application/json'});
    res.end(typeof data === 'string' ? data : JSON.stringify(data));
  });
  await new Promise(r => backend.listen(0, '127.0.0.1', r));
  const worker = createWorker({database: join(dir, 'accounts.db'), host: 'studio.test',
    upstreamSecretFile: join(dir, 'transport'), dataRoot: root,
    backendPort: backend.address().port, webRoot: dir, staticRoot: dir});
  await new Promise(r => worker.server.listen(0, '127.0.0.1', r));
  t.after(async () => {
    await new Promise(r => worker.server.close(r));
    await new Promise(r => backend.close(r));
    worker.auth.db.close();
    rmSync(dir, {recursive: true, force: true});
  });
  const owner = worker.auth.addOwner('owner', 'test-password');
  const token = worker.auth.issue(owner, ['media.read']);
  const own = (id, status = 200, data = {file_path: join(root, 'owned', 'clip.mp4')}) => {
    worker.auth.db.prepare('INSERT INTO media VALUES(?,?,?,?)').run(id, owner, 'test-hash', 'clip.mp4');
    replies.set(id, [status, data]);
  };
  const request = (path = '/media/owned/clip.mp4', method = 'GET', headers = {}) =>
    fetch(`http://127.0.0.1:${worker.server.address().port}/studio/bridge`, {
      method, headers: {authorization: 'Bearer test-transport',
        'x-studio-access': 'Bearer ' + token.access_token, 'x-studio-path': path, ...headers},
    });
  return {worker, owner, token, own, request, replies, calls, bytes, root};
}

test('deleted records before valid ownership do not block GET, HEAD or Range', async t => {
  const f = await fixture(t);
  f.own(1, 404, {error: 'Video not found'});
  f.own(2);
  for (const [method, headers, expected, body] of [
    ['GET', {}, 200, f.bytes],
    ['HEAD', {}, 200, Buffer.alloc(0)],
    ['GET', {range: 'bytes=2-7'}, 206, f.bytes.subarray(2, 8)],
    ['HEAD', {range: 'bytes=2-7'}, 206, Buffer.alloc(0)],
  ]) {
    f.calls.length = 0;
    const r = await f.request(undefined, method, headers);
    assert.equal(r.status, expected);
    assert.equal(r.headers.get('content-type'), 'video/mp4');
    assert.equal(r.headers.get('cache-control'), 'no-store');
    assert.equal(r.headers.get('accept-ranges'), 'bytes');
    if (expected === 206) assert.equal(r.headers.get('content-range'), `bytes 2-7/${f.bytes.length}`);
    assert.deepEqual(Buffer.from(await r.arrayBuffer()), body);
    assert.deepEqual(f.calls, [1, 2]);
  }
  assert.equal((await f.request(undefined, 'GET', {range: 'bytes=100-200'})).status, 416);
});

test('stop checking after proven ownership even when later records are deleted or unavailable', async t => {
  const f = await fixture(t);
  f.own(1);
  f.own(2, 404, {error: 'Video not found'});
  f.own(3, 503, {error: 'Backend unavailable'});
  const r = await f.request();
  assert.equal(r.status, 200);
  assert.deepEqual(Buffer.from(await r.arrayBuffer()), f.bytes);
  assert.deepEqual(f.calls, [1]);
});

test('missing ownership stays denied; existing files are not authority', async t => {
  const f = await fixture(t);
  f.own(1, 404, {error: 'Video not found'});
  assert.equal((await f.request()).status, 403);
  f.own(2);
  assert.equal((await f.request('/media/other/clip.mp4')).status, 403);
  const other = f.worker.auth.addOwner('other', 'test-password');
  const otherToken = f.worker.auth.issue(other, ['media.read']);
  assert.equal((await f.request(undefined, 'GET', {'x-studio-access': 'Bearer ' + otherToken.access_token})).status, 403);
});

test('non-404 errors and malformed replies still fail closed before ownership is established', async t => {
  const f = await fixture(t);
  f.own(1);
  f.own(2);
  for (const [status, data, expected] of [
    [503, {error: 'Backend unavailable'}, 503],
    [403, {error: 'Forbidden'}, 403],
    [410, {error: 'Unexpected gone response'}, 410],
    [404, 'not JSON', 502],
    [200, 'not JSON', 502],
  ]) {
    f.replies.set(1, [status, data]);
    f.calls.length = 0;
    assert.equal((await f.request()).status, expected);
    assert.deepEqual(f.calls, [1]);
  }
});

test('scope, revoked tokens, traversal and realpath containment remain enforced', async t => {
  const f = await fixture(t);
  f.own(1);
  const noRead = f.worker.auth.issue(f.owner, ['media.upload']);
  assert.equal((await f.request(undefined, 'GET', {'x-studio-access': 'Bearer ' + noRead.access_token})).status, 403);
  assert.equal((await f.request('/media/owned/escape.mp4')).status, 404);
  assert.equal((await f.request('/media/%2e%2e/outside.mp4')).status, 400);
  assert.equal((await f.request('/media/owned%2fclip.mp4')).status, 400);
  f.worker.auth.revoke(f.owner, f.token.grant_id);
  assert.equal((await f.request()).status, 401);
});
