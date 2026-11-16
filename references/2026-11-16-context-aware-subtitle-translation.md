# Use the same scene context for subtitle translation

Subtitle correction and metadata generation used the supplied scene context, but translation only received adjacent subtitle lines. That could make a salon conversation's ボリューム become sound volume, or セット become device settings. Short source-language lines can also leave speaker references ambiguous.

The normal process pipeline now passes its existing notes (or correction notes when no metadata notes are present) to translation. The translator uses this optional background only to disambiguate terminology and references. It must translate the supplied dialogue, without inserting background facts or changing native source text during annotation.

No new publisher, saved preference or mandatory configuration is added. Existing CLI `--prompt-file` processing carries the context automatically. Direct translation calls may supply `translationContext` or the existing `notes` field:

```json
{
  "lang": "zh-Hant",
  "usePolishedSubtitles": true,
  "notes": "A salon consultation about perm strength, hair volume and daily styling."
}
```

`translationContext` takes precedence over `notes`. Non-text context is rejected before processing. Background is trimmed, JSON-quoted and bounded to 8,000 characters in the model prompt. Without background, existing prompts and cache inputs remain unchanged. With background, it becomes part of the normal prompt hash, so cached translations from another interpretation are not reused.

Validation covers the actual translation handler with a stubbed provider, context precedence, invalid input, prompt bounds, unchanged legacy prompts, source preservation and distinct cache inputs. No model calls are made by these tests:

```bash
python -m pytest tests/test_translation_background_context.py tests/test_translation_editor_annotations.py tests/test_publish_dispatch.py tests/test_remote_queued_publish_receipt.py tests/test_lazyedit_publish_cli.py -q
```

All 44 tests pass. Keep active preparations and hosted acceptance locks intact when activating the backend change. Regenerate affected translations and the unpublished subtitle render through the normal pipeline; do not patch generated translation JSON or republish already completed videos.
