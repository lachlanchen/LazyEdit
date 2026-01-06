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

LazyEdit は AI 駆動の自動動画編集ツールです。プロ品質の字幕、ハイライト、単語カード、メタデータを自動生成し、AI で面倒な編集作業を効率化します。

## 特長

- **自動文字起こし**：AI による音声の文字起こし
- **自動キャプション**：映像内容の説明文を生成
- **自動字幕**：字幕を作成して直接焼き込み
- **自動ハイライト**：重要語句を自動で強調
- **自動メタデータ**：動画からメタデータを抽出・生成
- **単語カード**：語学学習用の単語カードを追加
- **ティーザー生成**：重要な場面を冒頭でリピート
- **多言語対応**：英語・中国語など複数言語に対応
- **カバー画像生成**：最適なカバー画像を抽出

## インストール

### 前提条件

- Python 3.10 以上
- FFmpeg
- CUDA 対応 GPU（文字起こしの高速化）
- Conda 環境管理

### インストール手順

1. リポジトリを取得：
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. インストールスクリプトを実行：
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

スクリプトの内容：
- 必要なシステムパッケージ（ffmpeg、tmux）をインストール
- "lazyedit" conda 環境を作成・設定
- systemd サービスを設定して自動起動
- 必要な権限を設定

## 使い方

LazyEdit は Web アプリとして動作し、http://localhost:8081 からアクセスできます。

### 動画を処理する

1. Web UI から動画をアップロード
2. LazyEdit が自動で以下を実行：
   - 文字起こしとキャプション生成
   - メタデータと学習コンテンツ生成
   - 言語検出に基づく字幕作成
   - 重要語句のハイライト
   - ティーザー生成
   - カバー画像作成
   - 処理結果のパッケージ化

### コマンドライン

以下で直接実行できます：

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## プロジェクト構成

- `app.py` - メインエントリ
- `lazyedit/` - コアモジュール
  - `autocut_processor.py` - 分割と文字起こし
  - `subtitle_metadata.py` - 字幕からメタデータ生成
  - `subtitle_translate.py` - 字幕翻訳
  - `video_captioner.py` - 映像キャプション生成
  - `words_card.py` - 単語カード生成
  - `utils.py` - ユーティリティ
  - `openai_version_check.py` - OpenAI API 互換層

## 設定

systemd サービス設定は `/etc/systemd/system/lazyedit.service` に作成されます。

LazyEdit は "lazyedit" という tmux セッションで動作し、バックグラウンドで継続稼働します。

## サービス管理

- 起動：`sudo systemctl start lazyedit.service`
- 停止：`sudo systemctl stop lazyedit.service`
- 状態：`sudo systemctl status lazyedit.service`
- ログ：`sudo journalctl -u lazyedit.service`

## 高度な使い方

以下をカスタマイズ可能です：
- ティーザーの長さと位置
- 単語ハイライトのスタイル
- 字幕フォントと配置
- 出力フォルダ構成
- GPU の選択

## トラブルシューティング

- 起動しない場合は systemd の状態とログを確認
- 処理失敗時は FFmpeg のインストール確認
- GPU 関連は CUDA と GPU の状態確認
- conda 環境が正しく有効化されているか確認

## ライセンス

[ライセンスをここに記載]

## 謝辞

LazyEdit は以下の OSS を使用しています：
- FFmpeg（動画処理）
- OpenAI モデル（AI 機能）
- Tornado Web フレームワーク
- MoviePy（動画編集）
- CJKWrap（多言語組版）
