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

## Final publication validation

- LazyEdit video: `566` (source `715371867.mp4`, 50.93 seconds, 544x960).
- Rebuilt using corrected subtitles; top-to-bottom rows EN / JA / ZH-Hant / FR,
  pronunciation guides, zero lift, existing top-right logo, no background fill.
- Saved only zero lift to the existing Studio layout/defaults; other preferences
  were preserved. The ZIP video hash matched the visually inspected master.
- Initial local job `409`, remote `job-1789299805700-1`: Douyin, Shipinhao and
  Instagram succeeded; YouTube stopped on an embedded-JavaScript syntax error.
  The historical failed combined-job status is retained, not rewritten as done.
- YouTube-only recovery job `410`, remote `job-1789300832722-1`: **done**.
  The publisher resumed the same private draft, completed checks, and verified
  the public receipt. No successful platform was submitted twice.
- Instagram receipt/caption verification:
  <https://www.instagram.com/lazyingart/reel/DdOf4qMurd-/>
- YouTube public receipt:
  <https://youtube.com/shorts/zMi-4Si_7_8>
- Douyin's stale management list showed the correct 51-second post after a
  reload, marked published at 19:45 on 2026-09-13. Shipinhao matched its new
  description in management after saving a draft and waiting for cover readiness.

AutoPublish fix `c37b0b7` corrects raw JavaScript strings and adds exact-title
open-draft reuse. Check-flow/metadata tests: 19 local passes; 17 check-flow
tests also passed on the Pi. The GitHub push succeeded locally, but the Pi could
not resolve GitHub and has only an `origin` remote (not the older `github`
alias). Deployment used an SSH-transferred Git bundle containing the same
commit, then `git fetch <bundle> main` and `git merge --ff-only FETCH_HEAD`.
The idle Tornado server autoreloaded; no browser or profile was restarted.
