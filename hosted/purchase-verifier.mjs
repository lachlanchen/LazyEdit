import {readFileSync} from 'node:fs';
import {fail} from '../studio/auth.mjs';
import {monthlyPlans} from './plans.mjs';

const bundle = 'art.lazying.lazyedit', appId = 6814061525;
const products = new Set(monthlyPlans.map(plan => plan.product));
export function createPurchaseVerifier(config) {
  let apple, google;
  const enabled = Object.keys({apple: config.apple, google: config.google}).filter(name => config[name]?.enabled);
  async function appleClients(sandbox) {
    if (!apple) {
      const sdk = await import('@apple/app-store-server-library'), s = config.apple;
      const roots = s.rootCertificateFiles.map(file => readFileSync(file));
      const key = readFileSync(s.privateKeyFile, 'utf8');
      apple = {sdk, key, roots};
    }
    const environment = sandbox ? apple.sdk.Environment.SANDBOX : apple.sdk.Environment.PRODUCTION;
    return {verifier: new apple.sdk.SignedDataVerifier(apple.roots, true, environment, bundle, appId), client: new apple.sdk.AppStoreServerAPIClient(apple.key, config.apple.keyId, config.apple.issuerId, bundle, environment)};
  }
  async function play(method, path, body) {
    if (!google) {const {GoogleAuth} = await import('google-auth-library'); google = new GoogleAuth({keyFile: config.google.serviceAccountFile, scopes: ['https://www.googleapis.com/auth/androidpublisher']});}
    const client = await google.getClient();
    const reply = await client.request({url: `https://androidpublisher.googleapis.com/androidpublisher/v3/applications/${bundle}${path}`, method, ...(body ? {data: body} : {}), timeout: 20000});
    return reply.data;
  }
  return {
    providers: () => enabled,
    async verify(provider, body, accountToken, owner) {
      if (!enabled.includes(provider)) fail(503, 'Store verification is unavailable');
      if (provider === 'apple') {
        if (typeof body.signedTransaction !== 'string' || body.signedTransaction.length > 32000) fail(400, 'Missing signed App Store transaction');
        const sandbox = body.environment === 'Sandbox';
        if (sandbox && !config.sandboxAccounts?.includes(owner)) fail(403, 'Sandbox purchases are restricted to test accounts');
        const {client, verifier} = await appleClients(sandbox);
        const claimed = await verifier.verifyAndDecodeTransaction(body.signedTransaction);
        const fresh = await client.getTransactionInfo(claimed.transactionId);
        let transaction = await verifier.verifyAndDecodeTransaction(fresh.signedTransactionInfo), status = 0, grace = 0;
        const validate = value => {
          if (value.bundleId !== bundle || value.originalTransactionId !== claimed.originalTransactionId || !products.has(value.productId) || value.appAccountToken?.toLowerCase() !== accountToken.toLowerCase() || value.type !== 'Auto-Renewable Subscription' || value.inAppOwnershipType !== 'PURCHASED') fail(403, 'Purchase does not belong to this Studio account');
        };
        validate(claimed); validate(transaction);
        const current = await client.getAllSubscriptionStatuses(transaction.originalTransactionId);
        for (const group of current.data || []) for (const item of group.lastTransactions || []) {
          if (item.originalTransactionId !== transaction.originalTransactionId) continue;
          const candidate = await verifier.verifyAndDecodeTransaction(item.signedTransactionInfo); validate(candidate);
          if ((candidate.expiresDate || 0) >= (transaction.expiresDate || 0)) {
            transaction = candidate; status = item.status;
            if (status === 4 && item.signedRenewalInfo) {
              const renewal = await verifier.verifyAndDecodeRenewalInfo(item.signedRenewalInfo);
              if (renewal.originalTransactionId === transaction.originalTransactionId) grace = renewal.gracePeriodExpiresDate || 0;
            }
          }
        }
        const expires = Math.max(transaction.expiresDate || 0, status === 4 ? grace : 0);
        return {provider, accountToken, product: transaction.productId, receipt: String(transaction.transactionId), subscription: String(transaction.originalTransactionId), expires, updated: Date.now(), revoked: Boolean(transaction.revocationDate || status === 5), active: [1, 4].includes(status) && expires > Date.now() && !transaction.revocationDate};
      }
      if (typeof body.purchaseToken !== 'string' || !body.purchaseToken || body.purchaseToken.length > 8000) fail(400, 'Missing Play purchase token');
      const value = await play('GET', `/purchases/subscriptionsv2/tokens/${encodeURIComponent(body.purchaseToken)}`);
      if (value.externalAccountIdentifiers?.obfuscatedExternalAccountId !== accountToken) fail(403, 'Purchase does not belong to this Studio account');
      const items = (value.lineItems || []).filter(item => products.has(item.productId)).sort((a, b) => Date.parse(b.expiryTime) - Date.parse(a.expiryTime));
      const item = items[0], expires = Date.parse(item?.expiryTime || '');
      if (!item || !Number.isFinite(expires)) fail(403, 'Unsupported subscription');
      const active = ['SUBSCRIPTION_STATE_ACTIVE', 'SUBSCRIPTION_STATE_IN_GRACE_PERIOD', 'SUBSCRIPTION_STATE_CANCELED'].includes(value.subscriptionState) && expires > Date.now();
      return {provider, accountToken, product: item.productId, receipt: item.latestSuccessfulOrderId || value.latestOrderId || body.purchaseToken, subscription: body.purchaseToken, expires, updated: Date.now(), active, revoked: value.subscriptionState === 'SUBSCRIPTION_STATE_EXPIRED', needsAcknowledgement: value.acknowledgementState !== 'ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED'};
    },
    async acknowledge(provider, body, value) {
      if (provider === 'google' && value.active && value.needsAcknowledgement) await play('POST', `/purchases/subscriptions/${encodeURIComponent(value.product)}/tokens/${encodeURIComponent(body.purchaseToken)}:acknowledge`, {});
    },
  };
}
