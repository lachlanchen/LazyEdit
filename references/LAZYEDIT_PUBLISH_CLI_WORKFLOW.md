# LazyEdit Publish CLI Workflow

Date: 2026-06-03

This workflow documents how to publish videos through LazyEdit without manually driving the Studio UI.

## Studio And CLI State

- Web Studio: `http://127.0.0.1:18791/editor` and Publish tab.
- Backend API: `http://127.0.0.1:18787`.
- CLI: `scripts/lazyedit_publish.py`.
- Remote platform automation runs on `lazyingart` through AutoPublish at `http://lazyingart:8081/publish`.
- Installable Codex skill copy: `references/skills/lazyedit-publish-workflow`.
- Portable LazySkills copy: `/home/lachlan/DiskMech/Projects/LazySkills/skills/lazyedit-publish-workflow`.
- AgInTiFlow handoff note: `references/HANDOFF_AGINTIFLOW_LAZYEDIT_PUBLISH_SKILL_2026_06_03.md`.

The CLI writes normal LazyEdit publish jobs, so jobs appear in the webapp publish queue. CLI options do not rewrite saved Studio settings unless `--persist-settings` is passed.

## Parameter Rules

- `--use-current-settings` reads current Studio defaults: subtitle burn, language order, layout, polished subtitle usage, and publication mode.
- One-shot overrides such as `--platforms`, `--languages`, `--subtitle-lift-ratio`, and `--no-burn-subtitles` apply only to that CLI run unless `--persist-settings` is also used.
- `--languages` is bottom-to-top subtitle order.
- `--no-process` publishes the already finished output. Use this for a completed current output or completed publication session.
- `--publication-session-id <id>` publishes a specific run/session. Omit it for the current output.
- `--new-run` creates a new publication session and processes into that session.
- `--guided-monitor` prints progress for subtitle correction, processing, local publish queue, remote AutoPublish queue, and optional Pi-side tmux logs.

## Publish Existing Finished Output

Publish an already processed current output to Shipinhao only:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python scripts/lazyedit_publish.py \
  --video-id 346 \
  --use-current-settings \
  --platforms shipinhao \
  --no-process \
  --wait \
  --poll-seconds 10
```

Publish a completed output to YouTube and Instagram only:

```bash
python scripts/lazyedit_publish.py \
  --video-id 346 \
  --use-current-settings \
  --platforms youtube,instagram \
  --no-process \
  --wait
```

## Process Then Publish

Use current Studio settings but override platforms for one run:

```bash
python scripts/lazyedit_publish.py \
  --video-id 346 \
  --use-current-settings \
  --platforms youtube,instagram \
  --wait
```

Override languages without changing the webapp default:

```bash
python scripts/lazyedit_publish.py \
  --video-id 346 \
  --use-current-settings \
  --languages zh-Hant,ja,en \
  --platforms youtube,instagram \
  --wait
```

## LALACHAN Generated Video Workflow

For a generated video from `/home/lachlan/ProjectsLFS/LALACHAN`, copy it to Nutstore AutoPublish and wait for import, or upload it directly through the CLI:

```bash
cp -f /home/lachlan/ProjectsLFS/LALACHAN/Videos/example.mp4 \
  "/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/example_COMPLETED.mp4"
```

Confirm AutoPubMonitor imported the file and find the LazyEdit video id:

```bash
tmux capture-pane -pt autopub-monitor:0.1 -S -100 | tail -n 100
tmux capture-pane -pt autopub-monitor:0.2 -S -100 | tail -n 100
curl -fsS http://127.0.0.1:18787/api/videos | jq '.videos[:20] | map({id,title,created_at,file_path})'
```

Publish the imported video with prompt-backed correction, metadata context, and guided monitoring:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/example.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'" \
  --wait
```

Use the generated story/prompt/script file as both subtitle-correction background and metadata background. For correction, the script is only a reference. Use a human middle path: do not over-edit, and do not stay too conservative when the ASR is obviously abnormal, broken, or mismatched with the context. Read neighboring lines, check whether the sentence makes sense, compare it with the audio/Whisper text and the story context, then infer the most likely intended wording. Fix recognition errors, names, objects, and broken phrases while keeping timing/line structure stable where possible. Do not force the final subtitles to match the script verbatim when the audio or generated video differs. Keep `--use-polished` or current Studio polished defaults unless deliberately testing original subtitles.

If the raw prompt needs extra guardrails, create a temporary context wrapper under `temp/`, pass that as `--prompt-file`, and delete it after the run. Do not commit temporary wrappers, ZIPs, or generated runtime media.

## Monitoring

Local LazyEdit queue:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq '.jobs[:8]'
```

Remote AutoPublish queue:

```bash
curl -fsS http://lazyingart:8081/publish/queue | jq '.jobs[:8]'
```

Raspberry Pi browser automation log:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -120 | tail -n 120'
```

Shipinhao may require a WeChat QR scan. The automation emails the login prompt, then continues after the account is detected as logged in.

Final verification:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq '.jobs[:5] | map({id,video_id,status,platforms,remote_status,remote_job_id,error,updated_at})'
curl -fsS http://lazyingart:8081/publish/queue | jq '.jobs[-5:] | map({id,status,platforms,filename,error,updated_at})'
git status --short --untracked-files=no
```

## 2026-06-03 Run Notes

- Imported Nutstore videos became LazyEdit `video_id=346` and `video_id=347`.
- Published both one by one to YouTube and Instagram with current Studio settings.
- Reused the same finished current outputs for Shipinhao with `--no-process`.
- Final LazyEdit publish jobs:
  - `346`: YouTube/Instagram job `144`, Shipinhao job `146`.
  - `347`: YouTube/Instagram job `145`, Shipinhao job `147`.
- A local Codex skill was also added at `~/.codex/skills/lazyedit-publish-workflow/SKILL.md`.

## 2026-06-03 Typhoon Generated Video Publish

Generated video:

- `typhoon_pingpong_shark_duanpian_4x3_15s_2026_06_03_22_46_26_COMPLETED`
- LazyEdit imported it as `video_id=348`.

Command used:

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

Important behavior:

- The LALACHAN script was used as a correction reference for ASR errors, not as a verbatim subtitle target.
- Correction saved polished subtitles before processing.
- Processing completed transcribe, translation, subtitle burn, metadata, and cover extraction.
- Shipinhao waited at QR login; the long wait was useful and should remain.
- The QR expired once and the automation refreshed it, sent a new email, and continued after the user logged in.
- Remote automation then published Shipinhao, Instagram, and YouTube.

Final result:

- LazyEdit job `148`
- Remote AutoPublish job `job-1780500057985-7`
- Status `done`

## 2026-06-06 Firefly Cave Generated Video Publish

Generated video:

- `/home/lachlan/ProjectsLFS/LALACHAN/Videos/firefly_cave_cicada_rain_4x3_15s.mp4`
- Copied to `/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/firefly_cave_cicada_rain_4x3_15s_COMPLETED.mp4`
- LazyEdit imported it as `video_id=352`.

Prompt/context:

- `/home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-06-firefly-cave-cicada-rain-duanpian-15s.md`
- A temporary `temp/firefly_cave_publish_context.md` wrapper emphasized gentle correction and metadata context, then was deleted.

Command pattern used:

```bash
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

Important behavior:

- AutoPubMonitor imported the Nutstore file in one validation cycle.
- AI subtitle correction ran first and saved polished subtitles.
- Processing completed translation, subtitle burn, metadata, and cover extraction.
- Shipinhao required login, sent the email/QR flow, recovered after login, saved draft, waited for cover readiness, and published.
- Instagram published after the crop/next flow.
- YouTube upload completed, title and description were filled from generated metadata, and publish completed.

Final result:

- LazyEdit job `154`
- Remote AutoPublish job `job-1780723994544-13`
- Platforms: `shipinhao`, `youtube`, `instagram`
- Status `done`

## Tools And Scripts Used

- `scripts/lazyedit_publish.py`: CLI wrapper around LazyEdit upload, correction, processing, publish, and monitoring APIs.
- LazyEdit APIs: `/api/videos`, `/api/videos/<id>/subtitle-correction`, `/api/videos/<id>/process`, `/api/videos/<id>/process-status`, `/api/videos/<id>/publish`, `/api/autopublish/queue`.
- AutoPubMonitor panes: `autopub-monitor:0.0` sync, `0.1` watcher, `0.2` process queue, `0.3` manual monitor.
- Remote AutoPublish API: `http://lazyingart:8081/publish/queue`.
- Remote log tail: `ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'`.
- Local checks: `curl`, `jq`, `tmux capture-pane`, `ssh`, `rg`, and `git status`.
