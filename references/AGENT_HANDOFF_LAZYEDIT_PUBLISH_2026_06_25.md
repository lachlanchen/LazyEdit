# Agent Handoff: Use LazyEdit To Correct, Process, And Publish Videos

Date: 2026-06-25

This note is for another Codex, AgInTiFlow, or automation agent that needs to use LazyEdit without relying on this chat history. It describes how to upload or select a video, correct subtitles with context, generate metadata, burn subtitles and the LazyEdit logo, publish through AutoPublish, and verify the final result.

## Mental Model

LazyEdit is the local orchestrator. It owns:

- video import/upload;
- transcription;
- AI subtitle correction and polished subtitle storage;
- translation;
- subtitle/logo burn;
- metadata generation;
- cover extraction;
- ZIP/package creation;
- local publish queue.

AutoPublish is the remote platform poster. It runs on the Raspberry Pi host `lazyingart` and owns:

- Shipinhao browser automation;
- YouTube browser/API automation;
- Instagram browser automation;
- platform login sessions and remote queue state.

The normal path for agents is:

1. Identify the exact source video.
2. Gather context for subtitle correction and metadata.
3. Run the LazyEdit CLI or API.
4. Monitor LazyEdit and AutoPublish queues.
5. Verify platform completion.

Prefer the CLI unless you specifically need low-level API calls.

## Runtime Map

- LazyEdit repo: `/home/lachlan/DiskMech/Projects/lazyedit`
- LazyEdit API: `http://127.0.0.1:18787`
- LazyEdit Studio: `http://127.0.0.1:18791/editor`
- CLI: `/home/lachlan/DiskMech/Projects/lazyedit/scripts/lazyedit_publish.py`
- AutoPubMonitor repo: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Nutstore AutoPublish import folder: `/home/lachlan/Nutstore Files/AutoPublish/AutoPublish`
- Remote AutoPublish host: `ssh lachlan@lazyingart`
- Remote AutoPublish repo: `/home/lachlan/Projects/autopub`
- Remote AutoPublish API: `http://lazyingart:8081`
- Remote AutoPublish tmux session: `autopub`
- Shipinhao Chromium debug port: `127.0.0.1:5006`
- Shipinhao Chromium profile: `/home/lachlan/chromium_dev_session_5006`

## Environment Setup

Run local commands from the LazyEdit repo:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

Check services:

```bash
curl -fsS http://127.0.0.1:18787/api/videos | jq '.videos[:3] | map({id,title,created_at,file_path})'
curl -fsS http://lazyingart:8081/publish/queue | jq .
```

If the frontend is needed:

```bash
tmux capture-pane -pt lazyedit:0 -S -80 | tail -n 80
```

## Core Rules For Agents

- Use polished/corrected subtitles for all real publishes unless the user explicitly asks for original subtitles.
- Burn the configured LazyEdit Studio logo at top-left for real publishes unless the user explicitly says no logo.
- Do not invent a new logo. Use the existing `logo_settings`.
- Use `--use-current-settings` to inherit Studio subtitle layout, language order, lift ratio, font scale, bold, outline, and logo defaults.
- CLI one-shot overrides do not change Studio settings unless `--persist-settings` is passed.
- `--languages` is bottom-to-top subtitle order.
- Avoid duplicate publishes. Use `--no-publish` first if you only need to inspect generated package/subtitles.
- If the user says "same version", "last run", "already finished run", or "no rerun", use `--no-process`.
- For generated videos, verify that the file is the intended final video before upload or publish. Do not blindly use `Downloads/final_video (N).mp4`.
- For browser-upload platforms such as Instagram, verify that the MP4 inside the
  publish ZIP is H.264/AVC `avc1`, `yuv420p`, AAC when audio exists, and
  browser-faststart. HEVC/H.265 `hvc1`, AV1, or unknown codecs are not
  acceptable terminal publish artifacts.
- Before claiming success, verify both LazyEdit local publish status and remote AutoPublish status.
- If visible platform state conflicts with queue state, inspect the live browser
  and let visible error/success text override queue assumptions.

## Verify Logo Settings Before Publish

For real publishes, check the persisted logo settings:

```bash
curl -fsS http://127.0.0.1:18787/api/ui-settings/logo_settings | jq .
```

Expected:

- `enabled: true`
- `logoPath` present
- `position: "top-left"`

Normal processed outputs with logo usually end in:

```text
_subtitles_logo.mp4
```

## Find Or Upload The Video

### Existing LazyEdit Video

List latest videos:

```bash
curl -fsS http://127.0.0.1:18787/api/videos \
  | jq '.videos[:20] | map({id,title,created_at,file_path})'
```

Use `--video-id VIDEO_ID` when the video is already listed.

### Direct CLI Upload

Use this when another agent generated a video and gives an exact path:

```bash
python scripts/lazyedit_publish.py \
  --video /absolute/path/to/video.mp4 \
  --title stable_title_COMPLETED \
  --use-current-settings \
  --no-publish \
  --wait
```

### Nutstore Import

Use Nutstore when the workflow expects AutoPubMonitor to import completed files:

```bash
cp -f /absolute/path/to/video.mp4 \
  "/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/stable_title_COMPLETED.mp4"
```

Watch import:

```bash
tmux capture-pane -pt autopub-monitor:0.1 -S -100 | tail -n 100
tmux capture-pane -pt autopub-monitor:0.2 -S -100 | tail -n 100
curl -fsS http://127.0.0.1:18787/api/videos \
  | jq '.videos[:20] | map({id,title,created_at,file_path})'
```

Do not recopy repeatedly. If import fails, inspect logs first.

## Wrong-Video Prevention

For generated videos, require at least two checks before upload or publish:

```bash
ffprobe -v error -show_entries format=duration,size -of json /path/to/video.mp4
sha256sum /path/to/video.mp4
```

If the source is from LALACHAN/Xiaoyunque:

- prefer the stable path under `/home/lachlan/ProjectsLFS/LALACHAN/Videos/`;
- compare against the latest `/home/lachlan/Downloads/final_video*.mp4` if the user mentioned a fresh download;
- use CLI safeguards when known:

```bash
python scripts/lazyedit_publish.py \
  --video /path/to/video.mp4 \
  --expect-sha256 SHA256 \
  --expect-duration 15.125 \
  --duration-tolerance 1.0 \
  --expect-min-size-mb 5 \
  --use-current-settings \
  --no-publish \
  --wait
```

Only use `--allow-stale-lalachan-copy` if the user explicitly accepts the older copy.

## Context Collection

Context can come from:

- user-provided background;
- a LALACHAN/RARACHAN prompt or story Markdown;
- an existing transcript;
- section notes or metadata from another repo;
- a product/project URL or repository name;
- web search for song titles, quotes, public names, product names, or other facts that are likely to be wrong from ASR alone.

When context is external and could change, verify it before using it. For example, if a street singer appears to sing a recognizable song, search the lyrics/title and use that as ASR context rather than guessing.

## Subtitle Correction Philosophy

Use context to fix ASR errors like a careful human editor.

Do:

- treat scripts/prompts as reference, not a verbatim transcript;
- read neighboring lines before editing;
- fix names, objects, places, song lyrics, product names, technical terms, and broken phrases;
- infer the most likely wording when the ASR is abnormal, sentence fragments are strange, or words contradict the visible context;
- preserve timing as much as possible;
- keep natural speech style;
- keep the correction moderate: not aggressive, not overly conservative.

Do not:

- invent unsupported dialogue;
- force generated-video subtitles to match the script if the actual audio differs;
- rewrite every sentence stylistically;
- change meaning just to make it prettier;
- turn metadata into a full script dump.

For multilingual subtitles:

- use `--correction-source polished` for repeated correction passes unless starting from raw original is explicitly requested;
- the saved polished subtitle version is shared for the video and should be reused by later runs;
- inspect `DATA/VIDEO_FOLDER/*_mixed_polished.md` when the content is important.

Manual inspection:

```bash
sed -n '1,220p' DATA/VIDEO_FOLDER/*_mixed_polished.md
rg -n "bad term|wrong name|ASR artifact" DATA/VIDEO_FOLDER/*_mixed_polished.*
```

## Correction Prompt Template

Use this as a wrapper when the raw script/background needs guardrails. Save it in `temp/` and pass it as `--correction-prompt-file`.

```markdown
# Subtitle Correction Context

You are correcting ASR subtitles for a short video. Preserve timestamps and line structure as much as possible.

Use the context below as background, not as a verbatim transcript. Correct clear recognition errors, broken phrases, wrong names, wrong objects, wrong song lyrics, wrong product/project names, and context-inconsistent fragments.

Use a human middle path: do not over-edit, but do not stay too conservative when the transcription is obviously abnormal. Read neighboring lines and infer the most likely intended wording. Keep natural speech. Do not invent unsupported content.

Important terms:

- TERM 1
- TERM 2

User/video context:

PASTE USER BACKGROUND HERE

Reference script/story/prompt:

PASTE SCRIPT OR LINKED MARKDOWN CONTENT HERE
```

## Metadata Prompt Template

Do not pass a long full script as metadata context unless there is no alternative. Metadata should be concise and viewer-facing.

Save a short metadata brief in `temp/` and pass it as `--metadata-prompt-file`.

```markdown
# Metadata Brief

Create platform metadata for this video. Use Traditional Chinese for Chinese metadata. English metadata may be generated separately for YouTube/Instagram.

Do not reveal every scene beat. Do not copy the full script. Write an appealing title and description based on the story, tone, and visible content.

Hook:

- ONE-SENTENCE HOOK

Characters / setting:

- WHO AND WHERE

Core idea:

- CENTRAL CONFLICT, JOKE, DEMO, OR EMOTION

Important terms:

- NAMES, PROJECTS, PLACES, PRODUCTS

Tone:

- quiet / funny / reflective / experimental / technical / family-life / etc.

Keywords and hashtags:

- 8 to 15 relevant terms
```

If Chinese metadata appears mostly English, rerun metadata generation or process with a clearer metadata brief before publishing.

## Common CLI Workflows

### Correct And Process, But Do Not Publish

Use this when you want to inspect subtitles and package quality first:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --correction-prompt-file temp/correction_context.md \
  --metadata-prompt-file temp/metadata_brief.md \
  --correct-subtitles \
  --correction-source polished \
  --no-publish \
  --guided-monitor \
  --wait \
  --poll-seconds 10 \
  --process-timeout 7200
```

### Process And Publish To All Main Platforms

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --correction-prompt-file temp/correction_context.md \
  --metadata-prompt-file temp/metadata_brief.md \
  --correct-subtitles \
  --correction-source polished \
  --platforms shipinhao,youtube,instagram \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -160 | tail -n 160'" \
  --wait \
  --poll-seconds 10 \
  --process-timeout 7200 \
  --publish-timeout 7200
```

### Publish Existing Finished Output

Use when no rerun is desired:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms shipinhao,youtube,instagram \
  --no-process \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -160 | tail -n 160'" \
  --wait \
  --poll-seconds 10 \
  --publish-timeout 7200
```

### YouTube And Instagram Only

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms youtube,instagram \
  --wait \
  --poll-seconds 10
```

### Shipinhao Only

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms shipinhao \
  --no-process \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -160 | tail -n 160'" \
  --wait \
  --poll-seconds 10 \
  --publish-timeout 7200
```

### Override Subtitle Order Without Changing Studio Defaults

`--languages` is bottom-to-top:

```bash
python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --languages zh-Hant,ja,en \
  --platforms youtube,instagram \
  --wait
```

Examples:

- `zh-Hant,ja,en`: Chinese bottom, Japanese above, English above.
- `fr,zh-Hant,ja,en`: French bottom, Chinese above, Japanese above, English above.

## Low-Level API Outline

The CLI wraps these endpoints. Prefer the CLI, but agents can use the API directly.

Upload:

```bash
curl -X PUT \
  --data-binary "@/path/to/video.mp4" \
  "http://127.0.0.1:18787/upload-stream?filename=video.mp4&title=video&source=api"
```

AI subtitle correction:

```bash
curl -X POST "http://127.0.0.1:18787/api/videos/VIDEO_ID/subtitle-correction" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "ai",
    "prompt": "Use supplied context to fix ASR errors. Preserve timing.",
    "sourceVariant": "polished",
    "use_cache": true
  }'
```

Process:

```bash
curl -X POST "http://127.0.0.1:18787/api/videos/VIDEO_ID/process" \
  -H "Content-Type: application/json" \
  -d '{
    "async": true,
    "steps": ["keyframes", "caption", "transcribe", "polish", "translate", "burn", "metadata_zh", "metadata_en", "cover"],
    "translationLanguages": ["zh-Hant", "ja", "en"],
    "usePolishedSubtitles": true,
    "burnSubtitles": true,
    "metadataPrompt": "short metadata brief",
    "notes": "subtitle correction context",
    "persistSettings": false
  }'
```

Poll process:

```bash
curl "http://127.0.0.1:18787/api/videos/VIDEO_ID/process-status?publicationSessionId=SESSION_ID"
```

Publish:

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
      "publicationMode": "override",
      "persistSettings": false
    }
  }'
```

Local queue:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue | jq .
```

Remote queue:

```bash
curl -fsS http://lazyingart:8081/publish/queue | jq .
```

## Monitoring

Local LazyEdit queue:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue \
  | jq '.jobs[:10] | map({id,video_id,status,platforms,remote_status,remote_job_id,error,updated_at})'
```

Remote AutoPublish queue:

```bash
curl -fsS http://lazyingart:8081/publish/queue \
  | jq '.jobs[-10:] | map({id,status,platforms,filename,error,updated_at})'
```

Remote browser automation log:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -160 | tail -n 160'
```

AutoPubMonitor import logs:

```bash
tmux capture-pane -pt autopub-monitor:0.1 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.2 -S -120 | tail -n 120
tmux capture-pane -pt autopub-monitor:0.3 -S -120 | tail -n 120
```

## Shipinhao Notes

Shipinhao runs in Chromium on the Pi:

- port: `5006`
- profile: `/home/lachlan/chromium_dev_session_5006`

The terminal helper and code path should now share the same browser/profile:

```bash
ssh lachlan@lazyingart \
  'bash -lc "source ~/scripts/sourced_chromium_aliases.sh; start_chromium_shipinhao"'
```

Expected if already open:

```text
Reusing existing Chromium session for shipinhao on port 5006 (/home/lachlan/chromium_dev_session_5006).
```

Useful success log lines:

```text
Reusing existing shipinhao Chromium session on port 5006.
Already logged in.
Shipinhao description set (... chars).
Shipinhao short title set to: '...'
Shipinhao save draft result: ...
Shipinhao publish button ready: ...
Successfully published on ShiPinHao.
```

If the description appears in the editor but not in the published post, inspect `AutoPublish/pub_shipinhao.py` and make sure the description path still types into `.input-editor[contenteditable]` with Selenium, instead of only setting `textContent` or `innerHTML`.

## Common Failure Handling

### Instagram Error After Queue Says Done

If Instagram shows a publish error popup while LazyEdit or AutoPublish says
`done`, check the actual MP4 extracted by AutoPublish. A known 2026-06-25
failure occurred because the remote ZIP contained an HEVC/H.265 `hvc1` MP4.
Instagram accepted the upload step but failed during processing/posting.

Required repair:

1. Rebuild the LazyEdit publish bundle.
2. Verify the local ZIP contains H.264/AVC `avc1`, `yuv420p`, and AAC when audio
   exists.
3. Resubmit only Instagram, not platforms that already succeeded.
4. Verify the remote extracted MP4 codec.
5. Inspect live Instagram browser evidence; `Your reel has been shared.` is
   success.

Detailed incident note:

```text
references/INSTAGRAM_BROWSER_SAFE_PUBLISH_BUNDLE_BUG_2026_06_25.md
```

### AutoPublish Service Not Reachable

Check:

```bash
curl -fsS http://lazyingart:8081/publish/queue | jq .
ssh lachlan@lazyingart 'ps -eo pid,cmd | rg "python app.py --refresh-time" || true'
```

If the service was just restarted, LazyEdit may cache a negative reachability result for about 30 seconds. Wait and retry after the queue endpoint responds.

### Shipinhao QR Login

The long QR wait is intentional. Do not shorten it. The user may scan later after doing other work.

Check:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -180 | tail -n 180'
```

### Cover Generation Wait

Shipinhao can keep publish disabled while cover generation is running. Wait for cover readiness and draft save before publish. Do not click publish early.

### Metadata Too Script-Like

If metadata reads like a storyboard or dumps all dialogue, regenerate with a shorter metadata brief. Keep metadata viewer-facing.

### No Subtitles On Silent Generated Video

If a generated video is silent or nearly silent, transcription can be empty and burn may be skipped. This is acceptable if the user expects no spoken dialogue. Still complete metadata, cover extraction, and publish verification.

### Duplicate Publish Risk

If a first real publish exposed a packaging issue, do not keep republishing the same video unless explicitly asked. Use:

```bash
python scripts/lazyedit_publish.py --video-id VIDEO_ID --use-current-settings --no-publish --wait
```

Inspect final output and ZIP first, then publish once.

## Final Verification Checklist

Before telling the user "done", verify:

- correct source video path and title;
- subtitles corrected using the provided context;
- metadata is concise and not a script dump;
- logo setting is enabled and top-left unless user opted out;
- final processed MP4 exists;
- local LazyEdit job is `done`;
- remote AutoPublish job is `done`;
- queue is not stuck in `running`;
- platform set matches the user request.

Commands:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue \
  | jq '.jobs[:8] | map({id,video_id,status,platforms,remote_status,remote_job_id,error,updated_at})'

curl -fsS http://lazyingart:8081/publish/queue \
  | jq '.jobs[-8:] | map({id,status,platforms,filename,error,updated_at})'

ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -120 | tail -n 120'
```

## Copy-Paste Handoff Prompt

Use this when asking another Codex/agent to publish a video:

```text
You are publishing through LazyEdit.

Repo: /home/lachlan/DiskMech/Projects/lazyedit
API: http://127.0.0.1:18787
Remote AutoPublish: http://lazyingart:8081
Use conda env: lazyedit
Preferred tool: python scripts/lazyedit_publish.py

Video:
- PATH_OR_VIDEO_ID

Platforms:
- shipinhao,youtube,instagram OR requested subset

Context for subtitle correction:
- USER_BACKGROUND_OR_SCRIPT_PATH

Rules:
- Use polished/corrected subtitles.
- Use context as reference, not verbatim transcript.
- Correct clear ASR errors, names, products, song lyrics, objects, and broken phrases.
- Do not over-edit and do not invent unsupported content.
- Metadata should be concise and viewer-facing, not a script dump.
- Use current Studio settings unless explicitly overridden.
- Burn the configured LazyEdit logo at top-left unless user opts out.
- Verify local LazyEdit and remote AutoPublish queues before reporting done.
```
