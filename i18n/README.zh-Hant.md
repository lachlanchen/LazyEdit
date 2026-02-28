[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>AI 輔助的影片工作流，整合生成、字幕處理、元資料與可選發佈。</b>
  <br />
  <sub>上傳或生成 -> 轉錄 -> 翻譯/潤飾 -> 燒錄字幕 -> 文案/關鍵影格 -> 元資料 -> 發佈</sub>
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

LazyEdit 是一套端對端 AI 輔助影片工作流，覆蓋內容創作、處理與可選發布。它整合了提示詞生成（Stage A/B/C）、媒體處理 API、字幕渲染、關鍵影格文案生成以及 AutoPublish 串接。

| 快速事實 | 數值 |
| --- | --- |
| 📘 官方英文文件 | `README.md`（本檔） |
| 🌐 語言版本 | `i18n/README.*.md`（每個 README 頂部僅保留一條語言導覽） |
| 🧠 後端入口 | `app.py`（Tornado） |
| 🖥️ 前端應用 | `app/`（Expo web/mobile） |
| 🧩 執行方式 | `python app.py`（手動）、`./start_lazyedit.sh`（tmux）、可選 `lazyedit.service` |
| 🎯 主要參考文件 | `README.md`、`references/QUICKSTART.md`、`references/API_GUIDE.md`、`references/APP_GUIDE.md` |

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

LazyEdit 以 Tornado 後端（`app.py`）與 Expo 前端（`app/`）為核心打造。

> 注意：若倉庫或執行時設定因機器而異，請保留既有預設值，並透過環境變數覆寫，不要刪除機器專屬的回退設定。

| 為何使用 | 實際效果 |
| --- | --- |
| 統一的操作流程 | 在同一流程中完成上傳、生成、重混與發布 |
| API 優先設計 | 易於腳本化，並可與其他工具整合 |
| 本機優先執行時 | 支援 tmux + 服務化部署模式 |

| 步驟 | 發生的事 |
| --- | --- |
| 1 | 上傳或生成影片 |
| 2 | 轉錄並可選翻譯字幕 |
| 3 | 依版面控制燒錄多語字幕 |
| 4 | 生成關鍵影格、字幕與元資料 |
| 5 | 打包並可選透過 AutoPublish 發布 |

### Pipeline focus

- 在單一操作介面完成上傳、生成、重混與素材庫管理。
- 採用 API 優先處理流程，覆蓋轉錄、字幕潤飾/翻譯、燒錄與元資料。
- 可選接入生成供應方（`agi/` 下的 Veo / Venice / A2E / Sora 助手）。
- 可選透過 `AutoPublish` 進行發布交接。

## 🎯 At a Glance

| 領域 | LazyEdit 內建 | 狀態 |
| --- | --- | --- |
| 核心應用 | Tornado API 後端 + Expo web/mobile 前端 | ✅ |
| 媒體流水線 | ASR、字幕翻譯/潤飾、燒錄、關鍵影格、文案、元資料 | ✅ |
| 生成 | Stage A/B/C 與供應方路由（`agi/`） | ✅ |
| 發佈 | 可選 AutoPublish 交接 | 🟡 Optional |
| 執行模型 | 本機優先腳本、tmux 工作流程、可選 systemd 服務 | ✅ |

## 🏗️ Architecture Snapshot

這個倉庫以「有 UI 層的 API-first 媒體流水線」方式組織：

- `app.py` 是 Tornado 入口與路由編排器，負責上傳、處理、生成、發布交接與媒體服務。
- `lazyedit/` 包含模組化流水線元件（資料庫持久化、翻譯、字幕燒錄、字幕、元資料、Provider 適配器）。
- `app/` 是 Expo Router 應用（web/mobile），用於上傳、處理、預覽與發布流程。
- `config.py` 統一處理環境變數載入與預設/回退路徑。
- `start_lazyedit.sh` 與 `lazyedit_config.sh` 提供可重現的 tmux 本機/部署執行模式。

| 層級 | 主要路徑 | 職責 |
| --- | --- | --- |
| API 與編排 | `app.py`, `config.py` | 介面、路由、環境變數解析 |
| 處理核心 | `lazyedit/`, `agi/` | 字幕/文案/元資料流水線 + Provider |
| UI | `app/` | 操作體驗（透過 Expo 的 web/mobile） |
| 執行腳本 | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 本機/服務啟動與維運 |

高層流程：

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

以下是從素材接入到元資料生成的主要操作路徑。

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>首頁 · 上傳</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>首頁 · 生成</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>首頁 · 重混</sub>
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
      <br /><sub>燒錄欄位</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>燒錄版面</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>關鍵影格 + 字幕</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>元資料生成器</sub>
    </td>
  </tr>
</table>

## 🧩 Features

- ✨ 基於提示詞的生成工作流程（Stage A/B/C），含 Sora 與 Veo 的整合路徑。
- 🧵 完整處理流水線：轉錄 -> 字幕潤飾/翻譯 -> 燒錄 -> 關鍵影格 -> 文案 -> 元資料。
- 🌏 多語言字幕編排，支援 furigana / IPA / romaji 相關鏈路。
- 🔌 API-first 後端，提供上傳、處理、媒體服務與發佈佇列介面。
- 🚚 可選串接 AutoPublish，用於社群平台發布交接。
- 🖥️ 透過 tmux 啟動腳本支援後端 + Expo 的整合工作流程。

## 🌍 Documentation & i18n

- 官方來源：`README.md`
- 多語言版本：`i18n/README.*.md`
- 語言導覽：每份 README 頂部僅保留一行語言選項（不得重複）
- 目前本倉庫包含語言：Arabic、German、English、Spanish、French、Japanese、Korean、Russian、Vietnamese、中文（簡體）、中文（繁體）

若翻譯與英文文件有差異，請以英文 README 作為事實來源，並逐一更新各語言檔。

| i18n 規範 | 規則 |
| --- | --- |
| 官方來源 | 保持 `README.md` 為事實來源 |
| 語言導覽 | 每個 README 頂部僅保留一行語言導覽 |

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

子模組 / 外部依賴說明：
- 本倉庫中的 Git 子模組包含 `AutoPublish`、`AutoPubMonitor`、`whisper_with_lang_detect`、`vit-gpt2-image-captioning`、`clip-gpt-captioning` 與 `furigana`。
- 本倉庫的作業指引會將 `furigana` 與 `echomind` 視為外部依賴；若有疑慮，請保留上游版本，避免在本倉庫直接修改。

## ✅ Prerequisites

| 依賴 | 說明 |
| --- | --- |
| Linux 環境 | `systemd` / `tmux` 腳本以 Linux 為導向 |
| Python 3.10+ | 使用 Conda 環境 `lazyedit` |
| Node.js 20+ + npm | `app/` 的 Expo 應用所需 |
| FFmpeg | 必須在 `PATH` 中可用 |
| PostgreSQL | 本機 peer 驗證或基於 DSN 的連線 |
| Git 子模組 | 核心流水線依賴 |

## 🚀 Installation

1. 克隆並初始化子模組：

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. 啟用 Conda 環境：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. 可選服務化安裝（systemd）：

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

服務安裝說明：
- `install_lazyedit.sh` 會安裝 `ffmpeg` 與 `tmux`，並建立 `lazyedit.service`。
- 它不會建立 `lazyedit_config.sh`、`start_lazyedit.sh` 或 `stop_lazyedit.sh`，這些檔案必須先存在且設定正確。

## ⚡ Quick Start

後端 + 前端本地最小啟動方式：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

在第二個終端機中：

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

可選的本地資料庫初始化：

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| 本機開發（手動） | `python app.py` + Expo 指令 | `8787` | `8091`（示例指令） |
| tmux 編排 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd 服務 | `sudo systemctl start lazyedit.service` | 由設定/環境決定 | N/A |

## 🧭 Command Cheat Sheet

| 任務 | 指令 |
| --- | --- |
| 初始化子模組 | `git submodule update --init --recursive` |
| 僅啟動後端 | `python app.py` |
| 啟動後端 + Expo（tmux） | `./start_lazyedit.sh` |
| 停止 tmux 執行 | `./stop_lazyedit.sh` |
| 進入 tmux 會話 | `tmux attach -t lazyedit` |
| 查詢服務狀態 | `sudo systemctl status lazyedit.service` |
| 查看服務日誌 | `sudo journalctl -u lazyedit.service` |
| 資料庫煙霧測試 | `python db_smoke_test.py` |
| Pytest 冒煙測試 | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### 僅後端開發

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

目前部署腳本使用的替代入口：

```bash
python app.py -m lazyedit
```

後端預設位址：`http://localhost:8787`（來自 `config.py`，可透過 `PORT` 或 `LAZYEDIT_PORT` 覆寫）。

### 後端 + Expo 應用（tmux）

```bash
./start_lazyedit.sh
```

`start_lazyedit.sh` 預設埠位：
- 後端：`18787`
- Expo Web：`18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

連線到會話：

```bash
tmux attach -t lazyedit
```

停止會話：

```bash
./stop_lazyedit.sh
```

### 服務管理

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Configuration

複製 `.env.example` 為 `.env` 後更新路徑與金鑰：

```bash
cp .env.example .env
```

設定優先順序說明：

- `config.py` 會載入 `.env` 的值，且不會覆寫 shell 已匯出的環境變數。
- 因此執行時值來源為：shell 匯出的環境變數 -> `.env` -> 程式預設值。
- 對於 tmux/service 執行，`lazyedit_config.sh` 控制啟動與會話參數（`LAZYEDIT_DIR`、`CONDA_ENV`、`APP_ARGS`，埠號由啟動腳本環境決定）。

### Key variables

| 變數 | 用途 | 預設值/回退 |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | 後端埠 | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | 媒體根目錄 | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | 本機回退 `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish 端點 | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish 請求逾時（秒） | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD 腳本路徑 | 視環境而定 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR 模型名稱 | `large-v3` / `large-v2`（示例） |
| `LAZYEDIT_CAPTION_PYTHON` | 字幕管線使用的 Python 執行環境 | 視環境而定 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 主要字幕路徑/腳本 | 視環境而定 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 備援字幕腳本/工作目錄 | 視環境而定 |
| `GRSAI_API_*` | Veo/GRSAI 整合設定 | 視環境而定 |
| `VENICE_*`, `A2E_*` | Venice/A2E 整合設定 | 視環境而定 |
| `OPENAI_API_KEY` | OpenAI 功能所需 | 未設定 |

機器相關說明：
- `app.py` 可能設定 CUDA 行為（參考程式碼中的 `CUDA_VISIBLE_DEVICES` 用法）。
- 某些預設路徑為工作站相關；若要行動版部署，請用 `.env` 覆寫。
- `lazyedit_config.sh` 負責部署腳本中的 tmux/會話啟動變數。

## 🧾 Configuration Files

| 檔案 | 用途 |
| --- | --- |
| `.env.example` | 後端/服務使用的環境變數範本 |
| `.env` | 本機本地覆蓋；若存在會被 `config.py`/`app.py` 讀取 |
| `config.py` | 後端預設值與環境變數解析 |
| `lazyedit_config.sh` | tmux/service 執行設定（部署路徑、conda 環境、應用參數、會話名稱） |
| `start_lazyedit.sh` | 在 tmux 中依指定埠啟動後端 + Expo |
| `install_lazyedit.sh` | 建立 `lazyedit.service` 並檢查現有腳本與設定 |

機器可攜性建議更新順序：
1. 複製 `.env.example` 到 `.env`。
2. 在 `.env` 設定路徑與 API 相關的 `LAZYEDIT_*` 值。
3. 僅在 tmux/service 部署行為需要時調整 `lazyedit_config.sh`。

## 🔌 API Examples

Base URL 示例預設 `http://localhost:8787`。

| API 群組 | 典型端點 |
| --- | --- |
| 上傳與媒體 | `/upload`, `/upload-stream`, `/media/*` |
| 影片紀錄 | `/api/videos`, `/api/videos/{id}` |
| 處理 | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| 發布 | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| 生成 | `/api/videos/generate`（加上 `app.py` 中的 provider 路由） |

上傳：

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

端到端處理：

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

列出影片：

```bash
curl http://localhost:8787/api/videos
```

發佈打包：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

更多端點與請求主體說明請見：`references/API_GUIDE.md`。

常用端點群組：
- 影片生命週期：`/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- 處理動作：`/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- 生成/provider 路徑：`/api/videos/generate` 及 `app.py` 暴露的 Venice/A2E 路由
- 發佈：`/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

若後端運行在 `8887`：

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

支援秒數：`4`、`8`、`12`。
支援尺寸：`720x1280`、`1280x720`、`1024x1792`、`1792x1024`。

## 🧪 Development Notes

- 使用 Conda 環境 `lazyedit` 中的 `python`，不要預設使用 `python3`。
- 請勿將大型媒體檔提交到 Git；請存放於 `DATA/` 或外部儲存。
- 當流水線元件無法解析時，初始化或更新子模組。
- 保持修改範圍集中，避免不相關的大型格式調整。
- 前端工作中，後端 API 位址由 `EXPO_PUBLIC_API_URL` 控制。
- 後端在開發階段對 CORS 開放。

子模組與外部依賴策略：
- 將外部依賴視為上游專案。在本倉庫工作流中，除非你要在該子專案內工作，否則請避免修改子模組內部。
- 本倉庫指引會將 `furigana`（以及部分本機環境中的 `echomind`）視為外部依賴路徑；若不確定，請保留上游並避免就地修改。

參考文件：
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

安全與設定規範：
- 將 API 金鑰與憑證放在環境變數，不要提交敏感資料。
- 優先在 `.env` 中放入機器本地覆蓋值，並保持 `.env.example` 作為公開範本。
- 若 CUDA/GPU 行為因主機不同而異，請透過環境變數覆寫，而非硬編碼機器值。

## ✅ Testing

目前正式測試覆蓋有限，主要為資料庫導向。

| 驗證層 | 指令或方法 |
| --- | --- |
| DB 冒煙測試 | `python db_smoke_test.py` |
| Pytest DB 檢查 | `pytest tests/test_db_smoke.py` |
| 功能流程 | 使用 `DATA/` 短樣本，透過 Web UI + API 跑一遍 |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

功能驗證請使用 web UI 與 API 流程，並搭配 `DATA/` 中的短樣本。

假設與可攜性說明：
- 部分程式中的預設路徑為工作站級回退，這是目前的預期行為。
- 若預設路徑在你的機器不存在，請在 `.env` 設定對應的 `LAZYEDIT_*` 變數。
- 若某個機器專屬值不確定，請保留既有設定並補上明確覆寫，不要刪除預設。

## 🧱 Assumptions & Known Limits

- 根環境目前未被鎖定；可重現性仍仰賴本機環境管理。
- `app.py` 在目前倉庫狀態下維持單體結構，包含大量路由。
- 大多數流程驗證為整合/手工驗證（UI + API + 範例媒體），正式自動化測試較少。
- 執行目錄（`DATA/`、`temp/`、`translation_logs/`）為輸出空間，大小可能快速成長。
- 子模組為完整功能所必需；僅部分檢出常導致缺少腳本的錯誤。

## 🚢 Deployment & Sync Notes

目前已知路徑與同步流程（來自倉庫作業文件）：

- 開發工作區：`/home/lachlan/ProjectsLFS/LazyEdit`
- 已部署 LazyEdit 後端 + 應用：`/home/lachlan/DiskMech/Projects/lazyedit`
- 已部署 AutoPubMonitor：`/home/lachlan/DiskMech/Projects/autopub-monitor`
- 發布系統主機：`/home/lachlan/Projects/auto-publish`（`lazyingart`）

| 環境 | 路徑 | 說明 |
| --- | --- | --- |
| 開發工作區 | `/home/lachlan/ProjectsLFS/LazyEdit` | 主源碼與子模組 |
| 已部署 LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | 運維文件中的 tmux 會話 `la-lazyedit` |
| 已部署 AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | monitor/sync/process 會話 |
| 發布主機 | `/home/lachlan/Projects/auto-publish`（`lazyingart`） | 子模組更新後請拉取 |

在本倉庫推送 `AutoPublish/` 更新後，於發布主機執行：

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| 問題 | 檢查 / 處理 |
| --- | --- |
| 缺少流水線模組或腳本 | 執行 `git submodule update --init --recursive` |
| FFmpeg 找不到 | 安裝 FFmpeg 並確認 `ffmpeg -version` 可執行 |
| 埠號衝突 | 後端預設 `8787`，`start_lazyedit.sh` 預設 `18787`，可明確設定 `LAZYEDIT_PORT` 或 `PORT` |
| Expo 無法連線後端 | 確保 `EXPO_PUBLIC_API_URL` 指向可用的後端 host/port |
| 資料庫連線問題 | 檢查 PostgreSQL 與 DSN/環境變數；可選執行 `python db_smoke_test.py` |
| GPU/CUDA 問題 | 驗證驅動與 CUDA 是否與已安裝的 Torch 版本相容 |
| 安裝服務腳本失敗 | 確保 `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` 在執行安裝前存在 |

## 🗺️ Roadmap

- 在應用內提供逐行控制的字幕/片段編輯，含 A/B 預覽。
- 為核心 API 流增強更完整的端到端測試覆蓋。
- 推進 i18n README 與部署模式文件的一致性。
- 加強生成供應方重試與狀態可見性的流程穩定性。

## 🤝 Contributing

歡迎貢獻。

1. Fork 並建立功能分支。
2. 保持提交聚焦且範圍清楚。
3. 本機驗證變更（`python app.py`、關鍵 API 流程、必要時串接 app）。
4. 提交 PR 時附上目的、重現步驟，以及前後對比（UI 變更請附圖）。

實務建議：
- 遵循 Python 樣式（PEP 8，4 空格，snake_case 命名）。
- 避免提交憑證與大型二進位檔。
- 行為變更時更新文件與設定腳本。

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit 是建立在多個開源函式庫與服務上，包含：
- FFmpeg 用於媒體處理
- Tornado 用於後端 API
- MoviePy 用於編輯流程
- OpenAI 模型用於 AI 輔助的流水線任務
- CJKWrap 與字幕流程中的多語言文字工具
