# Invite workspaces on the existing Studio / LazyEdge route

Deployed 2026-10-03 at **https://edit.lazying.art/accounts**. Registration is
invite-only. The original account stays at https://edit.lazying.art with its
existing password, data and Pi publication workflow. No DNS, certificate,
firewall, LazyTunnel service, owner backend or Pi change was needed.

## Routing and account separation

```text
Existing Caddy/TLS → Studio facade → pinned LazyEdge edge guard
  → existing reverse SSH → local guard → Studio ingress on 18798
      ├─ /accounts and authenticated invited sessions → Docker gateway 18980
      │    └─ selected user's private workspace / database / desktop
      └─ original owner requests → original Studio adapter / backend 18787
```

`hosted/ingress.mjs` verifies the original worker transport capability before
selecting a destination. The gateway requires a separate ingress credential.
Public callers cannot inject internal path/identity/capability headers. An
invited session selects a workspace only after central authentication; expired
sessions fail closed and never fall through to the original owner. Unready or
suspended workspaces cannot receive Studio requests. Explicit workspace API
calls require that workspace's scoped token; password/token/device bootstrap
endpoints authenticate through the existing Studio implementation.

Each user gets the same built image and their own writable `/state` volume,
PostgreSQL database, settings, media, queue, browser profiles and lightweight
Openbox desktop. No Pi profiles or accounts are imported. Raw backend,
publisher, VNC, CDP and database ports remain private. The only host-published
Docker port is the authenticated gateway on `127.0.0.1:18980`.

The central cookie is `__Host-hosted`; the workspace cookie is
`__Host-studio`. Both are Secure, HttpOnly, SameSite=Strict with 12-hour sessions.
Sign-out clears both. One browser session selects one workspace on this domain;
sign out before switching to the original owner. Shared-domain operation gives
separate data/profiles/credentials, not separate browser origins against hostile
tenants. The optional subdomain mode and browser/network hardening remain the
appropriate expansion path before public signup.

## User flow and API linking

1. Redeem an invitation at `/accounts`; choose a username and password.
2. Wait for automatic provisioning, then choose **Open Studio**. The 60-second
   entry ticket is bound to the workspace and can be used once.
3. Open **Platform accounts**, select a platform, and sign in in the private
   desktop. QR scans and verification codes use this user's browser profiles.
4. Upload, correct subtitles with context, process, preview and publish through
   the usual controls. Each workspace serializes its own publish queue.

The account endpoint `GET /accounts/account` returns:

```json
{"workspace":"https://edit.lazying.art",
 "apiBase":"https://edit.lazying.art/workspaces/<workspace-id>"}
```

LightMind/CLI clients must use `apiBase` for **all** endpoints, including login,
refresh, uploads, artifact/status requests and approved publication. The
original owner's base remains `https://edit.lazying.art`.

```bash
python scripts/studio/client.py \
  --server 'https://edit.lazying.art/workspaces/<workspace-id>' \
  --state /private/path/client-session.json \
  login --account-file /private/path/account.json
```

The private account JSON supplies `username` and `password`; do not pass either
on the command line or commit them. Login posts `mode=token` to `/auth/login`,
then uses scoped access/refresh tokens. Device approval uses `/connect`: first
sign into the invited account at `/accounts`, open Studio, then approve the
code under Account · Connect. Do not approve its code in the original account.
API IDs alone grant no access. Processing/publication preserve the existing
idempotency, review and approval contracts.

## Desktop transport and Caddy

Pinned LazyEdge 0.4 implements HTTP/SSE, not WebSocket forwarding. The optional
`hosted/lazyedge-runtime.mjs` wrapper uses that package's existing server,
manifest, token-store and binding APIs, and adds `desktop-upgrade.mjs`.
HTTP policy is unchanged. Upgrades accept only GET `/studio/bridge` representing
`/platforms/desktop/websockify`, exact Host/Origin, a valid handshake and the
existing separate edge/relay/upstream capabilities. Two live upgrade slots and
a 15-minute idle timeout bound the desktop transport. The cell then verifies
its browser session before forwarding to loopback noVNC. No raw VNC exposure,
second tunnel, shared LazyEdge package change or other gateway upgrade occurred.

Caddy needed `SAMEORIGIN` framing only on `/platforms/desktop/*` for the embedded
desktop. Other Studio pages retain `DENY`. Studio-only zstd/gzip reduces traffic
on HuanaYun's limited connection. The source example is
[edit.caddy.example](../deploy/hosted/edit.caddy.example); apply its settings to
this site only. Never replace the shared Caddyfile with it. Other hosts,
certificates, listeners, admin endpoint, NAT and LazyTunnel routes stay intact.

## Private state and operator actions

- Docker control/registry/bootstrap: `~/.local/share/lazyedit-hosted`.
- Existing Studio account/transport/units/receipts: `~/.config/lazyedit-studio`.
- Owner credentials, unchanged: Nutstore `Share/LazyEdit/studio-account.json`.
- New private operator handoff: Nutstore
  `Share/LazyEdit/HOSTED-STUDIO-20261003.md`.
- Private one-use invitation: Nutstore
  `Share/LazyEdit/hosted-invitation.json`.

The operator explicitly reused only selected AI-provider fields for this
trusted pilot in a private template. No full owner `.env`, SMTP, platform
cookies or profiles were copied. Use per-user provider credentials/budgets for
wider invitations; never configure the owner's email as every user's recipient.
Provider files are copied at first provisioning and require an idle workspace
restart when changed. Existing Pi delivery keeps its existing secrets and flow.

```bash
node hosted/admin.mjs status "$HOME/.local/share/lazyedit-hosted"
node hosted/admin.mjs invite "$HOME/.local/share/lazyedit-hosted"
docker compose -f "$HOME/.local/share/lazyedit-hosted/compose.json" ps
```

An invitation expires after 72 hours and can be redeemed once. Default capacity
is three workspaces, each with 8 GiB/two CPUs plus a 512 MiB database. The
controller polls every 30 seconds and claims a five-minute provisioning lease.
Failed provisioning is inspectable/retryable without creating another identity.
The gateway has no Docker socket; only the private networkless provisioner
uses fixed, operator-controlled templates. The CPU build is tested on this
workstation; the 1 GiB edge does not run containers or hold media.

## Updates and rollback

Build images once; users share immutable layers. Record image IDs and drain a
workspace before updating its image. Keep databases and named volumes.
`docker compose down -v` is deletion, not an upgrade command.

`scripts/studio/promote_hosted.py --state STATE_DIR` stages immutable code and
backs up the existing worker JSON plus worker/guard units; it does not activate
them. Future Studio updates must retain the hosted ingress entry point. Do not
silently use the old owner-only promotion recipe and remove the router.
The private receipt lists exact previous/release/rollback paths. Restart only
the two Studio adapter units after staging; preserve the tunnel, original
backend and Pi. On the edge, back up facade/edge units and Caddy before a
site-scoped change, validate, and reload through the existing private admin
listener rather than restarting shared ingress.

Rollback restores previous worker JSON/units, edge/facade units and the Studio
Caddy changes, then verifies owner login/API. Never overwrite account databases
with files from a prior code release. If another project has since edited the
shared Caddyfile, revert only this site's changes, not their later edits.

Media uses one canonical `/state/data` store: completed uploads are renamed,
not copied; local package handoff references the existing ZIP; per-job extracted
scratch is removed after completion/failure. Source, processed render and ZIP
are distinct required artifacts. Retention is not an indiscriminate deletion
of original media, corrected subtitles or prior runs. Console logs are bounded.

## Acceptance and practical limits

Twenty Node tests pass, including same-host selection, expired-session denial,
scoped API password login, cross-workspace denial and guarded desktop relay.
Public HTTPS verified owner login/library, anonymous API denial, one-use invite
registration, automatic provisioning, isolated empty library, resumable upload
with matching SHA-256 and exactly one canonical MP4, and authenticated WSS/RFB
through the complete LazyEdge chain. Anonymous desktop upgrades were denied.
Chromium rendered account portal, Studio and embedded desktop without page
errors. Compression reduced the tested frontend transfer from about 2.2 MB to
0.56 MB. Evidence is in the ignored deployment validation directory.

The disposable account, containers, volumes and temporary credentials were
removed after acceptance; account gateway/provisioner remain deployed. No
social posts were submitted. The original backend's PID/start time and queue
remain intact; no Pi deployment occurred. Fresh platform logins and real
provider/social submissions still require each invited user's own credentials
and normal workflow validation. This is an invite pilot, with CPU Whisper and
no billing, password recovery, storage quotas or global GPU scheduler. See the
[full Docker guide](2026-10-03-hosted-multiuser-docker.md) for existing limits.
