# Korean Hanja And Open Subtitle Languages

## Request And Scope

The owner approved the completed Vancouver publication, then requested better
Korean Hanja restoration and the ability to add arbitrary subtitle languages.
This is a quality/code audit, not permission to regenerate or republish that
video. Existing exports, translations, settings and platform posts are unchanged.

The active LazyEdit owner is working on application/mobile/hosted changes.
Coordination was queued to that existing session. This change owns only the
isolated annotation repair, its tests and this report. UI/API language integration
is handed off; it is not claimed complete.

## Published Korean Evidence

Video 603 has four Korean cues, with the same reviewed audio timing:

| Time | Clean Korean | Restored roots |
| --- | --- | --- |
| 4.100-5.800 | 밴쿠버, 우리 도착했어! | 도착 -> 到着, reading 도착 |
| 11.780-14.640 | 바다를 먼저 볼까, 아니면 먼저 먹을까? | None |
| 18.720-20.300 | 먹으면서 볼 수 있어요! | None |
| 20.300-22.200 | 입 좀 닦고, 사진 찍자. | 사진 -> 寫眞, reading 사진 |

The actual rendered fourth row contains Hanja with Hangul ruby. Other Korean
tokens have romanization. The JSON and rendered frame agree; this is not a case
where the renderer discarded all Hanja. The two restored spellings agree with
the National Institute of Korean Language dictionary:

- [도착하다 / 到着하다](https://krdict.korean.go.kr/eng/dicSearch/SearchView?ParaWordNo=70745&nation=eng&nationCode=6)
- [사진 / 寫眞](https://krdict.korean.go.kr/eng/dicMarinerSearch/search?mainSearchWord=%EC%82%AC%EC%A7%84&nation=eng)

Few Han characters in a mostly native-Korean sentence are not by themselves a
failure. Do not translate native words into Chinese, rewrite natural dialogue
to increase the count, or claim every loanword/name has a Hanja spelling.
This inspection does not certify every pronunciation or the linguistic quality
of other Korean videos.

Evidence is in the normal video DATA folder:
`vancouver_four_buddies_30s_2026-10-03/translations/ko/`.
Local LALACHAN screenshots remain in its private runtime folder, not Git.

## Fixed: Repair Skipped Dictionary Review

`SubtitlesTranslator._request_han_annotations` previously consulted dictionary
candidates only if the first response passed structural validation. If tokens
were missing, mixed Hangul/Hanja incorrectly, used romanization instead of native
ruby, or rewrote locked text, the sole repair received the validation error but
no dictionary evidence. A structurally valid repaired response then returned
without that candidate check.

The repair now derives candidates from the already locked clean Korean text
when the tokens are invalid. It uses no untrusted token offsets in that branch.
Both the validation error and contextual candidate evidence go into the same
existing repair request. Correct first responses still take one request; the
maximum remains two annotation requests, excluding pre-existing transport retries.

The dictionary remains a candidate source, not an automatic replacement table.
Native homophones can remain Hangul after review. Text/timestamp locks, suffix
separation, full token coverage and the final structural validator remain intact.
Vietnamese does not receive Korean candidates.

Validation:

```bash
python -m pytest -q tests/test_multilingual_annotations.py tests/test_hanja_dictionary.py
```

- Four new regression cases failed before the fix and pass after it.
- 38 focused tests pass, including the actual renderer token loader, ruby size,
  root/particle wrapping, native homophones, offline dictionary fallback,
  immutable translation and the bounded repair limit.
- Tests use mocked model responses and local fixtures, not paid generation.
- No new live LLM quality benchmark or full video render was run for this patch.
- This fixes a demonstrated review gap, not a guarantee of perfect etymology.

The earlier whitespace/token diagnostic fix is commit `8a88df8`; see
[annotation recovery](2026-10-03-subtitle-annotation-recovery.md).
The underlying candidate design is documented in
[dictionary review](2026-10-01-hanja-dictionary-review.md).

## Confirmed Language Gaps

| Layer | Observed behavior |
| --- | --- |
| `lazyedit/languages.py` | 102 fixed language keys |
| `app.py::_normalize_translation_language` | Accepts registered codes/names; rejects unregistered variants/languages |
| `lazyedit/plugins/languages.py`, live `GET /api/languages` | Only 12 menu entries |
| `app/app/video/[id]/index.tsx` | 11-member `TranslateLang` union, fixed normalizer and choices |
| `app/app/video/[id]/burn-subtitles.tsx` | 11 fixed options, not the union of registry and completed translations |
| `process_specified_language_translation` | Generic grammar-token translator exists, but requires membership in `LANGUAGES` |

Read-only function probes, without importing the application or starting jobs:

| Input | API normalizer result |
| --- | --- |
| `ko`, `it`, `de`, `th` | Accepted unchanged |
| `pt-BR`, `sr-Latn`, `fil`, `eo` | `None` |

An explicit settings selection of only `pt-BR` becomes the default
`ja,en,zh-Hant` through `_sanitize_translation_languages`. This silent fallback
can produce an unintended language set. The single-language translate endpoint
instead returns an unsupported-language error.

Therefore CLI/backend support for many languages is present, but arbitrary
language selection end to end is not. A mocked generic routing/schema probe
passed for 100 registered keys; Korean and Vietnamese need their specialized
reading fixtures and were tested separately. This is not proof of font coverage,
shaping, translation quality or public publication for 102 languages.

## Owner Handoff: General Language Support

Use one canonical language registry/resolver shared by the API, settings, CLI
and subtitle selectors. Preserve established aliases and special annotators.
Keep subtitle languages separate from the application's 11 UI locales and from
the ASR model's supported input languages.

Allow a validated additional language code and display name without adding a new
translation function or editing several frontend lists. Use an existing locale
resolver if available; validate canonical tags and safe path usage. A valid tag
does not prove provider or renderer capability. Return an explicit capability
error/warning rather than a fabricated successful translation.

The generic route should retain clean native text, timestamps, grammar tokens,
color and language identity. Specialized reading support is an optional capability:
Korean Hanja, Japanese furigana, Chinese pinyin and Arabic RTL should not be
advertised for an unrelated script. Imported/completed translations must remain
selectable even if absent from a curated common-language menu.

Explicit unsupported settings must fail clearly, not silently reset to defaults.
Missing settings may still inherit defaults. Preserve ordered language slots and
all unrelated per-job settings. Metadata language support should be distinguished
from subtitle support rather than implied by it.

Suggested acceptance checks (no real publication):

1. Select `de`, `it`, `th` from the UI; reload; assign to the bottom subtitle slot.
2. Add `pt-BR`, `sr-Latn` and a language outside the old list such as `eo`; verify
   the exact choice survives API/settings/CLI round trips.
3. Reject unknown/unsafe tags clearly, including path separators and traversal;
   do not substitute a different language set.
4. Retain an imported translation whose code is outside the common dropdown.
5. Run an actual short render for Latin, Thai/Indic, RTL and CJK examples; inspect
   glyph coverage, shaping, ruby, clipping and source-language audio icons.
6. Confirm `ko,zh-Hant,ja,en` still renders EN/JA/ZH/KO top to bottom, without
   changing the existing no-lift layout or publishing the test artifact.
7. Check context-sensitive Hanja with school/arrival/photo roots, attached
   particles, native homophones and malformed-token recovery. Evaluate the
   readings as well as the number of restored roots. Include single-syllable
   roots in the audit; the IME candidate helper currently starts at two syllables.

The active owner should record implementation, focused tests and visual evidence
before declaring open-language support complete. Current store/release work and
the existing remote publisher must remain undisturbed.
