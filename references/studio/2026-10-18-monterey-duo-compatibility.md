# Apple compatibility qualification

LazyEdit Studio uses a native SwiftUI / Mac Catalyst target (`StudioNative`,
`art.lazying.lazyedit`). Its iPhone/iPad minimum remains iOS 16. Mac Catalyst
uses the iOS 15 API baseline for macOS Monterey 12.0 and includes Intel x86_64
and Apple Silicon arm64.

## Build defaults and verification

Both Debug and Release now declare the Mac-only deployment baseline in the
Xcode project, including the UI test target. The `sdk=macosx*` condition leaves
ordinary iOS builds at 16.0. Previously, Monterey depended on shell-script
command-line overrides. Keep those explicit release constraints as a safeguard.

`check_macos_bundle.sh` checks bundle identity, version, minimum macOS, signature,
and both architectures. It now also inspects every Mach-O loader minimum using
`vtool`; a correct Info.plist alone cannot qualify an incompatible executable or
embedded framework. Both architectures of candidate 1.0 (16) declare Catalyst
15.0; the signed bundle declares macOS 12.0. This is build evidence, not an actual
Monterey runtime test.

## Adaptive layout audit

The native scene installs one root hosting controller and preserves its
`StudioStore` StateObject. Navigation, composer choices, selected tab and preview
player are not keyed to screen width, size class or orientation. Native navigation,
forms, scroll views and safe areas handle the available scene size. No global
UIScreen size or device-name-based layout was found in the native Swift sources.
The Mac minimum window remains 540 × 720. Preview pauses when leaving its screen
or when the app becomes inactive; a fold transition must be runtime-tested before
claiming uninterrupted playback.

Apple requires Xcode 27.1 / iOS 27.1 SDK for the Duo full-screen experience.
The inspected signing host has Xcode 26.3 and simulator runtimes 26.3.1 / 26.5;
this cannot qualify Duo, hinge/camera handling, partial folds or the new SDK.
No guessed hinge APIs or hard-coded phone dimensions have been introduced.

## Qualification matrix

- Monterey: universal signed binary and loader minimum checked; real 12.x runtime
  still required for launch, file picker, preview, export and login qualification.
- Newer Intel Mac: prior build-16 native account/login qualification retained.
- Duo: source audit only; full-screen and folding runtime tests pending a supported
  build host/toolchain and simulator or device.
- Existing iOS: prior signed candidate preserved; no minimum OS increase.
- Android / Windows / PWA: no platform source changes or unnecessary binary rebuild.
- Publication queues, hosted workspaces, billing and identity: no runtime changes.

Internal test delivery and exact provider states are recorded privately. TestFlight
availability does not constitute App Review approval or a public release.

## Follow-up test procedure

With an available authorized Xcode 27.1+ host, build sequentially without changing
global xcode-select. Test the same editing draft and player through outer/inner
screen, partial fold, rotation, Split View, keyboard and large Dynamic Type.
Verify file selection, scroll position and composer values survive; no resize may
submit, render, purchase or publish. Check ordinary phone/tablet behavior separately.
Use an isolated test account and retain current reviewer acceptance locks.

Sources: [Apple Xcode requirements](https://developer.apple.com/xcode/system-requirements),
[Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/),
[Adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/).
