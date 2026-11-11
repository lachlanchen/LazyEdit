# English Contraction Whitespace Tokens Block Translation

## Symptom

An English subtitle translation returned HTTP 500 with `Annotation tokens do not cover the complete subtitle`. The clean text was valid, but a separate whitespace token appeared between `We` and `'ve` in `We've arrived in Yokohama!`. Retrying reused the same cached response and failed identically; other language translations completed.

## Cause And Fix

The shared annotation validator already restored missing whitespace from authoritative clean text, but rejected surplus whitespace-only tokens. It now reconciles those tokens against the exact whitespace in the clean text: removes surplus whitespace-only tokens, restores missing gaps, and keeps every non-whitespace surface in its original order.

The clean subtitle text, timing, words, punctuation and grammar annotations remain authoritative. Missing or extra letters, omitted punctuation, reordered words and changed timestamps still fail. This is a local deterministic normalization, not an extra model call, a cache rewrite or a per-video translation patch.

## Verification

```bash
python -m pytest tests/test_subtitle_annotation_whitespace.py \
  tests/test_subtitle_annotation_punctuation.py \
  tests/test_multilingual_annotations.py \
  tests/test_translation_editor_annotations.py \
  tests/test_subtitle_burn_speaker_tokens.py -q
```

The two focused runs passed 87 and 8 tests respectively. The existing local owner API subsequently translated the cached English response successfully, and the same prepared video completed its multilingual render and metadata steps. Hosted worker releases were not promoted or replaced.
