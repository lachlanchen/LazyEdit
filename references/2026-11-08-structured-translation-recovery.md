# Recover malformed structured translations

A Shibuya travel clip stopped before rendering because one French model response
contained the requested JSON schema instead of translation data. It was valid
JSON, so the request layer cached it; pipeline retries repeatedly loaded the same
invalid response. A later English annotation retained a leading space in the
surface (` my`) but omitted that space in its display word (`my`).

The structured-request layer now validates both cached and fresh responses
against the supplied schema. A bad cached response is ignored; a fresh invalid
response follows the existing bounded retry/fallback path and is never cached.
Validation messages identify the field/rule without logging private text.
Portable hosted dependencies include jsonschema, already present in the owner
conda environment. Existing domain checks still enforce exact subtitle timing,
text coverage, and pronunciation requirements.

English display normalization now preserves the exact validated surface when
only surrounding whitespace or letter case differs. It still rejects substituted
words, missing letters, missing punctuation, and invalid Han restoration.

Regression checks cover schema echoes, wrong nested types, replacing an invalid
cache, reusing a valid cache, bounded failure without cache, and attached-space
English tokens. No publication occurs while preparation has an error. Resume
only the failed preparation steps and reuse the reviewed output for dispatch.

The normal translation editor also needs to invalidate old render annotations
when text changes in any language. Previously it did so only for Japanese,
allowing English/French tokens to display previous text after an edit. Clear the
old tokens/ruby fields for the edited cue, preserve its timestamps and other
cues, and let the renderer derive fresh pronunciation/tokens from the edited
text. Validate this through the normal translation endpoint and a final render;
do not rewrite generated JSON files manually.

## Lost dispatch acknowledgment

The Pi accepted the verified package, but the owner's HTTP request timed out
during large-package acceptance, before the queue acknowledgment arrived. The
Pi acceptance path performs synchronous archive storage/validation; queue timestamps
place the delay before queue insertion. The native job continued; the
local job had incorrectly been marked failed. Never resend solely because the
HTTP response was lost.

Dispatch transport exceptions now preserve a running `dispatch_unknown` intent.
Queue reconciliation adopts only one receipt with the same filename/platforms,
created during this local attempt or within five minutes of its last observation.
Older posts and ambiguous candidates are not adopted. The remote job ID is saved
immediately, including while it is still running. Legacy read-timeout failures
can be reconciled under the same checks. No retry or second upload is performed.
This is bounded recovery for the existing single-owner queue, not a replacement
for a future end-to-end immutable dispatch-token protocol.

## Verified completion

The reviewed 45-second portrait master was published to Shipinhao, Instagram,
YouTube and Douyin. The first remote run completed the first three platforms but
failed Douyin media transfer before final submission. The Douyin-only recovery
reused the identical archive and used the existing optional relay for exact media
hosts observed in this upload. Native management subsequently confirmed the
correct title, 00:45 duration, current publication time, and `已发布` status.

Douyin's listing took several minutes to show the accepted post. The existing
bounded verification loop refreshed the stale listing and confirmed it; no second
final submission was made. A submit acknowledgment alone was never reported as
publication. The original browser command/profile was restored after the queue
became idle; the relay, SSH forwards and observer were stopped, and their loopback
listeners were verified closed. Other platform posts were not repeated.
