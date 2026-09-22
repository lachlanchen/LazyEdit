# One-shot subtitle language readiness and classical-lyric review

## Confirmed readiness bug

With global publication languages `fr,zh-Hant,ja,en`, processing one video with
`--languages zh-Hant,ja,en --no-publish` correctly generates three translations
and a three-row burn, but `GET /api/videos/{id}/process-status` reports
`translate: idle, Missing: fr` and `ready_for_publish: false`.

`VideoProcessStatusHandler` uses global publish options unless a publication
session exists. The one-shot override path can have no session. As a result,
`wait_for_process()` keeps polling after all requested work has finished.
The queued publish prerequisite check uses that same status and may reprocess
an already-reviewed render, overwriting translation edits.

Expected: readiness and waiting must use the languages requested by that job,
without changing global settings or adding an unwanted subtitle row. Carry the
effective run configuration through status/prerequisite checks, including the
no-session override case. Add a regression test with four global languages and
three requested languages.

Recovery used: stop only the waiting CLI after verifying all work was complete;
review the three-language translations, use the existing burn-subtitles API,
then use the existing synchronous publish handoff (`wait: true`,
`persistSettings: false`). This packages the reviewed output and submits it to
the normal remote serial queue without repeating processing. Verify the MP4
inside the ZIP has the same hash as the inspected file. HTTP `published` here
only means the remote queue accepted it; monitor the remote job to completion.

## Translation findings

Classical Chinese lyrics exposed shortcomings in the first Japanese pass:

- Some items remained Chinese (`鉛華弗御`, `髣髴兮`) rather than Japanese.
- Some ruby readings were wrong, and a token surface changed `游` to `遊`
  without updating the sentence surface.
- `首飾` in this classical context refers to head ornaments, not a necklace.
- Literal treatment of the shoe name `遠遊` falsely implied a journey.

Review natural target-language meaning as well as ruby coverage. Check that
token surfaces concatenate to the actual sentence. Context supplied for
metadata is not evidence that the translation stage consumed that context;
investigate the translation prompt/cache boundary before claiming this works.
The incident was recovered with reviewed, per-video translation artifacts and
the existing colored/ruby renderer; no global cache or model settings changed.

The first `metadata_ja` output was also Chinese despite the endpoint language.
Regenerating only Japanese metadata with explicit Japanese output guidance and
`use_cache: false` produced Japanese text. Add target-language validation for
metadata rather than treating an HTTP success as proof of correct language.

## Verification

- Three subtitle rows, lift 0, no French, native portrait without background fill.
- Corrected translation cue times unchanged; source song preserved.
- Normal logo and subtitle renderer used; no new video generation.
- Source media, personal context and private paths intentionally omitted here.
