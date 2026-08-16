# Async Preview Probe and Publish Recovery

Date: 2026-08-16

## Problem

`GET /api/videos` enriched up to 100 rows with preview information. When a row
had no proxy, `_preview_info_for_video()` synchronously called `ffprobe` through
`_should_create_preview_proxy()`. Repeated Studio requests therefore blocked the
single Tornado request loop while a real publish job was trying to submit to
AutoPublish. The job failed before it acquired a remote job ID.

## Fix

- `_preview_info_for_video()` now returns current state immediately.
- `_enqueue_preview_probe()` runs codec/HDR probing on `PROXY_EXECUTOR`.
- `PROBING_PREVIEW_VIDEO_IDS` prevents duplicate probes while
  `QUEUED_PREVIEW_VIDEO_IDS` continues to prevent duplicate proxy/poster work.
- Preview backfill uses the same asynchronous probe path.
- `ffprobe` has a five-second timeout as a final process guard.

The browser/UI may briefly report `needs_preview_proxy=false` while the
background probe is pending. This field is advisory; the source video remains
directly playable, and a required proxy/poster is queued asynchronously.

## Regression Test

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python -m unittest tests.test_preview_probe_async
```

The test patches `_should_create_preview_proxy()` and proves it is never called
from `_preview_info_for_video(..., auto_enqueue=True)`.

Runtime check:

```bash
curl -fsS -o /dev/null -w '%{http_code} %{time_total}\n' \
  http://127.0.0.1:18787/api/videos
```

## Agent Rule

When an exact `video_id` or publish job ID is already known, agents should use
that identity and inspect the exact local/remote queue. Do not compensate for a
slow `/api/videos` endpoint by scanning for nearby videos or submitting another
publish. A request-path latency defect belongs in LazyEdit; retries and terminal
verification belong to the calling orchestrator.
