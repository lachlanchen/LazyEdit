# Corrected multilingual cues and native-text locking

An English-tagged Whisper cue can become Korean, Japanese or another script
after subtitle correction. Correction preserves the recognition language tag
as provenance. The translator must not use that stale tag to require an exact
English copy of the corrected non-English text.

The observed failure was `Annotation changed original native subtitle text`
when the English row translated corrected Korean `건배!` as `Cheers!`.
The earlier Han-only exception handled Chinese characters, but missed Hangul
and kana.

`SubtitlesTranslator._target_matches_source_language` now declines the
same-language lock for Latin-language tags when the corrected cue contains
letters but no Latin letters. This is a script mismatch check, not language
identification. It preserves the original tag and the normal translation,
annotation and timing validation paths. Actual Latin speech, mixed-script
speech, numbers and emoji retain the existing lock behavior.

Regression tests cover Korean, kana, Cyrillic, Arabic and mixed Han/Hangul with
an English recognition tag. Existing tests retain exact native English and
mixed speech. The focused annotation and editor suite passes 40 tests:

```sh
python -m pytest tests/test_multilingual_annotations.py \
  tests/test_translation_editor_annotations.py -q
```

For an affected failed preparation, retry the normal translate/render/metadata
steps using the reviewed polished transcript. Do not retranscribe, change cue
timings, disable annotation validation or dispatch another social publication
to repair a preparation failure.
