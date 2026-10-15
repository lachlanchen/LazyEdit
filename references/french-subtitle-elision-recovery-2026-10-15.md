# French Subtitle Elision Recovery

A normal four-language publication stopped in French translation because an
annotation token contained `surface: "d'"` and `word: "de"`. The sentence and
surface coverage were correct; the model supplied a dictionary form for the
display word. The Han-restoration validator rejected it before rendering.

`validate_annotations` now uses the exact validated French surface as the
display word for non-Han lemma mismatches, clearing an inapplicable reading.
It still rejects lost text, altered timing, and attempted Han replacement in
French. Korean and Vietnamese restoration behavior is unchanged.

Verification:

```bash
python -m pytest tests/test_multilingual_annotations.py tests/test_hanja_dictionary.py -q
```

Result: 64 tests passed. The previously failing live French request completed
from its existing translation cache. No provider switch, model retry loop or
video regeneration was needed.

The separate stale source-language issue after text correction remains recorded
in `bug-reports/2026-10-15-polished-french-cue-stale-language.md`.
