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
- For Shipinhao, monitor `ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -120 | tail -n 120'`.

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
