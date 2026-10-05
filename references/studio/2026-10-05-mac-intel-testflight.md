# Intel Mac support and TestFlight delivery — 2026-10-05

## Result and cause

Native **LazyEdit Studio 1.0 (12)** is now attached to **LazyEdit Studio
Internal**. Apple's API reports `MAC_OS`, `VALID`, `attached=true` and
`internalBuildState=IN_BETA_TESTING`. The owner is the group's sole tester.
Refresh TestFlight and select Mac build 12. Build 9 is the iOS candidate.

The reported Apple Silicon requirement came from the TestFlight delivery gap:
Mac12 was uploaded and submitted for formal Mac review, but had never been
attached to the internal testing group. That group offered iOS builds. An iOS
app running on a Mac requires Apple Silicon; the separate native Mac Catalyst
app supports both Intel and Apple Silicon. This was a missing distribution
step, not an architecture restriction in the Mac executable.

Build12 contains `x86_64 arm64`, declares macOS12.0, and is accepted by Apple as
a native Mac build. The original package remains unchanged, SHA256
`2dcf7534415d83aba4eaed79033d7cb52cdfb7ad95b73fb90377e3aa1a290d6b`.
Both Mac1.0/build12 and iOS1.0/build9 remain `WAITING_FOR_REVIEW`; internal
TestFlight availability does not mean App Store approval. No new app binary,
re-upload, formal-review cancellation or resubmission was needed.

## Actual testing and limits

| Environment | Exact build | Evidence |
| --- | --- | --- |
| Intel/x86_64 KVM, macOS15.7.9 | 12 | Native reviewer sign-in, private sample library, correction/metadata composer, hydrated full editor, editing-only account controls and Keychain persistence after relaunch passed. |
| ARM Mac mini | 9 previously | Earlier native launch/signature check; build12's ARM slice is verified statically, not claimed as fresh ARM UI qualification. |
| Intel Monterey3040 and Intel7050iMac | 9 previously | Earlier native launch checks; current SSH routes were unavailable, so no new build12 test is claimed on these machines. |

Today's UI check uses a development-signed copy of the submitted executable
on its registered QA Mac. The immutable distribution archive/export is
preserved. Actual framebuffer images are under ignored
`temp/desktop/evidence/mac-compatibility-20261005/`. They show native library,
composer, account/build12, hydrated WebKit editor and the library after
relaunch. No upload, processing request or social post was created. No owner
credentials or personal media were used. TCC/Gatekeeper and shared services
were not changed. The task-owned QA app is stopped after evidence capture;
the shared VM, store browser and other projects remain available.

## Repeatable release checks

`scripts/studio/check_macos_bundle.sh APP BUILD` checks exact bundle/build,
macOS12.0, both architectures in **every bundled Mach-O binary**, and the
strict signature. The local universal build, Store archive/export helper and
QA installer now call it. The actual current archive passes. A disposable
copy thinned to ARM-only is rejected before export/install; it was removed
after the negative test. Future signing Macs must receive this helper beside
the build/install scripts.

`apple_beta.py` now selects by platform **and** marketing version **and**
build number, rejects expired/invalid/ambiguous candidates, checks that the
group belongs to Studio and is internal, adds the requested build without
replacing other platforms, and reads back the assignment. Repeating attach
after a confirmed assignment makes no mutation. After a timeout, use status
to reconcile before retrying. Existing beta text is preserved.

Run with the LazyEdit environment's `python`:

```sh
python scripts/studio/apple_beta.py status \
  --platform MAC_OS --version 1.0 --build 12
python scripts/studio/apple_beta.py attach \
  --platform MAC_OS --version 1.0 --build 12 \
  --notes-file store/studio/macos-build-12-notes.txt
python scripts/studio/apple_beta.py status \
  --platform IOS --version 1.0 --build 9
```

For a future release, substitute the qualified candidate's exact version and
number. Uploading or submitting a Mac build does **not** assign it to a
manually managed TestFlight group. Verify `attached=true` and Apple's beta
state as a separate release step. Preserve existing iOS and Android lanes.

Eight focused beta regressions plus seven Mac-submission regressions pass,
including same-number iOS/Mac collision, missing version, duplicate candidate,
invalid/expired build, group ownership, read-only status, additive assignment,
repeat reconciliation and pending-review preservation.

Apple references:
[Universal Mac binaries](https://developer.apple.com/documentation/apple-silicon/building-a-universal-macos-binary),
[iOS on Mac versus Mac Catalyst](https://developer.apple.com/documentation/apple-silicon/running-your-ios-apps-in-macos),
[iOS TestFlight builds on Apple Silicon](https://developer.apple.com/help/app-store-connect/test-a-beta-version/test-iphone-and-ipad-apps-on-macs-with-apple-silicon).
