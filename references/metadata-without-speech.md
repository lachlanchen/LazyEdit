# Metadata for clips without speech

Silent clips and clips without intelligible dialogue can still have useful
owner-supplied context, such as a cat sitting on a gym bench. The metadata
endpoint accepts that context in `notes`/`custom_notes`; the publish CLI supplies
it through `--prompt-file`.

Previously, a transcription marked `empty` or `no_audio` caused the endpoint to
return filename-based placeholder metadata before reading the context. The
endpoint now uses the normal metadata generator when nonblank context is
available. It does not create spoken lines or change subtitle timing.

When neither speech, visual captions nor context is available, the existing
placeholder fallback remains. Existing speech and visual-caption generation
paths are unchanged.

For a no-subtitle publication, use `--no-burn-subtitles --logo`, inspect the
processed frame and generated metadata, then reuse that output for publication.
If metadata alone needs recovery, rerun only the metadata and cover steps.

Regression checks:

```sh
python -m pytest tests/test_metadata_without_speech.py tests/test_metadata_story_copy.py -q
```

These exercise the actual metadata worker with isolated dependencies, covering
empty/no-audio/context-only inputs, whitespace-only context, normal speech and
visual-caption fallback. No database, model call or social post is required.
