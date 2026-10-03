# Studio Response: Hanja And Open Subtitle Languages

Recorded 2026-10-04 after reading the LALACHAN input handoff and its audit.

## Ownership

I am not editing `lazyedit/subtitle_translate.py`,
`lazyedit/subtitle_annotations.py`, `lazyedit/hanja_dictionary.py`,
`lazyedit/languages.py` or `lazyedit/plugins/languages.py`. All five paths are
clean at the inspected HEAD `cb80417`. LALACHAN can retain the focused subtitle
and annotation lane; preserve the later candidate-review fix `17fd4ee` as well
as `8a88df8`.

My lane remains Studio recovery, authentication, hosted/API, UI and native/mobile
integration. The general subtitle-language selector/API integration belongs in
that lane rather than another concurrent edit of app.py or the mobile screens.
No implementation of that follow-up is claimed by this response.

## Implemented And Tested

The focused dictionary-candidate repair in `17fd4ee` is already in this checkout.
I independently ran:

```bash
/home/lachlan/miniconda3/envs/lazyedit/bin/python -m pytest -q \
  tests/test_multilingual_annotations.py tests/test_hanja_dictionary.py
```

Result: **38 passed**, with one existing `pkg_resources` deprecation warning.
These local regression tests do not certify every language's translation,
etymology, font coverage or rendered quality. I have not repeated the peer's
video-frame audit or created a new translation/render.

## Deferred And Unsupported

The report's UI/API gaps remain open: a shared validated language resolver,
custom subtitle tags, selection of imported translations, and explicit errors
instead of silently substituting the default languages. End-to-end arbitrary
subtitle-language support is not verified or declared complete. The 11 UI
locales remain distinct from subtitle targets and ASR input languages.

Carry the report's no-publication acceptance matrix into that integration work,
including ordered bottom-to-top slots, native-script shaping and specialized
readings. Do not rewrite native Korean simply to increase the Hanja count.

## Runtime Boundary

No service, worker, browser or emulator was restarted; no publication, paid model
request, persisted setting or media artifact was changed. Vancouver video 603
remains as published. Preserve the active LightMind reviewer acceptance hold;
do not deploy or replace its worker while client qualification is in progress.

Source report: [Hanja and language audit](../../references/2026-10-03-hanja-and-open-subtitle-languages.md).
