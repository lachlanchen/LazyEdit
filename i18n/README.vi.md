[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>AI-assisted video workflow</b> để tạo nội dung, xử lý phụ đề, metadata và xuất bản tùy chọn.
  <br />
  <sub>Tải lên hoặc tạo mới -> phiên âm -> dịch/chỉnh sửa -> đốt phụ đề -> keyframes/chú thích -> metadata -> xuất bản</sub>
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

LazyEdit là quy trình làm việc video end-to-end có hỗ trợ AI cho khâu tạo nội dung, xử lý và xuất bản tùy chọn. Nó kết hợp sinh nội dung theo prompt (Stage A/B/C), các API xử lý media, render phụ đề, keyframe captioning, sinh metadata, và bước bàn giao AutoPublish.

| Quick fact | Value |
| --- | --- |
| 📘 Canonical README | `README.md` (file này) |
| 🌐 Language variants | `i18n/README.*.md` (mỗi file README chỉ giữ một dòng lựa chọn ngôn ngữ ở đầu) |
| 🧠 Backend entrypoint | `app.py` (Tornado) |
| 🖥️ Frontend app | `app/` (Expo web/mobile) |
| 🧩 Runtime styles | `python app.py` (manual), `./start_lazyedit.sh` (tmux), tùy chọn `lazyedit.service` |
| 🎯 Primary references | `README.md`, `references/QUICKSTART.md`, `references/API_GUIDE.md`, `references/APP_GUIDE.md` |

## 🧭 Contents

- [Tổng quan](#overview)
- [Thông tin nhanh](#-quick-facts)
- [Nhìn nhanh](#at-a-glance)
- [Kiến trúc tổng quan](#architecture-snapshot)
- [Demos](#demos)
- [Tính năng](#features)
- [Tài liệu & i18n](#-documentation--i18n)
- [Cấu trúc dự án](#project-structure)
- [Yêu cầu ban đầu](#prerequisites)
- [Cài đặt](#installation)
- [Khởi động nhanh](#quick-start)
- [Bảng lệnh nhanh](#-command-cheat-sheet)
- [Cách dùng](#usage)
- [Cấu hình](#️-configuration)
- [Tệp cấu hình](#-configuration-files)
- [Ví dụ API](#api-examples)
- [Ví dụ](#examples)
- [Ghi chú phát triển](#development-notes)
- [Kiểm thử](#testing)
- [Giả định & giới hạn đã biết](#-assumptions--known-limits)
- [Triển khai & đồng bộ](#deployment--sync-notes)
- [Xử lý sự cố](#troubleshooting)
- [Lộ trình](#roadmap)
- [Đóng góp](#contributing)
- [Hỗ trợ](#-support)
- [Giấy phép](#license)
- [Lời cảm ơn](#acknowledgements)

## ✨ Overview

LazyEdit được xây dựng quanh backend Tornado (`app.py`) và frontend Expo (`app/`).

> Lưu ý: Nếu chi tiết repository/runtime khác theo máy, giữ nguyên giá trị mặc định hiện có và ghi đè bằng biến môi trường thay vì xóa fallback theo từng máy.

| Why teams use it | Practical result |
| --- | --- |
| Unified operator flow | Tải lên/tạo mới/remix/xuất bản từ cùng một workflow |
| API-first design | Dễ viết script và tích hợp với các công cụ khác |
| Local-first runtime | Hoạt động tốt với tmux + các mẫu triển khai service |

| Step | What happens |
| --- | --- |
| 1 | Tải lên hoặc tạo video |
| 2 | Phiên âm và tùy chọn dịch phụ đề |
| 3 | Đốt phụ đề đa ngôn ngữ với điều khiển layout |
| 4 | Sinh keyframes, captions và metadata |
| 5 | Đóng gói và tùy chọn xuất bản qua AutoPublish |

### Pipeline focus

- Tải lên, tạo mới, remix và quản lý thư viện từ một UI vận hành duy nhất.
- Dòng xử lý API-first cho transcription, polish/translate phụ đề, burn-in, và metadata.
- Tích hợp tùy chọn nhà cung cấp generation (`agi/`) cho Veo / Venice / A2E / helpers Sora.
- Bàn giao xuất bản tùy chọn qua `AutoPublish`.

## 🎯 At a Glance

| Area | Included in LazyEdit | Status |
| --- | --- | --- |
| Core app | Backend API Tornado + frontend Expo web/mobile | ✅ |
| Media pipeline | ASR, dịch/chỉnh sửa phụ đề, burn-in, keyframes, captions, metadata | ✅ |
| Generation | Stage A/B/C và route trợ giúp provider (`agi/`) | ✅ |
| Distribution | Handoff AutoPublish tùy chọn | 🟡 Tùy chọn |
| Runtime model | Script local-first, workflow tmux, service systemd tùy chọn | ✅ |

## 🏗️ Architecture Snapshot

Kho mã này được tổ chức như một media pipeline theo hướng API-first với lớp UI:

- `app.py` là điểm vào của Tornado và bộ điều phối route cho upload, processing, generation, bàn giao publish, và phục vụ media.
- `lazyedit/` chứa các khối pipeline module hóa (lưu trữ DB, translation, subtitle burn-in, captions, metadata, adapter provider).
- `app/` là ứng dụng Expo Router (web/mobile) điều phối upload, processing, preview, và publish.
- `config.py` gom cơ chế load environment và giải quyết đường dẫn mặc định.
- `start_lazyedit.sh` và `lazyedit_config.sh` cung cấp chế độ chạy local/deployed tái tạo được dựa trên tmux.

| Layer | Main paths | Responsibility |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | Endpoints, routing, env resolution |
| Processing core | `lazyedit/`, `agi/` | Pipeline phụ đề/caption/metadata + providers |
| UI | `app/` | Trải nghiệm vận hành (web/mobile qua Expo) |
| Runtime scripts | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Khởi chạy local/service và vận hành |

High-level flow:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

Các ảnh minh họa bên dưới thể hiện tuyến luồng vận hành chính từ ingest đến sinh metadata.

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

- ✨ Workflow tạo nội dung bằng prompt (Stage A/B/C) với đường dẫn tích hợp Sora và Veo.
- 🧵 Toàn bộ pipeline: phiên âm -> polish/translate phụ đề -> burn-in -> keyframes -> captions -> metadata.
- 🌏 Soạn phụ đề đa ngôn ngữ với support paths cho furigana/IPA/romaji.
- 🔌 Backend API-first với các endpoint upload, processing, media serving, publish queue.
- 🚚 Tích hợp AutoPublish tùy chọn để bàn giao sang platform.
- 🖥️ Hỗ trợ workflow backend + Expo được phối hợp qua script tmux.

## 🌍 Documentation & i18n


- Canonical source: `README.md`
- Language variants: `i18n/README.*.md`
- Language bar: giữ đúng một dòng language-options ở đầu mỗi README (không trùng lặp)
- Ngôn ngữ hiện có trong repo: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

If there is ever a mismatch between translations and English docs, treat this English README as source of truth, then update each language file one-by-one.

| i18n policy | Rule |
| --- | --- |
| Canonical source | Giữ `README.md` làm nguồn tham chiếu chính |
| Language bar | Chính xác một dòng language-options ở đầu |

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
├── whisper_with_lang_detect/         # Submodule (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule (primary captioner)
├── clip-gpt-captioning/             # Submodule (fallback captioner)
└── furigana/                        # External dependency in workflow (tracked submodule in this checkout)
```

Ghi chú submodule/dependency bên ngoài:
- Git submodule của repository gồm `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, và `furigana`.
- Hướng dẫn vận hành xử lý `furigana` và `echomind` như dependency ngoài và chỉ đọc trong workflow này. Nếu chưa rõ, ưu tiên giữ nguyên upstream và tránh sửa trực tiếp.

## ✅ Prerequisites

| Dependency | Notes |
| --- | --- |
| Linux environment | Các script `systemd`/`tmux` định hướng Linux |
| Python 3.10+ | Dùng Conda env `lazyedit` |
| Node.js 20+ + npm | Bắt buộc cho Expo app trong `app/` |
| FFmpeg | Phải có sẵn trong `PATH` |
| PostgreSQL | Kết nối local peer auth hoặc DSN |
| Git submodules | Bắt buộc cho pipeline then chốt |

## 🚀 Installation

1. Clone và khởi tạo submodule:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Kích hoạt Conda:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Cài đặt tùy chọn ở cấp hệ thống (service mode):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Service install notes:
- `install_lazyedit.sh` cài `ffmpeg` và `tmux`, sau đó tạo `lazyedit.service`.
- Nó không sinh `lazyedit_config.sh`, `start_lazyedit.sh`, hay `stop_lazyedit.sh`; các file này phải đã tồn tại và đúng cấu hình.

## ⚡ Quick Start

Chạy backend + frontend local (đường dẫn tối thiểu):

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Trong terminal thứ hai:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Khởi tạo DB local tùy chọn:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| Local dev (manual) | `python app.py` + Expo command | `8787` | `8091` (example command) |
| Tmux orchestrated | `./start_lazyedit.sh` | `18787` | `18791` |
| service systemd | `sudo systemctl start lazyedit.service` | Config/env-driven | N/A |

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

Entrypoint thay thế đang dùng trong các script deploy hiện tại:

```bash
python app.py -m lazyedit
```

Backend default URL: `http://localhost:8787` (theo `config.py`, có thể override bằng `PORT` hoặc `LAZYEDIT_PORT`).

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Ports mặc định của `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Đính vào session:

```bash
tmux attach -t lazyedit
```

Dừng session:

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

Copy `.env.example` sang `.env` rồi cập nhật đường dẫn/secrets:

```bash
cp .env.example .env
```

Configuration precedence note:

- `config.py` load giá trị `.env` nếu tồn tại và chỉ set các key chưa được export trong shell.
- Giá trị runtime có thể đến từ: biến môi trường đã export trong shell -> `.env` -> default trong code.
- Với tmux/service, `lazyedit_config.sh` điều khiển tham số khởi chạy/session (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, ports qua env của script).

### Key variables

| Variable | Purpose | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Backend port | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Thư mục gốc media | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN PostgreSQL | Fallback local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish endpoint | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout request AutoPublish (giây) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Đường dẫn script Whisper/VAD | phụ thuộc môi trường |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Tên mô hình ASR | `large-v3` / `large-v2` (ví dụ) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python cho caption pipeline | phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Đường dẫn/script chú thích chính | phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Script/fallback cwd cho caption | phụ thuộc môi trường |
| `GRSAI_API_*` | Cài đặt tích hợp Veo/GRSAI | phụ thuộc môi trường |
| `VENICE_*`, `A2E_*` | Cài đặt tích hợp Venice/A2E | phụ thuộc môi trường |
| `OPENAI_API_KEY` | Bắt buộc cho chức năng OpenAI-backed | None |

Machine-specific notes:
- `app.py` có thể set hành vi CUDA (`CUDA_VISIBLE_DEVICES` usage in codebase context).
- Một số đường dẫn mặc định mang tính máy chủ; dùng `.env` để override cho portable setup.
- `lazyedit_config.sh` điều khiển biến khởi chạy tmux/session cho các script deploy.

## 🧾 Configuration Files

| File | Purpose |
| --- | --- |
| `.env.example` | Mẫu biến môi trường dùng bởi backend/services |
| `.env` | Override máy địa phương; được load bởi `config.py`/`app.py` nếu tồn tại |
| `config.py` | Mặc định backend và logic resolve environment |
| `lazyedit_config.sh` | Profile runtime tmux/service (deploy path, conda env, app args, session name) |
| `start_lazyedit.sh` | Chạy backend + Expo trong tmux với ports đã chọn |
| `install_lazyedit.sh` | Tạo `lazyedit.service` và validate script/config hiện có |

Recommended update order for machine portability:
1. Copy `.env.example` thành `.env`.
2. Set các giá trị `LAZYEDIT_*` liên quan path/API trong `.env`.
3. Chỉ chỉnh `lazyedit_config.sh` cho hành vi deploy tmux/service.

## 🔌 API Examples

Mẫu base URL mặc định giả sử `http://localhost:8787`.

| API group | Representative endpoints |
| --- | --- |
| Upload and media | `/upload`, `/upload-stream`, `/media/*` |
| Video records | `/api/videos`, `/api/videos/{id}` |
| Processing | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publish | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generation | `/api/videos/generate` (+ provider routes trong `app.py`) |

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

Nếu backend đang chạy ở `8887`:

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

- Dùng `python` trong Conda env `lazyedit` (không giả định `python3` hệ thống).
- Giữ media lớn ngoài Git; lưu runtime media trong `DATA/` hoặc lưu trữ ngoài.
- Initialize/update submodules khi các component của pipeline lỗi hoặc không resolve được.
- Giữ các thay đổi scope hẹp; tránh format refactor không liên quan.
- Với frontend, API URL của app được điều khiển bởi `EXPO_PUBLIC_API_URL`.
- CORS backend mở cho app development.

Submodule and external dependency policy:
- Treat external dependencies as upstream-owned. In this repository workflow, avoid editing submodule internals unless intentionally working in those projects.
- Hướng dẫn vận hành của repo coi `furigana` (và một số thiết lập `echomind` trong môi trường local) là dependency ngoài; nếu không chắc chắn, giữ upstream và tránh sửa in-place.

Helpful references:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Security/config hygiene:
- Giữ API keys và secrets trong biến môi trường; không commit credential.
- Ưu tiên `.env` cho overrides máy local và giữ `.env.example` làm template công khai.
- Nếu hành vi CUDA/GPU khác theo host, override qua môi trường thay vì hardcode giá trị theo máy.

## ✅ Testing

Phạm vi test chính thức hiện tại nhỏ và tập trung DB.

| Validation layer | Command or method |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | Web UI + API chạy bằng sample ngắn trong `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Với kiểm chứng chức năng, dùng web UI + API flow với một clip ngắn trong `DATA/`.

Assumptions and portability notes:
- Một số đường dẫn mặc định trong code là fallback theo máy; đây là đặc điểm hiện tại.
- Nếu một đường dẫn mặc định không tồn tại trên máy bạn, set biến `LAZYEDIT_*` tương ứng trong `.env`.
- Nếu chưa chắc chắn về giá trị theo máy, giữ nguyên thiết lập hiện tại và thêm override rõ ràng thay vì xóa default.

## 🧱 Assumptions & Known Limits

- Bộ dependency backend chưa được khóa bằng lockfile gốc; reproducibility phụ thuộc kỷ luật thiết lập local.
- `app.py` hiện tại có phạm vi route lớn và được giữ intentionally monolithic.
- Hầu hết validation pipeline là integration/manual (UI + API + media mẫu), với automated test còn hạn chế.
- Các thư mục runtime (`DATA/`, `temp/`, `translation_logs/`) là output vận hành và có thể tăng nhanh kích thước.
- Submodule cần có đầy đủ để hoạt động; checkout một phần thường gây lỗi script mất tích.

## 🚢 Deployment & Sync Notes

Đường dẫn + luồng sync đã biết (theo tài liệu vận hành repo):

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` trên `lazyingart`

| Environment | Path | Notes |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Main source + submodules |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` in ops docs |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Monitor/sync/process sessions |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull sau khi cập nhật submodule |

Sau khi push thay đổi `AutoPublish/` từ repo này, pull trên host publishing:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| Problem | Check / Fix |
| --- | --- |
| Thiếu module hoặc script pipeline | Chạy `git submodule update --init --recursive` |
| FFmpeg not found | Cài FFmpeg và xác nhận `ffmpeg -version` chạy được |
| Port conflicts | Backend mặc định `8787`; `start_lazyedit.sh` mặc định `18787`; set `LAZYEDIT_PORT` hoặc `PORT` rõ ràng |
| Expo cannot reach backend | Đảm bảo `EXPO_PUBLIC_API_URL` trỏ đúng host/port backend đang chạy |
| Database connection issues | Kiểm tra PostgreSQL + DSN/env vars; smoke check tùy chọn: `python db_smoke_test.py` |
| GPU/CUDA issues | Kiểm tra driver/CUDA tương thích stack Torch |
| Service script fails at install | Đảm bảo `lazyedit_config.sh`, `start_lazyedit.sh`, và `stop_lazyedit.sh` tồn tại trước khi chạy installer |

## 🗺️ Roadmap

- Chỉnh sửa phụ đề/segment in-app với A/B preview và điều khiển per-line.
- Mở rộng coverage test end-to-end cho các API flow cốt lõi.
- Đồng bộ tài liệu giữa các README i18n và các chế độ deploy.
- Cứng hóa pipeline cho generation-provider retries và visibility của trạng thái xử lý.

## 🤝 Contributing

Đóng góp đều được hoan nghênh.

1. Fork và tạo nhánh feature.
2. Giữ các commit scoped và tập trung.
3. Validate local (`python app.py`, flow API chính, và integration app nếu liên quan).
4. Tạo PR với mục đích rõ, bước tái hiện, và ghi chú before/after (screenshots cho thay đổi UI).

Practical guidelines:
- Follow Python style (PEP 8, 4 spaces, snake_case naming).
- Avoid committing credentials or large binaries.
- Update docs/config scripts khi hành vi thay đổi.
- Preferred commit style: short, imperative, scoped (for example: `fix ffmpeg 7 compatibility`).



## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit dựa trên các thư viện và dịch vụ mã nguồn mở, gồm:
- FFmpeg cho xử lý media
- Tornado cho backend APIs
- MoviePy cho workflow chỉnh sửa
- OpenAI models cho pipeline tác vụ hỗ trợ AI
- CJKWrap và công cụ văn bản đa ngôn ngữ trong luồng phụ đề
