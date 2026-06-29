---
name: lazyedit-publish-workflow
description: Use when publishing videos through LazyEdit, AutoPubMonitor, AutoPublish on the lazyingart Raspberry Pi, Shipinhao, YouTube, Instagram, or LALACHAN-generated videos; covers direct CLI/API publishing, current-run reuse, one-shot settings overrides, subtitle correction prompts, Nutstore AutoPublish import, and monitoring/debugging the distributed publish workflow.
---

# LazyEdit Publish Workflow

Use this skill for normal LazyEdit publish tasks and for AI-generated videos from LALACHAN/RARACHAN that need subtitle correction, processing, and platform publishing.

## Runtime Map

- LazyEdit repo/backend: `/home/lachlan/DiskMech/Projects/lazyedit`
- Studio app: `http://127.0.0.1:18791/editor`
- LazyEdit API: `http://127.0.0.1:18787`
- Publish CLI: `scripts/lazyedit_publish.py`
- AutoPubMonitor repo: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Nutstore import folder: `/home/lachlan/Nutstore Files/AutoPublish/AutoPublish`
- Remote AutoPublish host: `ssh lachlan@lazyingart`
- Remote AutoPublish repo: `/home/lachlan/Projects/autopub`
- Remote publish API: `http://lazyingart:8081/publish`
- Remote tmux session: `autopub`

## Core Rule

Prefer the LazyEdit CLI over manual browser work. It creates normal LazyEdit jobs, so the webapp queue stays in sync.

Activate the environment first:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

## Safety Rules

- Do not publish to real platforms just to debug packaging, subtitles, or logo output. Use `--no-publish` first, inspect the generated ZIP/final MP4, then publish exactly once when the package is correct.
- Real publishes should use polished/corrected subtitles and the configured LazyEdit Studio logo unless the user explicitly asks otherwise. Verify logo settings with `curl -fsS http://127.0.0.1:18787/api/ui-settings/logo_settings | jq .`; normal logo outputs end in `_subtitles_logo.mp4`.
- For LALACHAN/RARACHAN generated videos, use the corresponding story/prompt/script as subtitle-correction and metadata context. Treat it as a reference, not a verbatim transcript: fix clear ASR errors and broken phrases without inventing unsupported dialogue.
- If correction is expected to recover missing generated-video dialogue, inspect `DATA/VIDEO_FOLDER/*_mixed_polished.md` before publish so missed or over-recovered subtitles are caught before any platform post.
- If missing-language recovery creates plain subtitle text, do not restore grammar colors with a per-video patch. Fix or use the shared `lazyedit/subtitle_tokens.py` normalization path so plain text, ruby markup, `word`/`reading` tokens, and speaker-helper rows all render through grammar-typed palette tokens.
- When copying through Nutstore, use one stable `_COMPLETED` filename and watch AutoPubMonitor panes before recopying. Avoid creating duplicate source files just to retrigger the watcher.
- Silent or nearly silent videos may produce empty transcripts and `burn=skipped`. This is acceptable when transcribe/translate/caption/keyframes are complete; continue metadata generation, cover extraction, publish queue submission, and terminal platform verification instead of waiting forever or swapping in an older video.
- AutoPublish browser uploads require a web-safe MP4 inside the ZIP. LazyEdit must package `_highlighted.mp4` as H.264/AVC (`avc1`), `yuv420p`, AAC audio, and `+faststart`. If the selected source/burn output is HEVC/H.265, AV1, or another browser-risk codec, transcode it during publish-bundle preparation before sending the ZIP.
- When the source path is already under LazyEdit `DATA/`, use `--video-id` or a non-colliding `--filename`. Do not re-upload `DATA/<stem>/<filename>` with the same filename, because the upload endpoint can truncate the source by writing over it.
- For XiaoHongShu, close hashtag suggestion popovers with Escape/blur before the final publish click. The red publish control may be inside a custom `xhs-publish-btn`, so use the AutoPublish fallback instead of hand-clicking random page coordinates.
- For Douyin, reuse an existing unpublished draft when the upload already exists. Do not use native `send_keys()` for title/description fields or the separate topic widget when debugging; the site can wedge Selenium. Use the AutoPublish JS field replacement path and keep hashtags in the description.
- For Bilibili, optional SMS verification after upload is only for completion notifications; close it and continue. If the page shows `请完成短信验证` while the upload is stuck at `0.0MB/0.0MB`, it is a hard SMS gate, not GeeTest. Click `获取验证码`, get the SMS code from the user, and do not retry upload loops without it.
- If Bilibili shows `0.0MB/0.0MB` and browser-side `preupload` returns code `601` with `您上传视频过快，请您稍作休息后再继续`, stop retrying and wait for cooldown. Repeated upload retries extend the block.
- To add a missing platform to an already-processed LazyEdit output, reuse the existing ZIP if it contains the correct rendered MP4. Re-submit the same ZIP with only the missing platform flags. Repackage only when the existing ZIP points at the wrong output.

## Setting Semantics

- `--use-current-settings` reads Studio defaults.
- One-shot flags such as `--platforms`, `--languages`, `--subtitle-lift-ratio`, and `--no-burn-subtitles` do not change Studio settings.
- Only `--persist-settings` writes CLI options back to the webapp preferences.
- `--languages` is bottom-to-top subtitle order.
- If Studio logo settings are enabled, `--no-burn-subtitles` still creates a processed logo-only output ending in `_logo.mp4` and publishes that output. Translation is skipped because subtitles are disabled.
- Use polished/corrected subtitles for real publishes and debug publishes unless the user explicitly requests original subtitles.
- Publish category defaults: personal phone/self recordings use `simplelife`; LazyingArt brand/product posts use `lazyingart`; pure music/art-track posts use `musia`; LALACHAN story videos use `lalachan`; LALACHAN character music videos use `lalamv`. Instagram has no stable per-post category/playlist in the desktop web upload flow, so AutoPublish only logs the inferred category there and uses normal captions/tags. LazyEdit metadata generation asks the model for `publish_category` (`simplelife`, `lazyingart`, `musia`, `lalachan`, or `lalamv`) and the router falls back to source-path/keyword inference. `music` is only a backwards-compatible alias for `musia`. Use `--publish-category lalamv`, `--youtube-playlist LalaMV`, or `--shipinhao-collection LalaMV` for MV overrides.
- `--no-process` reuses an already completed output. Use it when the user says "last run", "same version", or "already finished run".
- `--publication-session-id ID` targets a specific run. Omit it for the current output.

## Category Cleanup

Use platform cleanup scripts only after an inventory or dry run. They attach to
the logged-in browser sessions and are read-only until `--apply`.

Shipinhao collections:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py ensure-collection --collection LalaMV --apply'
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py ensure-collection --collection Musia --apply'
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py ensure-collection --collection 啦啦侠 --apply'
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py inventory --scrolls 5 --output /tmp/shipinhao_inventory.json'
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py move-category --category lalamv --lalamv-collection LalaMV --scrolls 5 --output /tmp/shipinhao_lalamv_plan.json'
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py move-classified --scrolls 5 --output /tmp/shipinhao_move_plan.json'
```

Apply in small batches or by exact visible title fragment:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py move --query "visible title fragment" --collection 啦啦侠 --apply'
```

Shipinhao mirrored metadata/description management:

```bash
python AutoPublish/scripts/shipinhao_mirror_manager.py export-metadata --metadata-root DATA --days 45 --output /tmp/lazyedit_shipinhao_metadata_index.json
python AutoPublish/scripts/shipinhao_mirror_manager.py export-publish-history --limit 500 --output /tmp/lazyedit_shipinhao_publish_history.json
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/shipinhao_mirror_manager.py mirror --scrolls 5 --output /tmp/shipinhao_mirror.json'
python AutoPublish/scripts/shipinhao_mirror_manager.py sync-db --db /tmp/shipinhao_management.sqlite --mirror /tmp/shipinhao_mirror.json --metadata-index /tmp/lazyedit_shipinhao_metadata_index.json --publish-history /tmp/lazyedit_shipinhao_publish_history.json --output-plan /tmp/shipinhao_description_plan.json
python AutoPublish/scripts/shipinhao_mirror_manager.py db-report --db /tmp/shipinhao_management.sqlite --limit 20
```

Use this mirror manager for existing-post control, not publication. On
2026-06-29, old date-only rows could be matched back to LazyEdit metadata, but
Shipinhao's `修改描述和封面` page only allowed modifying selected existing text
with a 20-character limit. Blank/missing descriptions could not be restored
through the visible desktop UI; the tool reports
`unsupported-description-repair` for that state and records apply attempts in
the SQLite mirror DB. Inspect every JSON plan before `--apply`.

YouTube playlists:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_y2b_videos.py move-category --category lalamv --lalamv-playlist LalaMV --scrolls 20 --output /tmp/youtube_lalamv_plan.json'
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_y2b_videos.py move-classified --scrolls 20 --output /tmp/youtube_move_plan.json'
```

Instagram:

Instagram does not have a comparable per-post category/playlist/collection
target in the current desktop web upload flow. Do not run an Instagram
category backfill. Keep using metadata category for YouTube/Shipinhao routing
and normal Instagram caption/tags.

Never bulk-apply a generated plan without inspecting the JSON. If the page is
logged out, wrong, or the visible row text is weak, stop and open the correct
management page in the browser first.

## Common Commands

Publish an already finished output:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms shipinhao,youtube,instagram \
  --no-process \
  --wait \
  --poll-seconds 10
```

Publish only YouTube and Instagram:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --platforms youtube,instagram --no-process --wait --poll-seconds 10
```

Publish only Shipinhao:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --platforms shipinhao --no-process --wait --poll-seconds 10
```

Process then publish:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --platforms youtube,instagram --wait --poll-seconds 10
```

Process/publish with lightweight guided monitoring:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -80 | tail -n 80'" \
  --wait \
  --poll-seconds 10
```

Use `--guided-monitor` when the user wants less manual supervision. It prints heartbeat progress during blocking subtitle correction, follows the local LazyEdit queue, checks the remote AutoPublish queue, and can periodically tail the Pi `autopub` tmux log. It should not restart services by itself; diagnose first, then intervene only when the queue reports failure or the logs show a clear stall.

Override languages for one run without changing Studio defaults:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --languages zh-Hant,ja,en --platforms youtube,instagram --wait
```

Create a no-subtitle video while keeping the configured Studio logo:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --no-burn-subtitles --platforms youtube,instagram --wait
```

Pure music/audio packaging should go through LazyEdit first, mirroring the
video ZIP contract. LazyEdit creates the metadata, lyrics, audio copy, YouTube
art-track MP4, manifest, original-proof ZIP, and cover candidates; AutoPublish
only consumes the ZIP with `publish_shipinhao_music=true` and/or
`publish_youtube_music=true`.

```bash
python scripts/lazyedit_music_package.py \
  --audio /path/to/song.mp3 \
  --title "Song Title" \
  --author "Musia 慕莎" \
  --language 中文 \
  --genre Pop \
  --story "Short music story for 音乐人说." \
  --lyrics-json /path/to/musia/lyrics/mixed-vocal/mul.json \
  --cover /path/to/artwork.png \
  --cover-video /path/to/related-video.mp4 \
  --cover-count 9 \
  --cover-model aginti+codex \
  --aginti-cover-count 5 \
  --codex-cover-count 4 \
  --proof /path/to/website/manifest.json \
  --source-url "https://fun.lazying.art/#song-id" \
  --output-slug song-title-music \
  --platforms shipinhao_music,youtube_music
```

The equivalent API is:

```bash
curl -fsS http://127.0.0.1:18787/api/music/package \
  -H 'Content-Type: application/json' \
  -d '{
    "audio": "/path/to/song.mp3",
    "title": "Song Title",
    "author": "Musia 慕莎",
    "language": "中文",
    "lyrics_json": "/path/to/lyrics.json",
    "cover": "/path/to/artwork.png",
    "cover_video": "/path/to/related-video.mp4",
    "cover_count": 9,
    "cover_model": "aginti+codex",
    "aginti_cover_count": 5,
    "codex_cover_count": 4,
    "source_url": "https://fun.lazying.art/#song-id",
    "slug": "song-title-music",
    "platforms": {"shipinhao_music": true, "youtube_music": true}
  }'
```

Set `--post` or JSON `"post": true` only after inspecting the package. As of
2026-06-29, the verified desktop creation route is:

```text
https://channels.weixin.qq.com/platform/post/createMusic
```

The management/sidebar route is:

```text
https://channels.weixin.qq.com/platform/post/music
```

Shipinhao currently has no verified standalone desktop `发表专辑` route. Album
(`专辑`) is handled as required metadata inside the `发表音乐` song form, and
also appears as a read-only management tab. Use AutoPublish
`pub_shipinhao_music.py` for song creation and `pub_shipinhao_zhuanji.py` for
read-only album/music tab inspection:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python pub_shipinhao_zhuanji.py'
```

The zhuanji helper saves `logs/shipinhao-zhuanji-management.json`. Do not
represent a click on `发表音乐` as final listing proof unless the management tab
or backend status shows a row.

After the account has at least one album, the music form may show only
`专辑信息 / 选择专辑 / 请选择专辑`. The publisher must switch the Vue album
component to `新建专辑` before filling `专辑名称`, cover, and intro; otherwise
`发表音乐` stays disabled. Verified on 2026-06-29: management showed two albums
and two music rows after publishing `One Sky, Three Lights` and
`アヤちゃん 光の雨`.

Do not claim `音乐人说`, `歌曲简介`, `歌曲故事`, or a video-style `声明原创`
was filled unless the live create form exposes those fields. In the verified
2026-06-29 run, the story text existed in package metadata and album intro, but
the separate `音乐人说` field was not present; `作品类型` stayed on the page
default `原创`, and original proof was uploaded through `证明文件`.

Shipinhao music rejects MP3 files below 256kbps. LazyEdit now transcodes low
bitrate MP3 inputs to a package-local `*_shipinhao_320k.mp3` copy. Verify with
`ffprobe` if a package fails to enable the submit button. Required fields filled
by AutoPublish include title, lyrics, author, singer, lyricist, composer,
producer, album name, album description, album cover, original-proof ZIP, and
the `我已阅读《视频号音乐人发表须知》` checkbox.

YouTube Music in this workflow means public YouTube Studio upload of a generated
music art-track video. LazyEdit writes `youtube_music_video_filename` and
`video_filename` to metadata, and AutoPublish `pub_y2b_music.py` uploads that
H.264/AAC MP4 with the cover thumbnail, title, description/story, lyrics, tags,
and `Musia` playlist when available. Direct YouTube Music audio upload is a
personal library feature, so do not claim it as public YouTube Music
distribution.

Music package records are durable in LazyEdit:

```bash
python scripts/lazyedit_music_records.py list --limit 20
python scripts/lazyedit_music_records.py update ID --shipinhao-item-url URL
python scripts/lazyedit_music_records.py update ID --deleted
```

When cover art is not fully prepared, pass one curated cover plus
`--cover-video` and `--cover-count 9`; LazyEdit will extract enough frame covers
to fill the nine-background-image package. If AgInTi generates better covers,
pass those as repeated `--cover` arguments instead.

## LALACHAN / AI-Generated Video

If a generated video should go through the normal import path, copy it to Nutstore with a stable `_COMPLETED` name:

```bash
cp -f /home/lachlan/ProjectsLFS/LALACHAN/Videos/VIDEO.mp4 \
  "/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/VIDEO_COMPLETED.mp4"
```

Then watch AutoPubMonitor and find the imported LazyEdit video id:

```bash
tmux capture-pane -pt autopub-monitor:0.1 -S -100 | tail -n 100
tmux capture-pane -pt autopub-monitor:0.2 -S -100 | tail -n 100
curl -fsS http://127.0.0.1:18787/api/videos | jq '.videos[:20] | map({id,title,created_at,file_path})'
```

For direct upload with correction and metadata prompt:

```bash
python scripts/lazyedit_publish.py \
  --video /home/lachlan/ProjectsLFS/LALACHAN/Videos/VIDEO.mp4 \
  --title TITLE_COMPLETED \
  --use-current-settings \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/PROMPT.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --wait \
  --poll-seconds 10
```

Use the LALACHAN story/prompt/script as both subtitle-correction background and metadata background. For subtitle correction, treat the script as a reference, not a verbatim source. Use a human middle path: do not over-edit, and do not stay too conservative when the ASR is obviously abnormal, broken, or mismatched with the context. Read neighboring lines, check whether the sentence makes sense, compare it with the audio/Whisper text and the story context, then infer the most likely intended wording. Fix recognition errors, names, objects, and broken phrases while preserving timing and line structure where possible. The final corrected subtitles do not need to be identical to the script if the audio or generated video differs, and they should not invent unsupported content.

If the prompt needs extra guardrails, create a temporary context wrapper in `temp/`, pass it as `--prompt-file`, then delete it after the run. Do not commit temporary prompt wrappers, generated ZIPs, or runtime media.

If the user requests no rerun, use `--no-process`.

## Monitoring

Local LazyEdit queue:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq '.jobs[:8]'
```

Remote AutoPublish queue:

```bash
curl -fsS http://lazyingart:8081/publish/queue | jq '.jobs[:8]'
```

Remote browser automation:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -120 | tail -n 120'
```

AutoPubMonitor import/session:

```bash
tmux capture-pane -pt autopub-monitor:0.0 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.1 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.2 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.3 -S -120 | tail -n 120
```

## Shipinhao Notes

- Shipinhao may require a WeChat QR/login email. Keep monitoring after the user scans.
- Keep the long login wait behavior. It is intentional and useful when the user is away or misses the first QR.
- The automation should wait for upload completion, cover readiness, save draft, then publish.
- Current UI may not expose short title or cover upload; skip those if absent.
- Expected successful log includes `Successfully published on ShiPinHao.`

## AutoPubMonitor Notes

- Nutstore files copied into `/home/lachlan/Nutstore Files/AutoPublish/AutoPublish` are synced/imported by AutoPubMonitor.
- If a file is renamed while monitor is active, check the tmux panes and queue file before assuming it imported.
- If LazyEdit is down, AutoPubMonitor wrapper must preserve nonzero exit codes so queued files are not silently dropped.

## Handoff Checks

Before final response, verify:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq '.jobs[:8] | map({id,video_id,status,platforms,remote_status,remote_job_id,error})'
curl -fsS http://lazyingart:8081/publish/queue | jq '.jobs[:8] | map({id,status,platforms,filename,error,updated_at})'
```

Report the LazyEdit job id, remote job id, platforms, status, and whether processing was reused or rerun.

## Verified Run: 2026-06-03 Typhoon Ping Pong Shark

Request:

- Publish `typhoon_pingpong_shark_duanpian_4x3_15s_2026_06_03_22_46_26_COMPLETED` as before.
- Use generated-video subtitle correction from the LALACHAN prompt/script.

Method:

```bash
python scripts/lazyedit_publish.py \
  --video-id 348 \
  --use-current-settings \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-03-typhoon-pingpong-shark-duanpian-15s-4x3-budget200.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --wait \
  --poll-seconds 10
```

What happened:

- LazyEdit had already imported the Nutstore file as `video_id=348`.
- AI subtitle correction saved polished subtitles before processing.
- Processing completed: transcribe, translate, burn, metadata, cover.
- Shipinhao blocked on login until the user scanned the emailed QR.
- The QR expired once; the existing long wait refreshed it and sent a new email.
- After login, Shipinhao published, then Instagram published, then YouTube published.

Tools used:

- `scripts/lazyedit_publish.py` for API/CLI orchestration.
- `curl` + `jq` for LazyEdit and remote AutoPublish queue checks.
- `ssh lachlan@lazyingart` and `tmux capture-pane -pt autopub:0` for remote browser automation logs.
- `tmux capture-pane -pt autopub-monitor:*` for Nutstore/import checks.
- `rg` on the Pi after installing `ripgrep` for faster code/log searches.

Final result:

- LazyEdit job `148`
- Remote job `job-1780500057985-7`
- Platforms `shipinhao`, `youtube`, `instagram`
- Status `done`

## Verified Run: 2026-06-06 Firefly Cave

Request:

- Copy `/home/lachlan/ProjectsLFS/LALACHAN/Videos/firefly_cave_cicada_rain_4x3_15s.mp4` to Nutstore.
- Use `/home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-06-firefly-cave-cicada-rain-duanpian-15s.md` as subtitle/metadata context.
- Publish to `shipinhao`, `youtube`, and `instagram`.

Method:

```bash
cp -f /home/lachlan/ProjectsLFS/LALACHAN/Videos/firefly_cave_cicada_rain_4x3_15s.mp4 \
  "/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/firefly_cave_cicada_rain_4x3_15s_COMPLETED.mp4"

python scripts/lazyedit_publish.py \
  --video-id 352 \
  --use-current-settings \
  --prompt-file temp/firefly_cave_publish_context.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'" \
  --wait \
  --poll-seconds 10 \
  --process-timeout 3600 \
  --publish-timeout 7200
```

What happened:

- AutoPubMonitor imported the Nutstore file as `video_id=352`.
- AI correction saved polished subtitles first.
- Processing completed translation, burn, metadata, and cover.
- Shipinhao required QR login, recovered after login, saved draft, waited for cover readiness, and published.
- Instagram published after crop/Next; YouTube uploaded, filled title/description from metadata, and published.

Final result:

- LazyEdit job `154`
- Remote job `job-1780723994544-13`
- Platforms `shipinhao`, `youtube`, `instagram`
- Status `done`
