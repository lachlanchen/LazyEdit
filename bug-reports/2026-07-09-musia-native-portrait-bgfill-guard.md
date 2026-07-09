# Bug: Native Portrait Musia Recordings Should Never Be Portrait Bg-Filled

Date: 2026-07-09

## Summary

LazyEdit can still apply or inherit portrait blur-fill settings for videos that
are already native portrait recordings. This is wrong for Musia Fun-player
recordings: a `2160x3840` portrait capture is already physically in the target
portrait aspect ratio, so there is no aspect-ratio gap to fill. Applying
portrait bg-fill to an already-portrait source can only duplicate/blur/reframe
the same content, reduce quality, or create a visually wrong layout.

Tool-level guardrails are needed so future agents and UI users cannot
accidentally bg-fill an already-portrait source.

## Impact

Musia portrait recordings are intended to be direct captures of the website:

```text
Fun Lazying Art header
Musia player
current KTV-style lyrics
chord carousel
guitar fingering
```

When a native portrait source is passed through a portrait bg-fill route, the
result can look like a converted landscape video rather than the actual mobile
page. This wastes resolution, changes composition, and causes publication
friction.

## Evidence

Correct no-bgfill rerun:

```text
/home/lachlan/ProjectsLFS/Musia/recorded_videos/gong-yin-chang-jiang-shui-mixed/gong-yin-chang-jiang-shui-mixed-lyrics-guitar-portrait-4k-native-nobgfill.mp4
```

Media facts:

```text
width=2160
height=3840
duration=74.000s
sha256=62f2f86f45d8171310f11b654adac9bbec2cb0d2eb6c4fd973b7459e239bd75d
```

LazyEdit publish rerun:

```text
video_id=466
publication_session_id=44
publish_job=293
remote_job_id=job-1783589234999-7
remote_zip=gong-yin-chang-jiang-shui-mixed-lyrics-guitar-portrait-4k-native-nobgfill_session_44.zip
```

The successful rerun explicitly used:

```text
--no-portrait-blur-fill
```

and the final config showed:

```json
"portraitBlurFill": {
  "enabled": false
}
```

## Current Risk

`scripts/lazyedit_publish.py` can inherit Studio burn-layout settings. If the
Studio settings or current publish options have `portraitBlurFill.enabled=true`,
a caller may accidentally bg-fill a native portrait Musia recording unless they
remember to pass `--no-portrait-blur-fill`.

Relevant code paths:

```text
scripts/lazyedit_publish.py
app.py
lazyedit/portrait_blurfill.py
```

The dangerous behavior is especially likely when using `--use-current-settings`
or when older Studio preferences persist from a LALACHAN/horizontal-video run.

## Expected Behavior

For a source that is already portrait and already matches the requested portrait
output ratio, LazyEdit should automatically prevent portrait bg-fill.

Example:

```text
source: 2160x3840
target: 1080x1920 or 2160x3840
source aspect: 9:16
target aspect: 9:16
```

Expected outcome:

```text
portraitBlurFill.enabled=false
no *_portrait_blurfill.mp4 intermediate
normal logo-only or subtitle/logo processing continues
```

## Suggested Tool-Level Fix

Add a source-aspect-ratio guard in both CLI and backend processing:

1. Probe source dimensions before processing if `portraitBlurFill.enabled=true`.
2. Compute source and target aspect ratio.
3. If source is already portrait and close to the target ratio, disable bg-fill
   or fail with a clear warning.
4. Add an explicit escape hatch only if truly needed, such as
   `--force-portrait-blur-fill` or `allowPortraitSource=true`.
5. In the Studio UI, show a warning or disable the portrait bg-fill toggle when
   the selected source is already portrait.

Suggested default policy:

```text
if source_h > source_w and abs(source_w/source_h - target_w/target_h) < 0.02:
    portraitBlurFill.enabled = false
```

For Musia source videos, be stricter:

```text
source == musia and source is portrait -> disable bg-fill by default
```

## Acceptance Criteria

- A `2160x3840` Musia recording published with current Studio settings cannot
  silently produce a portrait-bgfilled output.
- `lazyedit_publish.py --video portrait.mp4 --process` should either:
  - auto-disable portrait bg-fill and log the reason; or
  - fail early with a clear message unless a force flag is provided.
- The backend burn endpoint should enforce the same rule, not only the CLI.
- The UI should not let stale portrait bg-fill settings accidentally affect
  already-portrait recordings.
- Non-portrait sources, such as horizontal LALACHAN videos, should still be able
  to use portrait bg-fill with aspect-ratio-preserving foreground geometry.

## Regression Test

Add a test fixture with:

```text
input: 2160x3840 portrait MP4
config: portraitBlurFill.enabled=true, width=1080, height=1920
expected: guard disables or rejects bg-fill
```

Also keep a horizontal fixture:

```text
input: 1920x1080 horizontal MP4
config: portraitBlurFill.enabled=true, width=1080, height=1920
expected: bg-fill remains allowed and preserves foreground aspect ratio
```

## Operator Rule Until Fixed

For Musia Fun-player portrait recordings, always use:

```text
--no-portrait-blur-fill
```

Capture the page directly as portrait:

```text
--width 2160 --height 3840
--css-width 1080 --css-height 1920
--device-scale-factor 2
```

Do not create a landscape master and then bg-fill it into portrait.
