# LazyEdit Publication Methods, Tools, and Recovery Notes

Date: 2026-06-06

This note records the working publication method used for recent LazyEdit jobs and the recovery path used when a stale transcription failure blocks an otherwise valid publish.

## Primary Tools

- `scripts/lazyedit_publish.py`: preferred CLI for upload/process/publish. It keeps the Studio queue in sync.
- LazyEdit API: `http://127.0.0.1:18787`.
- Studio UI: `http://127.0.0.1:18791/editor`.
- Remote AutoPublish API: `http://lazyingart:8081/publish/queue`.
- Remote browser automation logs: `ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'`.
- Local queue checks: `curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq`.
- DB inspection/repair: `psql "${LAZYEDIT_DATABASE_URL:-${DATABASE_URL:-dbname=lazyedit_db}}"`.

## Context-Aware Publish Flow

For an existing video with no usable subtitles, create a temporary context file under `temp/` and run:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --prompt-file temp/context.md \
  --no-correct-subtitles \
  --steps keyframes,caption,transcribe,polish,translate,burn,metadata_zh,metadata_en,cover \
  --platforms shipinhao,youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'" \
  --wait \
  --poll-seconds 10 \
  --process-timeout 3600 \
  --publish-timeout 7200
```

Use `--no-correct-subtitles` here because there may be no transcript yet. The prompt is still used by the polish and metadata stages.

## Subtitle Review

Before publish, inspect:

```bash
sed -n '1,180p' DATA/VIDEO_FOLDER/*_mixed_polished.md
rg -n "bad term|broken term" DATA/VIDEO_FOLDER/*_mixed_polished.*
```

Keep corrections human and moderate: fix clear ASR errors and context mismatches, keep timing/structure, and avoid unsupported invention. If a corrected filler word is Chinese, normalize the JSON `lang` to `zh` so later translation does not treat it as stale `ja` or `en`.

## Stale Transcription Failure Recovery

If a duplicate Whisper run writes a newer failed `mixed` transcription row after valid subtitle files already exist, the process status may report `transcribe:error` even though translation/burn/metadata are usable.

Check:

```bash
ps -eo pid,ppid,cmd | rg 'vad_lang_subtitle|HandBrakeCLI|scripts/lazyedit_publish.py'
psql "${LAZYEDIT_DATABASE_URL:-${DATABASE_URL:-dbname=lazyedit_db}}" -P pager=off -c \
  "SELECT id, language_code, status, output_json_path, error, created_at
   FROM transcriptions WHERE video_id=VIDEO_ID ORDER BY id DESC LIMIT 8;"
```

If the worker is clearly a duplicate, stop only that PID. Then insert a fresh completed `mixed` row pointing at the verified corrected subtitle files:

```bash
psql "${LAZYEDIT_DATABASE_URL:-${DATABASE_URL:-dbname=lazyedit_db}}" -v ON_ERROR_STOP=1 -c "
INSERT INTO transcriptions (
  video_id, language_code, status,
  output_json_path, output_srt_path, output_md_path,
  error, publication_session_id
) VALUES (
  VIDEO_ID, 'mixed', 'completed',
  '/abs/path/to/VIDEO_compatible_mixed_polished.json',
  '/abs/path/to/VIDEO_compatible_mixed_polished.srt',
  '/abs/path/to/VIDEO_compatible_mixed_polished.md',
  NULL, NULL
);"
```

This repairs status ordering only; it does not rewrite subtitles.

## Cover and Publish-Only Finish

If downstream outputs are complete but cover is missing:

```bash
curl -m 180 -fsS -H 'Content-Type: application/json' \
  -d '{"lang":"zh"}' \
  http://127.0.0.1:18787/api/videos/VIDEO_ID/cover | jq .
```

Then publish without rerunning processing:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --no-correct-subtitles \
  --no-process \
  --platforms shipinhao,youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'" \
  --wait \
  --poll-seconds 10
```

## Recent Verified Example

`IMG_4285_2026_06_06_17_40_11_COMPLETED` used this method:

- Context: building staff gave away graduated students' leftover items; user received a badminton racket and asked a junior to fill the registration/application form.
- Corrected subtitles included `你看这个`, `嗯`, `呃...`, and `现在我领了一个拍子`.
- LazyEdit job: `157`.
- Remote AutoPublish job: `job-1780745384131-16`.
- Platforms: `shipinhao`, `youtube`, `instagram`.
- Final status: `done`.
