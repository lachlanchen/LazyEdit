# LightMind → LazyEdit owner return packet

Base URL: **https://edit.lazying.art**, replacing the proposed
`studioagent.lazying.art`. Landing remains `studio.lazying.art`.
Read [Studio reference](../../references/studio/README.md) and
[OpenAPI](../../studio/openapi.json). This is one owner's private workspace;
there is no public registration or production multi-user isolation claim.

## Linking

Recommended: POST `/auth/device` with `client_name` and scopes. Defaults omit
`publication.publish`. Display `user_code`; open the returned
`verification_uri` in the system browser. The user logs into Studio, enters the
code, reviews scopes and approves. Poll POST `/auth/token` with
`grant_type=urn:ietf:params:oauth:grant-type:device_code` and `device_code` every
5 seconds. `428 authorization_pending` means keep waiting; `429 slow_down`
means back off; `400 expired_token` means start a new user-initiated link.

Owner password alternative: POST `/auth/login` with `username`, `password`,
`mode: token`, `client_name`, `scopes`. Do not keep the password after exchange.
Use OS secure storage for the access/refresh credentials; never ship a shared
service token. Access lasts 15 minutes; refresh lasts 30 days and rotates on
use (old access and refresh credentials stop working). Store both new tokens
atomically; serialize refresh calls. Uncertain refresh response requires
re-linking, not repeated use of the old refresh token.

GET `/v1/studio/account` confirms issuer, owner subject, scopes and limits.
POST `/auth/revoke` with `grant_id` unlinks. Revocation does not cancel already
accepted work or delete retained media; state this in LightMind's unlink UI.

## Upload → edit → preview

1. Hash the original capture. POST `/v1/studio/uploads` with `filename`, `size`,
   `sha256` and optional `title`.
2. PUT `/v1/studio/upload-part?uploadId=…`, raw bytes, `Upload-Offset` matching
   the server offset. Prefer 8 MiB chunks. GET `/v1/studio/upload?uploadId=…`
   after interruption; resend only from the recorded offset.
3. POST `/v1/studio/upload-complete` with `uploadId`. The server probes the
   complete video, verifies the hash and returns `lazyedit_media_receipt.v1`.
   Save `videoId`, `sha256`, `byteLength`, media URLs and your capture identity.
   Repeating completion returns the same receipt, not a duplicate video.
4. POST `/api/videos/{videoId}/process`, `Idempotency-Key` required. Pass context
   in `autoCorrectPrompt`/`polish_notes` and audience-facing context in `notes`.
   `async` is forced true. The current render is used; native v1 cannot select
   historical run IDs. Do not persist Studio preferences.
5. Poll GET `/api/videos/{videoId}/process-status`. Preview using the returned
   authenticated `/media/…` URLs. The player must attach Authorization and
   support Range; never put bearer tokens in the URL. Browser preview uses the
   owner's secure cookie. Fetch-to-blob is suitable for small preview files;
   native large-file playback needs authenticated resource requests.
6. GET `/v1/studio/artifact?videoId=…` after a completed burn for render hash,
   size, preview URL and rendering configuration.

The legacy `PUT /upload-stream?filename=…` alias accepts declared Content-Length
and X-Content-SHA256, up to the transport request limit. Prefer resumable upload.

## Publication requires a separate user decision

`publication.publish` scope is not granted by default device linking. The
native client must explicitly request it, and the user approves that scope.
Then POST `/api/videos/{id}/publish` with a persistent unique Idempotency-Key:

```json
{
  "platforms": ["youtube"],
  "reviewApproved": true,
  "reviewedVideoId": 123,
  "reviewedSha256": "64-lowercase-hex-of-reviewed-render",
  "confirmation": "PUBLISH_REVIEWED_MEDIA",
  "productionConfirmation": "PUBLISH_REVIEWED_MEDIA_PRODUCTION"
}
```

Review the output, captions, metadata, cover and actual destination accounts in
Studio first. Capture does not imply publication. Processing does not imply
publication. The response is the existing queue receipt, not platform success.
GET `/api/autopublish/queue` returns only owned video jobs for linked clients.
The durable idempotency record is written before dispatch. A pending/uncertain
response is a reconciliation case; never use a new key to force a duplicate.

The production app-suite LightMind bridge previously stripped the confirmation
fields and relied on one operator bearer. **Do not simply change its base URL.**
Migrate to per-user rotating credentials and forward the explicit review
fields, reviewed digest and Idempotency-Key. Current native support is current
video output only, not music packages or historical sessions. Cancel/per-job
provider URLs remain existing Studio UI operations; no new cancellation API is
claimed. Do not call the coordinator's proposed `/v1/studio/jobs` routes; they
were a proposal, not the final contract.

## Deployment/evidence and limits

Own LazyEdge gateway + guard, separate SSH identity/listener, local account DB
and media. Existing LazyTunnel 23001–23007 listeners remained running. HuanaYun
has 2 Mbps: budget at least 6m40s per 100 MB through a saturated link. It is not a
video-storage or model host. PWA assets are served from the workstation too.

Validated: browser sign-in/upload, mobile-width layout, exact upload hash,
resume offset, duplicate completion, video registration, keyframe processing,
authenticated range previews, anonymous denials, invalid/expired/revoked tokens,
CSRF, object ownership, idempotency conflict, and tunnel 503/recovery. Test
videos were not socially published. Physical iPhone and actual store provider
receipts are separate evidence; see `store/` for current status. No claim of
LightMind code integration is made by this server deployment.

Private account and runtime handoff: Nutstore `Share/LazyEdit`. No secrets go
in this packet or LightMind source. Native iOS/Android packages have their own
`art.lazying.lazyedit` identity and do not reuse another project's app record.

## Current-output publication caveat

The digest check is at submission, not an immutable snapshot across the legacy
queue. Native publish options may change category only; rendering settings are
derived from the reviewed burn configuration. Do not reprocess/edit a video
while its reviewed publication is queued. Strict immutable queued-artifact
enforcement remains future backend work. Current account integration and
uploads are ready; do not claim LightMind-side integration or social publication
tests were performed by this deployment.
