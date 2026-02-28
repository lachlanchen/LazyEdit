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
  <b>用於生成、字幕處理、元資料和可選發布的一體化 AI 視訊工作流程。</b>
  <br />
  <sub>上傳或生成 -> 轉錄 -> 翻譯/潤飾 -> 燒錄字幕 -> 關鍵影格/文案 -> 元資料 -> 發布</sub>
</p>

# LazyEdit

LazyEdit 是一個端對端的 AI 輔助影像工作流程，涵蓋創作、處理與可選發布。它整合了以提示詞驅動的生成（Stage A/B/C）、媒體處理 API、字幕渲染、關鍵影格文案、元資料生成，以及 AutoPublish 交接。

| Quick fact | Value |
| --- | --- |
| 📘 Canonical README | `README.md`（本檔案） |
| 🌐 Language variants | `i18n/README.*.md`（每份 README 頂部保留單一語言列） |
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

LazyEdit 以 Tornado 後端（`app.py`）與 Expo 前端（`app/`）為核心。

> 注意：若不同主機上的 repo 或執行環境細節有差異，請保留現有預設值，並透過環境變數覆寫，而非刪除機器專用的回退設定。

| Why teams use it | Practical result |
| --- | --- |
| 統一的操作流程 | 從單一流程完成上傳、生成、混剪與發布 |
| API-first 設計 | 更容易腳本化，並可整合其他工具 |
| Local-first 運行時 | 搭配 tmux 與服務化部署模式可順利運作 |

| Step | What happens |
| --- | --- |
| 1 | 上傳或生成影片 |
| 2 | 轉錄並可選擇翻譯字幕 |
| 3 | 使用版面控制燒錄多語字幕 |
| 4 | 生成關鍵影格、文案與元資料 |
| 5 | 打包後可選透過 AutoPublish 發布 |

### Pipeline focus

- 從同一操作介面完成上傳、生成、混剪與素材庫管理。
- 採用 API-first 流程處理轉錄、字幕潤飾/翻譯、燒錄與元資料。
- 可選的生成供應商整合（`agi/` 中包含 Veo / Venice / A2E / Sora 輔助路徑）。
- 可選的 AutoPublish 發布交接。

## 🎯 At a Glance

| Area | Included in LazyEdit | Status |
| --- | --- | --- |
| 核心應用 | Tornado API 後端 + Expo web/mobile 前端 | ✅ |
| 媒體管線 | ASR、字幕翻譯/潤飾、燒錄、關鍵影格、文案、元資料 | ✅ |
| 生成 | Stage A/B/C 與供應商路由（`agi/`） | ✅ |
| 發布 | 可選 AutoPublish 交接 | 🟡 可選 |
| 運行模型 | 本機優先腳本、tmux 工作流、可選 systemd 服務 | ✅ |

## 🏗️ Architecture Snapshot

本儲存庫以 API-first 的媒體管線搭配 UI 層組織：

- `app.py` 是 Tornado 入口與路由編排者，負責上傳、處理、生成、發布交接與媒體服務。
- `lazyedit/` 包含模組化的流程元件（資料庫持久化、翻譯、字幕燒錄、文案、元資料、供應商轉接器）。
- `app/` 是一個 Expo Router 應用（web/mobile），提供上傳、處理、預覽與發布流程。
- `config.py` 統一負責環境變數載入與預設/回退路徑。
- `start_lazyedit.sh` 與 `lazyedit_config.sh` 提供可重現的 tmux 本機／部署執行模式。

| Layer | Main paths | Responsibility |
| --- | --- | --- |
| API 與編排 | `app.py`, `config.py` | 介面、路由、環境變數解析 |
| 處理核心 | `lazyedit/`, `agi/` | 字幕/文案/元資料管線 + 供應商 |
| UI | `app/` | 操作者體驗（透過 Expo 的 web/mobile） |
| 運行腳本 | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 本機／服務啟動與維運 |

高層流程：

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

以下截圖示範了從素材接收至元資料生成的主要操作路徑。

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>主頁 · 上傳</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>主頁 · 生成</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>主頁 · 混剪</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>素材庫</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>影片總覽</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>翻譯預覽</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>燒錄位置</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>燒錄版面</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>關鍵影格 + 文案</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>元資料生成器</sub>
    </td>
  </tr>
</table>

## 🧩 Features

- ✨ 以提示詞為主的生成工作流程（Stage A/B/C），整合了 Sora 與 Veo 的串接路徑。
- 🧵 完整處理管線：轉錄 -> 字幕潤飾/翻譯 -> 燒錄 -> 關鍵影格 -> 文案 -> 元資料。
- 🌏 多語字幕組裝並支援 furigana / IPA / romaji 相關處理路徑。
- 🔌 API-first 後端，提供上傳、處理、媒體服務與發布佇列介面。
- 🚚 可選整合 AutoPublish，用於社群平台交接。
- 🖥️ 透過 tmux 啟動腳本，同時支援後端與 Expo 一體化工作流程。

## 🌍 Documentation & i18n

LazyEdit 保留一份正規英文 README（`README.md`）與 `i18n/` 下的多語版本。

- Canonical source: `README.md`
- Language variants: `i18n/README.*.md`
- Language bar: 每份 README 僅保留一組語言選擇列（不重複）

若翻譯版與英文文件出現不一致，請以英文 README 為真實來源，並逐一更新每個 `i18n/README.*.md`。

| i18n policy | Rule |
| --- | --- |
| Canonical source | 以 `README.md` 為真實來源 |
| Language bar | 每份 README 僅保留單一語言導航列 |
| Update order | 先英文，再逐一更新每個 `i18n/README.*.md` |

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
├── stop_lazyedit.sh                 # tmux stop helper
├── lazyedit_config.sh               # Deployment/runtime shell config
├── config.py                        # Environment/config resolution (ports, paths, autopublish URL)
├── .env.example                     # Environment override template
├── references/                      # Additional docs (API guide, quickstart, deployment notes)
├── AutoPublish/                     # Submodule (optional publishing pipeline)
├── AutoPubMonitor/                  # Submodule (monitor/sync automation)
├── whisper_with_lang_detect/        # Submodule (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule (primary captioner)
```

Submodule/external dependency note:
- 本 repo 的 Git submodule 包含 `AutoPublish`、`AutoPubMonitor`、`whisper_with_lang_detect`、`vit-gpt2-image-captioning`、`clip-gpt-captioning` 與 `furigana`。
- 運行規範中將 `furigana` 與 `echomind` 視為外部唯讀依賴。若不確定，請保留上游原樣並避免在原處直接編輯。

## ✅ Prerequisites

| Dependency | Notes |
| --- | --- |
| Linux environment | `systemd` / `tmux` 腳本以 Linux 為主 |
| Python 3.10+ | 使用 Conda 環境 `lazyedit` |
| Node.js 20+ + npm | `app/` 需要，用於 Expo 應用 |
| FFmpeg | 必須可在 `PATH` 取得 |
| PostgreSQL | 本機 peer auth 或 DSN 連線 |
| Git submodules | 核心流程需完整子模組 |

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
- `install_lazyedit.sh` 會安裝 `ffmpeg` 與 `tmux`，並建立 `lazyedit.service`。
- 它不會建立 `lazyedit_config.sh`、`start_lazyedit.sh` 或 `stop_lazyedit.sh`；這些檔案必須已存在且正確。

## ⚡ Quick Start

Backend + frontend 本機執行（最簡流程）：

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
| 本機開發（手動） | `python app.py` + Expo 指令 | `8787` | `8091`（示例指令） |
| tmux 編排 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd service | `sudo systemctl start lazyedit.service` | 依據設定與環境 | N/A |

## 🧭 Command Cheat Sheet

| Task | Command |
| --- | --- |
| 初始化 submodule | `git submodule update --init --recursive` |
| 只啟動後端 | `python app.py` |
| 同時啟動後端與 Expo（tmux） | `./start_lazyedit.sh` |
| 停止 tmux 執行 | `./stop_lazyedit.sh` |
| 進入 tmux session | `tmux attach -t lazyedit` |
| 服務狀態 | `sudo systemctl status lazyedit.service` |
| 服務日誌 | `sudo journalctl -u lazyedit.service` |
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

後端預設位址： `http://localhost:8787`（可於 `config.py` 中調整，或以 `PORT`/`LAZYEDIT_PORT` 覆寫）。

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

`start_lazyedit.sh` 預設連接埠：
- Backend：`18787`
- Expo web：`18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

連接到 session：

```bash
tmux attach -t lazyedit
```

停止 session：

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

複製 `.env.example` 為 `.env` 並更新路徑/密鑰：

```bash
cp .env.example .env
```

Configuration precedence note:

- 若 `.env` 存在，`config.py` 會載入其值，且只會覆寫 shell 中尚未設定的鍵。
- 因此執行時可來自：已匯出的環境變數 -> `.env` -> 代碼預設值。
- 對於 tmux / service 模式，`lazyedit_config.sh` 會控制啟動與 session 參數（`LAZYEDIT_DIR`、`CONDA_ENV`、`APP_ARGS`、以及由啟動腳本控制的連接埠）。

### Key variables

| Variable | Purpose | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | 後端連接埠 | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | 媒體根目錄 | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | 預設本機 DB `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish endpoint | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish 請求逾時（秒） | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD 腳本路徑 | 依主機環境 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR 模型名稱 | `large-v3` / `large-v2`（示例） |
| `LAZYEDIT_CAPTION_PYTHON` | 文案管線所用 Python 執行檔 | 依主機環境 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 主要文案腳本路徑/腳本 | 依主機環境 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 備用文案腳本路徑/工作目錄 | 依主機環境 |
| `GRSAI_API_*` | Veo/GRSAI 整合設定 | 依主機環境 |
| `VENICE_*`, `A2E_*` | Venice/A2E 整合設定 | 依主機環境 |
| `OPENAI_API_KEY` | OpenAI 功能所需 | 無預設 |

Machine-specific notes:
- `app.py` 可能會設定 CUDA 行為（程式碼上下文中的 `CUDA_VISIBLE_DEVICES`）。
- 有些預設路徑是特定工作站專用；可透過 `.env` 覆寫以提高可攜性。
- `lazyedit_config.sh` 控制部署腳本的 tmux/session 啟動變數。

## 🧾 Configuration Files

| File | Purpose |
| --- | --- |
| `.env.example` | 提供後端/服務使用的環境變數樣板 |
| `.env` | 本機覆寫；若存在，會被 `config.py`/`app.py` 載入 |
| `config.py` | 後端預設與環境解析 |
| `lazyedit_config.sh` | tmux/服務執行環境設定（部署路徑、conda 環境、app args、session 名稱） |
| `start_lazyedit.sh` | 以 tmux 啟動後端與 Expo 並指定連接埠 |
| `install_lazyedit.sh` | 建立 `lazyedit.service`，並驗證既有腳本／設定 |

Recommended update order for machine portability:
1. Copy `.env.example` to `.env`。
2. 在 `.env` 中設定與路徑、API 相關的 `LAZYEDIT_*` 值。
3. 僅於 tmux/service 部署行為上調整 `lazyedit_config.sh`。

## 🔌 API Examples

Base URL examples assume `http://localhost:8787`.

| API group | Representative endpoints |
| --- | --- |
| 上傳與媒體 | `/upload`, `/upload-stream`, `/media/*` |
| 影片記錄 | `/api/videos`, `/api/videos/{id}` |
| 處理 | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| 發布 | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| 生成 | `/api/videos/generate`（加上 `app.py` 中的供應商路徑） |

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

- 使用 Conda 環境 `lazyedit` 的 `python`（不要假設有系統 `python3`）。
- 請勿將大型媒體檔加入 Git；請將運行中媒體存放於 `DATA/` 或外部儲存。
- 當管線組件無法解析時，請初始化或更新 submodule。
- 保持變更範圍聚焦，避免進行不相關的大規模格式調整。
- 前端開發時，後端 API URL 由 `EXPO_PUBLIC_API_URL` 控制。
- CORS 在後端為開發開啟。

Submodule and external dependency policy:
- 外部依賴視為上游負責。在本 repo 的工作流程中，除非明確要修改對應專案，否則避免編輯 submodule 內部。
- 本 repo 的運作指引將 `furigana`（以及某些本機環境中的 `echomind`）視為外部依賴路徑；若不確定，請保留上游並避免就地修改。

Helpful references:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Security/config hygiene:
- 將 API key 與密鑰留在環境變數，不要提交機密。
- 推薦使用 `.env` 進行機器特有覆寫，並保留 `.env.example` 作為公開範本。
- 若不同主機的 CUDA/GPU 行為不同，請用環境變數覆寫，而非硬編碼機器特有值。

## ✅ Testing

目前正式測試面很小，且偏向資料庫。

| Validation layer | Command or method |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | 以短片段素材在 `DATA/` 透過 Web UI 與 API 執行 |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

功能驗證請使用 Web UI 與 API 流程，並以 `DATA/` 中的短片段樣本為主。

Assumptions and portability notes:
- 一些程式中的預設路徑仍是特定工作站回退值，這是目前 repo 的現況。
- 若預設路徑在你的環境不存在，請在 `.env` 中設定對應 `LAZYEDIT_*` 變數。
- 對於不確定的機器專用值，保留原有設定並加上明確覆寫，而不是刪除預設值。

## 🧱 Assumptions & Known Limits

- 後端相依套件未在 repo 根目錄鎖檔；環境可重現性目前仍依賴本機安裝的一致性。
- 目前 `app.py` 在 repo 中是故意集中式（monolithic）設計，且包含大量路由邏輯。
- 多數流程驗證為整合/手動測試（UI + API + 範例媒體），正式自動化測試有限。
- 運行目錄（`DATA/`、`temp/`、`translation_logs/`）會產生大量輸出檔，可快速增長。
- submodule 為完整功能所必須；若只做部分 checkout 常見缺少腳本錯誤。

## 🚢 Deployment & Sync Notes

Current known paths and sync flow (from repository operations docs):

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` on `lazyingart`

| Environment | Path | Notes |
| --- | --- | --- |
| 開發工作區 | `/home/lachlan/ProjectsLFS/LazyEdit` | 主來源與 submodule |
| 已部署 LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | ops 文件中的 tmux `la-lazyedit` |
| 已部署 AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | 監控 / 同步 / 處理 sessions |
| 發布主機 | `/home/lachlan/Projects/auto-publish`（`lazyingart`） | 更新 AutoPublish 後請 pull |

After pushing `AutoPublish/` updates from this repo, pull on publishing host:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| Problem | Check / Fix |
| --- | --- |
| 缺少管線模組或腳本 | 執行 `git submodule update --init --recursive` |
| 找不到 FFmpeg | 安裝 FFmpeg 並確認 `ffmpeg -version` 可執行 |
| 連接埠衝突 | 後端預設 `8787`；`start_lazyedit.sh` 預設 `18787`；請明確設定 `LAZYEDIT_PORT` 或 `PORT` |
| Expo 無法連到後端 | 確保 `EXPO_PUBLIC_API_URL` 指向正在執行的後端主機與連接埠 |
| 資料庫連線問題 | 檢查 PostgreSQL 與 DSN/環境變數；可選擇進行 smoke check：`python db_smoke_test.py` |
| GPU/CUDA 問題 | 確認驅動與已安裝 Torch 的 CUDA 相容性 |
| 服務腳本安裝失敗 | 確認 `lazyedit_config.sh`、`start_lazyedit.sh` 與 `stop_lazyedit.sh` 於執行安裝前皆已存在 |

## 🗺️ Roadmap

- 內建字幕/分段編輯，提供 A/B 預覽與逐行控制。
- 加強核心 API 流的端到端測試覆蓋。
- 推進各語系 README 與部署模式文件的一致化。
- 增補生成供應商重試與狀態可見性的流程強化。

## 🤝 Contributing

歡迎參與貢獻。

1. Fork 並建立 feature branch。
2. 保持 commit 內容專注且範圍清晰。
3. 在本機驗證變更（`python app.py`、關鍵 API 流、必要時 app 串接）。
4. 提交 PR 時需包含目的、重現步驟與前後比較（UI 變更請附截圖）。

Practical guidelines:
- 依照 Python 風格（PEP 8、4 空格縮排、snake_case 命名）開發。
- 避免提交憑證或大型二進位檔。
- 行為變更時同步更新文件與設定。
- 建議 commit 訊息風格：簡短、祈使語、範圍明確（例如：`fix ffmpeg 7 compatibility`）。

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit 建立於以下開源函式庫與服務之上：
- FFmpeg：媒體處理
- Tornado：後端 API
- MoviePy：剪輯工作流程
- OpenAI models：AI 輔助流程任務
- CJKWrap 與多語文字工具：字幕流程
