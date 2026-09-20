# LazyEdit native beta builds

Application identifier: **art.lazying.lazyedit** on both platforms.
Version 1.0, build 2. Read store/studio/release.json for hashes and receipts;
a compiled binary, upload receipt, tester assignment and installation are
different states. No public production submission was made.

Verified 2026-09-20: iOS build 2 is VALID / IN_BETA_TESTING with one internal
tester; Play internal track is Active with build 2 available to the owner.
[Android test opt-in](https://play.google.com/apps/internaltest/4700083281147641073).
For iOS, open the Apple TestFlight invitation on the owner account; no public
join URL exists for this internal group.

## Rebuild

Use the shared installations; do not download another SDK, JDK or Xcode.

```sh
cd mobile
npm ci
node node_modules/@capacitor/cli/bin/capacitor sync
cd ..
python scripts/studio/build_icons.py
python scripts/studio/build_android.py
```

Node 22.21, Capacitor 8.5.1, Android SDK 36, Gradle wrapper 8.14.3,
and JDK 21.0.10 were used. A JRE-only JAVA_HOME fails because javac is missing.
Use the LazyEdit conda python. Android signing is generated once in private
~/.config/lazyedit-studio/android and backed up to Nutstore Share/LazyEdit.
Preserve that upload key; do not regenerate it for a later release.

Increment Android versionCode and iOS CURRENT_PROJECT_VERSION together before
another upload. build_ios.sh accepts LAZYEDIT_BUILD_NUMBER for artifact naming;
the Xcode project build number must independently match that value.

Sync mobile/ios to the existing Mac project's ios/ directory (without --delete),
plus build_ios.sh, the private provisioning profile and ExportOptions.plist.
Run build_ios.sh on that Mac. It uses its own keychain, imports the existing
authorized distribution certificate, restores the previous keychain list,
locks its keychain on exit, then verifies the signed archive. Do not alter
another app's profile, keychain, default Xcode or running simulator.

Copying/syncing Capacitor source never replaces store application identities.
This project reuses the original LazyEdit panda logo rasterized from figs/logo.svg;
it does not invent a new logo.

## Apple

App Store Connect app: **6814061525**.
Create the first record in the existing authenticated browser, iOS, English US,
name LazyEdit Studio, SKU lazyedit-studio-ios-2026, matching bundle ID.

Validate and upload the exact IPA using xcrun altool and the existing private
App Store Connect key. Save provider output privately, never the key.
An uncertain upload must be reconciled against Build Uploads before retrying.

Internal group **LazyEdit Studio Internal** uses manual build distribution.
The owner is its sole tester. No public TestFlight group was created.
Use `python scripts/studio/apple_beta.py status` for read-only status.
Once the exact build is VALID, `... apple_beta.py attach --build 2` adds
What to Test and attaches it once to the internal group. Inspect TestFlight's
actual Testing/Ready state afterward. The owner's TestFlight invitation is
separate from the Studio account password.

Apple login recovery: try the already-authorized existing browser session and
its Continue buttons first. An expired page does not imply a new 2FA code.
The shared KVM Mac has the owner's account available if Apple really requests
verification. Do not ask the owner for a code without observing that prompt.

## Google Play

Console app **4975166991517752718**, package art.lazying.lazyedit,
**Internal testing only**, free. Upload AAB, inspect version code and warnings,
enter release notes with language tags on separate lines, review, then use
Save and publish and its final confirmation. Add only the LazyEdit owner list,
not an unrelated app's existing list.

If a draft already contains build 1 and build 2, remove build 1 using its
Manage artifact menu → Remove app bundle → confirm Remove. Deleting the
upload progress row alone does not remove the artifact. Read back the review
page: exactly one version code, 2. Otherwise Play rejects the shadowed bundle.
No mapping-file warning is expected to block this unminified test client.

Until app setup/public review is complete, Google displays the temporary name
art.lazying.lazyedit (unreviewed). Internal availability does not imply a public
listing or production approval.

## Evidence and QA boundaries

Android: signed release APK installed on a project-owned read-only emulator;
real HTTPS login, native picker and hosted upload checked. iOS: simulator
build launch and real HTTPS login-page rendering checked; signed IPA validated
by Apple. These are not physical iPhone or installed-from-TestFlight receipts.

iOS's first request returned a network timeout, leaving the original WebView
blank; the next launch worked. Build 2 adds the bundled reconnect page using
server.errorPath, on both platforms. Do not solve this by disabling TLS.

Shared store browser: retain it for the owner; stop only this project's review
desktop/emulator/simulator after evidence capture. The private runtime handoff
records exact ownership and noVNC URL.
