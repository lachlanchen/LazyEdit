[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lazyingart/raw/main/figs/banner.png)](https://github.com/lachlanchen/lazyingart/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>생성, 자막 처리, 메타데이터 생성, 선택적 게시까지를 아우르는 AI 보조형 비디오 워크플로</b>
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
</p>

## 📌 Quick Facts

LazyEdit은(는) 생성, 처리, 선택적 게시까지 포괄하는 엔드투엔드 AI 지원 비디오 워크플로입니다. 프롬프트 기반 생성(Stage A/B/C), 미디어 처리 API, 자막 렌더링, 키프레임 캡션 생성, 메타데이터 생성, AutoPublish 연동을 하나의 흐름으로 통합합니다.

| Quick fact | Value |
| --- | --- |
| 📘 표준 README | `README.md` (현재 파일) |
| 🌐 언어 변형 | `i18n/README.*.md` (각 README 상단에 언어 바를 한 줄만 유지) |
| 🧠 백엔드 진입점 | `app.py` (Tornado) |
| 🖥️ 프런트엔드 앱 | `app/` (Expo web/mobile) |

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

LazyEdit은 Tornado 백엔드(`app.py`)와 Expo 프런트엔드(`app/`)를 중심으로 설계되었습니다.

> 참고: 머신별로 저장소/런타임 세부값이 다를 수 있습니다. 기존 기본값은 그대로 두고, 필요한 경우 환경 변수로만 덮어쓰기하세요.

| 팀이 쓰는 이유 | 실제 효과 |
| --- | --- |
| 운영 흐름 통합 | 업로드/생성/리믹스/배포를 한 화면에서 처리 |
| API 우선 설계 | 자동화 스크립트화가 쉽고 타 도구 연동이 쉬움 |
| 로컬 우선 실행 | tmux + 서비스 방식 배포 패턴에 최적화 |

| Step | What happens |
| --- | --- |
| 1 | 동영상 업로드 또는 생성 |
| 2 | 전사 후 필요 시 자막 번역 |
| 3 | 레이아웃 제어와 함께 다국어 자막 번인 |
| 4 | 키프레임, 캡션, 메타데이터 생성 |
| 5 | 패키징 후 AutoPublish로 선택적 배포 |

### Pipeline focus

- 업로드, 생성, 리믹스, 라이브러리 관리 기능을 하나의 운영자 UI에서 제공
- 전사, 자막 교정/번역, 번인, 메타데이터 생성까지 API-first 방식으로 처리
- 선택적 생성 제공자 연동 (`agi/`의 Veo / Venice / A2E / Sora 헬퍼)
- AutoPublish를 통한 선택적 배포 핸드오프

## 🎯 At a Glance

| Area | Included in LazyEdit | Status |
| --- | --- | --- |
| 코어 앱 | Tornado API 백엔드 + Expo web/mobile 프런트엔드 | ✅ |
| 미디어 파이프라인 | ASR, 자막 번역/교정, 번인, 키프레임, 캡션, 메타데이터 | ✅ |
| 생성 | Stage A/B/C 및 제공자 헬퍼 라우트(`agi/`) | ✅ |
| 배포 | AutoPublish 연동 (선택) | 🟡 Optional |
| 런타임 모델 | 로컬 우선 스크립트, tmux 워크플로, systemd 서비스(선택) | ✅ |

## 🏗️ Architecture Snapshot

이 저장소는 UI 레이어를 갖춘 API-first 미디어 파이프라인으로 구성됩니다.

- `app.py`는 업로드, 처리, 생성, 배포 핸드오프, 미디어 서빙을 관리하는 Tornado 진입점입니다.
- `lazyedit/`에는 모듈형 파이프라인 구성요소(DB 영속화, 번역, 자막 번인, 캡션, 메타데이터, 제공자 어댑터)가 들어 있습니다.
- `app/`는 업로드/처리/미리보기/배포 플로우를 담당하는 Expo Router 앱(web/mobile)입니다.
- `config.py`는 환경 로딩과 기본/대체 런타임 경로를 중앙에서 해석합니다.
- `start_lazyedit.sh`와 `lazyedit_config.sh`는 tmux 기반 로컬/배포 실행 모드를 재현 가능하게 제공합니다.

| Layer | Main paths | Responsibility |
| --- | --- | --- |
| API 및 오케스트레이션 | `app.py`, `config.py` | 엔드포인트, 라우팅, 환경 변수 해석 |
| 처리 코어 | `lazyedit/`, `agi/` | 자막/캡션/메타데이터 파이프라인 + 제공자 |
| UI | `app/` | 운영자 경험(Expo 기반 web/mobile) |
| 런타임 스크립트 | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 로컬/서비스 실행 및 운영 |

상위 흐름:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

아래 화면은 인제스트부터 메타데이터 생성까지의 기본 운영자 흐름을 보여줍니다.

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

- ✨ Stage A/B/C와 Sora/Veo 통합 경로를 갖춘 프롬프트 기반 생성 워크플로.
- 🧵 전사 -> 자막 교정/번역 -> 번인 -> 키프레임 -> 캡션 -> 메타데이터로 이어지는 전체 처리 파이프라인.
- 🌏 furigana/IPA/romaji 관련 지원 경로를 포함한 다국어 자막 조합.
- 🔌 업로드, 처리, 미디어 서빙, 배포 큐 엔드포인트를 제공하는 API-first 백엔드.
- 🚚 소셜 플랫폼 연동을 위한 AutoPublish 선택적 통합.
- 🖥️ tmux 실행 스크립트 기반으로 백엔드 + Expo 통합 워크플로 지원.

## 🌍 Documentation & i18n

- 기준 소스: `README.md`
- 언어 변형: `i18n/README.*.md`
- 언어 내비게이션: 각 README 상단에 언어 바를 한 줄만 유지(중복 금지)
- 현재 저장소 언어: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

영어 문서와 번역 문서가 달라지면 영어 README를 신뢰할 수 있는 원본으로 두고, 각 언어 파일을 순차적으로 갱신하세요.

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

서브모듈/외부 의존성 노트:
- 이 저장소의 Git 서브모듈은 `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, `furigana`를 포함합니다.
- 운영 가이드에서는 `furigana`와 `echomind`를 외부/읽기 전용으로 취급합니다. 불확실하면 upstream를 유지하고 in-place 수정을 피하세요.

## ✅ Prerequisites

| Dependency | Notes |
| --- | --- |
| Linux environment | `systemd`/`tmux` 스크립트는 Linux 중심 |
| Python 3.10+ | Conda env `lazyedit` 사용 |
| Node.js 20+ + npm | `app/`의 Expo 실행에 필요 |
| FFmpeg | PATH에 있어야 함 |
| PostgreSQL | 로컬 peer auth 또는 DSN 기반 연결 |
| Git submodules | 핵심 파이프라인 동작에 필요 |

## 🚀 Installation

1. 서브모듈 포함 저장소 클론:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Conda 환경 활성화:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. 선택적 시스템 레벨 설치(서비스 모드):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

서비스 설치 참고:
- `install_lazyedit.sh`는 `ffmpeg`와 `tmux`를 설치한 뒤 `lazyedit.service`를 만듭니다.
- `lazyedit_config.sh`, `start_lazyedit.sh`, `stop_lazyedit.sh`는 생성되지 않으므로, 사전에 준비되어 있어야 합니다.

## ⚡ Quick Start

백엔드 + 프런트엔드를 로컬에서 실행하는 최소 경로:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

두 번째 셸에서:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

선택적 로컬 DB 부트스트랩:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| 로컬 개발(수동) | `python app.py` + Expo 명령 | `8787` | `8091` (예시) |
| tmux 오케스트레이션 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd 서비스 | `sudo systemctl start lazyedit.service` | 설정/env 기반 | N/A |

## 🧭 Command Cheat Sheet

| Task | Command |
| --- | --- |
| 서브모듈 초기화 | `git submodule update --init --recursive` |
| 백엔드만 시작 | `python app.py` |
| 백엔드 + Expo (tmux) | `./start_lazyedit.sh` |
| tmux 실행 중지 | `./stop_lazyedit.sh` |
| tmux 세션 접속 | `tmux attach -t lazyedit` |
| 서비스 상태 확인 | `sudo systemctl status lazyedit.service` |
| 서비스 로그 | `sudo journalctl -u lazyedit.service` |
| DB smoke test | `python db_smoke_test.py` |
| Pytest smoke test | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### Development: backend only

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

현재 배포 스크립트에서 사용하는 대체 진입점:

```bash
python app.py -m lazyedit
```

백엔드 기본 URL: `http://localhost:8787` (`config.py` 기준, `PORT` 또는 `LAZYEDIT_PORT`로 재정의 가능).

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

기본 `start_lazyedit.sh` 포트:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

세션 연결:

```bash
tmux attach -t lazyedit
```

중지:

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

`.env.example`를 `.env`로 복사하고 경로/비밀값을 갱신하세요:

```bash
cp .env.example .env
```

설정 우선순위:

- `config.py`는 `.env` 값이 있으면 로드하고, 셸에서 이미 export된 키는 덮어쓰지 않습니다.
- 런타임 값은 다음 순서로 결정됩니다: 셸 export 환경 변수 -> `.env` -> 코드 기본값.
- tmux/service 실행에서는 `lazyedit_config.sh`가 시작/세션 파라미터(`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, 포트)를 제어합니다.

### Key variables

| Variable | Purpose | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | 백엔드 포트 | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | 미디어 루트 디렉터리 | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | 로컬 DB fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish endpoint | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish 요청 타임아웃(초) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD 스크립트 경로 | 환경별 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR 모델명 | `large-v3` / `large-v2` (예시) |
| `LAZYEDIT_CAPTION_PYTHON` | 캡션 파이프라인 Python 런타임 | 환경별 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 기본 캡셔닝 경로/스크립트 | 환경별 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 대체 캡셔닝 스크립트/작업 디렉터리 | 환경별 |
| `GRSAI_API_*` | Veo/GRSAI 연동 설정 | 환경별 |
| `VENICE_*`, `A2E_*` | Venice/A2E 연동 설정 | 환경별 |
| `OPENAI_API_KEY` | OpenAI 기반 기능에 필요 | None |

기계별 참고:
- `app.py`에서 CUDA 동작을 직접 설정할 수 있습니다(`CUDA_VISIBLE_DEVICES` 사용).
- 일부 기본 경로는 워크스테이션 전용일 수 있으므로 `.env` 오버라이드로 이식성을 확보하세요.
- `lazyedit_config.sh`는 배포 스크립트의 tmux/session 시작 변수를 제어합니다.

## 🧾 Configuration Files

| File | Purpose |
| --- | --- |
| `.env.example` | 백엔드/서비스에서 사용하는 환경 변수 템플릿 |
| `.env` | 머신 로컬 오버라이드. 존재 시 `config.py`/`app.py`에서 로드 |
| `config.py` | 백엔드 기본값과 환경 해석 |
| `lazyedit_config.sh` | tmux/service 실행 프로필(배포 경로, conda env, app args, 세션 이름) |
| `start_lazyedit.sh` | tmux에서 backend + Expo를 선택한 포트로 실행 |
| `install_lazyedit.sh` | `lazyedit.service` 생성 및 기존 스크립트/설정 유효성 검사 |

이식성 높은 업데이트 순서:
1. `.env.example`를 `.env`로 복사합니다.
2. `.env`에서 경로/API 관련 `LAZYEDIT_*` 값을 설정합니다.
3. tmux/service 배포 동작이 필요할 때만 `lazyedit_config.sh`를 조정합니다.

## 🔌 API Examples

Base URL 예시는 `http://localhost:8787`을 전제로 합니다.

| API group | Representative endpoints |
| --- | --- |
| Upload and media | `/upload`, `/upload-stream`, `/media/*` |
| Video records | `/api/videos`, `/api/videos/{id}` |
| Processing | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publish | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generation | `/api/videos/generate` (+ `app.py`의 provider routes) |

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

추가 엔드포인트와 페이로드 상세는 `references/API_GUIDE.md`.

관련 엔드포인트 그룹:
- 동영상 라이프사이클: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- 처리 동작: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- 생성/제공자 경로: `/api/videos/generate` + `app.py`에 노출된 Venice/A2E 라우트
- 배포: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Backend가 `8887`일 때:

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

지원 seconds: `4`, `8`, `12`.
지원 sizes: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Development Notes

- `python`는 Conda env `lazyedit`의 것을 사용하세요 (`python3` 가정 금지).
- 대용량 미디어는 Git에 넣지 말고 `DATA/` 또는 외부 스토리지에 보관하세요.
- 파이프라인 구성요소가 해결되지 않으면 서브모듈을 초기화/업데이트하세요.
- 변경 범위를 작게 유지하고, 불필요한 대형 포맷 변경은 피하세요.
- 프런트엔드 작업 시 백엔드 API URL은 `EXPO_PUBLIC_API_URL`로 제어됩니다.
- 앱 개발을 위해 백엔드 CORS는 개방 상태입니다.

서브모듈 및 외부 의존성 정책:
- 외부 의존성은 upstream 소유로 간주합니다. 필요할 때가 아니면 서브모듈 내부를 수정하지 않습니다.
- 운영 지침에서 `furigana`(및 일부 로컬 환경에서 `echomind`)를 외부 의존 경로로 취급합니다. 불확실할 때는 upstream를 보존하고 인플레이스 편집은 피하세요.

유용한 참고:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

보안/설정:
- API 키와 비밀번호는 환경 변수로 관리하고, 자격 증명을 커밋하지 마세요.
- 머신별 오버라이드는 `.env`에, 공개 템플릿은 `.env.example`로 유지하세요.
- CUDA/GPU 동작이 호스트마다 다르면 하드코딩 대신 env 오버라이드로 대응하세요.

## ✅ Testing

현재 정식 테스트 범위는 작고 DB 중심입니다.

| Validation layer | Command or method |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | `DATA/`의 짧은 샘플로 웹 UI + API 실행 |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

기능 검증은 웹 UI와 API 흐름으로 `DATA/`의 짧은 샘플 클립을 사용하세요.

Assumptions and portability notes:
- 코드 내 기본 경로 일부는 워크스테이션 전용 폴백으로 남아 있을 수 있습니다. 이는 현재 저장소 상태에서 정상입니다.
- 기본 경로가 현재 머신에 없으면 해당 `LAZYEDIT_*` 변수를 `.env`에 설정하세요.
- 머신별 값이 불명확하면 기존 설정을 유지하면서 명시적 오버라이드를 추가하세요.

## 🧱 Assumptions & Known Limits

- 루트 잠금 파일로 의존성을 고정하지 않아 재현성은 로컬 환경 관리에 좌우됩니다.
- 현재 저장소에서 `app.py`는 의도적으로 모놀리식이며 큰 라우트 표면을 가집니다.
- 파이프라인 검증은 대부분 통합/수동 방식(UI + API + 샘플 미디어)이고 정식 자동 테스트는 제한적입니다.
- 런타임 디렉터리(`DATA/`, `temp/`, `translation_logs/`)는 운영 산출물이므로 크기가 빠르게 증가할 수 있습니다.
- 전체 기능에는 서브모듈이 필수이며, 일부만 체크아웃하면 스크립트 누락 오류가 발생하기 쉽습니다.

## 🚢 Deployment & Sync Notes

현재 알려진 경로 및 동기화 흐름(운영 문서 기준):

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

이 저장소에서 `AutoPublish/` 변경을 push한 뒤 퍼블리싱 호스트에서 pull:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| Problem | Check / Fix |
| --- | --- |
| 파이프라인 모듈 또는 스크립트 누락 | `git submodule update --init --recursive` 실행 |
| FFmpeg 미설치 | FFmpeg 설치 후 `ffmpeg -version` 확인 |
| 포트 충돌 | 백엔드는 기본 `8787`, `start_lazyedit.sh`는 `18787` 기본값. `LAZYEDIT_PORT` 또는 `PORT`로 지정 |
| Expo가 백엔드에 연결 불가 | `EXPO_PUBLIC_API_URL`이 동작 중인 백엔드 호스트/포트를 가리키는지 확인 |
| DB 연결 문제 | PostgreSQL + DSN/env vars 확인, 선택적으로 `python db_smoke_test.py` 실행 |
| GPU/CUDA 문제 | 드라이버/CUDA와 설치된 Torch 스택 호환성 확인 |
| 서비스 설치 스크립트 실패 | 실행 전 `lazyedit_config.sh`, `start_lazyedit.sh`, `stop_lazyedit.sh` 존재 확인 |

## 🗺️ Roadmap

- 인앱 자막/세그먼트 편집(라인 단위 제어 및 A/B 미리보기) 지원
- 핵심 API 흐름의 E2E 테스트 커버리지 확대
- i18n README 변형과 배포 모드의 문서 정합성 강화
- 생성 제공자의 재시도 및 상태 가시성 개선

## 🤝 Contributing

기여를 환영합니다.

1. Fork하고 feature branch 생성.
2. 커밋은 작고 범위를 명확하게 유지.
3. 로컬에서 변경 검증 (`python app.py`, 핵심 API 플로우, 필요 시 앱 통합).
4. 목적, 재현 방법, 변경 전후 노트를 포함해 PR 작성( UI 변경 시 스크린샷 권장 ).

실무 지침:
- Python 스타일(PEP 8, 4-space, snake_case) 준수
- 자격 증명이나 대형 바이너리 커밋 금지
- 동작 변경 시 docs/config 스크립트도 함께 업데이트
- 권장 커밋 형식: 짧고 명령형, 범위를 가진 메시지 (예: `add preprocessing for Honor videos`)


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit는 FFmpeg, Tornado, MoviePy, OpenAI 모델, 자막 워크플로의 CJKWrap 및 다국어 텍스트 도구 등 오픈소스 라이브러리와 서비스를 기반으로 동작합니다.
