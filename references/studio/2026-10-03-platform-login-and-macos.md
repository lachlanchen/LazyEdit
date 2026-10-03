# Private platform login, mobile bandwidth and native Mac Studio

## Login loading fix

The private desktop's old noVNC page imported dozens of JavaScript modules at
once. Its burst exceeded the separate Studio LazyEdge request limit, so it
could show a noVNC title forever without a canvas. The replacement bundles the
locked noVNC client once with esbuild. The private page loads one script and one
authenticated WebSocket; the shared ingress limit remains unchanged.

The login page has explicit 45-second browser-start and 20-second desktop-connect
timeouts, useful errors and a manual Reconnect button. It never opens an endless
retry loop. The browser profile belongs only to that workspace. Platform opening
uses the publisher's existing queue and browser-control lock, so it cannot
navigate away from an active publication or create another profile.

Only the observed Chromium page/window is activated and fitted to the desktop.
`websocket-client` has no context-manager protocol; use `contextlib.closing` to
close its bounded CDP operation even on errors. This adapter is Docker-only;
owner Pi startup, profiles, login waits and runtime remain unchanged.

## Bandwidth and phone interaction

- A workspace allows one live desktop viewer. Half-closed WebSocket peers release
  their lease on EOF, so a disconnected phone can reconnect. Authenticated and
  same-origin checks still apply at every layer.
- The viewer requests compression level 8, quality 6 and scales the existing
  desktop; it doesn't resize the server or start a second desktop.
- Leaving/hiding the page pauses streaming. Five minutes without input also
  pauses it. Login/profile data stays saved. Reconnection is explicit.
- **Keep QR visible** snapshots the current framebuffer in browser memory and
  disconnects the live stream. Tap its QR area to enlarge a square local crop;
  tap again to restore. Cropping sends no network request, stores no server
  image and does not claim automatic QR recognition. Reconnect if the QR expires.
- Phone keyboard/clipboard controls send text through the authenticated desktop.
  Password input clears after sending; no new clipboard REST endpoint is exposed.

Live Shipinhao and Douyin views were checked in the private reviewer workspace.
The new Shipinhao page needed two resource loads; a frozen, locally enlarged QR
was decoded in QA at a phone viewport. Full-window fitting reached 1439×999 on
its 1440×1000 desktop. No real social post was sent for these tests.

These requests use Studio's independent reverse tunnel and authentication, not
the owner's personal LazyTunnel device registry. There is no enrollment of a
Docker worker or Pi in that fleet. Caddy/gateway/local guard remain separate.

## Preparation status

The async backend now reports bounded live preparation progress instead of
showing Idle while speech/caption work is running. The same video/run cannot
start duplicate preparation in one backend process. Completed progress does
not override newer artifact status; exceptions leave a generic error state.
This transient tracker does not promise restart/resume or replace persistent
publication queues. Two tracker tests plus 21 account/transport tests pass,
including single-viewer denial and EOF cleanup. A reviewer-owned harmless clip
completed actual transcription/correction, translation, rendering, all three
metadata languages and cover. Cold CPU model download/processing took about
16 minutes; subsequent caches are reused. No production speed claim is made.

## Native Mac build

`mobile/ios` supplies native SwiftUI/UIKit screens to both iOS and Mac Catalyst;
only advanced editing and platform login use secondary authenticated web views.
The now-unused Capacitor binary dependency was removed from the native target:
its XCFramework has no Mac Catalyst slice. The PWA and Android remain separate.
Navigation/share/context controls have availability fallbacks for Monterey.

On the existing build Mac, sync that source into `~/Projects/LazyEditStudio/ios`
and run `scripts/studio/build_macos.sh` there. It creates the universal Intel /
Apple Silicon build, verifies identity/build/signature/architectures, and ZIPs
it once. macOS minimum is 12.0; iOS's normal minimum stays 16.0. The local Mac
package is ad-hoc signed for owner QA, not notarized or submitted to a store.
Never disable Gatekeeper/TCC globally to install/test it.

See `store/studio/release.json` for qualified mobile provider states and the Mac
artifact digest. Exact device results and any limits are added below after QA.

The first Mac build crashed on Intel Monterey because it strongly linked the
new SwiftUICore framework. The Mac-only linker option
`-weak_framework SwiftUICore` fixed that dependency without changing iOS
linking. The corrected universal build launched on the 3040 Mac (macOS 12.7.6).
The preceding build had already launched on the 7050 iMac and Apple Silicon Mac
mini; signatures and both architectures were verified. KVM built the packages.
Mac XCTest compiled, but its UI runner was blocked by macOS automation/TCC.
These are build/signature/launch checks, not a claim of complete four-machine
UI automation. Never disable TCC or Gatekeeper to manufacture a passing result.

The subsequent browser-policy conflict and 11-language work are documented in
[the 2026-10-04 qualification note](2026-10-04-workspace-login-and-localization.md).
