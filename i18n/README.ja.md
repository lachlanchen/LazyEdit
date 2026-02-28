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

LazyEdit は、作成・処理・（任意の）公開までを一気通貫で扱える、AI 支援の動画ワークフローです。プロンプトベース生成（Stage A/B/C）、メディア処理 API、字幕レンダリング、キーフレームキャプション、メタデータ生成、AutoPublish への引き渡しを統合しています。

## ✨ 概要

LazyEdit は Tornado バックエンド（`app.py`）と Expo フロントエンド（`app/`）を中心に構成されています。

| Step | 内容 |
| --- | --- |
| 1 | 動画をアップロードまたは生成 |
| 2 | 字幕を文字起こしし、必要に応じて翻訳 |
| 3 | レイアウト制御付きで多言語字幕を焼き込み |
| 4 | キーフレーム、キャプション、メタデータを生成 |
| 5 | パッケージ化し、必要に応じて AutoPublish で公開 |

### パイプラインの主眼

- 単一のオペレーター UI で、アップロード・生成・リミックス・ライブラリ管理まで実行。
- 文字起こし、字幕の整形/翻訳、焼き込み、メタデータ生成を API ファーストで処理。
- 生成プロバイダ連携を任意で利用可能（`agi/` の Veo / Venice / A2E / Sora ヘルパー）。
- `AutoPublish` 経由の公開ハンドオフを任意で利用可能。

## 🎯 ひと目で分かる構成

| 領域 | LazyEdit に含まれるもの |
| --- | --- |
| コアアプリ | Tornado API バックエンド + Expo Web/モバイル フロントエンド |
| メディアパイプライン | ASR、字幕翻訳/整形、焼き込み、キーフレーム、キャプション、メタデータ |
| 生成 | Stage A/B/C とプロバイダヘルパールート（`agi/`） |
| 配信 | 任意の AutoPublish ハンドオフ |
| 実行モデル | ローカルファーストのスクリプト、tmux ワークフロー、任意の systemd サービス |

## 🎬 デモ

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>ホーム · アップロード</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>ホーム · 生成</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>ホーム · リミックス</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>ライブラリ</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>動画概要</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>翻訳プレビュー</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>焼き込みスロット</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>焼き込みレイアウト</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>キーフレーム + キャプション</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>メタデータ生成</sub>
    </td>
  </tr>
</table>

## 🧩 機能

- Sora / Veo 連携パスを含む、プロンプトベース生成ワークフロー（Stage A/B/C）。
- 完全な処理パイプライン：文字起こし -> 字幕整形/翻訳 -> 焼き込み -> キーフレーム -> キャプション -> メタデータ。
- furigana / IPA / romaji 関連のサポートパスを含む多言語字幕合成。
- アップロード、処理、メディア配信、公開キューの各エンドポイントを備えた API ファーストのバックエンド。
- ソーシャルプラットフォーム連携向けの任意の AutoPublish 統合。
- tmux 起動スクリプトでバックエンド + Expo の統合ワークフローをサポート。

## 🗂️ プロジェクト構成

```text
LazyEdit/
├── app.py                           # Tornado バックエンドのエントリーポイントと API オーケストレーション
├── app/                             # Expo フロントエンド（web/mobile）
├── lazyedit/                        # コアパイプラインモジュール（翻訳、メタデータ、burner、DB、テンプレート）
├── agi/                             # 生成プロバイダ抽象化（Sora/Veo/A2E/Venice ルート）
├── DATA/                            # 実行時メディア入出力（このワークスペースでは symlink）
├── translation_logs/                # 翻訳ログ
├── temp/                            # 実行時一時ファイル
├── install_lazyedit.sh              # systemd インストーラー（config/start/stop スクリプトを前提）
├── start_lazyedit.sh                # バックエンド + Expo 用 tmux ランチャー
├── stop_lazyedit.sh                 # tmux 停止ヘルパー
├── lazyedit_config.sh               # デプロイ/実行時シェル設定
├── config.py                        # 環境/設定解決（ポート、パス、autopublish URL）
├── .env.example                     # 環境上書きテンプレート
├── references/                      # 追加ドキュメント（API ガイド、クイックスタート、デプロイノート）
├── AutoPublish/                     # サブモジュール（任意の公開パイプライン）
├── AutoPubMonitor/                  # サブモジュール（監視/同期自動化）
├── whisper_with_lang_detect/        # サブモジュール（ASR/VAD）
├── vit-gpt2-image-captioning/       # サブモジュール（主要キャプショナー）
├── clip-gpt-captioning/             # サブモジュール（フォールバックキャプショナー）
└── furigana/                        # ワークフロー内の外部依存（このチェックアウトでは追跡サブモジュール）
```

## ✅ 前提条件

| Dependency | Notes |
| --- | --- |
| Linux 環境 | `systemd` / `tmux` スクリプトは Linux 前提 |
| Python 3.10+ | Conda 環境 `lazyedit` を使用 |
| Node.js 20+ + npm | `app/` 内の Expo アプリに必要 |
| FFmpeg | `PATH` 上で利用可能であること |
| PostgreSQL | ローカル peer 認証または DSN 接続 |
| Git submodules | 主要パイプラインに必須 |

## 🚀 インストール

1. クローンしてサブモジュールを初期化:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Conda 環境を有効化:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. 任意: システムレベルインストール（サービスモード）:

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

サービスインストールに関する注意:
- `install_lazyedit.sh` は `ffmpeg` と `tmux` をインストールし、`lazyedit.service` を作成します。
- `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` は自動生成されません。事前に存在し、内容が正しい必要があります。

## 🛠️ 使い方

### 開発: バックエンドのみ

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

現在のデプロイスクリプトで使われている代替エントリ:

```bash
python app.py -m lazyedit
```

バックエンド既定 URL: `http://localhost:8787`（`config.py` 由来。`PORT` または `LAZYEDIT_PORT` で上書き可能）。

### 開発: バックエンド + Expo アプリ（tmux）

```bash
./start_lazyedit.sh
```

`start_lazyedit.sh` の既定ポート:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

セッションへアタッチ:

```bash
tmux attach -t lazyedit
```

セッション停止:

```bash
./stop_lazyedit.sh
```

### サービス管理

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ 設定

`.env.example` を `.env` にコピーして、パス/シークレットを更新してください:

```bash
cp .env.example .env
```

### 主要変数

| Variable | Purpose | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | バックエンドポート | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | メディアルートディレクトリ | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | ローカル DB フォールバック `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish エンドポイント | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish リクエストタイムアウト（秒） | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD スクリプトパス | 環境依存 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR モデル名 | `large-v3` / `large-v2`（例） |
| `LAZYEDIT_CAPTION_PYTHON` | キャプションパイプライン用 Python ランタイム | 環境依存 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 主要キャプションのパス/スクリプト | 環境依存 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | フォールバックキャプションのパス/スクリプト/cwd | 環境依存 |
| `GRSAI_API_*` | Veo/GRSAI 連携設定 | 環境依存 |
| `VENICE_*`, `A2E_*` | Venice/A2E 連携設定 | 環境依存 |
| `OPENAI_API_KEY` | OpenAI ベース機能に必須 | なし |

マシン固有の注意:
- `app.py` は CUDA の挙動を設定する場合があります（コードベース中の `CUDA_VISIBLE_DEVICES` 利用）。
- 既定値の一部パスはワークステーション依存です。可搬性が必要なら `.env` で上書きしてください。
- `lazyedit_config.sh` はデプロイスクリプトの tmux/セッション起動変数を制御します。

## 🔌 API 例

Base URL 例は `http://localhost:8787` を想定しています。

アップロード:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

エンドツーエンド処理:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

動画一覧:

```bash
curl http://localhost:8787/api/videos
```

公開パッケージ:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

さらに多くのエンドポイントとペイロード詳細: `references/API_GUIDE.md`。

## 🧪 例

### フロントエンドのローカル実行（web）

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

バックエンドが `8887` の場合:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android エミュレーター

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS シミュレーター（macOS）

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### 任意: Sora 生成ヘルパー

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

対応秒数: `4`, `8`, `12`。
対応サイズ: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`。

## 🧪 開発メモ

- Conda 環境 `lazyedit` の `python` を使用してください（システム `python3` 前提にしない）。
- 大容量メディアは Git に含めず、`DATA/` または外部ストレージへ保存。
- パイプライン要素の解決に失敗したら、サブモジュールの初期化/更新を実施。
- 変更範囲は絞り、無関係な大規模フォーマット変更は避ける。
- フロントエンド開発時のバックエンド API URL は `EXPO_PUBLIC_API_URL` で制御。
- アプリ開発向けに、バックエンドの CORS はオープン設定。

サブモジュールおよび外部依存の運用方針:
- 外部依存は upstream 側の所有物として扱ってください。このリポジトリの運用では、意図的に当該プロジェクトを作業するとき以外、サブモジュール内部の編集は避けます。
- このリポジトリの運用ガイドでは `furigana`（ローカル構成によっては `echomind`）を外部依存パスとして扱います。判断に迷う場合は upstream を維持し、インプレース編集を避けてください。

参考ドキュメント:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ テスト

現在の正式なテスト対象は最小限で、主に DB 周辺です。

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

機能検証には、`DATA/` に短いサンプルクリップを置いて Web UI と API フローを使用してください。

## 🚢 デプロイと同期メモ

既知のパスと同期フロー（リポジトリ運用ドキュメントより）:

- 開発ワークスペース: `/home/lachlan/ProjectsLFS/LazyEdit`
- デプロイ済み LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- デプロイ済み AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- 公開システムホスト: `lazyingart` 上の `/home/lachlan/Projects/auto-publish`

このリポジトリから `AutoPublish/` の更新を push した後、公開ホスト側で pull:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 トラブルシューティング

| Problem | Check / Fix |
| --- | --- |
| パイプラインモジュールやスクリプトが不足 | `git submodule update --init --recursive` を実行 |
| FFmpeg が見つからない | FFmpeg をインストールし、`ffmpeg -version` が通ることを確認 |
| ポート競合 | バックエンド既定は `8787`、`start_lazyedit.sh` 既定は `18787`。`LAZYEDIT_PORT` または `PORT` を明示設定 |
| Expo からバックエンドに接続できない | `EXPO_PUBLIC_API_URL` が稼働中のバックエンド host/port を指しているか確認 |
| DB 接続エラー | PostgreSQL + DSN/env vars を確認。任意で `python db_smoke_test.py` を実行 |
| GPU/CUDA の問題 | インストール済み Torch スタックとのドライバ/CUDA 互換性を確認 |
| サービススクリプトのインストール失敗 | インストーラー実行前に `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` の存在を確認 |

## 🗺️ ロードマップ

- 行単位制御付き A/B プレビューを含む、アプリ内字幕/セグメント編集。
- コア API フロー向けのエンドツーエンドテストを強化。
- i18n README バリアントとデプロイモード間でドキュメントを収束。
- 生成プロバイダのリトライ制御とステータス可視化をさらに強化。

## 🤝 コントリビュート

貢献を歓迎します。

1. Fork して機能ブランチを作成。
2. コミットは焦点を絞って小さく保つ。
3. ローカルで変更を検証（`python app.py`、主要 API フロー、必要に応じてアプリ連携）。
4. 目的、再現手順、変更前後ノート（UI 変更時はスクリーンショット）付きで PR を作成。

実践ガイドライン:
- Python スタイル（PEP 8、4 スペース、snake_case）に従う。
- 認証情報や大容量バイナリはコミットしない。
- 振る舞いが変わる場合、ドキュメントや設定スクリプトも更新する。
- 推奨コミットスタイル: 短く、命令形、スコープ明確（例: `fix ffmpeg 7 compatibility`）。

## ❤️ 支援で実現できること

- <b>オープンなツールを継続</b>: ホスティング、推論、データ保存、コミュニティ運営。  
- <b>開発速度を向上</b>: EchoMind、LazyEdit、MultilingualWhisper に集中して OSS 開発するための時間を確保。  
- <b>ウェアラブル試作</b>: IdeasGlass + LightMind 向けの光学、センサー、ニューロモーフィック/エッジ部品。  
- <b>アクセスを広げる</b>: 学生、クリエイター、コミュニティ向けの導入支援。

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

## 🙏 Acknowledgements

LazyEdit は以下を含むオープンソースライブラリとサービスを基盤にしています:
- メディア処理の FFmpeg
- バックエンド API の Tornado
- 編集ワークフローの MoviePy
- AI 支援パイプライン処理の OpenAI モデル
- 字幕ワークフローの CJKWrap と多言語テキストツール群
