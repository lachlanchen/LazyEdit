# Authoritative SRT Fast Publish

Use this workflow when a video already has reviewed subtitle timing and text. It imports the SRT as both the original and polished transcript, skips Whisper, and keeps the normal LazyEdit translation, ruby/pinyin rendering, portrait blur-fill, logo, metadata, and AutoPublish stages.

## One-command publish

```bash
python scripts/lazyedit_publish.py \
  --video input.mp4 \
  --subtitle-file reviewed.zh-CN.srt \
  --subtitle-language zh \
  --prompt-file story-context.md \
  --publish-category lalachan \
  --languages fr,zh-Hant,ja,en \
  --portrait-blur-fill \
  --portrait-blur-mode lalachan \
  --logo \
  --logo-position top-right \
  --platforms shipinhao,youtube,instagram,douyin \
  --guided-monitor \
  --wait
```

`--prompt-file` remains metadata context. When `--subtitle-file` is present, it no longer implicitly enables AI subtitle correction. Add `--correct-subtitles` explicitly only when the imported wording should still be revised.

## Safety behavior

- Rejects empty SRT files, malformed timestamps, overlapping cues, and cues beyond the video duration.
- Writes the imported cues to both `mixed` and `mixed_polished` variants.
- Preserves cue boundaries while multilingual translations are generated.
- Reports `skipped_whisper: true` and the imported cue count.
- Omits `transcribe` from both the direct CLI process and deferred serial publish worker unless `--steps` explicitly requests it.
- Reuses the standard publish queue; this is not a separate publishing implementation.

Use contextual replacement text for unintelligible generated speech only after reviewing the matching visual action. Do not phonetically transcribe gibberish, and do not invent dialogue over silent scenes.

## Validated run

On 2026-08-30, video `546` imported three reviewed Chinese cues, generated three aligned cues in each requested language, rendered the normal blur-fill/subtitle/logo output, and completed one four-platform publish job (`385`). That run exposed a redundant late `transcribe` step even though the imported polished cues remained authoritative. The CLI and serial publish worker now omit that step by default when `--subtitle-file` is present.
