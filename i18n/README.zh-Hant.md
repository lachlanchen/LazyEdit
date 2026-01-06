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

LazyEdit 是一款 AI 驅動的自動影片剪輯工具，可為影片自動產生專業級字幕、重點高亮、單字卡與中繼資料，透過先進 AI 技術簡化繁瑣的剪輯流程。

## 功能特色

- **自動轉錄**：使用 AI 自動轉錄影片音訊
- **自動畫面描述**：為影片內容生成描述性字幕
- **自動字幕**：直接產生並燒錄字幕
- **自動高亮**：辨識並高亮播放中的關鍵詞
- **自動中繼資料**：從影片內容萃取並生成中繼資料
- **單字卡**：新增語言學習用單字卡
- **預告片生成**：以重複關鍵片段的方式產生精華預告
- **多語言支援**：支援多種語言（含英文與中文）
- **封面生成**：擷取最佳封面並加上文字疊圖

## 安裝

### 先決條件

- Python 3.10 以上
- FFmpeg
- 支援 CUDA 的 GPU（加速轉錄）
- Conda 環境管理工具

### 安裝步驟

1. 下載專案：
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. 執行安裝腳本：
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

安裝腳本將會：
- 安裝必要系統套件（ffmpeg、tmux）
- 建立並設定名為 "lazyedit" 的 conda 環境
- 設定 systemd 服務以自動啟動
- 設定所需權限

## 使用方式

LazyEdit 以網頁應用方式運行，可在 http://localhost:8081 存取。

### 處理影片

1. 透過網頁介面上傳影片
2. LazyEdit 會自動：
   - 進行轉錄與畫面描述
   - 生成中繼資料與學習內容
   - 產生偵測語言的字幕
   - 高亮重要詞彙
   - 生成前導預告
   - 產生封面圖
   - 封裝並輸出處理結果

### 命令列使用

也可直接執行 LazyEdit：

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## 專案結構

- `app.py` - 主程式入口
- `lazyedit/` - 核心模組目錄
  - `autocut_processor.py` - 影片分段與轉錄
  - `subtitle_metadata.py` - 由字幕生成中繼資料
  - `subtitle_translate.py` - 字幕翻譯
  - `video_captioner.py` - 產生畫面描述
  - `words_card.py` - 產生學習單字卡
  - `utils.py` - 工具函式
  - `openai_version_check.py` - OpenAI API 相容性處理

## 設定

systemd 服務設定會建立在 `/etc/systemd/system/lazyedit.service`。

LazyEdit 透過名為 "lazyedit" 的 tmux session 執行，方便在背景持續運行。

## 服務管理

- 啟動服務：`sudo systemctl start lazyedit.service`
- 停止服務：`sudo systemctl stop lazyedit.service`
- 查看狀態：`sudo systemctl status lazyedit.service`
- 查看日誌：`sudo journalctl -u lazyedit.service`

## 進階使用

LazyEdit 支援以下客製化：
- 預告片長度與位置
- 單字高亮樣式
- 字幕字型與位置
- 輸出資料夾結構
- GPU 選擇

## 疑難排解

- 若無法啟動，請檢查 systemd 狀態與日誌
- 若影片處理失敗，請確認 FFmpeg 安裝是否正確
- GPU 相關問題，請確認 CUDA 與 GPU 狀態
- 確認 conda 環境正確啟用

## 授權

[請在此填入授權資訊]

## 致謝

LazyEdit 使用以下開源工具與套件：
- FFmpeg 進行影片處理
- OpenAI 模型提供 AI 能力
- Tornado 網頁框架
- MoviePy 影片編輯
- CJKWrap 多語言排版
