import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {Registry} from './store.mjs';
import {BillingLedger, createBilling, monthlyPlans} from './billing.mjs';

test('store ledger binds purchases, survives refunds/replays and fails closed when stale', t => {
  const dir = mkdtempSync(join(tmpdir(), 'studio-billing-')), registry = new Registry(join(dir, 'registry.sqlite'), 'edit.test');
  t.after(() => {registry.db.close(); rmSync(dir, {recursive: true, force: true});});
  const alice = registry.addOwner('alice', 'test-only-long-password'), bob = registry.addOwner('bob', 'test-only-long-password'), ledger = new BillingLedger(registry);
  const now = Date.now(), proof = {provider: 'apple', product: monthlyPlans[0].product, receipt: 'test-transaction', subscription: 'test-subscription', accountToken: ledger.account(alice), updated: now, expires: now + 3600000, active: true, revoked: false};
  ledger.accept(alice, proof, 'encrypted-fixture'); assert.equal(ledger.status(alice).active, true);
  assert.throws(() => ledger.accept(bob, proof, 'fixture'), {status: 403});
  assert.throws(() => ledger.accept(bob, {...proof, accountToken: ledger.account(bob)}, 'fixture'), {status: 409});
  ledger.accept(alice, {...proof, updated: now + 1, revoked: true, active: false}, 'encrypted-fixture');
  ledger.accept(alice, {...proof, updated: now - 1}, 'encrypted-fixture');
  assert.equal(ledger.status(alice).active, false, 'older active proof cannot undo refund');
  ledger.accept(alice, {...proof, updated: now + 2}, 'encrypted-fixture');
  assert.equal(ledger.status(alice).active, false, 'even a later replay of the refunded receipt remains revoked');
  ledger.accept(alice, {...proof, receipt: 'renewal-transaction', updated: now + 3}, 'encrypted-fixture');
  assert.equal(ledger.status(alice).active, true, 'a new verified paid renewal can restore service');
  assert.equal(ledger.status(alice, now + 123000).active, false, 'stale state cannot grant indefinitely');
  registry.closeAccount(alice); ledger.close(alice);
  assert.throws(() => ledger.accept(alice, proof, 'fixture'), {status: 401});
});

test('prepared billing cannot charge or accept a client claimed entitlement', async t => {
  const dir = mkdtempSync(join(tmpdir(), 'studio-billing-off-')), registry = new Registry(join(dir, 'registry.sqlite'), 'edit.test');
  t.after(() => {registry.db.close(); rmSync(dir, {recursive: true, force: true});});
  const owner = registry.addOwner('tester', 'test-only-long-password'); let calls = 0;
  const billing = createBilling(registry, {}, {providers: () => ['apple'], verify: () => {calls++;}});
  const catalog = await billing.catalog(owner);
  assert.equal(catalog.enabled, false); assert.equal(catalog.paidDownloadCreditEnabled, false);
  assert.deepEqual(catalog.plans.map(p => p.requestedUSD), ['2.99', '14.99', '29.90']);
  assert.deepEqual(catalog.plans.map(p => p.benefits.processingMinutes), [10,60,150]);
  await assert.rejects(billing.submit(owner, 'apple', {verified: true, expires: Date.now() + 36000000}), {status: 503});
  assert.equal(calls, 0);
});
