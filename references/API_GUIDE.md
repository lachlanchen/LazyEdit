# LazyEdit API Guide

This guide documents the core HTTP endpoints used by LazyEdit and shows
end-to-end examples (upload -> process -> cover -> publish).

Base URL
Use the LazyEdit backend base URL. By default it is:

http://localhost:8787

All examples below assume the base URL above. If you deploy elsewhere,
replace the host/port.

---

Quick Start (Upload -> Process)

1) Upload a video

POST /upload
multipart/form-data fields:
- video (file, required)
- title (string, optional)
- filename (string, optional)
- source (string, optional: upload, generate, remix, api)

Example:

curl -F "video=@/home/lachlan/Nutstore Files/AutoPublish/AutoPublish/IMG_5503_2025_12_26_16_20_29_COMPLETED.MOV" \
     -F "title=IMG_5503_2025_12_26_16_20_29_COMPLETED" \
     -F "filename=IMG_5503_2025_12_26_16_20_29_COMPLETED.MOV" \
     -F "source=api" \
     http://localhost:8787/upload

Response (example):
{
  "status": "success",
  "message": "File IMG_5503_... uploaded successfully.",
  "file_path": "/abs/path/to/DATA/IMG_5503.../IMG_5503....MOV",
  "media_url": "/media/IMG_5503.../IMG_5503....MOV",
  "video_id": 123
}

2) Process a video

POST /video-processing
form fields:
- file_path (string, required)
- use_translation_cache (true/false, optional)
- use_metadata_cache (true/false, optional)

Example:

curl -X POST \
  -d "file_path=/abs/path/to/DATA/IMG_5503.../IMG_5503....MOV" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing

Response:
- Binary ZIP of the processed outputs.

---

Upload via streaming (large files)

PUT /upload-stream
query params:
- filename (string, required)
- title (string, optional)
- source (string, optional: upload, generate, remix, api)

Example:

curl -X PUT \
  --data-binary "@/path/to/video.mp4" \
  "http://localhost:8787/upload-stream?filename=video.mp4&title=video&source=api"

---

List videos

GET /api/videos

Response (example):
{
  "videos": [
    {
      "id": 123,
      "file_path": "/abs/path/to/DATA/...",
      "media_url": "/media/...",
      "preview_media_url": "/media/...",
      "title": "Example",
      "created_at": "2025-01-10T12:34:56.789Z",
      "source": "api"
    }
  ]
}

Video detail

GET /api/videos/{id}

---

Extract cover

POST /api/videos/{id}/cover
JSON body (optional):
{
  "lang": "zh"
}

Example:

curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"lang\":\"zh\"}" \
  http://localhost:8787/api/videos/123/cover

Response (example):
{
  "status": "completed",
  "cover_path": "/abs/path/to/publish/IMG_..._cover.jpg",
  "cover_url": "/media/..."
}

---

Publish package (AutoPublish integration)

POST /api/videos/{id}/publish
JSON body:
- platforms: object or list of platforms
- test (boolean, optional)
- wait (boolean, optional)

Example:

curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"platforms\":{\"xiaohongshu\":true,\"douyin\":true}}" \
  http://localhost:8787/api/videos/123/publish

Response (example):
{
  "status": "queued",
  "zip_url": "/media/...",
  "platforms": {
    "xiaohongshu": true,
    "douyin": true
  }
}

---

Other useful endpoints (summary)

- GET /api/languages
  Returns supported subtitle languages.

- POST /api/videos/{id}/transcribe
  Run ASR transcription.

- POST /api/videos/{id}/caption
  Run visual captioning.

- POST /api/videos/{id}/metadata
  Generate metadata (requires transcripts/captions).

- POST /api/videos/{id}/translate
  Translate subtitles.

- POST /api/videos/{id}/burn-subtitles
  Burn subtitles into the video.

- POST /api/videos/{id}/process
  Run the app pipeline (app-side orchestrated).

- POST /api/videos/generate
  Generate a video from a prompt (Sora).

---

Notes

- media_url and cover_url are relative paths (prefixed with /media). To fetch
  them from a client, prefix with the base URL.
- Use source=api when uploading from external services so the Home API tab
  shows the latest API-sourced clip.
