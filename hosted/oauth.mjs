// Optional identity linking. Registration remains invite-only; email is never identity.
import {createPublicKey, verify, sign, randomBytes, createCipheriv, createDecipheriv} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {secret, digest, fail} from '../studio/auth.mjs';

const proof = /^[A-Za-z0-9_-]{43}$/;
const definitions = {
  apple: {authorize: 'https://appleid.apple.com/auth/authorize', token: 'https://appleid.apple.com/auth/token', keys: 'https://appleid.apple.com/auth/keys', issuers: ['https://appleid.apple.com']},
  google: {authorize: 'https://accounts.google.com/o/oauth2/v2/auth', token: 'https://oauth2.googleapis.com/token', keys: 'https://www.googleapis.com/oauth2/v3/certs', issuers: ['https://accounts.google.com', 'accounts.google.com']},
};
export const challengeFor = verifier => Buffer.from(digest(verifier), 'hex').toString('base64url');

export function createOAuth(registry, config = {}, origin, fetcher = fetch) {
  registry.db.exec(`CREATE TABLE IF NOT EXISTS oauth_flows(hash TEXT PRIMARY KEY, provider TEXT, body TEXT, expires INTEGER);
    CREATE TABLE IF NOT EXISTS oauth_links(provider TEXT, subject TEXT, owner TEXT, refresh TEXT, PRIMARY KEY(provider,subject), UNIQUE(provider,owner));
    CREATE TABLE IF NOT EXISTS oauth_receipts(hash TEXT PRIMARY KEY, owner TEXT, challenge TEXT, expires INTEGER);`);
  const settings = Object.create(null);
  for (const name of Object.keys(definitions)) {
    const candidate = config[name];
    if (candidate?.enabled !== true || !candidate.clientId || !/^[a-f0-9]{64}$/.test(config.encryptionKey || '')) continue;
    if (name === 'apple') {
      if (!candidate.keyId || !candidate.teamId || !candidate.privateKeyFile) continue;
      settings[name] = {...candidate, key: readFileSync(candidate.privateKeyFile, 'utf8')};
    } else if (candidate.clientSecretFile) settings[name] = {...candidate, clientSecret: readFileSync(candidate.clientSecretFile, 'utf8').trim()};
  }
  const cache = new Map();
  async function remote(url, options = {}) {
    const result = await fetcher(url, {...options, redirect: 'error', signal: AbortSignal.timeout(20000)});
    if (!result.ok) { await result.body?.cancel(); fail(502, 'Identity provider could not finish the request; try again'); }
    const text = await result.text();
    if (text.length > 100000) fail(502, 'Invalid identity response');
    try { return JSON.parse(text); } catch { fail(502, 'Invalid identity response'); }
  }
  function encrypt(value) {
    const iv = randomBytes(12), cipher = createCipheriv('aes-256-gcm', Buffer.from(config.encryptionKey, 'hex'), iv);
    const body = Buffer.concat([cipher.update(value), cipher.final()]);
    return JSON.stringify({iv: iv.toString('base64url'), tag: cipher.getAuthTag().toString('base64url'), body: body.toString('base64url')});
  }
  function decrypt(value) {
    const v = JSON.parse(value), cipher = createDecipheriv('aes-256-gcm', Buffer.from(config.encryptionKey, 'hex'), Buffer.from(v.iv, 'base64url'));
    cipher.setAuthTag(Buffer.from(v.tag, 'base64url'));
    return Buffer.concat([cipher.update(Buffer.from(v.body, 'base64url')), cipher.final()]).toString();
  }
  const redirect = name => `${origin}/accounts/oauth/callback/${name}`;
  function clientSecret(name) {
    const s = settings[name];
    if (name === 'google') return s.clientSecret;
    const now = Math.floor(Date.now() / 1000);
    const input = Buffer.from(JSON.stringify({alg: 'ES256', kid: s.keyId})).toString('base64url') + '.' + Buffer.from(JSON.stringify({iss: s.teamId, iat: now, exp: now + 300, aud: 'https://appleid.apple.com', sub: s.clientId})).toString('base64url');
    return input + '.' + sign('sha256', Buffer.from(input), {key: s.key, dsaEncoding: 'ieee-p1363'}).toString('base64url');
  }
  async function identity(name, token, nonce) {
    if (typeof token !== 'string' || token.length > 16000) fail(401, 'Invalid provider identity');
    let header, claims, parts;
    try { parts = token.split('.'); header = JSON.parse(Buffer.from(parts[0], 'base64url')); claims = JSON.parse(Buffer.from(parts[1], 'base64url')); } catch { fail(401, 'Invalid provider identity'); }
    if (parts.length !== 3 || header.alg !== 'RS256' || typeof header.kid !== 'string') fail(401, 'Invalid provider identity');
    let keys = cache.get(name);
    if (!keys || keys.until < Date.now() || !keys.values.some(key => key.kid === header.kid)) {
      const data = await remote(definitions[name].keys);
      if (!Array.isArray(data.keys) || data.keys.length > 20) fail(502, 'Invalid provider keys');
      keys = {values: data.keys, until: Date.now() + 3600000}; cache.set(name, keys);
    }
    const key = keys.values.find(value => value.kid === header.kid && value.kty === 'RSA' && (!value.alg || value.alg === 'RS256'));
    if (!key || !verify('RSA-SHA256', Buffer.from(parts[0] + '.' + parts[1]), createPublicKey({key, format: 'jwk'}), Buffer.from(parts[2], 'base64url'))) fail(401, 'Invalid provider signature');
    const now = Math.floor(Date.now() / 1000);
    if (!definitions[name].issuers.includes(claims.iss) || claims.aud !== settings[name].clientId || claims.nonce !== nonce || typeof claims.sub !== 'string' || !claims.sub || claims.sub.length > 300 || !Number.isFinite(claims.exp) || claims.exp <= now || !Number.isFinite(claims.iat) || claims.iat < now - 600 || claims.iat > now + 60) fail(401, 'Provider identity expired or did not match Studio');
    return claims;
  }
  return {
    providers: () => Object.keys(settings),
    links: owner => registry.db.prepare('SELECT provider FROM oauth_links WHERE owner=?').all(owner).map(row => row.provider),
    start(name, body, owner, client) {
      if (!settings[name]) fail(503, 'This sign-in provider is not configured');
      if (!proof.test(body.challenge || '') || !['native', 'web'].includes(body.target)) fail(400, 'Invalid sign-in challenge');
      registry.throttle(`oauth:${client}`);
      const flow = secret(), verifier = secret(), nonce = secret();
      registry.db.prepare('DELETE FROM oauth_flows WHERE expires<?').run(Date.now());
      // The owner may finish a provider login later. Only the pending flow has
      // a longer window; provider identity freshness and the 2-minute PKCE
      // transfer receipt remain unchanged.
      registry.db.prepare('INSERT INTO oauth_flows VALUES(?,?,?,?)').run(digest(flow), name, JSON.stringify({challenge: body.challenge, target: body.target, owner: owner || null, verifier, nonce}), Date.now() + 3600000);
      const url = new URL(definitions[name].authorize);
      const values = {client_id: settings[name].clientId, redirect_uri: redirect(name), response_type: 'code', scope: name === 'apple' ? 'name email' : 'openid email', state: flow, nonce};
      if (name === 'apple') values.response_mode = 'form_post';
      else {
        Object.assign(values, {code_challenge: challengeFor(verifier), code_challenge_method: 'S256', prompt: owner ? 'consent select_account' : 'select_account'});
        // Request revocation credentials once while password-confirmed linking.
        // Normal sign-in need not repeatedly ask for consent or offline access.
        if (owner) values.access_type = 'offline';
      }
      for (const [key, value] of Object.entries(values)) url.searchParams.set(key, value);
      return {url: url.href};
    },
    async callback(name, body) {
      const expired=()=>{throw Object.assign(Error('Sign-in expired; start again'),{status:401,oauthReason:'expired'});};
      if (!settings[name] || !proof.test(body.state || '')) expired();
      const row = registry.db.prepare('DELETE FROM oauth_flows WHERE hash=? AND provider=? AND expires>? RETURNING body').get(digest(body.state), name, Date.now());
      if (!row) expired();
      if(body.error==='access_denied')throw Object.assign(Error('Sign-in cancelled; start again when ready'),{status:401,oauthReason:'cancelled'});
      if(typeof body.code!=='string'||!body.code||body.code.length>4096)fail(401,'Provider sign-in was incomplete; start again');
      const flow = JSON.parse(row.body);
      const values = {grant_type: 'authorization_code', code: body.code, client_id: settings[name].clientId, client_secret: clientSecret(name), redirect_uri: redirect(name)};
      if (name === 'google') values.code_verifier = flow.verifier;
      const tokens = await remote(definitions[name].token, {method: 'POST', headers: {'content-type': 'application/x-www-form-urlencoded'}, body: new URLSearchParams(values)});
      const claims = await identity(name, tokens.id_token, flow.nonce);
      const prior = registry.db.prepare('SELECT * FROM oauth_links WHERE provider=? AND subject=?').get(name, claims.sub);
      const owner = flow.owner || prior?.owner;
      if (!owner || registry.db.prepare('SELECT 1 FROM closed_accounts WHERE owner=?').get(owner)) fail(403, 'Create an invited Studio account first, then link this provider in Account');
      if (flow.owner) {
        if (prior && prior.owner !== flow.owner) fail(409, 'Provider is linked to another Studio account');
        const existing = registry.db.prepare('SELECT subject FROM oauth_links WHERE provider=? AND owner=?').get(name, owner);
        if (existing && existing.subject !== claims.sub) fail(409, 'Unlink the current provider account first');
        if (!tokens.refresh_token && !prior?.refresh) fail(502, 'The provider did not provide account-revocation credentials');
        registry.db.prepare('INSERT INTO oauth_links VALUES(?,?,?,?) ON CONFLICT(provider,subject) DO UPDATE SET refresh=excluded.refresh').run(name, claims.sub, owner, tokens.refresh_token ? encrypt(tokens.refresh_token) : prior?.refresh || null);
      }
      const ticket = secret();
      registry.db.prepare('DELETE FROM oauth_receipts WHERE expires<?').run(Date.now());
      registry.db.prepare('INSERT INTO oauth_receipts VALUES(?,?,?,?)').run(digest(ticket), owner, flow.challenge, Date.now() + 120000);
      return flow.target === 'native' ? `art.lazying.lazyedit://auth?ticket=${ticket}` : `${origin}/accounts#ticket=${ticket}`;
    },
    failureLocation(error) {
      const reason=['expired','cancelled'].includes(error.oauthReason)?error.oauthReason:error.status===403?'unlinked':'provider';
      return `${origin}/accounts?oauth_error=${reason}`;
    },
    redeem(body) {
      if (!proof.test(body.ticket || '') || !proof.test(body.verifier || '')) fail(401, 'Invalid sign-in receipt');
      const row = registry.db.prepare('SELECT * FROM oauth_receipts WHERE hash=? AND expires>?').get(digest(body.ticket), Date.now());
      if (!row || row.challenge !== challengeFor(body.verifier) || registry.db.prepare('SELECT 1 FROM closed_accounts WHERE owner=?').get(row.owner)) fail(401, 'Sign-in receipt expired or mismatched');
      registry.db.prepare('DELETE FROM oauth_receipts WHERE hash=?').run(row.hash);
      return row.owner;
    },
    async unlink(owner, name) {
      const row = registry.db.prepare('SELECT * FROM oauth_links WHERE owner=? AND provider=?').get(owner, name);
      if (!row) return;
      if (row.refresh) {
        if (!settings[name]) fail(503, 'Provider revocation is temporarily unavailable');
        const values = name === 'apple' ? {client_id: settings[name].clientId, client_secret: clientSecret(name), token: decrypt(row.refresh), token_type_hint: 'refresh_token'} : {token: decrypt(row.refresh)};
        const response = await fetcher(name === 'apple' ? 'https://appleid.apple.com/auth/revoke' : 'https://oauth2.googleapis.com/revoke', {method: 'POST', redirect: 'error', signal: AbortSignal.timeout(20000), headers: {'content-type': 'application/x-www-form-urlencoded'}, body: new URLSearchParams(values)});
        await response.body?.cancel(); if (!response.ok) fail(502, 'Provider revocation did not finish; try again');
      }
      registry.db.prepare('DELETE FROM oauth_links WHERE owner=? AND provider=?').run(owner, name);
    },
  };
}
