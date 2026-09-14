# Context review, pronunciation checks, and completed YouTube dialogs

## Context is evidence, not a replacement transcript

Use `scripts/lazyedit_publish.py --prompt-file ... --correct-subtitles
--use-polished` for the normal pipeline. Read the full transcript against the
creator's background. A short excerpt may contain only the end of the described
conversation. Do not insert unrecorded recollections into subtitle cues.

Correct obvious homophones in context while retaining cue order and timing.
When an unclear fragment remains inconsistent across independent recognition
passes, keep the reliable words instead of inventing a fluent ending. Save
reviewed SRT through `/api/videos/{id}/subtitle-correction` with
`action=save_polished`; rerun the dependent translation and burn steps. Do not
run Whisper again over already reviewed corrections.

For metadata, distinguish a speaker's beliefs and comparisons from factual
claims. Use concise descriptions of the actual encounter. If inspected output
copies too much background, strengthen the context and rerun metadata through
the normal generator. `--metadata-prompt-file` can isolate metadata instructions
after such a failure; it is not necessary for ordinary successful runs.

## Four subtitle rows with no lift

The CLI language list is **bottom to top**. For visible EN / JP / ZH / FR from
top to bottom, use `--languages fr,zh-Hant,ja,en --subtitle-rows 4
--subtitle-lift-ratio 0`. Retain the existing grammar colors and pinyin/romaji
settings. Use the existing Studio logo and the user-requested position.

Japanese romaji does not replace kanji furigana. Inspect the Japanese annotation
JSON: every kanji token must have a kana reading. Then inspect actual burned
frames, since valid settings or JSON alone cannot prove the rendered result.
The reviewed 25-cue sample contained 62 kanji tokens, all with readings; rendered
frames showed furigana above kanji and pinyin above Chinese. Original and polished
SRT timelines matched. The source was native portrait, so blur fill was disabled.

Before submitting a reviewed output, compare the MP4 inside the publish ZIP with
the final master. Use `--no-process --no-correct-subtitles --use-polished` without
a metadata prompt when reusing completed output. Leave all real submissions in
the normal LazyEdit/AutoPublish serial queue and check each platform result.

## Durable YouTube recovery

AutoPublish commit `5780fed` fixes the completed-publication confirmation being
misidentified as an unrelated draft. It closes only a proven success receipt,
waits for the old wizard to disappear, and preserves unfinished drafts. Failure
to clean up after verified success does not turn the job into a failed publish.

See [AutoPublish recovery details](../AutoPublish/references/youtube-completed-receipt-cleanup-2026-09-14.md).
The focused suite passed 23 tests, including JavaScript syntax checks and
no-reupload cases. The same commit was pushed and fast-forwarded onto the Pi;
existing browser profiles were retained.

Private media, context text, screenshots, and delivery receipts stay under
ignored runtime paths. This note does not include the private conversation.
