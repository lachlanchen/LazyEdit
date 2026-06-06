---
name: lazyedit-publish-workflow
description: Use when publishing videos through LazyEdit, AutoPubMonitor, AutoPublish on the lazyingart Raspberry Pi, Shipinhao, YouTube, Instagram, or LALACHAN-generated videos; covers direct CLI/API publishing, current-run reuse, one-shot settings overrides, subtitle correction prompts, Nutstore AutoPublish import, and monitoring/debugging the distributed publish workflow.
---

# LazyEdit Publish Workflow

Use this skill for normal LazyEdit publish tasks and for AI-generated videos from LALACHAN/RARACHAN that need subtitle correction, processing, and platform publishing.

## Runtime Map

- LazyEdit repo/backend: `/home/lachlan/DiskMech/Projects/lazyedit`
- Studio app: `http://127.0.0.1:18791/editor`
- LazyEdit API: `http://127.0.0.1:18787`
- Publish CLI: `scripts/lazyedit_publish.py`
- AutoPubMonitor repo: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Nutstore import folder: `/home/lachlan/Nutstore Files/AutoPublish/AutoPublish`
- Remote AutoPublish host: `ssh lachlan@lazyingart`
- Remote AutoPublish repo: `/home/lachlan/Projects/autopub`
- Remote publish API: `http://lazyingart:8081/publish`
- Remote tmux session: `autopub`

## Core Rule

Prefer the LazyEdit CLI over manual browser work. It creates normal LazyEdit jobs, so the webapp queue stays in sync.

Activate the environment first:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

## Setting Semantics

- `--use-current-settings` reads Studio defaults.
- One-shot flags such as `--platforms`, `--languages`, `--subtitle-lift-ratio`, and `--no-burn-subtitles` do not change Studio settings.
- Only `--persist-settings` writes CLI options back to the webapp preferences.
- `--languages` is bottom-to-top subtitle order.
- Use polished/corrected subtitles for real publishes and debug publishes unless the user explicitly requests original subtitles.
- `--no-process` reuses an already completed output. Use it when the user says "last run", "same version", or "already finished run".
- `--publication-session-id ID` targets a specific run. Omit it for the current output.

## Common Commands

Publish an already finished output:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms shipinhao,youtube,instagram \
  --no-process \
  --wait \
  --poll-seconds 10
```

Publish only YouTube and Instagram:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --platforms youtube,instagram --no-process --wait --poll-seconds 10
```

Publish only Shipinhao:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --platforms shipinhao --no-process --wait --poll-seconds 10
```

Process then publish:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --platforms youtube,instagram --wait --poll-seconds 10
```

Process/publish with lightweight guided monitoring:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -80 | tail -n 80'" \
  --wait \
  --poll-seconds 10
```

Use `--guided-monitor` when the user wants less manual supervision. It prints heartbeat progress during blocking subtitle correction, follows the local LazyEdit queue, checks the remote AutoPublish queue, and can periodically tail the Pi `autopub` tmux log. It should not restart services by itself; diagnose first, then intervene only when the queue reports failure or the logs show a clear stall.

Override languages for one run without changing Studio defaults:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --languages zh-Hant,ja,en --platforms youtube,instagram --wait
```

## LALACHAN / AI-Generated Video

If a generated video should go through the normal import path, copy it to Nutstore with a stable `_COMPLETED` name:

```bash
cp -f /home/lachlan/ProjectsLFS/LALACHAN/Videos/VIDEO.mp4 \
  "/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/VIDEO_COMPLETED.mp4"
```

Then watch AutoPubMonitor and find the imported LazyEdit video id:

```bash
tmux capture-pane -pt autopub-monitor:0.1 -S -100 | tail -n 100
tmux capture-pane -pt autopub-monitor:0.2 -S -100 | tail -n 100
curl -fsS http://127.0.0.1:18787/api/videos | jq '.videos[:20] | map({id,title,created_at,file_path})'
```

For direct upload with correction and metadata prompt:

```bash
python scripts/lazyedit_publish.py \
  --video /home/lachlan/ProjectsLFS/LALACHAN/Videos/VIDEO.mp4 \
  --title TITLE_COMPLETED \
  --use-current-settings \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/PROMPT.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --wait \
  --poll-seconds 10
```

Use the LALACHAN story/prompt/script as both subtitle-correction background and metadata background. For subtitle correction, treat the script as a reference, not a verbatim source. Use a human middle path: do not over-edit, and do not stay too conservative when the ASR is obviously abnormal, broken, or mismatched with the context. Read neighboring lines, check whether the sentence makes sense, compare it with the audio/Whisper text and the story context, then infer the most likely intended wording. Fix recognition errors, names, objects, and broken phrases while preserving timing and line structure where possible. The final corrected subtitles do not need to be identical to the script if the audio or generated video differs, and they should not invent unsupported content.

If the prompt needs extra guardrails, create a temporary context wrapper in `temp/`, pass it as `--prompt-file`, then delete it after the run. Do not commit temporary prompt wrappers, generated ZIPs, or runtime media.

If the user requests no rerun, use `--no-process`.

## Monitoring

Local LazyEdit queue:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq '.jobs[:8]'
```

Remote AutoPublish queue:

```bash
curl -fsS http://lazyingart:8081/publish/queue | jq '.jobs[:8]'
```

Remote browser automation:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -120 | tail -n 120'
```

AutoPubMonitor import/session:

```bash
tmux capture-pane -pt autopub-monitor:0.0 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.1 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.2 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.3 -S -120 | tail -n 120
```

## Shipinhao Notes

- Shipinhao may require a WeChat QR/login email. Keep monitoring after the user scans.
- Keep the long login wait behavior. It is intentional and useful when the user is away or misses the first QR.
- The automation should wait for upload completion, cover readiness, save draft, then publish.
- Current UI may not expose short title or cover upload; skip those if absent.
- Expected successful log includes `Successfully published on ShiPinHao.`

## AutoPubMonitor Notes

- Nutstore files copied into `/home/lachlan/Nutstore Files/AutoPublish/AutoPublish` are synced/imported by AutoPubMonitor.
- If a file is renamed while monitor is active, check the tmux panes and queue file before assuming it imported.
- If LazyEdit is down, AutoPubMonitor wrapper must preserve nonzero exit codes so queued files are not silently dropped.

## Handoff Checks

Before final response, verify:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq '.jobs[:8] | map({id,video_id,status,platforms,remote_status,remote_job_id,error})'
curl -fsS http://lazyingart:8081/publish/queue | jq '.jobs[:8] | map({id,status,platforms,filename,error,updated_at})'
```

Report the LazyEdit job id, remote job id, platforms, status, and whether processing was reused or rerun.

## Verified Run: 2026-06-03 Typhoon Ping Pong Shark

Request:

- Publish `typhoon_pingpong_shark_duanpian_4x3_15s_2026_06_03_22_46_26_COMPLETED` as before.
- Use generated-video subtitle correction from the LALACHAN prompt/script.

Method:

```bash
python scripts/lazyedit_publish.py \
  --video-id 348 \
  --use-current-settings \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-03-typhoon-pingpong-shark-duanpian-15s-4x3-budget200.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --wait \
  --poll-seconds 10
```

What happened:

- LazyEdit had already imported the Nutstore file as `video_id=348`.
- AI subtitle correction saved polished subtitles before processing.
- Processing completed: transcribe, translate, burn, metadata, cover.
- Shipinhao blocked on login until the user scanned the emailed QR.
- The QR expired once; the existing long wait refreshed it and sent a new email.
- After login, Shipinhao published, then Instagram published, then YouTube published.

Tools used:

- `scripts/lazyedit_publish.py` for API/CLI orchestration.
- `curl` + `jq` for LazyEdit and remote AutoPublish queue checks.
- `ssh lachlan@lazyingart` and `tmux capture-pane -pt autopub:0` for remote browser automation logs.
- `tmux capture-pane -pt autopub-monitor:*` for Nutstore/import checks.
- `rg` on the Pi after installing `ripgrep` for faster code/log searches.

Final result:

- LazyEdit job `148`
- Remote job `job-1780500057985-7`
- Platforms `shipinhao`, `youtube`, `instagram`
- Status `done`

## Verified Run: 2026-06-06 Firefly Cave

Request:

- Copy `/home/lachlan/ProjectsLFS/LALACHAN/Videos/firefly_cave_cicada_rain_4x3_15s.mp4` to Nutstore.
- Use `/home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-06-firefly-cave-cicada-rain-duanpian-15s.md` as subtitle/metadata context.
- Publish to `shipinhao`, `youtube`, and `instagram`.

Method:

```bash
cp -f /home/lachlan/ProjectsLFS/LALACHAN/Videos/firefly_cave_cicada_rain_4x3_15s.mp4 \
  "/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/firefly_cave_cicada_rain_4x3_15s_COMPLETED.mp4"

python scripts/lazyedit_publish.py \
  --video-id 352 \
  --use-current-settings \
  --prompt-file temp/firefly_cave_publish_context.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'" \
  --wait \
  --poll-seconds 10 \
  --process-timeout 3600 \
  --publish-timeout 7200
```

What happened:

- AutoPubMonitor imported the Nutstore file as `video_id=352`.
- AI correction saved polished subtitles first.
- Processing completed translation, burn, metadata, and cover.
- Shipinhao required QR login, recovered after login, saved draft, waited for cover readiness, and published.
- Instagram published after crop/Next; YouTube uploaded, filled title/description from metadata, and published.

Final result:

- LazyEdit job `154`
- Remote job `job-1780723994544-13`
- Platforms `shipinhao`, `youtube`, `instagram`
- Status `done`
