# Video List Preview Probe Can Block the API

## Summary

`GET /api/videos` performs synchronous preview checks for up to 100 rows. The
check calls `ffprobe` without a timeout. A slow or malformed media file can
therefore occupy the Tornado I/O loop long enough for unrelated lightweight
requests, including `/api/ui-settings/*`, to time out.

## Observed Impact

During a normal `lazyedit_publish.py` run on 2026-07-15:

- subtitle correction completed for video `481`;
- subsequent settings reads timed out;
- the backend accumulated many `CLOSE_WAIT` sockets;
- the active child was an unbounded `ffprobe` launched by
  `_should_create_preview_proxy()` for an unrelated 4K video;
- no publication session or publish job was created for video `481`.

The publish succeeded after pausing the congested backend and using a clean
backend instance against the same database.

## Relevant Path

`VideosHandler.get()` calls `_preview_info_for_video(..., auto_enqueue=True)`
for each returned row. `_should_create_preview_proxy()` invokes
`subprocess.run(["ffprobe", ...])` synchronously and without `timeout=`.

## Expected Behavior

- A health or settings request must not wait for media probing.
- One slow video must not block the Tornado I/O loop.
- Abandoned client requests must not leave long-lived probe work and sockets.

## Suggested Direction

1. Add a short timeout to every preview `ffprobe` call and handle
   `TimeoutExpired` as an enqueue/fallback condition.
2. Move preview probing and generation to the existing background queue.
3. Cache probe results by path plus file size/mtime.
4. Keep `/api/videos` limited to database and cached preview state.
5. Add a lightweight `/api/health` endpoint and use it for service checks.

## Regression Test

Create one video whose probe command exceeds the timeout, request
`GET /api/videos`, then concurrently request
`GET /api/ui-settings/publish_options`. The settings response should complete
quickly and the video list should return cached/fallback preview state.
