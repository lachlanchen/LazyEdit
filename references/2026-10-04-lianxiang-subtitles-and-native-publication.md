# 莲香西域: shared subtitle and native publication fixes

## Intended publication

Video 604 is `2026-10-04_12-29-32_COMPLETED.MOV` (28.875 seconds,
3840×2160). The owner had lunch at 莲香西域 and filmed staff stirring
noodles. The initial ASR birthday text was rejected by the owner. Confirmed speech is “你们这个很厉害啊”
and “谢谢你们”. No birthday content belongs in the subtitles or metadata.

Use the existing Studio logo at top-right, portrait blur fill with about 40%
bottom space, zero subtitle lift, four reserved rows. Subtitle order from top
to bottom: English, Japanese, Traditional Chinese, Korean. Korean replaces the
previous French bottom row for this request; persisted website defaults are
unchanged. Publish only Shipinhao, Instagram, YouTube and Douyin.

## Root causes and fixes

1. Whisper marked a noisy final cue English. Context correction replaced its
   text with Chinese but retained the recognition language tag. English's
   native-text lock then rejected a valid translation. The translator now
   excludes Han-only cues with stale Latin-language tags from the native lock.
   Actual English, mixed speech and numeric cues still stay locked.
2. Visual context was being turned into the unspoken caption “拌面”. Polishing
   instructions now distinguish background from verified dialogue. A confirmed
   hallucinated cue keeps its timestamps with empty text; translation skips
   empty corrected cues, so context cannot refill them. Only the two owner-confirmed speech cues remain in translations; all other
   rejected cues keep empty text and their original timestamps for audit. Correction used the normal API, not edits
   to the generated transcript files.
3. During QA of the rejected birthday transcript, Korean output used romanization above Hanja, combined Hanja and
   Hangul endings into a single display word, or hid an ending in the reading.
   `hanja_dictionary.normalize_selected_restorations` fixes the format of roots
   already selected by the model. Pure Hanja uses the original Hangul reading.
   A dictionary-confirmed selected root and exact unchanged ending are split;
   local `koroman` provides the ending’s romanization. It never chooses another
   Han spelling or rewrites the translation. The final corrected transcript has one natural restored root: 감사 → 感謝,
   with 감사 ruby and separate 합니다 / hamnida. Never force a restoration where
   the natural translation uses native words. The existing single bounded model
   review still checks contextual homophones and unresolved invalid output.
4. The original owner adapter omitted `capabilities`; Android consequently hid
   Publish despite authenticated publication scopes. The live adapter now
   returns capabilities derived from those scopes. Android's source also uses
   its authenticated, account-scoped legacy fallback when the field is absent;
   explicit false still disables publishing. Private member policy stays intact.
5. Metadata prompt grounding now rejects invented geography based on output
   language, unconfirmed celebration ownership, invented chronology/actions and
   unnecessarily long descriptions. Metadata was regenerated through the normal
   generator after the owner clarified the exact speech.
6. Native duplicate protection formerly blocked every failed attempt. A fresh
   request can now follow a proven local preparation failure only: known error,
   finished failed row, and explicit null dispatch artifacts/remote identifiers.
   Missing fields, uncertain dispatch, active jobs and existing posts still block.

## Normal system workflow and recovery

- First request went through the authenticated `/v1/studio/videos/604/plan` and
  `/submit` native composer used by iOS/Android. Stable intent was saved before
  dispatch. Job 444 failed during translation; no ZIP or remote submission existed.
- Recover the same run 109 using the authenticated full-editor correction and
  preparation APIs; reuse its source/keyframes and cached translation responses.
  Inspect corrected source, annotations and final render before publication.
- For the prepared run, use native composer `mode=reuse`, `sessionID=109`, review
  its plan, then submit once with a new saved idempotency key. Reuse does not
  transcribe, polish, translate or reburn the verified output.
- Do not replay a new key after an unknown result. Query the existing submission
  and queue. Never treat browser clicks or queue acceptance as completed posts.

## Deployment and tests

`backport_owner_composer.py` stages only the original owner adapter’s permission
responses and composer module from an immutable pinned release. It preserves
hosted ingress, account storage, credentials, browser profiles and private cells.
Activate only the owner adapter at an idle boundary. The owner backend received
an idle-boundary activation of the shared Python fixes. Docker reviewer and owner
workspace start timestamps remain unchanged; no Pi or reviewer worker was restarted.

Development runtime uses Tornado autoreload: do not edit imported Python modules
while preparing a render. It can stop the render and the existing recovery marks
that burn failed. Finish changes first, then resume the same run at a known idle
boundary. Never interrupt a remote publication merely to activate source changes.

The final focused Python suite passes 83 tests (annotation/dictionary, language
routing, and owner adapter compatibility). Four native composer tests pass,
including real HTTP submission/idempotency and account isolation. Android
`compileDebugJavaWithJavac` passes. The portable Docker requirements already
include `koroman`; no new service or dependency is required for root formatting.
Current App Store/Play review binaries and submissions were preserved; the
permission API compatibility fix works with the current Android build.

Private request/response evidence is in the ignored `temp/publication-604/`.
Credentials remain in the protected Studio account file, never in Git or this note.

## Final publication receipts

- Local job: **445**, video **604**, run **109**.
- Remote job: **`job-1791099134561-4`**. Submitted exactly once from the native
  composer after inspection. Job 444 never reached dispatch and did not post.
- Master: `DATA/2026-10-04_12-29-32_COMPLETED/publications/session_109/2026-10-04_12-29-32_COMPLETED_session_109_portrait_subtitles_logo.mp4`.
  Verified 1080×1920, 28.885 seconds, audio present. SHA-256 of the MP4 inside
  the ZIP matches this inspected master. Silence-frame and thanks-frame checks
  show no invented captions or overlapping pronunciation rows.
- Douyin: accepted submission and matching title found in management. The first
  two uploads failed; the existing publisher automatically reopened the failed
  unpublished draft and recovered on its third bounded attempt. No manual post,
  new job, browser restart or AutoPublish code change was needed.
- Shipinhao: description and short title filled, cover generation finished,
  draft saved, and matching description verified in management.
- Instagram: Original crop confirmed before submission; saved caption verified
  on the newest profile post, https://www.instagram.com/lazyingart/reel/DeEHuY6OyQt/.
- YouTube: platform checks completed with no issues; explicit published dialog
  confirmed https://youtube.com/shorts/gB7f0pRRLtw. SimpleLife playlist selected.

All four publishers completed through the same serial AutoPublish job. The
remote queue reports `done` at **2026-10-04 15:44:03**, with no error; the LazyEdit
queue also reports `done` and `remote_status=done`. No manual social publish
clicks or whole-job resubmission were used. Queue terminal status was verified
separately from the individual publisher receipts.

The shared corrections are committed as `b88270b`; native owner compatibility
and safe preparation retries as `66708d1`. These source fixes apply to the normal
pipeline, rather than per-video transcript or metadata file replacement.

The active Codex publishing skill and canonical
`ProjectsLFS/LazySkills/skills/lazyedit-publish-workflow` now link a focused
context-correction/native-recovery note. Other agents can follow the same rules
without copying this video's dialogue or private credentials.
