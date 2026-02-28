[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>用于生成、字幕处理、元数据和可选发布的一体化 AI 视频工作流。</b>
  <br />
  <sub>上传或生成 -> 转录 -> 翻译/润色 -> 烧录字幕 -> 文案/关键帧 -> 元数据 -> 发布</sub>
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

LazyEdit 是一个端到端的 AI 辅助视频工作流，覆盖创作、处理与可选发布。它整合了基于提示词的生成（Stage A/B/C）、媒体处理 API、字幕渲染、关键帧文案生成以及 AutoPublish 对接。

| 快速事实 | 值 |
| --- | --- |
| 📘 官方英文说明 | `README.md`（本文件） |
| 🌐 多语言版本 | `i18n/README.*.md`（每个 README 顶部仅保留一条语言导航） |
| 🧠 后端入口 | `app.py`（Tornado） |
| 🖥️ 前端应用 | `app/`（Expo web/mobile） |

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

LazyEdit 以 Tornado 后端（`app.py`）和 Expo 前端（`app/`）为核心搭建。

> 注意：如果仓库或运行时细节因机器而异，请保留现有默认值，并通过环境变量覆盖，不要删除机器特有的回退配置。

| 使用原因 | 实际效果 |
| --- | --- |
| 统一的操作流程 | 在同一个流程里完成上传、生成、重混与发布 |
| API 优先设计 | 易于脚本化，并便于与其他工具集成 |
| 本地优先运行时 | 支持 tmux + 基于服务的部署模式 |

| 步骤 | 发生的事情 |
| --- | --- |
| 1 | 上传或生成视频 |
| 2 | 转录并可选翻译字幕 |
| 3 | 按布局控制烧录多语言字幕 |
| 4 | 生成关键帧、字幕和元数据 |
| 5 | 打包并可选通过 AutoPublish 发布 |

### Pipeline focus

- 在单一操作界面内完成上传、生成、重混与素材库管理。
- 采用 API 优先处理流，覆盖转录、字幕润色/翻译、烧录与元数据。
- 可选接入生成提供方（`agi/` 下的 Veo / Venice / A2E / Sora 助手）。
- 可选通过 `AutoPublish` 进行发布交接。

## 🎯 At a Glance

| 模块 | LazyEdit 内含 | 状态 |
| --- | --- | --- |
| 核心应用 | Tornado API 后端 + Expo web/mobile 前端 | ✅ |
| 媒体流水线 | ASR、字幕翻译/润色、烧录、关键帧、文案、元数据 | ✅ |
| 生成 | Stage A/B/C 与提供方路由（`agi/`） | ✅ |
| 分发 | 可选 AutoPublish 交接 | 🟡 Optional |
| 运行模型 | 本机优先脚本、tmux 工作流、可选 systemd 服务 | ✅ |

## 🏗️ Architecture Snapshot

仓库采用“有 UI 层的 API-first 媒体流水线”组织：

- `app.py` 是 Tornado 入口与路由编排器，负责上传、处理、生成、发布交接和媒体服务。
- `lazyedit/` 包含模块化的流水线组件（数据库持久化、翻译、字幕烧录、字幕、元数据、Provider 适配器）。
- `app/` 是 Expo Router 应用（web/mobile），用于上传、处理、预览和发布流程。
- `config.py` 统一负责环境变量加载与默认/回退路径。
- `start_lazyedit.sh` 与 `lazyedit_config.sh` 提供可复现的 tmux 本地/部署运行模式。

| 层级 | 主要路径 | 职责 |
| --- | --- | --- |
| API 与编排 | `app.py`, `config.py` | 接口、路由、环境变量解析 |
| 处理核心 | `lazyedit/`, `agi/` | 字幕/文案/元数据流水线 + Provider |
| UI | `app/` | 操作体验（通过 Expo 的 web/mobile） |
| 运行脚本 | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 本地/服务启动与运维 |

高层流程：

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

下面展示从素材接入到元数据生成的主要操作路径。

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

- ✨ 基于提示词的生成工作流（Stage A/B/C），包含 Sora 与 Veo 的集成路径。
- 🧵 完整处理流水线：转录 -> 字幕润色/翻译 -> 烧录 -> 关键帧 -> 文案 -> 元数据。
- 🌏 多语言字幕编排，支持 furigana/IPA/romaji 相关链路。
- 🔌 API-first 后端，提供上传、处理、媒体服务和发布队列接口。
- 🚚 可选集成 AutoPublish，用于社交平台发布交接。
- 🖥️ 通过 tmux 启动脚本支持后端 + Expo 的一体化工作流。

## 🌍 Documentation & i18n

- 官方来源：`README.md`
- 多语言版本：`i18n/README.*.md`
- 语言导航：每个 README 顶部仅保留一行语言导航（不允许重复）

如果翻译与英文文档发生偏差，请以英语 README 为事实来源，并逐一更新各语言文件。

| i18n 规范 | 规则 |
| --- | --- |
| 官方来源 | 保持 `README.md` 为事实来源 |
| 语言导航 | 每个 README 顶部仅保留一行语言导航 |

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
├── start_lazyedit.sh                 # tmux launcher for backend + Expo
├── stop_lazyedit.sh                  # tmux stop helper
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

子模块 / 外部依赖说明：
- 本仓库中的 Git 子模块包括 `AutoPublish`、`AutoPubMonitor`、`whisper_with_lang_detect`、`vit-gpt2-image-captioning`、`clip-gpt-captioning` 与 `furigana`。
- 仓库运行指引会将 `furigana` 与 `echomind` 视为外部依赖；如有疑问，优先保留上游，不要在本仓库内直接编辑。

## ✅ Prerequisites

| 依赖 | 说明 |
| --- | --- |
| Linux 环境 | `systemd` / `tmux` 脚本以 Linux 为向导 |
| Python 3.10+ | 使用 Conda 环境 `lazyedit` |
| Node.js 20+ + npm | `app/` 的 Expo 应用所需 |
| FFmpeg | 必须在 `PATH` 中可用 |
| PostgreSQL | 本地 peer 认证或基于 DSN 的连接 |
| Git 子模块 | 核心流水线依赖 |

## 🚀 Installation

1. 克隆并初始化子模块：

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. 激活 Conda 环境：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. 可选的系统级安装（服务模式）：

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

服务安装说明：
- `install_lazyedit.sh` 会安装 `ffmpeg` 与 `tmux`，并创建 `lazyedit.service`。
- 它不会创建 `lazyedit_config.sh`、`start_lazyedit.sh` 或 `stop_lazyedit.sh`，这些文件必须已存在并配置正确。

## ⚡ Quick Start

后端 + 前端本地最小启动方式：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

在第二个终端中：

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

可选的本地数据库初始化：

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| 本地开发（手动） | `python app.py` + Expo 命令 | `8787` | `8091`（示例命令） |
| tmux 编排 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd 服务 | `sudo systemctl start lazyedit.service` | 由配置/环境决定 | N/A |

## 🧭 Command Cheat Sheet

| 任务 | 命令 |
| --- | --- |
| 初始化子模块 | `git submodule update --init --recursive` |
| 仅启动后端 | `python app.py` |
| 启动后端 + Expo（tmux） | `./start_lazyedit.sh` |
| 停止 tmux 会话 | `./stop_lazyedit.sh` |
| 连接 tmux 会话 | `tmux attach -t lazyedit` |
| 查询服务状态 | `sudo systemctl status lazyedit.service` |
| 查看服务日志 | `sudo journalctl -u lazyedit.service` |
| 数据库冒烟测试 | `python db_smoke_test.py` |
| Pytest 冒烟测试 | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### Development: backend only

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

当前部署脚本使用的备用入口：

```bash
python app.py -m lazyedit
```

默认后端地址：`http://localhost:8787`（来自 `config.py`，可通过 `PORT` 或 `LAZYEDIT_PORT` 覆盖）。

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

`start_lazyedit.sh` 默认端口：
- 后端：`18787`
- Expo Web：`18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

接入会话：

```bash
tmux attach -t lazyedit
```

停止会话：

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

将 `.env.example` 复制为 `.env` 并更新路径/密钥：

```bash
cp .env.example .env
```

配置优先级说明：

- `config.py` 会读取 `.env` 中的值，并且不会覆盖 shell 中已导出的键。
- 因此运行时值来源为：shell 导出的环境变量 -> `.env` -> 代码默认值。
- 对于 tmux/service 运行，`lazyedit_config.sh` 控制启动与会话参数（`LAZYEDIT_DIR`、`CONDA_ENV`、`APP_ARGS`，端口由启动脚本环境决定）。

### Key variables

| 变量 | 用途 | 默认值 / 回退 |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | 后端端口 | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | 媒体根目录 | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | 本地回退 `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish 端点 | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish 请求超时（秒） | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD 脚本路径 | 依环境而定 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR 模型名 | `large-v3` / `large-v2`（示例） |
| `LAZYEDIT_CAPTION_PYTHON` | 字幕管道使用的 Python 运行时 | 依环境而定 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 主字幕路径/脚本 | 依环境而定 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 备用字幕脚本/工作目录 | 依环境而定 |
| `GRSAI_API_*` | Veo/GRSAI 集成设置 | 依环境而定 |
| `VENICE_*`, `A2E_*` | Venice/A2E 集成设置 | 依环境而定 |
| `OPENAI_API_KEY` | OpenAI 相关功能所需 | 未设置 |

机器相关说明：
- `app.py` 可能设置 CUDA 行为（参考代码中的 `CUDA_VISIBLE_DEVICES` 使用）。
- 某些默认路径为工作站相关；便携部署请使用 `.env` 覆盖。
- `lazyedit_config.sh` 负责部署脚本中的 tmux/会话启动变量。

## 🧾 Configuration Files

| 文件 | 用途 |
| --- | --- |
| `.env.example` | 后端/服务使用的环境变量模板 |
| `.env` | 本机本地覆盖；若存在由 `config.py`/`app.py` 读取 |
| `config.py` | 后端默认配置与环境变量解析 |
| `lazyedit_config.sh` | tmux/service 运行配置（部署路径、conda env、应用参数、会话名） |
| `start_lazyedit.sh` | 在 tmux 中按选定端口启动后端 + Expo |
| `install_lazyedit.sh` | 创建 `lazyedit.service` 并校验现有脚本与配置 |

机器可移植建议更新顺序：
1. 复制 `.env.example` 到 `.env`。
2. 在 `.env` 中设置路径与 API 相关的 `LAZYEDIT_*` 值。
3. 仅在 tmux/service 部署行为需要时调整 `lazyedit_config.sh`。

## 🔌 API Examples

示例默认 Base URL 为 `http://localhost:8787`。

| API 分组 | 典型端点 |
| --- | --- |
| 上传与媒体 | `/upload`, `/upload-stream`, `/media/*` |
| 视频记录 | `/api/videos`, `/api/videos/{id}` |
| 处理 | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| 发布 | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| 生成 | `/api/videos/generate`（加上 `app.py` 中的 provider 路由） |

上传：

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

端到端处理：

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

列出视频：

```bash
curl http://localhost:8787/api/videos
```

发布打包：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

更多端点和请求体说明见：`references/API_GUIDE.md`。

常用端点组：
- 视频生命周期：`/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- 处理动作：`/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- 生成/provider 路径：`/api/videos/generate` 以及 `app.py` 暴露的 Venice/A2E 路由
- 分发：`/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

如果后端运行在 `8887`：

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

支持时长：`4`、`8`、`12`。
支持分辨率：`720x1280`、`1280x720`、`1024x1792`、`1792x1024`。

## 🧪 Development Notes

- 使用 Conda 环境 `lazyedit` 中的 `python`，不要默认假设有 `python3`。
- 不要将大体积媒体文件提交到 Git；放在 `DATA/` 或外部存储。
- 当流水线组件无法解析时，初始化或更新子模块。
- 保持改动范围集中，避免无关的大规模格式改动。
- 对于前端开发，后端 API 地址由 `EXPO_PUBLIC_API_URL` 控制。
- 后端对开发阶段会开放 CORS。

子模块与外部依赖策略：
- 将外部依赖视作上游项目。在本仓库工作流中，避免编辑子模块内部，除非你真的在该子项目中工作。
- 本仓库指引将 `furigana`（以及某些本地环境中的 `echomind`）视为外部路径；不确定时，保留上游并避免就地编辑。

参考资料：
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

安全与配置规范：
- 将 API Key 与凭据保存在环境变量中，不要提交敏感信息。
- 优先在 `.env` 中写入机器级覆盖，`.env.example` 保持公开模板。
- 若 CUDA/GPU 行为因主机不同而异，请通过环境变量覆盖，而不是硬编码机器值。

## ✅ Testing

当前正式测试覆盖有限，主要是数据库导向。

| 验证层 | 命令或方法 |
| --- | --- |
| DB 冒烟测试 | `python db_smoke_test.py` |
| Pytest DB 检查 | `pytest tests/test_db_smoke.py` |
| 功能流程 | 通过 `DATA/` 中的短样本，用 Web UI + API 跑一遍 |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

功能验证请使用 web UI 和 API 流程，并用 `DATA/` 中的短样本。

假设与可移植性说明：
- 代码中的部分默认路径是工作站级回退，这是当前仓库状态下的预期行为。
- 若默认路径在你机器上不存在，请在 `.env` 中设置对应的 `LAZYEDIT_*` 变量。
- 若某个机器特定值不确定，保留现有设置并补充显式覆盖，而不是删除默认值。

## 🧱 Assumptions & Known Limits

- 当前未对根环境加锁，环境可复现性仍依赖本地环境管理。
- `app.py` 在当前状态下保持“单体”结构，包含较大的路由面。
- 大多数流程验证为集成/手工验证（UI + API + 示例媒体），自动化测试较少。
- 运行目录（`DATA/`, `temp/`, `translation_logs/`）用于产物输出，体积可能快速增长。
- 子模块是完整功能所必需；只做部分检出常导致脚本缺失错误。

## 🚢 Deployment & Sync Notes

当前已知的路径与同步流程（来自仓库运维文档）：

- 开发工作区：`/home/lachlan/ProjectsLFS/LazyEdit`
- 已部署 LazyEdit 后端 + 应用：`/home/lachlan/DiskMech/Projects/lazyedit`
- 已部署 AutoPubMonitor：`/home/lachlan/DiskMech/Projects/autopub-monitor`
- 发布系统主机：`/home/lachlan/Projects/auto-publish`（主机：`lazyingart`）

| 环境 | 路径 | 说明 |
| --- | --- | --- |
| 开发工作区 | `/home/lachlan/ProjectsLFS/LazyEdit` | 主源码与子模块 |
| 已部署 LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | 运维文档中的 tmux 会话 `la-lazyedit` |
| 已部署 AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | monitor/sync/process 会话 |
| 发布主机 | `/home/lachlan/Projects/auto-publish`（`lazyingart`） | 子模块更新后请拉取 |

在从本仓库推送 `AutoPublish/` 更新后，在发布主机执行：

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| 问题 | 检查 / 处理 |
| --- | --- |
| 缺少流水线模块或脚本 | 运行 `git submodule update --init --recursive` |
| FFmpeg 未找到 | 安装 FFmpeg 并确认 `ffmpeg -version` 可执行 |
| 端口冲突 | 后端默认 `8787`，`start_lazyedit.sh` 默认 `18787`，可显式设置 `LAZYEDIT_PORT` 或 `PORT` |
| Expo 无法访问后端 | 确保 `EXPO_PUBLIC_API_URL` 指向当前可用的后端 host/port |
| 数据库连接问题 | 检查 PostgreSQL 与 DSN/环境变量；可选执行 `python db_smoke_test.py` |
| GPU/CUDA 问题 | 验证驱动与 CUDA 与已安装的 Torch 版本兼容 |
| 安装服务脚本失败 | 确保 `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` 在运行安装前存在 |

## 🗺️ Roadmap

- 在应用内提供逐行控制的字幕/片段编辑，含 A/B 预览。
- 为核心 API 流增加更完整的端到端测试覆盖。
- 推进 i18n README 与部署模式下文档的一致化。
- 强化生成提供方重试与状态可见性的流程稳定性。

## 🤝 Contributing

欢迎提交贡献。

1. Fork 并创建特性分支。
2. 保持提交聚焦且范围明确。
3. 本地验证改动（`python app.py`、关键 API 流程、必要时联调 app）。
4. 提交 PR 时说明目标、复现步骤、前后对比（UI 变更请附图）。

实践建议：
- 遵循 Python 风格（PEP 8，4 空格，snake_case 命名）。
- 避免提交凭据和大文件二进制。
- 当行为变化时同步更新文档与配置脚本。

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit 基于开源库与服务构建，包括：
- FFmpeg 用于媒体处理
- Tornado 用于后端 API
- MoviePy 用于编辑流程
- OpenAI 模型用于 AI 辅助的流水线任务
- CJKWrap 与字幕流程中的多语言文本工具
