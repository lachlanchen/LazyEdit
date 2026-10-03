# Studio identity operations

Studio registration remains invite-only. Apple/Google identities authenticate
an existing linked account; they never create an account from a matching email.
An invited member signs in with the Studio password and explicitly links the
provider from Account. Linking and unlinking require the current Studio
password. The normal login screen then offers the configured provider.

The gateway checks a provider-signed identity, issuer, audience, nonce and
expiry. Authorization state is single-use. Native/browser receipt redemption
requires its original verifier and is single-use. The receipt identifies the
same Studio account, with its original private workspace and role. Email is
not an identity key and cannot grant administrator/Pi access.

## Google

Use an app-owned Google Cloud project and Web application client. Register the
exact callback `https://edit.lazying.art/accounts/oauth/callback/google`.
Only `openid email` are requested. This is Studio identity, not a YouTube
publishing authorization; social profiles and their login flow remain separate.

Download/capture the client JSON into an owner-only private directory, never
repository files or terminal output. Configure the host with its protected
control-plane directory:

```bash
python scripts/studio/configure_google_signin.py \
  --state /private/hosted-state \
  --client-json /private/google-client.json
```

The default is disabled. `--enable` makes the prepared client available after
the gateway next starts; it does not prove provider qualification. The helper
checks the HTTPS callback, owner-only files and encryption-key preservation,
backs up configuration and copies only the client credential to the protected
registry mount. It does not restart workers or change any other Cloud project.

Password-confirmed linking requests offline access and consent once, so Studio
can retain an AES-GCM encrypted refresh credential for revocation. Normal login
only selects the provider account. Unlinking calls Google's revocation endpoint
before deleting the identity link. If revocation fails, the link remains so the
user can retry. A revoked/unlinked identity cannot sign in to Studio until
explicitly linked again.

The real Google browser test on 2026-10-04 qualified linking, sign-in, encrypted
revocation, unlinking and denial after unlink. The project is still
External/Testing, not brand-verified. Google's [publishing-state documentation](https://developers.google.com/identity/protocols/oauth2/production-readiness/overview)
explains the exception for identity-only scopes and the separate verification
and Workspace administrator controls. Public store review, OAuth production
status, brand verification and native OAuth testing are separate milestones.

## Apple

Use **this app's** primary App ID `art.lazying.lazyedit` and Services ID
`art.lazying.lazyedit.web`. Enable Sign in with Apple on the primary, configure
the Services ID for `edit.lazying.art` and callback
`https://edit.lazying.art/accounts/oauth/callback/apple`, and create a Sign in
with Apple key associated only with that primary. Do not accept a dropdown's
default selection if it points to another app. [Apple's web configuration guide](https://developer.apple.com/help/account/capabilities/configure-sign-in-with-apple-for-the-web)
describes these separate resources.

Download the `.p8` once into a protected directory, remove the browser's
download copy, and keep a secure private backup. Never dump the key, client
secret, OAuth URL query, callback code, state or receipt to a log. Credential
pages sometimes put the full secret inside a Copy button's accessible label;
generic aria-label/DOM inventories on those pages are unsafe.

Prepare a private JSON object with `clientId`, `teamId`, `keyId`,
`primaryAppId`, `privateKeyFile` and `redirectURI`, then run:

```bash
python scripts/studio/configure_apple_signin.py \
  --state /private/hosted-state \
  --client-json /private/apple-client.json
```

It defaults to disabled, validates the app identifiers and P-256 private key,
and preserves the existing Google configuration/encryption key. Like Google's
helper, it saves a rollback and never restarts services. Apple qualification
requires real linking, fresh sign-in and revocation, not just a configured key.

Changing the primary App ID's capabilities can invalidate its distribution
profile. Reconcile the exact existing app/profile/certificate first, generate
a replacement profile using the existing certificate, and put it in the Mac's
private `~/Projects/LazyEditStudio/LazyEdit.mobileprovision`. Preserve the old
profile with the old build's receipts. `build_ios.sh` decodes and validates the
current profile and uses its name/UUID for archive/export. Rebuilding an
unchanged native binary merely to turn on a server provider is unnecessary.

## Promotion and qualification

Check both local/publication queues and manual processing in every affected
workspace. Promote or restart **only the hosted gateway** for identity-only
changes. Keep worker/provisioner images and the original owner/Pi untouched.
Preserve private configuration and Compose rollback files. Read back
`/accounts/oauth/providers`, verify a real link and fresh sign-in, and inspect
only booleans/counts when confirming encrypted credentials in the registry.

Contract tests cover replay, signature/nonce/audience, wrong account,
password-confirmed linking, unlinking and closed-account refusal. They do not
replace real provider/browser/native checks. Do not configure charging from
identity setup: monthly products, quotas and purchases have their own disabled
qualification gate.
