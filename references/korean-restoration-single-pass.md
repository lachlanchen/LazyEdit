# Fast Korean Hanja Restoration

Updated 2026-10-06. Goal: useful common restorations, not exhaustive etymology.
Normal Korean translation/publication uses this automatically; no new CLI flag,
provider, manual subtitle patch, or per-video restoration instruction is needed.

## Divide The Work

1. Keep the existing one-request-per-subtitle-cue worker pool, with previous and
   next source cues as context. `LAZYEDIT_TRANSLATION_WORKERS` defaults to four.
2. Ask the configured translator for natural Korean plus `surface`, `word`, and
   grammar `type`. Restore common, confident Sino-Korean roots only. Uncertain
   words, native vocabulary and foreign names can stay in Hangul.
3. Locally derive exact Hangul ruby for selected Hanja and romanization for native
   Hangul with the existing `koroman` dependency. Retain native endings. Recover
   common mixed-root formatting only when the selected root/affixes align with
   the local dictionary; the dictionary never chooses a homophone's meaning.
4. Validate cue count, timing, clean text, surface coverage and token shape. Exact
   whitespace gaps and dictionary-form native lemmas can be repaired locally.
   A valid partial restoration returns immediately. A structurally invalid cue
   receives at most one annotation repair with clean text/times locked; a second
   invalid result fails visibly. Existing transport retries remain separate.
5. Reassemble cues in timeline order. Reuse the existing content-keyed request
   cache; cached compact responses still receive local normalization/validation.

This replaces the former routine dictionary-completeness review. Zero Hanja is
valid: for example, native `감자` (potato) should not become the unrelated financial
homophone `減資`. This is a practical annotation aid, not certified etymological
coverage. No semantic 100% guarantee is implied.

The renderer still receives `surface`, `word`, `reading`, and `type`. Only the
Korean LLM response schema omits `reading`, reducing generated fields. Other
language schemas and the configured DeepSeek/provider setup remain unchanged.

## Verification

```bash
python -m pytest -q tests/test_hanja_dictionary.py \
  tests/test_multilingual_annotations.py tests/test_subtitle_languages.py \
  tests/test_lazyedit_publish_cli.py
```

114 tests passed. Coverage includes one request per valid cue, parallel context
handling, stable ordering/timing, local readings/affix splits, native homophones,
bounded invalid-output repair, cache replay, ruby rendering and other languages.

An isolated text-only test using the configured DeepSeek backend produced:

| Source | Korean display |
| --- | --- |
| 今天在学校见面。 | 오늘 學校에서 만나요. |
| 我喜欢吃土豆。 | 저는 감자를 좋아해요. |
| 祝贺你，干杯！ | 祝賀해요, 乾杯! |

Three requests, no repair requests, approximately 1.4 seconds parallel elapsed
time in this sample; cached replay made zero network calls. Timing is an
observation, not a latency guarantee. All cues retained their original times.
No video was rendered or published for this test.

Implementation: `lazyedit/subtitle_translate.py`,
`lazyedit/subtitle_annotations.py`, `lazyedit/hanja_dictionary.py`.
The separately reported translation-output replacement transaction issue stays
with the owning workflow; see
`bug-reports/2026-10-06-korean-annotation-and-timing-review.md`.
