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

LazyEdit est un workflow vidéo de bout en bout assisté par IA, pour la création, le traitement et la publication optionnelle. Il combine la génération par prompts (Stage A/B/C), des API de traitement média, le rendu de sous-titres, la légende sur images clés, la génération de métadonnées et le passage vers AutoPublish.

## ✨ Vue d'ensemble

LazyEdit s'articule autour d'un backend Tornado (`app.py`) et d'un frontend Expo (`app/`).

| Étape | Ce qui se passe |
| --- | --- |
| 1 | Importer ou générer une vidéo |
| 2 | Transcrire et, si nécessaire, traduire les sous-titres |
| 3 | Incruster des sous-titres multilingues avec des contrôles de mise en page |
| 4 | Générer images clés, légendes et métadonnées |
| 5 | Packager et publier de façon optionnelle via AutoPublish |

### Focus du pipeline

- Import, génération, remix et gestion de bibliothèque depuis une seule interface opérateur.
- Flux de traitement orienté API pour transcription, amélioration/traduction des sous-titres, incrustation et métadonnées.
- Intégrations optionnelles de fournisseurs de génération (helpers Veo / Venice / A2E / Sora dans `agi/`).
- Transmission de publication optionnelle via `AutoPublish`.

## 🎯 En un coup d'œil

| Domaine | Inclus dans LazyEdit |
| --- | --- |
| Application principale | Backend API Tornado + frontend Expo web/mobile |
| Pipeline média | ASR, traduction/amélioration des sous-titres, incrustation, images clés, légendes, métadonnées |
| Génération | Stage A/B/C et routes helpers fournisseurs (`agi/`) |
| Distribution | Passage optionnel vers AutoPublish |
| Modèle d'exécution | Scripts local-first, workflows tmux, service systemd optionnel |

## 🎬 Démos

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Accueil · Import</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Accueil · Générer</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Accueil · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Bibliothèque</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Vue d'ensemble vidéo</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Aperçu traduction</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Slots d'incrustation</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Mise en page incrustation</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Images clés + légendes</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Générateur de métadonnées</sub>
    </td>
  </tr>
</table>

## 🧩 Fonctionnalités

- Workflow de génération basé sur prompts (Stage A/B/C) avec chemins d'intégration Sora et Veo.
- Pipeline de traitement complet : transcription -> amélioration/traduction des sous-titres -> incrustation -> images clés -> légendes -> métadonnées.
- Composition de sous-titres multilingues avec chemins de support liés à furigana/IPA/romaji.
- Backend orienté API avec endpoints d'import, traitement, diffusion média et file de publication.
- Intégration AutoPublish optionnelle pour la transmission vers les plateformes sociales.
- Workflow combiné backend + Expo pris en charge via scripts de lancement tmux.

## 🗂️ Structure du projet

```text
LazyEdit/
├── app.py                           # Point d'entrée backend Tornado et orchestration API
├── app/                             # Frontend Expo (web/mobile)
├── lazyedit/                        # Modules principaux du pipeline (traduction, métadonnées, burner, DB, templates)
├── agi/                             # Abstraction fournisseurs de génération (routes Sora/Veo/A2E/Venice)
├── DATA/                            # Entrées/sorties média d'exécution (symlink dans cet espace de travail)
├── translation_logs/                # Journaux de traduction
├── temp/                            # Fichiers temporaires d'exécution
├── install_lazyedit.sh              # Installateur systemd (attend les scripts config/start/stop)
├── start_lazyedit.sh                # Lanceur tmux pour backend + Expo
├── stop_lazyedit.sh                 # Helper d'arrêt tmux
├── lazyedit_config.sh               # Configuration shell déploiement/exécution
├── config.py                        # Résolution env/config (ports, chemins, URL autopublish)
├── .env.example                     # Modèle de surcharge d'environnement
├── references/                      # Documentation complémentaire (guide API, quickstart, notes de déploiement)
├── AutoPublish/                     # Sous-module (pipeline de publication optionnel)
├── AutoPubMonitor/                  # Sous-module (automatisation monitoring/sync)
├── whisper_with_lang_detect/        # Sous-module (ASR/VAD)
├── vit-gpt2-image-captioning/       # Sous-module (générateur de légendes principal)
├── clip-gpt-captioning/             # Sous-module (générateur de légendes de secours)
└── furigana/                        # Dépendance externe du workflow (sous-module suivi dans ce checkout)
```

## ✅ Prérequis

| Dépendance | Notes |
| --- | --- |
| Environnement Linux | Les scripts `systemd`/`tmux` sont orientés Linux |
| Python 3.10+ | Utiliser l'environnement Conda `lazyedit` |
| Node.js 20+ + npm | Requis pour l'app Expo dans `app/` |
| FFmpeg | Doit être disponible dans le `PATH` |
| PostgreSQL | Auth peer locale ou connexion via DSN |
| Sous-modules Git | Requis pour les pipelines clés |

## 🚀 Installation

1. Cloner et initialiser les sous-modules :

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Activer l'environnement Conda :

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Installation optionnelle au niveau système (mode service) :

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Notes d'installation du service :
- `install_lazyedit.sh` installe `ffmpeg` et `tmux`, puis crée `lazyedit.service`.
- Il ne génère pas `lazyedit_config.sh`, `start_lazyedit.sh` ou `stop_lazyedit.sh` ; ces fichiers doivent déjà exister et être corrects.

## 🛠️ Utilisation

### Développement : backend seul

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

Se connecter à la session :

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

Copier `.env.example` vers `.env` puis mettre à jour chemins/secrets :

```bash
cp .env.example .env
```

### Variables clés

| Variable | Rôle | Défaut / Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Port backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Répertoire racine des médias | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN PostgreSQL | Fallback DB locale `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout de requête AutoPublish (secondes) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Chemin script Whisper/VAD | Dépend de l'environnement |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Noms des modèles ASR | `large-v3` / `large-v2` (exemple) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python pour le pipeline de légendes | Dépend de l'environnement |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Chemin/script de légendage principal | Dépend de l'environnement |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Chemin/script/cwd de légendage de secours | Dépend de l'environnement |
| `GRSAI_API_*` | Paramètres d'intégration Veo/GRSAI | Dépend de l'environnement |
| `VENICE_*`, `A2E_*` | Paramètres d'intégration Venice/A2E | Dépend de l'environnement |
| `OPENAI_API_KEY` | Requise pour les fonctionnalités basées sur OpenAI | None |

Notes spécifiques machine :
- `app.py` peut définir le comportement CUDA (usage de `CUDA_VISIBLE_DEVICES` dans le contexte de code).
- Certains chemins par défaut sont spécifiques au poste ; utiliser les surcharges `.env` pour une configuration portable.
- `lazyedit_config.sh` contrôle les variables de démarrage tmux/session pour les scripts de déploiement.

## 🔌 Exemples d'API

Les exemples d'URL de base supposent `http://localhost:8787`.

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

Publier un package :

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Plus d'endpoints et détails de payload : `references/API_GUIDE.md`.

## 🧪 Exemples

### Exécution locale frontend (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Si le backend est sur `8887` :

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

- Utiliser `python` depuis l'environnement Conda `lazyedit` (ne pas supposer le `python3` système).
- Garder les médias volumineux hors Git ; stocker les médias d'exécution dans `DATA/` ou un stockage externe.
- Initialiser/mettre à jour les sous-modules quand des composants du pipeline ne sont pas résolus.
- Garder les modifications ciblées ; éviter les gros changements de formatage non liés.
- Pour le frontend, l'URL API backend est contrôlée par `EXPO_PUBLIC_API_URL`.
- CORS est ouvert côté backend pour le développement de l'app.

Politique sous-modules et dépendances externes :
- Traiter les dépendances externes comme gérées en amont. Dans ce workflow dépôt, éviter d'éditer l'interne des sous-modules sauf si vous travaillez volontairement sur ces projets.
- Les consignes opérationnelles de ce dépôt traitent `furigana` (et parfois `echomind` en setup local) comme des chemins de dépendances externes ; en cas d'incertitude, préserver l'amont et éviter les modifications sur place.

Références utiles :
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ Tests

La surface de tests formels actuelle est minimale et orientée DB.

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Pour la validation fonctionnelle, utiliser l'UI web et le flux API avec un court clip d'exemple dans `DATA/`.

## 🚢 Notes de déploiement et de synchronisation

Chemins connus actuels et flux de synchronisation (depuis la documentation d'exploitation du dépôt) :

- Espace de développement : `/home/lachlan/ProjectsLFS/LazyEdit`
- Déploiement backend + app LazyEdit : `/home/lachlan/DiskMech/Projects/lazyedit`
- Déploiement AutoPubMonitor : `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Hôte du système de publication : `/home/lachlan/Projects/auto-publish` sur `lazyingart`

Après avoir poussé les mises à jour `AutoPublish/` depuis ce dépôt, faire un pull sur l'hôte de publication :

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Dépannage

| Problème | Vérifier / Corriger |
| --- | --- |
| Modules ou scripts du pipeline manquants | Exécuter `git submodule update --init --recursive` |
| FFmpeg introuvable | Installer FFmpeg et vérifier que `ffmpeg -version` fonctionne |
| Conflits de ports | Le backend utilise `8787` par défaut ; `start_lazyedit.sh` utilise `18787` par défaut ; définir `LAZYEDIT_PORT` ou `PORT` explicitement |
| Expo n'atteint pas le backend | Vérifier que `EXPO_PUBLIC_API_URL` pointe vers l'hôte/port backend actif |
| Problèmes de connexion base de données | Vérifier PostgreSQL + DSN/variables d'env ; smoke check optionnel : `python db_smoke_test.py` |
| Problèmes GPU/CUDA | Confirmer la compatibilité driver/CUDA avec la stack Torch installée |
| Échec du script de service à l'installation | Vérifier que `lazyedit_config.sh`, `start_lazyedit.sh` et `stop_lazyedit.sh` existent avant de lancer l'installateur |

## 🗺️ Feuille de route

- Édition des sous-titres/segments dans l'app avec aperçu A/B et contrôles ligne par ligne.
- Couverture de tests end-to-end plus robuste pour les flux API principaux.
- Convergence de la documentation entre les variantes README i18n et les modes de déploiement.
- Renforcement supplémentaire des workflows de retry fournisseurs de génération et de visibilité de statut.

## 🤝 Contribution

Les contributions sont les bienvenues.

1. Forker puis créer une branche de fonctionnalité.
2. Garder des commits ciblés et cohérents.
3. Valider les changements localement (`python app.py`, flux API principal, et intégration app si pertinent).
4. Ouvrir une PR avec l'objectif, les étapes de reproduction et des notes avant/après (captures d'écran pour les changements UI).

Consignes pratiques :
- Suivre le style Python (PEP 8, 4 espaces, nommage snake_case).
- Éviter de commit des credentials ou de gros binaires.
- Mettre à jour docs/scripts de config lorsque le comportement change.
- Style de commit recommandé : court, impératif, ciblé (par exemple : `fix ffmpeg 7 compatibility`).

## ❤️ Ce que votre soutien rend possible

- <b>Garder les outils ouverts</b> : hébergement, inférence, stockage de données et opérations communautaires.  
- <b>Livrer plus vite</b> : des semaines de travail open source concentré sur EchoMind, LazyEdit et MultilingualWhisper.  
- <b>Prototyper des wearables</b> : optique, capteurs et composants neuromorphiques/edge pour IdeasGlass + LightMind.  
- <b>Accès pour tous</b> : déploiements subventionnés pour étudiants, créateurs et groupes communautaires.

### Faire un don

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

## 📄 Licence

[Apache-2.0](LICENSE)

## 🙏 Remerciements

LazyEdit s'appuie sur des bibliothèques et services open source, notamment :
- FFmpeg pour le traitement média
- Tornado pour les API backend
- MoviePy pour les workflows d'édition
- Les modèles OpenAI pour les tâches du pipeline assistées par IA
- CJKWrap et des outils de texte multilingue dans les workflows de sous-titres
