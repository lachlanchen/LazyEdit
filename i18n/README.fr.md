[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>AI-assisted vidéo workflow</b> pour la génération, le traitement des sous-titres, les métadonnées et la publication optionnelle.
  <br />
  <sub>Importer ou générer -> transcrire -> traduire/retoucher -> incruster les sous-titres -> keyframes/captions -> métadonnées -> publier</sub>
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

LazyEdit est un workflow vidéo complet assisté par IA pour la création, le traitement et la publication optionnelle. Il combine la génération basée sur prompt (Stage A/B/C), les API de traitement média, le rendu de sous-titres, le captioning par keyframes et la génération de métadonnées, ainsi que le relais vers AutoPublish.

| Quick fact | Value |
| --- | --- |
| 📘 Canonical README | `README.md` (ce fichier) |
| 🌐 Language variants | `i18n/README.*.md` (une seule barre de langues est conservée en haut) |
| 🧠 Backend entrypoint | `app.py` (Tornado) |
| 🖥️ Frontend app | `app/` (Expo web/mobile) |
| 🧩 Runtime modes | `python app.py` (manuel), `./start_lazyedit.sh` (tmux), `lazyedit.service` optionnel |
| 🎯 Références principales | `README.md`, `references/QUICKSTART.md`, `references/API_GUIDE.md`, `references/APP_GUIDE.md` |

## 🧭 Contents

- [Overview](#-overview)
- [Quick Facts](#-quick-facts)
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
- [Usage](#-usage)
- [Configuration](#️-configuration)
- [Configuration Files](#-configuration-files)
- [API Examples](#-api-examples)
- [Examples](#-examples)
- [Development Notes](#-development-notes)
- [Testing](#-testing)
- [Assumptions & Known Limits](#-assumptions--known-limits)
- [Deployment & Sync Notes](#-deployment--sync-notes)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Support](#-support)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## ✨ Overview

LazyEdit repose sur un backend Tornado (`app.py`) et un frontend Expo (`app/`).

> Note : si les détails du dépôt ou de l’environnement diffèrent selon la machine, conservez les valeurs par défaut existantes et surchargez-les via les variables d’environnement, au lieu de supprimer les valeurs de secours spécifiques à la machine.

| Why teams use it | Practical result |
| --- | --- |
| Flux opérateur unifié | Upload/generate/remix/publish depuis une seule chaîne de travail |
| API-first design | Automatisable facilement et intégrable avec d’autres outils |
| Runtime local-first | Fonctionne avec tmux et des déploiements basés service |

| Step | What happens |
| --- | --- |
| 1 | Importer ou générer une vidéo |
| 2 | Transcrire puis traduire les sous-titres (facultatif) |
| 3 | Incruster des sous-titres multilingues avec contrôle de mise en page |
| 4 | Générer keyframes, captions et métadonnées |
| 5 | Empaqueter puis publier optionnellement via AutoPublish |

### Pipeline focus

- Upload, génération, remix et gestion de bibliothèque depuis une seule interface opérateur.
- Flux de traitement API-first pour la transcription, la correction/traduction des sous-titres, l’incrustation et les métadonnées.
- Intégrations optionnelles de providers de génération (`agi/`) pour Veo / Venice / A2E / Sora.
- Handoff de publication optionnel via `AutoPublish`.

## 🎯 At a Glance

| Area | Included in LazyEdit | Status |
| --- | --- | --- |
| Core app | API backend Tornado + frontend Expo web/mobile | ✅ |
| Media pipeline | ASR, traduction/retouche de sous-titres, burn-in, keyframes, captions, métadonnées | ✅ |
| Generation | Stage A/B/C et routes helper providers (`agi/`) | ✅ |
| Distribution | Handoff AutoPublish optionnel | 🟡 Optionnel |
| Runtime model | Scripts local-first, flux tmux, service systemd optionnel | ✅ |

## 🏗️ Architecture Snapshot

Le dépôt est organisé comme un pipeline média API-first avec une couche UI :

- `app.py` est le point d’entrée Tornado et l’orchestrateur de routes pour l’upload, le traitement, la génération, le passage publication et le service média.
- `lazyedit/` contient des blocs de pipeline modulaires (persistance DB, traduction, burn-in, captions, métadonnées, adaptateurs providers).
- `app/` est une app Expo Router (web/mobile) qui pilote upload, traitement, prévisualisation et publication.
- `config.py` centralise le chargement d’environnement et la résolution de chemins par défaut.
- `start_lazyedit.sh` et `lazyedit_config.sh` fournissent des modes d’exécution locaux/déployés reproductibles via tmux.

| Layer | Main paths | Responsibility |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | Endpoints, routage, résolution env |
| Processing core | `lazyedit/`, `agi/` | Pipeline sous-titres/captions/métadonnées + providers |
| UI | `app/` | Expérience opérateur (web/mobile via Expo) |
| Runtime scripts | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Démarrage local/service et opérations |

Flow de haut niveau :

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

Les captures ci-dessous montrent le chemin opérateur principal, de l’ingestion jusqu’à la génération de métadonnées.

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

- ✨ Workflow de génération basé sur prompt (Stage A/B/C) avec intégrations Sora et Veo.
- 🧵 Pipeline complet : transcription -> retouche/traduction de sous-titres -> burn-in -> keyframes -> captions -> métadonnées.
- 🌏 Composition multilingue de sous-titres avec prise en charge furigana/IPA/romaji.
- 🔌 Backend API-first avec endpoints d’upload, de traitement, de service média et de file de publication.
- 🚚 Intégration AutoPublish optionnelle pour le relais vers plateformes.
- 🖥️ Workflow backend + Expo unifié via scripts de lancement tmux.

## 🌍 Documentation & i18n

- Source canonique : `README.md`
- Variantes linguistiques : `i18n/README.*.md`
- Barre de langues : conserver une seule ligne de navigation linguistique en haut de chaque README (sans doublons)
- Langues actuellement présentes dans ce repo : Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Simplified Chinese, Traditional Chinese

En cas de divergence entre les traductions et la documentation anglaise, ce README anglais est la source de vérité, puis mettez chaque version langue à jour un par un.

| i18n policy | Rule |
| --- | --- |
| Canonical source | Garder `README.md` comme source de vérité |
| Language bar | Exactement une ligne d’options linguistiques en haut |

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

Submodule/external dependency note:
- Git submodules in this repository include `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, and `furigana`.
- Le guide opérationnel traite `furigana` et `echomind` comme dépendances externes en lecture seule dans ce dépôt. Si incertain, privilégiez l’amont et évitez les modifications in-place.

## ✅ Prerequisites

| Dependency | Notes |
| --- | --- |
| Environnement Linux | Les scripts `systemd`/`tmux` ciblent Linux |
| Python 3.10+ | Utiliser l’environnement Conda `lazyedit` |
| Node.js 20+ + npm | Requis pour l’app Expo dans `app/` |
| FFmpeg | Doit être disponible dans le `PATH` |
| PostgreSQL | Authentification peer locale ou connexion DSN |
| Git submodules | Nécessaires pour les pipelines clés |

## 🚀 Installation

1. Cloner et initialiser les submodules :

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Activer l’environnement Conda :

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Installation système optionnelle (mode service) :

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Notes d’installation service :
- `install_lazyedit.sh` installe `ffmpeg` et `tmux`, puis crée `lazyedit.service`.
- Il ne génère pas `lazyedit_config.sh`, `start_lazyedit.sh` ni `stop_lazyedit.sh` ; ces fichiers doivent déjà exister et être corrects.

## ⚡ Quick Start

Démarrage backend + frontend local (chemin minimal) :

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Dans un second shell :

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Bootstrap local optionnel de base de données :

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| Profile | Start command | Default backend | Default frontend |
| --- | --- | --- | --- |
| Développement local (manuel) | `python app.py` + commande Expo | `8787` | `8091` (commande d’exemple) |
| Orchestration tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| Service systemd | `sudo systemctl start lazyedit.service` | Config/env | N/A |

## 🧭 Command Cheat Sheet

| Task | Command |
| --- | --- |
| Initialiser les submodules | `git submodule update --init --recursive` |
| Démarrer le backend seulement | `python app.py` |
| Démarrer backend + Expo (tmux) | `./start_lazyedit.sh` |
| Arrêter le run tmux | `./stop_lazyedit.sh` |
| Ouvrir session tmux | `tmux attach -t lazyedit` |
| Statut service | `sudo systemctl status lazyedit.service` |
| Logs service | `sudo journalctl -u lazyedit.service` |
| Smoke test DB | `python db_smoke_test.py` |
| Smoke test Pytest | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### Développement : backend only

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Entrée alternative utilisée dans les scripts de déploiement actuels :

```bash
python app.py -m lazyedit
```

URL backend par défaut : `http://localhost:8787` (depuis `config.py`, surcharge via `PORT` ou `LAZYEDIT_PORT`).

### Développement : backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Ports par défaut de `start_lazyedit.sh` :
- Backend : `18787`
- Expo web : `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Attacher à la session :

```bash
tmux attach -t lazyedit
```

Arrêter la session :

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

Copier `.env.example` vers `.env` puis mettre à jour chemins et secrets :

```bash
cp .env.example .env
```

Note de priorité de configuration :

- `config.py` charge les valeurs de `.env` si présentes et ne définit que les clés non déjà exportées dans le shell.
- Les valeurs runtime peuvent provenir de : variables d’environnement exportées dans le shell -> `.env` -> valeurs par défaut du code.
- Pour les exécutions tmux/service, `lazyedit_config.sh` contrôle les paramètres de démarrage/session (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, ports via l’environnement du script).

### Key variables

| Variable | Purpose | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Port backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Répertoire racine média | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN PostgreSQL | fallback local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout requête AutoPublish (seconds) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Chemin script Whisper/VAD | dépend de l’environnement |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Noms de modèle ASR | `large-v3` / `large-v2` (exemple) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python pour pipeline caption | dépend de l’environnement |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Script/chemin caption principal | dépend de l’environnement |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Script/cwd fallback caption | dépend de l’environnement |
| `GRSAI_API_*` | Réglages d’intégration Veo/GRSAI | dépend de l’environnement |
| `VENICE_*`, `A2E_*` | Réglages d’intégration Venice/A2E | dépend de l’environnement |
| `OPENAI_API_KEY` | Requis pour les fonctionnalités OpenAI | None |

Machine-specific notes:
- `app.py` peut définir le comportement CUDA (`CUDA_VISIBLE_DEVICES` dans le contexte du codebase).
- Certains chemins par défaut sont spécifiques à une machine ; utilisez `.env` pour des configurations portables.
- `lazyedit_config.sh` contrôle les variables de démarrage tmux/session pour les scripts de déploiement.

## 🧾 Configuration Files

| File | Purpose |
| --- | --- |
| `.env.example` | Template des variables d’environnement utilisées par backend/services |
| `.env` | Overrides machine locale ; chargées par `config.py`/`app.py` si présentes |
| `config.py` | Defaults et résolution d’environnement backend |
| `lazyedit_config.sh` | Profil d’exécution tmux/service (deploy path, env conda, args app, nom de session) |
| `start_lazyedit.sh` | Lance backend + Expo dans tmux avec ports sélectionnés |
| `install_lazyedit.sh` | Crée `lazyedit.service` et valide scripts/config existants |

Ordre recommandé pour la portabilité machine :
1. Copier `.env.example` vers `.env`.
2. Définir les valeurs `LAZYEDIT_*` liées chemins/API dans `.env`.
3. Ajuster `lazyedit_config.sh` uniquement pour le comportement de déploiement tmux/service.

## 🔌 API Examples

Les exemples d’URL de base supposent `http://localhost:8787`.

| API group | Representative endpoints |
| --- | --- |
| Upload and media | `/upload`, `/upload-stream`, `/media/*` |
| Video records | `/api/videos`, `/api/videos/{id}` |
| Processing | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publish | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generation | `/api/videos/generate` (+ routes provider dans `app.py`) |

Upload :

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

End-to-end process :

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Liste des vidéos :

```bash
curl http://localhost:8787/api/videos
```

Publish package :

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Pour plus de détails sur endpoints et payloads : `references/API_GUIDE.md`.

Groupes d’endpoints connexes que vous utiliserez probablement :
- Cycle de vie vidéo : `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Actions de traitement : `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Chemins generation/provider : `/api/videos/generate` plus routes Venice/A2E exposées dans `app.py`
- Distribution : `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Si le backend est sur `8887` :

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

Secondes supportées : `4`, `8`, `12`.
Tailles supportées : `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Development Notes

- Utiliser `python` de l’environnement Conda `lazyedit` (ne pas supposer le `python3` système).
- Garder les médias volumineux hors Git ; stocker les médias runtime dans `DATA/` ou un stockage externe.
- Initialiser/mettre à jour les submodules quand des composants du pipeline échouent à se résoudre.
- Garder les modifications ciblées ; éviter les refactors de formatting non liés.
- Pour le frontend, l’URL API dépend de `EXPO_PUBLIC_API_URL`.
- CORS est ouvert sur le backend pour le développement app.

Submodule and external dependency policy :
- Traiter les dépendances externes comme étant maintenues en amont. Dans ce workflow, évitez de modifier l’intérieur d’un submodule sauf si vous travaillez explicitement sur ces projets.
- Les consignes opérationnelles considèrent `furigana` (et parfois `echomind` dans certains setups locaux) comme des dépendances externes ; en cas de doute, préservez l’amont et évitez les modifications in-place.

Références utiles :
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Sécurité / configuration :
- Conserver clés API et secrets dans des variables d’environnement ; ne pas committer de credentials.
- Préférer `.env` pour les overrides machine locale et garder `.env.example` comme template public.
- Si le comportement CUDA/GPU diffère selon l’hôte, surchargez via l’environnement au lieu de coder en dur des valeurs machine.

## ✅ Testing

Le périmètre de test formel est minimal et orienté DB.

| Validation layer | Command or method |
| --- | --- |
| Smoke DB | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Flux fonctionnel | Web UI + API via un sample court dans `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Pour la validation fonctionnelle, utilisez le flux web UI et API avec un sample court dans `DATA/`.

Hypothèses et limites de portabilité :
- Certains chemins par défaut dans le code sont des fallbacks machine-specific ; c’est attendu dans l’état actuel du dépôt.
- Si un chemin par défaut n’existe pas sur votre machine, définissez la variable `LAZYEDIT_*` correspondante dans `.env`.
- Si vous hésitez sur une valeur par défaut machine, gardez les réglages existants et ajoutez des overrides explicites plutôt que de supprimer les valeurs par défaut.

## 🧱 Assumptions & Known Limits

- Les dépendances backend ne sont pas verouillées par un lockfile racine ; la reproductibilité de l’environnement dépend encore d’une discipline locale.
- `app.py` est volontairement monolithique dans l’état actuel et contient une surface de routes importante.
- La plupart de la validation de pipeline est intégration/manuelle (UI + API + média d’exemple), avec une couverture automatique limitée.
- Les répertoires runtime (`DATA/`, `temp/`, `translation_logs/`) sont des sorties opérationnelles et peuvent devenir volumineux.
- Les submodules sont requis pour la fonctionnalité complète ; un checkout partiel entraîne souvent des erreurs de scripts manquants.

## 🚢 Deployment & Sync Notes

Chemins et flux de sync connus (d’après notes opérations du dépôt) :

- Workspace de développement : `/home/lachlan/ProjectsLFS/LazyEdit`
- Backend + app LazyEdit déployé : `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor déployé : `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Hôte système de publication : `/home/lachlan/Projects/auto-publish` sur `lazyingart`

| Environment | Path | Notes |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Source principale + submodules |
| LazyEdit deployed | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` dans doc ops |
| AutoPubMonitor deployed | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Sessions monitor/sync/process |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull après mise à jour du submodule |

Après avoir poussé des changements `AutoPublish/` depuis ce dépôt, pull sur l’hôte de publication :

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| Problem | Check / Fix |
| --- | --- |
| Modules/scripts du pipeline manquants | Exécuter `git submodule update --init --recursive` |
| FFmpeg not found | Installer FFmpeg et vérifier que `ffmpeg -version` fonctionne |
| Port conflicts | Backend par défaut `8787`; `start_lazyedit.sh` par défaut `18787`; définissez explicitement `LAZYEDIT_PORT` ou `PORT` |
| Expo cannot reach backend | Vérifier que `EXPO_PUBLIC_API_URL` pointe vers l’hôte/port backend actif |
| Database connection issues | Vérifier PostgreSQL + vars env ; smoke check optionnel : `python db_smoke_test.py` |
| GPU/CUDA issues | Vérifier la compatibilité driver/CUDA avec la stack Torch installée |
| Service script fails at install | Vérifier que `lazyedit_config.sh`, `start_lazyedit.sh`, et `stop_lazyedit.sh` existent avant de lancer l’installateur |

## 🗺️ Roadmap

- Édition in-app des sous-titres/segments avec prévisualisation A/B et contrôles ligne par ligne.
- Couverture de tests de bout en bout plus solide pour les flux API principaux.
- Convergence de la documentation entre variantes i18n README et modes de déploiement.
- Durcissement du flux pour retries de providers de génération et visibilité des statuts.

## 🤝 Contributing

Les contributions sont les bienvenues.

1. Forker et créer une branche de feature.
2. Garder les commits ciblés et cohérents.
3. Valider localement (`python app.py`, flux API clés, et intégration app si pertinent).
4. Ouvrir une PR avec objectif, repro steps, et notes before/after (screenshots pour changements UI).

Guidelines pratiques :
- Suivre le style Python (PEP 8, 4 espaces, snake_case).
- Éviter de commiter credentials ou gros binaires.
- Mettre à jour docs/scripts de config quand le comportement change.
- Style de commit préféré : court, impératif, ciblé (par ex. `fix ffmpeg 7 compatibility`).



## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit s’appuie sur des bibliothèques et services open source, dont notamment :
- FFmpeg pour le traitement média
- Tornado pour les APIs backend
- MoviePy pour les workflows d’édition
- Modèles OpenAI pour les tâches de pipeline assistées par IA
- CJKWrap et outils texte multilingues dans les workflows de sous-titres
