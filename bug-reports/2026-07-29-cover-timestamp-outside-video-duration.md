# Cover Timestamp Outside Video Duration Blocks Publishing

## Summary

LazyEdit can accept a generated metadata cover timestamp that is later than the
video duration. `ffmpeg` may exit successfully without writing a frame, while
the cover extraction step is still reported as successful. The publication
session then has no cover file and remains `ready_for_publish: false`.

## Observed Impact

During publication session `57` for a `15.047s` video:

- generated metadata requested cover timestamp `00:10:44,000`;
- cover extraction returned without an error;
- no cover image was created;
- the cover stage remained idle and blocked package readiness;
- changing the timestamp to `00:00:10,000` and rerunning extraction produced
  the cover and allowed the existing session to publish.

## Expected Behavior

- Cover timestamps must be constrained to the source video duration.
- Cover extraction must only report success when a non-empty output image
  exists.
- An invalid generated timestamp should fall back to a safe frame without
  requiring manual metadata edits.

## Suggested Fix

1. Probe the selected publication video's duration.
2. Parse the metadata timestamp and clamp it to a valid range, for example
   `min(requested_time, max(duration - 0.25, 0))`.
3. After `extract_cover(...)`, require the destination file to exist and have a
   non-zero size.
4. If extraction fails, retry at a deterministic fallback such as the midpoint
   or one second before the end.
5. Return a clear error if both attempts fail.

## Regression Test

Use a 15-second fixture and metadata with cover `00:10:44,000`. The cover API
should create a valid image within the fixture duration, mark the cover stage
complete, and allow `ready_for_publish` to become true.
