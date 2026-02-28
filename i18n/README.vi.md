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
  <b>Luồng làm việc tạo video toàn bộ bằng AI</b> cho việc tạo nội dung, xử lý phụ đề, metadata và xuất bản tùy chọn.
  <br />
  <sub>Tải lên hoặc tạo mới -> phiên âm -> dịch/chỉnh sửa -> chèn phụ đề -> keyframe/chú thích -> metadata -> xuất bản</sub>
</p>

# LazyEdit

LazyEdit là một pipeline video đầu-cuối có hỗ trợ AI cho tạo nội dung, xử lý và xuất bản tùy chọn. Dự án kết hợp tạo nội dung theo prompt (Stage A/B/C), API xử lý media, render phụ đề, caption theo keyframe, sinh metadata và bàn giao sang AutoPublish.

| Thông tin nhanh | Giá trị |
| --- | --- |
| 📘 README chuẩn | `README.md` (tệp này) |
| 🌐 Biến thể ngôn ngữ | `i18n/README.*.md` (mỗi README chỉ giữ một dòng chọn ngôn ngữ ở đầu) |
| 🧠 Điểm vào backend | `app.py` (Tornado) |
| 🖥️ Ứng dụng frontend | `app/` (Expo web/mobile) |

## 🧭 Mục lục

- [Tổng quan](#-tổng-quan)
- [Tóm tắt nhanh](#-tóm-tắt-nhanh)
- [Kiến trúc tổng quan](#-kiến-trúc-tổng-quan)
- [Demo](#-demo)
- [Tính năng](#-tính-năng)
- [Tài liệu &amp; i18n](#--tài-liệu--i18n)
- [Cấu trúc dự án](#--cấu-trúc-dự-án)
- [Điều kiện tiên quyết](#-điều-kiện-tiên-quyết)
- [Cài đặt](#-cài-đặt)
- [Khởi động nhanh](#-khởi-động-nhanh)
- [Bảng lệnh nhanh](#-bảng-lệnh-nhanh)
- [Cách sử dụng](#-cách-sử-dụng)
- [Cấu hình](#-cấu-hình)
- [Tập tin cấu hình](#-tập-tin-cấu-hình)
- [Ví dụ API](#-ví-dụ-api)
- [Ví dụ](#-ví-dụ)
- [Ghi chú phát triển](#-ghi-chú-phát-triển)
- [Kiểm thử](#-kiểm-thử)
- [Giả định & giới hạn đã biết](#-giả-định--giới-hạn-đã-biết)
- [Ghi chú triển khai & đồng bộ](#-ghi-chú-triển-khai--đồng-bộ)
- [Xử lý sự cố](#-xử-lý-sự-cố)
- [Lộ trình](#-lộ-trình)
- [Đóng góp](#-đóng-góp)
- [Hỗ trợ](#-support)
- [Giấy phép](#-giấy-phép)
- [Lời cảm ơn](#-lời-cảm-ơn)

## ✨ Tổng quan

LazyEdit được xây dựng quanh backend Tornado (`app.py`) và frontend Expo (`app/`).

> Lưu ý: Nếu chi tiết repo/runtime khác nhau theo máy, giữ nguyên mặc định hiện có và ghi đè bằng biến môi trường thay vì xóa các giá trị fallback theo máy.

| Vì sao nhóm dùng | Kết quả thực tế |
| --- | --- |
| Luồng vận hành thống nhất | Tải lên/tạo mới/remix/xuất bản trong cùng một quy trình |
| Thiết kế API-first | Dễ viết script và tích hợp với các công cụ khác |
| Runtime theo hướng local-first | Hoạt động tốt với tmux + triển khai qua service |

| Bước | Diễn biến |
| --- | --- |
| 1 | Tải lên hoặc tạo mới video |
| 2 | Phiên âm và (tùy chọn) dịch phụ đề |
| 3 | Burn phụ đề đa ngôn ngữ với điều khiển layout |
| 4 | Sinh keyframes, captions và metadata |
| 5 | Gói và (tùy chọn) xuất bản qua AutoPublish |

### Trọng tâm pipeline

- Tải lên, tạo mới, remix và quản lý thư viện từ một giao diện vận hành duy nhất.
- Luồng xử lý API-first cho phiên âm, chỉnh sửa/dịch phụ đề, burn-in và metadata.
- Tích hợp provider tạo nội dung tùy chọn (Veo / Venice / A2E / Sora helpers trong `agi/`).
- Bàn giao xuất bản tùy chọn qua `AutoPublish`.

## 🎯 Tóm tắt nhanh

| Khu vực | Có trong LazyEdit | Trạng thái |
| --- | --- | --- |
| Ứng dụng cốt lõi | Backend API Tornado + frontend Expo web/mobile | ✅ |
| Pipeline media | ASR, dịch/làm mượt phụ đề, burn-in, keyframes, captions, metadata | ✅ |
| Tạo nội dung | Stage A/B/C và các route provider helper (`agi/`) | ✅ |
| Phân phối | Bàn giao AutoPublish (tùy chọn) | 🟡 Tùy chọn |
| Mô hình runtime | Script local-first, workflow tmux, service systemd tùy chọn | ✅ |

## 🏗️ Kiến trúc tổng quan

Repository được tổ chức như một pipeline xử lý media theo hướng API-first có lớp giao diện người dùng:

- `app.py` là entrypoint của Tornado và nơi điều phối route cho tải lên, xử lý, tạo nội dung, bàn giao xuất bản và phục vụ media.
- `lazyedit/` chứa các khối pipeline module hoá (lưu trữ DB, dịch thuật, burn-in phụ đề, captions, metadata, adapters provider).
- `app/` là ứng dụng Expo Router (web/mobile) điều phối upload, processing, preview và publish flows.
- `config.py` tập trung tải biến môi trường và fallback path runtime mặc định.
- `start_lazyedit.sh` và `lazyedit_config.sh` cung cấp chế độ chạy tmux local/deployed tái lập được.

| Lớp | Đường dẫn chính | Trách nhiệm |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | Endpoint, routing, giải quyết biến môi trường |
| Processing core | `lazyedit/`, `agi/` | Pipeline subtitle/caption/metadata + providers |
| UI | `app/` | Trải nghiệm vận hành (web/mobile qua Expo) |
| Runtime scripts | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Khởi chạy local/service và vận hành |

Luồng tổng quan:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demo

Các ảnh chụp dưới đây minh họa đường đi chính từ ingest đến sinh metadata.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Home · Tải lên</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Home · Tạo mới</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Home · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Thư viện</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Tổng quan video</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Xem trước bản dịch</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Burn slots</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Bố cục burn</sub>
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

## 🧩 Tính năng

- ✨ Quy trình tạo nội dung theo prompt (Stage A/B/C) với đường dẫn tích hợp Sora và Veo.
- 🧵 Pipeline xử lý toàn phần: phiên âm -> dịch/chỉnh sửa phụ đề -> burn-in -> keyframes -> captions -> metadata.
- 🌏 Soạn phụ đề đa ngôn ngữ với các hỗ trợ liên quan furigana/IPA/romaji.
- 🔌 Backend API-first với endpoint upload, processing, media serving và publish queue.
- 🚚 Tích hợp AutoPublish tùy chọn cho bàn giao sang nền tảng mạng xã hội.
- 🖥️ Hỗ trợ workflow backend + Expo cùng lúc thông qua script tmux.

## 🌍 Tài liệu & i18n

LazyEdit giữ nguyên một README tiếng Anh làm chuẩn (`README.md`) và các biến thể ngôn ngữ trong `i18n/`.

- Nguồn chuẩn: `README.md`
- Biến thể ngôn ngữ: `i18n/README.*.md`
- Thanh chọn ngôn ngữ: giữ duy nhất một dòng liên kết ngôn ngữ ở đầu mỗi README (không nhân bản)
- Ngôn ngữ hiện có trong repo: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

Nếu có bất kỳ sai lệch nào giữa bản dịch và README tiếng Anh, hãy coi `README.md` là nguồn gốc đúng, rồi cập nhật từng file `i18n/README.*.md` lần lượt.

| Chính sách i18n | Quy tắc |
| --- | --- |
| README chuẩn | Giữ `README.md` làm nguồn gốc |
| Thanh ngôn ngữ | Chỉ đúng một dòng language-options ở đầu |
| Thứ tự cập nhật | Tiếng Anh trước, rồi đến từng file `i18n/README.*.md` theo thứ tự |

## 🗂️ Cấu trúc dự án

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

Ghi chú submodule/external dependency:
- Git submodules trong repository gồm `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, và `furigana`.
- Hướng dẫn vận hành coi `furigana` và `echomind` là external/read-only trong workflow của repo. Nếu chưa chắc chắn, giữ nguyên upstream và tránh sửa trực tiếp.

## ✅ Điều kiện tiên quyết

| Dependency | Ghi chú |
| --- | --- |
| Môi trường Linux | Script `systemd`/`tmux` định hướng Linux |
| Python 3.10+ | Dùng Conda env `lazyedit` |
| Node.js 20+ + npm | Bắt buộc cho ứng dụng Expo trong `app/` |
| FFmpeg | Phải có sẵn trong `PATH` |
| PostgreSQL | Cần peer auth local hoặc kết nối DSN |
| Git submodules | Bắt buộc cho pipeline chính |

## 🚀 Cài đặt

1. Clone và khởi tạo submodules:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Kích hoạt môi trường Conda:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Cài đặt hệ thống (service mode, tùy chọn):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Ghi chú cài đặt service:
- `install_lazyedit.sh` cài `ffmpeg` và `tmux`, sau đó tạo `lazyedit.service`.
- Script này không tạo `lazyedit_config.sh`, `start_lazyedit.sh` hoặc `stop_lazyedit.sh`; các file này phải tồn tại sẵn và đúng.

## ⚡ Khởi động nhanh

Chạy backend + frontend local theo đường dẫn tối thiểu:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Trong shell thứ hai:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Tùy chọn bootstrap database local:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Profile runtime

| Profile | Lệnh khởi động | Backend mặc định | Frontend mặc định |
| --- | --- | --- | --- |
| Local dev (manual) | `python app.py` + lệnh Expo | `8787` | `8091` (ví dụ) |
| Tmux orchestrated | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd service | `sudo systemctl start lazyedit.service` | Theo config/env | N/A |

## 🧭 Bảng lệnh nhanh

| Nhiệm vụ | Lệnh |
| --- | --- |
| Khởi tạo submodule | `git submodule update --init --recursive` |
| Chạy backend only | `python app.py` |
| Chạy backend + Expo (tmux) | `./start_lazyedit.sh` |
| Dừng tmux run | `./stop_lazyedit.sh` |
| Mở tmux session | `tmux attach -t lazyedit` |
| Xem trạng thái service | `sudo systemctl status lazyedit.service` |
| Xem log service | `sudo journalctl -u lazyedit.service` |
| Smoke test DB | `python db_smoke_test.py` |
| Smoke test bằng pytest | `pytest tests/test_db_smoke.py` |

## 🛠️ Cách sử dụng

### Development: backend only

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Lối vào thay thế đang dùng trong scripts triển khai hiện tại:

```bash
python app.py -m lazyedit
```

Backend URL mặc định: `http://localhost:8787` (được lấy từ `config.py`, có thể override bằng `PORT` hoặc `LAZYEDIT_PORT`).

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Cổng mặc định của `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Kết nối session:

```bash
tmux attach -t lazyedit
```

Dừng session:

```bash
./stop_lazyedit.sh
```

### Quản lý service

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Cấu hình

Sao chép `.env.example` thành `.env` và cập nhật đường dẫn/secret:

```bash
cp .env.example .env
```

Lưu ý thứ tự ưu tiên cấu hình:

- `config.py` tải biến từ `.env` nếu có và chỉ đặt các key chưa được export sẵn trong shell.
- Giá trị runtime có thể đến từ: biến môi trường export shell -> `.env` -> mặc định trong code.
- Với tmux/service, `lazyedit_config.sh` điều khiển tham số khởi động/session (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, port qua env của script khởi động).

### Biến quan trọng

| Biến | Mục đích | Mặc định/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Cổng backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Thư mục gốc media | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Fallback local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Thời gian chờ request AutoPublish (giây) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Đường dẫn script Whisper/VAD | Phụ thuộc môi trường |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Tên mô hình ASR | `large-v3` / `large-v2` (ví dụ) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python cho pipeline caption | Phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Đường dẫn/script caption chính | Phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Đường dẫn/script/cwd caption fallback | Phụ thuộc môi trường |
| `GRSAI_API_*` | Cài đặt tích hợp Veo/GRSAI | Phụ thuộc môi trường |
| `VENICE_*`, `A2E_*` | Cài đặt tích hợp Venice/A2E | Phụ thuộc môi trường |
| `OPENAI_API_KEY` | Bắt buộc cho tính năng dùng OpenAI | None |

Ghi chú theo máy:
- `app.py` có thể thiết lập hành vi CUDA (sử dụng `CUDA_VISIBLE_DEVICES` trong ngữ cảnh codebase).
- Một số path mặc định là workstation-specific; dùng override `.env` cho thiết lập portable.
- `lazyedit_config.sh` điều khiển biến khởi động tmux/session cho scripts triển khai.

## 🧾 Tập tin cấu hình

| Tệp | Mục đích |
| --- | --- |
| `.env.example` | Mẫu biến môi trường cho backend/services |
| `.env` | Override local theo máy; được load bởi `config.py`/`app.py` nếu có |
| `config.py` | Defaults backend và logic giải quyết biến môi trường |
| `lazyedit_config.sh` | Profile runtime tmux/service (đường dẫn deploy, conda env, app args, session name) |
| `start_lazyedit.sh` | Khởi chạy backend + Expo trong tmux với port đã chọn |
| `install_lazyedit.sh` | Tạo `lazyedit.service` và kiểm tra script/config hiện có |

Thứ tự cập nhật khuyến nghị để portable theo máy:
1. Copy `.env.example` thành `.env`.
2. Đặt các giá trị `LAZYEDIT_*` liên quan path/API trong `.env`.
3. Chỉ chỉnh `lazyedit_config.sh` cho hành vi deploy tmux/service.

## 🔌 Ví dụ API

Các ví dụ Base URL mặc định `http://localhost:8787`.

| Nhóm API | Endpoint tiêu biểu |
| --- | --- |
| Upload và media | `/upload`, `/upload-stream`, `/media/*` |
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

Xử lý đầu-cuối:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Liệt kê video:

```bash
curl http://localhost:8787/api/videos
```

Publish gói:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Xem thêm endpoint chi tiết và payload tại: `references/API_GUIDE.md`.

Các nhóm endpoint liên quan thường dùng:
- Vòng đời video: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Hành động xử lý: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Generation/provider paths: `/api/videos/generate` cộng thêm các route Venice/A2E expose trong `app.py`
- Phân phối: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Ví dụ

### Chạy frontend local (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Nếu backend ở cổng `8887`:

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

### Tùy chọn helper tạo Sora

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Giây hỗ trợ: `4`, `8`, `12`.
Kích thước hỗ trợ: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Ghi chú phát triển

- Dùng `python` trong Conda env `lazyedit` (không giả định `python3` hệ thống).
- Không đưa media lớn lên Git; lưu media runtime trong `DATA/` hoặc bộ nhớ ngoài.
- Khởi tạo/cập nhật submodule khi thành phần pipeline không resolve.
- Giữ phạm vi chỉnh sửa gọn, tránh thay đổi format không liên quan.
- Với frontend, `EXPO_PUBLIC_API_URL` điều khiển địa chỉ API của backend.
- CORS được mở trong backend cho phát triển app.

Chính sách submodule & dependency ngoài:
- Xem dependency ngoài là do upstream sở hữu. Trong workflow repo này, tránh chỉnh sửa bên trong submodule nếu không có chủ đích làm việc trực tiếp trên project đó.
- Hướng dẫn vận hành repo này coi `furigana` (và đôi khi `echomind` trong setup cục bộ) là đường dẫn phụ thuộc bên ngoài; nếu không chắc, giữ nguyên upstream và tránh sửa tại chỗ.

Tham chiếu hữu ích:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Vệ sinh bảo mật/ cấu hình:
- Giữ API keys và secret trong biến môi trường; không commit credentials.
- Ưu tiên `.env` cho override theo máy và giữ `.env.example` làm template public.
- Nếu hành vi CUDA/GPU khác nhau theo host, ghi đè qua biến môi trường thay vì hardcode theo máy.

## ✅ Kiểm thử

Bề mặt kiểm thử chính thức hiện tại còn rất tối thiểu và thiên về DB.

| Lớp xác thực | Lệnh hoặc phương pháp |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Kiểm tra pytest DB | `pytest tests/test_db_smoke.py` |
| Kiểm thử chức năng | Web UI + API flow với sample ngắn trong `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Cho xác thực chức năng, dùng web UI và luồng API với một clip ngắn trong `DATA/`.

Giả định và ghi chú portability:
- Một số đường dẫn mặc định trong code là fallback dành cho một workstation cụ thể; đây là trạng thái hiện tại của repo.
- Nếu một path mặc định không có trên máy của bạn, đặt biến `LAZYEDIT_*` tương ứng trong `.env`.
- Nếu không chắc về giá trị cụ thể của máy, giữ nguyên cài đặt hiện có và bổ sung override rõ ràng thay vì xóa defaults.

## 🧱 Giả định & Giới hạn đã biết

- Bộ dependency của backend chưa được khóa bằng lockfile gốc; khả năng tái lập môi trường hiện phụ thuộc vào thiết lập cài đặt local.
- `app.py` hiện đang khá monolithic và chứa surface route khá lớn theo trạng thái hiện tại.
- Hầu hết validation pipeline là integration/manual (UI + API + sample media), với phạm vi test tự động hạn chế.
- Thư mục runtime (`DATA/`, `temp/`, `translation_logs/`) là output vận hành và có thể tăng rất nhanh.
- Submodule cần có đủ để đầy đủ chức năng; checkout thiếu sẽ dễ gây lỗi thiếu script.

## 🚢 Ghi chú triển khai & đồng bộ

Các đường dẫn và luồng đồng bộ đã biết (theo tài liệu vận hành repo):

- Workspace phát triển: `/home/lachlan/ProjectsLFS/LazyEdit`
- LazyEdit backend + app đã triển khai: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor đã triển khai: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Host hệ thống publishing: `/home/lachlan/Projects/auto-publish` trên `lazyingart`

| Môi trường | Đường dẫn | Ghi chú |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Source chính + submodules |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` trong tài liệu ops |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Monitor/sync/process sessions |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull sau khi cập nhật submodule |

Sau khi đẩy thay đổi `AutoPublish/` từ repo này, pull trên máy publishing:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Xử lý sự cố

| Vấn đề | Kiểm tra / Sửa |
| --- | --- |
| Thiếu module hoặc script pipeline | Chạy `git submodule update --init --recursive` |
| Không tìm thấy FFmpeg | Cài FFmpeg và xác nhận `ffmpeg -version` chạy được |
| Xung đột cổng | Backend mặc định `8787`; `start_lazyedit.sh` mặc định `18787`; set `LAZYEDIT_PORT` hoặc `PORT` rõ ràng |
| Expo không kết nối backend | Đảm bảo `EXPO_PUBLIC_API_URL` trỏ đúng host/cổng backend đang chạy |
| Lỗi kết nối database | Kiểm tra PostgreSQL + DSN/biến môi trường; smoke check tùy chọn: `python db_smoke_test.py` |
| Lỗi GPU/CUDA | Xác nhận driver/CUDA tương thích với Torch stack đã cài |
| Script service lỗi khi cài | Đảm bảo `lazyedit_config.sh`, `start_lazyedit.sh`, và `stop_lazyedit.sh` tồn tại trước khi chạy installer |

## 🗺️ Lộ trình

- Chỉnh sửa phụ đề/phân đoạn trực tiếp trong app với xem trước A/B và điều khiển theo dòng.
- Tăng độ phủ test end-to-end cho luồng API cốt lõi.
- Đồng bộ tài liệu giữa các biến thể README i18n và các chế độ triển khai.
- Gia cố thêm workflow cho retry provider tạo nội dung và hiển thị trạng thái.

## 🤝 Đóng góp

Đóng góp luôn được hoan nghênh.

1. Fork và tạo nhánh tính năng.
2. Giữ commit tập trung và trong phạm vi.
3. Xác thực thay đổi cục bộ (`python app.py`, luồng API chính, và tích hợp app khi cần).
4. Mở PR với mục đích, cách tái hiện, và ghi chú trước/sau (đính kèm ảnh chụp cho thay đổi UI).

Nguyên tắc thực hành:
- Tuân thủ style Python (PEP 8, 4 spaces, snake_case naming).
- Không commit credential hay file binary lớn.
- Cập nhật docs và scripts cấu hình khi hành vi thay đổi.
- Ưu tiên commit ngắn, mệnh lệnh, có phạm vi (ví dụ: `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 Giấy phép

[Apache-2.0](LICENSE)

## 🙏 Lời cảm ơn

LazyEdit được xây dựng trên các thư viện và dịch vụ mã nguồn mở, bao gồm:
- FFmpeg cho xử lý media
- Tornado cho backend API
- MoviePy cho quy trình chỉnh sửa
- OpenAI models cho pipeline có hỗ trợ AI
- CJKWrap và tooling xử lý văn bản đa ngôn ngữ trong luồng phụ đề
