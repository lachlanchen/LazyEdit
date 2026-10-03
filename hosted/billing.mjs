import {randomUUID, randomBytes, createCipheriv, createDecipheriv} from 'node:crypto';
import {fail, digest} from '../studio/auth.mjs';
import {createPurchaseVerifier} from './purchase-verifier.mjs';
import {monthlyPlans} from './plans.mjs';
export {monthlyPlans} from './plans.mjs';

// The ledger only receives provider-verified results, never client entitlements.
export class BillingLedger {
  constructor(registry) {
    this.registry = registry; this.db = registry.db;
    this.db.exec(`CREATE TABLE IF NOT EXISTS billing_accounts(owner TEXT PRIMARY KEY, token TEXT UNIQUE, closed INTEGER DEFAULT 0);
      CREATE TABLE IF NOT EXISTS billing_receipts(provider TEXT, receipt TEXT, owner TEXT, product TEXT, revoked INTEGER, updated INTEGER, PRIMARY KEY(provider,receipt));
      CREATE TABLE IF NOT EXISTS billing_sources(provider TEXT, subscription TEXT, owner TEXT, product TEXT, expires INTEGER, active INTEGER, updated INTEGER, body TEXT, PRIMARY KEY(provider,subscription));`);
  }
  account(owner) {
    if (this.registry.db.prepare('SELECT 1 FROM closed_accounts WHERE owner=?').get(owner)) fail(401, 'Account deleted');
    this.db.prepare('INSERT OR IGNORE INTO billing_accounts(owner,token) VALUES(?,?)').run(owner, randomUUID());
    const value = this.db.prepare('SELECT * FROM billing_accounts WHERE owner=?').get(owner);
    if (value.closed) fail(401, 'Billing account deleted');
    return value.token;
  }
  accept(owner, value, encryptedSource) {
    const accountToken = this.account(owner);
    if (value.accountToken?.toLowerCase() !== accountToken.toLowerCase() || !monthlyPlans.some(p => p.product === value.product) || !['apple', 'google'].includes(value.provider) || typeof value.receipt !== 'string' || typeof value.subscription !== 'string' || !Number.isSafeInteger(value.expires) || !Number.isSafeInteger(value.updated) || value.updated > Date.now() + 60000) fail(403, 'Purchase does not belong to this Studio account');
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const receipt = digest(value.receipt), subscription = digest(value.subscription);
      const old = this.db.prepare('SELECT * FROM billing_receipts WHERE provider=? AND receipt=?').get(value.provider, receipt);
      const source = this.db.prepare('SELECT * FROM billing_sources WHERE provider=? AND subscription=?').get(value.provider, subscription);
      if (old && old.owner !== owner || source && source.owner !== owner) fail(409, 'Purchase is already bound to another Studio account');
      const revoked = Boolean(value.revoked || old?.revoked);
      if (!old || value.updated >= old.updated || revoked) this.db.prepare('INSERT INTO billing_receipts VALUES(?,?,?,?,?,?) ON CONFLICT(provider,receipt) DO UPDATE SET revoked=excluded.revoked,updated=max(updated,excluded.updated)').run(value.provider, receipt, owner, value.product, Number(revoked), value.updated);
      if (!source || value.updated >= source.updated) this.db.prepare('INSERT INTO billing_sources VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(provider,subscription) DO UPDATE SET product=excluded.product,expires=excluded.expires,active=excluded.active,updated=excluded.updated,body=excluded.body').run(value.provider, subscription, owner, value.product, value.expires, Number(value.active && !revoked), value.updated, encryptedSource);
      if (revoked && source && value.updated >= source.updated) this.db.prepare('UPDATE billing_sources SET active=0 WHERE provider=? AND subscription=?').run(value.provider, subscription);
      this.db.exec('COMMIT');
    } catch (error) {this.db.exec('ROLLBACK'); throw error;}
  }
  status(owner, now = Date.now()) {
    this.account(owner);
    const active = this.db.prepare('SELECT provider,product,expires,updated FROM billing_sources WHERE owner=? AND active=1 AND expires>? AND updated>? ORDER BY expires DESC LIMIT 1').get(owner, now, now - 120000);
    return active ? {active: true, ...active} : {active: false};
  }
  close(owner) {
    this.db.prepare('UPDATE billing_accounts SET closed=1 WHERE owner=?').run(owner);
    this.db.prepare('UPDATE billing_sources SET active=0,body=NULL WHERE owner=?').run(owner);
  }
}

export function createBilling(registry, config = {}, verifierOverride) {
  const ledger = new BillingLedger(registry);
  const verifier = verifierOverride || createPurchaseVerifier(config);
  // No sale until limits, quota enforcement and exact store products are qualified.
  const enabled = Boolean(config.enabled === true && config.benefitsApproved === true && config.quotaEnforced === true && config.productsQualified === true && /^[a-f0-9]{64}$/.test(config.encryptionKey || ''));
  const seal = value => {
    const iv = randomBytes(12), cipher = createCipheriv('aes-256-gcm', Buffer.from(config.encryptionKey, 'hex'), iv);
    const body = Buffer.concat([cipher.update(JSON.stringify(value)), cipher.final()]);
    return JSON.stringify({iv: iv.toString('base64url'), tag: cipher.getAuthTag().toString('base64url'), body: body.toString('base64url')});
  };
  const open = value => {
    const v = JSON.parse(value), cipher = createDecipheriv('aes-256-gcm', Buffer.from(config.encryptionKey, 'hex'), Buffer.from(v.iv, 'base64url'));
    cipher.setAuthTag(Buffer.from(v.tag, 'base64url'));
    return JSON.parse(Buffer.concat([cipher.update(Buffer.from(v.body, 'base64url')), cipher.final()]).toString());
  };
  const refreshing = new Set();
  return {
    ledger,
    async catalog(owner) {
      const accountToken = ledger.account(owner);
      if (enabled && !refreshing.has(owner)) {
        refreshing.add(owner);
        try {
          for (const row of registry.db.prepare('SELECT * FROM billing_sources WHERE owner=? AND body IS NOT NULL AND updated<? LIMIT 6').all(owner, Date.now() - 60000)) {
            try {const source = open(row.body), value = await verifier.verify(row.provider, source, accountToken, owner); ledger.accept(owner, value, row.body);}
            catch { /* No stale entitlement after 120 seconds; no secret provider errors in UI. */ }
          }
        } finally {refreshing.delete(owner);}
      }
      return {enabled, accountToken, providers: enabled ? verifier.providers() : [], plans: monthlyPlans.map(plan => ({...plan, benefits: config.benefits?.[plan.id] || null})), entitlement: ledger.status(owner), paidDownloadCreditEnabled: false};
    },
    async submit(owner, provider, body) {
      if (!enabled || !verifier.providers().includes(provider)) fail(503, 'Billing is being prepared. No charge will be made.');
      registry.throttle(`purchase:${owner}`);
      const token = ledger.account(owner), value = await verifier.verify(provider, body, token, owner);
      ledger.accept(owner, value, seal(body));
      if (value.active) await verifier.acknowledge?.(provider, body, value);
      return {ok: true, entitlement: ledger.status(owner)};
    },
  };
}
