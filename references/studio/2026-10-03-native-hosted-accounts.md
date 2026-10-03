# Native Studio, invitations and publication endpoints

LazyEdit uses the same authenticated `https://edit.lazying.art` service from
the PWA, native SwiftUI iOS app and native Android app. The existing owner
endpoint and the new invite-only Docker workspaces remain separate. Media is
stored locally; the cloud edge streams requests through the existing LazyEdge
chain. It does not hold videos or run publication browsers.

## Administrator and invited users

The explicitly configured `lachlanchen` account is the administrator. Its
existing password remains valid. Other users register with a single-use,
72-hour invitation and choose **Private workspace** at native sign-in. They
cannot create invitations or access the original Pi endpoint.

In **Account**, the administrator can:

- Create an invitation and copy it or use the native share sheet.
- Switch to the private Docker workspace, using its own library, settings,
  database, platform profiles and serial publication queue.
- Switch back to the existing Pi workspace and original library/queue.

The Docker workspace is created once, within the operator's capacity limit.
Repeated mode-switch requests do not create another workspace. Creating it
does not migrate or copy the owner's media, platform cookies or Pi profiles.
Sign into the desired platforms in **Platform accounts** and configure that
workspace's logo before using those features for real publication. Switching
is refused while a local upload is unfinished. Existing queued tasks continue
in the workspace where they were submitted.

The web account portal at `/accounts` provides the same administrator actions.
An invitation link prefills the registration code, removes it from the address
bar and uses `no-referrer`/`no-store` responses. Keep these links private.

## Native interfaces

iOS uses SwiftUI navigation, lists/swipe removal, Photos/Files selection,
AVPlayer preview, preparation/review forms, publication activity and Account.
The login session is stored in Keychain, not as a saved password. Android's
launcher activity uses native Android views, a system document picker,
VideoView preview, native preparation/review dialogs, activity and Account.
Its session file is encrypted using an Android Keystore key. Android no longer
launches a Capacitor WebView as its primary interface.

Both apps use HTTPS JSON requests to the same reviewed Studio API. The advanced
web editor and the platform login desktop remain secondary authenticated web
screens. They expose the existing detailed subtitle/metadata/music controls;
they do not replace the native library, upload, review or account interface.
The PWA remains available and is not removed by a mobile release. Preserve
native source when syncing Capacitor assets; do not regenerate either launcher.

Library caches, staged uploads, publish drafts and uncertain-submit receipts
are scoped by account **and** workspace mode. Old requests cannot populate a
new workspace's library. Mode switching clears visible media and thumbnails.
Native uploads resume from the server's acknowledged offset; Android retains
a URI permission instead of creating a second local video. iOS retains the
one staged copy required for Photos/Files access until upload completion.
Native publication persists its idempotency key before sending and reconciles
an uncertain submission before offering to retry the same request.

Use the configured logo, correction context and language order supplied by the
workspace. Context is a reference for likely recognition errors, not a mandate
to replace actual speech with a script. Metadata describes the video/song,
not internal workflow details. The usual pronunciation/grammar rendering and
finished-run reuse remain in the mature LazyEdit pipeline.

## Operator setup and trust boundaries

For an existing owner, link the **existing salted password hash and identity**
from the owner database; no plaintext password is needed and that database is
opened read-only:

```bash
node hosted/admin.mjs link-owner \
  "$HOME/.local/share/lazyedit-hosted" lachlanchen \
  "$HOME/.config/lazyedit-studio/accounts.sqlite"
python scripts/studio/promote_hosted.py \
  --state "$HOME/.local/share/lazyedit-hosted" --admin-user lachlanchen
```

The promoter stages immutable code and rollback files; follow its existing
activation instructions. Build/update the gateway and provisioner images for
the new registry/account implementation. Do not restart the owner backend,
Pi publisher or shared tunnel to apply an account adapter update.

The ingress authenticates the original owner cookie before adding its internal
administrator identity. Public identity headers are stripped. The gateway
accepts that identity only behind its separate ingress capability. A Docker
session takes precedence over an owner cookie; guests cannot use this as a
fallback to the owner. Same-origin POST checks apply to invitations and mode
switches. Switching back revokes the central Docker browser session and issues
an original-owner session. Sign-out revokes the selected session and clears
both cookie names. The gateway has no Docker socket; the private controller
uses fixed provisioning templates.

Browser/native routing cookies are distinct from scoped API tokens. External
tools use the `apiBase` returned by `/accounts/account`, including the explicit
`/workspaces/<id>` prefix for Docker token calls. Never use the original owner
API base as the default for an invited user's CLI.

## Qualification and practical limits

Run the account/transport checks with:

```bash
node --test hosted/test.mjs studio/*.test.mjs
```

They cover invitation expiry/reuse, member denial, forged headers, foreign
Origins, idempotent workspace creation, return-to-owner identity, session
revocation, data isolation and authenticated desktop transport. Mobile UI tests
must use a dedicated simulator/emulator and temporary private credentials.
They create invitations and upload a tiny synthetic fixture; they never press
Prepare/Publish or send a social post. Store release status and exact hashes
belong in `store/studio/release.json`; see [mobile testing](mobile-testing.md).
An archive, an uploaded build, a provider-ready beta and a physical installation
are distinct observations.

This remains a trusted invite-only pilot: CPU processing, three workspaces by
default (including the administrator's private workspace), no public signup,
billing, password recovery, storage quotas or global GPU scheduler. Container
and shared-origin limits are documented in the [Docker guide](../2026-10-03-hosted-multiuser-docker.md).
Platform authentication may expire or require QR/verification; Docker does not
remove that requirement. The existing long login wait remains unchanged.

## Test runner lessons

A transient edge connection timeout initially failed simulator login. Check the
public route and repeat the same no-post QA after connectivity recovers; do not
change TLS, manufacture a successful login or upload an unqualified binary.
Both iOS UI scenarios subsequently passed against the live service.

For Android, build `:app:assembleDebugAndroidTest` rather than the unqualified
aggregate task: unrelated Capacitor plugin test modules have their own duplicate
class conflicts and are not the native launcher under test. Launch the exact
application ComponentName from instrumentation; relying on the class overload
can select the test APK's package. Deliver test credentials through stdin to
`run-as` on the dedicated emulator, never in command arguments or Git.

The installed Android 16.1 emulator image repeatedly crashed in SurfaceFlinger
region sampling with the old indirect SwiftShader mode, restarting system
services and causing package/instrumentation broken pipes. Preserve that crash
evidence, stop only the dedicated emulator, and qualify the app on an existing
stable Android 14 image with direct SwiftShader. This is emulator QA, not a
physical-device or latest-OS compatibility receipt. The native library renders
20 rows per page to keep the existing owner's large library responsive.

On the dedicated Android 14 emulator, the emulated Bluetooth service also
crashed and left a modal error over the app. Disable only that test emulator's
Bluetooth package and dismiss the observed stale dialog; do not change shared
phones or the application to hide a system-service failure. Native network work
now visibly disables action/navigation buttons while a request runs, keeping
Pause usable during upload. The instrumentation waits for request completion,
checks login/invitations/both mode switches and session persistence, then logs
out and removes its private credentials. Both Android tests passed.
