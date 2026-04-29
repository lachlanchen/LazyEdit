# Deployment Systems And Sync

This repo is the development source. The runtime deployments live in DiskMech and on the Raspberry Pi.

## Systems Overview
- Edit system (LazyEdit backend + Expo app)
  - Deployment path: `/home/lachlan/DiskMech/Projects/lazyedit`
  - Backend port: 18787
  - Expo app port: 18791
  - tmux session: `lazyedit` (left pane backend, right pane app)

- Monitor system (AutoPubMonitor)
  - Deployment path: `/home/lachlan/DiskMech/Projects/autopub-monitor`
  - tmux: `autopub-monitor` (2x2 panes: sync | monitor, process | manual) + `transcription-sync`
  - Default API base: `http://localhost:18787`
  - Flow: upload -> process -> publish via LazyEdit app API
  - Conda env: `autopub-video`
  - Notes:
    - `autopub-monitor.service` is mount-aware for `/home/lachlan`, `/home/lachlan/DiskMech`, and `/home/lachlan/AutoPublishDATA`
    - the manual pane stages the `autopub.py --force` command and waits for Enter
    - the `transcription-sync` session stages its rsync loop and waits for Enter
    - steady write churn comes mainly from `autopub_sync.sh` and log appends, not queue locks or `/dev/shm` temp files

- Publication system (AutoPublish)
  - Raspberry Pi: `lazyingart`
  - Path: `/home/lachlan/Projects/autopub`
  - Platforms: XiaoHongShu, Douyin, Bilibili, ShiPinHao, YouTube
  - Runtime secrets: `/home/lachlan/Projects/autopub/.env`
  - Notes:
    - repo `.env` is the source of truth; `.bashrc` is only a fallback
    - Gmail SMTP uses `APP_PASSWORD`
    - current visible account label is commonly `LazyingArt懒人艺术`

## Sync Workflow (High Level)
1) Develop in `/home/lachlan/ProjectsLFS/LazyEdit`.
2) `git push` from this repo and submodules when ready.
3) Pull on deployments:
   - Edit system: `cd /home/lachlan/DiskMech/Projects/lazyedit && git pull --no-rebase origin main`
   - Monitor system: `cd /home/lachlan/DiskMech/Projects/autopub-monitor && git pull --no-rebase origin main`
   - Raspberry Pi: `cd /home/lachlan/Projects/autopub && git pull github main`

## Common Restart Commands
- LazyEdit tmux: `tmux kill-session -t lazyedit || true` then `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`
- AutoPubMonitor tmux: `./autopub_monitor/autopub_monitor_tmux_session.sh stop && ./autopub_monitor/autopub_monitor_tmux_session.sh start`

## Related References

- `references/XIAOHONGSHU_AUTOPUBLISH_LAYOUT_CHANGE_2026_03.md`
