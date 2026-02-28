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
  <b>AI支援の動画ワークフロー</b>で、生成、字幕処理、メタデータ作成、任意の公開までを一貫して扱えます。
  <br />
  <sub>Upload or generate -> transcribe -> translate/polish -> burn subtitles -> caption/keyframes -> metadata -> publish</sub>
</p>

# LazyEdit

LazyEdit は、作成・処理・任意公開までを一気通貫で行う AI 支援動画ワークフローです。プロンプトベースの生成（Stage A/B/C）、メディア処理 API、字幕レンダリング、キーフレームキャプション、メタデータ生成、AutoPublish 連携を統合しています。

| クイック情報 | 内容 |
| --- | --- |
| 📘 正式 README | `README.md`（このファイル） |
| 🌐 多言語版 | `i18n/README.*.md`（先頭の言語バーは 1 本に統一） |
| 🧠 バックエンド入口 | `app.py`（Tornado） |
| 🖥️ フロントエンド | `app/`（Expo web/mobile） |

## 🧭 Contents

- [Overview](#-overview)
- [At a Glance](#-at-a-glance)
- [Architecture Snapshot](#-architecture-snapshot)
- [Demos](#-demos)
- [Features](#-features)
- [Documentation & i18n](#-documentation--i18n)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Command Cheat Sheet](#-command-cheat-sheet)
- [Usage](#️-usage)
- [Configuration](#️-configuration)
- [Configuration Files](#-configuration-files)
- [API Examples](#-api-examples)
- [Examples](#-examples)
- [Development Notes](#-development-notes)
- [Testing](#-testing)
- [Assumptions & Known Limits](#-assumptions--known-limits)
- [Deployment & Sync Notes](#-deployment--sync-notes)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [Support](#️-support)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

## ✨ Overview

LazyEdit は Tornado バックエンド（`app.py`）と Expo フロントエンド（`app/`）を中心に構成されています。

> 注: マシンごとにリポジトリ/ランタイム差異がある場合、既存のデフォルトを削除せず、環境変数で上書きしてください。

| 使われる理由 | 実際のメリット |
| --- | --- |
| 統一オペレーター導線 | 1つの流れで Upload/Generate/Remix/Publish |
| API ファースト設計 | スクリプト化や他ツール連携が容易 |
| ローカルファースト運用 | tmux + service ベース運用に適合 |

| Step | 処理内容 |
| --- | --- |
| 1 | 動画をアップロードまたは生成 |
| 2 | 字幕を文字起こしし、必要に応じて翻訳 |
| 3 | レイアウト制御付きで多言語字幕を焼き込み |
| 4 | キーフレーム、キャプション、メタデータを生成 |
| 5 | パッケージ化し、必要に応じて AutoPublish で公開 |

### Pipeline focus

- 単一のオペレーター UI で、アップロード、生成、リミックス、ライブラリ管理まで対応。
- 文字起こし、字幕整形/翻訳、焼き込み、メタデータ生成を API ファーストで処理。
- 任意の生成プロバイダ連携（`agi/` の Veo / Venice / A2E / Sora ヘルパー）に対応。
- `AutoPublish` への公開ハンドオフを任意で利用可能。

## 🎯 At a Glance

| 領域 | LazyEdit に含まれるもの | 状態 |
| --- | --- | --- |
| Core app | Tornado API backend + Expo web/mobile frontend | ✅ |
| Media pipeline | ASR, subtitle translation/polish, burn-in, keyframes, captions, metadata | ✅ |
| Generation | Stage A/B/C and provider helper routes (`agi/`) | ✅ |
| Distribution | Optional AutoPublish handoff | 🟡 Optional |
| Runtime model | Local-first scripts, tmux workflows, optional systemd service | ✅ |

## 🏗️ Architecture Snapshot

このリポジトリは、UI レイヤーを備えた API ファーストのメディアパイプラインとして構成されています。

- `app.py` は Tornado のエントリーポイントで、アップロード、処理、生成、公開ハンドオフ、メディア配信のルートを統括します。
- `lazyedit/` はパイプラインのモジュール群（DB 永続化、翻訳、字幕焼き込み、キャプション、メタデータ、プロバイダアダプタ）を提供します。
- `app/` は Expo Router アプリ（web/mobile）で、アップロード、処理、プレビュー、公開フローを操作します。
- `config.py` は環境変数の読み込みとデフォルト/フォールバック実行パスを一元管理します。
- `start_lazyedit.sh` と `lazyedit_config.sh` は、再現可能な tmux ベースのローカル/デプロイ運用を提供します。

| レイヤー | 主なパス | 役割 |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | Endpoints, routing, env resolution |
| Processing core | `lazyedit/`, `agi/` | Subtitle/caption/metadata pipeline + providers |
| UI | `app/` | Operator experience (web/mobile via Expo) |
| Runtime scripts | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Local/service startup and ops |

高レベルフロー:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

以下は、取り込みからメタデータ生成までの主要オペレーターフローの画面例です。

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

- ✨ Sora / Veo 連携パスを含む、プロンプトベース生成ワークフロー（Stage A/B/C）。
- 🧵 完全な処理パイプライン: transcription -> subtitle polish/translation -> burn-in -> keyframes -> captions -> metadata。
- 🌏 furigana/IPA/romaji 系の補助パスを含む多言語字幕合成。
- 🔌 アップロード、処理、メディア配信、公開キューを備えた API ファーストのバックエンド。
- 🚚 ソーシャル配信向けに任意で AutoPublish と連携可能。
- 🖥️ tmux 起動スクリプトによる backend + Expo の統合運用。

## 🌍 Documentation & i18n

LazyEdit は 1 つの正本英語 README（`README.md`）と、`i18n/` 配下の各言語版で運用します。

- 正本ソース: `README.md`
- 言語別ファイル: `i18n/README.*.md`
- 言語ナビゲーション: 各 README の先頭に 1 行のみ（重複させない）
- 現在の対応言語: Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

翻訳版と英語版に差異がある場合は、英語 README を正として各言語ファイルを順番に更新してください。

| i18n 方針 | ルール |
| --- | --- |
| Canonical source | `README.md` を常に正本として扱う |
| Language bar | 先頭に言語オプション行をちょうど 1 本 |
| Update order | 英語を先に更新し、`i18n/README.*.md` を順次更新 |

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

サブモジュール/外部依存に関する注記:
- このリポジトリの Git サブモジュールには `AutoPublish`、`AutoPubMonitor`、`whisper_with_lang_detect`、`vit-gpt2-image-captioning`、`clip-gpt-captioning`、`furigana` が含まれます。
- 運用ガイド上、このリポジトリでは `furigana` と `echomind` を外部の読み取り専用依存として扱います。迷う場合は upstream を保持し、直接編集を避けてください。

## ✅ Prerequisites

| Dependency | Notes |
| --- | --- |
| Linux environment | `systemd`/`tmux` scripts are Linux-oriented |
| Python 3.10+ | Use Conda env `lazyedit` |
| Node.js 20+ + npm | Required for Expo app in `app/` |
| FFmpeg | Must be available on `PATH` |
| PostgreSQL | Local peer auth or DSN-based connection |
| Git submodules | Required for key pipelines |

## 🚀 Installation

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

3. 任意: システムレベルインストール（service モード）:

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

サービスインストールに関する注記:
- `install_lazyedit.sh` は `ffmpeg` と `tmux` をインストールし、`lazyedit.service` を作成します。
- `lazyedit_config.sh`、`start_lazyedit.sh`、`stop_lazyedit.sh` は自動生成されません。事前に存在し内容が正しい必要があります。

## ⚡ Quick Start

backend + frontend をローカルで実行（最短手順）:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

別シェルで実行:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

任意のローカル DB 初期化:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| Local dev (manual) | `python app.py` + Expo command | `8787` | `8091` (example command) |
| Tmux orchestrated | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd service | `sudo systemctl start lazyedit.service` | Config/env-driven | N/A |

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

現在のデプロイスクリプトで使われる代替エントリ:

```bash
python app.py -m lazyedit
```

backend の既定 URL: `http://localhost:8787`（`config.py` 基準。`PORT` または `LAZYEDIT_PORT` で上書き可能）。

### Development: backend + Expo app (tmux)

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

### Service management

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Configuration

`.env.example` を `.env` にコピーし、パス/シークレットを更新してください:

```bash
cp .env.example .env
```

設定優先順位の注記:

- `config.py` は `.env` の値を読み込みますが、シェルで export 済みのキーは上書きしません。
- 実行時の値は、シェル環境変数 -> `.env` -> コード既定値の順で決まります。
- tmux/service 実行時は `lazyedit_config.sh` が起動/セッション変数（`LAZYEDIT_DIR`、`CONDA_ENV`、`APP_ARGS`、ポート）を制御します。

### Key variables

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

マシン固有の注記:
- `app.py` は CUDA 挙動を設定する場合があります（`CUDA_VISIBLE_DEVICES` の利用）。
- 既定値の一部パスはワークステーション固有のため、可搬性が必要なら `.env` で上書きしてください。
- `lazyedit_config.sh` はデプロイスクリプト向けの tmux/セッション起動変数を制御します。

## 🧾 Configuration Files

| File | Purpose |
| --- | --- |
| `.env.example` | Template for environment variables used by backend/services |
| `.env` | Machine-local overrides; loaded by `config.py`/`app.py` if present |
| `config.py` | Backend defaults and environment resolution |
| `lazyedit_config.sh` | tmux/service runtime profile (deploy path, conda env, app args, session name) |
| `start_lazyedit.sh` | Launches backend + Expo in tmux with selected ports |
| `install_lazyedit.sh` | Creates `lazyedit.service` and validates existing scripts/config |

可搬性を高める推奨更新順:
1. `.env.example` を `.env` にコピーする。
2. `.env` でパス/API 関連の `LAZYEDIT_*` を設定する。
3. tmux/service 運用に必要な場合のみ `lazyedit_config.sh` を調整する。

## 🔌 API Examples

Base URL の例は `http://localhost:8787` を想定しています。

| API group | Representative endpoints |
| --- | --- |
| Upload and media | `/upload`, `/upload-stream`, `/media/*` |
| Video records | `/api/videos`, `/api/videos/{id}` |
| Processing | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publish | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generation | `/api/videos/generate` (+ provider routes in `app.py`) |

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

より詳しいエンドポイントとペイロードは `references/API_GUIDE.md` を参照してください。

よく使う関連エンドポイント群:
- 動画ライフサイクル: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- 処理アクション: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- 生成/プロバイダ: `/api/videos/generate` と `app.py` で公開される Venice/A2E ルート
- 配信: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

backend が `8887` の場合:

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

- Conda 環境 `lazyedit` の `python` を使ってください（システム `python3` 前提にしない）。
- 大容量メディアは Git に含めず、`DATA/` または外部ストレージに保存してください。
- パイプライン部品が解決できない場合は、サブモジュールを初期化/更新してください。
- 変更範囲は絞り、無関係な大規模フォーマット変更を避けてください。
- フロントエンド開発時の API URL は `EXPO_PUBLIC_API_URL` で制御します。
- バックエンドの CORS はアプリ開発向けにオープン設定です。

サブモジュールと外部依存の運用方針:
- 外部依存は upstream 管理として扱い、対象プロジェクトを意図して作業するとき以外はサブモジュール内部を編集しないでください。
- このリポジトリ運用では `furigana`（ローカル構成により `echomind` も）を外部依存パスとして扱います。迷ったら upstream を維持し、インプレース編集を避けてください。

参考ドキュメント:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

セキュリティ/設定衛生:
- API キーやシークレットは環境変数で管理し、認証情報をコミットしないでください。
- マシンローカルの上書きは `.env` を使い、公開テンプレートは `.env.example` を維持してください。
- CUDA/GPU 挙動がホストごとに異なる場合は、ハードコードせず環境変数で上書きしてください。

## ✅ Testing

現時点での正式なテスト対象は最小限で、主に DB 周辺です。

| Validation layer | Command or method |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | Web UI + API run using short sample in `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

機能検証では、`DATA/` の短いサンプルクリップを使って Web UI と API フローを確認してください。

前提と可搬性の注記:
- コード中の既定パスの一部はワークステーション固有フォールバックです（現行状態として想定）。
- 既定パスが自分のマシンに存在しない場合は、対応する `LAZYEDIT_*` を `.env` で設定してください。
- マシン固有値に確信が持てない場合、既存設定を削除せず、明示的な上書きを追加してください。

## 🧱 Assumptions & Known Limits

- backend 依存セットはルート lockfile で厳密固定されておらず、再現性はローカル環境管理に依存します。
- `app.py` は現行状態で意図的にモノリシックで、ルート面積が大きめです。
- パイプライン検証の多くは integration/manual（UI + API + サンプルメディア）で、自動テストは限定的です。
- 実行ディレクトリ（`DATA/`, `temp/`, `translation_logs/`）は運用出力のため大きくなり得ます。
- 全機能の利用にはサブモジュールが必要で、部分 checkout ではスクリプト欠落エラーが発生しやすいです。

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

このリポジトリから `AutoPublish/` を更新して push した後、公開ホスト側で pull:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| Problem | Check / Fix |
| --- | --- |
| Missing pipeline modules or scripts | Run `git submodule update --init --recursive` |
| FFmpeg not found | Install FFmpeg and confirm `ffmpeg -version` works |
| Port conflicts | Backend defaults to `8787`; `start_lazyedit.sh` defaults to `18787`; set `LAZYEDIT_PORT` or `PORT` explicitly |
| Expo cannot reach backend | Ensure `EXPO_PUBLIC_API_URL` points to active backend host/port |
| Database connection issues | Verify PostgreSQL + DSN/env vars; optional smoke check: `python db_smoke_test.py` |
| GPU/CUDA issues | Confirm driver/CUDA compatibility with installed Torch stack |
| Service script fails at install | Ensure `lazyedit_config.sh`, `start_lazyedit.sh`, and `stop_lazyedit.sh` exist before running installer |

## 🗺️ Roadmap

- 行単位制御付き A/B プレビューを含む、アプリ内字幕/セグメント編集。
- コア API フロー向けエンドツーエンドテストの強化。
- i18n README バリアントとデプロイモード間のドキュメント収束。
- 生成プロバイダのリトライ制御とステータス可視化の強化。

## 🤝 Contributing

コントリビューションを歓迎します。

1. Fork して機能ブランチを作成。
2. コミットは焦点を絞って小さく保つ。
3. ローカルで変更を検証（`python app.py`、主要 API フロー、必要に応じてアプリ連携）。
4. 目的、再現手順、変更前後メモ（UI 変更時はスクリーンショット）付きで PR を作成。

実践ガイドライン:
- Python スタイル（PEP 8、4 スペース、snake_case）に従う。
- 認証情報や大容量バイナリをコミットしない。
- 振る舞いが変わる場合は docs/config scripts も更新する。
- 推奨コミットスタイル: short, imperative, scoped（例: `fix ffmpeg 7 compatibility`）。

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit は以下を含むオープンソースライブラリ/サービスを基盤にしています。
- FFmpeg（メディア処理）
- Tornado（バックエンド API）
- MoviePy（編集ワークフロー）
- OpenAI models（AI 支援パイプライン処理）
- CJKWrap と多言語テキスト処理（字幕ワークフロー）
