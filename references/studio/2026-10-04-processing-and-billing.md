# Private Studio processing and billing

The owner chose monthly prices USD 2.99, 14.99 and **29.90**. The last replaces
the unavailable requested Apple price 29.89. App downloads remain USD 0.99.
Suggested conservative benefits are 10, 60 and 150 source-video minutes per
UTC calendar month, respectively. These are prepared product terms, not a
claim that subscription purchases are active.

## Accounting

`hosted/plans.mjs` defines the prices and allowances. The hosted gateway derives
the allowance from a provider-verified account entitlement, never client JSON
or headers. While purchases are disabled, invited pilot members receive 10
minutes/month; the administrator is exempt. The original personal backend and
Pi do not install this meter.

The private cell uses `hosted/processing.mjs` and its existing protected SQLite
database. It probes the actual source with ffprobe, validates DATA containment
including symlinks, then atomically reserves the duration before upstream
dispatch. Durations are rounded up to milliseconds, not whole minutes.
Concurrent requests cannot exceed the allowance. Counts reset at midnight UTC
on the first of each month; unused time does not roll over.

A full pipeline request counts its source duration once. Its internal steps do
not traverse the meter again. A separately requested transcription, correction,
translation, render or metadata/frame regeneration counts another run. Upload,
preview, editing saved text, package assembly and reuse of completed output do
not consume processing minutes. Packaging existing music assets is separate
from video processing; no new music-generation entitlement is promised.

For publication, the private read-only `processing-quote` endpoint and the
actual queued publisher use the same `_publish_requires_processing` predicate
in `app.py`. The quote creates no session or job. New runs and requests for new
correction/metadata context require processing; a ready saved run or an existing
queue entry can be reused. The cell serializes submission for each video.

Idempotency retries preserve an accepted result and charge once. A definite
4xx rejection releases its reservation; an uncertain timeout/5xx keeps it held
for operator reconciliation. Do not bypass an uncertain submission with a new
key. A quota rejection is known to precede dispatch, so the linked-app intent
can safely be retried after upgrade or reset. Processing that actually starts
and subsequently fails consumes its requested source minutes.

Authenticated `GET /v1/studio/usage` reports limit, used and remaining minutes
and the UTC reset timestamp. This is a private workspace API. The legacy owner
worker returns no hosted usage feature.

## Store preparation and activation

`scripts/studio/store_products.py` reconciles only LazyEdit's own product group
and exact product IDs. All three approved prices exist in Apple's USA list;
finding a price point is separate from saving a price schedule. Never describe
an inactive draft as a purchasable subscription. Google and Apple subscription
configuration, sandbox purchase/restore/refund tests and full reviewer access
must be qualified before setting the billing activation gates.

The USD 0.99 download-to-subscription discount is not implemented. It needs a
store-supported, verified redemption design; a download receipt alone does not
silently create a credit. Provider signing keys, purchase proofs, credentials,
private reviewer access and rollback state remain outside Git.

## Verification

The contract suite covers private source containment, exhaustion, definite vs
ambiguous failure, replay, ready-run reuse and gateway header forgery. A linked
application can retry the same intent after a pre-dispatch quota rejection,
but cannot start or charge an accepted request twice. Focused Python checks
exercise the actual publish readiness functions without loading GPU models.
