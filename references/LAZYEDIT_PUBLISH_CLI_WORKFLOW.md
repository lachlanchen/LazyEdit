# LazyEdit Publish CLI Workflow

Date: 2026-06-03

This workflow documents how to publish videos through LazyEdit without manually driving the Studio UI.

## Studio And CLI State

- Web Studio: `http://127.0.0.1:18791/editor` and Publish tab.
- Backend API: `http://127.0.0.1:18787`.
- CLI: `scripts/lazyedit_publish.py`.
- Remote platform automation runs on `lazyingart` through AutoPublish at `http://lazyingart:8081/publish`.
- Installable Codex skill copy: `references/skills/lazyedit-publish-workflow`.
- AgInTiFlow handoff note: `references/HANDOFF_AGINTIFLOW_LAZYEDIT_PUBLISH_SKILL_2026_06_03.md`.

The CLI writes normal LazyEdit publish jobs, so jobs appear in the webapp publish queue. CLI options do not rewrite saved Studio settings unless `--persist-settings` is passed.

## Parameter Rules

- `--use-current-settings` reads current Studio defaults: subtitle burn, language order, layout, polished subtitle usage, and publication mode.
- One-shot overrides such as `--platforms`, `--languages`, `--subtitle-lift-ratio`, and `--no-burn-subtitles` apply only to that CLI run unless `--persist-settings` is also used.
- `--languages` is bottom-to-top subtitle order.
- `--no-process` publishes the already finished output. Use this for a completed current output or completed publication session.
- `--publication-session-id <id>` publishes a specific run/session. Omit it for the current output.
- `--new-run` creates a new publication session and processes into that session.

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

For a generated video from `/home/lachlan/ProjectsLFS/LALACHAN`, either copy it to Nutstore AutoPublish and wait for import, or upload it directly through the CLI:

```bash
python scripts/lazyedit_publish.py \
  --video /home/lachlan/ProjectsLFS/LALACHAN/Videos/example.mp4 \
  --title example_COMPLETED \
  --use-current-settings \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/example.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --wait
```

Use the generated story/prompt/script file as both subtitle-correction background and metadata background. For correction, the script is only a reference: compare it with the ASR subtitles, infer the most likely intended wording, fix recognition errors, and keep timing/line structure stable where possible. Do not force the final subtitles to match the script verbatim when the audio or generated video differs. Keep `--use-polished` or current Studio polished defaults unless deliberately testing original subtitles.

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

## 2026-06-03 Run Notes

- Imported Nutstore videos became LazyEdit `video_id=346` and `video_id=347`.
- Published both one by one to YouTube and Instagram with current Studio settings.
- Reused the same finished current outputs for Shipinhao with `--no-process`.
- Final LazyEdit publish jobs:
  - `346`: YouTube/Instagram job `144`, Shipinhao job `146`.
  - `347`: YouTube/Instagram job `145`, Shipinhao job `147`.
- A local Codex skill was also added at `~/.codex/skills/lazyedit-publish-workflow/SKILL.md`.
