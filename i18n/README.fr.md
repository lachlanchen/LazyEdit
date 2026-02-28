[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>Workflow vidéo assisté par IA</b> pour la génération, le traitement des sous-titres, les métadonnées et la publication optionnelle.
  <br />
  <sub>Importer ou générer -> transcrire -> traduire/retoucher -> incruster les sous-titres -> keyframes/légendes -> métadonnées -> publier</sub>
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

## 📌 Quick Facts

LazyEdit est un workflow vidéo de bout en bout assisté par IA pour la création, le traitement et la publication optionnelle. Il combine la génération basée sur prompts (Stage A/B/C), les API de traitement média, le rendu de sous-titres, le captioning par images-clés et la génération de métadonnées, ainsi que la prise en charge AutoPublish.

| Fait rapide | Valeur |
| --- | --- |
| 📘 README canonique | `README.md` (ce fichier) |
| 🌐 Variantes linguistiques | `i18n/README.*.md` (une seule barre de langue est maintenue en haut) |
| 🧠 Entrée backend | `app.py` (Tornado) |
| 🖥️ App frontend | `app/` (Expo web/mobile) |

## 🧭 Contents

- [Aperçu](#-overview)
- [Quick Facts](#-quick-facts)
- [En un coup d'œil](#-at-a-glance)
- [Architecture Snapshot](#-architecture-snapshot)
- [Démos](#-démos)
- [Fonctionnalités](#-features)
- [Documentation & i18n](#-documentation--i18n)
- [Structure du projet](#-project-structure)
- [Prérequis](#-prerequisites)
- [Installation](#-installation)
- [Démarrage rapide](#-quick-start)
- [Aide-mémoire des commandes](#-command-cheat-sheet)
- [Usage](#-usage)
- [Configuration](#️-configuration)
- [Fichiers de configuration](#-configuration-files)
- [Exemples d'API](#-api-examples)
- [Exemples](#-examples)
- [Notes de développement](#-development-notes)
- [Tests](#-testing)
- [Hypothèses et limites connues](#-assumptions--known-limits)
- [Notes de déploiement et synchronisation](#-deployment--sync-notes)
- [Dépannage](#-troubleshooting)
- [Feuille de route](#-roadmap)
- [Contribution](#-contributing)
- [Support](#-support)
- [License](#license)
- [Remerciements](#acknowledgements)

## ✨ Overview

LazyEdit s’appuie sur un backend Tornado (`app.py`) et un frontend Expo (`app/`).

> Note : si les détails du dépôt/runtime diffèrent selon la machine, conservez les valeurs par défaut existantes et surchagez-les via les variables d’environnement au lieu de supprimer des fallback spécifiques à une machine.

| Pourquoi les équipes l'utilisent | Résultat pratique |
| --- | --- |
| Flux opérateur unifié | Importer/générer/recomposer/publié depuis un seul workflow |
| Conception API-first | Facile à automatiser et intégrer avec d'autres outils |
| Runtime local-first | Compatible avec les déploiements tmux + service |

| Étape | Ce qui se passe |
| --- | --- |
| 1 | Importer ou générer une vidéo |
| 2 | Transcrire et traduire optionnellement les sous-titres |
| 3 | Incruster des sous-titres multilingues avec contrôle de la mise en page |
| 4 | Générer images-clés, légendes et métadonnées |
| 5 | Empaqueter et publier optionnellement via AutoPublish |

### Focus du pipeline

- Import, génération, remix et gestion de bibliothèque depuis une interface opérateur unique.
- Flux de traitement API-first pour transcription, révision/traduction de sous-titres, incrustation, images-clés, légendes et métadonnées.
- Intégrations optionnelles avec fournisseurs de génération (helpers Veo / Venice / A2E / Sora dans `agi/`).
- Délai de publication optionnel via `AutoPublish`.

## 🎯 At a Glance

| Domaine | Inclus dans LazyEdit | Statut |
| --- | --- | --- |
| App cœur | API backend Tornado + frontend Expo web/mobile | ✅ |
| Pipeline média | ASR, traduction/réécriture des sous-titres, incrustation, keyframes, légendes, métadonnées | ✅ |
| Génération | Stage A/B/C et routes helpers fournisseurs (`agi/`) | ✅ |
| Distribution | Passage vers AutoPublish (optionnel) | 🟡 Optionnel |
| Runtime model | Scripts local-first, workflows tmux, service systemd optionnel | ✅ |

## 🏗️ Architecture Snapshot

Le dépôt est organisé en pipeline média API-first avec une couche UI :

- `app.py` est l’orchestrateur d’entrée Tornado et de routes pour l’import, le traitement, la génération, la main-d’œuvre de publication et le service média.
- `lazyedit/` contient des briques modulaires du pipeline (persistances DB, traduction, incrustation, légendes, métadonnées, adaptateurs fournisseurs).
- `app/` est une app Expo Router (web/mobile) qui pilote l’import, le traitement, l’aperçu et les flux de publication.
- `config.py` centralise le chargement d’environnement et les chemins runtime de fallback.
- `start_lazyedit.sh` et `lazyedit_config.sh` offrent des modes d’exécution local/déployé reproductibles basés sur tmux.

| Couche | Chemins principaux | Responsabilité |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | Endpoints, routage, résolution env |
| Core de traitement | `lazyedit/`, `agi/` | Pipeline sous-titres/légendes/métadonnées + fournisseurs |
| UI | `app/` | Expérience opérateur (web/mobile via Expo) |
| Scripts runtime | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Démarrage local/service et opérations |

Flux de haut niveau :

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

Les captures ci-dessous montrent le parcours opérateur principal, de l’ingestion jusqu’à la génération de métadonnées.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Accueil · Upload</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Accueil · Generate</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Accueil · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Library</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Vue vidéo</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Aperçu traduction</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Créneaux burn</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Mise en page burn</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Keyframes + légendes</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Générateur de métadonnées</sub>
    </td>
  </tr>
</table>

## 🧩 Features

- ✨ Workflow de génération basé sur prompts (Stage A/B/C) avec intégrations Sora et Veo.
- 🧵 Pipeline complet : transcription -> révision/traduction de sous-titres -> burn-in -> keyframes -> légendes -> métadonnées.
- 🌏 Composition multilingue de sous-titres avec chemins furigana/IPA/romaji.
- 🔌 Backend API-first avec endpoints d’import, traitement, service média et file de publication.
- 🚚 Intégration AutoPublish optionnelle pour la transmission vers les plateformes.
- 🖥️ Workflow backend + Expo combiné via scripts de lancement tmux.

## 🌍 Documentation & i18n

- Source canonique : `README.md`
- Variantes linguistiques : `i18n/README.*.md`
- Navigation de langue : conserver une seule ligne d’options au haut de chaque README (pas de doublon de barres).
- Langues actuelles dans ce dépôt : Arabic, German, English, Spanish, French, Japanese, Korean, Russian, Vietnamese, Chinese (Simplified), Chinese (Traditional)

Si une divergence apparaît entre les traductions et la doc anglaise, cette README anglais reste la source de vérité et chaque fichier langue doit être mis à jour un par un.

| Politique i18n | Règle |
| --- | --- |
| Source canonique | Conserver `README.md` comme source de vérité |
| Barre de langue | Exactement une ligne de langue en haut |

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

Note sur les sous-modules/dépendances externes :
- Les sous-modules Git de ce dépôt incluent `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` et `furigana`.
- Les consignes opérationnelles traitent `furigana` et `echomind` comme dépendances externes en lecture seule dans ce workflow. En cas de doute, privilégiez l’amont et évitez les modifications in-place.

## ✅ Prerequisites

| Dépendance | Notes |
| --- | --- |
| Environnement Linux | Les scripts `systemd`/`tmux` sont orientés Linux |
| Python 3.10+ | Utiliser l’environnement Conda `lazyedit` |
| Node.js 20+ + npm | Requis pour l’app Expo dans `app/` |
| FFmpeg | Doit être disponible dans le `PATH` |
| PostgreSQL | Authentification locale peer ou connexion DSN |
| Git submodules | Nécessaires pour les pipelines clés |

## 🚀 Installation

1. Cloner et initialiser les sous-modules :

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
- Il ne génère pas `lazyedit_config.sh`, `start_lazyedit.sh`, ou `stop_lazyedit.sh` : ces fichiers doivent déjà exister et être corrects.

## ⚡ Quick Start

Exécution locale backend + frontend (chemin minimal) :

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

Bootstrap optionnel de base de données locale :

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Profils runtime

| Profil | Commande de démarrage | Backend par défaut | Frontend par défaut |
| --- | --- | --- | --- |
| Dév local (manuel) | `python app.py` + commande Expo | `8787` | `8091` (commande d’exemple) |
| Orchestration tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| service systemd | `sudo systemctl start lazyedit.service` | Basé sur config/env | N/A |

## 🧭 Command Cheat Sheet

| Tâche | Commande |
| --- | --- |
| Initialiser les sous-modules | `git submodule update --init --recursive` |
| Démarrer backend seulement | `python app.py` |
| Démarrer backend + Expo (tmux) | `./start_lazyedit.sh` |
| Arrêter session tmux | `./stop_lazyedit.sh` |
| Ouvrir session tmux | `tmux attach -t lazyedit` |
| Statut service | `sudo systemctl status lazyedit.service` |
| Logs service | `sudo journalctl -u lazyedit.service` |
| Smoke test DB | `python db_smoke_test.py` |
| Smoke test Pytest | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### Développement : backend seulement

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

### Développement : backend + app Expo (tmux)

```bash
./start_lazyedit.sh
```

Ports par défaut de `start_lazyedit.sh` :
- Backend : `18787`
- Expo web : `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Attacher la session :

```bash
tmux attach -t lazyedit
```

Arrêter la session :

```bash
./stop_lazyedit.sh
```

### Gestion du service

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Configuration

Copier `.env.example` vers `.env` puis mettre à jour les chemins et secrets :

```bash
cp .env.example .env
```

Note de priorité de configuration :

- `config.py` charge les valeurs de `.env` si présent et ne définit que les clés non exportées dans le shell.
- Les valeurs runtime peuvent provenir de : variables d’environnement exportées dans le shell -> `.env` -> valeurs par défaut du code.
- Pour les exécutions tmux/service, `lazyedit_config.sh` contrôle les paramètres de démarrage/session (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, ports via les variables d’environnement du script).

### Variables clés

| Variable | Usage | Valeur par défaut / fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Port backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Dossier racine média | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN PostgreSQL | fallback DB local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout requête AutoPublish (secondes) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Chemin script Whisper/VAD | dépend de l’environnement |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Noms de modèles ASR | `large-v3` / `large-v2` (exemple) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python pour pipeline caption | dépend de l’environnement |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Script/chemin de caption principal | dépend de l’environnement |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Script/cwd de caption de secours | dépend de l’environnement |
| `GRSAI_API_*` | Paramètres d’intégration Veo/GRSAI | dépend de l’environnement |
| `VENICE_*`, `A2E_*` | Paramètres d’intégration Venice/A2E | dépend de l’environnement |
| `OPENAI_API_KEY` | Nécessaire pour les fonctionnalités OpenAI-backed | Aucun |

Notes machine :
- `app.py` peut configurer le comportement CUDA (`CUDA_VISIBLE_DEVICES` dans le contexte codebase).
- Certains chemins par défaut sont spécifiques à une machine ; utilisez des overrides `.env` pour des setups portables.
- `lazyedit_config.sh` contrôle les variables de démarrage tmux/session pour les scripts de déploiement.

## 🧾 Configuration Files

| Fichier | Usage |
| --- | --- |
| `.env.example` | Template de variables d’environnement utilisé par backend/services |
| `.env` | Overrides locale machine ; chargé par `config.py`/`app.py` si présent |
| `config.py` | Résolution environnementale et defaults backend |
| `lazyedit_config.sh` | Profil d’exécution tmux/service (chemin déploiement, env conda, app args, nom session) |
| `start_lazyedit.sh` | Lance backend + Expo dans tmux avec ports choisis |
| `install_lazyedit.sh` | Crée `lazyedit.service` et valide scripts/config existants |

Ordre recommandé pour la portabilité machine :
1. Copier `.env.example` vers `.env`.
2. Définir les variables `LAZYEDIT_*` liées aux chemins/API dans `.env`.
3. Ajuster `lazyedit_config.sh` uniquement pour le comportement de déploiement tmux/service.

## 🔌 API Examples

Exemples d’URL de base supposent `http://localhost:8787`.

| Groupe API | Endpoints représentatifs |
| --- | --- |
| Upload et médias | `/upload`, `/upload-stream`, `/media/*` |
| Enregistrements vidéo | `/api/videos`, `/api/videos/{id}` |
| Traitement | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publication | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Génération | `/api/videos/generate` (+ routes fournisseurs dans `app.py`) |

Upload :

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Traitement end-to-end :

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

Publication package :

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Plus d’endpoints et détails payload : `references/API_GUIDE.md`.

Groupes d’endpoints proches que vous utiliserez probablement :
- Cycle de vie vidéo : `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Actions de traitement : `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Chemins génération/fournisseurs : `/api/videos/generate` plus routes Venice/A2E exposées dans `app.py`
- Distribution : `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### Exécution frontend locale (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Si le backend tourne sur `8887` :

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Émulateur Android

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### Simulateur iOS (macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### Helper de génération Sora optionnel

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Secondes supportées : `4`, `8`, `12`.
Taille supportées : `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Development Notes

- Utiliser `python` depuis l’environnement Conda `lazyedit` (ne pas supposer `python3` système).
- Garder les médias volumineux hors Git ; stocker les médias runtime dans `DATA/` ou stockage externe.
- Initialiser/met à jour les sous-modules quand les composants de pipeline ne se résolvent pas.
- Garder les modifications ciblées ; éviter les refactorings de formatage non liés.
- Pour le travail frontend, `EXPO_PUBLIC_API_URL` pilote l’URL backend.
- CORS est ouvert sur le backend pour le développement app.

Politique sous-modules et dépendances externes :
- Traiter les dépendances externes comme détenues par l’amont. Dans ce workflow, évitez de modifier les internes de sous-modules sauf si vous travaillez explicitement sur ces projets.
- Les consignes opérationnelles traitent `furigana` (et parfois `echomind` dans certains setups locaux) comme dépendances externes ; en cas de doute, préservez l’amont et évitez les modifications in-place.

Références utiles :
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Hygiène sécurité/config :
- Conserver clés API et secrets dans des variables d’environnement ; ne pas committer de credentials.
- Préférer `.env` pour les overrides machine locale et garder `.env.example` comme template public.
- Si le comportement CUDA/GPU diffère selon l’hôte, surcharger via l’environnement au lieu de coder en dur des valeurs machine.

## ✅ Testing

La couverture de tests formelle actuelle est minimale et orientée DB.

| Couche de validation | Commande ou méthode |
| --- | --- |
| Smoke test DB | `python db_smoke_test.py` |
| Vérification Pytest DB | `pytest tests/test_db_smoke.py` |
| Flux fonctionnel | Web UI + API sur un sample court dans `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Pour la validation fonctionnelle, utilisez le flux web UI et API avec un clip court dans `DATA/`.

Hypothèses et notes de portabilité :
- Certains chemins par défaut dans le code sont des fallbacks spécifiques à des postes ; c’est attendu dans l’état actuel du dépôt.
- Si un chemin par défaut n’existe pas sur votre machine, définissez la variable `LAZYEDIT_*` correspondante dans `.env`.
- En cas d’incertitude sur une valeur machine, conservez les paramètres existants et ajoutez des overrides explicites plutôt que supprimer les défauts.

## 🧱 Assumptions & Known Limits

- Les dépendances backend ne sont pas figées par un lockfile racine ; la reproductibilité de l’environnement dépend encore de la rigueur de setup local.
- `app.py` est volontairement monolithique dans l’état courant du dépôt et contient une surface de routes importante.
- La majorité de la validation du pipeline est intégration/manuelle (UI + API + média échantillon), avec peu de tests automatisés formels.
- Les répertoires runtime (`DATA/`, `temp/`, `translation_logs/`) sont des sorties opérationnelles et peuvent grandir fortement.
- Les sous-modules sont requis pour la fonctionnalité complète ; un checkout partiel provoque souvent des erreurs de scripts manquants.

## 🚢 Deployment & Sync Notes

Chemins connus et flux de sync actuels (d’après la doc d’exploitation du dépôt) :

- Workspace de développement : `/home/lachlan/ProjectsLFS/LazyEdit`
- LazyEdit backend + app déployé : `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor déployé : `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Système de publication : `/home/lachlan/Projects/auto-publish` sur `lazyingart`

| Environnement | Chemin | Notes |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Source principale + sous-modules |
| LazyEdit déployé | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` dans la doc ops |
| AutoPubMonitor déployé | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Sessions monitor/sync/process |
| Publication host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull après mise à jour de sous-module |

Après avoir poussé des changements `AutoPublish/` depuis ce dépôt, pull sur l’hôte de publication :

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| Problème | Vérification / correction |
| --- | --- |
| Modules/scripts pipeline manquants | Exécuter `git submodule update --init --recursive` |
| FFmpeg introuvable | Installer FFmpeg et vérifier que `ffmpeg -version` fonctionne |
| Conflits de port | Backend par défaut `8787` ; `start_lazyedit.sh` par défaut `18787` ; définir explicitement `LAZYEDIT_PORT` ou `PORT` |
| Expo ne rejoint pas le backend | Vérifier que `EXPO_PUBLIC_API_URL` pointe vers le backend actif host/port |
| Problème de connexion DB | Vérifier PostgreSQL + DSN/variables env ; smoke check optionnel : `python db_smoke_test.py` |
| Problèmes GPU/CUDA | Vérifier compatibilité driver/CUDA avec la stack Torch installée |
| Échec script service à l’installation | Vérifier que `lazyedit_config.sh`, `start_lazyedit.sh` et `stop_lazyedit.sh` existent avant de lancer l’installateur |

## 🗺️ Roadmap

- Édition in-app des sous-titres/segments avec preview A/B et contrôles ligne par ligne.
- Couverture de tests de bout en bout plus robuste pour les flux API principaux.
- Convergence de la doc entre variantes i18n README et modes de déploiement.
- Renforcement du workflow pour les retries des fournisseurs de génération et la visibilité d’état.

## 🤝 Contributing

Les contributions sont bienvenues.

1. Fork et créer une branche de fonctionnalité.
2. Garder des commits ciblés et cohérents.
3. Valider localement (`python app.py`, flux API clés, et intégration app si pertinent).
4. Ouvrir une PR avec objectif, étapes de reproduction, notes before/after (captures pour modifications UI).

Directives pratiques :
- Suivre le style Python (PEP 8, 4 espaces, naming snake_case).
- Éviter de commiter credentials ou gros binaires.
- Mettre à jour docs/scripts de configuration quand le comportement change.
- Style de commit préféré : court, impératif, ciblé (par ex. `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

LazyEdit s’appuie sur des bibliothèques et services open source, notamment :
- FFmpeg pour le traitement média
- Tornado pour les API backend
- MoviePy pour les workflows d’édition
- Les modèles OpenAI pour les tâches de pipeline assistées par IA
- CJKWrap et les outils texte multilingues dans les workflows de sous-titres
