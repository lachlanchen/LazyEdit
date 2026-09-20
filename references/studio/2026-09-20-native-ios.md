# Native iOS Studio, build 3

## Scope

The iOS root is SwiftUI, replacing the always-on hosted Capacitor root. Login,
Studio library/search, upload, video detail/AVKit preview, Activity and Account
are native. Back gestures, tab state, Dynamic Type and platform controls come
from iOS. There is no web bundle download before these screens can render.

Advanced subtitle, metadata, cover, render and publication controls remain in
the existing authenticated Studio editor, opened explicitly as a sheet. This
preserves the mature publisher, settings and queue, instead of duplicating them
in a second implementation. It is a native client with an embedded advanced
editor, not a claim that every editing control has been rewritten in Swift.
Android stays at its independent existing build; its shared web error fix is
available without a package update.

## Implementation

- `mobile/ios/App/App/SceneDelegate.swift`: SwiftUI root.
- `StudioAPI.swift`: owner HTTPS authentication, Keychain session, same-origin
  API validation, structured error decoding, four concurrent reads, bounded
  transient GET retries and no automatic mutation replay. All API redirects
  are refused so credentials/mutations cannot follow an unexpected target.
- `StudioStore.swift`: cached library, thumbnail cache, persistent staged video
  and upload ID, server-confirmed offsets, receipt reconciliation, queue reads.
- `StudioViews.swift`: native screens, Photos/Files system pickers, AVKit player,
  embedded WKWebView editor. Videos start loading only when Preview is tapped.
- `app/app/(tabs)/editor.tsx`: `?videoId=ID` selects the exact requested video.
  A missing ID never silently falls back to a different video. Opening the
  editor is not a request to process or publish.
- `figs/app-icon/`: source artwork/prompt for the new forest-teal ribbon icon.
  `scripts/studio/build_icons.py` derives opaque iOS icons. The configured
  burned video watermark is unchanged.

## Session and upload behavior

The native client uses the existing owner's password login and 12-hour browser
session, so the owner's full existing library remains visible. Only the opaque
session and its expiry/username are saved in Keychain, marked
AfterFirstUnlockThisDeviceOnly. Passwords are not saved. No new signup, scope
escalation, anonymous upload or account-sharing mechanism is introduced.
LightMind's separately scoped tokens and consent remain unchanged.

Photos/Files import copies the selected original to Application Support, which
is excluded from backup. Uploads send 8 MiB chunks through the existing
`/v1/studio/uploads`, `upload`, `upload-part`, `upload-complete` endpoints.
Pause/relaunch retains the local copy and upload ID. Resume reads the server's
offset before sending; after an uncertain finalize it checks the receipt first.
Completed/discarded copies are removed locally. Discard does not delete the
original or an imported server video; incomplete server allocations expire.

iOS may suspend the app. A short background task allows the active chunk to
finish; this is not an unlimited background-transfer promise. Keep the app open
for long uploads. An expired server allocation is reported and an explicit
Resume starts another allocation. The server's maximum is 10 GiB.

The advanced editor receives the secure HttpOnly cookie in a nonpersistent
WKWebView cookie store. Only the configured HTTPS Studio origin is allowed for
in-app navigation; explicitly tapped external HTTPS links open outside it.
The app does not weaken TLS or change gateway concurrency limits.

## QA and release

Run `node --test studio/session.test.mjs studio/test.mjs` for structured gateway
errors, request concurrency, no mutation replay, loading transitions, auth,
CSRF, ownership and server publication idempotency.

`StudioNative` is the shared Xcode simulator test scheme. Its UI test exercises
owner login, all native tabs, Keychain relaunch, a small Photos upload, preview,
and opening/closing the existing editor. It never presses a process/publish
button. Tests require a dedicated simulator with only a known tiny test video
in Photos. Supply `STUDIO_TEST_CREDENTIALS` pointing to the owner's protected
JSON in the **test runner** environment of the generated `.xctestrun`; do not
embed credentials in targets, source, launch arguments or test fixtures. An
unconfigured test is skipped, which is not a successful functional QA receipt.
Keep `.xcresult`, screenshots, logs and credentials private; XCUITest input logs
can contain sensitive account data. Do not run this test on a personal phone.

Use the existing Mac, SDK, provisioning profile and private release keychain.
Do not reset another project's simulator or change the global Xcode selection.
Build a signed archive only after native checks pass. `build_ios.sh` defaults
to build 3; verify the archive's bundle/version before validating/uploading.
Attach only the exact Apple VALID build to the existing owner-only internal
TestFlight group. Record actual provider state in `store/studio/release.json`.
Simulator checks are not physical-iPhone or installed-from-TestFlight evidence.

See also [React crash fix](2026-09-20-ios-react31.md) and
[store operations](mobile-testing.md).

## Verified in this change

- Ten Node regression/transport checks pass. Production browser reproduction
  injected 21 structured HTTP 429 responses without a React crash; status
  recovered after removing the injection. The loading screen appeared during
  a real cold bundle load and disappeared after React mounted.
- Production editor deep link selected video 572; an unavailable numeric ID
  made no process-status requests and left Publish disabled. No publish action
  was clicked.
- Signed simulator UI test passed, one test, zero skips/failures, 96.7 seconds:
  all tabs, saved Keychain session, Photos selection, persistence after process
  relaunch, server upload and opening/closing the authenticated editor. The
  tiny generated test clip became server video 576, then was removed from the
  Studio list after confirming no publication job referenced it.
- Unsigned simulator builds cannot validate Keychain: use ad-hoc simulator
  signing (`CODE_SIGNING_ALLOWED=YES CODE_SIGN_IDENTITY=-`). Do not implement an
  insecure credential-storage fallback just to accommodate an unsigned test.
- The iOS 26 Photos picker exposes assets as accessible Images, not collection
  cells. The test selects the known three-second fixture by its observed label.
- The KVM simulator has incomplete rendering of system Liquid Glass surfaces
  and sometimes invalid suggested accessibility hit points. Element-frame
  taps verified tab behavior; this is a simulator QA workaround, not app code.
  A separate authenticated AVFoundation check on the Mac confirmed the existing
  test media is playable (2.0 seconds, one video track) with the same cookie
  option used by the app. Physical TestFlight review is still needed for final
  system-bar appearance and playback quality; simulator screenshots alone are
  not proof of physical-device playback.
- Native archive uses the shared `StudioNative` scheme. Creating that explicit
  scheme suppresses the old autogenerated `App` scheme; release scripts must
  use the committed name.
