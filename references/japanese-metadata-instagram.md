# Japanese Metadata and Instagram Captions

New video processing includes `metadata_ja` alongside Chinese and English metadata. It uses the configured AI provider and the same transcription, creator notes, cache and publication-session handling as the existing generators.

- API: `POST /api/videos/{id}/metadata` with `{"lang":"ja","notes":"..."}`; `GET` with `?lang=ja` reads it. `jp`, `ja-JP` and `Japanese` are accepted aliases.
- Storage: the current publication's `metadata/ja/*_metadata_ja.json`.
- Publication ZIP: the usual metadata JSON keeps Chinese at the root, `english_version`, and adds `japanese_version` when available.
- CLI and Studio processing generate and report the Japanese step. Explicit `--steps` still controls selective processing.
- Existing packages without Japanese metadata remain publishable without rebuilding a completed video.

AutoPublish's Instagram caption builder displays Japanese, English, then Chinese. It prefers each version's concise middle description, falling back to brief and long descriptions. It deduplicates identical blocks and allocates the 2,200-character budget across languages so a long first description cannot erase the last language. Other platforms' metadata selection is unchanged.

Pass story context and any requested attribution through `--prompt-file`; do not hand-write a replacement publication JSON. Ask for concise prose and attribution in the descriptions when needed. Inspect the rendered caption before submitting if placement or length is important.

Each metadata template should produce only its target language. The publisher,
not the generator, composes multilingual captions. Telling the generator to put
all three languages into each `middle_description` duplicates the final post.
When subtitle-specific instructions leak into a description, use a concise
metadata-only context with `--metadata-prompt-file` and selectively regenerate
the metadata steps; keep the accepted video and subtitles unchanged.

Subtitle languages remain separate from metadata languages. For English/Japanese/Chinese/French subtitles with a bottom-anchored band, use `--languages fr,zh-Hant,ja,en --subtitle-lift-ratio 0`. This one-shot option does not change global settings.

Validation:

```bash
python -m pytest -q tests/test_japanese_metadata.py tests/test_lazyedit_publish_cli.py
cd AutoPublish
python -m unittest test_instagram_caption.py
```

Deploy the AutoPublish submodule change to the publishing host before posting. Avoid restarting an active publishing task; use its existing auto-reload only when the queue is idle.

## Recovery Notes

- Inspect `git remote -v` on the deployment checkout; remote names need not
  match the development checkout or an older deployment guide.
- Prefer the normal LazyEdit CLI to requeue a verified current output with
  `--no-process` and no correction/metadata prompt. Check platform receipts
  before retrying so completed posts are not duplicated.
- AutoPublish `/publish` accepts raw ZIP bytes with options in the query
  string. A metadata-only retry must explicitly use `reuse_existing=true`
  after verifying the stored ZIP. Do not send multipart form fields without
  that flag: this implementation writes the request body as the package.
- A selective `--steps` rerun can briefly expose previous completed status.
  Confirm new metadata timestamps before publishing; see the related bug report.
