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

LazyEdit 是一套端到端、AI 輔助的影片工作流程，用於創作、處理與可選的發佈。它整合了以提示詞驅動的生成流程（Stage A/B/C）、媒體處理 API、字幕燒錄、關鍵影格字幕、後設資料生成，以及 AutoPublish 交接。

## ✨ 總覽

LazyEdit 以 Tornado 後端（`app.py`）與 Expo 前端（`app/`）為核心。

| 步驟 | 內容 |
| --- | --- |
| 1 | 上傳或生成影片 |
| 2 | 轉錄並可選翻譯字幕 |
| 3 | 以版面控制燒錄多語字幕 |
| 4 | 生成關鍵影格、字幕文案與後設資料 |
| 5 | 封裝並可選透過 AutoPublish 發佈 |

### Pipeline 重點

- 在單一操作介面完成上傳、生成、remix 與媒體庫管理。
- 以 API 為核心的處理流程：轉錄、字幕潤飾/翻譯、燒錄與後設資料生成。
- 可選的生成供應商整合（`agi/` 中的 Veo / Venice / A2E / Sora helpers）。
- 可選透過 `AutoPublish` 進行發佈交接。

## 🎯 快速一覽

| 區塊 | LazyEdit 內含內容 |
| --- | --- |
| 核心應用 | Tornado API 後端 + Expo Web/Mobile 前端 |
| 媒體流程 | ASR、字幕翻譯/潤飾、燒錄、關鍵影格、字幕文案、後設資料 |
| 生成 | Stage A/B/C 與供應商輔助路由（`agi/`） |
| 發佈 | 可選 AutoPublish 交接 |
| 執行模式 | 本機優先腳本、tmux 工作流、可選 systemd 服務 |

## 🎬 展示

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
      <br /><sub>首頁 · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>媒體庫</sub>
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
      <br /><sub>燒錄槽位</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>燒錄版面</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>關鍵影格 + 字幕文案</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>後設資料生成器</sub>
    </td>
  </tr>
</table>

## 🧩 功能

- 以提示詞驅動的生成流程（Stage A/B/C），含 Sora 與 Veo 整合路徑。
- 完整處理管線：轉錄 -> 字幕潤飾/翻譯 -> 燒錄 -> 關鍵影格 -> 字幕文案 -> 後設資料。
- 多語字幕組版，含 furigana/IPA/romaji 相關支援路徑。
- 以 API 為優先的後端，提供上傳、處理、媒體供應與發佈佇列端點。
- 可選 AutoPublish 整合，用於社群平台交接發佈。
- 以 tmux 啟動腳本支援後端 + Expo 的整合工作流。

## 🗂️ 專案結構

```text
LazyEdit/
├── app.py                           # Tornado 後端入口與 API 編排
├── app/                             # Expo 前端（web/mobile）
├── lazyedit/                        # 核心管線模組（翻譯、後設資料、燒錄器、DB、模板）
├── agi/                             # 生成供應商抽象層（Sora/Veo/A2E/Venice 路由）
├── DATA/                            # 執行期媒體輸入/輸出（此工作區為 symlink）
├── translation_logs/                # 翻譯紀錄
├── temp/                            # 執行期暫存檔
├── install_lazyedit.sh              # systemd 安裝器（預期 config/start/stop 腳本已存在）
├── start_lazyedit.sh                # 後端 + Expo 的 tmux 啟動器
├── stop_lazyedit.sh                 # tmux 停止輔助腳本
├── lazyedit_config.sh               # 部署/執行期 shell 設定
├── config.py                        # 環境/設定解析（port、path、autopublish URL）
├── .env.example                     # 環境覆寫模板
├── references/                      # 補充文件（API 指南、快速開始、部署說明）
├── AutoPublish/                     # Submodule（可選發佈管線）
├── AutoPubMonitor/                  # Submodule（監控/同步自動化）
├── whisper_with_lang_detect/        # Submodule（ASR/VAD）
├── vit-gpt2-image-captioning/       # Submodule（主要 captioner）
├── clip-gpt-captioning/             # Submodule（備援 captioner）
└── furigana/                        # 工作流程中的外部依賴（此 checkout 中為追蹤 submodule）
```

## ✅ 先決條件

| 依賴 | 說明 |
| --- | --- |
| Linux 環境 | `systemd`/`tmux` 腳本以 Linux 為主 |
| Python 3.10+ | 使用 Conda 環境 `lazyedit` |
| Node.js 20+ + npm | `app/` 中 Expo 應用所需 |
| FFmpeg | 必須可在 `PATH` 找到 |
| PostgreSQL | 本機 peer auth 或 DSN 連線 |
| Git submodules | 關鍵管線必需 |

## 🚀 安裝

1. Clone 並初始化 submodules：

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

3. 可選系統層安裝（服務模式）：

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

服務安裝說明：
- `install_lazyedit.sh` 會安裝 `ffmpeg` 和 `tmux`，並建立 `lazyedit.service`。
- 不會自動生成 `lazyedit_config.sh`、`start_lazyedit.sh` 或 `stop_lazyedit.sh`；這些檔案必須先存在且設定正確。

## 🛠️ 使用方式

### 開發：僅後端

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

目前部署腳本使用的替代入口：

```bash
python app.py -m lazyedit
```

後端預設 URL：`http://localhost:8787`（來自 `config.py`，可用 `PORT` 或 `LAZYEDIT_PORT` 覆寫）。

### 開發：後端 + Expo app（tmux）

```bash
./start_lazyedit.sh
```

`start_lazyedit.sh` 預設埠：
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

附加到 session：

```bash
tmux attach -t lazyedit
```

停止 session：

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

## ⚙️ 設定

將 `.env.example` 複製為 `.env` 並更新路徑/密鑰：

```bash
cp .env.example .env
```

### 主要變數

| 變數 | 用途 | 預設/回退值 |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | 後端埠 | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | 媒體根目錄 | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | 本機 DB 回退 `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish 端點 | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish 請求逾時（秒） | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD 腳本路徑 | 依環境而定 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR 模型名稱 | `large-v3` / `large-v2`（範例） |
| `LAZYEDIT_CAPTION_PYTHON` | 字幕文案管線的 Python 執行環境 | 依環境而定 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 主要 captioning 路徑/腳本 | 依環境而定 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 備援 captioning 路徑/腳本/cwd | 依環境而定 |
| `GRSAI_API_*` | Veo/GRSAI 整合設定 | 依環境而定 |
| `VENICE_*`, `A2E_*` | Venice/A2E 整合設定 | 依環境而定 |
| `OPENAI_API_KEY` | OpenAI 相關功能必需 | 無 |

機器特定注意事項：
- `app.py` 可能設定 CUDA 行為（程式碼脈絡中的 `CUDA_VISIBLE_DEVICES` 用法）。
- 部分預設路徑依工作站而定；可用 `.env` 覆寫以提高可攜性。
- `lazyedit_config.sh` 控制部署腳本的 tmux/session 啟動變數。

## 🔌 API 範例

Base URL 範例假設為 `http://localhost:8787`。

Upload:

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

發佈封包：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

更多端點與 payload 細節：`references/API_GUIDE.md`。

## 🧪 範例

### 前端本機執行（web）

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

若後端在 `8887`：

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android 模擬器

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS 模擬器（macOS）

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### 可選 Sora 生成輔助

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

支援秒數：`4`、`8`、`12`。
支援尺寸：`720x1280`、`1280x720`、`1024x1792`、`1792x1024`。

## 🧪 開發備註

- 使用 Conda 環境 `lazyedit` 的 `python`（不要假設系統 `python3`）。
- 大型媒體請勿放入 Git；執行期媒體請放在 `DATA/` 或外部儲存。
- 當管線元件無法解析時，請初始化/更新 submodules。
- 變更請保持聚焦，避免無關的大範圍格式化修改。
- 前端開發時，後端 API URL 由 `EXPO_PUBLIC_API_URL` 控制。
- 為了 app 開發，後端 CORS 為開放設定。

Submodule 與外部依賴政策：
- 將外部依賴視為上游擁有。在本倉庫工作流中，除非你明確在維護那些專案，否則避免修改 submodule 內部。
- 此倉庫的操作指引將 `furigana`（以及部分本機環境中的 `echomind`）視為外部依賴路徑；若不確定，請保留上游內容並避免原地修改。

有用參考：
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ 測試

目前正式測試覆蓋面仍較少，且以 DB 相關為主。

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

功能驗證建議使用 web UI 與 API 流程，搭配 `DATA/` 中的短片樣本。

## 🚢 部署與同步說明

目前已知路徑與同步流程（來自倉庫操作文件）：

- 開發工作區：`/home/lachlan/ProjectsLFS/LazyEdit`
- 已部署的 LazyEdit backend + app：`/home/lachlan/DiskMech/Projects/lazyedit`
- 已部署的 AutoPubMonitor：`/home/lachlan/DiskMech/Projects/autopub-monitor`
- 發佈系統主機：`lazyingart` 上的 `/home/lachlan/Projects/auto-publish`

在此倉庫推送 `AutoPublish/` 更新後，請在發佈主機拉取：

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 疑難排解

| 問題 | 檢查 / 修復 |
| --- | --- |
| 缺少管線模組或腳本 | 執行 `git submodule update --init --recursive` |
| 找不到 FFmpeg | 安裝 FFmpeg，並確認 `ffmpeg -version` 可正常執行 |
| 埠衝突 | 後端預設 `8787`；`start_lazyedit.sh` 預設 `18787`；請明確設定 `LAZYEDIT_PORT` 或 `PORT` |
| Expo 無法連到後端 | 確認 `EXPO_PUBLIC_API_URL` 指向有效的後端 host/port |
| 資料庫連線問題 | 檢查 PostgreSQL + DSN/env vars；可選 smoke check：`python db_smoke_test.py` |
| GPU/CUDA 問題 | 確認驅動/CUDA 與已安裝 Torch 堆疊相容 |
| 服務安裝時腳本失敗 | 執行安裝器前，先確認 `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` 已存在 |

## 🗺️ 路線圖

- App 內字幕/片段編輯，包含 A/B 預覽與逐行控制。
- 為核心 API 流程補強端到端測試覆蓋率。
- 持續整合 i18n README 與各部署模式文件。
- 強化生成供應商重試機制與狀態可視化工作流。

## 🤝 貢獻

歡迎貢獻。

1. Fork 並建立功能分支。
2. 讓 commit 保持聚焦且範圍明確。
3. 在本機驗證變更（`python app.py`、主要 API 流程，以及必要時的 app 整合）。
4. 提交 PR，附上目的、重現步驟與前後差異說明（UI 變更請附截圖）。

實務準則：
- 遵循 Python 風格（PEP 8、4 spaces、snake_case 命名）。
- 避免提交憑證或大型二進位檔。
- 當行為變更時，請同步更新文件/設定腳本。
- 建議 commit 風格：簡短、祈使句、範圍明確（例如：`fix ffmpeg 7 compatibility`）。

## ❤️ 你的支持能帶來什麼

- <b>讓工具保持開放</b>：支撐託管、推論、資料儲存與社群營運。  
- <b>加速開發</b>：投入數週專注的開源時間到 EchoMind、LazyEdit 與 MultilingualWhisper。  
- <b>原型穿戴裝置</b>：支援 IdeasGlass + LightMind 的光學、感測器與類神經形態/邊緣元件。  
- <b>普及可近性</b>：為學生、創作者與社群團體提供補助部署。

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

## 📄 授權條款

[Apache-2.0](LICENSE)

## 🙏 致謝

LazyEdit 建立在多個開源函式庫與服務之上，包括：
- FFmpeg（媒體處理）
- Tornado（後端 API）
- MoviePy（編輯工作流）
- OpenAI models（AI 輔助管線任務）
- CJKWrap 與多語文字工具（字幕工作流）
