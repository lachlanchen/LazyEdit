# LazyEdit Studio remote access

The private owner pilot is at **https://edit.lazying.art**. `studio.lazying.art`
remains the landing page. One configured account, `lachlanchen`; no signup.
This is not a public multi-tenant service. The account password is in the
owner's Nutstore `Share/LazyEdit/studio-account.json`, never in this repository.

## Boundaries

```
HTTPS → isolated Studio Caddy → header-normalizing facade
      → LazyEdge token gateway → dedicated reverse SSH
      → LazyEdge worker guard → Studio account adapter → existing LazyEdit
```

Video storage, account database, processing, models, and the existing publishing
queue stay on the workstation. The edge streams bytes with backpressure; it
stores no uploaded video. The Studio tunnel uses its own key, Unix identity,
loopback listener and systemd units. LazyTunnel's existing tunnels and agents
are not used as Studio transport and were not restarted.

The exact LazyEdge transport contract is `/studio/bridge`. The facade replaces
caller-supplied internal headers. The worker requires LazyEdge's injected
upstream credential, then separately authenticates the owner cookie or scoped
user bearer. It validates path, method, object ownership and operation scope.
Only the owner browser can access legacy library/settings; linked clients can
access videos they upload under the owner, not arbitrary existing media IDs.
Machine credentials do not grant owner access.

- Browser: Secure, HttpOnly, SameSite=Strict session cookie, 12-hour expiry;
  state changes require the exact HTTPS Origin.
- API: opaque 15-minute access token; hashed, rotating 30-day refresh token;
  revoke invalidates the grant, including preview requests.
- Link: 10-minute device code, 5-second poll interval, explicit browser approval.
  Publishing is excluded from default linking scopes.
- No credentials in query parameters, browser localStorage or service-worker
  caches. localStorage retains only resumable upload IDs, never access tokens.
- Account revocation prevents new calls. It does not cancel accepted jobs,
  delete media or remove existing social posts.

## Upload and editing

Use the web uploader or `scripts/studio/client.py`. Web uploads are 8 MiB chunks;
reselecting the same file resumes its saved server offset. Native API clients
must calculate SHA-256 and supply it. Maximum video is 10 GiB; sessions expire
after 24 hours; partial chunks roll back and uncompleted parts are cleaned hourly.
At least 2 GiB free reserve is required. The edge transport's per-request limit
is 256 MiB; use chunks for large videos rather than raising that limit.

Completed files are probed as video before registering in the **same** LazyEdit
library. `videoId` is the real database ID. Existing editing/correction and
publication behavior remains in the original backend, not a second pipeline.
Processing uses asynchronous acceptance. Idempotency keys are mandatory for
linked-client processing and publishing; an uncertain submission remains
pending reconciliation instead of being replayed under a new key.

CLI examples (run with the LazyEdit environment's `python`):

```sh
python scripts/studio/client.py login --account-file /private/studio-account.json
python scripts/studio/client.py account
python scripts/studio/client.py upload /path/to/video.mp4
python scripts/studio/client.py process VIDEO_ID \
  --request /private/process-request.json --idempotency-key UNIQUE_EDIT_KEY
python scripts/studio/client.py status VIDEO_ID
python scripts/studio/client.py artifact VIDEO_ID
```

Example process request:

```json
{
  "translationLanguages": ["en", "ja", "zh-Hant"],
  "burnSubtitles": true,
  "usePolishedSubtitles": true,
  "autoCorrectSubtitles": true,
  "autoCorrectPrompt": "Read the full conversation. Correct likely recognition errors using the supplied context and sound; preserve actual wording. Do not rewrite to match a script.",
  "notes": "Audience-facing story context only. Do not put our editing instructions or workflow in metadata."
}
```

Omit optional rendering settings to inherit Studio defaults. One-shot changes
must not persist global preferences. Native v1 edits the current output;
historical publication-session selection remains in the owner web UI.
Do not publish until the finished render, captions, metadata, cover and named
platform destinations have been reviewed. Queue acceptance is not publication
success. The original distributed queue and platform receipts remain authoritative.

## PWA and native testing

On iPhone: open the HTTPS site in Safari, Share → Add to Home Screen.
On Android: open in Chrome and choose Install/Add to Home Screen.
The PWA requires network access; it does not cache private media offline.

`mobile/` contains separate Capacitor 8.5.1 iOS/Android test clients for this
HTTPS Studio. Bundle/package: `art.lazying.lazyedit`. These are an online private
beta client; they reuse the hosted editor and owner browser login, and contain
no embedded account or machine token. They are distinct from Expo Go and from
LightMind's account-link integration. A successful APK/IPA build is not a
TestFlight/Play release. Exact provider state is recorded in `store/`.

## Deployment and rollback

Use the reviewed LazyEdge manifest under `deploy/studio/`. Resolve private
machine paths from the Nutstore handoff. Scripts under `scripts/studio/` prepare
private state, immutable release archives, icons, review desktop and signed
mobile builds. They do not publish social content. `remote_admin.py` reads the
existing edge admin credential privately; it never puts a password in argv.

Keep source, immutable release digest and role-specific bindings together.
`promote_local.py` prepares local unit files; explicitly reload/restart only the
three `lazyedit-studio-*` services as needed. Never restart the original
`lazyedit` tmux service as a deployment shortcut. Before restoring a previous
worker release, stop only the Studio worker and restore its previous unit and
configuration together. Account/upload state is outside releases.

The first edge had no HTTP site or NAT rules. The LazyEdge greenfield redirect
helper creates only Studio's four digest-tagged 80/443 redirects. A separate
filter blocks direct access to high Caddy ports; SSH and LazyTunnel traffic is
unchanged. Do not run the migration renderer that expects four *existing*
redirects against this empty initial state. Preserve the owner-only initial
rollback script and rules snapshot. All service units are enabled; actual reboot
recovery has not been tested, to avoid disrupting other services.

Run `node --test studio/test.mjs`; verify both LazyEdge doctors, anonymous denials,
refresh/revoke, CSRF, cross-owner access, resumable bytes/hash, range playback,
and tunnel disconnect/recovery. See the private acceptance record for exact IDs.
No social content was published to test the deployment.

Operator details: [operations](operations.md), [native beta builds](mobile-testing.md),
[provider receipts](../../store/studio/release.json). Long uploads can refresh
their CLI access token between chunks. Keep one process per CLI state file.

Linked-client publication validates the reviewed render at submission, but
does not yet lock the legacy queue to an immutable historical snapshot. Do not
edit/reprocess that video until its pending publication has completed.
