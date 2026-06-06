# AgInTiFlow Handoff: LazyEdit Publish Skill

Date: 2026-06-03

## Purpose

This handoff gives AgInTiFlow a reusable skill for publishing videos through LazyEdit, AutoPubMonitor, and the AutoPublish host on `lazyingart`.

Do not install it automatically from this handoff. The user asked only to prepare the handoff and skill.

## Skill Artifact

Installable skill directory in this repo:

- `/home/lachlan/DiskMech/Projects/lazyedit/references/skills/lazyedit-publish-workflow`

The same skill is also installed for current local Codex sessions at:

- `/home/lachlan/.codex/skills/lazyedit-publish-workflow`

The portable public skill copy is maintained at:

- `/home/lachlan/DiskMech/Projects/LazySkills/skills/lazyedit-publish-workflow`
- `/home/lachlan/DiskMech/Projects/LazySkills/docs/lazyedit-publish-runbook.md`

## Suggested Install For AgInTiFlow

If AgInTiFlow wants to use the skill, copy the repo skill folder into its Codex skills location:

```bash
mkdir -p /home/lachlan/.codex/skills
cp -a /home/lachlan/DiskMech/Projects/lazyedit/references/skills/lazyedit-publish-workflow \
  /home/lachlan/.codex/skills/
```

If AgInTiFlow has its own skill/plugin packaging path, import the same directory as a standard Codex skill. The required file is `SKILL.md`.

## What The Skill Covers

- Publishing existing LazyEdit outputs without rerunning processing.
- Processing then publishing through `scripts/lazyedit_publish.py`.
- Publishing AI-generated LALACHAN/RARACHAN videos with story prompts for subtitle correction and metadata.
- Using the generated video script as a correction reference, not a verbatim target: compare script/story with ASR output, infer likely intended wording, fix recognition errors, and preserve subtitle timing.
- Copying generated videos to Nutstore AutoPublish, watching AutoPubMonitor import panes, then publishing by the imported LazyEdit `video_id`.
- Using `--guided-monitor` and remote tmux log tails to follow subtitle correction, processing, LazyEdit queue state, and Pi-side browser automation.
- One-shot CLI overrides versus persistent webapp Studio settings.
- Monitoring LazyEdit queue, remote AutoPublish queue, tmux panes, and Shipinhao login/publish state.
- Coordinating three systems:
  - LazyEdit backend/webapp on `/home/lachlan/DiskMech/Projects/lazyedit`
  - AutoPubMonitor on `/home/lachlan/DiskMech/Projects/autopub-monitor`
  - AutoPublish on `lazyingart:/home/lachlan/Projects/autopub`

## Key Operational Rules

- Prefer `scripts/lazyedit_publish.py` over manual browser control.
- `--use-current-settings` reads Studio defaults.
- CLI overrides do not change webapp settings unless `--persist-settings` is passed.
- `--no-process` reuses an already finished run/output.
- `--languages` is bottom-to-top order.
- Prefer polished/corrected subtitles unless the user explicitly asks for original subtitles.
- For generated videos, use the script/story to guide correction of ASR mistakes, but do not blindly copy the script if the audio differs.
- Subtitle correction should use a human middle path: not aggressive, not too conservative. If ASR is broken, strange, or context-mismatched, read neighboring lines and infer the most likely intended wording, while preserving timing and avoiding unsupported inventions.
- For Shipinhao, monitor `ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -120 | tail -n 120'`.
- Before claiming done, verify both `http://127.0.0.1:18787/api/autopublish/queue` and `http://lazyingart:8081/publish/queue` show the job as `done`.

## Recent Verified Example

On 2026-06-03, two Nutstore-imported videos were published through LazyEdit:

- `video_id=346`
  - YouTube/Instagram: LazyEdit job `144`, remote job `job-1780417501671-3`
  - Shipinhao: LazyEdit job `146`, remote job `job-1780457846482-5`
- `video_id=347`
  - YouTube/Instagram: LazyEdit job `145`, remote job `job-1780417878516-4`
  - Shipinhao: LazyEdit job `147`, remote job `job-1780458044387-6`

All four publish jobs completed successfully and appeared in the LazyEdit webapp queue.

## Reference

Read the detailed workflow note before operating:

- `/home/lachlan/DiskMech/Projects/lazyedit/references/LAZYEDIT_PUBLISH_CLI_WORKFLOW.md`
- `/home/lachlan/DiskMech/Projects/lazyedit/references/VIDEO_PUBLISH_CLI_HANDOFF.md`
- `/home/lachlan/DiskMech/Projects/LazySkills/docs/lazyedit-publish-runbook.md`
