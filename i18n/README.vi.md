[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>Quy trình làm việc AI-assist toàn diện cho video</b> dùng để tạo nội dung, xử lý phụ đề, metadata và xuất bản tùy chọn.
  <br />
  <sub>Tải lên hoặc tạo mới -> phiên âm -> dịch/chỉnh sửa -> chèn phụ đề -> keyframe/chú thích -> metadata -> xuất bản</sub>
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

## 📌 Thông tin nhanh

LazyEdit là pipeline video end-to-end hỗ trợ AI cho quá trình tạo, xử lý và xuất bản tùy chọn. Nó kết hợp tạo nội dung dựa trên prompt (Stage A/B/C), API xử lý media, render phụ đề, chú thích keyframe, sinh metadata và bàn giao sang AutoPublish.

| Thông tin nhanh | Giá trị |
| --- | --- |
| 📘 README chuẩn | `README.md` (tệp này) |
| 🌐 Biến thể ngôn ngữ | `i18n/README.*.md` (mỗi README chỉ giữ một dòng chọn ngôn ngữ ở đầu) |
| 🧠 Điểm vào backend | `app.py` (Tornado) |
| 🖥️ Ứng dụng frontend | `app/` (Expo web/mobile) |

## 🧭 Mục lục

- [Tổng quan](#-tổng-quan)
- [Thông tin nhanh](#-thông-tin-nhanh)
- [Nhìn nhanh](#-nhìn-nhanh)
- [Kiến trúc nhanh](#-kiến-trúc-nhanh)
- [Demos](#-demos)
- [Tính năng](#-tính-năng)
- [Tài liệu & i18n](#-tài-liệu--i18n)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
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

> Ghi chú: Nếu chi tiết repo/runtime khác theo máy, giữ nguyên mặc định hiện tại và override qua biến môi trường thay vì xóa các giá trị fallback theo máy.

| Vì sao đội ngũ dùng | Kết quả thực tế |
| --- | --- |
| Luồng vận hành thống nhất | Tải lên/tạo mới/phối hợp/xuất bản từ một quy trình duy nhất |
| Thiết kế API-first | Dễ viết script và tích hợp với công cụ khác |
| Runtime theo hướng local-first | Hoạt động tốt với tmux + triển khai theo service |

| Bước | Diễn biến |
| --- | --- |
| 1 | Tải lên hoặc tạo video |
| 2 | Phiên âm và (tùy chọn) dịch phụ đề |
| 3 | Chèn phụ đề đa ngôn ngữ với kiểm soát bố cục |
| 4 | Sinh keyframes, captions và metadata |
| 5 | Đóng gói và (tùy chọn) xuất bản qua AutoPublish |

### Trọng tâm pipeline

- Tải lên, tạo mới, remix và quản lý thư viện từ một UI vận hành duy nhất.
- Luồng xử lý API-first cho phiên âm, dịch/chỉnh sửa phụ đề, burn-in và metadata.
- Tích hợp tùy chọn provider tạo nội dung (Veo / Venice / A2E / Sora helpers trong `agi/`).
- Bàn giao xuất bản tùy chọn qua `AutoPublish`.

## 🎯 Nhìn nhanh

| Khu vực | Có trong LazyEdit | Trạng thái |
| --- | --- | --- |
| Ứng dụng lõi | Backend API Tornado + frontend Expo web/mobile | ✅ |
| Pipeline media | ASR, dịch/chỉnh sửa phụ đề, burn-in, keyframes, captions, metadata | ✅ |
| Tạo nội dung | Stage A/B/C và các route helper provider (`agi/`) | ✅ |
| Phân phối | Bàn giao AutoPublish (tùy chọn) | 🟡 Tùy chọn |
| Mô hình runtime | Script local-first, workflow tmux, service systemd tùy chọn | ✅ |

## 🏗️ Kiến trúc nhanh

Repository được tổ chức như một pipeline xử lý media theo hướng API-first có lớp giao diện người dùng:

- `app.py` là entrypoint của Tornado và điều phối route cho upload, xử lý, tạo nội dung, bàn giao xuất bản và phục vụ media.
- `lazyedit/` chứa các khối pipeline mô-đun (lưu trữ DB, dịch thuật, burn-in phụ đề, captions, metadata, adapter provider).
- `app/` là ứng dụng Expo Router (web/mobile) vận hành flow upload, processing, preview và publish.
- `config.py` gom logic đọc biến môi trường và các đường dẫn fallback.
- `start_lazyedit.sh` và `lazyedit_config.sh` cung cấp chế độ chạy tmux local/deployed có thể lặp lại.

| Tầng | Đường dẫn chính | Trách nhiệm |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | Endpoint, routing, giải quyết env |
| Processing core | `lazyedit/`, `agi/` | Pipeline subtitle/caption/metadata + providers |
| UI | `app/` | Trải nghiệm vận hành (web/mobile qua Expo) |
| Runtime scripts | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Khởi chạy local/service và vận hành |

Luồng tổng quan:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

Các ảnh minh họa dưới đây thể hiện luồng vận hành chính từ ingest đến sinh metadata.

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

- ✨ Quy trình tạo nội dung bằng prompt (Stage A/B/C) với các đường dẫn tích hợp Sora và Veo.
- 🧵 Pipeline xử lý toàn bộ: phiên âm -> dịch/chỉnh sửa phụ đề -> burn-in -> keyframes -> captions -> metadata.
- 🌏 Soạn phụ đề đa ngôn ngữ với luồng hỗ trợ furigana/IPA/romaji liên quan.
- 🔌 Backend API-first với endpoint upload, processing, media serving, publish queue.
- 🚚 Tích hợp AutoPublish tùy chọn cho bước bàn giao sang nền tảng xã hội.
- 🖥️ Hỗ trợ workflow backend + Expo cùng lúc thông qua các script tmux.

## 🌍 Tài liệu & i18n

- Nguồn chuẩn: `README.md`
- Biến thể ngôn ngữ: `i18n/README.*.md`
- Thanh chọn ngôn ngữ: giữ đúng một dòng chọn ngôn ngữ duy nhất ở đầu mỗi README (không nhân bản)
- Ngôn ngữ hiện có trong repo: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

Nếu có bất kỳ chênh lệch nào giữa bản dịch và README tiếng Anh, hãy coi `README.md` là nguồn gốc đúng rồi cập nhật từng file `i18n/README.*.md` lần lượt.

| Chính sách i18n | Quy tắc |
| --- | --- |
| README chuẩn | Giữ `README.md` làm nguồn gốc |
| Thanh ngôn ngữ | Chỉ đúng một dòng language-options ở đầu |

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

Ghi chú submodule/external dependency:
- Các git submodule trong repository gồm `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` và `furigana`.
- Hướng dẫn vận hành xem `furigana` và `echomind` là external/read-only trong luồng làm việc repo này. Nếu chưa chắc chắn, giữ nguyên upstream và tránh sửa trực tiếp.

## ✅ Điều kiện tiên quyết

| Dependency | Ghi chú |
| --- | --- |
| Môi trường Linux | Script `systemd`/`tmux` định hướng Linux |
| Python 3.10+ | Dùng môi trường Conda `lazyedit` |
| Node.js 20+ + npm | Bắt buộc cho ứng dụng Expo trong `app/` |
| FFmpeg | Phải có trong `PATH` |
| PostgreSQL | Local peer auth hoặc kết nối DSN |
| Git submodules | Bắt buộc cho các pipeline chính |

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
- `install_lazyedit.sh` cài `ffmpeg` và `tmux`, rồi tạo `lazyedit.service`.
- Nó không tạo `lazyedit_config.sh`, `start_lazyedit.sh` hoặc `stop_lazyedit.sh`; các tệp này phải đã có sẵn và đúng.

## ⚡ Khởi động nhanh

Chạy backend + frontend local theo đường dẫn tối thiểu:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Ở shell thứ hai:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Bootstrap database local (tùy chọn):

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Profile runtime

| Profile | Lệnh khởi động | Backend mặc định | Frontend mặc định |
| --- | --- | --- | --- |
| Phát triển local (thủ công) | `python app.py` + lệnh Expo | `8787` | `8091` (ví dụ) |
| Tmux orchestration | `./start_lazyedit.sh` | `18787` | `18791` |
| Service systemd | `sudo systemctl start lazyedit.service` | Theo cấu hình/env | N/A |

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

Backend URL mặc định: `http://localhost:8787` (lấy từ `config.py`, có thể override bằng `PORT` hoặc `LAZYEDIT_PORT`).

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Ports mặc định của `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Kết nối vào phiên:

```bash
tmux attach -t lazyedit
```

Dừng phiên:

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

Lưu ý độ ưu tiên cấu hình:

- `config.py` nạp giá trị từ `.env` nếu có và chỉ thiết lập các key chưa được export trong shell.
- Giá trị runtime có thể đến từ: biến môi trường export shell -> `.env` -> default trong code.
- Với chạy tmux/service, `lazyedit_config.sh` điều khiển tham số khởi động/session (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, ports qua env của script khởi động).

### Biến quan trọng

| Biến | Mục đích | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Cổng backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Thư mục gốc media | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN PostgreSQL | Fallback local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout request AutoPublish (giây) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Đường dẫn script Whisper/VAD | Phụ thuộc môi trường |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Tên mô hình ASR | `large-v3` / `large-v2` (ví dụ) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python cho pipeline caption | Phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Đường dẫn/script caption chính | Phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Đường dẫn/script/cwd caption fallback | Phụ thuộc môi trường |
| `GRSAI_API_*` | Cài đặt tích hợp Veo/GRSAI | Phụ thuộc môi trường |
| `VENICE_*`, `A2E_*` | Cài đặt tích hợp Venice/A2E | Phụ thuộc môi trường |
| `OPENAI_API_KEY` | Bắt buộc cho tính năng dựa trên OpenAI | None |

Ghi chú theo máy:
- `app.py` có thể thiết lập hành vi CUDA (`CUDA_VISIBLE_DEVICES` trong codebase context).
- Một số đường dẫn mặc định mang tính workstation-specific; dùng override trong `.env` cho cấu hình portable.
- `lazyedit_config.sh` điều khiển biến khởi động tmux/session cho scripts deploy.

### Tập tin cấu hình

| Tệp | Mục đích |
| --- | --- |
| `.env.example` | Mẫu biến môi trường cho backend/services |
| `.env` | Override local theo máy; được `config.py`/`app.py` load nếu có |
| `config.py` | Default backend và resolve env |
| `lazyedit_config.sh` | Runtime profile tmux/service (đường dẫn deploy, conda env, app args, session name) |
| `start_lazyedit.sh` | Khởi chạy backend + Expo trong tmux với ports đã chọn |
| `install_lazyedit.sh` | Tạo `lazyedit.service` và validate scripts/config hiện có |

Thứ tự cập nhật khuyến nghị cho portability:
1. Copy `.env.example` thành `.env`.
2. Thiết lập các biến `LAZYEDIT_*` liên quan path/API trong `.env`.
3. Chỉ chỉnh `lazyedit_config.sh` cho hành vi deploy tmux/service.

## 🔌 Ví dụ API

Ví dụ base URL mặc định lấy từ `http://localhost:8787`.

| Nhóm API | Endpoint tiêu biểu |
| --- | --- |
| Upload và media | `/upload`, `/upload-stream`, `/media/*` |
| Hồ sơ video | `/api/videos`, `/api/videos/{id}` |
| Processing | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publish | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generation | `/api/videos/generate` (+ route provider trong `app.py`) |

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Quy trình end-to-end:

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

Publish package:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Thêm endpoint và payload chi tiết: `references/API_GUIDE.md`.

Các nhóm endpoint thường dùng:
- Vòng đời video: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Hành động xử lý: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Generation/provider paths: `/api/videos/generate` cộng thêm Venice/A2E routes trong `app.py`
- Distribution: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Ví dụ

### Chạy frontend local (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Nếu backend chạy ở `8887`:

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

- Dùng `python` từ Conda env `lazyedit` (không giả định system `python3`).
- Không đẩy media lớn lên Git; lưu media runtime trong `DATA/` hoặc bộ nhớ ngoài.
- Khởi tạo/cập nhật submodule khi thành phần pipeline không resolve.
- Giữ phạm vi chỉnh sửa gọn; tránh sửa format lớn không liên quan.
- Với frontend, `EXPO_PUBLIC_API_URL` điều khiển URL API backend.
- CORS mở trên backend cho phát triển app.

Chính sách submodule & external dependency:
- Xem dependency bên ngoài là do upstream sở hữu. Trong workflow này, tránh chỉnh sửa nội bộ submodule trừ khi làm việc trực tiếp trên chính project đó.
- Hướng dẫn vận hành coi `furigana` (và đôi khi `echomind` trong một số setup local) là dependency bên ngoài; nếu chưa chắc, giữ nguyên upstream và tránh sửa tại chỗ.

Tài liệu tham khảo:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Vệ sinh bảo mật/cấu hình:
- Giữ API keys và secret trong biến môi trường; không commit credentials.
- Ưu tiên `.env` cho override theo máy và giữ `.env.example` làm template công khai.
- Nếu hành vi CUDA/GPU khác theo host, override bằng biến môi trường thay vì hardcode theo máy.

## ✅ Kiểm thử

Bề mặt kiểm thử hiện tại còn tối thiểu và thiên về DB.

| Lớp kiểm thử | Lệnh hoặc phương pháp |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Kiểm tra pytest DB | `pytest tests/test_db_smoke.py` |
| Kiểm thử chức năng | Web UI + API flow với sample ngắn trong `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Với kiểm thử chức năng, dùng web UI và luồng API với clip ngắn trong `DATA/`.

Giả định và ghi chú portability:
- Một số đường dẫn mặc định trong code là fallback dành cho workstation cụ thể; đây là trạng thái hiện tại.
- Nếu path mặc định không tồn tại trên máy bạn, đặt biến `LAZYEDIT_*` tương ứng trong `.env`.
- Nếu chưa chắc về giá trị cụ thể theo máy, giữ nguyên cấu hình hiện tại và thêm override rõ ràng thay vì xóa defaults.

## 🧱 Giả định & Giới hạn đã biết

- Bộ dependency backend chưa được khóa bằng root lockfile; khả năng tái lập môi trường hiện phụ thuộc kỷ luật cài đặt local.
- `app.py` hiện đang tương đối monolithic và chứa surface route khá rộng.
- Hầu hết validation pipeline là integration/manual (UI + API + sample media), với phạm vi test tự động hạn chế.
- Runtime directories (`DATA/`, `temp/`, `translation_logs/`) là output vận hành và có thể phình rất lớn.
- Submodule cần đầy đủ để dùng đủ chức năng; checkout thiếu sẽ dễ gây lỗi thiếu script.

## 🚢 Ghi chú triển khai & đồng bộ

Các đường dẫn và luồng đồng bộ đã biết (theo tài liệu vận hành repo):

- Workspace phát triển: `/home/lachlan/ProjectsLFS/LazyEdit`
- LazyEdit backend + app đã deploy: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor đã deploy: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Host hệ thống publishing: `/home/lachlan/Projects/auto-publish` trên `lazyingart`

| Môi trường | Đường dẫn | Ghi chú |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Nguồn chính + submodules |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` trong tài liệu ops |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Các phiên monitor/sync/process |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull sau khi cập nhật submodule |

Sau khi đẩy cập nhật `AutoPublish/` từ repo này, pull trên máy publishing:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Xử lý sự cố

| Vấn đề | Kiểm tra / Sửa |
| --- | --- |
| Thiếu module hoặc script pipeline | Chạy `git submodule update --init --recursive` |
| Không tìm thấy FFmpeg | Cài FFmpeg và kiểm tra `ffmpeg -version` hoạt động |
| Xung đột cổng | Backend mặc định `8787`; `start_lazyedit.sh` mặc định `18787`; set rõ `LAZYEDIT_PORT` hoặc `PORT` |
| Expo không kết nối backend | Đảm bảo `EXPO_PUBLIC_API_URL` trỏ đúng host/cổng backend đang chạy |
| Lỗi kết nối database | Kiểm tra PostgreSQL + DSN/env vars; smoke check tùy chọn: `python db_smoke_test.py` |
| Lỗi GPU/CUDA | Xác nhận driver/CUDA tương thích với Torch stack đã cài |
| Script service lỗi khi cài | Đảm bảo `lazyedit_config.sh`, `start_lazyedit.sh`, `stop_lazyedit.sh` tồn tại trước khi chạy installer |

## 🗺️ Lộ trình

- Chỉnh sửa phụ đề/segmentation trực tiếp trong app với xem trước A/B và điều khiển theo dòng.
- Tăng độ phủ test end-to-end cho luồng API cốt lõi.
- Đồng bộ tài liệu giữa các README i18n và các chế độ triển khai.
- Tăng độ bền cho workflow retry provider tạo nội dung và khả năng quan sát trạng thái.

## 🤝 Đóng góp

Đóng góp được chào đón.

1. Fork và tạo nhánh tính năng.
2. Giữ commit tập trung và có phạm vi rõ.
3. Xác thực thay đổi cục bộ (`python app.py`, luồng API chính, và tích hợp app nếu liên quan).
4. Mở PR kèm mục đích, hướng dẫn reproduce, và ghi chú before/after (ảnh chụp nếu có đổi UI).

Nguyên tắc thực hành:
- Tuân thủ style Python (PEP 8, 4 spaces, snake_case naming).
- Không commit credential hoặc file nhị phân lớn.
- Cập nhật docs/config khi hành vi thay đổi.
- Ưu tiên commit ngắn, mệnh lệnh, có phạm vi (ví dụ: `fix ffmpeg 7 compatibility`).

## 📄 Giấy phép

[Apache-2.0](LICENSE)

## 🙏 Lời cảm ơn

LazyEdit được xây dựng trên các thư viện và dịch vụ mã nguồn mở, bao gồm:
- FFmpeg cho xử lý media
- Tornado cho backend API
- MoviePy cho luồng chỉnh sửa
- OpenAI models cho pipeline có hỗ trợ AI
- CJKWrap và công cụ xử lý văn bản đa ngôn ngữ trong luồng phụ đề


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
