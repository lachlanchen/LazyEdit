[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>生成、字幕処理、メタデータ作成、必要に応じた公開までを扱う</b> AI支援の動画ワークフロー。
  <br />
  <sub>Upload or generate -> transcribe -> translate/polish -> burn subtitles -> caption/keyframes -> metadata -> publish</sub>
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

## 📌 クイックファクト

LazyEdit は、制作・処理・任意の公開までをカバーするエンドツーエンドの AI 支援動画ワークフローです。プロンプトベースの生成（Stage A/B/C）、メディア処理 API、字幕レンダリング、キーフレームキャプション生成、メタデータ作成、AutoPublish 連携を統合しています。

| クイックファクト | 値 |
| --- | --- |
| 📘 正式な README | `README.md`（このファイル） |
| 🌐 言語版 | `i18n/README.*.md`（各 README の先頭に言語バーを 1 つだけ保持） |
| 🧠 バックエンド開始点 | `app.py`（Tornado） |
| 🖥️ フロントエンドアプリ | `app/`（Expo web/mobile） |
| 🧩 ランタイム方式 | `python app.py`（手動）、`./start_lazyedit.sh`（tmux）、`lazyedit.service`（任意） |
| 🎯 主要参照 | `README.md`、`references/QUICKSTART.md`、`references/API_GUIDE.md`、`references/APP_GUIDE.md` |

## 🧭 目次

- [Overview](#overview)
- [Quick Facts](#-quick-facts)
- [At a Glance](#at-a-glance)
- [Architecture Snapshot](#architecture-snapshot)
- [Demos](#demos)
- [Features](#features)
- [Documentation & i18n](#-documentation--i18n)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Cheat Sheet](#-command-cheat-sheet)
- [Usage](#usage)
- [Configuration](#configuration)
- [Configuration Files](#-configuration-files)
- [API Examples](#api-examples)
- [Examples](#examples)
- [Development Notes](#development-notes)
- [Testing](#testing)
- [Assumptions & Known Limits](#-assumptions--known-limits)
- [Deployment & Sync Notes](#deployment--sync-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Support](#-support)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## ✨ Overview

LazyEdit は、Tornado バックエンド（`app.py`）と Expo フロントエンド（`app/`）を中核に構成されています。

> 注意: マシンごとでリポジトリや実行環境が異なる場合、既存のデフォルト値を消去せず、環境変数で上書きしてください。

| 利用される理由 | 実際の効果 |
| --- | --- |
| 統一されたオペレーターフロー | 1 つの流れで Upload / Generate / Remix / Publish を実行 |
| API ファースト設計 | スクリプト化しやすく、他ツールとの統合も容易 |
| ローカルファーストな実行 | tmux + サービス運用パターンに最適 |

| Step | 処理内容 |
| --- | --- |
| 1 | 動画をアップロードまたは生成 |
| 2 | 文字起こしと、必要に応じた字幕の翻訳 |
| 3 | レイアウト制御付きで多言語字幕を焼き込み |
| 4 | キーフレーム、キャプション、メタデータを生成 |
| 5 | パッケージ化して、必要に応じて AutoPublish で公開 |

### Pipeline focus

- 単一のオペレータ UI からアップロード、生成、リミックス、ライブラリ管理を行う。
- 文字起こし、字幕の整形/翻訳、焼き込み、メタデータ生成の一連処理を API ファーストで実装。
- オプションで生成プロバイダー（`agi/` 内の Veo / Venice / A2E / Sora ヘルパー）を統合。
- オプションで `AutoPublish` への公開ハンドオフを実施。

## 🎯 At a Glance

| 項目 | LazyEdit に含まれる内容 | 状態 |
| --- | --- | --- |
| コアアプリ | Tornado API backend + Expo web/mobile frontend | ✅ |
| メディアパイプライン | ASR、字幕翻訳・整形、焼き込み、キーフレーム、キャプション、メタデータ | ✅ |
| 生成 | Stage A/B/C および `agi/` のプロバイダー補助ルート | ✅ |
| 配信 | AutoPublish 連携（任意） | 🟡 Optional |
| 実行モデル | ローカルファーストなスクリプト、tmux ワークフロー、systemd サービス（任意） | ✅ |

## 🏗️ Architecture Snapshot

このリポジトリは、UI レイヤーを備えた API ファーストのメディアパイプラインとして構成されています。

- `app.py` は Tornado のエントリーポイントで、アップロード、処理、生成、公開ハンドオフ、メディア配信のルートを統合管理。
- `lazyedit/` はモジュール化されたコア処理群（DB 永続化、翻訳、字幕焼き込み、キャプション、メタデータ、プロバイダーアダプター）を含みます。
- `app/` は Expo Router アプリ（web/mobile）で、アップロード、処理、プレビュー、公開フローを操作する UI です。
- `config.py` は環境変数読込とデフォルト/フォールバックの実行パスを一元化。
- `start_lazyedit.sh` と `lazyedit_config.sh` は、tmux ベースの再現性あるローカル/デプロイ実行を提供。

| レイヤー | 主なパス | 責務 |
| --- | --- | --- |
| API とオーケストレーション | `app.py`, `config.py` | エンドポイント、ルーティング、環境変数解決 |
| 処理コア | `lazyedit/`, `agi/` | 字幕・キャプション・メタデータのパイプライン、およびプロバイダー |
| UI | `app/` | オペレーター体験（Expo による web/mobile） |
| ランタイムスクリプト | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | ローカル/サービス起動と運用 |

高レベルフロー:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

以下は、取り込みからメタデータ生成までの主要なオペレーターパスを示した画面です。

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

- ✨ Stage A/B/C を使うプロンプトベース生成ワークフロー。Sora と Veo の統合パスを含みます。
- 🧵 文字起こし -> 字幕整形/翻訳 -> 焼き込み -> キーフレーム -> キャプション -> メタデータまでをつなぐ完全パイプライン。
- 🌏 furigana、IPA、ローマ字系の補助パスを含む多言語字幕の構成。
- 🔌 アップロード、処理、メディア配信、公開キューを提供する API ファースト backend。
- 🚚 ソーシャル配信先連携向けに AutoPublish を任意で統合。
- 🖥️ tmux 起動スクリプトで backend と Expo の統合ワークフローをサポート。

## 🌍 Documentation & i18n

- 正本: `README.md`
- 言語版: `i18n/README.*.md`
- 言語ナビゲーション: 各 README の先頭に言語バーを 1 行のみ配置（重複なし）
- 本リポジトリの対応言語: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

English 版と翻訳版が一致しない場合は、英語 README をソース・オブ・トゥルースとして扱い、各言語ファイルを順次更新します。

| i18n ポリシー | ルール |
| --- | --- |
| Canonical source | `README.md` を正本として保持 |
| Language bar | 各 README の先頭に言語バーを **1 行のみ** |

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

サブモジュール/外部依存ノート:
- このリポジトリの Git submodule には `AutoPublish`、`AutoPubMonitor`、`whisper_with_lang_detect`、`vit-gpt2-image-captioning`、`clip-gpt-captioning`、`furigana` が含まれます。
- 本運用では `furigana` と `echomind` は外部依存として扱い、編集しない方針です。不明な場合は upstream を保全し、in-place 編集は避けてください。

## ✅ Prerequisites

| 依存 | 補足 |
| --- | --- |
| Linux environment | `systemd` / `tmux` の運用スクリプトは Linux 向け |
| Python 3.10+ | Conda 環境 `lazyedit` を使用 |
| Node.js 20+ + npm | `app/` の Expo アプリに必要 |
| FFmpeg | `PATH` 上で利用可能であること |
| PostgreSQL | ローカル peer 認証または DSN ベースの接続 |
| Git submodules | 主要パイプラインのため必須 |

## 🚀 Installation

1. サブモジュールを含めてクローンし初期化:

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

3. オプション（システムレベルインストール、service モード）:

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

サービスインストールの注意:
- `install_lazyedit.sh` は `ffmpeg` と `tmux` をインストールし、`lazyedit.service` を作成します。
- `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` は生成されません。既に存在し、正しく設定されている必要があります。

## ⚡ Quick Start

Backend + frontend をローカルで起動（最小手順）:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

別シェルで:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

オプションのローカル DB ブートストラップ:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| ローカル開発（手動） | `python app.py` + Expo コマンド | `8787` | `8091`（例） |
| tmux での起動 | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd サービス | `sudo systemctl start lazyedit.service` | 設定/環境依存 | N/A |

## 🧭 Command Cheat Sheet

| タスク | コマンド |
| --- | --- |
| サブモジュール初期化 | `git submodule update --init --recursive` |
| backend のみ起動 | `python app.py` |
| backend + Expo を tmux 起動 | `./start_lazyedit.sh` |
| tmux 停止 | `./stop_lazyedit.sh` |
| tmux セッション接続 | `tmux attach -t lazyedit` |
| サービス状態確認 | `sudo systemctl status lazyedit.service` |
| サービスログ | `sudo journalctl -u lazyedit.service` |
| DB スモークテスト | `python db_smoke_test.py` |
| pytest スモークテスト | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### Development: backend only

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

現在のデプロイスクリプトで使う代替エントリ:

```bash
python app.py -m lazyedit
```

バックエンドの既定 URL: `http://localhost:8787`（`config.py` で設定、`PORT` または `LAZYEDIT_PORT` で上書き可）。

### Development: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

`start_lazyedit.sh` の既定ポート:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

セッション接続:

```bash
tmux attach -t lazyedit
```

セッション停止:

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

`.env.example` を `.env` にコピーして、パスとシークレットを更新:

```bash
cp .env.example .env
```

設定の優先順位:

- `config.py` は `.env` の値を読み込む一方、すでに shell で export されたキーは上書きしません。
- 実行時値は、shell の環境変数 -> `.env` -> コード既定値 の順で決まります。
- tmux/service 実行時は、`lazyedit_config.sh` が起動/セッション変数（`LAZYEDIT_DIR`、`CONDA_ENV`、`APP_ARGS`、ポート）を制御します。

### Key variables

| 変数 | 用途 | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | バックエンドポート | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | メディアのルートディレクトリ | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | ローカル DB fallback: `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish endpoint | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish リクエストタイムアウト（秒） | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD スクリプトパス | 環境依存 |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR モデル名 | `large-v3` / `large-v2`（例） |
| `LAZYEDIT_CAPTION_PYTHON` | キャプションパイプライン用 Python 実行環境 | 環境依存 |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | 主系キャプションルート/スクリプト | 環境依存 |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | 代替キャプション用スクリプト/作業ディレクトリ | 環境依存 |
| `GRSAI_API_*` | Veo/GRSAI 統合設定 | 環境依存 |
| `VENICE_*`, `A2E_*` | Venice/A2E 統合設定 | 環境依存 |
| `OPENAI_API_KEY` | OpenAI を使う機能で必須 | 未設定 |

マシン固有の補足:
- `app.py` では CUDA の挙動が設定される場合があります（`CUDA_VISIBLE_DEVICES`）。
- 既定パスの一部はワークステーション固有です。持ち運び用には `.env` で上書きしてください。
- `lazyedit_config.sh` は tmux/セッション起動変数をデプロイスクリプトに合わせて制御します。

## 🧾 Configuration Files

| ファイル | 用途 |
| --- | --- |
| `.env.example` | バックエンド/サービスで使う環境変数のテンプレート |
| `.env` | ローカル設定上書き。`config.py` / `app.py` が存在時に読み込む |
| `config.py` | バックエンド既定値と環境解決 |
| `lazyedit_config.sh` | tmux/service 用実行プロファイル（deploy パス、conda env、アプリ引数、セッション名） |
| `start_lazyedit.sh` | 指定ポートで backend + Expo を tmux 起動 |
| `install_lazyedit.sh` | `lazyedit.service` を作成し、既存 script/config の検証を行う |

可搬性を高める推奨更新順:
1. `.env.example` を `.env` へコピー。
2. `.env` に `LAZYEDIT_*` でパス/API 関連の値を設定。
3. tmux/service デプロイ動作に必要な場合のみ `lazyedit_config.sh` を調整。

## 🔌 API Examples

Base URL の例は `http://localhost:8787` を前提とします。

| API グループ | 代表エンドポイント |
| --- | --- |
| アップロード / メディア | `/upload`, `/upload-stream`, `/media/*` |
| 動画レコード | `/api/videos`, `/api/videos/{id}` |
| 処理 | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| 公開 | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| 生成 | `/api/videos/generate` (+ app.py の provider routes) |

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

More endpoints and payload details: `references/API_GUIDE.md`。

関連する主要エンドポイント:
- 動画ライフサイクル: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- 処理アクション: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- 生成 / provider 系: `/api/videos/generate` と、`app.py` で公開される Venice/A2E routes
- 配信: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

バックエンドが `8887` の場合:

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

対応秒数: `4`, `8`, `12`。
対応サイズ: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`。

## 🧪 Development Notes

- Conda 環境 `lazyedit` の `python` を使ってください（`python3` を前提にしない）。
- 大きなメディアは Git にコミットせず、`DATA/` または外部ストレージへ。
- パイプラインコンポーネントの解決に問題がある場合は、サブモジュールを初期化/更新する。
- 変更は範囲を絞り、不要な大規模フォーマット変更を避ける。
- フロントエンド側では API URL を `EXPO_PUBLIC_API_URL` で制御。
- 開発時の CORS はアプリ開発向けに開放されています。

Submodule and external dependency policy:
- 外部依存は upstream 管理として扱います。本リポジトリの運用上、意図せずサブモジュール内部を編集しない。
- 運用ガイドでは、`furigana`（ローカル設定では `echomind` が加わる場合あり）を外部依存として扱い、編集が必要な場合を除き in-place 変更を避ける。

Helpful references:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Security/config hygiene:
- API キー/シークレットは環境変数管理。認証情報をコミットしない。
- マシン個別の上書きは `.env`、公開テンプレートは `.env.example` を維持。
- CUDA/GPU の挙動がホストで異なる場合、ハードコーディングせず環境変数で上書きする。

## ✅ Testing

現時点での正式テストは最小限で、主に DB 向けです。

| Validation layer | Command or method |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | Web UI + API を `DATA/` の短いサンプルで実行 |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

機能検証は、`DATA/` の短いサンプルクリップで Web UI と API フローを使って行ってください。

Assumptions and portability notes:
- コード内の既定パスの一部は、ワークステーション固有のフォールバックとして残っています（現行状態として想定）。
- 既定パスが環境に存在しない場合、対応する `LAZYEDIT_*` 変数を `.env` で設定する。
- マシン依存値が不明な場合は既存設定を残しつつ明示的上書きを追加し、既定値を削除しない。

## 🧱 Assumptions & Known Limits

- backend の依存はルートのロックファイルで固定されていないため、環境再現性はローカル運用の管理に依存。
- `app.py` は現状モジュール分割を行わず、大きなルート面を持つ意図的なモノリシック構成。
- ほとんどの検証は統合/手動（UI + API + サンプルメディア）で、形式的な自動テストは限定的。
- 運用ディレクトリ（`DATA/`, `temp/`, `translation_logs/`）は出力が増えやすい。
- サブモジュールは全機能に必要。部分チェックアウトはスクリプト欠落エラーを起こしやすい。

## 🚢 Deployment & Sync Notes

既知のパスと同期フロー（運用ドキュメント基準）:

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` on `lazyingart`

| Environment | Path | Notes |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Main source + submodules |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` in ops docs |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Monitor/sync/process sessions |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull after submodule updates |

`AutoPublish/` の更新を push 後は公開先で pull:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| 問題 | 確認 / 対処 |
| --- | --- |
| パイプラインモジュールまたはスクリプトが見つからない | `git submodule update --init --recursive` を実行 |
| FFmpeg が見つからない | FFmpeg をインストールし、`ffmpeg -version` を確認 |
| ポート競合 | backend は `8787` が既定、`start_lazyedit.sh` は `18787` が既定。`LAZYEDIT_PORT` または `PORT` を明示指定 |
| Expo が backend に接続できない | `EXPO_PUBLIC_API_URL` が稼働中の backend host/port を指しているか確認 |
| DB 接続エラー | PostgreSQL と DSN/env を確認。任意で `python db_smoke_test.py` を実行 |
| GPU/CUDA 問題 | インストール済み Torch スタックで driver/CUDA 互換を確認 |
| インストール時のサービス失敗 | `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` が存在するか確認 |

## 🗺️ Roadmap

- インアプリで、行単位制御付き A/B プレビューを用いた字幕/セグメント編集。
- コア API フロー向けのエンドツーエンドテスト強化。
- i18n README とデプロイモード間のドキュメント収束。
- 生成プロバイダーの再試行やステータス可視化の強化。

## 🤝 Contributing

コントリビュートは歓迎します。

1. Fork して feature branch を作成。
2. コミットは小さく、目的を絞る。
3. ローカルで変更を検証（`python app.py`、主要 API フロー、必要ならアプリ連携）。
4. PR を作成し、目的、再現手順、前後比較を添付（UI 変更時はスクリーンショット）。

実運用ガイドライン:
- Python スタイル（PEP 8, 4 spaces, snake_case）を守る。
- 認証情報や大容量バイナリをコミットしない。
- 挙動が変わる変更時は docs/config scripts も更新する。
- 推奨コミット形式: short, imperative, scoped（例: `fix ffmpeg 7 compatibility`）。

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit は次のオープンソースライブラリ・サービスの上に成り立っています。
- FFmpeg for media processing
- Tornado for backend APIs
- MoviePy for editing workflows
- OpenAI models for AI-assisted pipeline tasks
- CJKWrap and multilingual text tooling in subtitle workflows
