# Studio Response: Hanja And Open Subtitle Languages

Updated 2026-10-04 after the LALACHAN handoff. General language integration is
implemented and tested in source. **Deployment is held during LightMind reviewer
acceptance.** No worker replacement, restart, paid model call or real post occurred.

Implementation commit: `e572f54` (`open subtitle language selection across Studio`).

## Implemented

- One Babel/CLDR subtitle resolver, separate from the 11 UI locales and unchanged
  Whisper input-language table. The common catalogue has 103 canonical entries;
  `pt-BR`, `sr-Latn`, `fil`, `eo` and further known script/region tags resolve.
- Local API/settings, generic translator and Studio validation use that resolver.
  `GET/POST /api/languages` lists/validates targets without persisting or processing.
  The authenticated equivalent is `GET/POST /v1/studio/languages` with `media.read`.
  Linked clients check `capabilities.subtitleLanguageCatalogue` before using it.
- Unsupported explicit lists fail atomically with HTTP 400 and
  `unsupported_subtitle_language`; no dropped entries or default substitution.
  Missing choices inherit defaults, while explicit empty choices remain empty.
- Publish/translation/burn selectors include catalogue, saved and imported
  languages. Custom codes validate before addition. New picker messages cover
  all 11 UI locales. Failed saved-setting loads are visible rather than saved
  back as defaults. Native iOS/Android composition uses the shared catalogue.
- CLI one-shot tags survive unchanged; rejected saved languages are propagated,
  explicit empty choices are retained and overriding languages does not shrink
  reserved rows. Bottom-to-top ordering, zero selected lift, existing defaults,
  per-run settings and saved-run reuse are preserved.

## Focused Hanja Lane Preserved

Retained `17fd4ee` and `8a88df8`; the candidate-review/annotation algorithms remain
unchanged. No edits to `subtitle_annotations.py`, `hanja_dictionary.py`,
`languages.py`, furigana or EchoMind. My only `subtitle_translate.py` change
resolves the generic target code/name. Korean/Vietnamese specialized routes and
the bounded dictionary-informed repair remain intact. Vancouver video 603 and
all existing exports/posts are unchanged.

## Evidence

- 93 distinct focused Python checks passed: new language/API contracts, the
  existing 38 Hanja/annotation checks, CLI and processing quote checks. The final
  complete focused suite passes; all 19 CLI cases pass.
- 45 Studio/hosted/frontend tests pass, including imported choices, scoped API,
  malformed responses, per-run tags, ordering and unchanged posting isolation.
- TypeScript and Python/Node/OpenAPI syntax checks pass. Android Java compilation
  passes offline; Swift frontend parsing passes on the existing Mac route.
- Local synthetic actual burns cover Latin targets, Thai, Hindi, Arabic and
  Japanese/Chinese/Korean. The EN/JA/ZH/KO frame shows correct order, Japanese
  furigana, Chinese pinyin and Hanja/Hangul/native romanization without overlap.
  No paid/provider translation or public publication was used as a test.

Actual ignored fixtures, contact sheet, first frames and glyph report are under
`temp/open-subtitle-languages-20261004/`. The complete contract, exact test commands,
code paths, source/deployment boundary and rendering caveats are in
[implementation notes](../../references/2026-10-04-open-subtitle-languages.md).

## Deferred And Unsupported

The currently held worker remains `editor-first-20261004h`; its start time is
unchanged. Backend PID 5953, Expo PID 8056 and the reviewer acceptance lock remain.
These new API/UI changes are not certified live, and no new native beta was
distributed. Promote the backend/Studio/frontend/dependency image together only
after qualification releases the hold; native device acceptance is still needed.

Tag acceptance is not a guarantee of provider quality, etymology, font coverage
or specialized readings for every regional variant. Specialized `ja`, `ko`, `vi`,
Chinese and Cantonese capabilities are advertised only on their exact targets.

The actual Arabic test exposed an existing **RTL token-order defect**: individual
words are shaped, but word order is wrong. The catalogue, PWA picker and native
plan surface a preview warning. Repair is documented separately and is not claimed
complete: [RTL report](../../bug-reports/2026-10-04-rtl-subtitle-token-order.md).

The implementation and full test/render contract are committed in `e572f54`.
This response's commit reference is a documentation follow-through.
No acceptance lock, private runtime evidence, credentials or media is committed.
