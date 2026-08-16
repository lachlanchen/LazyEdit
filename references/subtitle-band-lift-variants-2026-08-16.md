# Subtitle Band Lift Variants

LazyEdit supports two valid vertical arrangements for a four-language subtitle band. Neither is the preferred default in this note; select the arrangement that fits the current video.

## Shared layout

The two inspected publications used the same relevant settings except for `liftRatio`:

```json
{
  "heightRatio": 0.4,
  "rows": 4,
  "cols": 1,
  "liftSlots": 0,
  "languagesTopToBottom": ["en", "ja", "zh-Hant", "fr"],
  "output": "1080x1920"
}
```

The portrait blur-fill composition and four language slots were otherwise equivalent.

## Variant A: lifted band

The Paris LALACHAN publication used:

```json
{
  "liftRatio": 0.1
}
```

This moves the entire subtitle band upward by 10% of the full frame height. On a `1920px` frame, the displacement is `192px`. English, Japanese, Chinese, and French all move upward together.

With a 40% subtitle band:

```text
band height = 1920 * 0.4 = 768px
lift = 1920 * 0.1 = 192px
band top = 1920 - 768 - 192 = 960px
```

This arrangement gives the lowest row more room below it and places English closer to the main picture.

## Variant B: bottom-anchored band

The later four-language robotic-arms publication used:

```json
{
  "liftRatio": 0.0
}
```

The band remains anchored to the bottom of the portrait frame:

```text
band height = 1920 * 0.4 = 768px
lift = 0px
band top = 1920 - 768 = 1152px
```

This keeps the English row at the established unlifted band height when another language is added. The additional language occupies another row inside the same band instead of moving the whole band upward.

## What actually changed

The new language did not automatically move English. The renderer calculates the band origin as:

```python
lift_pixels = int(frame_height * lift_ratio)
top_y = max(0, frame_height - band_height - lift_pixels)
```

Changing the number of rows changes each row's available height. Changing `liftRatio` moves every row together. The inspected difference is therefore exactly the explicit lift change from `0.1` to `0.0`, equal to `192px` at `1080x1920`.

## Operational guidance

- Use the lifted variant when the lower row needs extra clearance or the subtitle group should sit closer to the picture.
- Use the bottom-anchored variant when adding a language should leave the top language at the same vertical anchor as an unlifted layout.
- Keep `heightRatio`, row order, and portrait composition explicit when comparing layouts; otherwise more than one variable may move the text.
- Inspect a sample frame before publishing. A layout that is good for one source composition can be less suitable for another.

Verified examples:

- Paris LALACHAN: video `520`, publication session `67`, publish job `353`, `liftRatio=0.1`.
- Robotic arms: video `521`, publish job `355`, `liftRatio=0.0`.

Both published arrangements were accepted. This comparison does not change LazyEdit defaults and does not require either video to be republished.

Sample frames from both final `1080x1920` masters were inspected with active four-language subtitles and visually confirmed the calculated whole-band shift.
