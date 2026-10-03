import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {mkdtempSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {assertWorkspaceIdle} from './lifecycle.mjs';
import {createGateway} from './gateway.mjs';

test('deletion activity checks reject active queues, processing and unavailable replies', async t => {
  let queue = {jobs: []}, state = {steps: {burn: {status: 'done'}}};
  const server = http.createServer((req, res) => {res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(req.url === '/api/videos' ? {videos: [{id: 1}]} : req.url.includes('process-status') ? state : queue));});
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => {server.closeAllConnections(); server.close();});
  const port = server.address().port;
  await assertWorkspaceIdle(port, port);
  queue = {jobs: [{status: 'queued'}]};
  await assert.rejects(assertWorkspaceIdle(port, port), {status: 409});
  queue = {jobs: []}; state = {steps: {transcribe: {status: 'working'}}};
  await assert.rejects(assertWorkspaceIdle(port, port), {status: 409});
  queue = {status: 'unavailable', jobs: []};
  await assert.rejects(assertWorkspaceIdle(port, port), {status: 503});
});

test('member deletion requires password and confirmation, revokes sessions and preserves the operator', async t => {
  const dir = mkdtempSync(join(tmpdir(), 'studio-delete-'));
  const gateway = createGateway({database: join(dir, 'registry.sqlite'), domain: 'studio.test', capacity: 2});
  await new Promise(resolve => gateway.server.listen(0, '127.0.0.1', resolve));
  t.after(() => {gateway.server.closeAllConnections(); gateway.server.close(); gateway.registry.db.close(); rmSync(dir, {recursive: true, force: true});});
  const registry = gateway.registry, password = 'a-test-only-long-password';
  const member = registry.register({username: 'tester', password, invitation: registry.invite()}, 'fixture');
  const token = registry.issue(member, undefined, 'test', 'browser');
  const send = body => new Promise((resolve, reject) => {
    const request = http.request({hostname: '127.0.0.1', port: gateway.server.address().port, path: '/delete', method: 'POST', headers: {host: 'studio.test', origin: 'https://studio.test', cookie: '__Host-hosted=' + token.access_token, 'content-type': 'application/json'}}, response => {
      response.resume(); response.on('end', () => resolve({status: response.statusCode}));
    }); request.on('error', reject); request.end(JSON.stringify(body));
  });
  assert.equal((await send({confirm: 'different', password})).status, 400);
  assert.equal((await send({confirm: 'tester', password: 'wrong'})).status, 401);
  assert.equal((await send({confirm: 'tester', password})).status, 202);
  assert.equal(registry.workspace(member).status, 'deleting');
  assert.throws(() => registry.principal(token.access_token), {status: 401});
  assert.throws(() => registry.refresh(token.refresh_token), {status: 401});
  assert.throws(() => registry.login('tester', password, 'fixture'), {status: 401});
  assert.equal(registry.db.prepare('SELECT 1 FROM users WHERE username=?').get('tester'), undefined);
  const admin = registry.addOwner('lachlanchen', password);
  registry.linkOwner(registry.db.prepare('SELECT * FROM users WHERE id=?').get(admin));
  assert.throws(() => registry.closeAccount(admin), {status: 403});
  assert.equal(registry.login('lachlanchen', password, 'admin'), admin);
});
