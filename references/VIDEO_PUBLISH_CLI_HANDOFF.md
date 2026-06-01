# LazyEdit Video Publish CLI Handoff

This guide is for another Codex session, for example a Rarachan/LALACHAN session
that generated a video and already has the story/script prompts. It can publish
through LazyEdit without opening the Studio UI.

## Runtime Assumptions

- LazyEdit backend is running at `http://127.0.0.1:18787`.
- AutoPublish on `lazyingart` is reachable from LazyEdit for platform posting.
- Run commands from the LazyEdit repository:
  `/home/lachlan/DiskMech/Projects/lazyedit`.
- Use the `lazyedit` conda environment when calling Python locally:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

## CLI Entry Points

Direct Python:

```bash
python scripts/lazyedit_publish.py --help
```

Via npm package CLI:

```bash
npm run publish-video -- --help
lazyedit publish-video -- --help
```

The CLI uses the LazyEdit HTTP API. It uploads the video, optionally runs AI
subtitle correction, runs the process pipeline, queues AutoPublish, and monitors
until completion by default.

## Language Order

`--languages` is bottom-to-top subtitle order. Examples:

- `zh-Hant,ja,en`: Chinese bottom, Japanese above, English above.
- `fr,zh-Hant,ja,en`: French at the very bottom, Chinese above, Japanese above,
  English above.

The CLI sends `persistSettings=false` by default, so it does not change the
Studio web UI's saved language selection. Add `--persist-settings` only when
you intentionally want to update Studio defaults.

## One-Command Publish Example

For the generated Alps/Hamburg hamburger video:

```bash
python scripts/lazyedit_publish.py \
  --api-url http://127.0.0.1:18787 \
  --video /home/lachlan/ProjectsLFS/LALACHAN/Videos/2026-06-01-alps-hamburg-hamburger_01.mp4 \
  --title 2026-06-01-alps-hamburg-hamburger \
  --platforms shipinhao,youtube,instagram \
  --languages zh-Hant,ja,en \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-01-alps-hamburg-hamburger-submit-15s.md \
  --metadata-prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-01-alps-hamburg-hamburger-xyq-storyboard.md \
  --correct-subtitles \
  --use-polished \
  --burn-subtitles \
  --wait
```

For Shipinhao only:

```bash
python scripts/lazyedit_publish.py \
  --video /home/lachlan/ProjectsLFS/LALACHAN/Videos/2026-06-01-alps-hamburg-hamburger_01.mp4 \
  --platforms shipinhao \
  --languages zh-Hant,ja,en \
  --prompt-file /home/lachlan/ProjectsLFS/LALACHAN/references/prompts/2026-06-01-alps-hamburg-hamburger-submit-15s.md \
  --correct-subtitles \
  --use-polished \
  --wait
```

## Correct Subtitles First, Publish Later

If the other session wants to upload and correct subtitles without publishing:

```bash
python scripts/lazyedit_publish.py \
  --video /path/to/generated.mp4 \
  --no-publish \
  --prompt-file /path/to/story-or-script.md \
  --correct-subtitles \
  --use-polished \
  --wait
```

The correction is saved as LazyEdit's shared polished subtitle version for that
video. Later runs should use:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --platforms shipinhao,youtube,instagram \
  --languages zh-Hant,ja,en \
  --use-polished \
  --wait
```

## Existing Video ID

If the video is already in LazyEdit Studio, skip upload:

```bash
python scripts/lazyedit_publish.py \
  --video-id 344 \
  --platforms shipinhao \
  --languages zh-Hant,ja,en \
  --use-polished \
  --wait
```

## API Equivalent

The CLI is a wrapper around these endpoints:

1. Upload:

```bash
curl -X PUT \
  --data-binary "@/path/to/video.mp4" \
  "http://127.0.0.1:18787/upload-stream?filename=video.mp4&title=video&source=api"
```

2. Optional AI subtitle correction:

```bash
curl -X POST "http://127.0.0.1:18787/api/videos/VIDEO_ID/subtitle-correction" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "ai",
    "prompt": "Use the supplied story/script to fix recognition errors. Preserve timing.",
    "sourceVariant": "polished",
    "use_cache": true
  }'
```

3. Process:

```bash
curl -X POST "http://127.0.0.1:18787/api/videos/VIDEO_ID/process" \
  -H "Content-Type: application/json" \
  -d '{
    "async": true,
    "steps": ["keyframes", "caption", "transcribe", "translate", "burn", "metadata_zh", "metadata_en", "cover"],
    "translationLanguages": ["zh-Hant", "ja", "en"],
    "usePolishedSubtitles": true,
    "burnSubtitles": true,
    "metadataPrompt": "story/script context",
    "notes": "story/script context",
    "persistSettings": false
  }'
```

4. Poll process:

```bash
curl "http://127.0.0.1:18787/api/videos/VIDEO_ID/process-status?publicationSessionId=SESSION_ID"
```

5. Publish:

```bash
curl -X POST "http://127.0.0.1:18787/api/videos/VIDEO_ID/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": {"shipinhao": true, "youtube": true, "instagram": true},
    "persistSettings": false,
    "options": {
      "burnSubtitles": true,
      "translationLanguages": ["zh-Hant", "ja", "en"],
      "usePolishedSubtitles": true,
      "subtitleSourceVersion": "polished",
      "publicationSessionId": SESSION_ID,
      "publicationMode": "override",
      "persistSettings": false
    }
  }'
```

6. Poll publish queue:

```bash
curl "http://127.0.0.1:18787/api/autopublish/queue"
```

## Useful Options

- `--platforms shipinhao,youtube,instagram`: target platforms.
- `--languages zh-Hant,ja,en`: subtitle order, bottom-to-top.
- `--prompt-file FILE`: use the same story/script as subtitle correction and
  metadata context.
- `--correction-prompt-file FILE`: correction-only prompt.
- `--metadata-prompt-file FILE`: metadata-only context.
- `--new-run`: create a separate publication session.
- `--no-publish`: upload/process/correct only.
- `--no-process`: queue publish and let the publish worker process if needed.
- `--subtitle-lift-ratio 0.1`: subtitle lift from bottom; use `0` for no lift.
- `--subtitle-rows 4`: reserved subtitle rows independent of selected languages.
- `--subtitle-font-scale 1.0`: global subtitle scale.
- `--no-subtitle-font-bold`: disable bold text.
- `--no-subtitle-outline-bold`: disable thick outline.

## Handoff Prompt For Another Codex Session

Use this prompt in the generating repo:

> Use `/home/lachlan/DiskMech/Projects/lazyedit/scripts/lazyedit_publish.py` to
> upload and publish the generated video through LazyEdit. Pass the generated
> script/story markdown as `--prompt-file` so LazyEdit can correct subtitle
> recognition errors and use the same story context for metadata. Use polished
> subtitles, burn subtitles, and explicit bottom-to-top language order. Do not
> persist Studio settings unless asked.

