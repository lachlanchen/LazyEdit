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

## Traditional Chinese pronunciation lookup

Visual QA also found the generic pinyin dictionary reading traditional `乾杯`
as `qián bēi`. Reading lookup now uses the in-process OpenCC simplified phrase
when it preserves character count. Only the lookup changes: displayed text and
token alignment remain traditional. This selects `gān bēi` for `乾杯` and
`gān zào` for `乾燥`, while preserving `qián` in `乾隆` and `乾坤`.

The renderer disables the optional CLI conversion fallback, so missing OpenCC
cannot create a subprocess for each phrase. It retains the original lookup in
that case or when conversion changes character count. Five additional tests
cover phrase readings, unchanged display text and the no-subprocess boundary;
the same focused suite now passes 45 tests. Rerender through the normal burn
endpoint before dispatching the corrected output.

## Native publication findings

Publication qualification exposed separate AutoPublish issues. Their fixes live
in the submodule and apply to normal queued publishing:

- Shipinhao disabled classes, single-click dispatch, native submission
  acknowledgment, iframe management receipts and no whole-process retry after
  an uncertain submission: see
  [Shipinhao recovery](../AutoPublish/references/shipinhao-dependencies-and-published-retention.md).
- YouTube can hide an already completed success receipt. A matching current
  video ID, native completed receipt and public oEmbed title confirm completion
  without another upload: see
  [YouTube receipt reconciliation](../AutoPublish/references/youtube-hidden-publication-receipt.md).

Activate publisher changes at an idle queue boundary and preserve the explicit
queue-journal location. The Pi uses the protected repo `.env` for that location;
checking only HTTP health can miss accidentally opening an empty default
journal. Verify that historical job IDs and reconciled results survive startup.
Never turn a lost acknowledgment into another public post.
