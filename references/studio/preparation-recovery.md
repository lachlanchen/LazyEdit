# Recovering an interrupted editing preparation

The linked/native facade previously retained a preparation's idempotency receipt
while the legacy backend retained only in-memory pipeline progress. Replacing a
worker could lose the running task, leave completed frame/caption artifacts, and
return `pipeline=null`. Replaying its accepted key returned the old `started`
receipt without restarting work. This is a provider lifecycle failure, not a
client authorization failure or publication consent.

## Client contract

Keep the exact accepted `video_id`, source receipt/hash, original Idempotency-Key,
request body and account-scoped API base. Do not upload again, create a new key,
switch to an owner/Pi worker or retry a social publication.

Preparation acceptance in recovery-capable deployments includes `operation_id`.
The private cell persists that original intent, immutable resolved preparation
settings, source SHA, accepted response and recovery count in
`studio_preparations` beside its existing protected account/intent database.
It is not a new publication queue or a second copy of the media.

First read authenticated `/v1/studio/capabilities`; use this extension only if
`preparationRecovery=true`. Relative paths below belong to the same scoped
workspace API base, with the same private linked-app grant:

```text
GET /v1/studio/preparations/<operation_id>
POST /v1/studio/preparations/<operation_id>/resume
Content-Type: application/json
Body: {}
```

The read requires `jobs.read` and `media.read`. Resume requires `edit.submit` and
`media.read`, plus original operation/media ownership. No replacement settings,
publication destination, arbitrary source path or owner fallback is accepted.
Browser requests retain their same-origin rule.

Read states are `working`, `done`, `error`, `interrupted`, or
`reconciliation_required`. Only a known accepted request from an earlier worker
instance with no active pipeline can be `interrupted` and recoverable. Unknown
initial/recovery dispatches remain held for reconciliation, not an automatic
retry. A currently running/done preparation returns its state without dispatch.
Raw `started` acceptance remains distinct from completion.

Resume verifies the existing source SHA and private realpath, checks that no
social job exists even if failed, rejects a superseding preparation, and claims
recovery atomically. It retains the original publication-session identity and
only skips completed checkpoints whose timestamps belong to that operation.
The backend exposes its operation identity and per-step checkpoint times.
Recovery does not reserve another processing run or change the original intent
receipt. Text still follows the normal correction, translation, render and
metadata pipeline. Publication requires separate explicit approval/capability.

After completion, read the usual authenticated render/review endpoints and
verify the rendered SHA/Range response. Continue read-only polling with bounded
backoff through transient HTTP failures. Credentials and artifacts stay private.

## Legacy reconciliation and acceptance ownership

Older deployed cells lack this API. The operator helper
`scripts/studio/reconcile_preparation.mjs` runs inside the exact private cell:

```text
node scripts/studio/reconcile_preparation.mjs \
  --video-id ID --key ORIGINAL_KEY --brief PRIVATE_ORIGINAL_BRIEF_JSON
```

This is a dry run. Add `--apply` only after the original request fingerprint,
source/ownership hash, accepted receipt, missing live task and no social job are
verified. It supports the existing `lightmind-capture.v1` current-output preset;
it cannot migrate arbitrary historical/unknown requests. Legacy cells did not
store resolved settings, so migration uses the original brief/preset and checks
the existing configured logo. It records that limitation instead of pretending
an original resolved snapshot existed. Future operations persist the snapshot
before dispatch. Repeated helper calls cannot silently dispatch again.

The helper can be copied with its small source modules into a private state
folder without changing live service binaries or restarting the worker. Do not
replace a reviewer's worker while another client owns qualification. An
operator-owned `acceptance.lock` in that workspace's protected bootstrap folder
blocks `promote_cells.py` before any worker is replaced. Remove it only after the
owning qualification finishes. Current LightMind qualification retains this
lock; do not release it merely because Studio preparation finished.

## Qualification and rollout

Contract tests simulate worker replacement with the same private SQLite file,
media and grant. They check original receipt/key preservation, one recovery
dispatch, completed-stage reuse, unchanged processing reservation, source
tampering, other accounts/scopes, rejected replacement options, prior failed
social jobs and uncertain dispatch holds. Python checks cover checkpoint times
and the promotion acceptance lock.

On 2026-10-04, the original harmless reviewer fixture was recovered in its live
private cell and all editing stages completed. Scoped HTTP probes verified the
source/render hashes, cover/review, metadata and Range responses, with zero
publication jobs and an unchanged worker start time. Per-operation identities,
receipts and the client handoff remain in ignored private evidence.

The recovery API source is qualified but **not yet promoted to the existing
reviewer cell**: the no-restart acceptance boundary takes precedence. That cell
continues to serve its normal completed review/preview endpoints; its scoped
capability reply is the deployment truth. Coordinate an idle promotion after
LightMind finishes acceptance, rather than advertising staged endpoints as live.
