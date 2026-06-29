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
sources too close to the top and did not express the real requirement. The
current default is bottom-space-aware:

- Target a lower blurred reserve of `bottomSpaceRatio=0.4`.
- Scale the sharp foreground to full output width when that still leaves the
  requested bottom reserve.
- If a tall source cannot leave the requested bottom reserve at full width,
  reduce the foreground width just enough to fit.
- Clamp the computed foreground y coordinate to the legal output range.

For a typical 16:9 foreground scaled to 1080px wide, this puts the top margin
near 28% and the bottom margin at 40%. For a typical 4:3 foreground, the top
margin becomes about 18% while the bottom still stays near 40%. The top is
therefore derived from source aspect ratio; the design anchor is the lower
space.

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
    "bottomSpaceRatio": 0.4,
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

- `lalachan`: default, keeps roughly `bottomSpaceRatio` of the output height
  below the sharp foreground.
- `center`: foreground vertically centered; y input is ignored.
- `custom`: uses the saved foreground y value.

`centerShiftRatio` is still accepted as a legacy input field for older callers,
but it is no longer the active placement rule for `lalachan` mode.

Default geometry examples for a `1080x1920` output and `bottomSpaceRatio=0.4`:

- `16:9` landscape: sharp foreground remains `1080px` wide, `y=544`, bottom
  reserve `768px`.
- `4:3` landscape: sharp foreground remains `1080px` wide, `y=342`, bottom
  reserve `768px`.
- `9:16` portrait: full width would leave no lower reserve, so the foreground
  is narrowed to about `648px`, `y=0`, bottom reserve `768px`.

This is intentional: normal landscape clips keep full-width sharp content, while
taller clips are narrowed only when needed to keep the configured lower space
legal.

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
- `Bottom space`: shown for `LALACHAN`; default `0.4`.
- `Foreground Y`: shown only for `Custom`; default `240`.
- `Calculated layout`: reads the selected source video's real metadata and
  shows computed top, foreground size, bottom reserve, and center-relative
  shift.
- `View layout`: opens a modal with a scaled `1080x1920` visualization of the
  top region, sharp foreground, and bottom reserve.

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
      "bottomSpaceRatio": 0.4
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
  --portrait-bottom-space-ratio 0.4 \
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
- Synthetic ffmpeg renders from `16:9`, `4:3`, and `9:16` inputs to
  `1080x1920` outputs with video and audio streams.
- Geometry probe with default `bottomSpaceRatio=0.4`:
  - `16:9`: foreground width `1080`, y `544`.
  - `4:3`: foreground width `1080`, y `342`.
  - `9:16`: foreground width `648`, y `0`.

Important ffmpeg caveat found during testing:

- On this ffmpeg build, `-shortest` plus copied audio could produce an audio-only MP4 even though ffmpeg exited successfully.
- LazyEdit's helper does not use `-shortest`; the filtered video and audio come from the same input, so normal source duration alignment is preserved.
