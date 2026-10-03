# Private Studio release follow-through — 2026-10-04

## Completed service work

The invite-only service at `https://edit.lazying.art` uses the existing isolated
LazyEdge route and local storage. The original backend and Pi are preserved.
Only `lachlanchen` can select the Pi; invited users have private Docker media,
database, settings and publication profiles. The native administrator can
create invitations and switch workspace modes. New accounts get the authorized
Vancouver demo, with no owner library or social credentials.

The hosted pilot has three workspace slots including the administrator. Both
permanent cells, gateway and provisioner now run `editor-first-20261004h`, built
from source `9fbe02b`. Native binaries in testing remain build 8 / Android 5
until the next exact release is qualified and uploaded. The promotion
checked publication queues and manual processing, preserved volumes and saved
a private rollback. The h promotion did not restart ingress units. The owner
backend process, original Pi and shared LazyTunnel services were not restarted.

Live acceptance verified scoped demo access, member denial of Pi/invitation
access, disposable-member provisioning, immediate grant revocation on deletion
and removal of only that member's worker. Capacity returned after cleanup.
The two permanent cells stayed healthy. Thirty-eight Node contract tests pass,
plus three focused Python upgrade/readiness tests.

Before the final promotion, the gateway was independently updated to
`native-oauth-20261004a` from source `66e8a7d` for identity qualification. The
current h images include that implementation. Configured provider keys and
identity encryption remain external and were preserved during promotion.

The final live check authenticated both administrator and reviewer workspaces,
verified publication enabled for the administrator and disabled for members,
rejected forged grants, video/music posts and platform-desktop requests,
verified their own demo library, forwarded a valid private asset to the package
handler's required-field check, and rejected outside music assets and publisher
overrides. Billing stayed disabled; member Pi/invitation access remained denied.
No music package or external post was created by these checks. The upgrade
helper now selects ready registry accounts instead of replaying retained
deleted-member Compose receipts. See the [isolation incident](../../bug-reports/2026-10-04-hosted-music-asset-isolation.md).

## Platform login desktop

One bounded viewer reuses each workspace's desktop. QR freezing stops the
stream and displays a still image. Zoom, clipped pointer input and inactivity
pause reduce mobile bandwidth. Close browser preserves its platform profile,
leaves a restricted blank desktop, and refuses closure during publication.
Browser navigation policies and desktop shortcut restrictions preserve private
CDP file upload. A live reviewer desktop closed/reopened successfully; frozen
QR mode had no canvas stream. General browser/file/developer shortcuts did not
open another usable window. Real authentication on every platform is not claimed.

## Native and store state

Native iOS and Android library, upload, publication configuration, activity and
account screens include 11 languages. The detailed editor/login view uses the
authenticated existing web UI. Native UI is not replaced by an embedded whole
PWA. Monthly purchases remain hidden while billing is disabled. Optional
provider buttons follow the configured pilot providers; native provider UI
qualification is separate from the completed Google browser tests.

- Apple: exact signed build **8**, IPA SHA-256
  `e8d2039dcaef8dcb2ff7bdbb084a22b988f33dafe8f789681530976bb24ad4e4`,
  validated and uploaded once; processed `VALID` and attached to the existing
  internal group as `IN_BETA_TESTING`.
- Google: exact signed AAB **6**, SHA-256
  `1232df09acf819af759086600f4d8e92a7ea7f4a20e470df550f7e2b027184d3`,
  saved/published once and read back **Available to internal testers**. Two
  targeted instrumentation tests passed on the dedicated Android 14 emulator: member
  authentication/capabilities and trusted-origin checks. This is
  not a physical-device installation claim.
- Paid download: USD **0.99** was configured/read back on both stores.
- macOS: exact universal Catalyst build **8** launched on Intel Monterey 3040,
  iMac 7050 and the ARM Mac mini. Strict ad-hoc QA signatures and both
  architectures were verified; this is not a notarized public installer or a
  full Mac UI regression claim.
- Apple English name/subtitle/description/support/privacy/copyright were saved
  in the existing editable 1.0 record. Google saved the privacy URL and truthful
  no-ads, no-advertising-ID, non-government, no-financial-features and
  no-health-features declarations. Its content questionnaire was completed as
  an editing utility with a remote demo; Google returned Everyone/PEGI 3.
  Target audience, data safety and reviewer sign-in access remain separate
  declarations and do not become complete from that rating alone.
- Public review is not submitted. The ordinary editing-only member and
  reviewer have the same upload/edit/process/preview capabilities and need no
  social credentials. Listings disclose the separate operator-enabled publishing
  integration. Do not certify access to every publication feature from editing
  QA alone, and never share owner platform credentials.

## Repeatable qualification

Use `scripts/studio/test_ios.sh` on the existing Mac with a dedicated simulator
and protected QA credential file. Supply `STUDIO_TEST_SIMULATOR`,
`STUDIO_TEST_CREDENTIALS` and a new `STUDIO_TEST_RECEIPT`. Preserve old receipts.
The helper delegates simulated entitlements and ad-hoc signing to Xcode. A
simulator built without app identity cannot save a Keychain session (-34018).
Manually signing the finished simulator bundle with device entitlements makes
AMFI reject it. Neither case justifies weakening app credential storage or
changing system trust. XCTest also must handle the system Save Password dialog,
retained login fields and observed Liquid Glass tab frames.

The completed member XCTest also waited for the editor module to hydrate,
opened the private Shipinhao desktop inside WKWebView, observed its connected
state, froze the QR view and closed the browser with its profile retained.
This qualifies native desktop transport, not authentication or posting to a
real social account. The dedicated simulators/emulator and project review
desktop were stopped after evidence capture.

`scripts/studio/install_macos_review.sh ZIP BUILD SHA256` verifies the exact
artifact, bundle ID, build, strict signature and both architectures before
replacing this project's running review app. Use `lipo -archs` for compatibility
with both older and newer LLVM tools. A freshly extracted bundle on the Mac
mini initially failed `open` with error -10699 while its executable and window
worked. Registering that exact bundle with `lsregister -f` allowed normal
`open` to succeed. The installer now registers only the new Studio bundle; it
does not reset the shared Launch Services database or weaken Gatekeeper/TCC.

For Android QA, build only the application's test target:
`:app:assembleDebug :app:assembleDebugAndroidTest`. The generic root
`assembleDebugAndroidTest` additionally builds an unused Cordova module's test
target and can fail on its legacy Kotlin test dependencies, even when the app
test APK was produced. Keep test-only dependencies out of the release app.

`scripts/studio/store_listing.py status|prepare` reads or updates only this
app's existing editable Apple 1.0 record. It validates bundle identity, refuses
ambiguous/non-editable versions and does not submit review. Store text is in
`store/studio/listing.json`; reviewer passwords remain external.

## Remaining provider work

Google's own web client was registered and configured privately. Real browser
linking and sign-out/sign-in returned to the correct Studio account. A second
link obtained an encrypted revocation credential; unlinking successfully
revoked the Google grant, removed the Studio link, and a subsequent Google
sign-in was refused because it was no longer linked. Ordinary sign-in requests
no offline access or repeated consent; password-confirmed linking does. The
Google project remains External/Testing with only `openid email` scopes and no
billing. This is not brand verification or native OAuth UI qualification.

Apple's own native primary App ID, web Services ID, exact HTTPS callback and
Sign in with Apple key were configured. Its real OAuth page still needs Apple
Account authentication; successful real linking/revocation is not yet claimed.
The newly enabled capability invalidated this app's old distribution profile.
A new profile using the existing distribution certificate was generated and
verified on the Mac. `build_ios.sh` now reads and validates the private profile's
app ID/team/name/UUID and updates temporary export options; it no longer
hard-codes the invalidated profile. The already uploaded build 8 is unchanged.

Both provider configuration helpers default to disabled, require protected
files, preserve the existing identity encryption key and other provider, save
rollback files and never restart services. Apple's helper rejects a different
primary App ID before mutation. See [identity operations](identity-operations.md).

The owner approved monthly USD **2.99/14.99/29.90** with conservative
**10/60/150 source-video minutes per UTC calendar month**. The hosted meter is
live; browser and linked-app requests use trusted allowances and a private
atomic ledger. Live member/admin allowance and forged-header checks pass.
Finished-run reuse consumes no new processing time. Store purchase/restore/
refund checks remain pending. Paid-download subscription credit is not
implemented. Charging remains disabled.

`scripts/studio/store_products.py status|prepare|configure` reconciles only this
app's three own monthly Apple drafts. A separate readback verifies the exact
approved USA price schedules and monthly periods. The current Apple catalog
requires UPFRONT plan availability before saving a USA price; UPFRONT for a
ONE_MONTH product is ordinary monthly renewal, whereas its MONTHLY enum means
a 12-month instalment commitment. The helper hydrates price relationships for
readback and preserves any existing different schedule. Draft pricing is not
product approval or billing activation. See [the billing handoff](2026-10-04-processing-and-billing.md).

The authoritative boundaries and promotion/deletion workflow are in
[the account handoff](../2026-10-04-hosted-account-and-release-handoff.md).
`store/studio/release.json` contains verified artifact/provider facts. Private
receipts, current runtime ownership, rollback files and credentials are outside
Git. Public listing, public review, approval and availability are separate states.
