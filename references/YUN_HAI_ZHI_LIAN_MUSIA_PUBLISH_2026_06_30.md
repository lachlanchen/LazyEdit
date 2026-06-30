# Yun Hai Zhi Lian Musia Publish - 2026-06-30

## Inputs

- Handoff note: `handoffnotes/input/2026-06-30-yun-hai-zhi-lian-musia-publish.md`
- Video: `/home/lachlan/ProjectsLFS/Musia/recorded_videos/yun-hai-zhi-lian/yun-hai-zhi-lian-standard-zh-Hans-portrait-4k.mp4`
- Audio: `/home/lachlan/ProjectsLFS/Musia/data/creative_projects/yun-hai-zhi-lian-haifeng-duange-20260630/selected/yun-hai-zhi-lian-haifeng-duange-zh-Hans-ace-20260630.mp3`
- Corrected lyrics: `/home/lachlan/ProjectsLFS/Musia/website/data/songs/yun-hai-zhi-lian-haifeng-duange/lyrics/zh-vocal/zh-Hans.json`
- Public page: `https://fun.lazying.art/#yun-hai-zhi-lian-haifeng-duange`

## Video Publish

Published the 4K portrait Musia recording with:

- no LazyEdit subtitles;
- existing LazyEdit logo at top-right;
- category `musia`;
- platforms: Shipinhao, Instagram, YouTube.

Command pattern:

```bash
python scripts/lazyedit_publish.py \
  --api-url http://127.0.0.1:18787 \
  --video "$VIDEO" \
  --title '云海之恋 | Musia' \
  --platforms shipinhao,youtube,instagram \
  --use-current-settings \
  --no-burn-subtitles \
  --logo \
  --logo-position top-right \
  --publish-category musia \
  --metadata-prompt-file temp/yun-hai-zhi-lian/yun-hai-zhi-lian-metadata-brief.md \
  --guided-monitor \
  --remote-queue-url http://lazyingart:8081/publish/queue \
  --wait
```

Result:

- LazyEdit video id: `433`
- Remote job: `job-1782834445779-3`
- ZIP: `DATA/yun-hai-zhi-lian-standard-zh-Hans-portrait-4k/publish/yun-hai-zhi-lian-standard-zh-Hans-portrait-4k.zip`
- Remote status: `done`

Notes:

- Shipinhao collection `Musia` was requested, but the visible dropdown only exposed `简单生活` and `懒人艺术`; publish continued without collection.
- YouTube playlist `Musia` was created, but not immediately selectable in the upload dialog; publish continued without playlist.

## Music Publish

Packaged and published the pure music item as Shipinhao Music:

- title: `云海之恋`;
- artist/singer: `Musia`;
- author/lyricist/composer/producer: `Musia 慕莎`;
- language: `中文` / Shipinhao selected `普通话`;
- genre: `流行` / Shipinhao selected `城市流行`;
- lyrics: corrected plain lyrics converted from the Musia website `zh-vocal/zh-Hans.json`;
- cover set: 9 square covers, starting from the Musia 16:9 cover and extracted video frames;
- proof ZIP: handoff note, public page screenshot, manifest, corrected lyric JSON.

Package:

```text
DATA/music_publish/yun-hai-zhi-lian-musia-music/
DATA/music_publish/yun-hai-zhi-lian-musia-music/yun-hai-zhi-lian-musia-music.zip
```

Remote result:

- Remote job: `job-1782835535501-4`
- Platform: `shipinhao_music`
- Remote status: `done`

Important validation from remote log:

- audio selected;
- title filled;
- lyrics filled from corrected plain lyrics;
- author, singer, lyricist, composer, producer filled;
- published-elsewhere set to yes;
- album name and intro filled;
- album cover selected;
- proof ZIP selected and upload ready;
- agreement checked;
- publish button enabled;
- `Shipinhao music submitted.`

## Reusable Fix

The first music post failed because the CLI used the local `AUTOPUBLISH_URL` default and tried a dead localhost endpoint. A second attempt accidentally used the read-only queue URL and got `405 Method Not Allowed`.

Fix in `scripts/lazyedit_music_package.py`:

- normalize accidental `/publish/queue` URLs back to `/publish`;
- probe reachable AutoPublish candidates like the web app;
- prefer the reachable remote `http://lazyingart:8081/publish` when local `localhost:8081` is unavailable;
- record the resolved `autopublish_url` in CLI output.

Future music publish command can omit `--autopublish-url` unless an explicit override is needed.

Additional smoothing in `lazyedit/music_publish.py`:

- reset generated `covers/` and `proof/` subdirectories before rebuilding the
  same music package slug;
- this prevents retry builds from accumulating duplicate filenames such as
  `website-screenshot-2.png` and keeps the package manifest deterministic.
