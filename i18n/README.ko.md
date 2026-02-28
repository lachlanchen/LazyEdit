[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

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

<p align="center">
  <b>AI 보조 영상 워크플로</b>로 생성, 자막 처리, 메타데이터 생성, 선택적 퍼블리싱까지 연결합니다.
  <br />
  <sub>업로드/생성 -> 전사 -> 번역/교정 -> 자막 번인 -> 캡션/키프레임 -> 메타데이터 -> 퍼블리시</sub>
</p>

# LazyEdit

LazyEdit는 영상 생성, 처리, 선택적 배포까지 아우르는 엔드투엔드 AI 보조 워크플로입니다. 프롬프트 기반 생성(Stage A/B/C), 미디어 처리 API, 자막 렌더링, 키프레임 캡셔닝, 메타데이터 생성, AutoPublish 연계를 하나의 흐름으로 통합합니다.

| 빠른 정보 | 값 |
| --- | --- |
| 📘 기준 README | `README.md` (이 파일) |
| 🌐 다국어 문서 | `i18n/README.*.md` (상단 단일 언어 바 유지) |
| 🧠 백엔드 진입점 | `app.py` (Tornado) |
| 🖥️ 프런트엔드 앱 | `app/` (Expo web/mobile) |

## 🧭 목차

- [개요](#-개요)
- [한눈에 보기](#-한눈에-보기)
- [아키텍처 스냅샷](#️-아키텍처-스냅샷)
- [데모](#-데모)
- [기능](#-기능)
- [문서 & i18n](#-문서--i18n)
- [프로젝트 구조](#️-프로젝트-구조)
- [사전 요구 사항](#-사전-요구-사항)
- [설치](#-설치)
- [빠른 시작](#-빠른-시작)
- [명령어 치트시트](#-명령어-치트시트)
- [사용 방법](#️-사용-방법)
- [설정](#️-설정)
- [설정 파일](#-설정-파일)
- [API 예시](#-api-예시)
- [실행 예시](#-실행-예시)
- [개발 노트](#-개발-노트)
- [테스트](#-테스트)
- [가정 및 알려진 제한](#-가정-및-알려진-제한)
- [배포 및 동기화 메모](#-배포-및-동기화-메모)
- [문제 해결](#-문제-해결)
- [로드맵](#️-로드맵)
- [기여](#-기여)
- [Support](#-support)
- [라이선스](#-라이선스)
- [감사의 말](#-감사의-말)

## ✨ 개요

LazyEdit는 Tornado 백엔드(`app.py`)와 Expo 프런트엔드(`app/`)를 중심으로 구성됩니다.

> 참고: 머신마다 저장소/런타임 세부값이 다를 수 있습니다. 기존 기본값은 유지하고, 머신별 값은 삭제 대신 환경 변수로 오버라이드하세요.

| 팀이 선택하는 이유 | 실무 결과 |
| --- | --- |
| 단일 운영 흐름 | 업로드/생성/리믹스/퍼블리시를 한 워크플로에서 처리 |
| API 우선 설계 | 자동화 스크립트 및 타 도구 연동이 쉬움 |
| 로컬 우선 실행 모델 | tmux + 서비스 기반 배포 패턴과 잘 맞음 |

| 단계 | 수행 내용 |
| --- | --- |
| 1 | 영상 업로드 또는 생성 |
| 2 | 자막 전사 및 필요 시 번역 |
| 3 | 레이아웃 제어와 함께 다국어 자막 번인 |
| 4 | 키프레임, 캡션, 메타데이터 생성 |
| 5 | 패키징 후 필요 시 AutoPublish로 배포 |

### 파이프라인 초점

- 단일 운영자 UI에서 업로드, 생성, 리믹스, 라이브러리 관리를 수행.
- 전사, 자막 교정/번역, 번인, 메타데이터를 API 중심 플로우로 제공.
- 선택적 생성 제공자 연동(`agi/`의 Veo / Venice / A2E / Sora 헬퍼).
- `AutoPublish`를 통한 선택적 퍼블리시 핸드오프.

## 🎯 한눈에 보기

| 영역 | LazyEdit 포함 항목 | 상태 |
| --- | --- | --- |
| 핵심 앱 | Tornado API 백엔드 + Expo 웹/모바일 프런트엔드 | ✅ |
| 미디어 파이프라인 | ASR, 자막 번역/교정, 번인, 키프레임, 캡션, 메타데이터 | ✅ |
| 생성 | Stage A/B/C 및 제공자 헬퍼 라우트(`agi/`) | ✅ |
| 배포 | 선택적 AutoPublish 연동 | 🟡 Optional |
| 실행 모델 | 로컬 우선 스크립트, tmux 워크플로, 선택적 systemd 서비스 | ✅ |

## 🏗️ 아키텍처 스냅샷

저장소는 UI 레이어를 포함한 API 중심 미디어 파이프라인으로 구성됩니다.

- `app.py`는 업로드, 처리, 생성, 퍼블리시 핸드오프, 미디어 서빙을 오케스트레이션하는 Tornado 진입점입니다.
- `lazyedit/`는 모듈형 파이프라인 구성요소(DB 영속화, 번역, 자막 번인, 캡션, 메타데이터, 제공자 어댑터)를 담고 있습니다.
- `app/`는 업로드, 처리, 미리보기, 퍼블리싱 흐름을 다루는 Expo Router 앱(웹/모바일)입니다.
- `config.py`는 환경 변수 로딩과 기본/대체 런타임 경로를 중앙 관리합니다.
- `start_lazyedit.sh`와 `lazyedit_config.sh`는 재현 가능한 tmux 기반 로컬/배포 실행 모드를 제공합니다.

| 레이어 | 주요 경로 | 책임 |
| --- | --- | --- |
| API & 오케스트레이션 | `app.py`, `config.py` | 엔드포인트, 라우팅, 환경 해석 |
| 처리 코어 | `lazyedit/`, `agi/` | 자막/캡션/메타데이터 파이프라인 + 제공자 |
| UI | `app/` | 운영자 경험(Expo 기반 웹/모바일) |
| 실행 스크립트 | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 로컬/서비스 시작 및 운영 |

상위 흐름:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 데모

아래 화면은 인제스트부터 메타데이터 생성까지의 주요 운영 흐름을 보여줍니다.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>홈 · 업로드</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>홈 · 생성</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>홈 · 리믹스</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>라이브러리</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>영상 개요</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>번역 미리보기</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>번인 슬롯</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>번인 레이아웃</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>키프레임 + 캡션</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>메타데이터 생성기</sub>
    </td>
  </tr>
</table>

## 🧩 기능

- ✨ Sora/Veo 연동 경로를 포함한 프롬프트 기반 생성 워크플로(Stage A/B/C).
- 🧵 전체 처리 파이프라인: 전사 -> 자막 교정/번역 -> 번인 -> 키프레임 -> 캡션 -> 메타데이터.
- 🌏 furigana/IPA/romaji 관련 지원 경로를 포함한 다국어 자막 합성.
- 🔌 업로드, 처리, 미디어 서빙, 퍼블리시 큐 엔드포인트를 제공하는 API 우선 백엔드.
- 🚚 소셜 플랫폼 연계를 위한 선택적 AutoPublish 통합.
- 🖥️ tmux 실행 스크립트를 통한 백엔드 + Expo 통합 워크플로.

## 🌍 문서 & i18n

LazyEdit는 영어 기준 README(`README.md`)를 단일 소스로 유지하고, 번역본은 `i18n/`에 둡니다.

- 기준 문서: `README.md`
- 언어별 문서: `i18n/README.*.md`
- 언어 내비게이션: 각 README 상단에 언어 선택 줄을 정확히 1개만 유지(중복 금지)
- 현재 저장소 제공 언어: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

번역 문서와 영어 문서가 불일치하면 영어 README를 소스 오브 트루스로 간주하고, 각 언어 파일을 순차적으로 업데이트하세요.

| i18n 정책 | 규칙 |
| --- | --- |
| 기준 소스 | `README.md`를 소스 오브 트루스로 유지 |
| 언어 바 | 상단에 언어 선택 줄 1개만 유지 |
| 업데이트 순서 | 영어 먼저, 이후 `i18n/README.*.md`를 하나씩 갱신 |

## 🗂️ 프로젝트 구조

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

서브모듈/외부 의존성 참고:
- 이 저장소의 Git 서브모듈에는 `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, `furigana`가 포함됩니다.
- 운영 지침상 `furigana`, `echomind`는 외부/읽기 전용으로 취급합니다. 불확실할 때는 업스트림 상태를 보존하고 내부 수정을 피하세요.

## ✅ 사전 요구 사항

| 의존성 | 비고 |
| --- | --- |
| Linux 환경 | `systemd`/`tmux` 스크립트는 Linux 지향 |
| Python 3.10+ | Conda env `lazyedit` 사용 |
| Node.js 20+ + npm | `app/`의 Expo 앱 실행에 필요 |
| FFmpeg | `PATH`에 존재해야 함 |
| PostgreSQL | 로컬 peer auth 또는 DSN 연결 |
| Git submodules | 핵심 파이프라인에 필요 |

## 🚀 설치

1. 저장소 클론 및 서브모듈 초기화:

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
- `install_lazyedit.sh`는 `ffmpeg`와 `tmux`를 설치한 뒤 `lazyedit.service`를 생성합니다.
- `lazyedit_config.sh`, `start_lazyedit.sh`, `stop_lazyedit.sh`는 자동 생성되지 않으므로 미리 준비되어 있어야 합니다.

## ⚡ 빠른 시작

백엔드 + 프런트엔드 로컬 실행(최소 경로):

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

### 런타임 프로필

| 프로필 | 시작 명령 | 기본 백엔드 | 기본 프런트엔드 |
| --- | --- | --- | --- |
| 로컬 개발(수동) | `python app.py` + Expo 명령 | `8787` | `8091` (예시) |
| tmux 오케스트레이션 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd 서비스 | `sudo systemctl start lazyedit.service` | Config/env 기반 | N/A |

## 🧭 명령어 치트시트

| 작업 | 명령 |
| --- | --- |
| 서브모듈 초기화 | `git submodule update --init --recursive` |
| 백엔드만 시작 | `python app.py` |
| 백엔드 + Expo 시작(tmux) | `./start_lazyedit.sh` |
| tmux 실행 중지 | `./stop_lazyedit.sh` |
| tmux 세션 접속 | `tmux attach -t lazyedit` |
| 서비스 상태 | `sudo systemctl status lazyedit.service` |
| 서비스 로그 | `sudo journalctl -u lazyedit.service` |
| DB 스모크 테스트 | `python db_smoke_test.py` |
| Pytest 스모크 테스트 | `pytest tests/test_db_smoke.py` |

## 🛠️ 사용 방법

### 개발: 백엔드만 실행

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

현재 배포 스크립트에서 사용하는 대체 엔트리:

```bash
python app.py -m lazyedit
```

백엔드 기본 URL: `http://localhost:8787` (`config.py` 기준, `PORT` 또는 `LAZYEDIT_PORT`로 재정의 가능).

### 개발: 백엔드 + Expo 앱(tmux)

```bash
./start_lazyedit.sh
```

기본 `start_lazyedit.sh` 포트:
- 백엔드: `18787`
- Expo 웹: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

세션 접속:

```bash
tmux attach -t lazyedit
```

세션 중지:

```bash
./stop_lazyedit.sh
```

### 서비스 관리

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ 설정

`.env.example`를 `.env`로 복사한 뒤 경로/시크릿 값을 업데이트하세요.

```bash
cp .env.example .env
```

설정 우선순위 참고:

- `config.py`는 `.env` 값이 있으면 로드하되, 셸에서 이미 export된 키는 덮어쓰지 않습니다.
- 따라서 실제 런타임 값의 출처는 다음 순서입니다: 셸 export 환경 변수 -> `.env` -> 코드 기본값.
- tmux/service 실행에서는 `lazyedit_config.sh`가 시작/세션 파라미터(`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, 시작 스크립트 환경 변수 기반 포트)를 제어합니다.

### 주요 변수

| 변수 | 용도 | 기본값/대체값 |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | 백엔드 포트 | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | 미디어 루트 디렉터리 | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | 로컬 DB 대체값 `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish 엔드포인트 | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish 요청 타임아웃(초) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD 스크립트 경로 | 환경 의존 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR 모델명 | `large-v3` / `large-v2` (예시) |
| `LAZYEDIT_CAPTION_PYTHON` | 캡션 파이프라인 Python 런타임 | 환경 의존 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 기본 캡셔닝 경로/스크립트 | 환경 의존 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 대체 캡셔닝 경로/스크립트/cwd | 환경 의존 |
| `GRSAI_API_*` | Veo/GRSAI 연동 설정 | 환경 의존 |
| `VENICE_*`, `A2E_*` | Venice/A2E 연동 설정 | 환경 의존 |
| `OPENAI_API_KEY` | OpenAI 기반 기능에 필요 | None |

머신별 참고 사항:
- `app.py`는 CUDA 동작을 설정할 수 있습니다(코드 문맥상 `CUDA_VISIBLE_DEVICES` 사용).
- 일부 기본 경로는 워크스테이션 종속입니다. 이식성을 위해 `.env` 오버라이드를 사용하세요.
- `lazyedit_config.sh`는 배포 스크립트용 tmux/세션 시작 변수를 제어합니다.

## 🧾 설정 파일

| 파일 | 용도 |
| --- | --- |
| `.env.example` | 백엔드/서비스에서 사용하는 환경 변수 템플릿 |
| `.env` | 머신 로컬 오버라이드; 존재 시 `config.py`/`app.py`가 로드 |
| `config.py` | 백엔드 기본값 및 환경 변수 해석 |
| `lazyedit_config.sh` | tmux/service 런타임 프로필(배포 경로, conda env, app args, 세션명) |
| `start_lazyedit.sh` | 선택한 포트로 tmux에서 백엔드 + Expo 실행 |
| `install_lazyedit.sh` | `lazyedit.service` 생성 및 기존 스크립트/설정 유효성 확인 |

머신 이식성 권장 업데이트 순서:
1. `.env.example`를 `.env`로 복사.
2. `.env`에서 경로/API 관련 `LAZYEDIT_*` 값을 설정.
3. tmux/service 배포 동작이 필요할 때만 `lazyedit_config.sh`를 조정.

## 🔌 API 예시

Base URL 예시는 `http://localhost:8787`를 가정합니다.

| API 그룹 | 대표 엔드포인트 |
| --- | --- |
| 업로드/미디어 | `/upload`, `/upload-stream`, `/media/*` |
| 비디오 레코드 | `/api/videos`, `/api/videos/{id}` |
| 처리 | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| 퍼블리시 | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| 생성 | `/api/videos/generate` (+ `app.py`의 제공자 라우트) |

업로드:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

종단간 처리:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

비디오 목록 조회:

```bash
curl http://localhost:8787/api/videos
```

퍼블리시 패키지 요청:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

추가 엔드포인트와 payload 상세는 `references/API_GUIDE.md`를 참고하세요.

실무에서 자주 쓰는 엔드포인트 그룹:
- 비디오 라이프사이클: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- 처리 액션: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- 생성/제공자 경로: `/api/videos/generate` + `app.py`에 노출된 Venice/A2E 라우트
- 배포: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 실행 예시

### 프런트엔드 로컬 실행(웹)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

백엔드가 `8887`일 때:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android 에뮬레이터

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS 시뮬레이터(macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### 선택적 Sora 생성 헬퍼

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

지원 seconds: `4`, `8`, `12`.
지원 sizes: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 개발 노트

- Conda env `lazyedit`의 `python`을 사용하세요(시스템 `python3` 가정 금지).
- 대용량 미디어는 Git에 커밋하지 말고 `DATA/` 또는 외부 스토리지에 저장하세요.
- 파이프라인 구성요소가 해석되지 않을 때는 서브모듈을 초기화/업데이트하세요.
- 변경 범위를 작고 명확하게 유지하고, 관련 없는 대규모 포맷 변경은 피하세요.
- 프런트엔드 작업 시 백엔드 API URL은 `EXPO_PUBLIC_API_URL`로 제어됩니다.
- 앱 개발을 위해 백엔드 CORS는 열려 있습니다.

서브모듈 및 외부 의존성 정책:
- 외부 의존성은 업스트림 소유로 취급합니다. 이 저장소 워크플로에서는 해당 프로젝트를 의도적으로 작업할 때가 아니면 서브모듈 내부 수정은 피하세요.
- 이 저장소 운영 지침에서는 `furigana`(그리고 일부 로컬 환경의 `echomind`)를 외부 의존성 경로로 취급합니다. 확실하지 않다면 업스트림을 보존하고 인플레이스 편집을 피하세요.

유용한 참고 문서:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

보안/설정 위생:
- API 키와 시크릿은 환경 변수로 관리하고, 자격 증명은 커밋하지 마세요.
- 머신 로컬 오버라이드는 `.env`를 우선 사용하고, 공개 템플릿은 `.env.example`로 유지하세요.
- CUDA/GPU 동작이 호스트마다 다르면 머신 고정값 하드코딩 대신 환경 변수 오버라이드를 사용하세요.

## ✅ 테스트

현재 공식 테스트 범위는 작고 DB 중심입니다.

| 검증 레이어 | 명령 또는 방법 |
| --- | --- |
| DB 스모크 | `python db_smoke_test.py` |
| Pytest DB 체크 | `pytest tests/test_db_smoke.py` |
| 기능 플로우 | `DATA/`의 짧은 샘플로 웹 UI + API 실행 |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

기능 검증은 `DATA/`의 짧은 샘플 클립을 사용해 웹 UI + API 흐름으로 확인하세요.

가정 및 이식성 참고:
- 코드의 일부 기본 경로는 워크스테이션 종속 대체값이며, 현재 저장소 상태에서 예상되는 동작입니다.
- 기본 경로가 현재 머신에 없으면 대응되는 `LAZYEDIT_*` 변수를 `.env`에 설정하세요.
- 머신별 값이 불확실하면 기존 설정을 삭제하지 말고 명시적 오버라이드를 추가하세요.

## 🧱 가정 및 알려진 제한

- 루트 잠금 파일로 백엔드 의존성이 고정되어 있지 않아, 환경 재현성은 로컬 셋업 규율에 의존합니다.
- 현재 저장소 상태에서 `app.py`는 의도적으로 모놀리식 구조이며 라우트 표면적이 큽니다.
- 대부분의 파이프라인 검증은 통합/수동(UI + API + 샘플 미디어) 방식이며, 자동화 테스트는 제한적입니다.
- 런타임 디렉터리(`DATA/`, `temp/`, `translation_logs/`)는 운영 산출물이므로 크기가 빠르게 증가할 수 있습니다.
- 전체 기능에는 서브모듈이 필요하며, 부분 체크아웃은 누락 스크립트 오류로 이어지는 경우가 많습니다.

## 🚢 배포 및 동기화 메모

저장소 운영 문서 기준 현재 알려진 경로 및 동기화 흐름:

- 개발 워크스페이스: `/home/lachlan/ProjectsLFS/LazyEdit`
- 배포된 LazyEdit 백엔드 + 앱: `/home/lachlan/DiskMech/Projects/lazyedit`
- 배포된 AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- 퍼블리싱 시스템 호스트: `lazyingart`의 `/home/lachlan/Projects/auto-publish`

| 환경 | 경로 | 비고 |
| --- | --- | --- |
| 개발 워크스페이스 | `/home/lachlan/ProjectsLFS/LazyEdit` | 메인 소스 + 서브모듈 |
| 배포된 LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | 운영 문서상 tmux `la-lazyedit` |
| 배포된 AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | monitor/sync/process 세션 |
| 퍼블리싱 호스트 | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | 서브모듈 갱신 후 pull 필요 |

이 저장소에서 `AutoPublish/` 업데이트를 push한 뒤, 퍼블리싱 호스트에서 pull:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 문제 해결

| 문제 | 점검 / 해결 |
| --- | --- |
| 파이프라인 모듈/스크립트 누락 | `git submodule update --init --recursive` 실행 |
| FFmpeg 미설치 | FFmpeg 설치 후 `ffmpeg -version` 확인 |
| 포트 충돌 | 백엔드 기본 `8787`, `start_lazyedit.sh` 기본 `18787`; `LAZYEDIT_PORT` 또는 `PORT` 명시 설정 |
| Expo가 백엔드에 연결 불가 | `EXPO_PUBLIC_API_URL`이 활성 백엔드 호스트/포트를 가리키는지 확인 |
| DB 연결 문제 | PostgreSQL + DSN/env vars 확인; 선택적 스모크 체크: `python db_smoke_test.py` |
| GPU/CUDA 문제 | 설치된 Torch 스택과 드라이버/CUDA 호환성 확인 |
| 서비스 설치 스크립트 실패 | 설치 전 `lazyedit_config.sh`, `start_lazyedit.sh`, `stop_lazyedit.sh` 존재 확인 |

## 🗺️ 로드맵

- 라인 단위 제어와 A/B 미리보기를 포함한 인앱 자막/세그먼트 편집.
- 핵심 API 흐름에 대한 엔드투엔드 테스트 커버리지 강화.
- i18n README 변형과 배포 모드 전반의 문서 수렴.
- 생성 제공자 재시도 및 상태 가시성 강화를 위한 워크플로 고도화.

## 🤝 기여

기여를 환영합니다.

1. 포크 후 기능 브랜치를 생성하세요.
2. 커밋은 작고 목적이 분명하게 유지하세요.
3. 로컬에서 변경을 검증하세요(`python app.py`, 핵심 API 흐름, 필요 시 앱 연동).
4. 목적, 재현 단계, 변경 전/후 노트(UI 변경 시 스크린샷 권장)를 포함해 PR을 열어주세요.

실무 가이드:
- Python 스타일(PEP 8, 4칸 들여쓰기, snake_case 네이밍)을 따르세요.
- 자격 증명이나 대용량 바이너리는 커밋하지 마세요.
- 동작 변경 시 문서/설정 스크립트도 함께 갱신하세요.
- 권장 커밋 스타일: 짧고 명령형이며 범위가 보이게(예: `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 라이선스

[Apache-2.0](LICENSE)

## 🙏 감사의 말

LazyEdit는 다음을 포함한 오픈소스 라이브러리와 서비스를 기반으로 구축되었습니다.
- 미디어 처리를 위한 FFmpeg
- 백엔드 API를 위한 Tornado
- 편집 워크플로를 위한 MoviePy
- AI 보조 파이프라인 작업을 위한 OpenAI 모델
- 자막 워크플로의 CJKWrap 및 다국어 텍스트 도구
