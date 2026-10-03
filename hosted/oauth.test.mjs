import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync, sign} from 'node:crypto';
import {mkdtempSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {Registry} from './store.mjs';
import {createOAuth, challengeFor} from './oauth.mjs';
import {secret} from '../studio/auth.mjs';

test('provider proof, linking, account isolation and single-use transfer', async t => {
  const dir = mkdtempSync(join(tmpdir(), 'studio-oauth-'));
  const registry = new Registry(join(dir, 'registry.sqlite'), 'edit.test');
  t.after(() => {registry.db.close(); rmSync(dir, {recursive: true, force: true});});
  writeFileSync(join(dir, 'google-secret'), 'generated-test-only');
  const keys = generateKeyPairSync('rsa', {modulusLength: 2048});
  const jwk = {...keys.publicKey.export({format: 'jwk'}), kid: 'fixture', alg: 'RS256'};
  let nonce, subject = 'provider-subject', audience = 'studio.test.client', signatureGood = true;
  function jwt() {
    const now = Math.floor(Date.now() / 1000), encode = value => Buffer.from(JSON.stringify(value)).toString('base64url');
    const input = encode({alg: 'RS256', kid: 'fixture'}) + '.' + encode({iss: 'https://accounts.google.com', aud: audience, sub: subject, nonce, exp: now + 300, iat: now, email: 'same-email@example.test'});
    return input + '.' + (signatureGood ? sign('RSA-SHA256', Buffer.from(input), keys.privateKey).toString('base64url') : Buffer.from('invalid').toString('base64url'));
  }
  let revoked = false, missingRefresh = false;
  const oauth = createOAuth(registry, {encryptionKey: 'a'.repeat(64), google: {enabled: true, clientId: 'studio.test.client', clientSecretFile: join(dir, 'google-secret')}}, 'https://edit.test', async (url, options) => {
    if (url.endsWith('/revoke')) {
      assert.equal(options.body.get('token'), 'fixture-refresh-private'); revoked = true;
      return new Response('', {status: 200});
    }
    return new Response(JSON.stringify(url.includes('/certs') ? {keys: [jwk]} : {id_token: jwt(), ...(missingRefresh ? {} : {refresh_token: 'fixture-refresh-private'})}), {status: 200});
  });
  const alice = registry.addOwner('alice', 'test-only-long-password'), bob = registry.addOwner('bob', 'test-only-long-password');
  const verifier = secret();
  function start(owner) {
    const result = oauth.start('google', {challenge: challengeFor(verifier), target: 'native'}, owner, secret());
    const url = new URL(result.url); nonce = url.searchParams.get('nonce');
    assert.equal(url.searchParams.get('access_type'), owner ? 'offline' : null);
    assert.equal(url.searchParams.get('prompt'), owner ? 'consent select_account' : 'select_account');
    return {state: url.searchParams.get('state'), code: 'fixture-code'};
  }
  assert.deepEqual(oauth.providers(), ['google']);
  await assert.rejects(oauth.callback('google', start(undefined)), {status: 403}, 'email alone must not create or merge an account');
  missingRefresh = true;
  await assert.rejects(oauth.callback('google', start(alice)), {status: 502}, 'a new link must support provider revocation');
  missingRefresh = false;
  const linkFlow = start(alice), callback = await oauth.callback('google', linkFlow);
  await assert.rejects(oauth.callback('google', linkFlow), {status: 401}, 'consumed state cannot replay');
  const ticket = new URL(callback).searchParams.get('ticket');
  assert.throws(() => oauth.redeem({ticket, verifier: secret()}), {status: 401});
  assert.equal(oauth.redeem({ticket, verifier}), alice);
  assert.throws(() => oauth.redeem({ticket, verifier}), {status: 401});
  await assert.rejects(oauth.callback('google', start(bob)), {status: 409}, 'another user cannot claim the linked provider');
  const login = await oauth.callback('google', start(undefined));
  assert.equal(oauth.redeem({ticket: new URL(login).searchParams.get('ticket'), verifier}), alice);
  assert.ok(!registry.db.prepare('SELECT refresh FROM oauth_links WHERE owner=?').get(alice).refresh.includes('fixture-refresh-private'));
  audience = 'another.app';
  await assert.rejects(oauth.callback('google', start(undefined)), {status: 401});
  audience = 'studio.test.client'; signatureGood = false;
  await assert.rejects(oauth.callback('google', start(undefined)), {status: 401});
  signatureGood = true;
  const badNonce = start(undefined); nonce = 'mismatch';
  await assert.rejects(oauth.callback('google', badNonce), {status: 401});
  await oauth.unlink(alice, 'google'); assert.equal(revoked, true); assert.deepEqual(oauth.links(alice), []);
  await assert.rejects(oauth.callback('google', start(undefined)), {status: 403}, 'a revoked link cannot sign in');
  await oauth.callback('google', start(alice));
  const late = start(undefined); registry.closeAccount(alice);
  await assert.rejects(oauth.callback('google', late), {status: 403}, 'deleted accounts cannot return through a provider');
});

test('unconfigured providers stay disabled', () => {
  const dir = mkdtempSync(join(tmpdir(), 'studio-oauth-off-')), registry = new Registry(join(dir, 'registry.sqlite'), 'edit.test');
  try {const oauth = createOAuth(registry, {}, 'https://edit.test'); assert.deepEqual(oauth.providers(), []); assert.throws(() => oauth.start('apple', {}, undefined, 'fixture'), {status: 503});}
  finally {registry.db.close(); rmSync(dir, {recursive: true, force: true});}
});
