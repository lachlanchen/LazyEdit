# Musia Publish Failures: Animal の 第六感

Date: 2026-07-04

## Context

Musia recording:

```text
/home/lachlan/ProjectsLFS/Musia/recorded_videos/animal-no-di-liu-gan/animal-no-di-liu-gan-mixed-lyrics-guitar-portrait-4k.mp4
```

Clean song-only publish package:

```text
/home/lachlan/DiskMech/Projects/lazyedit/DATA/animal-no-di-liu-gan-clean-metadata/publications/song_only_metadata/publish/animal-no-di-liu-gan-clean-metadata.zip
```

Important metadata requirement:

```text
Title: Animal の 第六感
Metadata should describe the song itself only.
Do not include Musia implementation notes, player implementation notes, publication workflow notes, or conversation context.
```

## Jobs

```text
Shipinhao: job-1783138924417-1
Douyin:    job-1783139093254-2
YouTube:   job-1783139588635-3
```

## Shipinhao

The earlier Shipinhao run failed after clicking publish because management-page
verification did not find the post quickly enough. AutoPublish then retried the
whole publish flow, risking duplicate posts.

Workaround used for the successful run:

```bash
AUTOPUB_VERIFY_PUBLISH=0 AUTOPUB_SHIPINHAO_SAVE_DRAFT=0
```

Result:

```text
Successfully published on ShiPinHao.
```

Fix requested:

```text
1. Do not retry a full Shipinhao upload after the publish click if only the
   management-page verification failed.
2. Treat that case as pending verification, or verify against draft/audit/pending
   tabs before retrying.
3. Save a screenshot and HTML snapshot, but do not upload a duplicate.
4. If the requested collection is unavailable, fall back cleanly to a configured
   visible collection such as 懒人艺术.
```

## Douyin

Douyin failed before submission. The remote log shows repeated failure to find
the upload file input on the creator upload page:

```text
Douyin publish failed: Maximum retry attempts reached. Douyin process failed.
selenium.common.exceptions.TimeoutException
File: /home/lachlan/Projects/autopub/pub_douyin.py
Function: _upload_video_file
Failure: could not find upload <input type=file>
Page: https://creator.douyin.com/creator-micro/content/upload
```

Fix requested:

```text
1. Update Douyin upload selectors for the current Creator UI.
2. Add a pre-upload debug snapshot when file input is not found.
3. Detect and close blocking overlays, stale draft prompts, and upload-area
   wrappers before looking for the file input.
4. Prefer a robust JS query over narrow XPath:
   document.querySelectorAll('input[type=file]')
5. If no file input exists, click the visible upload/drop area first, then retry.
6. Avoid recursive full-process retries when the file input is missing; fail once
   with a useful screenshot and DOM excerpt.
```

Implemented:

```text
AutoPublish/pub_douyin.py now probes document.querySelectorAll('input[type=file]'),
clicks visible upload/drop-area entry points when the input is lazy-rendered,
temporarily makes hidden file inputs interactable if Selenium rejects send_keys,
and saves JSON/PNG/HTML snapshots under temp_screenshot/ when no upload input is
available. Missing upload input is now a specific exception and no longer causes
recursive full-process retry loops.
```

## YouTube

The YouTube publisher logged success in an earlier run, but the user saw the
video in YouTube drafts. This means clicking the final button is not enough
evidence of publication.

Fix requested:

```text
1. After clicking the final YouTube button, verify the video in YouTube Studio
   content management.
2. If the video is still in Drafts, open that draft by title and set visibility
   to Public.
3. Return the actual YouTube video URL or ID, not the upload page URL.
4. Do not report success from set_visibility_and_publish() until the management
   page confirms published/public state.
```

## Metadata

The previous package used process/tooling-oriented metadata. That is not
acceptable for public posts.

Fix requested:

```text
1. Default metadata for Musia recordings must be song-facing.
2. Metadata can mention Musia as artist/creator.
3. Metadata must not mention internal pipeline details, recording modes,
   publication masters, no-subtitle settings, or implementation notes unless the
   user explicitly asks for a technical demo post.
4. Platform descriptions should focus on song title, mood, theme, language mix,
   and artist.
```
