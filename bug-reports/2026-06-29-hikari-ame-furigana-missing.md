# Bug: Hikari Ame Japanese Furigana Track Has Empty Readings

## Summary

The Hikari Ame MV publish output includes timed Japanese translation JSON, but the furigana metadata is empty. The website can preserve ruby/furigana when provided, but this run only exposes plain Japanese strings.

## Evidence

Affected run:

```text
/home/lachlan/DiskMech/Projects/lazyedit/DATA/aya_chan_hikari_ame_full_mv_song_locked_portrait_fg30_bottom40_2026-06-29
```

Files checked:

```text
translations/ja/aya_chan_hikari_ame_full_mv_song_locked_portrait_fg30_bottom40_2026-06-29_ja_furigana.json
burn/aya_chan_hikari_ame_full_mv_song_locked_portrait_fg30_bottom40_2026-06-29_ja_furigana_speaker_ja.json
```

Example rows:

```json
{
  "start": "00:00:00,000",
  "end": "00:00:05,090",
  "ja": "窓辺で小さなアヤちゃん",
  "ruby": "窓辺で小さなアヤちゃん",
  "tokens": [],
  "furigana_pairs": []
}
```

The same pattern appears on kanji-heavy lines such as `雨粒を星に変える`, `胸の鈴が光って`, `踊りながら`, `勇気が花になる`, and `朝が来る`.

## Expected Behavior

For Japanese learner-facing subtitle exports:

- `furigana_pairs` should contain base text and reading data for kanji terms.
- `ruby` should either contain valid `<ruby><rt>...</rt></ruby>` markup or enough structured token metadata to render furigana downstream.
- The burn JSON and translation JSON should preserve the same reading metadata.

## Actual Behavior

- `ruby` is identical to `ja`.
- `tokens` is empty.
- `furigana_pairs` is empty.
- Downstream pages cannot render furigana without inventing readings, which should be avoided.

## Impact

LalaMedias and future MV websites can render timed multilingual subtitles, but Hikari Ame cannot show Japanese readings. This weakens Japanese learning support and makes the MV harder for non-Japanese readers.

## Suggested Fix

Check the Japanese translation/subtitle correction path for MV/music publishes:

1. Ensure the furigana analyzer runs after subtitle correction and before both `translations/ja/*_ja_furigana.json` and `burn/*_ja_furigana*.json` are written.
2. Verify that the MV/music route does not skip furigana generation when the source text is already Japanese.
3. Add a validation warning when a `_ja_furigana.json` file contains kanji but has no `furigana_pairs` and no `<rt>` markup.
4. Add a regression sample using the Hikari Ame lines above.

