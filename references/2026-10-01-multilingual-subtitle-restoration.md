# Multilingual grammar and Han restoration

The modern single-pass translators bypassed legacy Korean Hanja / Vietnamese
Chữ Hán conversion and saved only plain text. Arabic and other translation
paths also discarded grammatical annotations. Same-language shortcuts skipped
annotation entirely.

The shared translation path now requests lossless grammar tokens alongside
clean text. Korean and Vietnamese restore confidently identified Sino-derived
roots as traditional Han characters, with the original native spelling as ruby.
Native words, particles and uncertain etymologies retain their original spelling:
Korean gets Revised Romanization; Vietnamese gets Hanoi IPA pronunciation
(Vietnamese already uses a Latin alphabet). Do not invent Chinese replacements
for native words or names. Grammar colors remain attached to the displayed word.

Examples: 학교 → 學校 with 학교 above; học → 學 with học above;
나 stays 나 with na above. Plain SRT/metadata still uses 학교 / học / 나.

Arabic, Russian, Spanish, English, French and Cantonese now retain grammatical
tokens, as does the generic language path including German. Existing Japanese
and Chinese specialized annotation paths are unchanged. The burner no longer
throws away an explicit grammatical label on a one-word caption.

Implementation:
- `lazyedit/subtitle_annotations.py`: schema/prompt contract, exact surface
  coverage, timestamp/count validation, native-text preservation and required ruby.
- `lazyedit/subtitle_translate.py`: annotations in single-pass and generic paths;
  versioned request cache names prevent reading old plain-only model responses.
- `lazyedit/subtitle_tokens.py`: preserve explicitly classified single tokens.
- `tests/test_multilingual_annotations.py`: mocked translation through the actual
  segment loader; restoration, readings, colors, missing-token/reading rejection,
  same-language annotation and German generic routing.

Existing completed translation files and burned videos are not rewritten. Request
a fresh translation/process to regenerate them. A running backend must load the
updated Python code before new requests use it; no live service was restarted as
part of this change. No publication or global UI preferences changed.

Validation covers contracts and actual renderer segment ingestion, not a live
model linguistic-quality audit. Ambiguous Han etymologies and Vietnamese IPA
still require reviewing model output. Invalid/incomplete annotations fail visibly
instead of silently burning dropped words.

## Korean/Vietnamese wrapping follow-up

The LazyEdit-owned burner adapter groups adjacent restored roots and native
suffixes until a space or punctuation boundary. This reuses the existing timed
long-line splitting, preserving ruby and grammar colors without splitting a
Korean word between its Hanja root and Hangul particle. The external furigana
symlink remains read-only. A regression test checks an overwide repeated cue,
root/particle adjacency, preserved ruby and unchanged overall cue interval.

## Live validation: food clip 600

A real render exposed two additional issues: generated space tokens sometimes
had an empty display word, and Korean ruby was present but rendered almost
invisibly because the auto-romaja UI toggle was off. The validator now restores
verified whitespace from `surface`; Korean/Vietnamese token annotations enable
normal ruby sizing independently of automatic-pronunciation toggles.

The CLI process monitor now passes its one-shot language selection to status
queries instead of waiting for the persisted French selection when Korean was
requested. Failed translation status uses the failed language's timestamp,
not a newer successful language's timestamp (which made an old error look new).
A burn-only rerun also accepts unchanged successful translation dependencies.

Validation: 32 focused tests pass. The actual Korean burn was visually inspected
at 6.3 seconds: romanization is readable above the native words, all four rows
are separated, the portrait lower area fits them, and the existing logo is top
right. Words without a confident conventional Han spelling keep Hangul and
romanization. Do not infer that they lack historical Chinese etymology: 감자
is treated as native in modern dictionary classification but has a documented
connection to 감저/甘藷. Correct ASR was recovered with explicit Chinese recognition
and word alignment: 看着很好吃 (3.50–4.80), 牛肉配土豆 (5.56–7.04).

The same one-shot language parameter must also be passed by the *publish queue
worker* when checking prerequisites, not only by the CLI monitor. Otherwise a
ready Korean run is reported as missing persisted French, and the worker
regenerates the render and metadata despite `--no-process`. This was reproduced
on job 441 and fixed in `_process_publish_job`, with an isolated worker test.
The incomplete remote attempt was stopped at Douyin's empty upload form before
submission; no platform post occurred. Only this job was active. AutoPublish
was restarted with browser profiles left intact, corrected metadata regenerated
through LazyEdit, and replacement job 442 reused the completed output correctly.
33 targeted regression tests pass after the full fix.

## Lightweight dictionary follow-up

See `2026-10-01-hanja-dictionary-review.md` for the local Korean candidate
dictionary and one bounded LLM review. Korean/Vietnamese prompts now explicitly
check every root and homophone. Translation still normally uses one request;
there is no mandatory second LLM pass or vector database.
