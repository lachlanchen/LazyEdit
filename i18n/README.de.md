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

LazyEdit ist ein durchgängiger, KI-gestützter Video-Workflow für Erstellung, Verarbeitung und optionales Publishing. Er kombiniert promptbasierte Generierung (Stage A/B/C), Media-Processing-APIs, Untertitel-Rendering, Keyframe-Captioning, Metadaten-Generierung und AutoPublish-Übergabe.

## ✨ Überblick

LazyEdit basiert auf einem Tornado-Backend (`app.py`) und einem Expo-Frontend (`app/`).

| Schritt | Was passiert |
| --- | --- |
| 1 | Video hochladen oder generieren |
| 2 | Untertitel transkribieren und optional übersetzen |
| 3 | Mehrsprachige Untertitel mit Layout-Steuerung einbrennen |
| 4 | Keyframes, Captions und Metadaten erzeugen |
| 5 | Paket erstellen und optional über AutoPublish veröffentlichen |

### Pipeline-Fokus

- Upload, Generierung, Remix und Library-Verwaltung in einer einzigen Operator-UI.
- API-first-Verarbeitungsfluss für Transkription, Untertitel-Polishing/-Übersetzung, Burn-in und Metadaten.
- Optionale Integrationen von Generierungsanbietern (Veo / Venice / A2E / Sora-Helper in `agi/`).
- Optionale Publishing-Übergabe über `AutoPublish`.

## 🎯 Auf einen Blick

| Bereich | In LazyEdit enthalten |
| --- | --- |
| Kernanwendung | Tornado-API-Backend + Expo-Web/Mobile-Frontend |
| Media-Pipeline | ASR, Untertitel-Übersetzung/-Polishing, Burn-in, Keyframes, Captions, Metadaten |
| Generierung | Stage A/B/C und Provider-Helper-Routen (`agi/`) |
| Distribution | Optionale AutoPublish-Übergabe |
| Laufzeitmodell | Local-first-Skripte, tmux-Workflows, optionaler systemd-Service |

## 🎬 Demos

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Startseite · Upload</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Startseite · Generieren</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Startseite · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Bibliothek</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Video-Übersicht</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Übersetzungsvorschau</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Burn-Slots</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Burn-Layout</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Keyframes + Captions</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Metadaten-Generator</sub>
    </td>
  </tr>
</table>

## 🧩 Funktionen

- Promptbasierter Generierungs-Workflow (Stage A/B/C) mit Sora- und Veo-Integrationspfaden.
- Vollständige Verarbeitungs-Pipeline: Transkription -> Untertitel-Polishing/-Übersetzung -> Burn-in -> Keyframes -> Captions -> Metadaten.
- Mehrsprachige Untertitel-Komposition mit Support-Pfaden rund um Furigana/IPA/Romaji.
- API-first-Backend mit Endpunkten für Upload, Verarbeitung, Media Serving und Publish Queue.
- Optionale AutoPublish-Integration für die Übergabe an Social-Plattformen.
- Kombinierter Backend- + Expo-Workflow über tmux-Startskripte.

## 🗂️ Projektstruktur

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

## ✅ Voraussetzungen

| Abhängigkeit | Hinweise |
| --- | --- |
| Linux-Umgebung | `systemd`/`tmux`-Skripte sind auf Linux ausgerichtet |
| Python 3.10+ | Verwende die Conda-Umgebung `lazyedit` |
| Node.js 20+ + npm | Erforderlich für die Expo-App in `app/` |
| FFmpeg | Muss im `PATH` verfügbar sein |
| PostgreSQL | Lokale Peer-Auth oder DSN-basierte Verbindung |
| Git-Submodule | Für zentrale Pipelines erforderlich |

## 🚀 Installation

1. Repository klonen und Submodule initialisieren:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Conda-Umgebung aktivieren:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Optionale Installation auf Systemebene (Service-Modus):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Hinweise zur Service-Installation:
- `install_lazyedit.sh` installiert `ffmpeg` und `tmux` und erstellt anschließend `lazyedit.service`.
- Es erzeugt nicht `lazyedit_config.sh`, `start_lazyedit.sh` oder `stop_lazyedit.sh`; diese müssen bereits vorhanden und korrekt sein.

## 🛠️ Nutzung

### Entwicklung: nur Backend

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Alternativer Einstieg, der in aktuellen Deployment-Skripten verwendet wird:

```bash
python app.py -m lazyedit
```

Standard-URL des Backends: `http://localhost:8787` (aus `config.py`, überschreibbar mit `PORT` oder `LAZYEDIT_PORT`).

### Entwicklung: Backend + Expo-App (tmux)

```bash
./start_lazyedit.sh
```

Standard-Ports in `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Session verbinden:

```bash
tmux attach -t lazyedit
```

Session stoppen:

```bash
./stop_lazyedit.sh
```

### Service-Verwaltung

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Konfiguration

Kopiere `.env.example` nach `.env` und aktualisiere Pfade/Secrets:

```bash
cp .env.example .env
```

### Zentrale Variablen

| Variable | Zweck | Standard/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Backend-Port | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Medien-Root-Verzeichnis | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL-DSN | Lokaler DB-Fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish-Endpunkt | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Request-Timeout für AutoPublish (Sekunden) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Skriptpfad für Whisper/VAD | Umgebungsabhängig |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR-Modellnamen | `large-v3` / `large-v2` (Beispiel) |
| `LAZYEDIT_CAPTION_PYTHON` | Python-Runtime für Caption-Pipeline | Umgebungsabhängig |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Primärer Captioning-Pfad/-Skript | Umgebungsabhängig |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Fallback-Captioning-Pfad/-Skript/-cwd | Umgebungsabhängig |
| `GRSAI_API_*` | Veo/GRSAI-Integrations-Einstellungen | Umgebungsabhängig |
| `VENICE_*`, `A2E_*` | Venice/A2E-Integrations-Einstellungen | Umgebungsabhängig |
| `OPENAI_API_KEY` | Erforderlich für OpenAI-basierte Features | None |

Hinweise zu maschinenspezifischen Einstellungen:
- `app.py` kann CUDA-Verhalten setzen (Nutzung von `CUDA_VISIBLE_DEVICES` im Kontext der Codebasis).
- Einige Standardpfade sind auf bestimmte Workstations zugeschnitten; nutze `.env`-Overrides für portable Setups.
- `lazyedit_config.sh` steuert tmux-/Session-Startvariablen für Deployment-Skripte.

## 🔌 API-Beispiele

Die Base-URL-Beispiele gehen von `http://localhost:8787` aus.

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

End-to-end-Prozess:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Videos auflisten:

```bash
curl http://localhost:8787/api/videos
```

Publish-Paket:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Weitere Endpunkte und Payload-Details: `references/API_GUIDE.md`.

## 🧪 Beispiele

### Frontend lokal ausführen (Web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Falls das Backend auf `8887` läuft:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android-Emulator

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS-Simulator (macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### Optionaler Sora-Generierungs-Helper

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Unterstützte Sekundenwerte: `4`, `8`, `12`.
Unterstützte Größen: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Entwicklungshinweise

- Verwende `python` aus der Conda-Umgebung `lazyedit` (nicht vom System-`python3` ausgehen).
- Halte große Medien außerhalb von Git; speichere Laufzeitmedien in `DATA/` oder externem Storage.
- Initialisiere/aktualisiere Submodule, sobald Pipeline-Komponenten nicht aufgelöst werden können.
- Halte Änderungen fokussiert; vermeide große, nicht zusammenhängende Formatierungsänderungen.
- Für Frontend-Arbeit wird die Backend-API-URL über `EXPO_PUBLIC_API_URL` gesteuert.
- CORS ist im Backend für die App-Entwicklung offen.

Richtlinie für Submodule und externe Abhängigkeiten:
- Behandle externe Abhängigkeiten als upstream-owned. In diesem Repository-Workflow solltest du Submodule intern nur ändern, wenn du gezielt in diesen Projekten arbeitest.
- Die operative Leitlinie in diesem Repo behandelt `furigana` (und in manchen lokalen Setups `echomind`) als externe Abhängigkeitspfade; bei Unsicherheit Upstream unverändert lassen und In-Place-Edits vermeiden.

Hilfreiche Referenzen:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ Tests

Die derzeitige formale Testabdeckung ist minimal und DB-orientiert.

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Für funktionale Validierung nutze die Web-UI und den API-Flow mit einem kurzen Beispielclip in `DATA/`.

## 🚢 Deployment- & Sync-Hinweise

Aktuell bekannte Pfade und Sync-Flow (aus den Repository-Betriebsdokumenten):

- Entwicklungs-Workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deploytes LazyEdit-Backend + App: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deploytes AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing-System-Host: `/home/lachlan/Projects/auto-publish` auf `lazyingart`

Nach dem Push von `AutoPublish/`-Updates aus diesem Repo auf dem Publishing-Host pullen:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Fehlerbehebung

| Problem | Prüfung / Lösung |
| --- | --- |
| Fehlende Pipeline-Module oder Skripte | `git submodule update --init --recursive` ausführen |
| FFmpeg nicht gefunden | FFmpeg installieren und prüfen, ob `ffmpeg -version` funktioniert |
| Portkonflikte | Backend standardmäßig `8787`; `start_lazyedit.sh` standardmäßig `18787`; `LAZYEDIT_PORT` oder `PORT` explizit setzen |
| Expo erreicht Backend nicht | Prüfen, ob `EXPO_PUBLIC_API_URL` auf aktiven Backend-Host/-Port zeigt |
| Datenbankverbindungsprobleme | PostgreSQL + DSN/Env-Variablen prüfen; optionaler Smoke Check: `python db_smoke_test.py` |
| GPU/CUDA-Probleme | Treiber/CUDA-Kompatibilität mit installiertem Torch-Stack prüfen |
| Service-Skript schlägt bei Installation fehl | Sicherstellen, dass `lazyedit_config.sh`, `start_lazyedit.sh` und `stop_lazyedit.sh` vor Ausführung des Installers existieren |

## 🗺️ Roadmap

- In-App-Editing für Untertitel/Segmente mit A/B-Vorschau und Steuerung pro Zeile.
- Robustere End-to-end-Testabdeckung für zentrale API-Flows.
- Dokumentations-Konvergenz über i18n-README-Varianten und Deployment-Modi hinweg.
- Zusätzliche Workflow-Härtung für Retries bei Generierungsanbietern und bessere Status-Sichtbarkeit.

## 🤝 Mitwirken

Beiträge sind willkommen.

1. Forken und einen Feature-Branch erstellen.
2. Commits fokussiert und klar begrenzt halten.
3. Änderungen lokal validieren (`python app.py`, zentraler API-Flow und App-Integration falls relevant).
4. PR mit Zweck, Reproduktionsschritten und Vorher/Nachher-Notizen öffnen (bei UI-Änderungen mit Screenshots).

Praktische Richtlinien:
- Python-Style einhalten (PEP 8, 4 Leerzeichen, snake_case-Namensgebung).
- Keine Zugangsdaten oder große Binärdateien committen.
- Doku/Config-Skripte aktualisieren, wenn sich Verhalten ändert.
- Bevorzugter Commit-Stil: kurz, imperativ, scoped (zum Beispiel: `fix ffmpeg 7 compatibility`).

## ❤️ Was deine Unterstützung ermöglicht

- <b>Werkzeuge offen halten</b>: Hosting, Inferenz, Datenspeicher und Community-Betrieb.  
- <b>Schneller liefern</b>: Wochen fokussierter Open-Source-Zeit für EchoMind, LazyEdit und MultilingualWhisper.  
- <b>Wearables prototypen</b>: Optik, Sensorik und neuromorphe/Edge-Komponenten für IdeasGlass + LightMind.  
- <b>Zugang für alle</b>: Subventionierte Deployments für Studierende, Creator und Community-Gruppen.

### Spenden

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

## 📄 Lizenz

[Apache-2.0](LICENSE)

## 🙏 Danksagungen

LazyEdit baut auf Open-Source-Bibliotheken und -Diensten auf, darunter:
- FFmpeg für Media Processing
- Tornado für Backend-APIs
- MoviePy für Editing-Workflows
- OpenAI-Modelle für KI-gestützte Pipeline-Aufgaben
- CJKWrap und mehrsprachige Text-Tools in Untertitel-Workflows
