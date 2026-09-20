import { DatabaseSync } from 'node:sqlite';
import { randomBytes, scryptSync, timingSafeEqual, createHash } from 'node:crypto';
import { chmodSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

export const digest = value => createHash('sha256').update(value).digest('hex');
export const secret = () => randomBytes(32).toString('base64url');
export const SCOPES = ['media.read', 'media.upload', 'edit.submit', 'jobs.read', 'publication.prepare', 'publication.publish'];
export function fail(status, message) { throw Object.assign(new Error(message), { status }); }
export function passwordHash(password, salt = randomBytes(16).toString('hex')) {
  return `${salt}:${scryptSync(password, salt, 64).toString('hex')}`;
}
function verify(password, stored) {
  const [salt, hash] = stored.split(':');
  return timingSafeEqual(scryptSync(password, salt, 64), Buffer.from(hash, 'hex'));
}
export class AuthStore {
  constructor(path) {
    mkdirSync(dirname(path), { recursive: true, mode: 0o700 });
    this.db = new DatabaseSync(path); chmodSync(path, 0o600);
    this.db.exec(`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
      CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT);
      CREATE TABLE IF NOT EXISTS grants (id TEXT PRIMARY KEY, owner TEXT NOT NULL, label TEXT, scopes TEXT, kind TEXT, revoked INTEGER DEFAULT 0, created INTEGER);
      CREATE TABLE IF NOT EXISTS tokens (hash TEXT PRIMARY KEY, grant_id TEXT, kind TEXT, expires INTEGER, FOREIGN KEY(grant_id) REFERENCES grants(id));
      CREATE TABLE IF NOT EXISTS devices (hash TEXT PRIMARY KEY, code TEXT UNIQUE, expires INTEGER, scopes TEXT, label TEXT, owner TEXT, approved INTEGER DEFAULT 0, polled INTEGER DEFAULT 0);
      CREATE TABLE IF NOT EXISTS media (video_id INTEGER PRIMARY KEY, owner TEXT NOT NULL, sha256 TEXT, filename TEXT);
      CREATE TABLE IF NOT EXISTS uploads (id TEXT PRIMARY KEY, owner TEXT, filename TEXT, title TEXT, size INTEGER, sha256 TEXT, offset INTEGER DEFAULT 0, expires INTEGER, receipt TEXT);
      CREATE TABLE IF NOT EXISTS intents (id TEXT PRIMARY KEY, owner TEXT, key TEXT, fingerprint TEXT, response TEXT, state TEXT, created INTEGER, UNIQUE(owner,key));
      CREATE TABLE IF NOT EXISTS attempts (key TEXT PRIMARY KEY, count INTEGER, until INTEGER);`);
  }
  addOwner(username, password) {
    const exists = this.db.prepare('SELECT * FROM users WHERE username=?').get(username);
    if (exists) return exists.id;
    const id = secret(); this.db.prepare('INSERT INTO users VALUES(?,?,?)').run(id, username, passwordHash(password)); return id;
  }
  throttle(key) {
    const now = Date.now(); const row = this.db.prepare('SELECT * FROM attempts WHERE key=?').get(key);
    if (row && row.until > now && row.count >= 8) fail(429, 'Too many attempts. Wait 15 minutes.');
    this.db.prepare('INSERT OR REPLACE INTO attempts VALUES(?,?,?)').run(key, row && row.until > now ? row.count + 1 : 1, row && row.until > now ? row.until : now + 900000);
  }
  login(username, password, client) {
    this.throttle(`login:${client}`);
    const row = this.db.prepare('SELECT * FROM users WHERE username=?').get(username);
    if (!row) { scryptSync(String(password).slice(0,256), 'dummy-user-salt', 64); fail(401, 'Invalid username or password'); }
    if (!verify(String(password).slice(0,256), row.password)) fail(401, 'Invalid username or password');
    this.db.prepare('DELETE FROM attempts WHERE key=?').run(`login:${client}`); return row.id;
  }
  issue(owner, scopes = SCOPES, label = 'LightMind', kind = 'device') {
    if (!Array.isArray(scopes) || !scopes.length || scopes.some(s => !SCOPES.includes(s))) fail(400, 'Invalid scopes');
    const id = secret();
    this.db.prepare('INSERT INTO grants(id,owner,label,scopes,kind,created) VALUES(?,?,?,?,?,?)').run(id, owner, String(label).slice(0,80), JSON.stringify(scopes), kind, Date.now());
    return this.mint(id, kind);
  }
  mint(grant, kind = 'device') {
    const access = secret(), refresh = secret(), ttl = kind === 'browser' ? 43200 : 900;
    this.db.prepare('INSERT INTO tokens VALUES(?,?,?,?)').run(digest(access), grant, 'access', Date.now()+ttl*1000);
    this.db.prepare('INSERT INTO tokens VALUES(?,?,?,?)').run(digest(refresh), grant, 'refresh', Date.now()+30*86400000);
    return { access_token: access, refresh_token: refresh, token_type: 'Bearer', expires_in: ttl, grant_id: grant };
  }
  principal(token, kind = 'access') {
    if (!token || token.length > 200) fail(401, 'Authentication required');
    const r = this.db.prepare('SELECT g.*,t.expires FROM tokens t JOIN grants g ON g.id=t.grant_id WHERE t.hash=? AND t.kind=? AND t.expires>? AND g.revoked=0').get(digest(token), kind, Date.now());
    if (!r) fail(401, 'Credential expired or revoked');
    return { ...r, scopes: JSON.parse(r.scopes) };
  }
  refresh(token) {
    const p = this.principal(token, 'refresh');
    // Rotate refresh credentials. Revoke prior access tokens for this grant as well.
    this.db.prepare('DELETE FROM tokens WHERE grant_id=?').run(p.id);
    return this.mint(p.id, p.kind);
  }
  revoke(owner, id) { this.db.prepare('UPDATE grants SET revoked=1 WHERE id=? AND owner=?').run(id, owner); }
  device(scopes, label, client) {
    this.throttle(`device:${client}`);
    if (!Array.isArray(scopes) || !scopes.length || scopes.some(s=>!SCOPES.includes(s))) fail(400,'Invalid scopes');
    const code = randomBytes(5).toString('hex').toUpperCase(), token = secret();
    this.db.prepare('DELETE FROM devices WHERE expires<?').run(Date.now());
    this.db.prepare('INSERT INTO devices(hash,code,expires,scopes,label) VALUES(?,?,?,?,?)').run(digest(token), code, Date.now()+600000, JSON.stringify(scopes), String(label||'LightMind').slice(0,80));
    return {device_code:token,user_code:code,expires_in:600,interval:5};
  }
  approve(owner, code) {
    const row=this.db.prepare('SELECT * FROM devices WHERE code=? AND expires>?').get(code,Date.now());
    if(!row || row.approved) fail(400,'Code unavailable');
    this.db.prepare('UPDATE devices SET owner=?,approved=1 WHERE code=?').run(owner,code);
  }
  poll(token) {
    const row=this.db.prepare('SELECT * FROM devices WHERE hash=? AND expires>?').get(digest(token||''),Date.now());
    if(!row) fail(400,'expired_token');
    if(Date.now()-row.polled<4500) fail(429,'slow_down');
    this.db.prepare('UPDATE devices SET polled=? WHERE hash=?').run(Date.now(),row.hash);
    if(!row.approved) fail(428,'authorization_pending');
    this.db.prepare('DELETE FROM devices WHERE hash=?').run(row.hash);
    return this.issue(row.owner,JSON.parse(row.scopes),row.label);
  }
  own(p,videoId) {
    if(p.kind==='browser') return; // Single explicitly configured owner controls the existing library.
    if(!this.db.prepare('SELECT 1 FROM media WHERE video_id=? AND owner=?').get(Number(videoId),p.owner)) fail(403,'Media is not owned by this account');
  }
}
