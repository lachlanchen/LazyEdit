# Korean Annotation Review During LALACHAN Publication

## Fixed: Native Pronunciation And Mixed-Root Formatting

Video 606 exposed two bounded annotation problems before public dispatch:

- `그랜빌섬` remained correctly in Hangul, but its generated romanization was `geuraenbilleom`, omitting the `s` of `섬`.
- A Korean-only review returned `surface=콧수염이`, `word=콧鬚髥이`, `reading=kotsuyeomi`. The validator correctly rejected this mixed display token after the repair attempt.

The shared `normalize_selected_restorations` now uses the already installed `koroman` library for Latin readings of pure, non-restored Hangul tokens. It also splits a model-selected Hanja root with native prefixes/endings only when unchanged affixes match exactly and the selected spelling is a dictionary candidate. It never selects an alternative Hanja meaning or changes clean Korean text/timestamps.

Expected example: `콧 / kot`, `鬚髥 / 수염`, `이 / i`. A conflicting dictionary spelling remains rejected. Existing handling of native homophones, unknown spellings and Vietnamese remains intact.

Validation: `python -m pytest tests/test_hanja_dictionary.py tests/test_multilingual_annotations.py -q` passed 49 tests. The same video was reprocessed through the normal Korean translation endpoint, then the normal burner; no rendered subtitle JSON was hand-patched.

The final actual restored words were checked against the National Institute of Korean Language:

- [건배 / 乾杯](https://krdict.korean.go.kr/jpn/dicSearch/SearchView?ParaWordNo=23629)
- [수염 / 鬚髥](https://krdict.korean.go.kr/kor/dicSearch/SearchView?ParaWordNo=64609)

## Separate Observations For The Owning Agent

Follow-up: the user's common-only, sentence-level optimization is implemented in
`references/korean-restoration-single-pass.md`. Valid partial restorations now
return without a completeness review. Readings are computed locally; only invalid
structure receives one repair. The earlier 49-test publication record above is
preserved as history. The published video was not rerendered or republished.

These broader behaviors were not changed during this publication:

1. The initial ASR's third cue began at 2.680s, while independent word-timestamp ASR placed that speech at 5.660s. Text polishing correctly preserved the bad original timing, so timeline equality alone cannot certify alignment. Original and first-polished SRTs were preserved in the video's local QA evidence. A separately reviewed five-cue SRT was imported via the supported `--subtitle-file` flow. The exact imported timeline was validated before publication.
2. The first Japanese metadata response contained Chinese prose despite the Japanese template. Regenerating only Japanese metadata through `/api/videos/606/metadata` with English factual notes and explicit Japanese output succeeded. Metadata was not manually replaced.
3. `VideoTranslateHandler` deletes existing translated outputs before attempting replacement. A failed review can therefore remove a previously valid translation. Consider staging new artifacts and atomically replacing them only after validation; this transaction change is deferred to the owning agent.

The video source, original generation, other languages and unrelated publication jobs were not rerun. No additional Xiaoyunque credits were spent.
