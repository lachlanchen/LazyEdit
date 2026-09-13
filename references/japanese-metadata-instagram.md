# Japanese Metadata and Instagram Captions

New video processing includes `metadata_ja` alongside Chinese and English metadata. It uses the configured AI provider and the same transcription, creator notes, cache and publication-session handling as the existing generators.

- API: `POST /api/videos/{id}/metadata` with `{"lang":"ja","notes":"..."}`; `GET` with `?lang=ja` reads it. `jp`, `ja-JP` and `Japanese` are accepted aliases.
- Storage: the current publication's `metadata/ja/*_metadata_ja.json`.
- Publication ZIP: the usual metadata JSON keeps Chinese at the root, `english_version`, and adds `japanese_version` when available.
- CLI and Studio processing generate and report the Japanese step. Explicit `--steps` still controls selective processing.
- Existing packages without Japanese metadata remain publishable without rebuilding a completed video.

AutoPublish's Instagram caption builder displays Japanese, English, then Chinese. It prefers each version's concise middle description, falling back to brief and long descriptions. It deduplicates identical blocks and allocates the 2,200-character budget across languages so a long first description cannot erase the last language. Other platforms' metadata selection is unchanged.

Pass story context and any requested attribution through `--prompt-file`; do not hand-write a replacement publication JSON. Ask for concise prose and attribution in the descriptions when needed. Inspect the rendered caption before submitting if placement or length is important.

Subtitle languages remain separate from metadata languages. For English/Japanese/Chinese/French subtitles with a bottom-anchored band, use `--languages fr,zh-Hant,ja,en --subtitle-lift-ratio 0`. This one-shot option does not change global settings.

Validation:

```bash
python -m pytest -q tests/test_japanese_metadata.py tests/test_lazyedit_publish_cli.py
cd AutoPublish
python -m unittest test_instagram_caption.py
```

Deploy the AutoPublish submodule change to the publishing host before posting. Avoid restarting an active publishing task; use its existing auto-reload only when the queue is idle.
