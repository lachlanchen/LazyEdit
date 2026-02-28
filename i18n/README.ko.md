[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0" /></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Backend-Tornado-222222" alt="Backend: Tornado" />
  <img src="https://img.shields.io/badge/Frontend-Expo-000020?logo=expo&logoColor=white" alt="Frontend: Expo" />
  <img src="https://img.shields.io/badge/FFmpeg-required-0A0A0A?logo=ffmpeg&logoColor=white" alt="FFmpeg required" />
  <img src="https://img.shields.io/badge/PostgreSQL-supported-336791?logo=postgresql&logoColor=white" alt="PostgreSQL supported" />
  <img src="https://img.shields.io/badge/Stage_A%2FB%2FC-enabled-0f766e" alt="Stage A/B/C enabled" />
  <img src="https://img.shields.io/badge/AutoPublish-optional-orange" alt="AutoPublish optional" />
</p>

# LazyEdit

LazyEdit는 제작, 처리, 선택적 퍼블리싱까지 다루는 종단간 AI 보조 영상 워크플로입니다. 프롬프트 기반 생성(Stage A/B/C), 미디어 처리 API, 자막 렌더링, 키프레임 캡셔닝, 메타데이터 생성, AutoPublish 핸드오프를 하나로 결합합니다.

## ✨ 개요

LazyEdit는 Tornado 백엔드(`app.py`)와 Expo 프런트엔드(`app/`)를 중심으로 구성됩니다.

| 단계 | 수행 내용 |
| --- | --- |
| 1 | 영상 업로드 또는 생성 |
| 2 | 자막 전사 및 선택적 번역 |
| 3 | 레이아웃 제어로 다국어 자막 번인 |
| 4 | 키프레임, 캡션, 메타데이터 생성 |
| 5 | 패키징 후 필요 시 AutoPublish로 퍼블리시 |

### 파이프라인 핵심

- 단일 운영자 UI에서 업로드, 생성, 리믹스, 라이브러리 관리를 처리.
- 전사, 자막 보정/번역, 번인, 메타데이터 생성을 API 우선 흐름으로 제공.
- 선택적 생성 제공자 연동(`agi/` 내 Veo / Venice / A2E / Sora 헬퍼).
- `AutoPublish`를 통한 선택적 퍼블리시 핸드오프.

## 🎯 한눈에 보기

| 영역 | LazyEdit 포함 내용 |
| --- | --- |
| 핵심 앱 | Tornado API 백엔드 + Expo 웹/모바일 프런트엔드 |
| 미디어 파이프라인 | ASR, 자막 번역/보정, 번인, 키프레임, 캡션, 메타데이터 |
| 생성 | Stage A/B/C 및 제공자 헬퍼 라우트(`agi/`) |
| 배포 | 선택적 AutoPublish 핸드오프 |
| 실행 모델 | 로컬 우선 스크립트, tmux 워크플로, 선택적 systemd 서비스 |

## 🎬 데모

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

- Sora 및 Veo 연동 경로를 포함한 프롬프트 기반 생성 워크플로(Stage A/B/C).
- 전체 처리 파이프라인: 전사 -> 자막 보정/번역 -> 번인 -> 키프레임 -> 캡션 -> 메타데이터.
- furigana/IPA/romaji 관련 지원 경로를 포함한 다국어 자막 합성.
- 업로드, 처리, 미디어 서빙, 퍼블리시 큐 엔드포인트를 갖춘 API 우선 백엔드.
- 소셜 플랫폼 핸드오프를 위한 선택적 AutoPublish 연동.
- tmux 실행 스크립트를 통한 백엔드 + Expo 통합 워크플로 지원.

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

## ✅ 사전 요구 사항

| 의존성 | 비고 |
| --- | --- |
| Linux 환경 | `systemd`/`tmux` 스크립트는 Linux 지향 |
| Python 3.10+ | Conda env `lazyedit` 사용 |
| Node.js 20+ + npm | `app/`의 Expo 앱 실행에 필요 |
| FFmpeg | `PATH`에서 사용 가능해야 함 |
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
- `lazyedit_config.sh`, `start_lazyedit.sh`, `stop_lazyedit.sh`는 자동 생성되지 않으므로 미리 존재하고 올바르게 구성되어 있어야 합니다.

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

`.env.example`를 `.env`로 복사한 뒤 경로/시크릿을 업데이트하세요:

```bash
cp .env.example .env
```

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
| `LAZYEDIT_CAPTION_PYTHON` | 캡션 파이프라인용 Python 런타임 | 환경 의존 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 기본 캡셔닝 경로/스크립트 | 환경 의존 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 대체 캡셔닝 경로/스크립트/cwd | 환경 의존 |
| `GRSAI_API_*` | Veo/GRSAI 연동 설정 | 환경 의존 |
| `VENICE_*`, `A2E_*` | Venice/A2E 연동 설정 | 환경 의존 |
| `OPENAI_API_KEY` | OpenAI 기반 기능에 필요 | 없음 |

머신별 참고 사항:
- `app.py`는 CUDA 동작을 설정할 수 있습니다(코드베이스 문맥상 `CUDA_VISIBLE_DEVICES` 사용).
- 일부 기본 경로는 워크스테이션 종속이므로 이식 가능한 구성을 위해 `.env` 재정의를 사용하세요.
- `lazyedit_config.sh`는 배포 스크립트용 tmux/세션 시작 변수를 제어합니다.

## 🔌 API 예시

기본 URL 예시는 `http://localhost:8787`를 가정합니다.

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

영상 목록 조회:

```bash
curl http://localhost:8787/api/videos
```

패키지 퍼블리시:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

추가 엔드포인트와 payload 상세: `references/API_GUIDE.md`.

## 🧪 예시

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

- Conda env `lazyedit`의 `python`을 사용하세요(시스템 `python3`를 가정하지 마세요).
- 대용량 미디어는 Git에 포함하지 말고 `DATA/` 또는 외부 스토리지에 저장하세요.
- 파이프라인 컴포넌트를 찾지 못할 때는 서브모듈을 초기화/업데이트하세요.
- 변경 범위는 명확히 제한하고, 관련 없는 대규모 포맷 변경은 피하세요.
- 프런트엔드 작업 시 백엔드 API URL은 `EXPO_PUBLIC_API_URL`로 제어합니다.
- 앱 개발을 위해 백엔드 CORS는 열려 있습니다.

서브모듈 및 외부 의존성 정책:
- 외부 의존성은 업스트림 소유로 취급하세요. 이 저장소 워크플로에서는 해당 프로젝트 작업이 목적이 아닌 한 서브모듈 내부 편집을 피하세요.
- 이 저장소의 운영 지침에서는 `furigana`(그리고 로컬 환경에 따라 `echomind`)를 외부 의존성 경로로 취급합니다. 확실하지 않다면 업스트림 상태를 유지하고 인플레이스 수정은 피하세요.

유용한 참고 문서:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ 테스트

현재 공식 테스트 범위는 작고 DB 중심입니다.

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

기능 검증은 `DATA/`의 짧은 샘플 클립으로 웹 UI와 API 흐름을 사용해 진행하세요.

## 🚢 배포 및 동기화 참고

현재 알려진 경로와 동기화 흐름(저장소 운영 문서 기준):

- 개발 워크스페이스: `/home/lachlan/ProjectsLFS/LazyEdit`
- 배포된 LazyEdit 백엔드 + 앱: `/home/lachlan/DiskMech/Projects/lazyedit`
- 배포된 AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- 퍼블리싱 시스템 호스트: `lazyingart`의 `/home/lachlan/Projects/auto-publish`

이 저장소에서 `AutoPublish/` 업데이트를 push한 뒤, 퍼블리싱 호스트에서 pull:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 문제 해결

| 문제 | 확인 / 해결 |
| --- | --- |
| 파이프라인 모듈 또는 스크립트를 찾을 수 없음 | `git submodule update --init --recursive` 실행 |
| FFmpeg를 찾을 수 없음 | FFmpeg 설치 후 `ffmpeg -version` 동작 확인 |
| 포트 충돌 | 백엔드 기본 `8787`, `start_lazyedit.sh` 기본 `18787`; `LAZYEDIT_PORT` 또는 `PORT`를 명시적으로 설정 |
| Expo가 백엔드에 연결 불가 | `EXPO_PUBLIC_API_URL`이 활성 백엔드 호스트/포트를 가리키는지 확인 |
| 데이터베이스 연결 문제 | PostgreSQL + DSN/env vars 확인; 선택적 스모크 체크: `python db_smoke_test.py` |
| GPU/CUDA 문제 | 설치된 Torch 스택과 드라이버/CUDA 호환성 확인 |
| 설치 중 서비스 스크립트 실패 | 설치 전 `lazyedit_config.sh`, `start_lazyedit.sh`, `stop_lazyedit.sh` 존재 여부 확인 |

## 🗺️ 로드맵

- 라인별 제어와 A/B 미리보기를 포함한 앱 내 자막/세그먼트 편집.
- 핵심 API 흐름에 대한 종단간 테스트 커버리지 강화.
- i18n README 변형과 배포 모드 전반의 문서 통합.
- 생성 제공자 재시도 및 상태 가시성 강화를 위한 워크플로 고도화.

## 🤝 기여

기여를 환영합니다.

1. 포크 후 기능 브랜치를 만드세요.
2. 커밋 범위를 작고 명확하게 유지하세요.
3. 로컬에서 변경을 검증하세요(`python app.py`, 핵심 API 흐름, 필요 시 앱 연동).
4. 목적, 재현 단계, 변경 전/후 노트(UI 변경은 스크린샷 권장)를 포함해 PR을 열어주세요.

실무 가이드:
- Python 스타일(PEP 8, 4칸 들여쓰기, snake_case 네이밍)을 따르세요.
- 자격 증명이나 대용량 바이너리 커밋을 피하세요.
- 동작 변경 시 문서/설정 스크립트를 함께 업데이트하세요.
- 권장 커밋 스타일: 짧고 명령형이며 범위가 드러나게(예: `fix ffmpeg 7 compatibility`).

## ❤️ 여러분의 후원이 가능하게 만드는 것

- <b>도구를 계속 오픈 상태로 유지</b>: 호스팅, 추론, 데이터 저장, 커뮤니티 운영.  
- <b>더 빠른 출시</b>: EchoMind, LazyEdit, MultilingualWhisper를 위한 집중 오픈소스 개발 시간.  
- <b>웨어러블 프로토타입</b>: IdeasGlass + LightMind를 위한 광학, 센서, 뉴로모픽/엣지 부품.  
- <b>모두를 위한 접근성</b>: 학생, 크리에이터, 커뮤니티 그룹을 위한 보조 배포.

### Donate

<div align="center">
<table style="margin:0 auto; text-align:center; border-collapse:collapse;">
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://chat.lazying.art/donate">https://chat.lazying.art/donate</a>
    </td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://chat.lazying.art/donate"><img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/figs/donate_button.svg" alt="Donate" height="44"></a>
    </td>
  </tr>
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://paypal.me/RongzhouChen">
        <img src="https://img.shields.io/badge/PayPal-Donate-003087?logo=paypal&logoColor=white" alt="Donate with PayPal">
      </a>
    </td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400">
        <img src="https://img.shields.io/badge/Stripe-Donate-635bff?logo=stripe&logoColor=white" alt="Donate with Stripe">
      </a>
    </td>
  </tr>
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><strong>WeChat</strong></td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><strong>Alipay</strong></td>
  </tr>
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><img alt="WeChat QR" src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/figs/donate_wechat.png" width="240"/></td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><img alt="Alipay QR" src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/figs/donate_alipay.png" width="240"/></td>
  </tr>
</table>
</div>

**支援 / Donate**

- ご支援は研究・開発と運用の継続に役立ち、より多くのオープンなプロジェクトを皆さんに届ける力になります。  
- 你的支持将用于研发与运维，帮助我持续公开分享更多项目与改进。  
- Your support sustains my research, development, and ops so I can keep sharing more open projects and improvements.

## 📄 라이선스

[Apache-2.0](LICENSE)

## 🙏 감사의 말

LazyEdit는 다음을 포함한 오픈소스 라이브러리와 서비스를 기반으로 합니다:
- 미디어 처리를 위한 FFmpeg
- 백엔드 API를 위한 Tornado
- 편집 워크플로를 위한 MoviePy
- AI 보조 파이프라인 작업을 위한 OpenAI 모델
- 자막 워크플로의 CJKWrap 및 다국어 텍스트 도구
