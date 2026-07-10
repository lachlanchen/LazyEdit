# IMG_5500 Publish Fixes - 2026-07-10

## Scope

Video: `IMG_5500_2026_07_08_18_49_38_COMPLETED`

Requested publish targets: Shipinhao, Instagram, YouTube, Douyin.

Required render behavior:

- Keep native portrait videos as native portrait; do not apply portrait bg-fill when the display aspect already matches 9:16.
- Use the normal LazyEdit subtitle/logo pipeline.
- Keep the configured logo and publish settings.

## Problems Found

- Shipinhao changed the logged-out QR page structure. The QR iframe can now live under `#wx-oauth-container iframe`, and the old broad page-title detector could mistake a logged-in page for a login page.
- Shipinhao large uploads can show a preview and enabled publish button while the upload is still running. The old timeout was too short for large processed packages.
- Retrying a large package rewrote and re-extracted the same ZIP, wasting time on every retry.
- YouTube Studio no longer always renders the old final-check string, even when the upload is complete and the `Next` button is enabled.
- LazyEdit allowed portrait bg-fill to remain enabled for a native 2160x3840 portrait source.
- Local queue rows could remain stale when the remote AutoPublish queue was reachable but an old local remote job no longer existed remotely.

## Fixes Applied

- AutoPublish Shipinhao QR/login detection now recognizes the updated WeChat QR iframe and avoids treating a logged-in creator page as a login page.
- AutoPublish Shipinhao post-upload readiness now waits much longer and logs readiness state while uploads finish.
- AutoPublish supports `reuse_existing=true` for an already-copied package and skips extraction when ZIP members are already current.
- AutoPublish YouTube final-check wait now also accepts an upload-complete page with a visible enabled `Next` button.
- LazyEdit resolves portrait bg-fill against ffprobe display geometry and disables it when the source is already portrait with the target aspect ratio.
- LazyEdit CLI now records display width/height/rotation during preflight and applies the same native-portrait guard for one-shot publishes.
- LazyEdit queue merging can mark old missing remote jobs stale when the remote queue is reachable, keeping the publish pool from getting stuck on ghost rows.

## Validation

- `IMG_5500_..._subtitles_logo.mp4` was verified as `2160x3840`, no bg-fill, top-right logo, and normal subtitles.
- Douyin published and verified before the Shipinhao retry.
- Shipinhao published after QR login and post-upload wait fixes.
- Instagram published.
- YouTube published after the final-check wait was unblocked; the reusable fix is now in AutoPublish.

