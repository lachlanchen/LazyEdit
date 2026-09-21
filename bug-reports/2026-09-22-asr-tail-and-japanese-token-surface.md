# ASR Tail Hallucination And Japanese Token Surface Drift

Observed during LALACHAN video 582, a 30.266666-second generated travel story.
The issues were caught before any public post. This report does not change the
shared runtime or transcription/translation defaults.

## ASR Evidence

The initial transcription contained six real dialogue cues followed by four
cues squeezed into 30.000-30.255 seconds: a fabricated subscription/donation
outro. Ordinary context correction retained this text and added speaker-name
prefixes to the six real lines. Timeline equality alone passed, despite the
hallucinated content and overly early cue starts (first line started at zero).

Independent Whisper large-v3 decoding with word alignment, no prompt,
temperature zero, and `condition_on_previous_text=False` placed the six lines
at 5.600-7.640, 7.640-9.680, 13.220-15.340, 15.800-17.760,
21.940-23.560, and 23.560-25.820 seconds. Its final tail instead hallucinated
`谢谢大家` at 30.000-30.220, with the first word probability about 0.025 and
the final word of zero duration. The incompatible tail detections and implausible
speech durations were rejected, not replaced with scripted words.

Recovery: preserve original ASR/polished files, import the six reviewed,
word-aligned cues through the existing authoritative-SRT CLI option, then run
normal translation, burn, metadata, and packaging. Only the homophonic name
and punctuation changed in the retained source text. No human listening review
is claimed; evidence is machine transcription/alignment and visual inspection.

## Japanese Evidence

The Japanese sentence field was correct:

`私はただこの石を飛び越えたかっただけなのに！`

But `tokens` and `furigana_pairs` used the dictionary form `飛び越える`
followed by `たかった`. The renderer trusted those surfaces and visibly
burned `飛び越えるたかった`, disagreeing with the sentence/SRT.

Recovery: preserve the first render and translation JSON, change that token
surface to `飛び越え` with reading `とびこえ` in both representations, and
rerun the existing `burn-subtitles` endpoint with its saved layout and logo
configuration. Timing, palette, other languages, metadata, and source video
remain unchanged.

The first attempted CLI recovery with `--steps burn` was insufficient:
`VideoProcessHandler` sets `needs_translate` whenever burning subtitles, so
cached translation output overwrote the reviewed token edit. A direct call to
the normal burn handler avoids that dependency rerun. This is a second recovery
caveat: an explicitly burn-only operation should preserve reviewed translation
edits or document that it regenerates translations.

## Queue Reprocessing Caveat

The corrected normal-burn output was fully decoded, visually checked, and copied
to Nutstore. However a later CLI command using `--no-process --no-correct-subtitles`
with the shared `--prompt-file` created job 420 and triggered processing again.
`_process_publish_job` unconditionally enters its processing branch whenever
`metadata_prompt` is nonempty; the CLI's no-process flag is not a queue-level
reuse contract. Translation restored the bad token from cache again. The six
reviewed polished source cues and their timing remained correct.

This was discovered after the remote job began and accepted the Douyin publish
action. No duplicate post was submitted to repair this single Japanese suffix.
The corrected local export remains preserved. Future reuse must omit an already
applied metadata prompt, or use a verified bundle reuse path until a real
queue-level no-process contract and hash guard exist.

Expected regression test: an inspected processed output plus `--no-process`
and story context should reuse exactly that file (same SHA-256), not call
transcribe/translate/burn again. Supplying metadata context should not silently
invalidate reviewed video/subtitle artifacts.

## General Fix To Consider

- Add an acoustic-quality gate for implausible tail cues; do not blanket-delete
  ordinary thanks or subscription speech when genuinely spoken.
- Distinguish a timestamp-preserving text check from an audio-alignment check.
- Require concatenated Japanese token surfaces to reconstruct the accepted
  sentence exactly before rendering. On mismatch, repair tokenization against
  that sentence rather than inventing words or dropping furigana/colors.
- Regression tests should include a real spoken outro and a music-only tail,
  plus conjugated Japanese verbs with auxiliary tokens and mixed kana/kanji.

Task evidence is retained privately under the LALACHAN run's `publish-qc`
directory. Private audio, screenshots, and generated media are not committed.
