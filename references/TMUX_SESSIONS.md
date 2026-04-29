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
| `lazyedit` | systemd service | `/etc/systemd/system/lazyedit.service` | Calls `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`. |
| `autopub-monitor` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Main 2x2 tmux session created by `autopub_monitor_tmux_session.sh`. |
| `transcription-sync` | systemd service | `/etc/systemd/system/autopub-monitor.service` | Staged rsync loop session created by `autopub_monitor_tmux_session.sh`; waits for Enter. |

## By Script / Service

### `/home/lachlan/scripts/create_tmux_session.sh`
- `sys-base`
- `ll-lll`
- `gs-gpt-sovits`
- `em-voice-api`
- `em-ngrok-api`

### `/home/lachlan/DiskMech/Projects/autopub-monitor/autopub_monitor/autopub_monitor_tmux_session.sh`
- `autopub-monitor`
- `transcription-sync`

### `/home/lachlan/DiskMech/Projects/lazyedit/start_lazyedit.sh`
- `lazyedit`

## Notes

- `lazyedit.service` uses `start_lazyedit.sh` in `DiskMech/Projects/lazyedit` (current service config).
- Standard session name for the current deployment is `lazyedit`.
- `autopub-monitor` contains the sync, monitor, process, and manual panes inside a
  single session; only `transcription-sync` is a separate extra session.
