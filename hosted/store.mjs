import { AuthStore, secret, digest, fail } from '../studio/auth.mjs';

// This registry contains account routing, never media or platform credentials.
export class Registry extends AuthStore {
  constructor(path, domain, capacity = 3) {
    super(path);
    this.db.exec('PRAGMA busy_timeout=5000');
    if (!/^[a-z0-9.-]+$/.test(domain) || domain.includes('..')) throw Error('Invalid service domain');
    this.domain = domain;
    this.capacity = capacity;
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS invitations(hash TEXT PRIMARY KEY, expires INTEGER, used INTEGER DEFAULT 0);
      CREATE TABLE IF NOT EXISTS workspaces(
        id TEXT PRIMARY KEY, owner TEXT UNIQUE NOT NULL REFERENCES users(id),
        transport TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created INTEGER, lease INTEGER DEFAULT 0);
      CREATE TABLE IF NOT EXISTS entry_tickets(hash TEXT PRIMARY KEY, workspace TEXT, expires INTEGER);
    `);
    if(!this.db.prepare('PRAGMA table_info(workspaces)').all().some(c=>c.name==='lease'))this.db.exec('ALTER TABLE workspaces ADD COLUMN lease INTEGER DEFAULT 0');
  }
  invite(hours = 72) {
    const token = secret();
    this.db.prepare('INSERT INTO invitations(hash,expires) VALUES(?,?)').run(digest(token), Date.now() + hours * 3600000);
    return token;
  }
  register({ username, password, invitation }, client) {
    this.throttle(`register:${client}`);
    if (!/^[a-z][a-z0-9_-]{2,31}$/.test(username || '')) fail(400, 'Use 3–32 lowercase letters, numbers, hyphens or underscores');
    if (typeof password !== 'string' || password.length < 12 || password.length > 128) fail(400, 'Use a password of 12–128 characters');
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const inv = this.db.prepare('SELECT * FROM invitations WHERE hash=? AND used=0 AND expires>?').get(digest(String(invitation || '')), Date.now());
      if (!inv) fail(400, 'Invitation unavailable');
      if (this.db.prepare('SELECT count(*) AS n FROM workspaces').get().n >= this.capacity) fail(503, 'Workspace capacity reached; contact the operator');
      if (this.db.prepare('SELECT 1 FROM users WHERE username=?').get(username)) fail(409, 'Username unavailable');
      const owner = this.addOwner(username, password), id = digest(secret()).slice(0, 24);
      this.db.prepare('INSERT INTO workspaces(id,owner,transport,created) VALUES(?,?,?,?)').run(id, owner, secret(), Date.now());
      this.db.prepare('UPDATE invitations SET used=1 WHERE hash=?').run(inv.hash);
      this.db.exec('COMMIT');
      return owner;
    } catch (e) { this.db.exec('ROLLBACK'); throw e; }
  }
  workspace(owner) { return this.db.prepare('SELECT * FROM workspaces WHERE owner=?').get(owner); }
  host(row) { return `w-${row.id}.${this.domain}`; }
  route(host) {
    const suffix = `.${this.domain}`;
    if (!host.startsWith('w-') || !host.endsWith(suffix)) return null;
    const id = host.slice(2, -suffix.length);
    if (!/^[a-z0-9-]{24}$/.test(id)) return null;
    return this.db.prepare("SELECT * FROM workspaces WHERE id=? AND status='ready'").get(id);
  }
  enter(owner) {
    const w = this.workspace(owner);
    if (w?.status !== 'ready') fail(409, 'Your workspace is being prepared');
    const ticket = secret();
    this.db.prepare('DELETE FROM entry_tickets WHERE expires<?').run(Date.now());
    this.db.prepare('INSERT INTO entry_tickets VALUES(?,?,?)').run(digest(ticket), w.id, Date.now()+60000);
    return `https://${this.host(w)}/hosted-entry?ticket=${ticket}`;
  }
  consume(ticket, workspace) {
    return Boolean(this.db.prepare('DELETE FROM entry_tickets WHERE hash=? AND workspace=? AND expires>? RETURNING hash')
      .get(digest(String(ticket || '')), workspace, Date.now()));
  }
}
