# Deployment Systems And Sync

This repo is the development source. The runtime deployments live in DiskMech and on the Raspberry Pi.

## Systems Overview
- Edit system (LazyEdit backend + Expo app)
  - Deployment path: `/home/lachlan/DiskMech/Projects/lazyedit`
  - Backend port: 18787
  - Expo app port: 18791
  - tmux session: `la-lazyedit` (left pane backend, right pane app)

- Monitor system (AutoPubMonitor)
  - Deployment path: `/home/lachlan/DiskMech/Projects/autopub-monitor`
  - tmux session: `autopub-monitor` (2x2 panes: sync | monitor, process | manual)
  - Default API base: `http://localhost:18787`
  - Flow: upload -> process -> publish via LazyEdit app API

- Publication system (AutoPublish)
  - Raspberry Pi: `lazyingart`
  - Path: `/home/lachlan/Projects/auto-publish`
  - Platforms: XiaoHongShu, Douyin, Bilibili, ShiPinHao, YouTube

## Sync Workflow (High Level)
1) Develop in `/home/lachlan/ProjectsLFS/LazyEdit`.
2) `git push` from this repo and submodules when ready.
3) Pull on deployments:
   - Edit system: `cd /home/lachlan/DiskMech/Projects/lazyedit && git pull --no-rebase origin main`
   - Monitor system: `cd /home/lachlan/DiskMech/Projects/autopub-monitor && git pull --no-rebase origin main`
   - Raspberry Pi: `cd /home/lachlan/Projects/auto-publish && git pull github main`

## Common Restart Commands
- LazyEdit tmux: `tmux kill-session -t la-lazyedit || true` then `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`
- AutoPubMonitor tmux: `./autopub_monitor/autopub_monitor_tmux_session.sh stop && ./autopub_monitor/autopub_monitor_tmux_session.sh start`
