# Subtitle Token Normalization

Date: 2026-06-21

LazyEdit subtitle correction and translation can produce several valid shapes:

- plain text only, for example `{"ja": "孔子は魯に帰った。"}`
- Japanese schema tokens, for example `{word, reading, type}`
- burner-native tokens, for example `{text, ruby, type, color}`
- legacy `furigana_pairs` or ruby markup
- speaker icon helper tokens plus normal subtitle text

These shapes must not be fixed per video. The shared tool layer is
`lazyedit/subtitle_tokens.py`, called from
`lazyedit/subtitles_burner/burner.py` before delegating to the external
`furigana` renderer.

## Pipeline Contract

1. Subtitle correction may recover missing lines as plain `text`/`ja`/`zh`.
2. Translation should preserve structured tokens when available.
3. The burn wrapper normalizes every subtitle item into ordered token dicts.
4. Each visible token receives a grammar `type`; existing ruby/readings/colors are preserved.
5. The upstream renderer applies the selected grammar palette and language-specific ruby/pinyin options.

## Fallback Behavior

When a line has no usable tokens, LazyEdit now builds typed tokens from the plain
line text:

- Japanese keeps common particles separate (`は`, `が`, `を`, `に`, etc.) and
  classifies likely verbs, nouns, copulas, numbers, and punctuation.
- Chinese/Cantonese splits Han text into character tokens with pronoun, verb,
  particle, preposition, number, punctuation, and noun fallbacks.
- Latin-script lines split into words, numbers, punctuation, and spaces with a
  small grammar heuristic.

This fallback is intentionally conservative. It preserves editability and visual
grammar colors even when AI correction only produced plain recovered text. For
high-quality final subtitles, prefer model-generated token schemas; the fallback
is the safety net, not the linguistic gold standard.

## Regression Tests

Run:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python -m unittest tests/test_subtitle_burn_speaker_tokens.py
```

The tests cover speaker-token fallback, plain Japanese tokenization, preserved
`word`/`reading` tokens, and plain Chinese tokenization with palette colors.
