# Agent mode: native test builds, 2026-10-09

The owner requested iOS and Android test builds of the chat-driven editing
and publication workflow. The native screens use the same authenticated
Agent routes and preparation/publication queue as the PWA. See
[Agent mode](agent-mode.md) for its permissions and idempotency contract.

## Candidates

- iPhone/iPad: version 1.0, build 11, existing private TestFlight group.
- Android: version 1.0, versionCode 9, existing Google Play internal track.
- Public Android6, existing Apple review submissions and Mac13 are separate.
  This task does not submit or change a public review.

Final provider readback: iOS11 is `VALID`, attached to the existing internal
group and `IN_BETA_TESTING` (build/delivery ID
`b77df6eb-2606-487b-a824-46e7efe8dbe8`). Google9 is **Available to internal
testers** on the active Internal track. Exact artifact hashes and provider
receipts are recorded in `store/studio/release.json` and the private handoff.

Agent appears only when the signed-in workspace advertises `agentChat`.
The live owner workspace supports it. The older isolated reviewer workspace
is still under its client's acceptance lock; it was not replaced or restarted.
An older worker safely hides this tab. Account invitations and subscriptions
do not grant social publishing access.

## Verification

- iOS: dedicated Studio simulator, native owner sign-in, Agent tab, attachment
  menu, Files picker cancellation and sign-out: one test passed in 68.669s.
- Android: exact signed release APK9 installed and launched on the dedicated
  API34 emulator. Same-source instrumentation checked native Agent navigation,
  unchecked publication by default, message entry, Files picker cancellation,
  and authenticated-origin restrictions: two tests passed in 6.014s.
- No test sent a chat request, rendered a real video or posted to a channel.
  The prior Agent implementation's API/queue contracts and synthetic upload
  exercise remain separate evidence, not a claim of native end-to-end posting.
- These are simulator/emulator results, not physical-device qualification.
  The iOS simulator retains its known translucent tab-bar framebuffer artifact;
  native navigation and accessibility checks passed.

## Fix and release lessons

Cancelling or rejecting an Agent attachment now clears its routing intent,
so a later ordinary upload is not accidentally opened as an Agent attachment.
Android had already accepted candidate8 before this fix. Candidate8 was
removed from the release draft and replaced with9; it was not released.
Google's final preview must contain only9 and the correct release notes.

The Android test opens the system DocumentsUI picker. Return with Android's
global Back action; Espresso's application-idle Back helper can hang while
the app is not the foreground activity. This is a test-harness correction.

The dedicated Android emulator had an incompatible quick-boot snapshot. Use
`-no-snapshot` to cold boot that AVD; do not erase the AVD or touch other devices.
Stop it after evidence capture. The signed release APK and debug instrumentation
APK have different keys, so replace only this app on the disposable Studio AVD.
Do not apply that uninstall procedure to a user's installed app.

Apple validation briefly logged an upstream HTTP500, then completed successfully
through the tool's normal retry. A log line alone is not a failed submission:
inspect the final JSON receipt. Validate the final exact artifact again after
any source fix. Reconcile upload receipts and ASC processing state before retrying
an uncertain upload; never create a duplicate delivery blindly.

## Repeatable release steps

1. Read the live stores' app identity, platform, version and highest build.
2. Increment Android versionCode and iOS CURRENT_PROJECT_VERSION independently.
3. Build with the existing protected signing keys using `build_android.py` and
   `build_ios.sh`; preserve the current published artifacts before rebuilding.
4. Qualify native navigation using the tests in `StudioNativeTest.java` and
   `StudioUITests.swift`, with temporary private credentials.
5. Upload the AAB once to the existing Internal track. Focus/type/blur release
   fields and verify their preview; confirm the Internal track before Save and
   publish. The missing mapping-file warning is expected for this unminified app.
6. Validate and upload the IPA once through `altool`, then wait for `VALID` and
   attach the exact IOS build through `apple_beta.py attach`. Do not use its
   public-review helpers for a private beta request.
7. Read back actual tester availability, update `store/studio/release.json`,
   stop the owned test devices, remove temporary QA credentials, and push source
   and release notes. Preserve the shared Apple/Google login desktop.

Private receipts and coordination go under
`/home/lachlan/Nutstore Files/OneTimeSync/LazyEdit/agent-native-beta-2026-10-09/`.
Working evidence stays ignored under `temp/studio-agent-beta-20261009/`.
Signed IPA archives remain on the established build Mac; credentials, binaries,
screenshots containing private account data and browser state do not enter Git.
