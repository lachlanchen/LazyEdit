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

LazyEdit là một quy trình video đầu-cuối có hỗ trợ AI cho việc tạo, xử lý và (tùy chọn) xuất bản. Dự án kết hợp tạo nội dung theo prompt (Stage A/B/C), API xử lý media, render phụ đề, caption theo keyframe, tạo metadata và bàn giao sang AutoPublish.

## ✨ Tổng quan

LazyEdit được xây dựng quanh backend Tornado (`app.py`) và frontend Expo (`app/`).

| Bước | Điều gì xảy ra |
| --- | --- |
| 1 | Tải lên hoặc tạo video |
| 2 | Chuyển giọng nói thành văn bản và (tùy chọn) dịch phụ đề |
| 3 | Burn phụ đề đa ngôn ngữ với điều khiển bố cục |
| 4 | Tạo keyframe, caption và metadata |
| 5 | Đóng gói và (tùy chọn) xuất bản qua AutoPublish |

### Trọng tâm pipeline

- Tải lên, tạo mới, remix và quản lý thư viện từ một giao diện vận hành duy nhất.
- Luồng xử lý ưu tiên API cho phiên âm, làm mượt/dịch phụ đề, burn-in và metadata.
- Tích hợp tùy chọn với các nhà cung cấp tạo nội dung (helper cho Veo / Venice / A2E / Sora trong `agi/`).
- Bàn giao xuất bản tùy chọn qua `AutoPublish`.

## 🎯 Tóm tắt nhanh

| Khu vực | Có trong LazyEdit |
| --- | --- |
| Ứng dụng cốt lõi | Backend API Tornado + frontend Expo web/mobile |
| Pipeline media | ASR, dịch/làm mượt phụ đề, burn-in, keyframe, caption, metadata |
| Tạo nội dung | Stage A/B/C và các route helper nhà cung cấp (`agi/`) |
| Phân phối | Bàn giao AutoPublish (tùy chọn) |
| Mô hình runtime | Script local-first, workflow tmux, dịch vụ systemd tùy chọn |

## 🎬 Demo

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Home · Tải lên</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Home · Tạo</sub>
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
      <br /><sub>Keyframe + caption</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Trình tạo metadata</sub>
    </td>
  </tr>
</table>

## 🧩 Tính năng

- Quy trình tạo nội dung theo prompt (Stage A/B/C) với các nhánh tích hợp Sora và Veo.
- Pipeline xử lý đầy đủ: phiên âm -> làm mượt/dịch phụ đề -> burn-in -> keyframe -> caption -> metadata.
- Biên soạn phụ đề đa ngôn ngữ với các nhánh hỗ trợ liên quan furigana/IPA/romaji.
- Backend ưu tiên API với endpoint tải lên, xử lý, phục vụ media và hàng đợi xuất bản.
- Tích hợp AutoPublish tùy chọn để bàn giao lên các nền tảng mạng xã hội.
- Workflow kết hợp backend + Expo được hỗ trợ bằng script khởi chạy tmux.

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

## ✅ Điều kiện tiên quyết

| Phụ thuộc | Ghi chú |
| --- | --- |
| Môi trường Linux | Script `systemd`/`tmux` định hướng Linux |
| Python 3.10+ | Dùng Conda env `lazyedit` |
| Node.js 20+ + npm | Cần cho ứng dụng Expo trong `app/` |
| FFmpeg | Phải có trên `PATH` |
| PostgreSQL | Xác thực peer cục bộ hoặc kết nối dựa trên DSN |
| Git submodules | Cần cho các pipeline chính |

## 🚀 Cài đặt

1. Clone và khởi tạo submodule:

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

3. Cài đặt cấp hệ thống (tùy chọn, chế độ service):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Ghi chú cài đặt service:
- `install_lazyedit.sh` cài `ffmpeg` và `tmux`, sau đó tạo `lazyedit.service`.
- Script này không tạo `lazyedit_config.sh`, `start_lazyedit.sh` hoặc `stop_lazyedit.sh`; các file này phải tồn tại sẵn và chính xác.

## 🛠️ Sử dụng

### Development: chỉ backend

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Điểm vào thay thế đang dùng trong script triển khai hiện tại:

```bash
python app.py -m lazyedit
```

URL backend mặc định: `http://localhost:8787` (từ `config.py`, có thể ghi đè bằng `PORT` hoặc `LAZYEDIT_PORT`).

### Development: backend + ứng dụng Expo (tmux)

```bash
./start_lazyedit.sh
```

Cổng mặc định của `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Gắn vào session:

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

Sao chép `.env.example` thành `.env` và cập nhật đường dẫn/khóa bí mật:

```bash
cp .env.example .env
```

### Biến quan trọng

| Biến | Mục đích | Mặc định/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Cổng backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Thư mục gốc media | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Fallback DB cục bộ `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout request AutoPublish (giây) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Đường dẫn script Whisper/VAD | Phụ thuộc môi trường |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Tên model ASR | `large-v3` / `large-v2` (ví dụ) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python cho pipeline caption | Phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Đường dẫn/script caption chính | Phụ thuộc môi trường |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Đường dẫn/script/cwd caption fallback | Phụ thuộc môi trường |
| `GRSAI_API_*` | Thiết lập tích hợp Veo/GRSAI | Phụ thuộc môi trường |
| `VENICE_*`, `A2E_*` | Thiết lập tích hợp Venice/A2E | Phụ thuộc môi trường |
| `OPENAI_API_KEY` | Bắt buộc cho các tính năng dùng OpenAI | Không có |

Ghi chú theo từng máy:
- `app.py` có thể thiết lập hành vi CUDA (cách dùng `CUDA_VISIBLE_DEVICES` trong ngữ cảnh codebase).
- Một số đường dẫn mặc định mang tính workstation-specific; dùng ghi đè trong `.env` để có cấu hình portable.
- `lazyedit_config.sh` điều khiển biến khởi động tmux/session cho script triển khai.

## 🔌 Ví dụ API

Ví dụ URL gốc giả định `http://localhost:8787`.

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Quy trình đầu-cuối:

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

Xuất bản gói:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Thêm endpoint và chi tiết payload: `references/API_GUIDE.md`.

## 🧪 Ví dụ

### Chạy frontend cục bộ (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Nếu backend ở `8887`:

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

### Helper tạo nội dung Sora (tùy chọn)

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Giây hỗ trợ: `4`, `8`, `12`.
Kích thước hỗ trợ: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Ghi chú phát triển

- Dùng `python` từ Conda env `lazyedit` (không giả định `python3` hệ thống).
- Không đưa media lớn vào Git; lưu media runtime trong `DATA/` hoặc bộ nhớ ngoài.
- Khởi tạo/cập nhật submodule khi các thành phần pipeline không được resolve.
- Giữ phạm vi chỉnh sửa gọn; tránh thay đổi format lớn không liên quan.
- Với frontend, URL API backend được điều khiển bằng `EXPO_PUBLIC_API_URL`.
- CORS được mở ở backend để phát triển ứng dụng.

Chính sách submodule và phụ thuộc bên ngoài:
- Xem phụ thuộc bên ngoài là do upstream sở hữu. Trong workflow repo này, tránh chỉnh sửa phần bên trong submodule trừ khi bạn chủ động làm việc trong chính các project đó.
- Hướng dẫn vận hành trong repo này xem `furigana` (và đôi khi `echomind` trong một số thiết lập cục bộ) là đường dẫn phụ thuộc bên ngoài; nếu không chắc chắn, hãy giữ nguyên upstream và tránh sửa trực tiếp.

Tài liệu tham khảo hữu ích:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ Kiểm thử

Bề mặt kiểm thử chính thức hiện tại còn tối thiểu và thiên về DB.

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Để xác thực chức năng, dùng web UI và luồng API với một clip mẫu ngắn trong `DATA/`.

## 🚢 Ghi chú triển khai & đồng bộ

Các đường dẫn đã biết hiện tại và luồng đồng bộ (theo tài liệu vận hành repo):

- Workspace phát triển: `/home/lachlan/ProjectsLFS/LazyEdit`
- Backend + ứng dụng LazyEdit đã triển khai: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor đã triển khai: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Máy chủ hệ thống xuất bản: `/home/lachlan/Projects/auto-publish` trên `lazyingart`

Sau khi đẩy cập nhật `AutoPublish/` từ repo này, pull trên máy chủ xuất bản:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Khắc phục sự cố

| Vấn đề | Kiểm tra / Cách sửa |
| --- | --- |
| Thiếu module hoặc script pipeline | Chạy `git submodule update --init --recursive` |
| Không tìm thấy FFmpeg | Cài FFmpeg và xác nhận `ffmpeg -version` chạy được |
| Xung đột cổng | Backend mặc định `8787`; `start_lazyedit.sh` mặc định `18787`; đặt rõ `LAZYEDIT_PORT` hoặc `PORT` |
| Expo không kết nối được backend | Đảm bảo `EXPO_PUBLIC_API_URL` trỏ đúng host/cổng backend đang chạy |
| Lỗi kết nối cơ sở dữ liệu | Kiểm tra PostgreSQL + DSN/biến môi trường; smoke check tùy chọn: `python db_smoke_test.py` |
| Lỗi GPU/CUDA | Xác nhận tương thích driver/CUDA với stack Torch đã cài |
| Script service lỗi khi cài | Đảm bảo `lazyedit_config.sh`, `start_lazyedit.sh`, và `stop_lazyedit.sh` tồn tại trước khi chạy installer |

## 🗺️ Lộ trình

- Chỉnh sửa phụ đề/phân đoạn ngay trong app với xem trước A/B và điều khiển theo từng dòng.
- Tăng độ bao phủ kiểm thử end-to-end cho các luồng API cốt lõi.
- Đồng bộ hóa tài liệu giữa các biến thể README i18n và các chế độ triển khai.
- Gia cố thêm workflow cho retry của nhà cung cấp tạo nội dung và hiển thị trạng thái.

## 🤝 Đóng góp

Rất hoan nghênh đóng góp.

1. Fork và tạo nhánh tính năng.
2. Giữ commit tập trung và đúng phạm vi.
3. Xác thực thay đổi cục bộ (`python app.py`, luồng API chính, và tích hợp app nếu liên quan).
4. Mở PR kèm mục đích, bước tái hiện, và ghi chú trước/sau (kèm ảnh chụp với thay đổi UI).

Hướng dẫn thực tế:
- Tuân thủ style Python (PEP 8, 4 dấu cách, đặt tên snake_case).
- Không commit thông tin xác thực hoặc binary lớn.
- Cập nhật docs/script cấu hình khi hành vi thay đổi.
- Kiểu commit ưu tiên: ngắn, mệnh lệnh, có phạm vi (ví dụ: `fix ffmpeg 7 compatibility`).

## ❤️ Sự ủng hộ của bạn giúp hiện thực hóa

- <b>Giữ công cụ luôn mở</b>: hosting, suy luận, lưu trữ dữ liệu và vận hành cộng đồng.  
- <b>Ra bản nhanh hơn</b>: thêm nhiều tuần tập trung phát triển mã nguồn mở cho EchoMind, LazyEdit và MultilingualWhisper.  
- <b>Tạo mẫu thiết bị đeo</b>: quang học, cảm biến và thành phần neuromorphic/edge cho IdeasGlass + LightMind.  
- <b>Tiếp cận cho mọi người</b>: triển khai có hỗ trợ chi phí cho sinh viên, nhà sáng tạo và nhóm cộng đồng.

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

## 📄 Giấy phép

[Apache-2.0](LICENSE)

## 🙏 Lời cảm ơn

LazyEdit được xây dựng trên các thư viện và dịch vụ mã nguồn mở, bao gồm:
- FFmpeg cho xử lý media
- Tornado cho backend API
- MoviePy cho workflow chỉnh sửa
- Các model OpenAI cho tác vụ pipeline có hỗ trợ AI
- CJKWrap và bộ công cụ văn bản đa ngôn ngữ trong workflow phụ đề
