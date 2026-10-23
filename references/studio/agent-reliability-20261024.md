# Studio Agent reliability qualification — 2026-10-24

Studio Agent uses the same editing pipeline and publication queue as the
composer. This repair addresses failures between task acceptance, progress
reporting and preview, without introducing a second publisher or shell agent.

## Reproduced faults and fixes

| Trigger | Previous behavior | Current behavior |
| --- | --- | --- |
| A new preparation has no burn record yet | `GET burn-subtitles` returns 404 and the entire chat response fails after accepting work | Return the durable receipt and progress; add the preview when its run produces one |
| Progress endpoint temporarily fails | Conversation refresh fails, obscuring accepted work | Preserve messages and receipt, show a translated status warning, retry reads only |
| A new publication is queued without a run ID | Status can refer to an older current output | Wait for the job's actual run before presenting output |
| User asks for progress | Planner lacks task evidence | Supply bounded observed step/receipt state; answer without submitting again |
| A second edit arrives while a separate run works | Current-output status can look idle | Check the previous preparation's own session; require completion or recovery |
| Preparation deliberately has no subtitle, logo or background change | No render exists to preview | Expose the owned source after preparation completes, without making a duplicate video |
| iOS progress read throws once | Polling loop exits | Catch failures inside the polling loop; resume reads until cancellation |

Executable turns still display deterministic settings and backend receipts,
not a model's claim that publication succeeded. Authorization, immutable message
IDs, media ownership and publication duplicate checks remain enforced.

The planner also retains supplied story/product background for metadata, not
only the quoted speech. Metadata prompts exclude statements about missing
captions/transcripts and discourage padding short clips. Japanese metadata
instructions distinguish localized place/dialogue wording from exact requested
brand names and credits. Generated copy still needs preview/review.

## Whisper runtime fallback

A recent job failed with an NVML driver/library assertion. `nvidia-smi` also
reports a mismatch on this workstation, but that warning alone does not prove
CUDA inference will fail: the live speech test succeeded with GPU Whisper.

`AutocutProcessor` now recognizes explicit driver/NVML failures from a failed
transcription attempt and makes one CPU attempt with multilingual `medium`,
or `LAZYEDIT_WHISPER_CPU_MODEL` when configured. It does not cycle through smaller
GPU models for a broken driver. Existing CUDA out-of-memory handling still
steps down through GPU models. A harmless NVML warning does not discard a
successful GPU result. An unrelated input error does not trigger CPU fallback.
CPU processing can be slower; failure is surfaced rather than retried forever.
No driver, workstation or shared GPU service restart is required.

## Verification

- 51 Node tests pass across `studio/*.test.mjs` and `hosted/*.test.mjs`, including
  the new failure reproductions, session conflict check, authorization and
  duplicate-dispatch cases.
- Seven deterministic Python tests cover runtime failure classification, one
  CPU attempt, CPU failure, unrelated errors, OOM and harmless warnings.
- PWA TypeScript check and production export pass. Android Java compilation
  and its configured unit-test Gradle task complete successfully.
- The real public Studio UI, at a 430-pixel phone viewport, uploaded a separate
  five-second approved sample, sent one prepare-only chat instruction and
  completed transcription, context correction, EN/JA/ZH translation, subtitle
  and top-right logo burn, keyframes, three metadata variants and cover.
- The corrected transcript repaired a place-name recognition error. Inspected
  frames show Japanese readings and Chinese pinyin. The preview opened through
  the app and reached browser video `readyState=4`, duration 5 seconds, no error.
- A second chat message asked for progress and received the observed completed
  state. Database checks confirm one run and zero social publication jobs for
  the sample. This is editing acceptance, not a claim of live social publication.
- The CPU error path is covered by controlled regression fixtures; the real
  media test used GPU successfully and does not prove a live CPU failure recovery.

## Deployment boundaries

The original-owner Studio adapter/PWA is promoted with
`scripts/studio/promote_agent.py` after idle checks. The owner Python backend was
gracefully reloaded in its existing pane to activate the transcription fallback.
Expo, monitors, AutoPublish Pi, shared ingress and other workspaces were preserved.

Installed native clients use the repaired server contract. The additional native
warning/polling changes are source changes for the next qualified internal build;
this task does not claim a new TestFlight or Play delivery. Shared Mac build
serialization remains required, so no unallocated Mac build was launched.

The locked reviewer workspace remains on its accepted deployment. It was not
replaced or used as the owner's test account. Hosted image rollout remains a
separate deployment step after workspace acceptance locks permit it.

Private run IDs, exact media/preview paths, screenshots and deployment receipts
are recorded in `OneTimeSync/LazyEdit/STUDIO-AGENT-RELIABILITY-20261024.md`.
