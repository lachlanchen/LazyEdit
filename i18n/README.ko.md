[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lazyingart/raw/main/figs/banner.png)](https://github.com/lachlanchen/lazyingart/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>생성, 자막 처리, 메타데이터 생성, 선택적 게시까지를 지원하는 AI 보조형 비디오 워크플로</b>
  <br />
  <sub>Upload or generate -> transcribe -> translate/polish -> burn subtitles -> caption/keyframes -> metadata -> publish</sub>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0" /></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Backend-Tornado-222222" alt="Backend: Tornado" />
  <img src="https://img.shields.io/badge/Frontend-Expo-000020?logo=expo&logoColor=white" alt="Frontend: Expo" />
  <img src="https://img.shields.io/badge/Platform-Linux-informational?logo=linux&logoColor=white" alt="Platform: Linux" />
  <img src="https://img.shields.io/badge/FFmpeg-required-0A0A0A?logo=ffmpeg&logoColor=white" alt="FFmpeg required" />
  <img src="https://img.shields.io/badge/PostgreSQL-supported-336791?logo=postgresql&logoColor=white" alt="PostgreSQL supported" />
  <img src="https://img.shields.io/badge/Stage_A%2FB%2FC-enabled-0f766e" alt="Stage A/B/C enabled" />
  <img src="https://img.shields.io/badge/AutoPublish-optional-orange" alt="AutoPublish optional" />
  <img src="https://img.shields.io/badge/i18n-11%20languages-1f883d" alt="i18n: 11 languages" />
  <a href="https://github.com/lachlanchen/LazyEdit/commits/main"><img src="https://img.shields.io/github/last-commit/lachlanchen/LazyEdit?color=0ea5e9" alt="Last commit" /></a>
  <a href="https://github.com/lachlanchen/LazyEdit/graphs/contributors"><img src="https://img.shields.io/github/contributors/lachlanchen/LazyEdit?color=8a4fff" alt="Contributors" /></a>
</p>

## 📌 Quick Facts

LazyEdit는 생성, 처리, 선택적 게시까지를 포괄하는 엔드투엔드 AI 보조형 비디오 워크플로입니다. 프롬프트 기반 생성(Stage A/B/C), 미디어 처리 API, 자막 렌더링, 키프레임 캡션 생성, 메타데이터 생성, AutoPublish 연동이 하나의 흐름으로 통합되어 있습니다.

| Quick fact | Value |
| --- | --- |
| 📘 Canonical README | `README.md` (this file) |
| 🌐 Language variants | `i18n/README.*.md` (각 README 상단 언어 바는 한 줄만 유지) |
| 🧠 Backend entrypoint | `app.py` (Tornado) |
| 🖥️ Frontend app | `app/` (Expo web/mobile) |
| 🧩 Runtime styles | `python app.py` (수동), `./start_lazyedit.sh` (tmux), optional `lazyedit.service` |
| 🎯 Primary references | `README.md`, `references/QUICKSTART.md`, `references/API_GUIDE.md`, `references/APP_GUIDE.md` |

## 🧭 Contents

- [Overview](#overview)
- [Quick Facts](#-quick-facts)
- [At a Glance](#at-a-glance)
- [Architecture Snapshot](#architecture-snapshot)
- [Demos](#demos)
- [Features](#features)
- [Documentation & i18n](#-documentation--i18n)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Cheat Sheet](#-command-cheat-sheet)
- [Usage](#usage)
- [Configuration](#configuration)
- [Configuration Files](#-configuration-files)
- [API Examples](#api-examples)
- [Examples](#examples)
- [Development Notes](#development-notes)
- [Testing](#testing)
- [Assumptions & Known Limits](#-assumptions--known-limits)
- [Deployment & Sync Notes](#deployment--sync-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Support](#-support)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## ✨ Overview

LazyEdit은 Tornado 백엔드(`app.py`)와 Expo 프런트엔드(`app/`)를 중심으로 설계되어 있습니다.

> 참고: 머신/저장소/런타임 세부값이 기기마다 다를 수 있습니다. 기존 기본값은 제거하지 말고, 환경 변수로 오버라이드하세요.

| Why teams use it | Practical result |
| --- | --- |
| 통합 운영 흐름 | 업로드/생성/리믹스/게시를 한 번의 워크플로로 처리 |
| API 우선 설계 | 스크립팅/자동화가 쉬우며 다른 도구와 연동이 용이 |
| 로컬 우선 운영 | tmux + service 방식 배포에 맞춰 동작 |

| Step | What happens |
| --- | --- |
| 1 | 동영상 업로드 또는 생성 |
| 2 | 전사 후 자막 번역(필요 시) |
| 3 | 다국어 자막 번인 및 레이아웃 제어 |
| 4 | 키프레임, 캡션, 메타데이터 생성 |
| 5 | 패키징 후 AutoPublish로 선택적 게시 |

### Pipeline focus

- 하나의 운영자 UI에서 업로드, 생성, 리믹스, 라이브러리 관리를 처리합니다.
- 전사, 자막 정제/번역, 번인, 메타데이터 생성까지 API-first 방식으로 흐름을 구성합니다.
- `agi/` 내 Veo / Venice / A2E / Sora 헬퍼를 통한 선택적 생성 제공자 통합이 가능합니다.
- AutoPublish를 통한 선택적 배포 연동이 가능합니다.

## 🎯 At a Glance

| Area | Included in LazyEdit | Status |
| --- | --- | --- |
| Core app | Tornado API backend + Expo web/mobile frontend | ✅ |
| Media pipeline | ASR, subtitle translation/polish, burn-in, keyframes, captions, metadata | ✅ |
| Generation | Stage A/B/C and provider helper routes (`agi/`) | ✅ |
| Distribution | Optional AutoPublish handoff | 🟡 Optional |
| Runtime model | Local-first scripts, tmux workflows, optional systemd service | ✅ |

## 🏗️ Architecture Snapshot

이 저장소는 UI 계층을 갖춘 API-first 미디어 파이프라인으로 구성됩니다.

- `app.py`는 업로드, 처리, 생성, 게시 핸드오프, 미디어 제공을 담당하는 Tornado 진입점입니다.
- `lazyedit/`에는 모듈형 파이프라인 블록(DB 영속화, 번역, 자막 번인, 캡션, 메타데이터, provider adapter)이 포함됩니다.
- `app/`는 업로드, 처리, 미리보기, 게시 흐름을 제공하는 Expo Router 앱(web/mobile)입니다.
- `config.py`는 환경 로딩과 기본/대체 런타임 경로를 중앙에서 해석합니다.
- `start_lazyedit.sh`와 `lazyedit_config.sh`는 tmux 기반의 로컬/배포 실행 모드를 재현 가능한 방식으로 제공합니다.

| Layer | Main paths | Responsibility |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | 엔드포인트, 라우팅, 환경 변수 해석 |
| Processing core | `lazyedit/`, `agi/` | 자막/캡션/메타데이터 파이프라인 + provider |
| UI | `app/` | 운영자용 UX(Expo 기반 web/mobile) |
| Runtime scripts | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 로컬/서비스 시작 및 운영 |

High-level flow:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

아래 화면은 인제스트부터 메타데이터 생성까지의 핵심 운영 경로를 보여줍니다.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Home · Upload</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Home · Generate</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Home · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Library</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Video overview</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Translation preview</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Burn slots</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Burn layout</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Keyframes + captions</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Metadata generator</sub>
    </td>
  </tr>
</table>

## 🧩 Features

- ✨ Stage A/B/C를 활용한 프롬프트 기반 생성 워크플로(프롬프트 기반 생성을 Sora/Veo 통합 경로로 실행).
- 🧵 전사 -> 자막 정제/번역 -> 번인 -> 키프레임 -> 캡션 -> 메타데이터로 이어지는 전체 파이프라인.
- 🌏 furigana/IPA/romaji 연계 경로를 포함한 다국어 자막 구성.
- 🔌 업로드, 처리, 미디어 제공, 게시 큐 엔드포인트를 제공하는 API-first 백엔드.
- 🚚 소셜 플랫폼 전환을 위한 선택적 AutoPublish 통합.
- 🖥️ tmux 실행 스크립트를 통한 backend + Expo 통합 워크플로 지원.

## 🌍 Documentation & i18n


- 표준 소스: `README.md`
- 언어 변형: `i18n/README.*.md`
- 언어 탐색 링크: 각 README 상단에 언어 바를 한 줄만 유지(중복 없음)
- 현재 저장소 지원 언어: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

영문 README와 번역본이 불일치할 경우 `README.md`를 신뢰 가능한 원문으로 두고 언어별 파일을 하나씩 업데이트합니다.

| i18n policy | Rule |
| --- | --- |
| Canonical source | `README.md`를 원본으로 유지 |
| Language bar | Exactly one language-options line at top |

## 🗂️ Project Structure

```text
LazyEdit/
├── app.py                           # Tornado backend entrypoint and API orchestration
├── app/                             # Expo frontend (web/mobile)
├── lazyedit/                        # Core pipeline modules (translation, metadata, burner, DB, templates)
├── agi/                             # Generation provider abstraction (Sora/Veo/A2E/Venice routes)
├── DATA/                            # Runtime media input/output (symlink in this workspace)
├── translation_logs/                # Translation logs
├── temp/                            # Temporary runtime files
├── install_lazyedit.sh              # systemd installer (expects config/start/stop scripts)
├── start_lazyedit.sh                # tmux launcher for backend + Expo
├── stop_lazyedit.sh                 # tmux stop helper
├── lazyedit_config.sh               # Deployment/runtime shell config
├── config.py                        # Environment/config resolution (ports, paths, autopublish URL)
├── .env.example                     # Environment override template
├── references/                      # Additional docs (API guide, quickstart, deployment notes)
├── AutoPublish/                     # Submodule (optional publishing pipeline)
├── AutoPubMonitor/                  # Submodule (monitor/sync automation)
├── whisper_with_lang_detect/        # Submodule (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule (primary captioner)
├── clip-gpt-captioning/             # Submodule (fallback captioner)
└── furigana/                        # External dependency in workflow (tracked submodule in this checkout)
```

Submodule/external dependency note:
- Git submodules in this repository include `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, and `furigana`.
- Operational guidance treats `furigana` and `echomind` as external/read-only dependencies in this workflow. If uncertain, preserve upstream and avoid editing in place.

## ✅ Prerequisites

| Dependency | Notes |
| --- | --- |
| Linux environment | `systemd`/`tmux` scripts are Linux-oriented |
| Python 3.10+ | Use Conda env `lazyedit` |
| Node.js 20+ + npm | Required for Expo app in `app/` |
| FFmpeg | Must be available on `PATH` |
| PostgreSQL | Local peer auth or DSN-based connection |
| Git submodules | Required for key pipelines |

## 🚀 Installation

1. Clone and initialize submodules:

```bash

git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Activate Conda environment:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Optional system-level install (service mode):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Service install notes:
- `install_lazyedit.sh` installs `ffmpeg` and `tmux`, then creates `lazyedit.service`.
- It does not generate `lazyedit_config.sh`, `start_lazyedit.sh`, or `stop_lazyedit.sh`; these files must already exist and be correct.

## ⚡ Quick Start

Backend + frontend local run (minimal path):

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

In a second shell:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Optional local database bootstrap:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| 로컬 개발(수동) | `python app.py` + Expo command | `8787` | `8091` (example command) |
| Tmux 오케스트레이션 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd service | `sudo systemctl start lazyedit.service` | Config/env-driven | N/A |

## 🧭 Command Cheat Sheet

| Task | Command |
| --- | --- |
| Initialize submodules | `git submodule update --init --recursive` |
| Start backend only | `python app.py` |
| Start backend + Expo (tmux) | `./start_lazyedit.sh` |
| Stop tmux run | `./stop_lazyedit.sh` |
| Open tmux session | `tmux attach -t lazyedit` |
| Service status | `sudo systemctl status lazyedit.service` |
| Service logs | `sudo journalctl -u lazyedit.service` |
| DB smoke test | `python db_smoke_test.py` |
| Pytest smoke test | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### Development: backend only

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Alternate entry used in current deployment scripts:

```bash
python app.py -m lazyedit
```

Backend default URL: `http://localhost:8787` (from `config.py`, override with `PORT` or `LAZYEDIT_PORT`).

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Default `start_lazyedit.sh` ports:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Attach to session:

```bash
tmux attach -t lazyedit
```

Stop session:

```bash
./stop_lazyedit.sh
```

### Service management

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and update paths/secrets:

```bash
cp .env.example .env
```

Configuration precedence note:

- `config.py` loads `.env` values if present and only sets keys not already exported in the shell.
- Runtime values can therefore come from: shell-exported env vars -> `.env` -> code defaults.
- For tmux/service runs, `lazyedit_config.sh` controls startup/session parameters (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, ports via startup script env).

### Key variables

| Variable | Purpose | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Backend port | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Media root directory | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Local DB fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish endpoint | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish request timeout (seconds) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD script path | Environment-dependent |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR model names | `large-v3` / `large-v2` (example) |
| `LAZYEDIT_CAPTION_PYTHON` | Python runtime for caption pipeline | Environment-dependent |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Primary captioning path/script | Environment-dependent |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Fallback captioning path/script/cwd | Environment-dependent |
| `GRSAI_API_*` | Veo/GRSAI integration settings | Environment-dependent |
| `VENICE_*`, `A2E_*` | Venice/A2E integration settings | Environment-dependent |
| `OPENAI_API_KEY` | Required for OpenAI-backed features | None |

Machine-specific notes:
- `app.py` may set CUDA behavior (`CUDA_VISIBLE_DEVICES` usage in codebase context).
- Some paths in defaults are workstation-specific; use `.env` overrides for portable setups.
- `lazyedit_config.sh` controls tmux/session startup variables for deployment scripts.

## 🧾 Configuration Files

| File | Purpose |
| --- | --- |
| `.env.example` | Template for environment variables used by backend/services |
| `.env` | Machine-local overrides; loaded by `config.py`/`app.py` if present |
| `config.py` | Backend defaults and environment resolution |
| `lazyedit_config.sh` | tmux/service runtime profile (deploy path, conda env, app args, session name) |
| `start_lazyedit.sh` | Launches backend + Expo in tmux with selected ports |
| `install_lazyedit.sh` | Creates `lazyedit.service` and validates existing scripts/config |

Recommended update order for machine portability:
1. Copy `.env.example` to `.env`.
2. Set path- and API-related `LAZYEDIT_*` values in `.env`.
3. Adjust `lazyedit_config.sh` only for tmux/service deployment behavior.

## 🔌 API Examples

Base URL examples assume `http://localhost:8787`.

| API group | Representative endpoints |
| --- | --- |
| Upload and media | `/upload`, `/upload-stream`, `/media/*` |
| Video records | `/api/videos`, `/api/videos/{id}` |
| Processing | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publish | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generation | `/api/videos/generate` (+ provider routes in `app.py`) |

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

End-to-end process:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

List videos:

```bash
curl http://localhost:8787/api/videos
```

Publish package:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

More endpoints and payload details: `references/API_GUIDE.md`.

Related endpoint groups you will likely use:
- Video lifecycle: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Processing actions: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Generation/provider paths: `/api/videos/generate` plus provider routes exposed in `app.py`
- Distribution: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

If backend is on `8887`:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android emulator

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS simulator (macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### Optional Sora generation helper

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Supported seconds: `4`, `8`, `12`.
Supported sizes: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Development Notes

- Use `python` from Conda env `lazyedit` (do not assume system `python3`).
- Keep large media out of Git; store runtime media in `DATA/` or external storage.
- Initialize/update submodules whenever pipeline components fail to resolve.
- Keep edits scoped; avoid unrelated large-formatting changes.
- For frontend work, backend API URL is controlled by `EXPO_PUBLIC_API_URL`.
- CORS is open on the backend for app development.

Submodule and external dependency policy:
- Treat external dependencies as upstream-owned. In this repository workflow, avoid editing submodule internals unless intentionally working in those projects.
- Operational guidance in this repo treats `furigana` (and sometimes `echomind` in local setups) as external dependency paths; if uncertain, preserve upstream and avoid in-place edits.

Helpful references:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Security/config hygiene:
- Keep API keys and secrets in environment variables; do not commit credentials.
- Prefer `.env` for machine-local overrides and keep `.env.example` as the public template.
- If CUDA/GPU behavior differs by host, override via environment instead of hardcoding machine-specific values.

## ✅ Testing

Current formal test surface is minimal and DB-oriented.

| Validation layer | Command or method |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | Web UI + API run using short sample in `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

For functional validation, use the web UI and API flow with a short sample clip in `DATA/`.

Assumptions and portability notes:
- Some default paths in code are workstation-specific fallbacks; this is expected in current repo state.
- If a default path does not exist on your machine, set the corresponding `LAZYEDIT_*` variable in `.env`.
- If uncertain about a machine-specific value, preserve existing settings and add explicit overrides rather than deleting defaults.

## 🧱 Assumptions & Known Limits

- The backend dependency set is not pinned by a root lockfile; environment reproducibility currently depends on local setup discipline.
- `app.py` is intentionally monolithic in current repo state and contains a large route surface.
- Most pipeline validation is integration/manual (UI + API + sample media), with limited formal automated tests.
- Runtime directories (`DATA/`, `temp/`, `translation_logs/`) are operational outputs and can grow significantly.
- Submodules are required for full functionality; partial checkout often leads to missing-script errors.

## 🚢 Deployment & Sync Notes

Current known paths and sync flow (from repository operations docs):

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` on `lazyingart`

| Environment | Path | Notes |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Main source + submodules |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` in ops docs |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Monitor/sync/process sessions |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull after submodule updates |

After pushing `AutoPublish/` updates from this repo, pull on publishing host:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| Problem | Check / Fix |
| --- | --- |
| Missing pipeline modules or scripts | Run `git submodule update --init --recursive` |
| FFmpeg not found | Install FFmpeg and confirm `ffmpeg -version` works |
| Port conflicts | Backend defaults to `8787`; `start_lazyedit.sh` defaults to `18787`; set `LAZYEDIT_PORT` or `PORT` explicitly |
| Expo cannot reach backend | Ensure `EXPO_PUBLIC_API_URL` points to active backend host/port |
| Database connection issues | Verify PostgreSQL + DSN/env vars; optional smoke check: `python db_smoke_test.py` |
| GPU/CUDA issues | Confirm driver/CUDA compatibility with installed Torch stack |
| Service script fails at install | Ensure `lazyedit_config.sh`, `start_lazyedit.sh`, and `stop_lazyedit.sh` exist before running installer |

## 🗺️ Roadmap

- In-app subtitle/segment editing with A/B preview and per-line controls.
- Stronger end-to-end test coverage for core API flows.
- Documentation convergence across i18n README variants and deployment modes.
- Additional workflow hardening for generation-provider retries and status visibility.

## 🤝 Contributing

Contributions are welcome.

1. Fork and create a feature branch.
2. Keep commits focused and scoped.
3. Validate changes locally (`python app.py`, key API flow, and app integration if relevant).
4. Open a PR with purpose, reproduction steps, and before/after notes (screenshots for UI changes).

Practical guidelines:
- Follow Python style (PEP 8, 4 spaces, snake_case naming).
- Avoid committing credentials or large binaries.
- Update docs/config scripts when behavior changes.
- Preferred commit style: short, imperative, scoped (for example: `fix ffmpeg 7 compatibility`).



## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit builds on open-source libraries and services, including:
- FFmpeg for media processing
- Tornado for backend APIs
- MoviePy for editing workflows
- OpenAI models for AI-assisted pipeline tasks
- CJKWrap and multilingual text tooling in subtitle workflows
