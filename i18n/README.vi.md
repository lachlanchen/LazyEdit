<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

<p>
  <b>Languages:</b>
  <a href="../README.md">English</a>
  · <a href="README.zh-Hant.md">中文（繁體）</a>
  · <a href="README.zh-Hans.md">中文 (简体)</a>
  · <a href="README.ja.md">日本語</a>
  · <a href="README.ko.md">한국어</a>
  · <a href="README.vi.md">Tiếng Việt</a>
  · <a href="README.ar.md">العربية</a>
  · <a href="README.fr.md">Français</a>
  · <a href="README.es.md">Español</a>
</p>

# LazyEdit

LazyEdit là công cụ chỉnh sửa video tự động dựa trên AI. Công cụ tạo phụ đề, điểm nhấn, thẻ từ và metadata chuyên nghiệp, giúp tự động hóa các bước chỉnh sửa tốn thời gian.

## Tính năng

- **Tự động ghi âm thành chữ**: Chuyển giọng nói thành văn bản bằng AI
- **Tự động caption**: Tạo mô tả cho nội dung video
- **Tự động phụ đề**: Tạo và burn phụ đề trực tiếp lên video
- **Tự động highlight**: Làm nổi bật các từ khóa quan trọng
- **Tự động metadata**: Trích xuất và tạo metadata cho video
- **Thẻ từ vựng**: Thêm thẻ học từ cho ngôn ngữ
- **Tạo teaser**: Lặp đoạn quan trọng ở đầu video
- **Hỗ trợ đa ngôn ngữ**: Nhiều ngôn ngữ như Anh/Trung
- **Tạo ảnh bìa**: Chọn khung hình đẹp và chèn chữ

## Cài đặt

### Yêu cầu

- Python 3.10 trở lên
- FFmpeg
- GPU hỗ trợ CUDA (tăng tốc ghi âm)
- Trình quản lý môi trường Conda

### Các bước cài đặt

1. Clone repository:
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. Chạy script cài đặt:
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

Script sẽ:
- Cài đặt các gói hệ thống cần thiết (ffmpeg, tmux)
- Tạo môi trường conda "lazyedit"
- Thiết lập systemd để tự khởi động
- Cấu hình quyền cần thiết

## Sử dụng

LazyEdit chạy dưới dạng ứng dụng web tại http://localhost:8081

### Xử lý video

1. Tải video lên qua giao diện web
2. LazyEdit sẽ tự động:
   - Ghi âm và tạo caption
   - Tạo metadata và nội dung học tập
   - Tạo phụ đề theo ngôn ngữ phát hiện
   - Highlight từ quan trọng
   - Tạo teaser
   - Tạo ảnh bìa
   - Đóng gói và trả kết quả

### Dùng dòng lệnh

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## Cấu trúc dự án

- `app.py` - Entry chính
- `lazyedit/` - Thư mục module cốt lõi
  - `autocut_processor.py` - Phân đoạn và ghi âm
  - `subtitle_metadata.py` - Tạo metadata từ phụ đề
  - `subtitle_translate.py` - Dịch phụ đề
  - `video_captioner.py` - Tạo caption video
  - `words_card.py` - Tạo thẻ từ vựng
  - `utils.py` - Tiện ích
  - `openai_version_check.py` - Lớp tương thích OpenAI API

## Cấu hình

Dịch vụ systemd nằm ở `/etc/systemd/system/lazyedit.service`.

LazyEdit chạy trong tmux session tên "lazyedit" để hoạt động nền.

## Quản lý dịch vụ

- Khởi động: `sudo systemctl start lazyedit.service`
- Dừng: `sudo systemctl stop lazyedit.service`
- Trạng thái: `sudo systemctl status lazyedit.service`
- Log: `sudo journalctl -u lazyedit.service`

## Nâng cao

Có thể tùy chỉnh:
- Độ dài và vị trí teaser
- Kiểu highlight từ
- Font và vị trí phụ đề
- Cấu trúc thư mục đầu ra
- Chọn GPU

## Khắc phục sự cố

- Ứng dụng không chạy: kiểm tra systemd và log
- Xử lý lỗi: kiểm tra FFmpeg
- GPU: kiểm tra CUDA và GPU
- Đảm bảo môi trường conda đã kích hoạt

## Giấy phép

[Điền giấy phép tại đây]

## Ghi nhận

LazyEdit sử dụng các thư viện nguồn mở sau:
- FFmpeg (xử lý video)
- OpenAI models (AI)
- Tornado (web framework)
- MoviePy (chỉnh sửa video)
- CJKWrap (xử lý đa ngôn ngữ)
