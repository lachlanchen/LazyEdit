# Rounded icon: internal testing only, 2026-10-07

The owner requested rounded icon corners and test distribution, explicitly
excluding a new public review submission. The existing vivid ribbon/play
artwork is retained. Publication watermarks and the publishing service were
not changed.

## Assets and builds

`figs/app-icon/lazyedit-studio-icon-v2-rounded.png` is the image-tool-edited
transparent master. `scripts/studio/build_icons.py` preserves its alpha for
desktop, legacy Android, Windows and in-app/PWA assets. Mac exports have a
1/16 transparent inset on each side. iOS uses the opaque full-bleed original
and its system mask; Android adaptive icons retain their system mask.

| Target | Version / build | Distribution scope |
| --- | --- | --- |
| Android | 1.0 / 7 | Existing Google Play internal tester group |
| iPhone / iPad | 1.0 / 10 | Existing private internal TestFlight group |
| Native Mac, Intel + ARM | 1.0 / 13 | Existing private internal TestFlight group |

Provider readbacks and exact binary hashes are recorded in
`store/studio/release.json`. The corresponding `*-build-*-notes.txt` files
contain the test release notes. Windows assets were regenerated for consistency;
no Windows package or Store submission is claimed by this change.

Native candidates also include already-committed source improvements since the
previous mobile releases: backend-provided subtitle-language choices and the
scoped publishing capability fallback; iOS also includes the existing guard
against fetching a burned artifact before a render exists. This is not a
claim that only icon bytes changed in the mobile binaries.

## Qualification

- Icon checks: iOS 1024px RGB and fully opaque; Android adaptive foreground
  fully opaque; Mac, legacy Android and PWA corner alpha zero. Mac small-size
  exports and the running app's Dock icon were visually inspected.
- Android: exact signed release APK7 installed and launched on the dedicated
  Studio API34 emulator. Two same-source instrumentation tests passed: live
  isolated member editing and authenticated-origin restrictions. No publishing
  action was triggered. Release signing identity was unchanged.
- iOS: the dedicated iPhone 17 Pro Max simulator passed one live member-editing
  test in 117.572 seconds. It verifies sign-in, private library/account controls,
  native composer, hydrated full editor without social controls, and sign-out.
  The signed distribution IPA was separately validated by Apple. Simulator
  framebuffer capture showed a graphics artifact in the translucent sheet
  header, so this does not claim physical-device visual qualification.
- Mac: the exact signed candidate passed the universal Mach-O, minimum macOS
  12.0, bundle ID/build and strict signature checks plus Apple validation.
  A separately development-signed copy of that executable launched on the
  existing Intel KVM Mac and displayed the rounded Dock icon. The shared GUI
  was busy with another app's store authentication; no full Mac13 UI regression
  or physical/ARM-device test is claimed. Mac12's previous qualification remains
  separate evidence.

## Repeatable commands and lessons

Use the existing protected signing setup and pinned Mac SSH route. Do not copy
credentials into the repository or create a replacement browser profile.

```bash
python scripts/studio/build_icons.py
python scripts/studio/build_android.py
# On the established build Mac, after syncing mobile/ios/:
LAZYEDIT_BUILD_NUMBER=10 bash build_ios.sh
LAZYEDIT_BUILD_NUMBER=13 bash build_macos_store.sh
```

For Android test packaging use `:app:assembleDebug :app:assembleDebugAndroidTest`.
The unqualified Gradle task also builds unrelated Cordova plugin tests and can
fail on their duplicate Kotlin dependencies; it is not the Studio test target.
Use the explicit emulator serial, never `adb -e` on a shared machine.

For Google release notes, scroll the observed textarea into view, focus it
with a real click, type and blur, then read back the **preview**. Setting a
detached/unfocused field was not retained. Upload AAB7 once, reuse that draft,
and confirm the internal track before its final Save and publish action.
The missing deobfuscation-file warning is expected for this unminified build;
do not invent a mapping file.

For Apple, validate and upload each exact signed artifact once. Wait for its
platform-specific build to become `VALID`, then use:

```bash
python scripts/studio/apple_beta.py attach --platform IOS --version 1.0 \
  --build 10 --notes-file store/studio/ios-build-10-notes.txt
python scripts/studio/apple_beta.py attach --platform MAC_OS --version 1.0 \
  --build 13 --notes-file store/studio/macos-build-13-notes.txt
```

The helper verifies the app, platform, build number and internal group, adds
the exact build without replacing other assignments, and reads back its beta
state. Check `status` before retrying an uncertain result. Never use the public
review `prepare`/`submit` commands for an internal-only request.

## Preservation and cleanup

Google production remains build6. The existing Apple formal-review attachments
remain iOS9 and Mac12. No new review submission, external beta review, billing
activation, social publication or worker restart is part of this task.

Ignored evidence is under `temp/studio-beta-20261007/`; signed Apple packages
remain in `~/Projects/LazyEditStudio/release/` on the established build Mac.
Previous production Android6 artifacts were retained under the evidence
directory's `previous/android6/` before building7. Credentials, archives,
browser state and QA logs are not committed.

The dedicated Android emulator and Studio iOS simulator were stopped after
tests. Studio's Mac QA app was quit and its temporary reviewer credential was
removed. Shared Mac services, other apps and the existing store noVNC desktop
were preserved. The final coordination note is in the owner's default
`Nutstore Files/OneTimeSync/` folder.
