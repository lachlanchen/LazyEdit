# Operating the private Studio pilot

Read README.md and the LightMind handoff before extending the routes. The pilot
has one owner. It is not a multi-user hosted editing business or a replacement
for LazyTunnel. Public URL: https://edit.lazying.art.

## Source and runtime

The live checkout resolves to /home/lachlan/ProjectsLFS/lazyedit (lowercase).
Do not deploy from the separate uppercase LazyEdit checkout without reconciling
its branch. The existing backend remains on 18787; Expo development remains
on 18791. No changes to their startup are required by this adapter.

The account, machine credentials, release paths, private receipts and runtime
ownership are under the operator's private Nutstore Share/LazyEdit handoff and
~/.config/lazyedit-studio. No passwords, tokens or signing material belong in Git.

The adapter runs under Node 22.21 with built-in SQLite. Runtime database,
incoming uploads and credentials live outside checksum-named releases.
Account creation is explicit; prepare_runtime.py creates the first owner if
absent, and never rotates a password on rerun. There is no public signup.

## Update the workstation adapter

1. Read git status, the active queue, memory and current service ownership.
2. Run Node 22: `node --test studio/test.mjs studio/session.test.mjs studio/media.test.mjs`.
3. For UI changes, export from app/:

   ```sh
   LAZYEDIT_REMOTE_STUDIO=1 EXPO_PUBLIC_REMOTE_STUDIO=1 \
     EXPO_PUBLIC_API_URL=https://edit.lazying.art \
     node node_modules/expo/bin/cli export --platform web --max-workers 2 \
       --output-dir ../temp/studio-deploy/webdist
   ```

4. Run `python scripts/studio/promote_local.py` using the LazyEdit conda
   interpreter. It creates an immutable release and retargets only Studio's
   service units. Record the new archive SHA-256 before activation.
5. `systemctl --user daemon-reload`, then restart
   `lazyedit-studio-worker.service`. Do not restart the original backend.
6. Check anonymous /api/videos returns 401, /v1/studio/health returns 200,
   browser sign-in, upload resume and linked-client status. Roll back the unit
   and worker.json together if checks fail. Never roll back the account DB by
   replacing it with an old release directory.

prepare_runtime.py is initial provisioning, not the normal update command. It
requires the pinned LazyEdge tarball and verified adjacent dependency, creates
role-specific bindings, and renders candidates; it does not deploy edge changes.
Do not rerun initial bootstrap/firewall scripts against an already-live edge.
The deployment manifest is committed; machine-specific rendered scripts and
prior-state rollback remain in the private operational handoff.

For adapter-only changes, prefer `python scripts/studio/promote_worker.py`.
It keeps the current web assets and only stages adapter modules, worker config
and worker unit. It does not bootstrap accounts or rewrite guard/tunnel units.
Run `node --test studio/test.mjs studio/*.test.mjs` before staging; then activate
with daemon-reload and restart **only** `lazyedit-studio-worker`.

## Edge update and ingress

Use the same reviewed archive/digest, extract into a new edge release, then
retarget only lazystudio-facade. Keep previous unit/config snapshots. The
LazyEdge gateway release is separate and must not be changed for UI updates.

Caddy's Studio reverse_proxy block MUST overwrite these request headers:

```caddy
header_up Host edit.lazying.art
header_up X-Studio-Peer {remote_host}
```

The loopback-only facade requires that peer to be an IP address and replaces
all transport/auth/path identity headers. Public client-supplied X-Forwarded-For
or X-Studio-Client must never select the rate-limit identity. Without this,
every client looks like loopback and failed logins can lock out other devices.
Validate before `caddy reload` at the private admin address. The dedicated
Caddy unit has no ExecReload; use Caddy's own reload command, not a broad restart.

The owned ingress service maintains four digest-tagged NAT redirects plus an
owned direct-high-port filter. Do not flush nftables, replace another table,
write iptables-save, or modify the separate LazyTunnel SSH configuration.
Service enablement and recovery were tested; a full cloud/workstation reboot
was not performed.

The public-facade machine token is time limited (initially 365 days). Rotate
before expiry using the pinned LazyEdge CLI, update the private token file and
restart only the facade. Owner access/refresh tokens are separate.

## Operational limits and failure handling

The hosted UI's bounded GET scheduler and error normalization are required for
iOS/Android as well as PWA operation. Do not remove them or enable eager video
list preloads on the remote app. See [React #31 incident and regression checks](2026-09-20-ios-react31.md).

- HuanaYun's 2 Mbps is the media bottleneck: 100 MB takes at least ~6m40s.
  Chunks improve recovery, not bandwidth. The edge never stores full videos.
- CLI state is private, with atomic token replacement and automatic refresh
  when an upload outlives access-token expiry. One process per --state file;
  different clients must not race the same rotating refresh token.
- Browser sessions last 12 hours. If expired, sign in again and reselect the
  same file to resume the saved server offset.
- Keep the same idempotency key after a lost processing/publication response.
  A pending intent requires reconciliation with the existing queue. Do not
  delete its row or generate a new key to force submission.
- Native publication checks the completed render's digest at submission and
  copies its render options instead of accepting new render settings. This
  version does NOT freeze a historical immutable publication session across
  the entire legacy queue. Do not edit/reprocess the same video while its
  reviewed publication is pending; strict queued-digest enforcement remains a
  backend extension, not a guarantee of this adapter.
- Current native API uses current video output. Music, historical runs,
  cancellation and provider management are not new v1 API contracts.
- The remote home hides generation/remix tools whose private provider APIs
  are not exposed. Local Studio retains those tools.
- Revocation blocks future requests; accepted jobs, files and social posts
  have separate lifecycles. There is no promise of automatic deletion.

## Browser and native QA

Use one dedicated review service via systemd-run --user --collect and
scripts/studio/launch_review.sh. The current noVNC URL/port/profile and exact
service name live in the private runtime note. Stop only that owned unit after
screenshots. The store browser is shared with EchoMind and remains untouched.

Raw one-tab CDP is available through scripts/studio/cdp.py. It raises browser
JavaScript errors and avoids connecting Playwright to every stale shared tab.
Read the actual dialog, await its transition, and confirm the resulting state.
A click alone is not proof of a provider mutation.

Initial iOS simulator launch timed out (-1001); relaunch displayed the real
login page. Both native clients now include Capacitor server.errorPath with a
bundled Reconnect screen. These hosted-WebView clients are private online beta
clients, not claimed production App Store-ready or offline apps. Capacitor's
server.url is documented for live-reload rather than production; a production
release should bundle the frontend and retain explicit native account linking.

References: [Capacitor configuration](https://capacitorjs.com/docs/config),
[Apple build uploads](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds).
