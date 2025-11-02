# LazyEdit – Quick Start (Backend + Frontend)

This is a minimal, copy‑paste guide to run the Tornado backend and the Expo (PWA/Android/iOS) app locally.

## Prerequisites
- Conda env: `lazyedit` (Python 3.10+). Use `python` from the env, not `python3`.
- FFmpeg installed and on PATH.
- Node.js 20+ and npm (Expo tooling).
- Postgres locally (peer auth okay) or a DSN for a remote instance.

## 1) Backend (Tornado + Postgres)
- Activate env and install system deps (optional):
  ```bash
  source ~/miniconda3/etc/profile.d/conda.sh
  conda activate lazyedit
  ```
- Database (local peer):
  ```bash
  createdb lazyedit_db || true
  # optional: verify
  psql -d lazyedit_db -tAc "SELECT 'ok'"
  ```
  Or set a DSN:
  ```bash
  export LAZYEDIT_DATABASE_URL='postgresql://lachlan:the11thfzpe.g.@localhost:5432/lazyedit_db'
  ```
- Run the server (default port 8081):
  ```bash
  python app.py
  ```
- Key endpoints:
  - `POST /upload` – upload video (multipart `video` field)
  - `POST /video-processing` – end‑to‑end processing
  - `GET /api/languages` – supported languages
  - `GET /api/videos` – list videos

Quick DB check (optional):
```bash
python db_smoke_test.py
```

## 2) Frontend (Expo: PWA, Android, iOS)
From `app/` directory:
```bash
cd app
npm install  # first time only
```

- Web (PWA) on a non‑conflicting port (Metro uses 8081 by default):
  ```bash
  EXPO_PUBLIC_API_URL="http://localhost:8081" npx expo start --web --port 8091
  ```
- Android emulator:
  ```bash
  # If using Android emulator on the same host, backend is at 10.0.2.2
  EXPO_PUBLIC_API_URL="http://10.0.2.2:8081" npx expo start --android
  ```
- iOS simulator (run on macOS):
  ```bash
  EXPO_PUBLIC_API_URL="http://127.0.0.1:8081" npx expo start --ios
  ```

Home tab lets you pick a video and upload to the backend. Library tab lists videos from the database.

## Notes
- CORS is open on the backend for app development.
- Do not modify symlinked directories `furigana` or `echomind` in this repo; they are read‑only.
- If port 8081 is busy, keep backend on 8081 and move Expo web to `--port 8091`.
