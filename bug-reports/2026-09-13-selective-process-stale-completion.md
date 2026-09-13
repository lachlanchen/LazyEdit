# Selective Process Can Report Previous Completion

## Observed

On a video with completed metadata, a CLI request using `--steps
metadata_zh,metadata_en,metadata_ja --no-publish --wait` returned immediately
with the previous completed timestamps. The asynchronous backend generated the
new metadata a few seconds later. This reproduced on two selective reruns.

## Cause and Risk

`scripts/lazyedit_publish.py:wait_for_process` captures a baseline for error
handling but `requested_process_ready` accepts unchanged completed statuses.
An immediate subsequent publish could package stale metadata.

## Recovery Used

Waited for fresh completion timestamps for all three requested metadata
languages, read their contents, and only then submitted publication. Video and
subtitle rendering were reused, not rerun.

## Proposed Test and Fix

Add a deterministic polling test with an old done snapshot, then working, then
fresh done. Require evidence that the requested run has completed, preferably a
backend run ID; do not treat an unchanged cached result as new completion. Keep
intentional cache reuse and legitimately skipped steps supported.

This report contains no private video, personal context, or credentials.
