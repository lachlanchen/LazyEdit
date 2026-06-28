# Shipinhao Music Upload, Logo, And Subtitle Publish Handoff

Date: 2026-06-28

Scope of this note: Shipinhao music research, LazyEdit logo/subtitle behavior,
and the AutoPublish music handoff contract. The first pass was static research
only. A later code pass added the LazyEdit logo-only processing path and the
AutoPublish music ZIP/publisher entry point. The live Shipinhao desktop music
route still needs a `test=true` browser verification before a real music submit.

## What Was Confirmed

The supplied screenshots show a Shipinhao `发表音乐` flow. The visible fields are:

- `+ 添加音乐`
- `歌曲名称`
- `歌词内容`
- `声明原创`
- `歌曲曲风`
- `歌曲语言`
- `作者信息`
- `歌曲背景图片(9张)`
- `音乐人说`
- agreement checkbox for `微信视频号音乐服务平台使用协议`
- final `完成` button

Public references also indicate that WeChat Channels supports music/audio
publishing. Some public articles distinguish `音乐` from `音频`: desktop
Channels Assistant has been described as using content management / audio
management / publish audio, while mobile screenshots show direct music
publishing. Because the current live desktop route has not been test-submitted
yet, the exact automatable desktop URL still needs verification with
`test=true`.

Useful public references from this research pass:

- Tencent Cloud community article: `https://cloud.tencent.com/developer/news/1144917`
- Tencent Cloud community article about audio publishing: `https://cloud.tencent.com/developer/news/1102633`
- Sohu article with mobile `发表音乐` steps: `https://www.sohu.com/a/704647694_121046697`

## Current AutoPublish State

AutoPublish implements Shipinhao video publishing and now has a separate
Shipinhao music entry point. Video and music are intentionally separate routes.

Relevant files:

- `AutoPublish/app.py`
- `AutoPublish/pub_shipinhao.py`
- `AutoPublish/pub_shipinhao_music.py`
- `AutoPublish/login_shipinhao.py`
- `AutoPublish/utils.py`
- `AutoPublish/scripts/package_shipinhao_music.py`

Current publish job flow:

1. `/publish` accepts flags such as `publish_shipinhao`,
   `publish_shipinhao_music`, `publish_y2b`, and `publish_instagram`.
2. `_process_publish_job()` extracts the ZIP into `transcription_data`.
3. It reads `{stem}_metadata.json`.
4. It expects video metadata fields such as `video_filename` and
   `cover_filename`.
5. If `publish_shipinhao=true`, it creates `ShiPinHaoPublisher(...)` on port
   `5006`.
6. `ShiPinHaoPublisher` navigates to
   `https://channels.weixin.qq.com/platform/post/create` and fills the video
   post form.

The QR-login email path is already reusable. `ShiPinHaoLogin.check_and_act()`
uses `utils.SendMail`, and `SendMail` creates an Apple-Watch-friendly inline QR
PNG using `QRCodeProcessor.build_watch_friendly_png()`. A music publisher should
reuse this path rather than building a second email mechanism.

## LazyEdit Music Package Contract

LazyEdit now owns the music package step, mirroring the video publish ZIP flow.
Use this path for future Musia/LALACHAN handoffs instead of asking
AutoPublish to assemble the metadata itself.

Implemented LazyEdit additions:

- `lazyedit/music_publish.py`
- `scripts/lazyedit_music_package.py`
- `POST /api/music/package`

The package contains:

- the audio file;
- `{slug}_metadata.json` using the AutoPublish music metadata contract;
- `{slug}_lyrics.txt`;
- `{slug}_manifest.json`;
- up to nine cover candidates under `covers/`.

If a `--cover-video` is supplied, LazyEdit extracts enough frame covers to reach
`--cover-count` (default `9`). This lets a calling agent provide one curated
artwork image and let LazyEdit derive the remaining candidates from the video.
Later, AgInTi-generated images can simply be passed as repeated `--cover`
arguments; the ZIP format is unchanged.

Example:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
python scripts/lazyedit_music_package.py \
  --audio /home/lachlan/ProjectsLFS/Musia/website/assets/audio/one-sky-three-lights-mixed.mp3 \
  --title "One Sky, Three Lights" \
  --author "Musia 慕莎" \
  --language 中文 \
  --genre Pop \
  --story "Musia original mixed-language song with English, Mandarin pinyin, and Japanese romaji vocals, shown with trilingual lyric display on Fun Lazying Art." \
  --lyrics-json /home/lachlan/ProjectsLFS/Musia/website/data/songs/one-sky-three-lights-mixed/lyrics/mixed-vocal/mul.json \
  --cover /home/lachlan/ProjectsLFS/Musia/recorded_videos/one-sky-three-lights/one-sky-three-lights-mixed-en-ja-zh-portrait-4k-2160x3840-thumb-24s.png \
  --cover-video /home/lachlan/ProjectsLFS/Musia/recorded_videos/one-sky-three-lights/one-sky-three-lights-mixed-en-ja-zh-portrait-4k-2160x3840.mp4 \
  --cover-count 9 \
  --output-slug one-sky-three-lights-mixed-music
```

The tested output path was:

```text
/home/lachlan/DiskMech/Projects/lazyedit/DATA/music_publish/one-sky-three-lights-mixed-music/one-sky-three-lights-mixed-music.zip
```

API equivalent:

```bash
curl -fsS http://127.0.0.1:18787/api/music/package \
  -H 'Content-Type: application/json' \
  -d '{
    "audio": "/path/to/song.mp3",
    "title": "Song Title",
    "author": "Musia 慕莎",
    "language": "中文",
    "lyrics_json": "/path/to/lyrics.json",
    "cover": "/path/to/cover.png",
    "cover_video": "/path/to/video.mp4",
    "cover_count": 9,
    "slug": "song-title-music"
  }'
```

Set `"post": true` only when the package has been inspected and the target
platform route is known to work.

## Implemented AutoPublish Music Contract

Do not overload `publish_shipinhao` for music. Use the explicit platform flag
`publish_shipinhao_music=true` so a music upload cannot accidentally enter the
video publish route.

Implemented additions:

- `AutoPublish/pub_shipinhao_music.py`
- `publish_shipinhao_music` request flag in `AutoPublish/app.py`
- `shipinhao_music` platform label in the queue status
- optional `ignore_shipinhao_music` ignore file
- `AutoPublish/scripts/package_shipinhao_music.py`

Supported package metadata contract:

```json
{
  "music_filename": "song.mp3",
  "audio_filename": "song.wav",
  "title": "Song title",
  "song_title": "Song title",
  "lyrics": "Full lyrics...",
  "song_lyrics": "Full lyrics...",
  "music_story": "Short story shown in music comments, max 300 chars.",
  "cover_filename": "cover.jpg",
  "background_image_filenames": ["cover.jpg", "image2.jpg"],
  "author": "Artist name",
  "genre": "Pop",
  "language": "中文",
  "declare_original": false
}
```

The publisher should accept either `music_filename` or `audio_filename`, with
`music_filename` taking priority. Keep video metadata support separate.

Implementation behavior:

1. Start or reuse Chromium on port `5006`, using the same profile/session logic
   as the video publisher.
2. Run `ShiPinHaoLogin.check_and_act()` first so QR email behavior stays exactly
   like video publishing.
3. After login, navigate to the verified music/audio publish URL. Do not assume
   the video URL works for music.
4. In `test=true` mode, fill fields and stop before `完成`.
5. Upload the audio file through the real `input[type=file]` element.
6. Upload up to nine background images if the desktop UI exposes the image file
   inputs.
7. Fill `歌曲名称`, `歌词内容`, `音乐人说`, genre/language, and optional author
   using real input paths. For Vue/React-style forms, prefer Selenium typing or
   native value setters plus `input`, `change`, and `blur` events. Do not rely on
   `textContent` alone.
8. Click the service-agreement checkbox only if present and unchecked.
9. Wait until `完成` is enabled before submitting.
10. Save HTML/screenshot snapshots on failure with the same `log_html_snapshot`
    pattern used by `pub_shipinhao.py`.

Important blocker before real submit: verify whether the desktop web site
exposes a usable music upload form at one of the candidate routes. If it only
exists in the mobile WeChat app, AutoPublish should not fake a desktop
publisher. In that case, the correct fallback is a documented manual/mobile
step or a separate mobile automation strategy.

## Handoff For LALACHAN Or Musia

For pure Shipinhao music uploads, call the LazyEdit music package script/API,
then post the generated ZIP with `publish_shipinhao_music=true`. First run with
`test=true` until the live desktop route is visually confirmed.

For a future pure music publish handoff, the calling repo should provide:

- audio file path;
- lyrics file or lyrics text;
- short story/context for `音乐人说`, no more than 300 characters;
- one to nine square or portrait artwork/background images;
- title, artist/author, language, and optional genre;
- explicit platform target `shipinhao_music`.

For Musia, lyrics should be treated as the authoritative context. If an ASR or
lyric-derived field conflicts with the curated lyrics, use the curated lyrics.
Do not rewrite lyrics aggressively; fix clear recognition or formatting errors
only.

For LALACHAN generated story videos with songs, decide first whether the desired
post is:

- a video post: use the existing LazyEdit video publish pipeline;
- a pure music/audio post: use the `shipinhao_music` publisher, initially with
  `test=true` until the route has been verified.

Current blocker found on 2026-06-29: the desktop Shipinhao account/session
shows the music management page and a `发表音乐` button, but no tested route
exposes an audio file input. Clicking `发表音乐` stays on the management table;
`post/create?type=music` falls back to the normal video uploader. The evidence
is saved on the Pi:

- `/home/lachlan/Projects/autopub/logs/shipinhao-music_route_not_found.png`
- `/home/lachlan/Projects/autopub/logs/selenium-shipinhao.log`

Do not keep retrying music publish blindly until either the account eligibility
or the desktop route changes. The LazyEdit package is still valid and reusable.

## LazyEdit Logo And Subtitle Burning Rules

Current default LazyEdit publish options are:

- `burnSubtitles: true`
- `usePolishedSubtitles: true`
- `subtitleSourceVersion: polished`

The CLI loads Studio settings when `--use-current-settings` is passed. It reads:

- `publish_options`
- `translation_languages`
- `burn_layout`
- `logo_settings`

During processing, `scripts/lazyedit_publish.py` adds `logo_settings` to the
process payload only when the settings contain both `enabled=true` and a
`logoPath`.

Before real video publishes, verify:

```bash
curl -fsS http://127.0.0.1:18787/api/ui-settings/logo_settings | jq .
```

Expected state:

```json
{
  "enabled": true,
  "logoPath": "...",
  "position": "top-left"
}
```

For normal video publishing, use:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms shipinhao,youtube,instagram \
  --use-polished \
  --burn-subtitles \
  --wait
```

For generated videos, keep the full script as subtitle-correction context, but
use a concise metadata brief. Do not feed the entire storyboard to metadata
generation, because the metadata can become an over-detailed script dump.

## Logo-Only Video Output

LazyEdit supports logo-only processed output. When Studio logo settings are
enabled and `burnSubtitles=false`, the process/publish path still runs the burn
stage as a logo overlay job. The resulting output ends in `_logo.mp4`, is written
as H.264/AAC with `+faststart`, and is selected for the publish ZIP. Translation
is skipped because subtitles are disabled.

Meaning:

- `--burn-subtitles` with enabled logo produces the normal subtitle/logo output.
- `--no-burn-subtitles` with enabled logo produces a no-subtitle logo-only
  output.
- `--no-burn-subtitles` with logo disabled publishes the original/preprocessed
  source video.

## Music Route Verification Checklist

When no Shipinhao publish is active, verify the music route without submitting:

1. Check `autopub` tmux and queue are idle.
2. Reuse the port `5006` browser profile; do not force restart unless needed.
3. Open candidate desktop routes or navigate manually from content management.
4. Save the HTML snapshot of the music form.
5. Confirm the form contains audio upload input, song title, lyrics, story,
   background image upload, agreement checkbox, and `完成`.
6. Run a package with `publish_shipinhao_music=true&test=true`.
7. Confirm the page filled audio, title, lyrics, language, author/story,
   artwork, agreement, and an enabled `完成` button.
8. Only real-submit after the filled form is visually verified.
