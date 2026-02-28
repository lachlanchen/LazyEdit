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

LazyEdit 是一套端到端、AI 辅助的视频工作流，覆盖创作、处理和可选发布。它结合了基于提示词的生成（Stage A/B/C）、媒体处理 API、字幕渲染、关键帧文案生成、元数据生成，以及 AutoPublish 交接。

## ✨ 概览

LazyEdit 围绕 Tornado 后端（`app.py`）和 Expo 前端（`app/`）构建。

| 步骤 | 执行内容 |
| --- | --- |
| 1 | 上传或生成视频 |
| 2 | 转写并可选翻译字幕 |
| 3 | 通过布局控制烧录多语言字幕 |
| 4 | 生成关键帧、文案和元数据 |
| 5 | 打包并可选通过 AutoPublish 发布 |

### 流水线重点

- 在统一操作 UI 中完成上传、生成、混剪与素材库管理。
- 以 API 为核心的处理流程：转写、字幕润色/翻译、烧录和元数据。
- 可选生成服务商集成（`agi/` 中的 Veo / Venice / A2E / Sora 辅助）。
- 可选通过 `AutoPublish` 完成发布交接。

## 🎯 一览

| 领域 | LazyEdit 内置内容 |
| --- | --- |
| 核心应用 | Tornado API 后端 + Expo Web/移动端前端 |
| 媒体流水线 | ASR、字幕翻译/润色、烧录、关键帧、文案、元数据 |
| 生成能力 | Stage A/B/C 与服务商辅助路由（`agi/`） |
| 分发 | 可选 AutoPublish 交接 |
| 运行模型 | 本地优先脚本、tmux 工作流、可选 systemd 服务 |

## 🎬 演示

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
      <br /><sub>烧录槽位</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>烧录布局</sub>
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

## 🧩 功能

- 基于提示词的生成工作流（Stage A/B/C），含 Sora 与 Veo 集成路径。
- 完整处理流水线：转写 -> 字幕润色/翻译 -> 烧录 -> 关键帧 -> 文案 -> 元数据。
- 多语言字幕编排，包含 furigana/IPA/romaji 相关支持路径。
- API 优先后端，提供上传、处理、媒体服务与发布队列端点。
- 可选 AutoPublish 集成，用于社交平台发布交接。
- 通过 tmux 启动脚本支持后端 + Expo 一体化工作流。

## 🗂️ 项目结构

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

## ✅ 前置依赖

| 依赖项 | 说明 |
| --- | --- |
| Linux 环境 | `systemd`/`tmux` 脚本面向 Linux |
| Python 3.10+ | 使用 Conda 环境 `lazyedit` |
| Node.js 20+ + npm | `app/` 中 Expo 应用所需 |
| FFmpeg | 必须可通过 `PATH` 调用 |
| PostgreSQL | 本地 peer auth 或基于 DSN 的连接 |
| Git submodules | 关键流水线需要 |

## 🚀 安装

1. 克隆仓库并初始化 submodules：

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

3. 可选系统级安装（服务模式）：

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

服务安装说明：
- `install_lazyedit.sh` 会安装 `ffmpeg` 与 `tmux`，并创建 `lazyedit.service`。
- 它不会生成 `lazyedit_config.sh`、`start_lazyedit.sh` 或 `stop_lazyedit.sh`；这些文件必须预先存在且配置正确。

## 🛠️ 使用

### 开发：仅后端

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

当前部署脚本中使用的备用入口：

```bash
python app.py -m lazyedit
```

后端默认 URL：`http://localhost:8787`（来自 `config.py`，可通过 `PORT` 或 `LAZYEDIT_PORT` 覆盖）。

### 开发：后端 + Expo 应用（tmux）

```bash
./start_lazyedit.sh
```

默认 `start_lazyedit.sh` 端口：
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

连接到会话：

```bash
tmux attach -t lazyedit
```

停止会话：

```bash
./stop_lazyedit.sh
```

### 服务管理

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ 配置

将 `.env.example` 复制为 `.env`，并更新路径/密钥：

```bash
cp .env.example .env
```

### 关键变量

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

机器相关说明：
- `app.py` 可能会设置 CUDA 行为（代码中涉及 `CUDA_VISIBLE_DEVICES` 的使用）。
- 某些默认路径与具体工作站有关；可使用 `.env` 覆盖以便跨机器部署。
- `lazyedit_config.sh` 控制部署脚本中的 tmux/会话启动变量。

## 🔌 API 示例

Base URL 示例假设为 `http://localhost:8787`。

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

发布包：

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

更多端点与 payload 细节见：`references/API_GUIDE.md`。

## 🧪 示例

### 前端本地运行（Web）

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

如果后端运行在 `8887`：

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android 模拟器

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS 模拟器（macOS）

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### 可选 Sora 生成辅助

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

支持时长：`4`、`8`、`12`。
支持分辨率：`720x1280`、`1280x720`、`1024x1792`、`1792x1024`。

## 🧪 开发说明

- 使用 Conda 环境 `lazyedit` 中的 `python`（不要假设系统 `python3`）。
- 大体积媒体文件不要提交到 Git；运行期媒体请放在 `DATA/` 或外部存储。
- 当流水线组件无法解析时，初始化/更新 submodules。
- 修改保持聚焦，避免无关的大规模格式化。
- 前端开发时，后端 API URL 由 `EXPO_PUBLIC_API_URL` 控制。
- 为了应用开发，后端 CORS 处于开放状态。

Submodule 与外部依赖策略：
- 将外部依赖视为上游维护。在本仓库工作流中，除非明确在对应项目内开发，否则避免修改 submodule 内部。
- 本仓库的操作指引将 `furigana`（以及部分本地环境中的 `echomind`）视为外部依赖路径；如不确定，请保留上游内容并避免原位修改。

有用参考：
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ 测试

当前正式测试覆盖较少，主要面向数据库。

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

功能验证建议通过 Web UI 与 API 流程，配合 `DATA/` 中的短视频样本完成。

## 🚢 部署与同步说明

当前已知路径与同步流程（来自仓库运维文档）：

- 开发工作区：`/home/lachlan/ProjectsLFS/LazyEdit`
- 已部署 LazyEdit backend + app：`/home/lachlan/DiskMech/Projects/lazyedit`
- 已部署 AutoPubMonitor：`/home/lachlan/DiskMech/Projects/autopub-monitor`
- 发布系统主机：`lazyingart` 上的 `/home/lachlan/Projects/auto-publish`

从本仓库推送 `AutoPublish/` 更新后，在发布主机执行拉取：

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 故障排查

| 问题 | 检查 / 修复 |
| --- | --- |
| 缺少流水线模块或脚本 | 运行 `git submodule update --init --recursive` |
| 找不到 FFmpeg | 安装 FFmpeg 并确认 `ffmpeg -version` 可用 |
| 端口冲突 | 后端默认 `8787`；`start_lazyedit.sh` 默认 `18787`；请显式设置 `LAZYEDIT_PORT` 或 `PORT` |
| Expo 无法连接后端 | 确认 `EXPO_PUBLIC_API_URL` 指向活动后端的 host/port |
| 数据库连接问题 | 检查 PostgreSQL 与 DSN/env 变量；可选冒烟检查：`python db_smoke_test.py` |
| GPU/CUDA 问题 | 确认驱动/CUDA 与已安装 Torch 栈兼容 |
| 服务安装脚本失败 | 运行安装器前确保 `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` 已存在 |

## 🗺️ 路线图

- 在应用内提供字幕/片段编辑，支持 A/B 预览与逐行控制。
- 为核心 API 流程提供更完整的端到端测试覆盖。
- 持续收敛 i18n README 版本与不同部署模式的文档一致性。
- 强化生成服务商重试机制与状态可见性。

## 🤝 贡献

欢迎贡献。

1. Fork 并创建功能分支。
2. 保持提交聚焦且范围清晰。
3. 在本地验证改动（`python app.py`、关键 API 流程，以及相关的 app 集成）。
4. 提交 PR 时附上目的、复现步骤和前后对比说明（UI 改动请附截图）。

实践指南：
- 遵循 Python 风格（PEP 8、4 空格、snake_case 命名）。
- 避免提交凭据或大体积二进制文件。
- 行为变化时同步更新文档/配置脚本。
- 推荐提交风格：简短、祈使句、范围明确（例如：`fix ffmpeg 7 compatibility`）。

## ❤️ 你的支持将带来

- <b>让工具保持开放</b>：用于托管、推理、数据存储与社区运营。  
- <b>更快交付</b>：投入数周专注开源开发 EchoMind、LazyEdit 与 MultilingualWhisper。  
- <b>可穿戴原型</b>：支持 IdeasGlass + LightMind 的光学、传感器与神经形态/边缘组件。  
- <b>惠及更多人</b>：为学生、创作者与社区团体提供补贴部署。

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

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 致谢

LazyEdit 构建于诸多开源库与服务之上，包括：
- FFmpeg（媒体处理）
- Tornado（后端 API）
- MoviePy（编辑工作流）
- OpenAI models（AI 辅助流水线任务）
- CJKWrap 与多语言文本工具链（字幕工作流）
