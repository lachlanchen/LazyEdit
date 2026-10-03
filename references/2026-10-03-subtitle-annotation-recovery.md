# Exact Spacing And Actionable Han Annotation Repair

## Observed Failure

A normal generated-video publication failed translation validation before any
public post. French tokens omitted spaces present in the clean translation.
Korean had the same spacing issue and returned mixed tokens such as
`到着했어` with romanization instead of a restored root and native suffix.
The existing single repair attempt received only a generic validation error.

## General Fix

- Restore omitted whitespace tokens only when the clean translation proves the
  exact gap. Missing letters, punctuation, extra text and reordered tokens remain
  hard failures. Translation wording and timestamps stay unchanged.
- Include the offending surface, display word and reading in Han validation
  errors. Explain that restored roots contain only Han characters, use the exact
  native surface as ruby, and separate native suffixes with pronunciation.
- Keep the existing one-repair limit, contextual dictionary review, DeepSeek
  provider and normal renderer. No task-specific vocabulary was added to code.

## Verification

`python -m pytest -q tests/test_multilingual_annotations.py tests/test_hanja_dictionary.py`

34 tests passed. The subsequent live Korean translation restored `도착` to
`到着` with `도착` ruby and `사진` to `寫眞` with `사진` ruby. Native words
remain Hangul with romanization. The four clean Korean sentences retain exact
source cue boundaries.

## Separate Audio Correction

This run also exposed an ASR timing problem before translation: music was
recognized as English and dialogue spans included long silent intervals.
The initial polished text was not used for publication. A separate Chinese
word-level transcription aligned four actual lines; only the place-name
recognition and punctuation were corrected. A zero-duration trailing Whisper
hallucination was excluded. The reviewed SRT was imported through the standard
`--subtitle-file --subtitle-language zh` path.

When resuming an imported-subtitle job, retain `--subtitle-file` or explicitly
omit `transcribe` from `--steps`; `--no-correct-subtitles` alone does not disable
transcription in the CLI default pipeline. Ordinary text corrections still
require identical cue count and timestamps; realignment is a separate reviewed
operation, not a license to replace ASR with a story script.
