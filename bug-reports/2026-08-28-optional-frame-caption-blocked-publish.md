# Optional frame caption blocked a completed publish

## Symptom

A normal LALACHAN publish completed transcription, subtitle correction,
translation, metadata, keyframes, cover generation, portrait blur-fill,
subtitle burn, and logo overlay. The auxiliary frame-caption backend returned
no output files, leaving `caption:error`. LazyEdit then reported
`ready_for_publish:false` and the serial publish worker attempted the failing
caption step again.

## Expected behavior

Frame captions are visual metadata enrichment. They should improve metadata
when available, but a caption backend failure must not block publication when
the transcript, creator context, metadata, keyframes, cover, and requested
processed video are complete.

## Resolution

- Removed `caption` from the hard publication readiness gates.
- Removed `caption` from the serial publish worker's mandatory recovery steps.
- Removed `caption` from the CLI's default process steps; callers can still
  request it explicitly with `--steps caption,...`.
- Added regression coverage for a completed video with `caption:error`.

The caption status remains visible for diagnostics and explicit caption runs.
