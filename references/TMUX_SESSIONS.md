# Tmux Session Map

This file maps each tmux session name to the script or service that creates it.

## By Session

| Session | Created by | Script/Service | Notes |
| --- | --- | --- | --- |
| `base` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Base tmux session bootstrap. |
| `autopub-manual` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs `autopub.py` with cache flags. |
| `lll` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs `Projects/lll/local_server_tornado.py`. |
| `gpt-sovits` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs GPT-SoVITS `api_v2.py`. |
| `voice-api` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs `Projects/EchoMind/apis/api_server.py`. |
| `ngrok-api` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs `ngrok http` for `voice-api`. |
| `lazyedit` | systemd service | `/etc/systemd/system/lazyedit.service` | Calls `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`. |
| `monitor-autopub` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |
| `process-queue` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |
| `transcription-sync` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |
| `video-sync` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |

## By Script / Service

### `/home/lachlan/scripts/create_tmux_session.sh`
- `base`
- `autopub-manual`
- `lll`
- `gpt-sovits`
- `voice-api`
- `ngrok-api`

### `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub_monitor_tmux_session.sh`
- `video-sync`
- `monitor-autopub`
- `process-queue`
- `transcription-sync`

### `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`
- `lazyedit`

## Notes

- `lazyedit.service` uses `start_lazyedit.sh` in `DiskMech/Projects/lazyedit` (current service config).
- There is also a legacy helper `/home/lachlan/scripts/start_lazyedit.sh` that creates `lazyedit` under
  `/home/lachlan/ProjectsM/lazyedit`.
