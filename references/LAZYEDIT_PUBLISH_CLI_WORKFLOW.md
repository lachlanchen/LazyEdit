# LazyEdit Publish CLI Workflow

Date: 2026-06-03

This workflow documents how to publish videos through LazyEdit without manually driving the Studio UI.

Latest incident/runbook note:

- `references/PUBLISH_RUNBOOK_MUSIA_AND_PLATFORM_SMOOTHING_2026_06_30.md`

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
- If Studio logo settings are enabled, `--no-burn-subtitles` still creates a processed logo-only output ending in `_logo.mp4` and publishes that output. Translation is skipped because subtitles are disabled.
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

Create a no-subtitle video while keeping the configured Studio logo:

```bash
python scripts/lazyedit_publish.py \
  --video-id 346 \
  --use-current-settings \
  --no-burn-subtitles \
  --platforms youtube,instagram \
  --wait
```

This runs the burn step as a logo-only overlay when `logo_settings.enabled=true`
and `logo_settings.logoPath` is set. The output is H.264/AAC with `+faststart`.

For Musia recording videos, force the current Musia/MV default:
`--no-burn-subtitles --logo --logo-position top-right`. Verify a sample frame
or inspect the generated ZIP before real publish, because an older `_logo.mp4`
may still have the logo on the wrong side.

## Pure Shipinhao Music Package

For pure music/audio upload, use the AutoPublish package helper instead of the
LazyEdit video pipeline:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit/AutoPublish
python scripts/package_shipinhao_music.py \
  --audio /path/to/song.mp3 \
  --cover /path/to/artwork.png \
  --lyrics-json /path/to/musia/lyrics/mixed-vocal/mul.json \
  --title "Song Title" \
  --author "Musia 慕莎" \
  --language 中文 \
  --genre Pop \
  --story "Short music story for 音乐人说." \
  --output /tmp/song_shipinhao_music.zip \
  --post \
  --test
```

The helper sends `publish_shipinhao_music=true` when `--post` is used. Keep
`--test` for the first browser verification of a new Shipinhao music route;
remove it only after the form fields and `完成` button are visually confirmed.

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

## Failure Notes And Caveats Added 2026-06-07

Duplicate publishing:

- Do not use a real platform publish just to inspect the ZIP or logo output.
- For debugging, run `scripts/lazyedit_publish.py --no-publish` or publish with `--no-process` only after the processed output is verified.
- A previous debug cycle republished the same episode because the first real publish exposed a missing logo/packaging issue. The safer check is to inspect the generated ZIP and final MP4 path locally, then publish once only when the package is correct.

Logo packaging:

- Real publishes should burn the configured LazyEdit Studio logo, not a new uploaded asset.
- Confirm current logo state before CLI publishes:

```bash
curl -fsS http://127.0.0.1:18787/api/ui-settings/logo_settings | jq .
```

- Expected state is `enabled: true`, a valid `logoPath`, and top-left placement.
- Normal subtitle/logo outputs should end in `_subtitles_logo.mp4`.

Subtitle correction:

- Use the generated story/prompt/script as context for LALACHAN videos.
- Treat the script as reference, not a verbatim transcript. Correct clear ASR failures, broken phrases, names, and objects; avoid inventing unsupported dialogue.
- Do not patch recovered missing-language subtitles per video to regain colors. The general path is `lazyedit/subtitle_tokens.py` plus the burner wrapper: plain recovered text, ruby markup, `word`/`reading` tokens, and speaker-helper rows must all normalize into grammar-typed tokens before rendering.
- If the ASR misses obvious generated dialogue, the correction step may re-segment when the story/script is present. Verify the polished subtitle count before publishing:

```bash
sed -n '1,180p' DATA/VIDEO_FOLDER/*_mixed_polished.md
```

Metadata language:

- Chinese metadata should be Traditional Chinese at the root level. English metadata may still be generated separately for YouTube/Instagram.
- If Chinese metadata appears mostly English, rerun metadata generation with the same prompt/script context before publishing.

Nutstore import:

- Copy generated videos into the synced folder with a stable `_COMPLETED` filename.
- Watch both the AutoPubMonitor watcher and queue panes. The watcher detects the file first, then waits for stability before `process_queue.sh` imports it into LazyEdit.
- If a file was copied while LazyEdit was down, check logs before recopying; the wrapper should preserve failures so the queue is not silently dropped.

Remote publish monitoring:

- Shipinhao can pause for QR login and cover generation. Keep the long login wait behavior.
- Use the Pi tmux log to confirm upload, draft save, cover readiness, and final platform status:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'
```

## 2026-06-07 Mars Chip Factory Generated Video

Generated video:

- `/home/lachlan/ProjectsLFS/LALACHAN/Videos/mars_2d_atom_chip_factory_zhuangzi_15s.mp4`
- `/home/lachlan/ProjectsLFS/LALACHAN/outputs/xyq-2026-06-07-mars-chip/mars_2d_atom_chip_factory_zhuangzi_15s.mp4`

Prompt/script context:

- `/home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-07-mars-2d-atom-chip-factory-zhuangzi-duanpian-15s.md`
- Full story: `/home/lachlan/ProjectsLFS/LALACHAN/references/stories/2026-06-07-mars-2d-atom-chip-factory-zhuangzi.md`

Import command:

```bash
cp -f /home/lachlan/ProjectsLFS/LALACHAN/Videos/mars_2d_atom_chip_factory_zhuangzi_15s.mp4 \
  "/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/mars_2d_atom_chip_factory_zhuangzi_15s_COMPLETED.mp4"
```

Publish command pattern:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-07-mars-2d-atom-chip-factory-zhuangzi-duanpian-15s.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -n 140'" \
  --wait \
  --poll-seconds 10 \
  --process-timeout 7200 \
  --publish-timeout 7200
```
