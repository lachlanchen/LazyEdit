# Private Studio release follow-through — 2026-10-04

## Completed service work

The invite-only service at `https://edit.lazying.art` uses the existing isolated
LazyEdge route and local storage. The original backend and Pi are preserved.
Only `lachlanchen` can select the Pi; invited users have private Docker media,
database, settings and publication profiles. The native administrator can
create invitations and switch workspace modes. New accounts get the authorized
Vancouver demo, with no owner library or social credentials.

The hosted pilot has three workspace slots including the administrator. Both
permanent cells, gateway and provisioner now run `native-login-20261004f`, built
from hosted music-isolation source `27fbae0`. Native binaries remain from
account-lifecycle/native-sign-in source `256a9ac`. The promotion
checked publication queues and manual processing, preserved volumes and saved
a private rollback. Only Studio's ingress units were reloaded. The owner
backend process, original Pi and shared LazyTunnel services were not restarted.

Live acceptance verified scoped demo access, member denial of Pi/invitation
access, disposable-member provisioning, immediate grant revocation on deletion
and removal of only that member's worker. Capacity returned after cleanup.
The two permanent cells stayed healthy. Thirty-two Node contract tests pass,
plus two focused Python upgrade tests.

Before the final promotion, the gateway was independently updated to
`native-oauth-20261004a` from source `66e8a7d` for identity qualification. The
current f images include that implementation. Configured provider keys and
identity encryption remain external and were preserved during promotion.

The final live check authenticated both administrator and reviewer workspaces,
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
- Google: exact signed AAB **5**, SHA-256
  `f6b0d9d1f2efc159ebbfc6b0d9be4b9b4ebc9d0a0a4a37b478e61fe367f2b26f`,
  saved/published once and read back **Available to internal testers**. Two
  instrumentation tests passed on the dedicated Android 14 emulator. This is
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
- Public review is not submitted. Google's full-access certification requires
  separate social test-account access. The private reviewer can upload, edit,
  process and configure publication, but has no connected social channels.
  Do not certify complete publication access or share owner platform credentials.

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

Monthly USD 2.99/14.99/29.89 plans need
defined benefits, enforced usage limits, exact store products and sandbox
purchase/refund tests. Paid-download subscription credit is not implemented.
Keep charging disabled until those steps succeed.

`scripts/studio/store_products.py status|prepare` reconciles only this app's
three own monthly Apple drafts. Preparation created them once, and a separate
readback verified the product IDs and monthly periods without creating another
group. All remain `MISSING_METADATA`; no price schedule, subscription offer or
review submission was changed. Apple's actual USA price list supports USD 2.99
and 14.99, but not 29.89. Its nearest alternatives are 29.90, 29.95 and 29.99.
The requested 29.89 remains unchanged pending the owner's choice; no alternative
price was silently substituted.

The authoritative boundaries and promotion/deletion workflow are in
[the account handoff](../2026-10-04-hosted-account-and-release-handoff.md).
`store/studio/release.json` contains verified artifact/provider facts. Private
receipts, current runtime ownership, rollback files and credentials are outside
Git. Public listing, public review, approval and availability are separate states.
