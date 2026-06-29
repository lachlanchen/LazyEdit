# Shipinhao Mirror Management

Date: 2026-06-29

This workflow is separate from publication. Use it to mirror existing
Shipinhao posts, match them to LazyEdit metadata/history, and plan safe
maintenance actions.

## Current Finding

Six older Shipinhao rows on the first management page have date-only visible
descriptions and can be matched back to LazyEdit metadata by publish time:

- `2026-06-23 11:18` -> `紀念日單軌列車與泰迪熊`
- `2026-06-22 21:57` -> `地板下的金色秘密`
- `2026-06-21 16:24` -> `橄欖油當洗髮水？結局笑翻`
- `2026-06-21 16:21` -> `橄欖油當洗髮水？結局笑翻`
- `2026-06-21 16:06` -> `日語朗讀測試：史記·孔子世家`
- `2026-06-21 15:44` -> `輕盈前髮修剪技巧分享`

A real one-row apply probe on `2026-06-23 11:18` still returns
`unsupported-description-repair`: Shipinhao opens `coverEdit`, but for a blank
description row the edit area is empty and no full description editor is
exposed. The current visible desktop UI only supports modifying selected
existing text with a 20-character limit, so blank descriptions cannot be
restored through this UI yet.

## Stronger Mirror Tool

The implementation is in AutoPublish:

- `scripts/manage_shipinhao_videos.py`
- `scripts/shipinhao_mirror_manager.py`
- `docs/SHIPINHAO_MIRROR_MANAGEMENT.md`

The manager now captures row image/cover URLs, links, row attributes, local
metadata hashes, local cover hashes, ZIP fingerprints, and LazyEdit publish job
history into a SQLite DB.

## Commands

Mirror the live Shipinhao page on the Pi:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/shipinhao_mirror_manager.py mirror --scrolls 5 --output /tmp/shipinhao_mirror.json'
```

Build local LazyEdit evidence:

```bash
python AutoPublish/scripts/shipinhao_mirror_manager.py export-metadata --metadata-root DATA --days 120 --output /tmp/lazyedit_shipinhao_metadata_index.json
python AutoPublish/scripts/shipinhao_mirror_manager.py export-publish-history --limit 500 --output /tmp/lazyedit_shipinhao_publish_history.json
```

Build the management DB and plan:

```bash
python AutoPublish/scripts/shipinhao_mirror_manager.py sync-db \
  --db /tmp/shipinhao_management.sqlite \
  --mirror /tmp/shipinhao_mirror.json \
  --metadata-index /tmp/lazyedit_shipinhao_metadata_index.json \
  --publish-history /tmp/lazyedit_shipinhao_publish_history.json \
  --output-plan /tmp/shipinhao_description_plan.json
```

Inspect:

```bash
python AutoPublish/scripts/shipinhao_mirror_manager.py db-report --db /tmp/shipinhao_management.sqlite --limit 20
```

Apply only after inspecting the plan. Start with one row:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/shipinhao_mirror_manager.py apply-descriptions --plan /tmp/shipinhao_description_plan.json --db /tmp/shipinhao_management.sqlite --apply --limit 1 --output /tmp/shipinhao_description_apply_limit1.json'
```

The tool records every attempt in `shipinhao_apply_attempts`, including
unsupported UI states.
