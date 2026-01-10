# LazyEdit legacy processing pipeline (summary)

Source reviewed:
- `/home/lachlan/ProjectsLFS/lachlanchen/LazyEdit/app.py`
- `/home/lachlan/ProjectsLFS/lachlanchen/LazyEdit/lazyedit/autocut_processor.py`
- `/home/lachlan/ProjectsLFS/lachlanchen/LazyEdit/lazyedit/subtitle_translate.py`
- `/home/lachlan/ProjectsLFS/lachlanchen/LazyEdit/lazyedit/subtitle_metadata.py`
- `/home/lachlan/ProjectsLFS/lachlanchen/LazyEdit/lazyedit/video_captioner.py`

## Entry points (HTTP)
- `POST /upload`: saves a single video file to `DATA/<basename>/<filename>` and returns file path. (Stream variant: `PUT /upload-stream`.)
- `POST /video-processing`: runs the full processing pipeline and returns a zip file of outputs.
- `GET /api/languages`, `GET/POST /api/videos`, `GET/POST /api/videos/:id/captions`: lightweight APIs for the app.

## End-to-end pipeline (high level)
1. **Input validation + preprocessing**
   - Reads `file_path` from the request.
   - Runs `preprocess_if_needed()` (HandBrake wrapper) to normalize incompatible input.
   - Derives `base_name`, `output_folder`, and video resolution/length.
2. **Transcription (Autocut/Whisper)**
   - `AutocutProcessor.run_autocut('mixed', gpu_id)` runs an external VAD + Whisper script.
   - Produces `*_mixed.json` and `*_mixed.srt` in the output folder.
3. **Frame captioning**
   - `VideoCaptioner.run_captioning()` calls an external captioning script (two fallback commands).
   - Produces `*_caption.json` and `*_caption.srt`.
4. **Subtitle translation + layout**
   - `SubtitlesTranslator.process_subtitles()`:
     - splits subtitles into 1-minute batches,
     - translates into multiple languages via OpenAI structured outputs,
     - merges into `*_processed.json` and `*_processed.ass`.
5. **Burn subtitles**
   - `burn_subtitles()` overlays the ASS (or SRT) subtitles via ffmpeg.
   - Produces `*_subtitles.mp4`.
6. **Metadata generation**
   - `Subtitle2Metadata.generate_video_metadata()` calls OpenAI twice:
     - Chinese social platforms prompt (XiaoHongShu, Bilibili, Douyin).
     - English/YouTube prompt.
   - Output includes: title, descriptions, tags, teaser range, cover timestamp, and word list.
   - Saves `*_metadata.json`.
7. **Teaser + word card overlay**
   - Computes teaser range from metadata and subtitles.
   - Inserts teaser segment at start (`*_teasered.mp4`).
   - Requests a word card image from LazyingArt service and overlays it into the video.
   - Highlights remaining words (often a dummy no-op to avoid freezes).
   - Produces `*_highlighted.mp4`.
8. **Cover image**
   - Extracts a cover frame based on metadata timestamp (ffmpeg with OpenCV fallback).
   - Optionally overlays the word card on the cover.
   - Produces `*_cover.jpg` (and a plain cover temp file).
9. **Package outputs**
   - Zips: highlighted video, mixed JSON/SRT, cover image, metadata JSON.
   - Returns zip bytes as the HTTP response.

## Key outputs
- `*_mixed.json`, `*_mixed.srt`: transcription output (Whisper).
- `*_caption.json`, `*_caption.srt`: frame captioning output.
- `*_processed.json`, `*_processed.ass`: translated/merged subtitles.
- `*_subtitles.mp4`: subtitles burned in.
- `*_teasered.mp4`, `*_highlighted.mp4`: teaser + word card overlay results.
- `*_cover.jpg`, `*_cover_plain.jpg`: cover image.
- `*_metadata.json`: OpenAI-generated metadata.
- `*.zip`: bundled response from `/video-processing`.

## External dependencies (hard-coded paths)
- Whisper/VAD script: `/home/lachlan/Projects/whisper_with_lang_detect/vad_lang_subtitle.py`
- Captioning models: `/home/lachlan/Projects/vit-gpt2-image-captioning/vit_captioner_video.py`
- Fallback captioner: `/home/lachlan/Projects/image_captioning/clip-gpt-captioning/src/v2c.py`
- Word card service: `http://lazyingart:8082/get_words_card`

## Observations for refactor planning
- The pipeline is synchronous inside the request handler (can block IOLoop).
- Multiple external scripts are called via `subprocess` with hard-coded paths.
- "Autopublication" is metadata generation only; no platform API integration.
