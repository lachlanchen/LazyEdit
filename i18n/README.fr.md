[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="Licence : Apache-2.0" /></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Backend-Tornado-222222" alt="Backend : Tornado" />
  <img src="https://img.shields.io/badge/Frontend-Expo-000020?logo=expo&logoColor=white" alt="Frontend : Expo" />
  <img src="https://img.shields.io/badge/Platform-Linux-informational?logo=linux&logoColor=white" alt="Plateforme : Linux" />
  <img src="https://img.shields.io/badge/FFmpeg-required-0A0A0A?logo=ffmpeg&logoColor=white" alt="FFmpeg requis" />
  <img src="https://img.shields.io/badge/PostgreSQL-supported-336791?logo=postgresql&logoColor=white" alt="PostgreSQL pris en charge" />
  <img src="https://img.shields.io/badge/Stage_A%2FB%2FC-enabled-0f766e" alt="Étape A/B/C activée" />
  <img src="https://img.shields.io/badge/AutoPublish-optional-orange" alt="AutoPublish optionnel" />
  <img src="https://img.shields.io/badge/i18n-11%20languages-1f883d" alt="i18n : 11 langues" />
</p>

<p align="center">
  <b>Workflow vidéo assisté par IA</b> pour la génération, le traitement des sous-titres, les métadonnées et la publication optionnelle.
  <br />
  <sub>Importer ou générer -> transcrire -> traduire/améliorer -> incruster les sous-titres -> captions/images clés -> métadonnées -> publier</sub>
</p>

# LazyEdit

LazyEdit est un workflow vidéo de bout en bout assisté par IA pour la création, le traitement et la publication optionnelle. Il combine la génération basée sur des prompts (Stage A/B/C), des API de traitement média, le rendu des sous-titres, le captioning par images clés, la génération de métadonnées et le handoff vers AutoPublish.

| Fait rapide | Valeur |
| --- | --- |
| 📘 README canonique | `README.md` (ce fichier) |
| 🌐 Variantes linguistiques | `i18n/README.*.md` (une seule barre de langue est volontairement conservée en haut) |
| 🧠 Point d’entrée backend | `app.py` (Tornado) |
| 🖥️ Application frontend | `app/` (Expo web/mobile) |

## 🧭 Sommaire

- [Vue d’ensemble](#-vue-densemble)
- [En un coup d’œil](#-en-un-coup-dœil)
- [Aperçu de l’architecture](#️-aperçu-de-larchitecture)
- [Démos](#-démos)
- [Fonctionnalités](#-fonctionnalités)
- [Documentation & i18n](#-documentation--i18n)
- [Structure du projet](#️-structure-du-projet)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Démarrage rapide](#-démarrage-rapide)
- [Aide-mémoire des commandes](#-aide-mémoire-des-commandes)
- [Utilisation](#️-utilisation)
- [Configuration](#️-configuration)
- [Fichiers de configuration](#-fichiers-de-configuration)
- [Exemples d’API](#-exemples-dapi)
- [Exemples](#-exemples)
- [Notes de développement](#-notes-de-développement)
- [Tests](#-tests)
- [Hypothèses et limites connues](#-hypothèses-et-limites-connues)
- [Notes de déploiement et de synchronisation](#-notes-de-déploiement-et-de-synchronisation)
- [Dépannage](#-dépannage)
- [Feuille de route](#️-feuille-de-route)
- [Contribution](#-contribution)
- [Support](#️-support)
- [Licence](#-licence)
- [Remerciements](#-remerciements)

## ✨ Vue d’ensemble

LazyEdit s’articule autour d’un backend Tornado (`app.py`) et d’un frontend Expo (`app/`).

> Remarque : si les détails dépôt/runtime varient selon la machine, conservez les valeurs par défaut existantes et surchargez-les via des variables d’environnement au lieu de supprimer les fallbacks spécifiques à un poste.

| Pourquoi les équipes l’utilisent | Résultat concret |
| --- | --- |
| Flux opérateur unifié | Importer/générer/remixer/publier depuis un seul workflow |
| Conception API-first | Facile à scripter et à intégrer avec d’autres outils |
| Exécution local-first | Compatible avec des schémas de déploiement tmux + service |

| Étape | Ce qui se passe |
| --- | --- |
| 1 | Importer ou générer une vidéo |
| 2 | Transcrire et éventuellement traduire les sous-titres |
| 3 | Incruster des sous-titres multilingues avec contrôle de mise en page |
| 4 | Générer des images clés, des captions et des métadonnées |
| 5 | Préparer le package puis publier via AutoPublish (optionnel) |

### Axe du pipeline

- Import, génération, remix et gestion de bibliothèque depuis une interface opérateur unique.
- Flux de traitement API-first pour la transcription, l’amélioration/traduction des sous-titres, le burn-in et les métadonnées.
- Intégrations optionnelles avec des fournisseurs de génération (helpers Veo / Venice / A2E / Sora dans `agi/`).
- Handoff de publication optionnel via `AutoPublish`.

## 🎯 En un coup d’œil

| Domaine | Inclus dans LazyEdit | Statut |
| --- | --- | --- |
| Application cœur | Backend API Tornado + frontend Expo web/mobile | ✅ |
| Pipeline média | ASR, traduction/amélioration des sous-titres, burn-in, images clés, captions, métadonnées | ✅ |
| Génération | Stage A/B/C et routes helper fournisseurs (`agi/`) | ✅ |
| Distribution | Handoff AutoPublish optionnel | 🟡 Optionnel |
| Modèle d’exécution | Scripts local-first, workflows tmux, service systemd optionnel | ✅ |

## 🏗️ Aperçu de l’architecture

Le dépôt est organisé comme un pipeline média API-first avec une couche UI :

- `app.py` est le point d’entrée Tornado et l’orchestrateur des routes pour l’import, le traitement, la génération, le handoff de publication et le service des médias.
- `lazyedit/` contient les briques modulaires du pipeline (persistance DB, traduction, incrustation des sous-titres, captions, métadonnées, adaptateurs fournisseurs).
- `app/` est une application Expo Router (web/mobile) qui pilote les flux d’import, de traitement, de prévisualisation et de publication.
- `config.py` centralise le chargement de l’environnement et les chemins runtime par défaut/de secours.
- `start_lazyedit.sh` et `lazyedit_config.sh` fournissent des modes d’exécution local/déployé reproductibles basés sur tmux.

| Couche | Chemins principaux | Responsabilité |
| --- | --- | --- |
| API & orchestration | `app.py`, `config.py` | Endpoints, routage, résolution d’environnement |
| Cœur de traitement | `lazyedit/`, `agi/` | Pipeline sous-titres/captions/métadonnées + fournisseurs |
| UI | `app/` | Expérience opérateur (web/mobile via Expo) |
| Scripts runtime | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Démarrage local/service et opérations |

Flux global :

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Démos

Les captures ci-dessous montrent le parcours opérateur principal, de l’ingestion à la génération de métadonnées.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Import depuis l’accueil" width="240" />
      <br /><sub>Accueil · Import</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Génération depuis l’accueil" width="240" />
      <br /><sub>Accueil · Générer</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Remix depuis l’accueil" width="240" />
      <br /><sub>Accueil · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Liste de la bibliothèque" width="240" />
      <br /><sub>Bibliothèque</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Vue d’ensemble vidéo" width="240" />
      <br /><sub>Vue d’ensemble vidéo</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Aperçu de traduction" width="240" />
      <br /><sub>Aperçu de traduction</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Emplacements de burn" width="240" />
      <br /><sub>Emplacements de burn</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Mise en page du burn" width="240" />
      <br /><sub>Mise en page du burn</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Images clés et captions" width="240" />
      <br /><sub>Images clés + captions</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Générateur de métadonnées" width="240" />
      <br /><sub>Générateur de métadonnées</sub>
    </td>
  </tr>
</table>

## 🧩 Fonctionnalités

- ✨ Workflow de génération basé sur des prompts (Stage A/B/C) avec chemins d’intégration Sora et Veo.
- 🧵 Pipeline complet : transcription -> amélioration/traduction des sous-titres -> burn-in -> images clés -> captions -> métadonnées.
- 🌏 Composition de sous-titres multilingues avec prise en charge liée à furigana/IPA/romaji.
- 🔌 Backend API-first avec endpoints d’import, de traitement, de service média et de file de publication.
- 🚚 Intégration AutoPublish optionnelle pour le handoff vers les plateformes sociales.
- 🖥️ Workflow backend + Expo combiné, pris en charge via des scripts de lancement tmux.

## 🌍 Documentation & i18n

LazyEdit maintient un README anglais canonique (`README.md`) et des variantes linguistiques dans `i18n/`.

- Source canonique : `README.md`
- Variantes linguistiques : `i18n/README.*.md`
- Navigation des langues : conserver une seule ligne d’options de langue en haut de chaque README (pas de barres de langue dupliquées)
- Langues actuellement présentes dans ce dépôt : arabe, allemand, anglais, espagnol, français, japonais, coréen, russe, vietnamien, chinois simplifié, chinois traditionnel

S’il existe un décalage entre les traductions et la documentation anglaise, considérez ce README anglais comme source de vérité, puis mettez à jour chaque fichier de langue un par un.

| Politique i18n | Règle |
| --- | --- |
| Source canonique | Garder `README.md` comme source de vérité |
| Barre de langue | Une seule ligne d’options de langue en haut |
| Ordre de mise à jour | Anglais d’abord, puis chaque `i18n/README.*.md` un par un |

## 🗂️ Structure du projet

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
- Les consignes opérationnelles traitent `furigana` et `echomind` comme externes/en lecture seule dans ce workflow de dépôt. En cas de doute, préservez l’amont et évitez les modifications en place.

## ✅ Prérequis

| Dépendance | Notes |
| --- | --- |
| Environnement Linux | Les scripts `systemd`/`tmux` sont orientés Linux |
| Python 3.10+ | Utiliser l’environnement Conda `lazyedit` |
| Node.js 20+ + npm | Requis pour l’application Expo dans `app/` |
| FFmpeg | Doit être disponible dans le `PATH` |
| PostgreSQL | Auth peer locale ou connexion DSN |
| Sous-modules Git | Requis pour les pipelines clés |

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

Notes sur l’installation du service :
- `install_lazyedit.sh` installe `ffmpeg` et `tmux`, puis crée `lazyedit.service`.
- Il ne génère pas `lazyedit_config.sh`, `start_lazyedit.sh` ni `stop_lazyedit.sh` ; ces fichiers doivent déjà exister et être corrects.

## ⚡ Démarrage rapide

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

### Profils d’exécution

| Profil | Commande de démarrage | Backend par défaut | Frontend par défaut |
| --- | --- | --- | --- |
| Dev local (manuel) | `python app.py` + commande Expo | `8787` | `8091` (commande d’exemple) |
| Orchestré via tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| Service systemd | `sudo systemctl start lazyedit.service` | Piloté par config/env | N/A |

## 🧭 Aide-mémoire des commandes

| Tâche | Commande |
| --- | --- |
| Initialiser les sous-modules | `git submodule update --init --recursive` |
| Démarrer seulement le backend | `python app.py` |
| Démarrer backend + Expo (tmux) | `./start_lazyedit.sh` |
| Arrêter l’exécution tmux | `./stop_lazyedit.sh` |
| Ouvrir la session tmux | `tmux attach -t lazyedit` |
| Statut du service | `sudo systemctl status lazyedit.service` |
| Logs du service | `sudo journalctl -u lazyedit.service` |
| Smoke test DB | `python db_smoke_test.py` |
| Smoke test Pytest | `pytest tests/test_db_smoke.py` |

## 🛠️ Utilisation

### Développement : backend uniquement

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Point d’entrée alternatif utilisé dans les scripts de déploiement actuels :

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

Copier `.env.example` vers `.env` puis mettre à jour les chemins/secrets :

```bash
cp .env.example .env
```

Note sur la priorité de configuration :

- `config.py` charge les valeurs de `.env` si présent et ne définit que les clés qui ne sont pas déjà exportées dans le shell.
- Les valeurs runtime peuvent donc provenir de : variables d’environnement exportées dans le shell -> `.env` -> valeurs par défaut du code.
- Pour les exécutions tmux/service, `lazyedit_config.sh` contrôle les paramètres de démarrage/session (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, ports via les variables d’environnement du script de démarrage).

### Variables clés

| Variable | Rôle | Valeur par défaut / fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Port backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Répertoire racine média | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN PostgreSQL | Fallback DB locale `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Délai de requête AutoPublish (secondes) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Chemin du script Whisper/VAD | Dépend de l’environnement |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Noms des modèles ASR | `large-v3` / `large-v2` (exemple) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python pour le pipeline captions | Dépend de l’environnement |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Chemin/script de caption principal | Dépend de l’environnement |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Chemin/script/cwd de caption de fallback | Dépend de l’environnement |
| `GRSAI_API_*` | Paramètres d’intégration Veo/GRSAI | Dépend de l’environnement |
| `VENICE_*`, `A2E_*` | Paramètres d’intégration Venice/A2E | Dépend de l’environnement |
| `OPENAI_API_KEY` | Requis pour les fonctionnalités basées sur OpenAI | Aucun |

Notes spécifiques machine :
- `app.py` peut définir le comportement CUDA (usage de `CUDA_VISIBLE_DEVICES` dans le contexte du codebase).
- Certains chemins dans les valeurs par défaut sont spécifiques à un poste ; utilisez des surcharges `.env` pour les setups portables.
- `lazyedit_config.sh` contrôle les variables de démarrage tmux/session pour les scripts de déploiement.

## 🧾 Fichiers de configuration

| Fichier | Rôle |
| --- | --- |
| `.env.example` | Template des variables d’environnement utilisées par le backend/services |
| `.env` | Surcharges locales machine ; chargé par `config.py`/`app.py` s’il est présent |
| `config.py` | Valeurs backend par défaut et résolution de l’environnement |
| `lazyedit_config.sh` | Profil runtime tmux/service (chemin de déploiement, env conda, args app, nom de session) |
| `start_lazyedit.sh` | Lance backend + Expo dans tmux avec les ports choisis |
| `install_lazyedit.sh` | Crée `lazyedit.service` et valide les scripts/config existants |

Ordre de mise à jour recommandé pour la portabilité machine :
1. Copier `.env.example` vers `.env`.
2. Définir les valeurs `LAZYEDIT_*` liées aux chemins/API dans `.env`.
3. Ajuster `lazyedit_config.sh` uniquement pour le comportement de déploiement tmux/service.

## 🔌 Exemples d’API

Les exemples d’URL de base supposent `http://localhost:8787`.

| Groupe API | Endpoints représentatifs |
| --- | --- |
| Import et médias | `/upload`, `/upload-stream`, `/media/*` |
| Enregistrements vidéo | `/api/videos`, `/api/videos/{id}` |
| Traitement | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publication | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Génération | `/api/videos/generate` (+ routes fournisseurs dans `app.py`) |

Import :

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Traitement de bout en bout :

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Lister les vidéos :

```bash
curl http://localhost:8787/api/videos
```

Package de publication :

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Plus d’endpoints et détails de payload : `references/API_GUIDE.md`.

Groupes d’endpoints connexes que vous utiliserez probablement :
- Cycle de vie vidéo : `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Actions de traitement : `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Chemins génération/fournisseurs : `/api/videos/generate` plus routes Venice/A2E exposées dans `app.py`
- Distribution : `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Exemples

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

### Helper optionnel de génération Sora

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Secondes prises en charge : `4`, `8`, `12`.
Tailles prises en charge : `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Notes de développement

- Utilisez `python` depuis l’environnement Conda `lazyedit` (ne présumez pas la présence de `python3` système).
- Gardez les médias volumineux hors Git ; stockez les médias runtime dans `DATA/` ou un stockage externe.
- Initialisez/mettez à jour les sous-modules dès qu’un composant pipeline ne se résout pas.
- Gardez des modifications ciblées ; évitez les gros changements de formatage non liés.
- Côté frontend, l’URL API backend est pilotée par `EXPO_PUBLIC_API_URL`.
- CORS est ouvert sur le backend pour le développement de l’app.

Politique sous-modules et dépendances externes :
- Traitez les dépendances externes comme détenues par l’amont. Dans ce workflow de dépôt, évitez d’éditer l’interne des sous-modules sauf si vous travaillez intentionnellement sur ces projets.
- Les consignes opérationnelles de ce dépôt traitent `furigana` (et parfois `echomind` en setup local) comme chemins de dépendances externes ; en cas de doute, préservez l’amont et évitez les modifications en place.

Références utiles :
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Hygiène sécurité/config :
- Conservez les clés API et secrets dans des variables d’environnement ; ne committez pas de credentials.
- Préférez `.env` pour les surcharges locales machine et gardez `.env.example` comme template public.
- Si le comportement CUDA/GPU diffère selon l’hôte, surchargez via l’environnement plutôt que de coder en dur des valeurs spécifiques machine.

## ✅ Tests

La surface de tests formels actuelle est minimale et orientée DB.

| Couche de validation | Commande ou méthode |
| --- | --- |
| Smoke test DB | `python db_smoke_test.py` |
| Vérification DB Pytest | `pytest tests/test_db_smoke.py` |
| Flux fonctionnel | Exécution Web UI + API avec un court échantillon dans `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Pour la validation fonctionnelle, utilisez le flux Web UI et API avec un court clip d’exemple dans `DATA/`.

Hypothèses et notes de portabilité :
- Certains chemins par défaut dans le code sont des fallbacks spécifiques poste ; c’est attendu dans l’état actuel du dépôt.
- Si un chemin par défaut n’existe pas sur votre machine, définissez la variable `LAZYEDIT_*` correspondante dans `.env`.
- En cas d’incertitude sur une valeur spécifique machine, conservez les réglages existants et ajoutez des surcharges explicites plutôt que de supprimer les valeurs par défaut.

## 🧱 Hypothèses et limites connues

- L’ensemble de dépendances backend n’est pas verrouillé par un lockfile racine ; la reproductibilité de l’environnement dépend actuellement de la discipline de setup locale.
- `app.py` est volontairement monolithique dans l’état actuel du dépôt et contient une surface de routes importante.
- La majorité de la validation pipeline est de type intégration/manuelle (UI + API + média échantillon), avec peu de tests automatisés formels.
- Les répertoires runtime (`DATA/`, `temp/`, `translation_logs/`) sont des sorties opérationnelles et peuvent grossir fortement.
- Les sous-modules sont requis pour les fonctionnalités complètes ; un checkout partiel mène souvent à des erreurs de scripts manquants.

## 🚢 Notes de déploiement et de synchronisation

Chemins connus actuels et flux de synchronisation (selon la documentation d’exploitation du dépôt) :

- Workspace de développement : `/home/lachlan/ProjectsLFS/LazyEdit`
- Backend + app LazyEdit déployés : `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor déployé : `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Hôte du système de publication : `/home/lachlan/Projects/auto-publish` sur `lazyingart`

| Environnement | Chemin | Notes |
| --- | --- | --- |
| Workspace dev | `/home/lachlan/ProjectsLFS/LazyEdit` | Source principal + sous-modules |
| LazyEdit déployé | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` dans la doc ops |
| AutoPubMonitor déployé | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Sessions monitor/sync/process |
| Hôte de publication | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull après mise à jour de sous-module |

Après un push des mises à jour `AutoPublish/` depuis ce dépôt, faire un pull sur l’hôte de publication :

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Dépannage

| Problème | Vérification / correction |
| --- | --- |
| Modules ou scripts pipeline manquants | Exécuter `git submodule update --init --recursive` |
| FFmpeg introuvable | Installer FFmpeg et vérifier que `ffmpeg -version` fonctionne |
| Conflits de ports | Backend par défaut `8787` ; `start_lazyedit.sh` par défaut `18787` ; définir explicitement `LAZYEDIT_PORT` ou `PORT` |
| Expo ne joint pas le backend | Vérifier que `EXPO_PUBLIC_API_URL` pointe vers l’hôte/port backend actif |
| Problèmes de connexion DB | Vérifier PostgreSQL + DSN/variables env ; smoke check optionnel : `python db_smoke_test.py` |
| Problèmes GPU/CUDA | Vérifier la compatibilité driver/CUDA avec la stack Torch installée |
| Échec du script de service à l’installation | Vérifier que `lazyedit_config.sh`, `start_lazyedit.sh` et `stop_lazyedit.sh` existent avant de lancer l’installateur |

## 🗺️ Feuille de route

- Édition in-app des sous-titres/segments avec aperçu A/B et contrôles par ligne.
- Couverture de tests end-to-end plus robuste sur les flux API principaux.
- Convergence de la documentation entre les variantes i18n du README et les modes de déploiement.
- Durcissement supplémentaire du workflow pour les retries des fournisseurs de génération et la visibilité du statut.

## 🤝 Contribution

Les contributions sont les bienvenues.

1. Forker puis créer une branche de fonctionnalité.
2. Garder des commits ciblés et cohérents.
3. Valider les changements localement (`python app.py`, flux API clés, et intégration app si pertinent).
4. Ouvrir une PR avec objectif, étapes de reproduction et notes avant/après (captures d’écran pour les changements UI).

Directives pratiques :
- Suivre le style Python (PEP 8, 4 espaces, nommage snake_case).
- Éviter de commit des credentials ou de gros binaires.
- Mettre à jour la documentation/les scripts de config quand le comportement change.
- Style de commit préféré : court, impératif, ciblé (par exemple : `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 Licence

[Apache-2.0](LICENSE)

## 🙏 Remerciements

LazyEdit s’appuie sur des bibliothèques et services open source, notamment :
- FFmpeg pour le traitement média
- Tornado pour les API backend
- MoviePy pour les workflows d’édition
- Les modèles OpenAI pour les tâches de pipeline assistées par IA
- CJKWrap et des outils de texte multilingue dans les workflows de sous-titres
