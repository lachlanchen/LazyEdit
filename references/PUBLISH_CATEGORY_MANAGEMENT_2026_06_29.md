# Publish Category and Backfill Management

Date: 2026-06-29

## Forward Routing

LazyEdit now writes publish-routing fields into every video/music publish ZIP:

- `publish_category`
- `youtube_playlist`
- `playlist_name`
- `shipinhao_collection`

Default mapping:

| Content type | YouTube playlist | Shipinhao collection |
| --- | --- | --- |
| personal recordings / normal phone videos | `SimpleLife` | `简单生活` |
| LALACHAN story / Xiaoyunque videos | `LALACHAN` | `啦啦侠` |
| Musia music / art-track uploads | `Musia` | `Musia` |

The defaults can be overridden with environment variables:

```bash
LAZYEDIT_YOUTUBE_PLAYLIST_SIMPLELIFE=SimpleLife
LAZYEDIT_YOUTUBE_PLAYLIST_LALACHAN=LALACHAN
LAZYEDIT_YOUTUBE_PLAYLIST_MUSIC=Musia
LAZYEDIT_SHIPINHAO_COLLECTION_SIMPLELIFE=简单生活
LAZYEDIT_SHIPINHAO_COLLECTION_LALACHAN=啦啦侠
LAZYEDIT_SHIPINHAO_COLLECTION_MUSIC=Musia

AUTOPUB_YOUTUBE_PLAYLIST_SIMPLELIFE=SimpleLife
AUTOPUB_YOUTUBE_PLAYLIST_LALACHAN=LALACHAN
AUTOPUB_YOUTUBE_PLAYLIST_MUSIC=Musia
AUTOPUB_SHIPINHAO_COLLECTION_SIMPLELIFE=简单生活
AUTOPUB_SHIPINHAO_COLLECTION_LALACHAN=啦啦侠
AUTOPUB_SHIPINHAO_COLLECTION_MUSIC=Musia
```

For CLI publishes, use one-shot overrides:

```bash
python scripts/lazyedit_publish.py \
  --video /path/to/lalachan.mp4 \
  --publish-category lalachan \
  --platforms youtube,instagram,shipinhao \
  --wait
```

LazyEdit asks the metadata model to return `publish_category` as one of `simplelife`, `lalachan`, or `music`. The prompt tells it to choose `simplelife` for personal recordings, `lalachan` for LALACHAN/Xiaoyunque/Seedance fictional story videos, and `music` for Musia/song/audio-focused content. If the model is uncertain between personal recording and LALACHAN, it should choose `simplelife`. LALACHAN videos under `/home/lachlan/ProjectsLFS/LALACHAN/Videos` are still auto-routed to `lalachan` as a fallback. Music packages are always `music`.

## Backfill Tools

The platform-management tools live in AutoPublish:

- `AutoPublish/scripts/manage_y2b_videos.py`
- `AutoPublish/scripts/manage_shipinhao_videos.py`

Both attach to the existing logged-in Chromium sessions:

- YouTube: port `9222`
- Shipinhao: port `5006`

They are read-only by default. Anything destructive or mutating requires `--apply`.

### YouTube Inventory

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit/AutoPublish
python scripts/manage_y2b_videos.py inventory \
  --scrolls 80 \
  --output /tmp/youtube_inventory.json
```

The script extracts titles, links, video ids, visible row text, and a conservative `category_guess`. Music detection runs first and looks for `Musia`, `Musica`, `慕莎`, song/lyrics terms, and known song-title fragments. LALACHAN detection uses route hints such as `LALACHAN`, `啦啦侠`, `阿芽酱`, `飒飒君`, `小云雀`, `Seedance`, `Xiaoyunque`, and `duanpian`.

Dry-run all LALACHAN playlist moves:

```bash
python scripts/manage_y2b_videos.py move-lalachan \
  --playlist LALACHAN \
  --scrolls 80 \
  --output /tmp/youtube_lalachan_move_plan.json
```

Dry-run Musia playlist moves:

```bash
python scripts/manage_y2b_videos.py move-music \
  --playlist Musia \
  --scrolls 80 \
  --output /tmp/youtube_music_move_plan.json
```

Dry-run both music and LALACHAN moves from the same scan:

```bash
python scripts/manage_y2b_videos.py move-classified \
  --lalachan-playlist LALACHAN \
  --music-playlist Musia \
  --scrolls 80 \
  --output /tmp/youtube_classified_move_plan.json
```

Apply after reviewing the plan:

```bash
python scripts/manage_y2b_videos.py move-lalachan \
  --playlist LALACHAN \
  --scrolls 80 \
  --apply \
  --output /tmp/youtube_lalachan_move_result.json
```

Move one video:

```bash
python scripts/manage_y2b_videos.py move \
  --video-id VIDEO_ID \
  --playlist LALACHAN \
  --apply
```

Get links by query:

```bash
python scripts/manage_y2b_videos.py link --query "red sand" --scrolls 80
```

Delete is intentionally two-lock:

```bash
python scripts/manage_y2b_videos.py delete \
  --video-id VIDEO_ID \
  --title-contains "exact visible title fragment" \
  --apply
```

### Shipinhao Inventory

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit/AutoPublish
python scripts/manage_shipinhao_videos.py inventory \
  --scrolls 80 \
  --output /tmp/shipinhao_inventory.json
```

If Shipinhao changes the management URL, open the correct management page manually in the `5006` browser and run with `--url ""` to keep the current tab:

```bash
python scripts/manage_shipinhao_videos.py inventory --url "" --scrolls 80
```

Get links by query:

```bash
python scripts/manage_shipinhao_videos.py link --query "阿芽" --scrolls 80
```

Shipinhao delete is also two-lock:

```bash
python scripts/manage_shipinhao_videos.py delete \
  --query "visible title fragment" \
  --title-contains "same confirmed title fragment" \
  --apply
```

Existing-video Shipinhao collection moves are more UI-dependent than upload-time collection selection. The current tool inventories LALACHAN candidates first:

```bash
python scripts/manage_shipinhao_videos.py move-lalachan \
  --lalachan-collection 啦啦侠 \
  --scrolls 80 \
  --output /tmp/shipinhao_lalachan_candidates.json
```

Dry-run music candidates:

```bash
python scripts/manage_shipinhao_videos.py move-music \
  --music-collection Musia \
  --scrolls 80 \
  --output /tmp/shipinhao_music_candidates.json
```

Dry-run both categories from the same scan:

```bash
python scripts/manage_shipinhao_videos.py move-classified \
  --lalachan-collection 啦啦侠 \
  --music-collection Musia \
  --scrolls 80 \
  --output /tmp/shipinhao_classified_candidates.json
```

Use the generated candidate report to verify whether this account exposes collection editing on existing posts before applying any bulk move. When applying, use a small `--scrolls` value first for recent rows, or move one row by exact title fragment:

```bash
python scripts/manage_shipinhao_videos.py move \
  --query "visible title fragment" \
  --collection 啦啦侠 \
  --apply
```

## Caveats

- YouTube playlist moves depend on the logged-in Studio UI. If the playlist named `LALACHAN` or `Musia` does not exist, create it manually first or change the env var.
- Shipinhao upload-time collection selection is automated. Existing-post collection edits are more UI-dependent, so inventory first and apply in small batches.
- Never run bulk `--apply` before inspecting the exported plan.
