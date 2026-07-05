# Musia Sha Sha Publish Report - 2026-07-05

## Scope

This is a factual report from the Musia `sha-sha` publish run. It is not a
claim that LazyEdit or AutoPublish is generally broken. The normal system can
publish successfully; the issues below describe specific behavior observed
during this run after several interrupted attempts.

## Source Assets

- Musia repo: `/home/lachlan/ProjectsLFS/Musia`
- Verified recording:
  `/home/lachlan/ProjectsLFS/Musia/recorded_videos/sha-sha/sha-sha-zh-lyrics-guitar-portrait-4k.mp4`
- Verified Nutstore copy:
  `/home/lachlan/Nutstore Files/Projects/Musia/sha-sha-zh-lyrics-guitar-portrait-4k.mp4`
- Corrected lyric JSON used for website/music handoff:
  `/home/lachlan/ProjectsLFS/Musia/website/data/songs/sha-sha/lyrics/zh-vocal/zh-Hans.json`
- Direct AutoPublish package:
  `/home/lachlan/DiskMech/Projects/lazyedit/DATA/sha-sha-musia-lyrics-guitar-4k/publish_direct_4k/sha-sha-musia-lyrics-guitar-4k-direct.zip`

## Confirmed Good State

- Musia website validation passed before recording.
- The inspected recording is `2160x3840`, `24 fps`, about `76.4s`, with audio.
- Sample frames from the inspected recording showed the intended layout:
  player, current lyrics, current chord, and guitar fingering with no overlap.
- Douyin publish was verified by AutoPublish management-page matching during the
  first direct-package run.

## LazyEdit Packaging Observation

An initial LazyEdit CLI route using logo-only processing produced a derived file
under:

```text
/home/lachlan/DiskMech/Projects/lazyedit/DATA/sha-sha-musia-lyrics-guitar-4k/sha-sha-musia-lyrics-guitar-4k_portrait_logo.mp4
```

Observed facts:

- The source recording was `2160x3840`.
- The LazyEdit processed output inspected during the run was `1080x1920`.
- A sample frame showed a blurred-margin portrait composition and a larger
  top-right logo than the already-inspected Musia recording style.
- Because the user wanted to preserve the 4K recording quality and layout, the
  run switched to a direct AutoPublish ZIP instead of publishing the processed
  LazyEdit output.

Suggested fix:

- Add an explicit "direct 4K Musia recording" publish path in LazyEdit that
  packages an already-approved MP4 without resizing or portrait recomposition.
- If a logo is required, either verify that the existing recording already has
  the intended logo or provide a high-quality logo-only burn that preserves the
  source resolution and framing.
- Before real publish, show or log the exact MP4 selected for the ZIP, including
  resolution, duration, and whether it was reprocessed.

## Metadata Guardrail Observation

During this run the user corrected that public platform metadata must describe
the song itself, not the generation conversation or workflow.

Suggested fix:

- For Musia publish category, prefer a song-only metadata brief:
  title, artist, language, genre, mood, story, public URL, corrected lyrics
  source.
- Do not include pipeline notes, model names, correction discussion, or internal
  recording layout notes in public platform descriptions unless explicitly
  requested.
- Preserve the supplied title for direct packages unless the caller explicitly
  asks for generated title alternatives.

## Corrected Lyrics Requirement

For music-platform packages, the lyrics source must be the corrected website
JSON for the selected vocal:

```text
/home/lachlan/ProjectsLFS/Musia/website/data/songs/sha-sha/lyrics/zh-vocal/zh-Hans.json
```

Do not use the original draft lyric or prompt text for Shipinhao Music.
