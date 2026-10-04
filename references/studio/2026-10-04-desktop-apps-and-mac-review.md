# Native desktop apps and Mac review — 2026-10-04

## Confirmed release state

**Mac 1.0, build 12 is WAITING_FOR_REVIEW**, submitted at
`2026-10-04T14:35:26.1Z`. The official App Store Connect API confirms the
exact build is attached and VALID. Submission ID:
`68643764-845a-4dd1-ada8-95f7a01dc1e7`; version ID:
`75ec2713-0287-46a7-a556-e588ed57a2c7`.
This is review submission, not approval or public availability.

The universal Mac Catalyst client supports Intel and Apple Silicon, minimum
macOS 12. Native SwiftUI/UIKit screens provide library, upload, editing
choices, activity and account controls. Only detailed editing and permitted
platform account views use secondary authenticated web views. The existing
approved Studio icon is reused; the video logo asset is unchanged.

**Windows 1.0.0 x64 is built and qualified**, as a native WPF client using the
same Studio API. The portable ZIP includes the .NET runtime and requires the
WebView2 Evergreen Runtime. It is unsigned, with no Microsoft Store submission
or Authenticode claim. Password/invitation sign-in works; Windows native OAuth
is not part of this first release. See [Windows instructions](../../mobile/windows/README.md).

The iOS build 9 and Android build 6 submissions were preserved. No hosted worker,
original backend, personal Pi publisher, shared VM or ingress was restarted.
No social post was made to qualify either desktop client.

## Actual qualification

- Mac: exact candidate executable, re-signed in a separate copy with an
  app-owned development identity and a registered-device Catalyst profile.
  Live reviewer sign-in, Keychain persistence across relaunch, private sample
  library, native correction/metadata/subtitle/logo controls, hydrated advanced
  editor and member account isolation were observed on macOS 15.7.9.
- Three genuine 1280×800 screenshots from build 12 were uploaded separately
  to the Mac localization. Apple reports COMPLETE and matching checksums.
- The same universal native source previously launched on the Monterey 3040
  Mac, 7050 iMac and Apple Silicon Mac mini. Those launch checks were build 9;
  full build 12 UI qualification was on the existing KVM Mac. Do not claim
  build 12 was installed on all three physical Macs.
- Windows: self-contained Release build passed with no warnings. Native
  origin/security checks and live isolated reviewer qualification passed:
  login, private library, composer, server plan, hydrated WebView2 editor,
  account isolation and logout. No upload, processing task or post was created.
- Fourteen focused release regressions pass: screenshot checksum/reconciliation,
  platform separation, exact unexpired VALID Mac build selection, pending
  review preservation and refusal to modify a foreign review item.

The reviewer uses the same editing permissions as ordinary invited members.
Platform publication remains separately enabled by the operator. Neither
client falls back to owner media, personal channel sessions or the owner Pi.
The native clients submit through the established queue and server plan
contract; there is no desktop-only processing or publishing pipeline.

## Build and submit Mac

Sync `mobile/ios/` into the established build Mac's
`~/Projects/LazyEditStudio/ios`, and copy the build helpers to that project.
Reuse the existing SDK and signing setup. Candidate archives are immutable.

```sh
LAZYEDIT_BUILD_NUMBER=12 bash build_macos_store.sh
# Resume only an export failure; do not rebuild an accepted archive:
LAZYEDIT_BUILD_NUMBER=12 LAZYEDIT_EXPORT_ONLY=1 bash build_macos_store.sh
```

The helper archives the StudioNative scheme for generic Mac Catalyst,
verifies identity/build/architecture/signature and exports `App.pkg` using
the **MAC_CATALYST_APP_STORE** profile and installer signing certificate.
It uses an app-owned release keychain and restores the previous search list.
Credentials are read privately, never included in source or log output.

Run Apple's `altool --validate-app`, then `--upload-app` once, with `--type
macos`. Set `API_PRIVATE_KEYS_DIR` to the existing protected Apple key
directory. Keep JSON receipts and logs in the private release directory.
Inspect `success-message`/`product-errors`; command exit status alone does not
prove provider acceptance. Reconcile an uncertain upload before repeating it.

The local API helpers use the LazyEdit interpreter and existing protected ASC
key. `status` is read-only. `prepare` operates only on an editable Mac version;
review credentials come from the existing isolated private account file.
For new releases, supply the actual candidate rather than reusing this note's
historical build number:

```sh
python scripts/studio/macos_store.py status
python scripts/studio/macos_store.py prepare --review-credentials /private/reviewer.json
python scripts/studio/app_store_screenshot.py screenshot.png \
  --sha256 REVIEWED_FILE_SHA256 --display APP_DESKTOP --platform MAC_OS --version 1.0
python scripts/studio/macos_store.py submit --build 12 --version 1.0
```

Submission requires one unexpired VALID Mac candidate with the exact build and
marketing version, a compatible Mac-only review item, and Apple's required
metadata. It does not attach an iOS build with the same number, change pending
iOS review or replay a pending Mac submission. Read the actual version,
attached build and submission state after the request. Existing app privacy,
rights/age/availability/pricing declarations were reused; no subscription was
activated in this release.

## Problems fixed and boundaries

1. **Wrong profile kind:** ordinary MAC_APP_STORE cannot sign Catalyst's
   application identifier. Use MAC_CATALYST_APP_STORE, including the existing
   bundle/team and matching distribution certificate.
2. **Incomplete desktop icon:** Mac requires the complete 16–1024 family.
   Export the approved master and declare Mac size/scale entries without
   replacing the iOS icon. Windows uses an ICO derived from the same artwork.
3. **Unreadable installed resources:** private `umask 077` reached the app's
   generated profile/signature files. Archive/export now use ordinary bundle
   permissions while the parent release directory and credentials stay
   private. Apple validation passes.
4. **Keychain sign-in failure:** ad-hoc or missing access-group signatures
   produce OSStatus -34018. The Mac sandbox entitlements now include the
   app-owned Keychain group, outbound network and user-selected files.
   Development-device QA uses those same entitlement values. The store
   archive itself is not re-signed or modified for testing.
5. **Store package cannot be launched as a local QA app:** test a separate
   registered-device copy of the exact executable with
   `sign_macos_qa.sh`. Do not disable Gatekeeper, TCC or SIP. Compare the
   executable before signing; preserve the original distribution archive.
6. **False fresh-video error:** native detail requested a burned artifact
   before any render existed, showing "burn not found". It now requests the
   artifact only when the burn step reports completed. Existing submitted
   iOS9 is unchanged; this source fix is in Mac12 and future mobile builds.
7. **SSH screenshots misleading:** macOS denied Screen Recording for the SSH
   process, so `screencapture` omitted application windows. Genuine QA used
   the existing VM's framebuffer, not a fabricated image or a relaxed TCC
   policy. `scripts/studio/capture_vnc.py` captures an existing loopback-only
   raw RFB framebuffer; it neither starts nor restarts a GUI/VM.
8. **Windows service-session WebView failure:** OpenSSH session 0 has no
   interactive window handle. Live QA ran once in the existing logged-in
   desktop through a project-owned temporary task, which was removed along
   with the temporary credentials. Other applications were left running.

Earlier Mac candidates 10 and 11 were uploaded during qualification but never
submitted. Only 12 is attached to this review. Preserve exact provider receipts;
do not interpret previous VALID builds as submitted apps.

## Artifacts, private access and cleanup

Mac package:
`~/Projects/LazyEditStudio/release/mac-store-export-12/App.pkg` on the existing
build Mac. SHA-256:
`2dcf7534415d83aba4eaed79033d7cb52cdfb7ad95b73fb90377e3aa1a290d6b`.

Windows ZIP:
`temp/desktop/LazyEditStudio-windows-x64-1.0.0.zip`. SHA-256:
`5ceb3a987038634b9057ada60f87d8a9967f0ad996170f33e57b6fbde9d26e40`.

Public evidence/receipts are in `store/studio/release.json`; approved Mac store
screenshots are in `store/studio/screenshots/mac/`. Other genuine qualification
screenshots are under ignored `temp/desktop/evidence/`. Generated apps, build
trees, profiles and credentials are excluded from Git.

Private reviewer account:
`/home/lachlan/Nutstore Files/Share/LazyEdit/lightmind-reviewer-account.json`.
Local ASC key: `~/.config/echomind/private/`; build-Mac provider keys and
keychain password: `~/.config/echomind/apple/`. Mac QA private signing files:
`~/.config/lazyedit-studio/qa-signing/`. These are file-location hints, not
credentials to distribute. Never copy their contents into this repository.

The existing store noVNC browser remains the single store-login desktop.
The Mac QA app was stopped after evidence capture; the shared Mac VM/noVNC
was preserved. Windows qualification removed its own temporary interactive
task and private credentials and exited its app. Keep current/previous
reproducible packages; retain evidence rather than obsolete running apps.

Official references:
[Apple platform records](https://developer.apple.com/help/app-store-connect/create-an-app-record/add-platforms/),
[Mac distribution signing](https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac/),
[Windows packaging](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/publish-first-app).
