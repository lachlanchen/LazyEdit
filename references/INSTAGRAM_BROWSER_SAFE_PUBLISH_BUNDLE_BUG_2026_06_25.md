# Instagram Browser-Safe Publish Bundle Bug

Date: 2026-06-25

## Summary

An Instagram publish for
`c05ffae4cac15cfb5f8abe6a8922c486_COMPLETED` appeared successful in the
LazyEdit/AutoPublish queues, but Instagram showed a publish error popup. The
remote AutoPublish extraction directory proved the failed package contained an
HEVC/H.265 video.

## Evidence

Failed remote extracted MP4:

```text
path: /home/lachlan/Projects/auto-publish/transcription_data/c05ffae4cac15cfb5f8abe6a8922c486_COMPLETED/c05ffae4cac15cfb5f8abe6a8922c486_COMPLETED_highlighted.mp4
codec_name: hevc
codec_tag_string: hvc1
pix_fmt: yuv420p
duration: 7.533333
size: 841449
```

Corrected LazyEdit publish bundle:

```text
path: DATA/c05ffae4cac15cfb5f8abe6a8922c486_COMPLETED/publish/c05ffae4cac15cfb5f8abe6a8922c486_COMPLETED_browser_upload.mp4
codec_name: h264
codec_tag_string: avc1
pix_fmt: yuv420p
duration: 7.534000
size: 2072411
```

Corrected Instagram-only publish:

```text
LazyEdit video_id: 409
LazyEdit job: 219
Remote AutoPublish job: job-1782391804462-4
Result: done
Live Instagram evidence: "Your reel has been shared."
```

## Root Cause

Browser-driven publishers should not receive HEVC/H.265, AV1, or other
browser-risk MP4s. Instagram can accept the file chooser/upload stage and fail
later during processing/posting. A queue `done` value is not enough when the
browser shows a platform error.

## Required LazyEdit Invariant

Every publish bundle sent to AutoPublish for browser-upload platforms must
contain a web-safe MP4:

- video codec: H.264/AVC (`h264`, tag `avc1`);
- pixel format: `yuv420p` or `yuvj420p`;
- audio codec: AAC when audio exists;
- container optimized for browser upload with `+faststart`.

If the selected source, mixed, subtitle-burned, or logo-burned output is HEVC,
H.265, AV1, or otherwise unsafe, LazyEdit must transcode during publish-bundle
preparation and write the transcoded file into the ZIP under the expected
`*_highlighted.mp4` archive name.

## Verification Commands

Probe the selected publish MP4:

```bash
ffprobe -v error \
  -select_streams v:0 \
  -show_entries stream=codec_name,codec_tag_string,pix_fmt,width,height \
  -show_entries format=duration,size \
  -of json /path/to/publish_video.mp4
```

Inspect the ZIP payload:

```bash
unzip -l DATA/VIDEO_FOLDER/publish/VIDEO_FOLDER.zip
```

Check local and remote queues:

```bash
curl -fsS http://127.0.0.1:18787/api/autopublish/queue \
  | jq '.jobs | map(select(.video_id==VIDEO_ID))'

curl -fsS http://lazyingart:8081/publish/queue \
  | jq '.jobs[-10:]'
```

If a platform popup conflicts with the queue state, inspect the live browser
state before reporting success.

## Repair Playbook

For a stale HEVC package already extracted on AutoPublish:

1. Rebuild the LazyEdit publish bundle.
2. Verify the local ZIP contains H.264/AVC `avc1`.
3. Resubmit only the failed platform.
4. Verify remote extracted MP4 codec.
5. Verify platform browser success text or public URL evidence.

Example:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit

python scripts/lazyedit_publish.py \
  --video-id VIDEO_ID \
  --use-current-settings \
  --platforms instagram \
  --no-process \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -160 | tail -n 160'" \
  --wait \
  --poll-seconds 10 \
  --publish-timeout 1800
```

Do not republish Shipinhao, YouTube, or other already successful platforms
unless the current user request explicitly asks for that.
