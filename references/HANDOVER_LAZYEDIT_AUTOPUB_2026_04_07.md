# LazyEdit + AutoPub Monitor Handover

Date: 2026-04-07  
Prepared from Codex thread: `019d61fd-58e2-7bb0-99f1-b4e68d2fe327`

Status note:

- This note captures the repo state at handover time.
- Later work in the same repo has since implemented the local serial publish queue, the collapsible Studio queue UI, web upload streaming, and automatic preview-proxy backfill scheduling.
- Read this file as historical context for service/runtime assumptions and AutoPub Monitor behavior, not as the latest source of truth for the Studio publish/preview feature set.

## Scope

This note is for handing over current LazyEdit and AutoPub Monitor context to a new Codex session working in:

- `/home/lachlan/DiskMech/Projects/lazyedit`
- `/home/lachlan/DiskMech/Projects/autopub-monitor`

The main user-facing website is:

- `http://127.0.0.1:18791/editor`

## Current Runtime State

- `lazyedit.service` is active.
- `autopub-monitor.service` is active.
- Current tmux sessions observed:
- `lazyedit`
- `autopub-monitor`
- `transcription-sync`

Important service design detail:

- `lazyedit.service` and `autopub-monitor.service` are launcher-style services, not full runtime supervisors.
- `autopub-monitor.service` starts tmux sessions and exits successfully.
- If tmux sessions disappear later, `systemd` can still report the service as active.

## Important Dirty Worktree State

Before making changes, the next session should know the `lazyedit` repo is already dirty:

- `AutoPublish`
- `app.py`
- `app/app/(tabs)/editor.tsx`
- `app/app/video/[id]/process.tsx`
- `lazyedit/autocut_processor.py`
- `lazyedit/db.py`
- `lazyedit/video_captioner.py`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`
- `references/XIAOHONGSHU_AUTOPUBLISH_LAYOUT_CHANGE_2026_03.md`
- `vit-gpt2-image-captioning`
- `whisper_with_lang_detect` (git submodule dirty)
- `words.db` (untracked)

The `autopub-monitor` repo is also dirty:

- `autopub_monitor/autopub_monitor_tmux_session.sh`
- `autopub_monitor/install_autopub_monitor.sh`
- `.auto-readme-work/` (untracked)

Do not assume all current changes were made by the current session.

## What Was Already Fixed In LazyEdit

### 1. Preview proxy for black preview videos

Goal:

- Some uploaded/studio-added videos showed as black or not browser-playable in the publish/editor preview.

Current code locations:

- `/home/lachlan/DiskMech/Projects/lazyedit/app.py`
- preview proxy directory logic around `proxy_previews`
- API fields now expose `preview_media_url`
- frontend consumes `preview_media_url` in `/home/lachlan/DiskMech/Projects/lazyedit/app/app/(tabs)/editor.tsx`

What was done:

- Upload/studio-add paths were changed to create a browser-safe preview proxy for affected videos.
- API responses now return `preview_media_url`.
- The editor tab uses `preview_media_url || media_url` for display.

Known limitation:

- This is not yet documented as a guaranteed backfill for every historical video already in the database.
- The user now wants this to become an automatic fix for all videos, not only new uploads or selectively fixed ones.

### 2. Publish button misleading failure

Old behavior:

- First publish click could show `Publish failed: Process failed` even when the processing pipeline was simply still finishing.
- Clicking again later often worked.

Current code location:

- `/home/lachlan/DiskMech/Projects/lazyedit/app/app/(tabs)/editor.tsx`

What was changed:

- `waitForProcessReady()` now waits longer and checks readiness more carefully.
- The UI now shows active processing messages like `Processing: Burn subtitles` or similar step text.
- Slow processing is no longer treated immediately as a publish failure.

### 3. Deadlock around keyframe extraction / schema setup

Observed issue:

- PostgreSQL deadlock around keyframe extraction and schema/index creation.
- User saw errors like:
- `deadlock detected`
- relation lock conflict between `keyframe_extractions` and other schema activity

Current code locations:

- `/home/lachlan/DiskMech/Projects/lazyedit/lazyedit/db.py`
- `/home/lachlan/DiskMech/Projects/lazyedit/app.py`

What was changed:

- `ensure_schema()` was made effectively one-time/process-local guarded instead of racing during live request handling.
- Schema initialization is called at backend startup instead of repeatedly creating index/schema work in the middle of request execution.

### 4. Stale subtitle burn progress after backend crash

Observed issue:

- Burn subtitles could remain stuck at a stale progress percentage even though no worker was alive.
- UI looked like it was still processing but there was no live ffmpeg process.

Current code location:

- `/home/lachlan/DiskMech/Projects/lazyedit/app.py`
- helper `_get_latest_subtitle_burn_with_recovery(...)`

What was changed:

- Stale `subtitle_burns` rows are auto-recovered after crash/restart.
- Stuck rows are marked failed instead of pretending the burn is still active.
- Duplicate burn starts are blocked if a real active burn already exists.

### 5. Whisper/autocut GPU selection in LazyEdit

Observed issue:

- The user saw Whisper transcribe warnings like:
- `FP16 is not supported on CPU; using FP32 instead`
- even though CUDA worked.

Current code location:

- `/home/lachlan/DiskMech/Projects/lazyedit/app.py`

What was changed:

- LazyEdit’s transcription/autocut path no longer hardcodes GPU `1`.
- It now resolves GPU preference in this order:
- `LAZYEDIT_WHISPER_GPU_ID`
- `LAZYEDIT_CUDA_VISIBLE_DEVICES`
- `CUDA_VISIBLE_DEVICES`
- fallback to `0`

Practical meaning:

- On a one-GPU machine it should use GPU `0` by default.

### 6. Pillow/HarfBuzz segfault in translation/burn flow

Observed issue:

- Backend Python segfaulted in native text-rendering code after translations completed.
- The crash landed in Pillow’s bundled HarfBuzz path.

What was done:

- The `lazyedit` conda env had Pillow upgraded from `10.2.0` to `12.2.0`.
- The exact French translation flow was rerun and completed cleanly afterward.

Important interpretation:

- That crash looked like a LazyEdit runtime dependency problem, separate from the whole-machine freeze problem.

## What Is Known About AutoPub Monitor

Key scripts:

- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub_monitor_tmux_session.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub_sync.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/monitor_autopublish.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/process_queue.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub.py`

Current data path expectation:

- `/home/lachlan/AutoPublishDATA` is now a symlink to `/home/lachlan/DiskMech/AutoPublishDATA`

Current service file no longer requires the old mount:

- `/etc/systemd/system/autopub-monitor.service`

Pipeline summary:

1. `autopub_sync.sh` syncs files from the source/Nutstore-like area into `AutoPublishDATA/AutoPublish`.
2. `monitor_autopublish.sh` watches the local folder with `inotifywait`.
3. Valid files get appended to `queue_list.txt`.
4. `process_queue.sh` polls the queue and invokes `autopub.sh`.
5. `autopub.py` drives LazyEdit over the local backend API at port `18787`.

Important startup race:

- The watcher only sees future `close_write` and `moved_to` events.
- It does not do an initial scan of files already present in the directory.
- If a synced file lands before `inotifywait` is live, it can be missed.
- Renaming or touching the file later retriggers processing.

This exact startup race was already documented in the `autopub-monitor` repo README files.

## Current Product Requests From User

These are desired next tasks. They are not fully implemented yet.

### A. Make preview fixing automatic for all videos

User expectation:

- Every video in LazyEdit Studio should have a working preview automatically.
- No manual fix should be needed after adding a video.
- Historical videos should also be handled, not only newly uploaded ones.

Suggested implementation direction:

- Add a server-side backfill or lazy-on-read mechanism:
- When listing videos, if `preview_media_url` is missing or invalid and the source is a known black-preview format, create the proxy automatically.
- Add a one-shot backfill script or queue worker for historical rows.
- Cache the proxy path in the DB or derive it deterministically.

### B. Multi-video publish queue with persistent status

User expectation:

- The user can click publish on multiple videos.
- Publish requests stay in queue.
- Publish state survives refresh.
- Publish state survives switching between videos.
- UI shows queue and status clearly.

Suggested implementation direction:

- Add a DB-backed publish job table, not only in-memory task state.
- Use one worker queue per publish target or a global bounded queue.
- Expose queue/job status through API.
- Frontend should poll or subscribe to job state instead of relying on the currently selected video only.

### C. Avoid freezing the website during processing

User expectation:

- Processing should not freeze the web UI.
- Refreshing, switching videos, and monitoring should remain responsive during heavy work.

Suggested implementation direction:

- Move long-running work out of request threads.
- Use job records plus background workers.
- Do not run heavy processing inline inside Tornado request handlers.
- Prefer bounded worker pools and persisted job state over ad hoc threads only.
- Make all frontend status pages poll persisted state instead of blocking on request lifecycle.

## Current Assessment Of What Still Needs Design Work

There is already a partial preview fix, but not yet a complete productized strategy for:

- backfilling all historical videos
- guaranteeing proxy creation for every unsupported browser-preview format
- queuing publish actions across multiple videos
- showing queue state persistently across refreshes and video switches
- making long processing resilient and fully asynchronous at the product level

The next session should treat these as product/architecture tasks, not just one-off bug fixes.

## Suggested Handover Starting Points

If a new Codex session takes over in `lazyedit`, the first files worth reading are:

- `/home/lachlan/DiskMech/Projects/lazyedit/app.py`
- `/home/lachlan/DiskMech/Projects/lazyedit/lazyedit/db.py`
- `/home/lachlan/DiskMech/Projects/lazyedit/app/app/(tabs)/editor.tsx`
- `/home/lachlan/DiskMech/Projects/lazyedit/references/DEPLOYMENT_SYSTEMS.md`
- `/home/lachlan/DiskMech/Projects/lazyedit/references/TMUX_SESSIONS.md`
- `/home/lachlan/DiskMech/Projects/lazyedit/references/XIAOHONGSHU_AUTOPUBLISH_LAYOUT_CHANGE_2026_03.md`

For AutoPub Monitor, start with:

- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub_monitor_tmux_session.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub_sync.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/monitor_autopublish.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/process_queue.sh`
- `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub.py`

## Recommended First Handover Prompt

Suggested short prompt for the next `lazyedit` session:

> Read `references/HANDOVER_LAZYEDIT_AUTOPUB_2026_04_07.md` first. Then inspect the current preview proxy flow, publish readiness/status flow, and background processing architecture. Design a robust plan to 1) automatically fix preview playback for all videos including historical videos, 2) support multi-video publish queue with persisted status across refreshes, and 3) make processing non-blocking and durable so the website stays responsive during heavy work.
