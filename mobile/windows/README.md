# LazyEdit Studio for Windows

Native WPF screens cover sign-in/invitation registration, private library,
resumable upload, editing choices, reviewed task submission, activity and
account controls. The detailed editor and optional platform login open in a
secondary WebView2 window. This is not a packaged PWA.

The client connects only to `https://edit.lazying.art`, with the same account
permissions and queue as the mobile apps. Ordinary invited members can edit
and preview; publication controls require server-granted publishing access.
Only the owner can request the existing Pi mode, and the server enforces this.
Passwords, reviewer logins and platform cookies are not embedded in the app.

## Install

Extract `LazyEditStudio-windows-x64-1.0.1.zip` into a directory and run
`LazyEditStudio.exe`. Windows 10/11 x64 and the Microsoft Edge WebView2
Evergreen Runtime are required. The package includes its .NET runtime; users
do not need an SDK. The portable ZIP remains unsigned. A separate MSIX was
signed with a nonexportable development certificate and tested on the HKU lab
PC and KVM Windows. This is local test trust, not a public CA signature or a
Microsoft Store release. Do not disable system protection to run the ZIP.

Sign in with an invited Studio account. Sessions are encrypted with Windows
DPAPI for the current Windows user. This version uses password/invitation
sign-in; native Apple/Google OAuth is not implemented on Windows yet.

The 11 existing Studio locale files are reused. Core translated labels are
available; new Windows-specific labels fall back to English. Arabic uses a
right-to-left layout. The language preference is stored only on this device.

## Editing and reliable submission

- Choose subtitle languages in bottom-to-top order, correction context,
  metadata direction, layout, logo, existing run and eligible platforms.
- Per-video choices stay local; they do not overwrite website defaults.
- Perfect portrait input cannot enable background fill.
- **Review plan** obtains the server's plan digest before submitting.
- Uploads stream in 8 MiB chunks from the original file. A saved receipt
  reconciles the server offset; it does not make another media copy.
- A task's exact body and idempotency key are saved before submission. After
  an interrupted request, use **Check saved submission**. The app does not
  blindly create another task. A definitively rejected request can be edited;
  an unknown outcome retains its identity.
- Only active Activity windows poll. Web views close on sign-out. The server
  remains responsible for workspace isolation and restricted login desktops.

## Build and qualification

From PowerShell on Windows with the shared .NET 10 SDK:

```powershell
./scripts/studio/build_windows.ps1 -DotNet /path/to/dotnet.exe
```

This publishes the self-contained x64 directory, runs the local native/origin
contract check, and creates one ZIP under `temp/desktop/`. Generated `bin`,
`obj`, packages and state are excluded from Git.

Optional live qualification accepts an existing *isolated* editing-only
reviewer JSON file containing `username` and `password`:

```powershell
./LazyEditStudio.exe --workspace-check /private/reviewer-qa.json
```

Run this in an interactive desktop, not OpenSSH's Windows service session.
It verifies actual account/library/composer/plan/editor access and logout,
captures genuine native/WebView screenshots, and submits no preparation or
social publication. Results go to `%LOCALAPPDATA%/LazyEditStudio/`.
Delete the temporary credential file and any owned temporary scheduled task
afterward. Never put these credentials in source or command-line values.

The qualified package and Mac submission are recorded in
[the desktop release note](../../references/studio/2026-10-04-desktop-apps-and-mac-review.md)
and [the provider manifest](../../store/studio/release.json).

## MSIX signing and Microsoft Store

See [the Windows qualification and submission handoff](../../references/studio/2026-10-05-windows-signing-and-store.md).
`package_windows.ps1` packages the existing native build and preserves its
portable ZIP. A Store build requires the exact reserved Partner Center name,
publisher CN and publisher display name in an identity JSON with
`"source": "partner-center"`. Never upload the dedicated `.QA` identity.

Run signing from the existing interactive Windows console. An SSH service
token may see a certificate but cannot unlock its private key. The key stays
on its Windows machine; do not export a PFX to work around that restriction.

`install_windows_test.ps1` and `check_windows.ps1` use bounded, temporary tasks
in that console for remote qualification. They protect other apps, preserve
the exact candidate digest, and remove their own tasks and temporary reviewer
input. Sideload trust is limited to the public test certificate in TrustedPeople
and is removed after the dedicated QA package is uninstalled.
