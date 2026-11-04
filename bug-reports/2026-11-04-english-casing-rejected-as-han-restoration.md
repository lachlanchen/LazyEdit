# English Display Casing Rejected As Han Restoration

## Observed Failure

A normal four-language preparation completed French, Chinese and Japanese but
failed English before rendering or publication. The annotation had validated
surface `Make`, display word `make` and an empty reading. Its surfaces reproduced
the translated sentence exactly, but the display mismatch reached the strict
Han-restoration branch and failed.

## Scoped Repair

After exact surface coverage is checked, English tokens differing only by
`casefold()` now display the authoritative surface with empty reading. This
changes no translated text, timestamps, grammar types or cue count. Non-case
lemma substitutions and Han replacements still fail. Korean/Vietnamese
restoration rules and existing French elision handling are unchanged.

Regression cases cover `Make/make`, `I/i`, `OK/ok`, an English lemma mismatch
and an unauthorized Han substitution.

```bash
python -m pytest -q tests/test_multilingual_annotations.py \
  tests/test_subtitle_annotation_punctuation.py tests/test_hanja_dictionary.py
```

Result: 105 passed. The same failed preparation record was resumed, reusing
the existing successful languages. English then completed and the publication
master passed decode, timing and subtitle-frame review. No duplicate source
upload or manual translation/metadata-file replacement was needed.
