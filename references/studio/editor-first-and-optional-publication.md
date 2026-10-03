# Editor-first Studio and optional publication

Owner decision, 2026-10-04: finishing and previewing the edit is the main
product. Social publication needs dedicated account preparation and is an
optional, operator-enabled integration. A normal member never needs social
credentials to use the editor. This is the same policy for real members and
the reviewer; there is no review-detection code.

## Normal workflow

Sign in to the private workspace, upload a video, choose subtitle/layout/logo
options, add context, review the choices, process once and preview the result.
The existing pipeline still handles ASR correction, translations/readings,
rendering, cover and metadata. A completed run is reusable. Unknown submission
results retain their request ID and require reconciliation, not another post.

Native configuration supports **Prepare only**. **Preview edited video** uses
the authenticated rendered-media endpoint. The full PWA editor keeps processing,
context correction, cover and preview controls available. Platform selection,
music publication and the publication queue appear only for enabled accounts.

## Operator configuration

Protected hosted control configuration, not source code or a public user field:

```json
{
  "publishing": {
    "enabled": true,
    "administrators": true,
    "accountIds": []
  }
}
```

Omitting this policy disables hosted publication. `enabled:false` pauses it
globally. An immutable registry account ID may be added to `accountIds` when
the operator chooses to enable a particular member. Usernames supplied by a
client, subscription receipts, invitations and OAuth identities do not grant
this capability. The account still uses only its own Docker platform profiles.
The Pi remains restricted to the existing owner by the separate ingress rule.

Update both protected host `config.json` and `registry/gateway.json`, preserving
their other fields. Activate configuration at an idle gateway boundary; do not
restart the personal backend or Pi. Never publish these credential-bearing
files to Git.

## API contract and enforcement

`GET /accounts/account`, `GET /auth/me`, and the native composer response expose
`capabilities:{editing:true,publishing:false|true}`. The authenticated PWA context
contains the same worker decision. A linked app should always offer editing
and preview, and offer publication only if this flag **and** its granted
`publication.publish` scope allow it.

The gateway overwrites `x-studio-publishing` from operator policy. Client headers
cannot forge it. The cell checks that trusted capability before opening a
platform desktop or accepting video/music publication. Existing tokens are
constrained on every request; holding an old broad scope does not bypass the
capability. Prepared-only music packages explicitly use `post:false` and remain
limited to that account's media. Denied publication does not allocate an intent,
consume a processing reservation, start a browser or reach the publisher.

The original owner worker has no hosted policy hook and retains its existing
behavior. Native compatibility for an older personal ingress is confined to
the already authenticated owner mode; private members fail closed.

## Reviewer and LightMind handoff

Use the existing separately stored Studio reviewer credentials. There is no
need to create temporary third-party channels or share personal channel
sessions. Reviewer and ordinary member capabilities match. Check the demo
library, upload, correction options, processing, metadata/cover and rendered
preview. LightMind can link this account for editing and preview while keeping
its final publication action optional and capability-aware.

Public store descriptions disclose managed publication rather than suggesting
every member can post immediately. Do not certify that every publication feature
is accessible solely because the editor was tested. Both stores require truthful
access to submitted functionality: [Google review access](https://support.google.com/googleplay/android-developer/answer/15748846?hl=en),
[Apple review guidance](https://developer.apple.com/app-store/review/).
This capability design does not itself submit or guarantee public review.

## Recovery improvements

Pending Apple/Google login flows now allow one hour to finish. Provider identity
freshness, nonce/audience/signature checks, single-use state and the two-minute
PKCE receipt remain unchanged. Expired/cancelled/provider errors return to the
account screen with a safe restart message; authorization codes and provider
error text are not reflected into the URL. Passwords are cleared, and retries
start a new consent flow rather than reusing stale state.

Store preparation waits for loaded data before inferring a missing draft,
recovers a read-only stuck page once, and never blindly replays Create/Save.
Apple draft preparation first reconciles plan availability and uses the exact
approved monthly price; legacy localization remains supported. These are draft
operations, independent of billing activation and release submission.

## Validation

Integration contracts cover ordinary editing/preview, disabled platform and
music/video post routes, forged capability headers, stale broad tokens, no
backend dispatch on rejection, explicit account opt-in and global pause. Existing
isolation, quotas, idempotency and publication contracts remain in the suite.
Native/PWA runtime and release evidence is recorded separately in the release
manifest; a compile or mocked contract is not an actual social-publication test.
