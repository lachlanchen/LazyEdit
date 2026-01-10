# Tmux Session Map

This file maps each tmux session name to the script or service that creates it.

## By Session

| Session | Created by | Script/Service | Notes |
| --- | --- | --- | --- |
| `sys-base` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Base tmux session bootstrap. |
| `ll-lll` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs `Projects/lll/local_server_tornado.py`. |
| `gs-gpt-sovits` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs GPT-SoVITS `api_v2.py`. |
| `em-voice-api` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs `Projects/EchoMind/apis/api_server.py`. |
| `em-ngrok-api` | manual script | `/home/lachlan/scripts/create_tmux_session.sh` | Runs `ngrok http` for `em-voice-api`. |
| `la-lazyedit` | systemd service | `/etc/systemd/system/lazyedit.service` | Calls `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`. |
| `am-manual` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Runs `autopub.py` with cache flags. |
| `am-monitor` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |
| `am-process-queue` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |
| `am-transcription-sync` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |
| `am-video-sync` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Created by `autopub_monitor_tmux_session.sh`. |

## By Script / Service

### `/home/lachlan/scripts/create_tmux_session.sh`
- `sys-base`
- `ll-lll`
- `gs-gpt-sovits`
- `em-voice-api`
- `em-ngrok-api`

### `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub_monitor_tmux_session.sh`
- `am-video-sync`
- `am-monitor`
- `am-process-queue`
- `am-transcription-sync`
- `am-manual`

### `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`
- `la-lazyedit`

## Notes

- `lazyedit.service` uses `start_lazyedit.sh` in `DiskMech/Projects/lazyedit` (current service config).
- There is also a legacy helper `/home/lachlan/scripts/start_lazyedit.sh` that creates `la-lazyedit` under
  `/home/lachlan/ProjectsM/lazyedit`.
