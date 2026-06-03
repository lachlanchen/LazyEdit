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

Override languages for one run without changing Studio defaults:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --languages zh-Hant,ja,en --platforms youtube,instagram --wait
```

## LALACHAN / AI-Generated Video

If a generated video was copied into Nutstore AutoPublish, first find the imported LazyEdit video id:

```bash
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

Use the LALACHAN story/prompt/script as both subtitle-correction background and metadata background. For subtitle correction, treat the script as a reference, not a verbatim source: compare the ASR transcription with the generated script/story, infer the most likely intended wording, fix recognition errors, and preserve the subtitle timing and line structure where possible. The final corrected subtitles do not need to be identical to the script if the audio or generated video differs.

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
