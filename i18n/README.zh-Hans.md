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
  <b>用于生成、字幕处理、元数据和可选发布的一体化 AI 视频工作流。</b>
  <br />
  <sub>上传或生成 -> 转录 -> 翻译/润色 -> 烧录字幕 -> 关键帧/文案 -> 元数据 -> 发布</sub>
</p>

# LazyEdit

LazyEdit 是一个端到端的 AI 辅助视频工作流，支持创作、处理和可选发布。它整合了基于提示词的生成（Stage A/B/C）、媒体处理 API、字幕渲染、关键帧文案、元数据生成，以及 AutoPublish 交接。

| Quick fact | Value |
| --- | --- |
| 📘 Canonical README | `README.md` (this file) |
| 🌐 Language variants | `i18n/README.*.md`（每个 README 顶部仅保留一套语言导航） |
| 🧠 Backend entrypoint | `app.py`（Tornado） |
| 🖥️ Frontend app | `app/`（Expo web/mobile） |

## 🧭 Contents

- [Overview](#overview)
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

LazyEdit 以 Tornado 后端（`app.py`）和 Expo 前端（`app/`）为核心。

> 注意：如果不同机器上的仓库或运行时细节有差异，请保留已有默认值，并通过环境变量覆盖，而不要删除机器特定的回退配置。

| Why teams use it | Practical result |
| --- | --- |
| Unified operator flow | 在同一流程里完成上传、生成、混剪、发布 |
| API-first design | 更容易脚本化，并与其他工具集成 |
| Local-first runtime | 适配 tmux + 基于服务的部署模式 |

| Step | What happens |
| --- | --- |
| 1 | 上传或生成视频 |
| 2 | 转录并可选翻译字幕 |
| 3 | 使用布局控制烧录多语言字幕 |
| 4 | 生成关键帧、文案和元数据 |
| 5 | 打包并可选通过 AutoPublish 发布 |

### Pipeline focus

- 从同一个操作界面完成上传、生成、混剪和素材库管理。
- API 优先的处理流程涵盖转录、字幕润色/翻译、烧录和元数据。
- 可选的生成提供方集成（`agi/` 中的 Veo / Venice / A2E / Sora 助手）。
- 可选通过 `AutoPublish` 进行发布交接。

## 🎯 At a Glance

| Area | Included in LazyEdit | Status |
| --- | --- | --- |
| Core app | Tornado API 后端 + Expo web/mobile 前端 | ✅ |
| Media pipeline | ASR、字幕翻译/润色、烧录、关键帧、文案、元数据 | ✅ |
| Generation | Stage A/B/C 与服务提供方路由（`agi/`） | ✅ |
| Distribution | 可选 AutoPublish 交接 | 🟡 可选 |
| Runtime model | 本机优先脚本、tmux 工作流、可选 systemd 服务 | ✅ |

## 🏗️ Architecture Snapshot

仓库按 API-first 媒体管道组织，并提供 UI 层：

- `app.py` 是 Tornado 入口与路由编排层，负责上传、处理、生成、发布交接和媒体服务。
- `lazyedit/` 包含模块化管道组件（数据库持久化、翻译、字幕烧录、字幕、元数据、Provider 适配器）。
- `app/` 是一个 Expo Router 应用（web/mobile），用于上传、处理、预览和发布流程。
- `config.py` 统一处理环境变量加载及默认/回退路径。
- `start_lazyedit.sh` 和 `lazyedit_config.sh` 提供可复现的 tmux 本地/部署运行模式。

| Layer | Main paths | Responsibility |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | 接口、路由、环境变量解析 |
| Processing core | `lazyedit/`, `agi/` | 字幕/文案/元数据管道 + Provider |
| UI | `app/` | 操作体验（通过 Expo 的 web/mobile） |
| Runtime scripts | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 本地/服务启动与运维 |

High-level flow:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

以下截图展示了从素材接入到元数据生成的主要操作路径。

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>首页 · 上传</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>首页 · 生成</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>首页 · 混剪</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>素材库</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>视频总览</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>翻译预览</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>字幕位布局</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>字幕布局</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>关键帧 + 文案</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>元数据生成器</sub>
    </td>
  </tr>
</table>

## 🧩 Features

- ✨ 基于提示词的生成工作流（Stage A/B/C），包含 Sora 与 Veo 的集成路径。
- 🧵 完整的处理流水线：转录 -> 字幕润色/翻译 -> 烧录 -> 关键帧 -> 文案 -> 元数据。
- 🌏 多语言字幕编排，并支持 furigana/IPA/romaji 相关链路。
- 🔌 API-first 后端，提供上传、处理、媒体服务和发布队列接口。
- 🚚 可选集成 AutoPublish，用于社交平台发布交接。
- 🖥️ 借助 tmux 启动脚本，支持后端与 Expo 一体化工作流。

## 🌍 Documentation & i18n

LazyEdit 保留一份规范英文 README（`README.md`），多语言版本位于 `i18n/` 下。

- Canonical source: `README.md`
- Language variants: `i18n/README.*.md`
- Language bar: 每个 README 顶部仅保留一行语言导航（不允许重复）

如果翻译版与英文文档出现不一致，以英文 README 为真值源，并逐个更新语言文件。

| i18n policy | Rule |
| --- | --- |
| Canonical source | `README.md` is the source of truth |
| Language bar | 顶部语言导航必须唯一 |

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
- This repo's submodules include `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, and `furigana`.
- Operational guidance treats `furigana` and `echomind` as external/read-only in this repo workflow. When uncertain, preserve upstream and avoid editing in place.

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
- It does not generate `lazyedit_config.sh`, `start_lazyedit.sh`, or `stop_lazyedit.sh`; these must already exist and be correct.

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
| Local dev (manual) | `python app.py` + Expo command | `8787` | `8091` (example command) |
| Tmux orchestrated | `./start_lazyedit.sh` | `18787` | `18791` |
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
- Generation/provider paths: `/api/videos/generate` plus Venice/A2E routes exposed in `app.py`
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
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit builds on open-source libraries and services, including:
- FFmpeg for media processing
- Tornado for backend APIs
- MoviePy for editing workflows
- OpenAI models for AI-assisted pipeline tasks
- CJKWrap and multilingual text tooling in subtitle workflows
