# Publish Category and Backfill Management

Date: 2026-06-29

LazyEdit and AutoPublish share one `publish_category` contract. LazyEdit writes
the category into the publish ZIP metadata; AutoPublish resolves that category
to a YouTube playlist and Shipinhao collection.

## Category Contract

| Category | Use For | YouTube | Shipinhao | Instagram |
| --- | --- | --- | --- | --- |
| `simplelife` | personal/self recordings, real-world daily videos | `SimpleLife` | `简单生活` | normal caption/tags |
| `lazyingart` | LazyingArt brand, product, shop, portfolio posts | `LazyingArt` | `懒人艺术` | normal caption/tags |
| `musia` | pure Musia songs, audio/art-track uploads | `Musia` | `Musia` | normal caption/tags |
| `lalachan` | LALACHAN story videos that are not primarily MVs | `LALACHAN` | `啦啦侠` | normal caption/tags |
| `lalamv` | LALACHAN character music videos and song-led MVs | `LalaMV` | `LalaMV` | normal caption/tags |

`music` is only a backwards-compatible alias for `musia`.

## LazyEdit Publish Overrides

For an MV, use `lalamv` explicitly:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --publish-category lalamv \
  --youtube-playlist LalaMV \
  --shipinhao-collection LalaMV \
  --platforms shipinhao,youtube,instagram \
  --wait
```

Forward metadata fields:

- `publish_category`
- `youtube_playlist` / `playlist_name`
- `shipinhao_collection`

LazyEdit metadata prompts and schemas should allow exactly:

```text
simplelife, lazyingart, musia, lalachan, lalamv
```

## Environment Overrides

```bash
LAZYEDIT_YOUTUBE_PLAYLIST_SIMPLELIFE=SimpleLife
LAZYEDIT_YOUTUBE_PLAYLIST_LAZYINGART=LazyingArt
LAZYEDIT_YOUTUBE_PLAYLIST_MUSIA=Musia
LAZYEDIT_YOUTUBE_PLAYLIST_LALACHAN=LALACHAN
LAZYEDIT_YOUTUBE_PLAYLIST_LALAMV=LalaMV

LAZYEDIT_SHIPINHAO_COLLECTION_SIMPLELIFE=简单生活
LAZYEDIT_SHIPINHAO_COLLECTION_LAZYINGART=懒人艺术
LAZYEDIT_SHIPINHAO_COLLECTION_MUSIA=Musia
LAZYEDIT_SHIPINHAO_COLLECTION_LALACHAN=啦啦侠
LAZYEDIT_SHIPINHAO_COLLECTION_LALAMV=LalaMV
```

AutoPublish equivalents use the `AUTOPUB_` prefix.

## Validation

Run on the AutoPublish host:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python - <<'"'"'PY'"'"'
from publish_routing import category_names, infer_publish_category, resolve_shipinhao_collection, resolve_youtube_playlist

expected = {
    "simplelife": ("SimpleLife", "简单生活"),
    "lazyingart": ("LazyingArt", "懒人艺术"),
    "musia": ("Musia", "Musia"),
    "lalachan": ("LALACHAN", "啦啦侠"),
    "lalamv": ("LalaMV", "LalaMV"),
}
for category, names in expected.items():
    actual = category_names(category)
    assert (actual["youtube_playlist"], actual["shipinhao_collection"]) == names, actual

metadata = {"publish_category": "lalamv", "title": "Aya Chan Hikari Ame"}
assert infer_publish_category(metadata)[0] == "lalamv"
assert resolve_youtube_playlist(metadata) == "LalaMV"
assert resolve_shipinhao_collection(metadata) == "LalaMV"
print("category routing ok")
PY'
```

## Category Creation and Backfill

Use platform cleanup scripts only after an inventory or dry run. They attach to
logged-in browser sessions and are read-only until `--apply`.

Shipinhao can create missing collections:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py ensure-collection --collection LalaMV --apply'
```

YouTube upload-time routing can create a missing playlist from the upload dialog
when the YouTube UI exposes the create control. For existing videos, run a dry
plan first:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_y2b_videos.py move-category --category lalamv --lalamv-playlist LalaMV --scrolls 20 --output /tmp/youtube_lalamv_plan.json'
```

Shipinhao LalaMV dry run:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py move-category --category lalamv --lalamv-collection LalaMV --scrolls 20 --output /tmp/shipinhao_lalamv_plan.json'
```

Classified dry runs for all non-`simplelife` categories:

```bash
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_y2b_videos.py move-classified --scrolls 20 --output /tmp/youtube_category_plan.json'
ssh lachlan@lazyingart 'cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python scripts/manage_shipinhao_videos.py move-classified --scrolls 20 --output /tmp/shipinhao_category_plan.json'
```

Never bulk-apply a generated plan without inspecting the JSON. Use exact title
fragments for existing-post repair when the platform UI is unstable.

## Instagram Status

Instagram does not expose a stable per-post category, playlist, folder, or
collection in the desktop web upload flow. AutoPublish logs the category for
traceability but does not select any Instagram category UI.
