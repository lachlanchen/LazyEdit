# LazyEdit App Guide

This guide describes the target UX and pipeline for the new LazyEdit mobile/web app, with multilingual support and a plugin model for language-specific behavior.

## Platforms
- PWA (web), Android, and iOS via Expo Router (see `app/`).
- Bottom navigation fixed like WeChat, with a minimal white theme and subtle blue → flamingo gradient.

## Backend
- Tornado app (`app.py`) exposes JSON APIs for the app:
  - `GET /api/languages` – list supported language plugins.
  - `GET /api/videos` – recent videos from Postgres.
  - `POST /api/videos` – register a video (path + optional title).
  - `GET /api/videos/:id/captions` – list captions for a video.
  - `POST /api/videos/:id/captions` – add a caption row.
- Existing endpoints reused:
  - `POST /upload` – multipart upload of a video file.
  - `POST /video-processing` – end-to-end automatic processing.
- Database module: `lazyedit/db.py` (tables `videos`, `captions`).

## Language Plugins
- Registry in `lazyedit/plugins/languages.py` lists supported languages:
  - English (en), Chinese (zh), Cantonese (yue), Japanese (ja), Korean (ko), Arabic (ar), Vietnamese (vi), French (fr), Spanish (es).
- Prompts and JSON formats harvested from external `echomind` into Markdown per language under `docs/prompts/`. Symlinked repo is read-only by policy.

## User Flow
1. Select a video (Home tab): user picks or drops a video file, uploads to the backend.
2. Transcribe: backend extracts audio, transcribes source language.
3. Translate: backend produces translations; Japanese receives furigana via `furigana` dependency.
4. Compose subtitles: render strategy uses half-screen budget to select languages, font sizes, and line breaking.
5. Burn-in elegantly: generate subtitle overlays and export a clean, legible video.
6. Highlights: detect and extract key segments for teasers.
7. Extras: word cards, original + translation pairs, and diarization + voice conversion (e.g., GPT-SoVITS) for speaker-aware dubbing.
8. Deliver: final video packaged for download; metadata and assets zip archived.

## Manual Editing
- Future work: add an in-app subtitle/segment editor with A/B previews, language toggles, and per-line font sizing.

## Notes
- Do not modify symlinked dependencies (`furigana`, `echomind`) within this repo. They are read-only according to AGENTS.md.
- Keep large media out of Git (`DATA/` is the working dir; ignore big binaries).

