# RTL Grammar Tokens: Word Order Needs Repair

## Observed In A Local Fixture

While verifying open subtitle targets, the actual slot burner rendered the
Arabic sentence `الكتاب جميل` from two noun/adjective grammar tokens. Each word
is shaped and visible, but the tokens are laid out in logical left-to-right
sequence. The first word should be on the right. The coloured token render
therefore has incorrect visual word order.

This is an existing renderer limitation, not a failed locale lookup or missing
Arabic font. No real video, translation, publication or settings were changed
to diagnose it. The ignored contact sheet and four-slot burn are in
`temp/open-subtitle-languages-20261004/contact-sheet.png` and `scripts.png`.

Synthetic cue:

```json
{
  "start": "00:00:00,000",
  "end": "00:00:01,000",
  "ar": "الكتاب جميل",
  "tokens": [
    {"surface": "الكتاب", "word": "الكتاب", "reading": "", "type": "noun"},
    {"surface": "جميل", "word": "جميل", "reading": "", "type": "adjective"}
  ]
}
```

The reproduction used `burn_video_with_slots`, the normal grammar palette and
`fonts/arial-unicode-ms.ttf`, on a 540×960 solid fixture, four reserved rows and
zero lift. The relevant local integration is
`lazyedit/subtitles_burner/burner.py` and its existing external ruby renderer.
Do not edit the external `furigana` symlink from this repository.

## Current Mitigation And Remaining Work

The subtitle-language catalogue now reports `rtl: true`, `requiresPreview: true`
and a `renderingWarning`. The PWA picker and native plan show the warning.
This is disclosure, not a rendering fix; do not certify the current RTL route
as fully correct based only on word shaping or successful provider JSON.

A follow-up should resolve bidi visual runs across the complete line while
retaining the mapping from glyphs/runs to grammar colours and optional ruby.
Do not reverse Unicode characters or blindly reverse all tokens: Arabic plus
Latin product names, numbers, punctuation and wrapped lines need distinct bidi
handling. Keep source text, timestamps and stored token identity unchanged.

Acceptance must cover at least two Arabic words, mixed Arabic/Latin text,
decimals, punctuation, multiple lines, Hebrew, Persian, colours and reading
alignment. Use synthetic fixtures and preview evidence before any publication.
The current release and ongoing reviewer worker must remain undisturbed.
