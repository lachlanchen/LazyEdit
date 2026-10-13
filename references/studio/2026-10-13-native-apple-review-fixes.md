# Mac review fixes: native Apple identity and application naming

Completed qualification on 2026-10-14. Scope: fix the Mac build 12 feedback,
prepare signed candidates, and preserve existing review submissions. No App
Review reply, submission, TestFlight upload, or public release was performed.

## Reported problems and changes

| Feedback | Cause | Implemented behavior |
| --- | --- | --- |
| Apple login opens a browser | Apple shared the browser OAuth path | `ASAuthorizationAppleIDProvider` presents Apple's native system sheet on Mac Catalyst and iOS. Google retains its browser OAuth flow. |
| Another login after Apple authentication | An unlinked provider subject could not enter invited registration | A verified new Apple identity continues into native invitation/account setup without another Apple authentication. Existing linked identities enter their existing workspace. |
| Raw authentication error | Cancellation/provider failures escaped as framework errors | Cancellation leaves the login usable. Other failures show an actionable message; a failed provider link does not discard an existing Studio session. |
| Installed app is named “App” | Product name inherited the Xcode target name | Product, bundle, exported package, title and menu use **LazyEdit Studio**. The Swift module remains `App` for existing scene bindings. |

The official Apple sign-in control supplies the localized label and accessibility
behavior. Three onboarding strings are synchronized across all 11 interface
languages. The new flow does not use provider email/name to merge accounts and
does not grant publication privileges.

## Server contract

The optional operator-owned `oauth.apple.nativeClientId` is the native bundle ID,
separate from the existing Apple web Services ID. Both must belong to the app's
configured Apple identity setup. `configure_apple_signin.py --native` enables the
native configuration; signing profiles must include the Apple sign-in entitlement.

1. `POST /accounts/oauth/apple/native/start` accepts a SHA-256 PKCE challenge.
   Linking additionally requires the current account session and fresh password.
2. The app passes the returned state and nonce to Apple's native authorization
   request. It validates the returned state before forwarding the code.
3. `POST /accounts/oauth/apple/native/finish` checks state and device proof,
   consumes the flow before network I/O, exchanges the code using the native
   client ID, and verifies signature, issuer, audience, nonce and freshness.
4. Existing linked identities receive a two-minute one-use transfer receipt.
   New identities receive a five-minute encrypted enrollment, bound to the same
   PKCE proof, until they supply an invitation, username and recovery password.
5. `POST /accounts/oauth/apple/native/enroll` atomically consumes that enrollment,
   registers the isolated member and links the provider. Invalid invitation or
   input rolls back so the user can correct it without repeating Apple login.
6. The existing receipt redemption/session and workspace provisioning paths are
   reused. There is no second publisher or special reviewer bypass.

All new POST routes retain same-origin, body-size and throttling protections.
Subject collisions and closed accounts are rejected. Apple refresh credentials
remain encrypted with their issuing client ID so deletion/unlink revokes against
the correct native or web client. Older web-linked credentials remain readable.
Registration uses nested SQLite savepoints so a failed provider link cannot leave
an account behind or consume its invitation.

## Qualification evidence

- 19 hosted Node tests pass, including native proof binding, audience and nonce
  rejection, replay prevention, invitation retry, account isolation, transaction
  rollback and native Apple revocation.
- 15 Python release-selection tests pass; Mac/iOS build selection and review
  boundaries remain covered.
- 11 interface dictionaries, 396 keys each, validate and synchronize.
- Updated build/install/signing shell scripts pass syntax checks.
- Real native Apple login tested on the existing Intel KVM Mac: native sheet,
  cancel/reopen, invitation setup, private library, linked account, sign-out and
  returning login without another Studio password prompt.
- Deleted that disposable account through the app. The app returned to login;
  the normal deletion route completed Apple revocation, removed links/grants,
  and the provisioner reclaimed its workspace. No owner media was used.
- Real public HTTPS health and provider discovery pass, including
  `nativeApple: true`. Invalid device proof and missing Origin are rejected.
- Signed **Mac 1.0 (16)** archive/package passes strict code-sign verification,
  correct-name checks, macOS 12 minimum and both arm64/x86_64 slice checks.
- Signed **iOS 1.0 (16)** archive/IPA builds and verifies successfully. This run
  does not claim a new real-device iOS Apple sign-in test or a macOS 27.2 test.

The Mac guard now checks the actual bundle/product name as well as every Mach-O
architecture. Removed an obsolete forced link to private `SwiftUICore`, which
current SDKs reject. The iOS build script now explicitly applies the requested
build number instead of relying on the project default.

## Deployment and operations

Only the hosted identity gateway was replaced. The original owner backend/Pi,
existing owner/reviewer workers, databases, provisioner, acceptance lock and
shared ingress were preserved; existing container IDs were compared afterward.
The live gateway and checked-in OAuth source differ only in indentation.

A Docker Hub DNS failure during the second build was handled by using the already
verified local gateway image as the base and copying the three changed hosted
source files. No Docker networking, firewall, shared ingress or peer service was
altered. The normal repository Dockerfile remains the reproducible build path.

Private screenshots, signed-artifact paths/checksums, image/rollback details and
QA cleanup evidence are under `OneTimeSync/LazyEdit/mac-native-auth-fix-20261013/`.
They are intentionally outside Git. The shared store/KVM desktop is retained;
only this task's app and viewer tab are closed after evidence collection.

These fixes address the observed technical feedback. They do not constitute
Apple approval, resolve the separate iOS 4.3 decision, or authorize resubmission.

## References

- [Apple: authenticating users with Sign in with Apple](https://developer.apple.com/documentation/signinwithapple/authenticating-users-with-sign-in-with-apple)
- [Apple: generate and validate tokens](https://developer.apple.com/documentation/SigninwithAppleRESTAPI/Generate-and-validate-tokens)
- Source: `hosted/oauth.mjs`, `hosted/gateway.mjs`, `hosted/store.mjs`,
  `hosted/oauth-native.test.mjs`, `mobile/ios/App/App/StudioAPI.swift`,
  `StudioStore.swift`, `StudioViews.swift`, and `scripts/studio/` build helpers.
