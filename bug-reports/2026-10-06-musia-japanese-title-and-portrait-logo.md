# Japanese Release Titles and Portrait Logo Sizing

## Observed

Musia release: `楓の向こうで · Beyond the Maples`.
LazyEdit video 607, local publication job 448, remote job
`job-1791281504171-7`, 2026-10-06.

1. The no-publish metadata generator first substituted a Chinese translation
   for the Japanese release title. After explicit exact-title context, the EN
   generator still appended a genre suffix. The suffix was removed in the EN
   artifact as a narrowly documented recovery; generated descriptions were kept.
2. `app.py::_simplify_metadata_payload` simplified Japanese `楓` to Chinese `枫`
   when packaging the otherwise correct ZH metadata title.
3. Remote AutoPublish `china_platform_metadata`/`sanitize_china_platform_text`
   then logged this transformation:

   `枫の向こうで  Beyond the Maples` -> `枫的向 Beyond the Maples`.

   This is not a meaningful translation of the Japanese title. The known proper
   Chinese display title is `枫叶彼端`. The EN nested metadata preserved the
   canonical Japanese title, but the primary title used by Instagram had already
   passed through the Chinese simplifier.
4. Studio's saved logo height of 0.15 covered the song title in the 2160x3840
   native portrait player recording. A one-shot 0.028-height top-right logo
   fixed that overlap without changing Studio preferences. Burn 874 was reviewed.

## Expected

- Preserve the canonical release title as a proper name, independent of the
  language of the surrounding description. Do not simplify Japanese kanji.
- Where a live platform actually disallows kana, prefer an explicitly provided
  localized title, e.g. `枫叶彼端 · Beyond the Maples`, rather than a destructive
  character-filter pseudo-translation. Keep canonical and localized title fields.
- Show the final platform-specific transformed title at the no-publish preview
  stage, not only after dispatch.
- Allow CLI one-shot logo sizing and inspect against recording safe areas.
  A scale appropriate for plain footage may cover UI text in a player recording.

## Evidence and Boundaries

- Package: `DATA/aya-canada-beyond-the-maples-ja-portrait-4k/publish/aya-canada-beyond-the-maples-ja-portrait-4k.zip`.
- Reviewed final rendered SHA-256:
  `d82aac3d417ce947e5f51c348d3bc101c2b787fd00f237548e6570e23d28e93e`.
- Musia handoff: `handoff/lazyedit/aya-canada-beyond-the-maples/README.md`.
- The music package uses corrected Japanese lyric text, not Chinese translations.
- Do not blindly rerun publication to fix a title. Inventory current posts and
  edit in place where supported; avoid duplicate uploads. Do not restart another
  project's publishing browser or shared worker.

These are observed metadata/layout defects, not claims of login or platform
publication failure. Platform outcomes must be checked separately.

## Additional Live Results

The initial video job failed at Douyin upload before posting. The page visibly
showed `上传失败，重新上传`, after reporting 2%, 0.7/41.9 MB, 12.8 KB/s and about
55 minutes remaining. Retry 1 also timed out in
`DouyinPublisher._resume_unpublished_draft_if_present` at `_click_first`.
No root cause for the network upload failure is established. Recovery isolates
the other three platforms in local job 449 / remote `job-1791281836107-9`, and
restarts only Douyin in remote `job-1791281868420-10`.

Job 449 completed Shipinhao, Instagram and YouTube successfully. The isolated
Douyin retry used a malformed multipart request without ZIP bytes or
`reuse_existing=true`, which the old handler saved over the archive. AutoPublish
commit `69de891` fixes validation before replacement, reports per-platform
outcomes and improves draft/upload diagnostics. It was deployed only with an
idle queue. The corrected raw-archive retry is `job-1791282667698-1`; no other
platform is being replayed. The malformed request is an operator/API-contract
failure, not evidence of another Douyin upload failure.

Douyin-only job `job-1791282667698-1` completed at 18:39:52 after one bounded
upload retry. Publish receipt and management row matched; the row displayed
`审核中` on a separate read-only check. This is a successful submission, not
proof that moderation has finished. No duplicate posts were needed. Follow-up
AutoPublish `c56930e` also verifies extracted member CRCs and covers the HTTP
retry contract in tests.

Shipinhao Music item 44 / remote `job-1791281606306-8` did publish successfully:
the management snapshot contains the exact Japanese release title and `已上架`.
The package and form used the correct 36 Japanese lyric lines, square cover,
full MP3 and successfully uploaded proof ZIP. However, the uploader logged:

`Optional Shipinhao music option not selected (语言=日语)` with aliases
`日语`, `日文`, `日本語`, `Japanese`, reason `option-not-found`, scope `语言`.

The final form state retained `普通话`. The audio is unequivocally Japanese.
This proves a selection mismatch, not that the live site has no Japanese
option; inspect the actual menu and portal behavior before claiming that.
Prefer a correctly supported Japanese value or an explicitly reported `其他`
fallback over silently retaining Mandarin. Do not re-upload the already-listed
song to debug this; use an edit route if available.
