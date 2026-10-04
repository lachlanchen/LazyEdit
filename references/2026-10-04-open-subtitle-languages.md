# Open Subtitle Targets: Source Integration

## Status And Boundaries

Implemented and locally verified on 2026-10-04, following the
[LALACHAN audit](2026-10-03-hanja-and-open-subtitle-languages.md). This is a source
change awaiting deployment after LightMind reviewer qualification. It does not
replace the current worker, install a native build, publish, regenerate video
603, call a paid provider or modify persisted user settings.

The focused Korean repair in `17fd4ee` and prior annotation fix `8a88df8` remain
intact. No changes were made to `subtitle_annotations.py`, `hanja_dictionary.py`,
the ASR language table or the external furigana/EchoMind symlinks. The only
translator change resolves the target/name of the existing generic translation
method. Korean and Vietnamese still use their specialized bounded annotation
paths, with native text and timestamps locked.

## One Subtitle Resolver

`lazyedit/subtitle_languages.py` now resolves subtitle targets independently of
the 11 UI locales and Whisper's input languages. It reads the existing language
table as a seed and uses Babel's CLDR data for additional language/script/region
tags. The common catalogue has **103 unique canonical targets**; additional
known locales such as `pt-BR` and `sr-Latn` resolve on demand. `fil` and `eo` are
also selectable. This does not expand Whisper's recognizer or the metadata
output-language templates.

Codes have a two/three-letter primary language, optional four-letter script and
optional two-letter or three-digit region. Unknown locales, path separators,
traversal, NUL, extensions and private-use tags fail. The resolver retains
existing registered names and Chinese/Cantonese aliases: `zh`/`zh-TW` become
`zh-Hant`, `zh-CN` becomes `zh-Hans`, and `zh-yue-hk` becomes `yue`.

Explicit invalid lists are rejected atomically with HTTP 400 and error code
`unsupported_subtitle_language`, before saving preferences or starting the
processing job. They are never partly dropped or replaced by Japanese/English/
Chinese. Missing settings inherit the existing defaults; an explicit `[]` stays
empty. Burning subtitles with no selected language is an error. Camel-case and
snake-case request aliases must agree if both are provided.

Order remains **bottom to top**. The backend reverses placement into its physical
slots without shrinking the reserved grid or adding lift. CLI language overrides
now retain the reserved row count; `--subtitle-rows` can still explicitly override
it. No saved default order or lift ratio is changed by this integration.

## API And Clients

The local/private backend supports:

```http
GET /api/languages
POST /api/languages
Content-Type: application/json

{"languages":["pt-br","sr-Latn","fil","eo"]}
```

The POST returns canonical `codes` in order and matching `languages` descriptors.
It only validates; it does not register languages globally, save preferences,
translate, create a task or publish. The body must contain only a `languages`
list, with at most 40 entries. Duplicate aliases collapse to one code.

Descriptors include `code`, `name`, `grammarColors`, `reading`, `rtl`,
`requiresPreview`, and a `renderingWarning` where applicable. A valid tag and
`grammarColors: true` describe routing/token support, not grammatical accuracy,
provider availability or full glyph/shaping coverage.

Authenticated Studio clients get the same catalogue/resolution at
`GET/POST /v1/studio/languages`, requiring `media.read`. Check
`capabilities.subtitleLanguageCatalogue` first: the currently held worker does
not have this extension. Always use the account's own API base and existing
scoped authentication; no owner fallback or new privilege is introduced.
The contract is in `studio/openapi.json`.

Expo's Publish, video translation and burn-slot screens now use the API catalogue
plus saved choices and imported/completed translations. A custom-code input
validates through the API before adding a choice. An imported entry is visible
even when absent from the common catalogue; this does not override backend
validation or claim that an unknown imported language can be regenerated.
The new picker messages cover all 11 UI locales. Failed saved-setting loads are
shown and cannot silently save screen defaults; Publish offers a reload action.

The iOS composer has a searchable catalogue/custom-code sheet and retains drag
ordering. Android has the catalogue plus its existing free code field. Both
validate the final plan against the backend. Native composition retains its
existing maximum of eight rows; language catalogue validation alone is not a
promise that 40 simultaneous rows will look good. New choices are per-run unless
the user explicitly persists preferences. Reuse still uses the saved render.

The dependency-free Python CLI forwards codes to that same backend. A rejected
saved-language response is now propagated instead of swallowed by its settings
loader. A mocked no-process/no-publish invocation verified `pt-BR,sr-Latn,fil,eo`,
four reserved rows, zero lift and no preferences mutation. Real use must select
the account's proper server and follow the existing scoped client/publish guide.

## Specialized Readings And Rendering Limits

Exact canonical targets retain their current paths:

| Target | Reading/restoration route |
| --- | --- |
| `ja` | Kanji furigana and configured kana romaji |
| `zh-Hant`, `zh-Hans` | Pinyin |
| `yue` | Jyutping capability, subject to existing render choices |
| `ko` | Context-reviewed Hanja roots, Hangul ruby, native-word romanization |
| `vi` | Context-reviewed Chu Han roots, Vietnamese readings |
| Other resolved tags | Generic native text and grammar tokens |

Regional/script variants are not automatically advertised as specialized
annotators. For example, `ko-KR` can be resolved generically but does not claim
the `ko` Hanja route. Use the advertised canonical target when readings are
required. Provider quality, linguistic choices and readings still need review;
do not rewrite native Korean merely to increase the Hanja count.

Local synthetic fixtures used the actual slot burner, a 540×960 one-second
source, four reserved rows, zero lift and the existing Arial Unicode font.
They exercised `pt-BR`, `sr-Latn`, `fil`, `eo`, Thai, Hindi, Arabic, Japanese,
Chinese and Korean. Sampled text was nonblank and did not match the missing-glyph
sentinel. This only tests the sample glyphs, not entire scripts.

The inspected EN/JA/ZH/KO frame preserved physical top-to-bottom order and showed
Japanese `写真`/`しゃしん`, Chinese `照片`/`zhào piàn`, Korean `學校`/`학교`, plus
romanization on native Korean words. Main text and ruby fit without overlap.
Thai/Devanagari sample glyphs and the Latin samples rendered visibly.

**RTL is not fully verified.** Arabic words are individually shaped, but their
grammar-token order is wrong for the two-token test. RTL descriptors and the
picker/native plan now carry a preview warning. See the separate
[RTL token-order report](../bug-reports/2026-10-04-rtl-subtitle-token-order.md).
This integration does not change the renderer or claim that warning fixes it.

Ignored local evidence is under `temp/open-subtitle-languages-20261004/`:
`report.json`, `contact-sheet.png`, `latin.png`, `scripts.png`, `ordered.png`,
small fixture JSON and disposable fixture/burned MP4s. No source video, user
transcript, profile, credential or model output was copied into this report.

## Verification And Release Gate

```bash
/home/lachlan/miniconda3/envs/lazyedit/bin/python -m pytest -q \
  tests/test_subtitle_languages.py tests/test_multilingual_annotations.py \
  tests/test_hanja_dictionary.py tests/test_lazyedit_publish_cli.py \
  tests/test_studio_publish_processing_quote.py
node --test hosted/test.mjs hosted/*.test.mjs studio/test.mjs studio/*.test.mjs app/lib/subtitleLanguages.test.mjs
cd app
./node_modules/.bin/tsc --noEmit
```

- 93 focused Python checks passed together; the CLI suite has 19 cases.
- 45 Studio/hosted/frontend tests passed, including ownership, unchanged
  publication idempotency, language errors and absence of mutation on validation.
- TypeScript, Python/Node syntax and OpenAPI JSON validation passed.
- Android `:app:compileDebugJavaWithJavac` passed offline with one worker and a
  768 MB single-use Gradle daemon, which stopped after the check.
- `swiftc -frontend -parse` passed using the existing Mac route. This is syntax
  validation, not a full signed iOS build or device UI acceptance.
- No live model translation benchmark, store build distribution or publication
  smoke test was performed.

Promote backend, hosted dependency image, Studio API and frontend together at a
safe release boundary. Do not deploy only the new selector against the old
backend's 12-entry catalogue/unsupported POST. Preserve the LightMind acceptance
lock, existing worker/image and all personal/publication state until qualification
ends. Deployment, native device acceptance and the separate RTL fix remain open.
