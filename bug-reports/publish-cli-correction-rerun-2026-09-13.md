# Correction and rerun readiness in the publish CLI

Observed during a preview-only publish preparation; no bad preview was submitted.

## Failures

1. `--correct-subtitles` first transcribed and saved polished subtitles, but the
   default process list then ran Whisper again. Nondeterministic segmentation
   changed the raw cue count while the polished file kept the earlier timeline.
2. On a completed video's asynchronous rerun, `--wait` immediately accepted the
   previous run's durable `done` rows before the new rendering started.

## Fixes

- Treat successful CLI correction as authoritative input for the subsequent
  default processing/queue phase, just like reviewed subtitle import. Skip the
  second transcription. Explicit `--steps transcribe,...` remains an opt-in.
- Compare requested-step status markers against the pre-run baseline before
  reporting completion. All requested steps must have fresh completion evidence.
- Regression coverage: `python -m pytest tests/test_lazyedit_publish_cli.py -q`.
  All 12 tests passed after the changes.
- Only the CLI and its tests changed; no backend or AutoPublish restart required.

## ASR review caveat

No timing check can certify recognition accuracy. In this street-juice video,
the segmented ASR misclassified Japanese narration and hallucinated repetitive
text over machinery noise; the first context correction also invented a
Chinese introduction. Independent whole-file large-v2/large-v3 transcription
plus the user's fruit-name context provided a better review baseline. The
reviewed SRT was imported through the existing subtitle-import endpoint, and
translation, rendering, metadata and queuing stayed in the normal pipeline.
Brief English lines were marked as English in both source/polished JSON.

Do not translate a broken baseline or force a context note into spoken dialogue.
Keep context factual, preserve ordinary cue timing, and distinguish deliberate
audio-based resegmentation from text-only correction. Review public metadata
for unsupported speaker attributions, prices, locations and workflow prose.
