# Arabic Subtitle Line Shaping

Arabic subtitles were joining letters within each token but laying the tokens
out left-to-right. This put words and punctuation in the wrong order and could
break clitics split across grammatical tokens.

The LazyEdit renderer now sends the complete logical line to Pillow/libraqm.
BiDi ordering and contextual shaping run together; source JSON and timings stay
unchanged. Measurement and drawing use the same full-line path, including mixed
Latin text and numbers. The external `furigana` dependency is unchanged.

Joining-script lines currently use the selected uniform text color. Other rows
retain grammar colors and ruby. Per-word color for Arabic needs run-aware
shaping; drawing colored words separately or reversing a token list is not an
equivalent solution. Optional romanization is centered above the joined line.
Pillow without libraqm fails clearly rather than producing incorrect Arabic.

Validation: `python -m pytest tests/test_subtitle_rtl.py
tests/test_subtitle_burn_speaker_tokens.py -q`. Compare an actual burned frame
with a complete-line RTL reference before public delivery. The one-shot Arabic
bottom slot is `ar,zh-Hant,ja,en` in the publication CLI's bottom-to-top order.
