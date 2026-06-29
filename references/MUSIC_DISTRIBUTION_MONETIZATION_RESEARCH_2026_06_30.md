# Music Distribution And Monetization Research

Date: 2026-06-30

This note records the practical route for publishing Musia songs beyond
Shipinhao Music, and the LazyEdit tooling added for the next upload targets.

## Current Publish Result

`Take Care of Yourself` was packaged and submitted to Shipinhao Music through
LazyEdit/AutoPublish.

- LazyEdit music item: `9`
- Remote job: `job-1782769968656-1`
- Package:
  `DATA/music_publish/take-care-of-yourself-en-musia-music/take-care-of-yourself-en-musia-music.zip`
- Management page:
  `https://channels.weixin.qq.com/platform/post/music`
- Title used on platform: `Take Care of Yourself`
- Artist/singer: `Musia`
- Author/lyricist/composer/producer: `Musia 慕莎`
- Lyrics source:
  `/home/lachlan/ProjectsLFS/Musia/handoff/musia/take-care-of-yourself-hope-music/lyrics-en-corrected.txt`
- Audio source:
  `/home/lachlan/ProjectsLFS/MusiaSongs/audio/take-care-of-yourself-hope-en.mp3`
- Packaged audio:
  `take-care-of-yourself-hope-en_shipinhao_320k.mp3`

The Shipinhao form accepted the upload. The final form snapshot showed the
shortened title, corrected plain lyrics, square cover, original proof ZIP, and
composer/lyricist/producer fields before the submit button was clicked.

## Official Sources Checked

- Spotify for Artists provider directory:
  https://artists.spotify.com/providers
- YouTube Help, music aggregators / distribution to YouTube and YouTube Music:
  https://support.google.com/youtube/answer/9105565
- Bandcamp for Artists:
  https://bandcamp.com/artists
- SoundCloud for Artists payment/monetization help:
  https://help.soundcloud.com/hc/en-us/articles/360051802713-Getting-Paid-by-SoundCloud-for-Artists
- DistroKid pricing:
  https://distrokid.com/plan/
- TuneCore pricing:
  https://www.tunecore.com/pricing
- CD Baby pricing:
  https://cdbaby.com/pricing
- RouteNote pricing:
  https://routenote.com/pricing
- SoundOn:
  https://www.soundon.global/
- Tencent Musician:
  https://y.tencentmusic.com/
- NetEase Musician:
  https://music.163.com/st/musician

Pricing, royalty splits, territory availability, and account eligibility can
change. Before paying or committing to a release, re-open the official page and
confirm the current terms.

## Recommended Route

### 1. Keep Shipinhao Music As The China-First Quick Publish

Use LazyEdit music packages for Shipinhao Music because the flow is already
implemented and keeps the same queue/history model as video publishing.

Rules:

- Use corrected Musia website/publish lyrics for the exact vocal.
- Upload plain lyric lines, not LRC timestamps.
- Use square cover art.
- Fill author, singer, lyricist, composer, producer, genre, album, album
  description, originality proof, and agreement when visible.
- If the live language dropdown lacks English/Japanese, report the fallback
  instead of claiming the exact language was selected.

### 2. Use A Distributor For Spotify / Apple Music / YouTube Music / TikTok Libraries

Spotify and YouTube both point artists toward distribution/aggregator routes
instead of a direct self-upload form for normal music-store delivery. The
practical choices to compare are:

- DistroKid: simple subscription model, fast for frequent releases.
- TuneCore: mainstream distributor with broader admin options.
- CD Baby: per-release model; useful when avoiding an annual subscription.
- RouteNote: free/revenue-share and premium routes.
- SoundOn: useful if TikTok/SoundOn distribution is important.

LazyEdit should not try to automate those legal/account workflows directly.
Instead, LazyEdit should generate a distributor-ready release bundle with audio,
cover, corrected lyrics, metadata CSV/JSON, source proof, and upload notes.

### 3. Use Bandcamp For Direct Fan Sales

Bandcamp is the easiest direct-sales target. It is not a replacement for DSP
distribution, but it is the best next manual platform if the goal is direct fan
support and download sales.

LazyEdit can prepare the upload bundle. Manual upload is still preferable until
the account fields, payment settings, and release-page conventions are stable.

### 4. Use SoundCloud For Discovery / Optional Monetization

SoundCloud can be used as a discovery and public player target. Monetization
and broader distribution depend on SoundCloud for Artists account terms and
plan availability. Treat it as a secondary direct upload target after Bandcamp
and distributor packaging are stable.

### 5. China DSPs Are Worth Researching, But Need Account-Specific Setup

Tencent Musician and NetEase Musician are likely important for China-native
music distribution, but they may need real-name verification, creator account
review, platform-specific copyright proof, and Chinese metadata. Use the same
release bundle as source material, but do not assume the Shipinhao Selenium
flow maps directly to those sites.

## LazyEdit Implementation Added

New script:

```bash
scripts/lazyedit_music_distribution_bundle.py
```

It exports an existing LazyEdit music publish folder into a clean bundle for
Bandcamp, SoundCloud, or distributor upload:

```bash
python scripts/lazyedit_music_distribution_bundle.py \
  --package-dir DATA/music_publish/take-care-of-yourself-en-musia-music \
  --source-url 'https://fun.lazying.art/#take-care-of-yourself-hope-version'
```

Output created for this song:

```text
DATA/music_distribution/take-care-of-yourself-en-musia-music/
  audio/take-care-of-yourself-hope-en_shipinhao_320k.mp3
  audio/take-care-of-yourself-en-musia-music_distribution_44k16.wav
  cover/take-care-of-yourself-en-musia-music_cover_01_square.jpg
  lyrics/lyrics.txt
  metadata/release.json
  metadata/release.csv
  UPLOAD_NOTES.md
```

Important: if Musia can provide a true WAV/FLAC master, use that for paid DSP
distribution. The generated WAV in this bundle is a compatibility derivative
from the available MP3, not a lossless source master.

## Next Implementation Order

1. Add a Music tab action in LazyEdit UI: `Export distribution bundle`.
2. Add platform-specific checklist panels for Bandcamp and distributor upload.
3. Add optional fields to the LazyEdit music metadata contract:
   - release date
   - explicit flag
   - copyright line
   - territories
   - ISRC/UPC if available
   - label
   - primary genre and secondary genre
   - composer/lyricist/producer splits
4. After one manual Bandcamp release succeeds, write a `pub_bandcamp_music.py`
   only if the upload form is stable and login/session persistence is reliable.
5. For YouTube Music as an official music release, use a distributor. LazyEdit
   can still create an art-track MP4 for normal YouTube, but that is not the
   same thing as distributor delivery to YouTube Music.

## Platform Decision For `Take Care of Yourself`

Best order:

1. Shipinhao Music English: done.
2. Bandcamp: use the generated distribution bundle and upload manually.
3. Distributor comparison: DistroKid vs TuneCore vs RouteNote. Pick based on
   release volume and whether subscription or revenue-share is preferred.
4. After the English release is stable, publish Japanese and Mandarin versions
   as separate version releases using their corrected vocal lyrics.

