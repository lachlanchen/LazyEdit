[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>用於生成、字幕處理、元資料與可選發布的一體化 AI 視訊工作流程。</b>
  <br />
  <sub>上傳或生成 -> 轉錄 -> 翻譯/潤飾 -> 燒錄字幕 -> 字幕/關鍵影格 -> 元資料 -> 發布</sub>
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

LazyEdit 是一個端到端的 AI 輔助視訊工作流程，涵蓋創作、處理與可選發布。它整合了基於提示詞的生成（Stage A/B/C）、媒體處理 API、字幕渲染、關鍵影格文案生成，以及 AutoPublish 交接。

| 快速事實 | 值 |
| --- | --- |
| 📘 官方英文說明 | `README.md`（本檔案） |
| 🌐 多語言版本 | `i18n/README.*.md`（每個 README 頂部只保留一列語言導覽） |
| 🧠 後端入口點 | `app.py`（Tornado） |
| 🖥️ 前端應用 | `app/`（Expo web/mobile） |

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

LazyEdit 以 Tornado 後端（`app.py`）和 Expo 前端（`app/`）為核心建置。

> 注意：若倉庫或執行環境細節因電腦而異，請保留既有預設值，並透過環境變數覆蓋，而不是刪除機器特定的回退配置。

| 使用原因 | 實際效果 |
| --- | --- |
| 統一的操作流程 | 在同一流程中完成上傳、生成、重混與發布 |
| API-first 設計 | 易於腳本化，並可與其他工具整合 |
| Local-first 執行時 | 支援 tmux + 以服務為基礎的部署模式 |

| 步驟 | 發生的事情 |
| --- | --- |
| 1 | 上傳或生成影片 |
| 2 | 轉錄並可選擇翻譯字幕 |
| 3 | 按版面控制加入多語系字幕 |
| 4 | 生成關鍵影格、字幕與元資料 |
| 5 | 打包並可選擇透過 AutoPublish 發布 |

### Pipeline focus

- 在單一操作介面內完成上傳、生成、重混與素材庫管理。
- 採用 API-first 處理流程，涵蓋轉錄、字幕潤飾/翻譯、字幕燒錄與元資料。
- 可選接入生成服務提供者（`agi/` 下的 Veo / Venice / A2E / Sora 輔助程式）。
- 可選透過 `AutoPublish` 進行發布交接。

## 🎯 At a Glance

| 項目 | LazyEdit 是否包含 | 狀態 |
| --- | --- | --- |
| 核心應用 | Tornado API 後端 + Expo web/mobile 前端 | ✅ |
| 媒體流程 | ASR、字幕翻譯/潤飾、字幕燒錄、關鍵影格、字幕文案、元資料 | ✅ |
| 生成 | Stage A/B/C 與服務商路由（`agi/`） | ✅ |
| 發布 | 可選 AutoPublish 交接 | 🟡 可選 |
| 執行模式 | 本機優先腳本、tmux 工作流程、可選 systemd 服務 | ✅ |

## 🏗️ Architecture Snapshot

此倉庫採「具備 UI 層的 API-first 媒體流水線」組織：

- `app.py` 是 Tornado 入口與路由協調器，負責上傳、處理、生成、發布交接與媒體服務。
- `lazyedit/` 包含模組化流程組件（資料庫持久化、翻譯、字幕燒錄、字幕、元資料、服務商適配器）。
- `app/` 是 Expo Router 應用（web/mobile），驅動上傳、處理、預覽與發布流程。
- `config.py` 統一負責環境載入與預設/回退路徑。
- `start_lazyedit.sh` 與 `lazyedit_config.sh` 提供可重現的 tmux 本機/部署執行模式。

| 層級 | 主要路徑 | 職責 |
| --- | --- | --- |
| API 與編排 | `app.py`, `config.py` | 端點、路由、環境解析 |
| 處理核心 | `lazyedit/`, `agi/` | 字幕/字幕文案/元資料流程 + 服務商 |
| UI | `app/` | 操作體驗（透過 Expo 的 web/mobile） |
| 執行腳本 | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | 本機/服務啟動與維運 |

高層流程：

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

以下為從素材接收到元資料生成的主要操作路徑截圖。

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>主畫面 · 上傳</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>主畫面 · 生成</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>主畫面 · 重混</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>作品庫</sub>
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
      <br /><sub>字幕槽位</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>字幕版面</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>關鍵影格 + 字幕文案</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>元資料產生器</sub>
    </td>
  </tr>
</table>

## 🧩 Features

- ✨ 以提示詞驅動的生成流程（Stage A/B/C），包含 Sora 與 Veo 的整合路徑。
- 🧵 完整處理流程：轉錄 -> 字幕潤飾/翻譯 -> 燒錄字幕 -> 關鍵影格 -> 文案 -> 元資料。
- 🌏 多語系字幕編排，支援 furigana/IPA/romaji 相關路徑。
- 🔌 API-first 後端，提供上傳、處理、媒體服務與發布佇列端點。
- 🚚 可選整合 AutoPublish，用於社群平台發布交接。
- 🖥️ 透過 tmux 啟動腳本支援後端 + Expo 的一體化工作流程。

## 🌍 Documentation & i18n


- 官方來源：`README.md`
- 多語言版本：`i18n/README.*.md`
- 語言導覽：每個 README 頂部僅保留一行語言導覽（不可重複）

若英文 README 與譯文有差異，請以英文 README 為真實來源，並逐一更新各語言檔。

| i18n 政策 | 規則 |
| --- | --- |
| 官方來源 | 保持 `README.md` 為真實來源 |
| 語言導覽 | 每個 README 只保留一行語言選項 |

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
- 本倉庫的 Git 子模組包含 `AutoPublish`、`AutoPubMonitor`、`whisper_with_lang_detect`、`vit-gpt2-image-captioning`、`clip-gpt-captioning` 與 `furigana`。
- 運作指引將 `furigana` 和 `echomind` 視為外部相依；若不確定，請保留上游版本並避免在本倉庫直接修改。

## ✅ Prerequisites

| 依賴 | 說明 |
| --- | --- |
| Linux 環境 | `systemd`/`tmux` 腳本以 Linux 為導向 |
| Python 3.10+ | 使用 Conda 環境 `lazyedit` |
| Node.js 20+ + npm | `app/` 的 Expo 應用所需 |
| FFmpeg | 必須在 `PATH` 可用 |
| PostgreSQL | 本機 peer 驗證或 DSN-based 連線 |
| Git 子模組 | 核心流程所必需 |

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

3. 可選的系統層安裝（服務模式）：

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

服務安裝備註：
- `install_lazyedit.sh` 會安裝 `ffmpeg` 與 `tmux`，接著建立 `lazyedit.service`。
- 它不會建立 `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh`，這些需先存在並正確設定。

## ⚡ Quick Start

後端 + 前端本機啟動（最小路徑）：

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

在第二個 shell：

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

可選的本機資料庫初始化：

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| 本機開發（手動） | `python app.py` + Expo 命令 | `8787` | `8091`（示例命令） |
| Tmux 編排 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd 服務 | `sudo systemctl start lazyedit.service` | 由設定/環境決定 | N/A |

## 🧭 Command Cheat Sheet

| 任務 | 指令 |
| --- | --- |
| 初始化子模組 | `git submodule update --init --recursive` |
| 僅啟動後端 | `python app.py` |
| 啟動後端 + Expo（tmux） | `./start_lazyedit.sh` |
| 停止 tmux 執行 | `./stop_lazyedit.sh` |
| 連接 tmux 會話 | `tmux attach -t lazyedit` |
| 查詢服務狀態 | `sudo systemctl status lazyedit.service` |
| 查看服務日誌 | `sudo journalctl -u lazyedit.service` |
| DB 冒煙測試 | `python db_smoke_test.py` |
| Pytest 冒煙測試 | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### Development: backend only

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

部署腳本目前使用的備用入口：

```bash
python app.py -m lazyedit
```

後端預設網址：`http://localhost:8787`（來自 `config.py`，可透過 `PORT` 或 `LAZYEDIT_PORT` 覆蓋）。

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

`start_lazyedit.sh` 預設端口：
- 後端：`18787`
- Expo web：`18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

連接到會話：

```bash
tmux attach -t lazyedit
```

停止會話：

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

複製 `.env.example` 成 `.env` 並更新路徑/密鑰：

```bash
cp .env.example .env
```

設定優先順序：

- `config.py` 會讀取 `.env` 的值，且只會使用 shell 尚未匯出的鍵。
- 因此執行時值的來源是：shell 匯出的環境變數 -> `.env` -> 程式預設值。
- 對於 tmux/service 執行，`lazyedit_config.sh` 會控制啟動與會話參數（`LAZYEDIT_DIR`、`CONDA_ENV`、`APP_ARGS`、透過啟動腳本環境設定端口）。

### Key variables

| 變數 | 用途 | 預設 / 回退 |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | 後端端口 | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | 媒體根目錄 | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | 本機回退 `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish 端點 | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish 請求逾時（秒） | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD 腳本路徑 | 視環境而定 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR 模型名稱 | `large-v3` / `large-v2`（示例） |
| `LAZYEDIT_CAPTION_PYTHON` | 字幕流程使用的 Python 執行環境 | 視環境而定 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 主要字幕路徑/腳本 | 視環境而定 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 備援字幕腳本/工作目錄 | 視環境而定 |
| `GRSAI_API_*` | Veo/GRSAI 整合設定 | 視環境而定 |
| `VENICE_*`, `A2E_*` | Venice/A2E 整合設定 | 視環境而定 |
| `OPENAI_API_KEY` | OpenAI 驅動功能所需 | 未設定 |

機器特定備註：
- `app.py` 可能設置 CUDA 行為（參見程式碼中的 `CUDA_VISIBLE_DEVICES` 用法）。
- 部分預設路徑屬於工作站特定；如需可攜式環境請用 `.env` 覆蓋。
- `lazyedit_config.sh` 在部署腳本中負責控制 tmux/會話啟動變數。

## 🧾 Configuration Files

| 檔案 | 用途 |
| --- | --- |
| `.env.example` | 後端/服務使用的環境變數模板 |
| `.env` | 機器本地覆蓋；若存在則由 `config.py`/`app.py` 讀取 |
| `config.py` | 後端預設與環境解析 |
| `lazyedit_config.sh` | tmux/service 運行設定（部署路徑、conda env、app args、會話名稱） |
| `start_lazyedit.sh` | 依選定端口在 tmux 中啟動後端 + Expo |
| `install_lazyedit.sh` | 建立 `lazyedit.service` 並驗證現有腳本/設定 |

建議的可攜式更新順序：
1. 將 `.env.example` 複製到 `.env`。
2. 在 `.env` 中設定路徑與 API 相關的 `LAZYEDIT_*` 值。
3. 僅當 tmux/service 部署行為需要時，調整 `lazyedit_config.sh`。

## 🔌 API Examples

Base URL 示例預設為 `http://localhost:8787`。

| API 群組 | 代表性端點 |
| --- | --- |
| 上傳與媒體 | `/upload`, `/upload-stream`, `/media/*` |
| 影片紀錄 | `/api/videos`, `/api/videos/{id}` |
| 處理 | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| 發布 | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| 生成 | `/api/videos/generate`（加上 `app.py` 中的服務商路由） |

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

發布打包：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

更多端點與 payload 說明請參閱：`references/API_GUIDE.md`。

常用端點群組：
- 影片生命週期：`/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- 處理行為：`/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- 生成/provider 路徑：`/api/videos/generate` 以及 `app.py` 暴露的 Venice/A2E 路由
- 發布：`/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

如果後端位於 `8887`：

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

- 使用 `python`（Conda 環境 `lazyedit` 中）執行，不要假設系統中的 `python3`。
- 不要將大型媒體檔提交到 Git；請放在 `DATA/` 或外部儲存。
- 當流程元件無法解析時，請初始化或更新子模組。
- 保持修改範圍集中，避免不相關的大型格式化變更。
- 前端開發中，後端 API URL 由 `EXPO_PUBLIC_API_URL` 控制。
- 為了開發便利，後端 CORS 目前為開放狀態。

子模組與外部依賴政策：
- 將外部依賴視為上游專案。本倉庫工作流中請避免直接編輯子模組內部，除非你真正要在該專案中工作。
- 本倉庫運作指引將 `furigana`（以及某些本機環境中的 `echomind`）視為外部路徑；不確定時請保留上游並避免原地修改。

參考資源：
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

安全與設定衛生：
- 將 API 金鑰與憑證存於環境變數，不要提交憑證。
- 優先在 `.env` 中寫入機器本地覆蓋，並將 `.env.example` 保持為公開模板。
- 若 CUDA/GPU 行為因主機不同而異，請透過環境變數覆蓋，而非硬編碼機器值。

## ✅ Testing

目前正式的測試覆蓋有限，以資料庫導向為主。

| 驗證層級 | 指令或方法 |
| --- | --- |
| DB 冒煙測試 | `python db_smoke_test.py` |
| Pytest DB 檢查 | `pytest tests/test_db_smoke.py` |
| 功能流程 | 使用 `DATA/` 中短片樣本並透過 Web UI + API 執行 |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

功能驗證請使用 Web UI 與 API 流程，並以 `DATA/` 中的短樣本作驗證。

假設與可攜性說明：
- 程式碼中的部分預設路徑是工作站特定回退，這是目前倉庫狀態下可預期的行為。
- 若預設路徑在你的機器上不存在，請在 `.env` 中設定對應的 `LAZYEDIT_*` 變數。
- 若不確定某個機器特定值，請保留既有設定，並加入明確覆蓋而非刪除預設值。

## 🧱 Assumptions & Known Limits

- 後端依賴目前未以根鎖檔釘住，環境可重現性仍仰賴本機環境管理。
- `app.py` 在目前狀態下仍採較大的一體化路由結構。
- 大多數流程驗證仍為整合/手動（UI + API + 示例媒體），自動化測試相對有限。
- 運行目錄（`DATA/`、`temp/`、`translation_logs/`）是產物輸出目錄，體積可能快速成長。
- 全功能運作需要子模組；不完整的檢出常會導致缺少腳本錯誤。

## 🚢 Deployment & Sync Notes

目前已知的路徑與同步流程（來自倉庫運維文件）：

- 開發工作區：`/home/lachlan/ProjectsLFS/LazyEdit`
- 已部署 LazyEdit 後端 + 應用：`/home/lachlan/DiskMech/Projects/lazyedit`
- 已部署 AutoPubMonitor：`/home/lachlan/DiskMech/Projects/autopub-monitor`
- 發布系統主機：`/home/lachlan/Projects/auto-publish`（位於 `lazyingart`）

| 環境 | 路徑 | 說明 |
| --- | --- | --- |
| 開發工作區 | `/home/lachlan/ProjectsLFS/LazyEdit` | 主來源與子模組 |
| 已部署 LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | 運維文件中的 tmux 會話 `la-lazyedit` |
| 已部署 AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | monitor/sync/process 會話 |
| 發布主機 | `/home/lachlan/Projects/auto-publish`（`lazyingart`） | 子模組更新後請拉取 |

從本倉庫推送 `AutoPublish/` 更新後，請在發布主機執行：

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| 問題 | 檢查 / 修正 |
| --- | --- |
| 缺少流程模組或腳本 | 執行 `git submodule update --init --recursive` |
| 找不到 FFmpeg | 安裝 FFmpeg 並確認 `ffmpeg -version` 可執行 |
| 端口衝突 | 後端預設 `8787`，`start_lazyedit.sh` 預設 `18787`；可設定 `LAZYEDIT_PORT` 或 `PORT` |
| Expo 無法連到後端 | 確認 `EXPO_PUBLIC_API_URL` 指向目前可用的後端主機與端口 |
| 資料庫連線問題 | 檢查 PostgreSQL 與 DSN/環境變數；可選擇性執行 `python db_smoke_test.py` |
| GPU/CUDA 問題 | 確認驅動與 CUDA 與已安裝 Torch 版本的相容性 |
| 服務腳本安裝失敗 | 確認 `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` 在執行安裝前存在 |

## 🗺️ Roadmap

- 在應用內提供逐行可控的字幕/片段編輯，含 A/B 預覽。
- 為核心 API 流程補強更完整的端到端測試覆蓋。
- 推進 i18n README 在不同部署模式間的文件一致性。
- 加強生成服務商重試機制與狀態可見性。

## 🤝 Contributing

歡迎提交貢獻。

1. Fork 並建立 feature 分支。
2. 保持提交聚焦且範圍清楚。
3. 本地驗證變更（`python app.py`、核心 API 流程，必要時整合 app）。
4. 提交 PR 時附上目標、重現步驟與前後對照（UI 變更請附截圖）。

實務建議：
- 遵循 Python 風格（PEP 8、4 空格、snake_case 命名）。
- 避免提交憑證與大型二進位檔。
- 行為變更時同步更新文件與設定腳本。
- 建議的提交風格：短小、祈使式、聚焦（例如：`fix ffmpeg 7 compatibility`）。



## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit 建立於開源函式庫與服務之上，包括：
- FFmpeg 用於媒體處理
- Tornado 用於後端 API
- MoviePy 用於編輯流程
- OpenAI 模型用於 AI 輔助流程任務
- CJKWrap 與字幕流程中的多語言文本工具
