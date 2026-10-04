# Studio account and native release handoff — 2026-10-04

## Current deployment contract

Use `https://edit.lazying.art`. Invite-only accounts share the domain but each
gets a private Docker database, media volume and browser profiles. The existing
Pi and owner backend are separate. Only `lachlanchen` may select that mode.
Membership, invitation and workspace routing checks are server-enforced.

Editing and preview are the normal member workflow. Social publication is a
separate operator-enabled capability, disabled for ordinary members and the
reviewer alike. Only approved accounts can open platform desktops or submit
posts; they still use their own profiles. Neither subscriptions nor invitations
grant publishing. Read [the capability contract](studio/editor-first-and-optional-publication.md)
before linking another app. The personal Pi is never reviewer infrastructure.

Upload, editing, subtitle context correction, metadata/cover preview, rendering
and explicit publication use the established Studio APIs and shared per-worker
queue. A new upload does not publish automatically. Choose platforms and review
the current output. Reuse an already verified run/archive when adding platforms;
keep submission IDs and reconcile an uncertain response before retrying.

The authorized Vancouver demo is seeded once per new private workspace, with a
verified source checksum and ownership mapping for browser and device tokens.
Owner channels, credentials, Nutstore contents and the owner library are never
copied. LightMind review credentials live only in the protected external handoff.

## Platform login desktop

For publishing-enabled accounts, the native Account screen opens an
authenticated private browser view. The PWA
has the same view. There is one desktop and at most one connected viewer per
workspace. A connection times out after 20 seconds; inactivity pauses streaming
after five minutes. Leaving the page also pauses it. Reconnect deliberately.

Fit or zoom the same stream; do not create another desktop to zoom. Keep QR
visible replaces the live desktop with a still image. Tap the still image to
focus a QR area; no live bandwidth is used until reconnecting. A second device
may be necessary to scan a displayed QR. Phone keyboard entry and clipboard
work only inside the selected private browser.

Chromium runs in kiosk mode with managed navigation allowlists for publication,
authentication and captcha origins. File picker dialogs, extensions, printing,
incognito/guest profiles and general desktop launchers are disabled. Openbox
captures browser chrome/developer-tool shortcuts. Private CDP remains enabled
for the publisher; disabling its targets also breaks uploads. File upload is
through Studio, with programmatic file selection in the publisher.

Close platform browser closes only the selected fixed platform via private CDP.
Profiles remain saved. It refuses closure while a publication is queued/running
or the browser is opening. Browser close leaves no general desktop application.
Pausing/freezing is distinct from closing and permits an ongoing login to finish.
These restrictions are scoped to Docker; the existing owner Pi is unchanged.

## Account deletion

Members can delete their own account from native Account or `/accounts`, after
confirming their Studio password. The web flow also asks for the username.
The operator account is protected. Both publication queues and manual processing
are checked before closure. Deletion revokes sessions/device grants, closes the
viewer, anonymizes the login and schedules deletion of that exact workspace's
media, profiles and database volumes. Cleanup retries safely after a crash and
rechecks worker activity before removing volumes. Minimal anonymous replay and
billing tombstones remain. External social posts are not deleted by this action.
Capacity is not released until the worker cleanup finishes.

## Optional Apple/Google identity

`hosted/oauth.mjs` provides own-provider authorization code exchange, Google
PKCE, signed JWKS validation, nonce/audience/issuer checks, one-use state and
short-lived receipt redemption. Native callbacks use
`art.lazying.lazyedit://auth` with a proof-bound opaque receipt, never a session
in the URL. New users still require an invitation and Studio account. Existing
accounts link a provider only after confirming their Studio password. Email or
display names never claim an existing owner identity. Unlink/revocation and
account deletion are supported.

Provider buttons depend on the operator's own configured client IDs, redirect
URLs and protected keys. Google browser linking, fresh sign-in and revocation
have been verified for the pilot. Apple registration is prepared; real Apple
Account authentication and native provider UI qualification remain pending.
See [identity operations](studio/identity-operations.md) for the exact boundaries.

## Private music packages

The hosted `/api/music/package` endpoint accepts asset files only from the
signed-in member's private media directory. It checks both the requested path
and the resolved filesystem path; sibling directories, parent traversal and
symlinks to runtime files are rejected before reaching the package builder.
This applies to audio, covers, proof, lyrics, metadata and screenshot aliases.
Upload assets into the workspace first. Hosted requests cannot override the
publisher URL; packages use that worker's configured publication service.
The existing owner's local CLI and Pi workflow retain their established behavior.
Editing-only hosted accounts can prepare a music package with explicit
`post:false`; a music post is rejected before asset processing or dispatch.

The regression uses harmless fixtures, authenticates a real isolated cell and
verifies that rejected requests never reach its fake package backend. It does
not read production credentials or create an external publication.

## Pricing and purchase readiness

Requested paid download price: USD 0.99 on Apple and Google; store schedules
were saved/read back separately. Approved monthly plans: USD 2.99, 14.99 and
29.90. The owner explicitly selected 29.90 after Apple's list lacked 29.89.
All three USA Apple draft price schedules have been saved and read back.

Native StoreKit 2 and Google Play Billing are prepared. The backend uses the
Apple App Store Server Library and Google subscriptionsv2, exact own product
IDs, account-token binding, canonical provider verification, acknowledgement,
refund/out-of-order/replay protection and encrypted proof storage. Clients
cannot grant themselves an entitlement. Purchases remain disabled until plan
store products and sandbox checks are verified. Hosted source-minute limits
are now enforced: 10/60/150 minutes per UTC calendar month. While charging is
disabled, invited pilot members receive 10 minutes and the administrator is
exempt. Finished renders can be reused without another processing charge.
See [processing and billing](studio/2026-10-04-processing-and-billing.md).
Paid-download subscription credit is not implemented yet.

There is no promise of open unlimited signup or unrestricted public compute.
Current capacity is a controlled three-workspace pilot including the operator;
each worker uses two CPU cores and eight GiB RAM. Billing, hard storage quotas,
account recovery and a global GPU scheduler are not active.

## Upgrade and qualification

1. Build exact `workspace`, `gateway` and `provisioner` images from
   `deploy/hosted/Dockerfile`, retaining the current and previous images.
2. `scripts/studio/promote_cells.py --state PRIVATE_STATE --tag EXACT_TAG`
   selects ready accounts from the registry, checks both queues and manual
   processing, backs up config, preserves volumes,
   rolls only private workers, then gateway/provisioner. Never run `down -v` for
   an upgrade. That operation is only for confirmed member deletion.
   Deleted-account Compose receipts are skipped; pending provisioning, failed
   workers and unfinished deletion must be resolved before promotion.
3. `scripts/studio/promote_hosted.py --state PRIVATE_STATE --admin-user lachlanchen`
   stages immutable ingress; reload/restart only the two Studio ingress units.
   It does not restart owner backend, Pi, AutoPubMonitor or LazyTunnel.
4. Run hosted/Studio contract tests, actual mobile desktop tests and isolated
   account lifecycle checks. Native UI QA must be labeled simulator/emulator or
   physical accurately. Do not test account deletion against the operator or
   permanent reviewer account.
5. Build signed native candidates once per source revision, verify exact hash
   and bundle identity, qualify, then upload to TestFlight/internal testing.
   Formal review and public availability are separate states.

Release facts are recorded in `store/studio/release.json`; protected receipts,
credentials, screenshots and runtime ownership belong outside Git. No OAuth,
store review or publisher login secrets belong in a README or command line.

October 4 continuation: [store submission and reviewer evidence](studio/2026-10-04-store-submission-and-lightmind-reviewer.md).
Studio Android6 and LightMind Android54 are in Google review. Studio iOS9 was
submitted at 11:18 HKT, after the privacy questionnaire was published in the
renewed existing browser. Console/API confirm `WAITING_FOR_REVIEW`; the same
build9 and draft were reused, with one item and one submission. An optional-font fallback
was deployed to static editor assets without replacing either worker or the
reviewer's completed operation. Preserve this accepted runtime through review;
the general source promotion procedure above is not authorization to restart it.

Primary references:
- [Google OpenID Connect](https://developers.google.com/identity/openid-connect/openid-connect)
- [Apple token revocation](https://developer.apple.com/documentation/signinwithapplerestapi/revoke-tokens)
- [Google Play Billing integration](https://developer.android.com/google/play/billing/integrate)
- [Google subscription verification](https://developers.google.com/android-publisher/api-ref/rest/v3/purchases.subscriptionsv2/get)
- [Apple App Store Server Library](https://developer.apple.com/documentation/AppStoreServerAPI/simplifying-your-implementation-by-using-the-app-store-server-library)
