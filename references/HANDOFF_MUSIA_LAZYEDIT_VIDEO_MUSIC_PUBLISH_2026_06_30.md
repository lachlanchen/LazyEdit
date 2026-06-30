# Handoff: Publish Musia Videos And Music Through LazyEdit

Date: 2026-06-30

This note is for another Codex, Musia, LALACHAN, or AgInTi session that needs to publish with LazyEdit without depending on manual babysitting.

LazyEdit can publish two different things:

1. **Video posts**: MP4 recordings/MVs to Shipinhao, YouTube, Instagram, Douyin, Xiaohongshu, and Bilibili through `scripts/lazyedit_publish.py`.
2. **Music posts**: pure song/audio packages to Shipinhao Music, and distributor-ready bundles through `scripts/lazyedit_music_package.py` and `scripts/lazyedit_music_distribution_bundle.py`.

Run all local commands from:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

LazyEdit backend should be running at:

```text
http://127.0.0.1:18787
```

Remote AutoPublish host:

```text
http://lazyingart:8081
ssh lachlan@lazyingart
cd ~/Projects/autopub
tmux attach -t autopub
```

## Default Video Publish Settings

Use these unless the user explicitly overrides them.

### Normal Multilingual Subtitle Video

This is the mature LazyEdit pipeline used for normal story videos, LALACHAN videos, and phone recordings where subtitles are wanted.

Visual subtitle stack:

- top row: English
- middle row: Japanese
- bottom row: Chinese

CLI language order is bottom-to-top, so pass:

```text
--languages zh-Hant,ja,en
```

Expected subtitle behavior:

- Use polished/corrected subtitles.
- Burn subtitles.
- Japanese uses LazyEdit's default ruby/furigana/romaji handling.
- Chinese uses LazyEdit's default pinyin/ruby handling.
- Grammar-analysis color should come from the default LazyEdit renderer/token pipeline. Do not bypass it with a custom ASS/SRT patch unless fixing the shared renderer.
- Use the existing LazyEdit Studio logo at top-right.

Command pattern:

```bash
python scripts/lazyedit_publish.py \
  --video /path/to/video.mp4 \
  --title "Public title" \
  --platforms shipinhao,youtube,instagram \
  --use-current-settings \
  --languages zh-Hant,ja,en \
  --correct-subtitles \
  --correction-source polished \
  --use-polished \
  --burn-subtitles \
  --logo \
  --logo-position top-right \
  --publish-category musia \
  --correction-prompt-file /path/to/full-script-or-context.md \
  --metadata-prompt-file /path/to/short-metadata-brief.md \
  --guided-monitor \
  --wait
```

Use `--platforms douyin,xiaohongshu` or `--platforms shipinhao,youtube,instagram,douyin,xiaohongshu` when those platforms are requested and logged in.

### Musia Screen Recording Video Without Extra Subtitles

For Musia website/player screen recordings, the video often already includes lyrics and timing from the webapp. In that case the default is no extra LazyEdit subtitles, but still burn the existing logo at top-right.

Command pattern:

```bash
python scripts/lazyedit_publish.py \
  --video /path/to/musia-recording.mp4 \
  --title "Song Title - Musia English Version" \
  --platforms shipinhao,youtube,instagram \
  --use-current-settings \
  --no-burn-subtitles \
  --logo \
  --logo-position top-right \
  --publish-category musia \
  --metadata-prompt-file /path/to/short-metadata-brief.md \
  --guided-monitor \
  --wait
```

If the user asks for subtitles on a Musia recording, switch back to the normal multilingual subtitle command above.

### Logo Check

Before real publish, verify LazyEdit logo settings:

```bash
curl -fsS http://127.0.0.1:18787/api/ui-settings/logo_settings | jq .
```

For current Musia/LALACHAN/MV work, the expected logo position is:

```json
{
  "enabled": true,
  "position": "top-right"
}
```

Do not invent a new logo asset. Use the configured LazyEdit Studio logo.

For no-subtitle logo-only runs, inspect the rendered MP4 before publishing:

```bash
ffmpeg -y -ss 00:00:03 -i DATA/<video-folder>/*_logo.mp4 -frames:v 1 temp/logo-check.jpg
```

Confirm visually:

- top-right logo is present;
- no unwanted LazyEdit subtitle rows;
- video is the exact intended version.

## Video Context And Metadata Rules

Use the source script/story differently for subtitle correction and metadata.

Subtitle correction:

- Give the full script/story/context.
- Treat it as reference, not verbatim truth.
- Fix clear ASR errors and broken phrases.
- Do not over-edit or invent unsupported speech.
- For generated videos, recover missing dialogue only when it matches the audio and context.

Metadata generation:

- Do not pass a full storyboard/script dump as public metadata context.
- Create a short metadata brief with:
  - title intent;
  - hook;
  - characters/setting;
  - story payoff;
  - mood;
  - keywords/tags;
  - category.

Example metadata brief:

```markdown
# Metadata Brief

Title: Take Care of Yourself
Category: musia
Tone: warm, hopeful, gentle pop
Hook: a Musia song about self-care and quiet courage
Description guidance: viewer-facing and concise. Do not expose the full script.
Tags: Musia, LazyingArt, original music, healing, self-care
```

## Safe Video Publish Workflow

For important publishes, dry-run processing first:

```bash
python scripts/lazyedit_publish.py \
  --video /path/to/video.mp4 \
  --title "Public title" \
  --platforms shipinhao,youtube,instagram \
  --use-current-settings \
  --languages zh-Hant,ja,en \
  --correct-subtitles \
  --use-polished \
  --burn-subtitles \
  --logo \
  --logo-position top-right \
  --publish-category musia \
  --correction-prompt-file /path/to/full-context.md \
  --metadata-prompt-file /path/to/metadata-brief.md \
  --no-publish \
  --guided-monitor \
  --wait
```

Inspect:

- `DATA/<video-folder>/*_subtitles_logo.mp4` for subtitle runs;
- `DATA/<video-folder>/*_logo.mp4` for logo-only runs;
- `DATA/<video-folder>/publish/*.zip`;
- metadata JSON under `DATA/<video-folder>/metadata/`.

Then publish the already-processed output:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --platforms shipinhao,youtube,instagram \
  --use-current-settings \
  --no-process \
  --publish \
  --guided-monitor \
  --wait
```

If adding a missing platform later, reuse the same ZIP/output if it already contains the correct rendered MP4. Do not regenerate unless the MP4, subtitles, logo, or metadata are wrong.

## Music Publish Inputs

A music publish is separate from video publish. Use this for pure songs/audio, especially Shipinhao Music.

Required inputs:

- audio file: MP3 or WAV for Shipinhao Music;
- title: public song title, not a long prompt title;
- artist/author: usually `Musia` or `Musia 慕莎`; use `陈荣周` only when a real-name field requires it;
- corrected lyric JSON for the exact vocal/audio version;
- plain corrected lyric text for upload;
- language;
- genre/style;
- short story / `音乐人说`;
- public description;
- square cover images, preferably 9 candidates;
- proof/source files when available.

Critical lyric rule:

Use the corrected Musia website/publish lyric JSON for the exact selected vocal. Do not use:

- original prompt lyrics;
- draft lyrics;
- another language/vocal's translation JSON;
- ASR output before correction.

If lyrics are wrong, fix Musia first, then package music.

## Generate Or Prepare 9 Square Covers

Shipinhao Music expects square cover/background candidates.

Preferred cover shape:

```text
1:1 square, high resolution, PNG or JPG
```

Recommended:

- generate 5 covers with AgInTi if available;
- generate 4 covers with Codex/image tooling if available;
- or provide one strong square cover and let LazyEdit extract/derive remaining candidates from a video with `--cover-video --cover-count 9`.

Put covers in a stable folder such as:

```text
/home/lachlan/ProjectsLFS/Musia/handoff/<song-slug>/covers/
```

Pass each curated cover with repeated `--cover`:

```bash
--cover /path/to/cover-01.png \
--cover /path/to/cover-02.png \
--cover /path/to/cover-03.png
```

If only one cover exists:

```bash
--cover /path/to/cover-square.png \
--cover-video /path/to/recording-or-mv.mp4 \
--cover-count 9
```

## Package And Publish Shipinhao Music

First create a package and inspect it:

```bash
python scripts/lazyedit_music_package.py \
  --audio /path/to/song.mp3 \
  --title "Take Care of Yourself" \
  --artist "Musia" \
  --author "Musia 慕莎" \
  --language "English" \
  --genre "Pop" \
  --story "A warm Musia original song about self-care, quiet courage, and staying hopeful." \
  --description "Take Care of Yourself is an original Musia song about gentle self-care and hope." \
  --lyrics-json /path/to/corrected-lyrics.json \
  --lyrics-format plain \
  --cover /path/to/cover-square-01.png \
  --cover /path/to/cover-square-02.png \
  --cover-count 9 \
  --proof /path/to/project-or-prompt-proof.md \
  --website-screenshot /path/to/fun-lazying-art-song-page.png \
  --webapp-screenshot /path/to/musia-webapp-generation-session.png \
  --source-url "https://fun.lazying.art/..." \
  --output-slug take-care-of-yourself-en-music
```

Inspect:

```bash
ls -lah DATA/music_publish/take-care-of-yourself-en-music
sed -n '1,120p' DATA/music_publish/take-care-of-yourself-en-music/*_lyrics.txt
jq . DATA/music_publish/take-care-of-yourself-en-music/*_metadata.json
```

Verify:

- lyric text matches the corrected exact vocal JSON;
- no `[mm:ss]` timestamps for Shipinhao Music;
- title is clean and public;
- cover files are square;
- proof screenshots/files are included if available.

Then publish to Shipinhao Music:

```bash
python scripts/lazyedit_music_package.py \
  --audio /path/to/song.mp3 \
  --title "Take Care of Yourself" \
  --artist "Musia" \
  --author "Musia 慕莎" \
  --language "English" \
  --genre "Pop" \
  --story "A warm Musia original song about self-care, quiet courage, and staying hopeful." \
  --description "Take Care of Yourself is an original Musia song about gentle self-care and hope." \
  --lyrics-json /path/to/corrected-lyrics.json \
  --lyrics-format plain \
  --cover /path/to/cover-square-01.png \
  --cover /path/to/cover-square-02.png \
  --cover-count 9 \
  --proof /path/to/project-or-prompt-proof.md \
  --website-screenshot /path/to/fun-lazying-art-song-page.png \
  --webapp-screenshot /path/to/musia-webapp-generation-session.png \
  --source-url "https://fun.lazying.art/..." \
  --output-slug take-care-of-yourself-en-music \
  --post \
  --shipinhao-music
```

If testing a changed publisher route, add `--test` first so AutoPublish fills the page but does not submit.

Monitor the music publish with the queue/log commands in the monitoring section below.

## Shipinhao Music Field Checklist

AutoPublish should fill all visible fields when available:

- add/upload music/audio;
- song title;
- lyric content;
- declaration/originality checkbox if applicable;
- genre/style;
- language;
- author information;
- 9 square background images/covers;
- `音乐人说` story;
- service agreement checkbox;
- cover confirmation overlay after image upload;
- final submit/complete button.

Do not publish as album/zhuanji when the request is a song/music item.

If a field is unavailable in the current desktop UI:

- publish only if the required fields are accepted;
- report the exact fallback;
- do not claim a field was selected when the UI did not expose it.

## Music Distribution Bundle

For monetization platforms beyond Shipinhao Music, create a distributor-ready bundle instead of automating a brittle browser upload.

```bash
python scripts/lazyedit_music_distribution_bundle.py \
  --package-dir DATA/music_publish/take-care-of-yourself-en-music \
  --source-url "https://fun.lazying.art/..." \
  --make-wav
```

Use this bundle for:

- Bandcamp;
- SoundCloud;
- DistroKid;
- TuneCore;
- CD Baby;
- RouteNote;
- SoundOn;
- LANDR;
- other distributors that deliver to Spotify, Apple Music, YouTube Music, Amazon Music, TikTok/Instagram music libraries, etc.

LazyEdit's YouTube music/art-track publishing is normal YouTube publishing, not official YouTube Music DSP delivery. Use a distributor for official YouTube Music/Spotify/Apple Music delivery.

## Monitoring

LazyEdit local queue:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq .
```

Remote AutoPublish queue:

```bash
curl -fsS http://lazyingart:8081/publish/queue | jq .
```

Remote browser/publisher logs:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -160 | tail -n 160'
```

The current AutoPublish verifier checks Douyin and Shipinhao management pages after submit. A submit-button click alone is not enough.

## Copy-Paste Handoff Packet Template

Use this block when handing a job to another agent:

```markdown
# LazyEdit Publish Request

Type: video | music

## For Video

Source MP4:
Title:
Platforms:
Category: musia | lalamv | lalachan | simplelife | lazyingart
Subtitle mode: multilingual subtitles | no extra LazyEdit subtitles
Logo: top-right LazyEdit Studio logo
Languages if subtitles: visual EN / JP / ZH, CLI `zh-Hant,ja,en`
Correction context file:
Metadata brief file:
Notes:
- Use polished/corrected subtitles.
- Japanese ruby/furigana/romaji and Chinese pinyin are LazyEdit defaults.
- Do not override grammar color renderer.
- Dry-run with `--no-publish` if output is not already verified.

## For Music

Audio:
Title:
Artist:
Author:
Language:
Genre:
Corrected lyrics JSON:
Plain lyrics file if already prepared:
Covers folder or cover paths:
Proof files/screenshots:
Website/source URL:
Story / 音乐人说:
Platforms: shipinhao_music
Notes:
- Lyrics must match exact corrected vocal.
- Use plain lyrics for Shipinhao Music.
- Fill originality/agreement fields when present.
- Use 9 square covers.
```

## Final Safety Checklist

Before real publish:

- exact source file is correct;
- no stale or wrong video version in ZIP;
- logo side is correct;
- subtitle mode is explicit;
- if subtitles are enabled: EN/JP/ZH are present, Japanese ruby/romaji and Chinese pinyin render normally;
- metadata is concise and viewer-facing;
- music lyrics are corrected exact-vocal lyrics;
- Shipinhao Music cover candidates are square;
- remote AutoPublish queue is not already running another job;
- publish once, then verify platform status instead of repeated blind retries.
