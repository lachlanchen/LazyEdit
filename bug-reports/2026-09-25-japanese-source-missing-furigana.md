# Japanese Source Speech Skipped Reading Annotation

Observed while preparing video 592, before any platform submission.

Japanese translated from other languages had kana readings, while a Japanese
source greeting rendered its kanji without furigana. The source-language
shortcut returned empty tokens and furigana pairs. Speaker-row normalization
restored visible text but could not infer the missing readings.

The Japanese path now uses the configured annotation provider even for
Japanese source speech. It asks for annotation only, retains the exact source
text/timing, and validates full token coverage and kana readings for kanji.
Plain same-language handling for other languages is unchanged. Source
annotations have a distinct cache key. Existing translation outputs require
a deliberate Japanese refresh and normal subtitle reburn to pick up the fix.

Regression tests cover annotation, preserved text/timing, rejected rewrites,
missing tokens/readings, extra cues, and ordinary non-Japanese translation.

Validation: 11 tests passed across `test_japanese_source_readings.py` and
`test_subtitle_burn_speaker_tokens.py`. Refreshing the Japanese translation
through the existing API produced `中秋節` with `ちゅうしゅうせつ`, retained
the reviewed source timeline, and preserved source-language attribution.
