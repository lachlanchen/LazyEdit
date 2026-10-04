# Windows signing, real-machine QA and Microsoft Store handoff

Updated 2026-10-05. Owner authorized Windows testing on the physical HKU lab
PC and existing KVM Windows, signing, and Microsoft Store submission with a
US **$0.99 paid download**. This is separate from subscriptions and from the
already submitted Apple/Google releases.

## Actual state

Native WPF **1.0.1 x64** built with the existing .NET 10 SDK. The self-contained
ZIP is unsigned; the separate development MSIX and its own launcher are signed.
The same signed MSIX installed and passed live reviewer qualification on both
Windows 11 machines. No upload, preparation or social post was submitted by QA.

The test certificate is self-signed, RSA-3072, code-signing EKU, and its private
key is **nonexportable**, retained on the signing PC. The public leaf was
temporarily trusted in **TrustedPeople**, never TrustedRoot. This is not public
CA trust. Microsoft applies the trusted Store signature after certification.

Microsoft's company enrollment is in progress. The owner Microsoft session
works, but initially had no Apps & Games workspace. The existing verified
company D-U-N-S record was read back from Google Play and selected in Microsoft's
lookup. Company website/display name and legal/support contact fields are
prepared. The company email verification request returned HTTP 200; a code
had not arrived during the checks recorded here. **No app name has yet been
reserved, no production Store identity exists, $0.99 is requested rather than
configured, and no Windows review submission is claimed.** Resume that same
enrollment instead of creating another account.

Mail delivery was checked without changing DNS or account settings. The actual
iCloud Custom Email Domain panel shows **Allow All Incoming Messages: On**, with
both attempted company addresses active under the domain owner. MX records point
to iCloud, and other domain messages were received recently. Read-only IMAP checks
covered all ten folders, including Inbox and Junk, and found no matching Microsoft
verification message. The sender's HTTP 200 / "code sent" confirmation does not
prove SMTP delivery. The cause remains undetermined; do not disable filtering,
change the catch-all or repeatedly request codes to conceal this pending state.

## Exact candidates

| Artifact | SHA-256 |
| --- | --- |
| `temp/desktop/LazyEditStudio-windows-x64-1.0.1.zip` | `2c4e4a3cb414b6a082b7163c51e8b8223cc0643bd13608cfe1ef6bac3be109e4` |
| `temp/desktop/LazyEditStudio-windows-x64-1.0.1.0-qa.msix` | `1bf3f8aff06b1cc095e4443dd605a66628ac27fa8746476fdb1ace18c15f0eb0` |
| Installed signed `LazyEditStudio.exe` on both machines | `9b55504b4462e5a39985302c2a760b765634663b25a76c3df37e6b4f114d409d` |

Dedicated development package identity: `LazyingArt.LazyEditStudio.QA`;
publisher `CN=LazyingArt Studio QA`; package version `1.0.1.0`.
It is not a reserved Microsoft Store identity.

HKU and KVM live checks passed at respectively `2026-10-04T21:32:39.1868004Z`
and `2026-10-04T21:32:12.5893803Z`. They verify real reviewer sign-in, an isolated
private library, native editing composer, server plan digest, a fully hydrated
secondary editor showing the actual selected video, editing-only account
permissions and sign-out. Both installed launchers report `Valid` signatures
under the temporary local test trust. Windows 10 is declared as the minimum;
actual Windows 10 hardware QA has not been performed.

Genuine public screenshots are under `store/studio/screenshots/windows/`.
Machine-specific evidence and full certification reports remain in ignored
`temp/desktop/evidence/windows-{hku,kvm}-1.0.1/`.

## Findings and durable fixes

1. **Wrong Windows SSH identity / too many offered keys:** use the pinned
   existing route and actual console user. Connection hints are private, not
   an excuse to disable host-key checking or guess passwords.
2. **MSIX install through SSH fails with 0x80070005:** event logs showed
   Process Lifetime Manager initialization failing in the service token.
   `install_windows_test.ps1` runs Add-AppxPackage in the already logged-in
   console through one limited interactive task. It is scoped only to the
   dedicated QA package. No global policy or developer-mode change is needed.
   Task polling also waits for a fresh LastRunTime and result, rather than
   treating the task's initial Ready state as completion; queued tasks are
   included in owned-task cleanup.
3. **SignTool sees a certificate but cannot use the key:** a later SSH session
   failed at its private-key filter despite HasPrivateKey=true. Signing in the
   existing console succeeds. Keep the nonexportable key there; do not export
   it, weaken its permissions or falsely label the portable ZIP signed.
4. **Interrupted packaging leaves misleading output:** `package_windows.ps1`
   now packs/signs a temporary MSIX and promotes it only after success, with a
   digest receipt. A failed signing attempt left no final candidate; the
   subsequent interactive signing completed. Existing candidates are preserved.
5. **Preview test captured the shell before data loaded:** native QA now waits
   for the actual selected video's title in the WebView before capturing it.
   The new screenshot shows the loaded private library, not a loading spinner.
6. **High-DPI declaration missing:** an embedded asInvoker application manifest
   now declares PerMonitorV2 and legacy true/pm. `mt.exe` extracted and verified
   the manifest from the installed signed launcher. Win32 runtime queries
   independently report both process and window PerMonitorV2=true at 96 DPI.
7. **Old certification scanner warning persists:** WACK `10.0.19041.5609`
   completed all 24 tests on Windows 11 build 26200, but its final result is
   **WARNING**, not PASS. DPIAwarenessValidation says it could not process the
   launcher even with the verified declaration and runtime context. This
   suggests a tool-analysis issue; it is not proof of certification clearance.
   The other non-pass is optional Blocked executables, with references in
   bundled .NET/WPF/WebView components. Other required tests passed. Recheck with
   a current kit or Microsoft's actual certification before claiming approval;
   do not modify Microsoft runtime DLLs to suppress informational scans.

## Reusable release procedure

Build in ordinary PowerShell with the existing SDK:

```powershell
./scripts/studio/build_windows.ps1 -DotNet /absolute/path/to/dotnet.exe
```

The builder takes the version from the project, runs the native/origin contract
check, and creates a new ZIP without overwriting an existing candidate. The
approved icon master also produces MSIX tile assets via `build_icons.py`.

For production, reserve **LazyEdit Studio** in Partner Center, then copy the
actual identity from Product identity into a public, app-owned JSON:

```json
{
  "name": "ACTUAL_RESERVED_PACKAGE_NAME",
  "publisher": "CN=ACTUAL_MICROSOFT_PUBLISHER_ID",
  "publisherDisplayName": "LazyingArt LLC",
  "source": "partner-center"
}
```

Use that exact identity, not this note's placeholder strings:

```powershell
./scripts/studio/package_windows.ps1 -IdentityFile /path/to/store-identity.json -Version 1.0.1.0
```

Microsoft Store accepts an unsigned MSIX for its own signing. If doing another
local signed test, the certificate subject must exactly equal the manifest
publisher; run SignTool where that key is accessible. `-TestPackage` explicitly
marks development packages. Private certificates/reviewer files never enter
the staging tree or upload.

Remote live test, after installing the exact QA package in the interactive
console:

```powershell
./scripts/studio/install_windows_test.ps1 -Package /path/to/qa.msix -ExpectedSha256 ACTUAL_PACKAGE_SHA256
./scripts/studio/check_windows.ps1 -Executable /installed/path/LazyEditStudio.exe -ExpectedSha256 ACTUAL_EXE_SHA256 -ReviewerCredentials "$env:LOCALAPPDATA\LazyEditStudio\reviewer-qa.json"
```

Copy only the isolated reviewer input to that explicitly temporary path; the
helper protects and deletes it. Never pass the source account file. Packaged
LocalAppData may be redirected into the package cache; the check handles both
locations and requires exactly one fresh result.

Run `appcert reset` then `appcert test -packagefullname ACTUAL_FULL_NAME
-reportoutputpath /path/report.xml` in the same existing console, after checking
that no other project is running certification. Read the XML result; exit code
0 only means the tool finished. Remove only the task created for that run.

Finally uninstall the dedicated QA MSIX via `install_windows_test.ps1 -Remove`
and remove its exact temporary TrustedPeople leaf. Preserve the current signed
candidate, public certificate, digest receipt and immediately previous package.
Keep the nonexportable signing key in protected CurrentUser/My for future tests.
No new GUI stack is needed; preserve the shared VMs and other projects' browsers.

## Store submission after enrollment

Use the existing Store desktop/profile. Start at
`https://storedeveloper.microsoft.com/` for company onboarding; the generic
Partner Center home is not proof of an Apps & Games developer account.
Reuse the existing signed-in owner identity and company legal records, verify
the company-domain email, complete the agreement and provider verification,
then wait for authoritative enrollment/role status.

After enrollment, reserve the name and use the actual production identity.
Prepare Pricing and availability with US $0.99 and verify the saved value;
complete company payout/tax eligibility from actual protected records rather
than guessing a tax classification. Use Photo & video as the editing category,
answer IARC based on actual features, upload the production MSIX, reuse
`store/studio/listing.json` and the genuine Windows screenshots, disclose
runFullTrust for native WPF/DPAPI/file-picker functionality, and provide the
isolated reviewer credentials only in the provider's private review notes.

Review access is ordinary private editing; social publication remains an
optional backend-granted operator feature. No owner Pi, channels or social
credentials are shared with review. Subscriptions remain inactive. Submit once
and read back the provider's submission ID/state, price and package digest.

Private enrollment/company files: `~/.config/lazyedit-studio/microsoft/`.
Reviewer source: Nutstore `Share/LazyEdit/lightmind-reviewer-account.json`.
The D-U-N-S verification note is maintained in the **private**
`LazyingArtLinkPrivate/docs/company/duns-verification-20261005.md` repository.
No tax IDs, passwords, codes, raw account screenshots or identity scans belong
in this public repo.

Official references:
[Store onboarding](https://learn.microsoft.com/en-us/windows/apps/publish/get-started),
[Company registration](https://learn.microsoft.com/en-us/windows/apps/publish/partner-center/open-a-developer-account?tabs=company),
[MSIX signing](https://learn.microsoft.com/en-us/windows/msix/package/sign-msix-package-guide),
[DPI manifests](https://learn.microsoft.com/en-us/windows/win32/hidpi/setting-the-default-dpi-awareness-for-a-process),
[Desktop Bridge required/optional tests](https://learn.microsoft.com/en-us/windows/uwp/debug-test-perf/windows-desktop-bridge-app-tests).
