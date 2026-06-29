# LazyEdit Publish Runbook: Musia, Video, Music, And Platform Smoothing

Date: 2026-06-30

This note records the problems hit while publishing the Hikari Ame MV and the
Xiao Xiao Zhu Musia video/music batch, plus the rules that should make the next
publish smoother.

## Scope

This covers:

- LazyEdit video publishes to Shipinhao, Instagram, YouTube, Douyin,
  Xiaohongshu, and Bilibili.
- LazyEdit music packages for Shipinhao Music and YouTube art-track music.
- Musia recording videos: top-right LazyEdit logo, no subtitles unless the user
  explicitly asks for subtitle review.
- LALACHAN/generated story videos: corrected subtitles using the script as
  context, but metadata must remain concise.

## Problems Met And Fixes

### Wrong Output Version Was Published

Problem:

- A prepared LazyEdit video could point at the original or wrong landscape
  output while the desired output was the portrait bg-fill, subtitle/logo burned
  version.
- The same source video can have several LazyEdit runs, ZIPs, and manual
  packages, so "publish this one" is ambiguous if we do not inspect the ZIP.

Fix:

- Treat the MP4 inside the ZIP as the source of truth before submitting.
- For already-finished runs, reuse the existing ZIP only if the internal MP4 is
  the desired rendered version.
- Repackage only when the existing ZIP points to the wrong output.
- For adding missing platforms, resubmit the same correct ZIP with only the
  missing platform flags instead of rerunning the pipeline.

Checklist:

```bash
unzip -l /path/to/publish.zip | sed -n '1,120p'
tmpdir=$(mktemp -d)
unzip -q /path/to/publish.zip -d "$tmpdir"
find "$tmpdir" -maxdepth 2 -type f \( -iname '*.mp4' -o -iname '*metadata.json' \) -print
ffprobe -v error -show_entries stream=width,height -show_entries format=duration \
  -of default=nw=1:nk=1 "$tmpdir"/path/to/video.mp4
```

### Logo Was On The Wrong Side

Problem:

- Musia recordings should use the existing LazyEdit logo at the top-right, but
  older publish defaults and some docs still said top-left.
- A logo-only output can look "processed" even if the position is wrong.

Fix:

- For Musia recordings and current MV work, force `--logo --logo-position
  top-right`.
- For personal SimpleLife phone videos, keep the normal Studio setting unless
  the user says otherwise.
- After changing logo position, force a fresh process/burn instead of reusing an
  older `_logo.mp4`.
- Extract a frame and inspect it before publish.

Commands:

```bash
curl -fsS http://127.0.0.1:18787/api/ui-settings/logo_settings | jq .

ffmpeg -y -ss 3 -i DATA/<video>/<rendered>_logo.mp4 \
  -frames:v 1 temp/logo_check.jpg
```

Expected for Musia recording video publishes:

- `logo_settings.enabled=true`
- `logoPath` present
- `position="top-right"`
- no subtitle rows unless requested

### No-Subtitle Publish Still Needs Processing

Problem:

- "No subtitles" does not mean "publish the raw video." For Musia recordings we
  still need the logo-only render.

Fix:

- Use `--no-burn-subtitles --logo --logo-position top-right`.
- Do not add `--no-process` unless the correct `_logo.mp4` already exists and
  was verified.
- Translation should be skipped in this path; metadata and cover can still be
  generated.

Example:

```bash
python scripts/lazyedit_publish.py \
  --video /path/to/musia-recording.mp4 \
  --source musia \
  --publish-category musia \
  --use-current-settings \
  --no-correct-subtitles \
  --no-burn-subtitles \
  --logo \
  --logo-position top-right \
  --platforms shipinhao,youtube,instagram,douyin,xiaohongshu \
  --guided-monitor \
  --wait
```

### Generated-Video Metadata Became Too Script-Like

Problem:

- Passing a full Xiaoyunque/Musia script directly as metadata context can make
  platform descriptions read like a storyboard or prompt dump.

Fix:

- Use the full script for subtitle correction only.
- Use a separate short metadata brief for metadata generation:
  hook, characters, setting, emotional payoff, keywords, and platform category.
- Do not expose full prompt mechanics, reference-image order, file paths, or
  "do not generate subtitles" constraints in public metadata.

### Subtitle Correction Must Be Contextual But Not Aggressive

Rule:

- The script/prompt is context, not a transcript.
- Correct apparent ASR errors, names, broken phrases, and impossible lines.
- Do not rewrite good lines just because the script says something prettier.
- For songs/Musia lyrics, the curated lyric JSON is authoritative. If lyrics
  are wrong, fix them in Musia first instead of improvising in LazyEdit.

### Shipinhao Video Collection Was Missing

Problem:

- The publish requested category/collection `Musia`, but the visible Shipinhao
  collection picker only exposed `简单生活` and `懒人艺术`.

Fix:

- The publisher should continue without failing when a requested collection is
  absent, and report it.
- Use the management scripts later to create/move collections if needed.

### YouTube Playlist Was Not Immediately Selectable

Problem:

- The YouTube publisher could create/attempt `Musia`, but the playlist was not
  immediately exposed in the upload dialog selection list.

Fix:

- Continue the publish rather than failing the whole job.
- Report playlist fallback after success.
- Use a later management pass for playlist cleanup if needed.

### Douyin Existing Drafts Should Be Reused

Problem:

- Uploading again can waste time or wedge the page. Douyin fields can also hang
  Selenium if native `send_keys()` is used on some widgets.

Fix:

- Reuse existing unpublished drafts when the upload already exists.
- Use the AutoPublish JavaScript field replacement path for title/description.
- Keep hashtags inside the description instead of using the separate topic
  widget during automation.

### Xiaohongshu Publish Button And Popovers

Problem:

- Hashtag suggestion popovers can cover or intercept the final publish control.
- The red publish control may be a custom `xhs-publish-btn` element.

Fix:

- Escape/blur after filling text.
- Use the AutoPublish fallback selector/click path rather than random screen
  coordinates.

### Bilibili Cooldown And SMS Gates

Problem:

- Bilibili can show stale upload rows, optional SMS overlays, hard SMS gates, or
  `preupload` code `601` upload cooldown.

Fix:

- Track the current filename's own upload row.
- Close optional notification SMS overlays.
- If hard SMS verification blocks upload, get the SMS code; Tuling/GeeTest does
  not solve this.
- If `preupload` returns `601`, stop retrying and wait for cooldown.
- Missing cover upload should not force a full reupload.

### Shipinhao Music Language Dropdown

Problem:

- Shipinhao Music accepted the song publish, but the language dropdown was
  fragile and did not always select Japanese/English/Chinese correctly.
- In the 2026-06-30 English Xiao Xiao Zhu run, the form accepted the song and
  all core metadata, but the live dropdown did not expose an English option, so
  the page state still showed `普通话`.

Fix:

- AutoPublish `pub_shipinhao_music.py` was patched and pushed to use a more
  robust language-selection path.
- Pull the latest AutoPublish on `lazyingart` before the next music batch.
- Treat language selection as best-effort until the live dropdown exposes a
  matching option. Do not block a valid song publish solely because the current
  page has no English/Japanese option, but report the fallback clearly.

Verification:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && git log --oneline -3'
```

### Shipinhao Music Fields Need Full Coverage

For music uploads, fill every visible relevant field when present:

- music/audio file
- song title
- lyrics
- language
- genre/style
- author/artist, usually `Musia 慕莎`
- cover/background images, currently square works best
- `音乐人说` / story, short and viewer-facing
- originality/declaration checkbox when applicable and safe
- agreement checkbox
- proof files in the ZIP: Musia webapp/website screenshot or source artifact

Before posting, verify that `*_lyrics.txt` in the package was derived from the
corrected Musia website vocal JSON for the exact audio, for example:

```text
/home/lachlan/ProjectsLFS/Musia/website/data/songs/<song-id>/lyrics/en-vocal/en.json
```

Do not use the original prompt lyric, companion draft, or another vocal's
translation JSON. In the Xiao Xiao Zhu English run, the corrected website lyric
started with `But you are a piggy...`; the original draft started with
`You are a piggy...`. The package must use the corrected website line.

Do not publish as album/zhuanji when the user asked for a single song. Use the
music/song upload path.

### QR Email Rendering

Problem:

- Some QR emails no longer rendered well on Apple Watch.

Fix:

- AutoPublish uses the watch-friendly inline PNG method verified by test mail.
- Reuse the existing Shipinhao login email path for music and video.

### Too Many Open Monitor Processes

Problem:

- Long debugging sessions opened too many exec/monitor sessions, triggering:
  "maximum number of unified exec processes ... 60".

Fix:

- Prefer one CLI `--guided-monitor` process per publish.
- Use one-shot `curl`/`tmux capture-pane` checks instead of long-lived extra
  terminals.
- When a background session is no longer needed, stop or close it before
  starting another.
- Avoid parallel manual browser debugging while the CLI publish is already
  monitoring the same job.

## Platform Defaults Going Forward

### Personal Phone Recordings

- Category: `simplelife`
- Usually publish to Shipinhao, Instagram, YouTube, and optionally Douyin/XHS.
- Use subtitles unless the user explicitly asks for no subtitles.
- Use context for subtitle correction.

### LALACHAN Story Videos

- Category: `lalachan`
- Use script for subtitle correction.
- Use short metadata brief, not raw script dump.
- Burn subtitles and configured logo unless user says otherwise.

### LALACHAN/Musia MV Videos

- Category: `lalamv` or `musia` depending on the source.
- For Musia recordings, no subtitles by default.
- Logo top-right by default.
- If the video already has lyric overlays from Musia, do not add LazyEdit
  subtitles unless requested.

### Pure Music

- Use `scripts/lazyedit_music_package.py`.
- Use curated lyric JSON from Musia.
- Generate or supply square covers.
- Publish as music/song, not as album.
- Record the music item in LazyEdit and update status after publish.

## Smooth Publish Procedure

1. Identify the exact source and desired rendered version.
2. Confirm category and platform list.
3. Confirm subtitle policy:
   - normal videos: corrected subtitles;
   - Musia recordings: no subtitles unless requested;
   - music packages: lyrics only.
4. Confirm logo policy:
   - Musia/MV: top-right;
   - others: Studio default or user override.
5. Run package/process without real publish if anything changed.
6. Inspect the rendered MP4 or ZIP.
7. Publish exactly once with `--guided-monitor`.
8. Report platform fallbacks, not just "done."
9. Commit and push only code/docs that were intentionally changed; do not stage
   unrelated dirty files.

## Useful Final Status Commands

LazyEdit queue:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue \
  | jq '.jobs[:8] | map({id,video_id,status,platforms,remote_status,remote_job_id,error,updated_at})'
```

Remote AutoPublish queue:

```bash
curl -fsS http://lazyingart:8081/publish/queue \
  | jq '.jobs[:8] | map({id,status,platforms,filename,error,updated_at})'
```

Pi browser log:

```bash
ssh lachlan@lazyingart \
  'tmux capture-pane -pt autopub:0 -S -140 | tail -100'
```
