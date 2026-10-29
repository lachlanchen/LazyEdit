# Translation edits can render stale wording

Observed on the existing owner backend during publication preparation, before
any public post. Video 641, cue index 4, EN/JA/FR; video 642, JA cues 0 and 4.

## Reproduction

1. Complete normal translation and burn.
2. POST `/api/videos/641/translation?lang=en` with index 4 and corrected text.
3. The API updates `en` but preserves `tokens` from the old text.
4. Call the independent `/burn-subtitles` endpoint with the existing layout.
5. The image still shows the old English wording. French behaves the same way.

The save handler invalidates annotations only for Japanese. The renderer accepts
nonempty content tokens without checking that their concatenated surface matches
the authoritative text. Consequently, an apparently successful text edit can be
absent from the public artifact.

Separately, CLI `--steps burn --no-publish` ran a translation dependency and
restored cached old text. Use the independent burn endpoint to preserve reviewed
translations until this behavior is clarified.

## Scoped Recovery

Saved the pre-repair translation JSONs outside source control. Cleared stale
tokens for the two changed EN/FR cues; supplied reviewed JA readings for the
changed cues; used the existing independent burn endpoint with the previous
layout and configured logo. No source video/audio changes or service restart.

Evidence and recovery script:
`LALACHAN/outputs/publication-20261029/`.
The `snowy-yurt-warm-hands.jpg` pre-repair frame shows edited Japanese alongside
the old English and French. Final publication QA is recorded separately.

## Suggested Acceptance Tests

- Text edits invalidate/rebuild annotations for every supported language.
- Rendered token surfaces agree with the edited text, allowing whitespace-only
  normalization, while preserving cue timing and speaker icons.
- Japanese edits retain kanji readings and kana romaji after regeneration.
- A burn-only action does not overwrite manually reviewed translations.

This report does not claim a backend fix or authorize restarting the shared
service. Keep current release and other users' jobs unchanged.
