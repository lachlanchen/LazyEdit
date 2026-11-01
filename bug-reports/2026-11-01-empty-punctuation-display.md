# Empty punctuation display blocked translation

An English translation contained a comma token with `surface=","`, `word=""`,
and `reading=""`. The token surfaces matched the complete translation, but
the shared validator treated the empty display word as invalid Han restoration.
Reusing the cached response repeated the failure and prevented publication.

The validator now restores the exact verified surface for empty display words
consisting only of Unicode punctuation or whitespace. It does not alter clean
text, timing, lexical tokens, or Han restoration rules. Missing punctuation in
the surfaces still fails coverage validation. The fix applies across languages.

Verification:

```bash
python -m pytest -q tests/test_subtitle_annotation_punctuation.py tests/test_multilingual_annotations.py tests/test_hanja_dictionary.py
```

Result: 100 passed. Production recovery reuses the imported corrected subtitles
and cached translations; no transcription or video generation is required.
