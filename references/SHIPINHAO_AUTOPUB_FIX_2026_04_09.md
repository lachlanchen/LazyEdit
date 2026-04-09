# Shipinhao AutoPublish Fix Notes

Date: 2026-04-09

## Goal

Restore reliable Shipinhao publishing from LazyEdit and AutoPublish after the platform UI changed.

## Repositories and Hosts

- LazyEdit workspace: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPublish submodule inside LazyEdit: `/home/lachlan/DiskMech/Projects/lazyedit/AutoPublish`
- Live AutoPublish host: `lazyingart`
- Live repo on host: `~/Projects/autopub`
- Live tmux session on host: `autopub`
- Live AutoPublish HTTP endpoint: `http://lazyingart:8081`

## Main Problems Found

1. Shipinhao had moved away from the older top-document and breadcrumb-based DOM assumptions.
2. The live editor was inside `iframe[name="content"]`.
3. Selenium element references were going stale after upload because the page re-rendered.
4. Cover upload was no longer a stable requirement and could trigger a top-level “暂时无法使用该功能” modal.
5. Upload detection needed to read the real preview state instead of waiting on old text markers.
6. Post-upload editor controls could appear later than the first preview-ready signal, so publishing too early remained risky.
7. Collection selection markup changed from the older `.display-text` pattern to a selected-value node under `.collection-text span`.

## Effective Fixes

1. Switched the upload flow to target `iframe[name="content"]`.
2. Replaced brittle Selenium file input handling with CDP file upload where needed.
3. Detected upload completion from the content-frame preview state instead of old hidden-text indicators.
4. Skipped cover upload entirely for the new Shipinhao UI.
5. Reworked post-upload actions to use content-frame DOM actions rather than stale Selenium elements.
6. Added explicit verification for:
   - description field write
   - short title field write
   - original-declaration checkboxes
7. Added a post-upload stabilization wait so Shipinhao only proceeds after the editor controls are present and stable.
8. Updated collection handling to read the selected value from the current DOM structure instead of the older `.display-text` node.

## Verified Live Behavior

Confirmed on the live `autopub` tmux session:

- video upload completes
- description is written
- short title is written
- original declaration flow completes
- publish button is clicked
- Shipinhao returns success

Examples from live logs:

- `Shipinhao description set (224 chars).`
- `Shipinhao short title set to: '中文的獨特性'`
- `Shipinhao post-upload editor is stable: {... 'ready': True, 'uploading': False}`
- `Process completed successfully!`
- `Successfully published on ShiPinHao.`

## Tools Used

- `ssh lazyingart`
- `tmux capture-pane -pt autopub:0.0`
- AutoPublish queue endpoint:
  - `http://127.0.0.1:8081/publish/queue`
- Direct duplicate publish POSTs to:
  - `http://lazyingart:8081/publish?...&publish_shipinhao=true`
- Chrome remote debugging on host:
  - `127.0.0.1:5006`
- Selenium + CDP inspection against the live browser

## How The Host Is Controlled

1. Connect with `ssh lazyingart`.
2. Inspect runtime with `tmux capture-pane -pt autopub:0.0`.
3. Restart service process inside tmux when deploying new code:
   - send `C-c`
   - rerun `/home/lachlan/venvs/autopub/bin/python /home/lachlan/Projects/autopub/app.py --refresh-time 1800 --port 8081`
4. Pull latest AutoPublish on the host:
   - `cd ~/Projects/autopub && git pull --rebase --autostash origin main`
5. Use the queue endpoint and tmux together:
   - queue endpoint for machine-readable state
   - tmux for the real authoritative progress/failure details

## Important Remaining Note

Collection selection is not a blocker for successful publish. The live account/session clearly exposes `简单生活`, and the latest code now targets the new selected-value DOM. If the log still reports a collection issue on a future run, treat it as a UI-selector regression to inspect, not evidence that the collection is unavailable.
