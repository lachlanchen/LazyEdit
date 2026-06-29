# LazyEdit Portrait Blur-Fill

Date: 2026-06-29

## Source Research

LALACHAN has two blur-fill helpers:

- `/home/lachlan/ProjectsLFS/LALACHAN/scripts/video_blurfill.sh`
- `/home/lachlan/ProjectsLFS/LALACHAN/scripts/portrait_blurfill_subtitle_space.sh`

The current LALACHAN publishing behavior is closest to
`portrait_blurfill_subtitle_space.sh`:

- Output frame: `1080x1920` portrait.
- Background: same input frame, scaled to cover, cropped, blurred.
- Foreground: original frame kept sharp, scaled to full output width.
- Earlier default foreground offset: fixed `y=240`, intentionally higher than center to leave lower blurred space for subtitles.
- Quality defaults: Lanczos scaling, `gblur=36`, background brightness `-0.08`, saturation `1.08`, x264 CRF around `10-12`.
- Audio: copied when possible.

LazyEdit originally copied the fixed `y=240` default, but that placed 16:9
sources too close to the top. The current default is aspect-ratio-aware:

- Compute the exact vertically centered foreground position.
- Move that centered top offset upward by `centerShiftRatio`.
- Default `centerShiftRatio=0.1`.

For a typical 16:9 foreground scaled to 1080px wide, this puts the top margin
near 31% and the bottom margin near 38%, which is close to the desired
"top 30% / bottom 40%" placement while keeping other aspect ratios reasonable.

## LazyEdit Implementation

Backend helper:

- `lazyedit/portrait_blurfill.py`

The option is stored inside the existing `burn_layout` UI preference:

```json
{
  "portraitBlurFill": {
    "enabled": true,
    "mode": "lalachan",
    "width": 1080,
    "height": 1920,
    "foregroundWidth": 1080,
    "foregroundY": 240,
    "centerShiftRatio": 0.1,
    "blur": 36,
    "backgroundDim": -0.08,
    "backgroundSaturation": 1.08,
    "crf": 12,
    "preset": "slow",
    "scaleFlags": "lanczos",
    "audioMode": "copy"
  }
}
```

Modes:

- `lalachan`: default, exact center shifted upward by `centerShiftRatio`.
- `center`: foreground vertically centered; y input is ignored.
- `custom`: uses the saved foreground y value.

The feature is integrated into the existing burn/processed-output step:

- Subtitles on: portrait blur-fill first, then subtitles burn onto the portrait master.
- Subtitles off + logo on: portrait blur-fill first, then logo overlays.
- Subtitles off + logo off: portrait blur-fill alone still creates a processed output.
- Publishing uses the latest completed processed output through the existing subtitle-burn table, so ZIP generation and AutoPublish do not need a separate video selection path.

Output suffixes:

- `_portrait_blurfill.mp4`: intermediate source for later burn/logo.
- `_portrait.mp4`: portrait-only processed output.
- `_portrait_logo.mp4`: portrait plus logo, no subtitles.
- `_portrait_subtitles.mp4`: portrait plus subtitles.
- `_portrait_subtitles_logo.mp4`: portrait plus subtitles plus logo.

## UI

Publish tab controls:

- `Portrait blur fill`: enable or disable.
- `Portrait layout`: `LALACHAN`, `Center`, or `Custom`.
- `Center shift`: shown for `LALACHAN`; default `0.1`.
- `Foreground Y`: shown only for `Custom`; default `240`.

The settings are remembered through `burn_layout`, the same preference object used for subtitle rows, lift ratio, font size, and outline settings.

## API

One-shot process request:

```bash
curl -fsS http://127.0.0.1:18787/api/videos/VIDEO_ID/process \
  -H 'Content-Type: application/json' \
  -d '{
    "async": true,
    "steps": ["keyframes", "caption", "transcribe", "translate", "burn", "metadata_zh", "metadata_en", "cover"],
    "burnSubtitles": true,
    "portraitBlurFill": {
      "enabled": true,
      "mode": "lalachan",
      "centerShiftRatio": 0.1
    }
  }'
```

Logo or portrait-only without subtitles:

```json
{
  "steps": ["keyframes", "caption", "transcribe", "burn", "metadata_zh", "metadata_en", "cover"],
  "burnSubtitles": false,
  "portraitBlurFill": {"enabled": true, "mode": "lalachan"}
}
```

## CLI

Use current Studio defaults but enable portrait blur-fill for one run:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --portrait-blur-fill \
  --portrait-blur-mode lalachan \
  --portrait-center-shift-ratio 0.1 \
  --platforms youtube,instagram \
  --wait
```

Centered foreground:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --portrait-blur-fill \
  --portrait-blur-mode center \
  --platforms youtube,instagram \
  --wait
```

Portrait video without subtitles but still processed:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --no-burn-subtitles \
  --portrait-blur-fill \
  --platforms youtube,instagram \
  --wait
```

Add `--persist-settings` only when the CLI should save the portrait blur-fill choice back to Studio preferences.

## Verification

Basic checks performed:

- `python -m py_compile app.py lazyedit/portrait_blurfill.py scripts/lazyedit_publish.py`
- `npx tsc --noEmit` from `app/`
- Synthetic ffmpeg render from a 640x480 input to a `1080x1920` output with video and audio streams.

Important ffmpeg caveat found during testing:

- On this ffmpeg build, `-shortest` plus copied audio could produce an audio-only MP4 even though ffmpeg exited successfully.
- LazyEdit's helper does not use `-shortest`; the filtered video and audio come from the same input, so normal source duration alignment is preserved.
