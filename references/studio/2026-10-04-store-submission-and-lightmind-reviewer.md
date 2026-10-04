# Studio store submission and LightMind review access — 2026-10-04

## Confirmed outcomes

Google Play accepted **LazyEdit Studio 1.0 (6)** for production review at
**10:24 HKT / 02:24Z**. Publishing overview confirmed **10 changes sent for
review** and **Changes in review**. A separate production-track readback at
10:26 confirmed the exact release **in review**, targeting **173 countries /
regions**. This is the first release: full rollout after approval, managed
publishing off. Public availability is not yet verified.

The qualified existing internal bundle was reused through **Add from library**;
it was not rebuilt or uploaded again. Target SDK is 36, minimum API 24. Its SHA-256
is `1232df09acf819af759086600f4d8e92a7ea7f4a20e470df550f7e2b027184d3`.
The production Console's single release warning is the missing deobfuscation
map. Its dashboard also recommends edge-to-edge validation and R8 optimization;
these are follow-ups, not approval or new QA evidence.

**Apple iOS 1.0 build 9 was submitted for formal review at 11:18 HKT /
03:18:40.974Z.** Both the Console and official API confirm
**WAITING_FOR_REVIEW**, one review item and the exact attached build 9.
The same VALID signed IPA remains in internal TestFlight. Category, age declaration,
rights declaration, USD 0.99 pricing, reviewer login/contact/notes and four
verified screenshots are prepared. Availability is configured for 175
territories, including future territories; this does not imply regulatory
approval or public availability in those territories.

The earlier attempt to add the version to review failed with
`STATE_ERROR.APP_DATA_USAGES_REQUIRED`: published answers to app data collection
are required. The existing browser login expired. After the owner renewed it,
App Privacy was completed and published through the visible Console. The same
draft `38267310-a95e-435f-9008-1349611c9307` and version
`5097e8ff-f535-489b-b4c3-ef01561b8e9a` were reused. The documented API added
one version item; the Console showed **Item Ready to Submit / 1.0 (9)**.
**Submit for Review** was clicked once. The Console showed **1 Item Submitted**
and **Waiting for Review**; an independent API read confirmed the timestamp,
exact build attachment, one item and `WAITING_FOR_REVIEW`. Neither store's
submission is approval or public availability. No new binary was built/uploaded.

## Reviewer access and coordination

The isolated Studio account is an ordinary editing member, with upload,
subtitle/context configuration, preparation, cover/metadata and preview.
Publication is disabled for all ordinary members, including this reviewer.
There is no reviewer-only bypass and no owner Pi, media or social-account
fallback. The supplied account is already provisioned: it needs no invitation,
OTP, purchase or social login for ordinary editing features.

Credentials and exact client-link instructions are retained outside Git:

- `Nutstore Files/Share/LazyEdit/lightmind-reviewer-account.json` (0600).
- `Nutstore Files/Share/LazyEdit/LIGHTMIND-REVIEW-ACCESS-20261004.md` (0600).

The owner-authorized LightMind session consumed the handoff and submitted
**LightMind Agent 1.0.1 (54)** at **09:09 HKT**. Its automatic checks cleared at
09:12; Play confirms **In review**, 20% rollout, 178 countries. Its own tracked
report is `references/android-build54-submission-20261004.md`. No second
submission or acknowledgment loop is needed.

Its real-service native acceptance resumed the retained video 2 operation:
**1 passed, 48.154s**. Authenticated source/Range, rotating refresh, actual
rendered playback beyond 25%, visible frame, cover and metadata were verified.
No duplicate upload/preparation and no social post occurred. Preserve the
reviewer account, workspace, completed artifact and acceptance lock through
review; coordinate any later deployment or credential change first.

## Real startup bug fixed without worker replacement

The iPad native test exposed a WKWebView failure in the full editor: an optional
interface font timed out after 6000 ms, and `app/app/_layout.tsx` threw the font
error into the router error boundary. The editor could not open.

The root now warns generically, dismisses its splash screen and uses system
font fallback when optional font loading fails. The production native binary
is unchanged. The iOS test helper now recognizes adaptive iPad top tabs as well
as iPhone bottom tabs; this is a test-only adjustment.

The hosted web export was built from qualified base
`9fbe02bf1388ded26af1616cb4adbf025c23fe72` plus only that font fallback,
with `EXPO_PUBLIC_REMOTE_STUDIO=1` and `LAZYEDIT_REMOTE_STUDIO=1`. The original
`hosted/build-web.mjs` decoration was retained. The unrelated broader language
and durable-operation source updates were not promoted during acceptance.

The derived image is
`lazyedit-workspace:editor-first-20261004h-font-fallback`, digest
`sha256:44bf661ac09f9cb693afeb8b24075a3579d671f13a38592ea62425b61b77b93a`.
Its immutable bundle is `entry-71ccc91c98ad155dca24ea38be710a6b.js`.
Private provisioner configuration selects this image for future workspace
creation. Existing workers received static assets first and an atomic index
replacement; old bundles remain available for open pages. Neither worker was
restarted, and APIs, databases, media and operation identities were unchanged.

The initial root `chmod` failed because copied files belonged to the workspace
UID and the container drops `CAP_FOWNER`. The files were already world-readable;
no capability or permissions expansion was needed. Staging and atomic index
replacement succeeded without that redundant chmod. Rollback restores each
saved original index; do not remove old assets while a page may still use them.

After this patch, the same native iOS9 iPad test passed: **1 test, 108.870s**.
Reviewer source/render/cover hashes and authenticated Range remained correct,
all preparation stages were done, and the publication queue was empty. Worker
start times remained unchanged. The dedicated iPad simulator and Android
emulator were stopped and the copied test credential was removed from the Mac.
These are simulator/emulator checks, not physical-device installation claims.

## Listings, screenshots and data declarations

Listings describe editing first and disclose invite-only membership, bounded
processing, private workspaces and optional operator-enabled publication. The
app download is USD 0.99. Monthly products remain inactive drafts; neither
subscription purchases nor paid-download subscription credits are offered in
this pilot.

Google received the existing approved icon, its matching feature graphic and
four genuine native Android screenshots (library, upload, editor and account).
Only the icon and feature graphic were labeled as AI-created assets. The
screenshots were not AI-generated or altered to imply functionality. The
feature SVG must be rendered correctly: ImageMagick's output lost the gradient
and icon and was rejected locally. Chromium rendered the exact 1024×500 SVG
correctly; that checked result was uploaded.

Apple received two genuine iPhone screenshots and two genuine iPad screenshots
(library and account). All four assets reached `COMPLETE`, with matching MD5
source checksums. An immediate `UPLOAD_COMPLETE` response is asynchronous and
is not final acceptance. `scripts/studio/app_store_screenshot.py` reuses an
existing named asset, rejects conflicting checksums, validates upload origins
and byte ranges, never forwards an API token/cookie to an upload target, redacts
signed-URL transfer errors and polls boundedly for final completion. Five
offline regressions pass; re-running against a completed Apple asset returned
the same asset ID and verified checksum without creating or uploading another.

Google's saved Data Safety form covers user identifiers, optional provider
email claims, uploaded photos/videos/audio/music/files/other content, processing
interactions and diagnostics. Diagnostics use Google's analytics definition
for technical diagnosis; there is no analytics/tracking SDK or advertising.
Media/context AI processing and explicitly chosen platform submission are
disclosed in the privacy policy. Do not misdescribe a service-provider or
user-initiated sharing exemption as meaning that no data leaves the server.
Account deletion is supported; hiding an item is not partial data deletion.

Apple's published responses declare eight retained data types: Photos or
Videos, Audio Data, Other User Content, Browsing History, User ID, Product
Interaction, Performance Data and Other Diagnostic Data. Each is used for
**App Functionality**, linked to the account and **not used for tracking**.
The audit covered the account registry, private media/context and operation
ledgers, connection/error logs and the optional operator platform-browser
profile. Browsing History includes navigation retained in that private browser
profile; ordinary members still have no unrestricted browser or owner access.
Account-linked diagnostics are not described as anonymous. Optional OAuth
email/name claims are used for immediate verification and are not persisted
in Studio's identity-link registry; provider subject IDs are declared as User ID.
Inactive purchases and absent advertising/device-ID/location collection were
not declared as active features. Apple explicitly includes server uptime,
security and performance in App Functionality; Google's technical-diagnosis
Analytics label was not mechanically copied into Apple's questionnaire.

The reviewer login was saved and verified in both providers' private review
fields, not in a public listing. It does not certify access to the separately
restricted operator publication integration. Google target audience is 18+;
the questionnaire's computed content rating is a distinct provider result.

## Continuation and evidence

Current release facts: `store/studio/release.json`. Private receipts, actual
native screenshots, screenshot delivery checks, web promotion/rollback hashes
and provider readbacks: `temp/store-submission-20261004/`, mirrored selectively
to the protected Nutstore runtime directory. Do not commit keys, passwords,
cookies, browser profiles, raw session histories or media packages.

Monitor the existing Google and Apple reviews; do not create another release,
submit the same changes again or replace a pending binary. Preserve the ordinary
reviewer worker during store acceptance. Both worker start times remained
unchanged and health checks passed after the Apple submission.

The reusable `store-login-session` skill is installed in
`~/.codex/skills/store-login-session/` and mirrored in the canonical
`/home/lachlan/ProjectsLFS/LazySkills/skills/store-login-session/` inventory.
It tries the existing remembered account and observed Continue transitions
before asking for reauthentication. ASC, Developer Portal and Sign in with
Apple OAuth are separate authentication scopes. The owner's common two-click
recovery is documented as a strategy, not an untested guarantee or a blind
double-click. The existing user-requested store desktop remains at
`http://127.0.0.1:6165/vnc.html?autoconnect=1&resize=scale`, local CDP `9497`,
with its persistent Chrome profile. No cookies were reset, new desktop created,
or recurring login/keepalive traffic scheduled. Provider-required fresh 2FA
can still need the owner; session persistence is not permanent authentication.

The October 4 continuation's protected receipts are
`apple-privacy-published-dom.json`, `apple-review-item-after-privacy.json`,
`apple-submit-ui.json` and `apple-formal-submitted.json`. Privacy and submission
screenshots are saved beside them. No private account/password appears in these
public notes or the skill.

Primary provider references:

- [Apple app privacy workflow](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/)
- [Apple submission workflow](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/)
- [Apple asset upload API](https://developer.apple.com/documentation/appstoreconnectapi/uploading-assets-to-app-store-connect)
- [Google Data Safety definitions](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en)
- [Google reviewer access requirements](https://support.google.com/googleplay/android-developer/answer/15748846?hl=en-EN)
