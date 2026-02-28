[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>KI-unterstützter Video-Workflow</b> für Generierung, Untertitelverarbeitung, Metadaten und optionales Publishing.
  <br />
  <sub>Upload oder Generierung -> Transkription -> Übersetzen/Überarbeiten -> Untertitel einbrennen -> Captioning/Keyframes -> Metadaten -> Veröffentlichung</sub>
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

## 📌 Kurzfakten

LazyEdit ist ein durchgängiger KI-unterstützter Video-Workflow für Erstellung, Verarbeitung und optionales Publishing. Es kombiniert prompt-basierte Generierung (Stage A/B/C), Medienverarbeitungs-APIs, Untertitel-Rendering, Keyframe-Beschriftung, Metadatengenerierung und Übergabe an AutoPublish.

| Kurzinfo | Wert |
| --- | --- |
| 📘 Kanonisches README | `README.md` (diese Datei) |
| 🌐 Sprachvarianten | `i18n/README.*.md` (in jeder README gibt es eine einzige Sprachleiste am Anfang) |
| 🧠 Backend-Einstiegspunkt | `app.py` (Tornado) |
| 🖥️ Frontend-App | `app/` (Expo Web/Mobile) |

## 🧭 Inhalte

- Überblick
- Kurzfakten
- Kurzüberblick
- Architektur-Snapshot
- Demos
- Funktionen
- Dokumentation & i18n
- Projektstruktur
- Voraussetzungen
- Installation
- Schnellstart
- Command Cheat Sheet
- Nutzung
- Konfiguration
- Konfigurationsdateien
- API-Beispiele
- Beispiele
- Entwicklungsnotizen
- Tests
- Annahmen und bekannte Grenzen
- Deployment- und Sync-Notizen
- Fehlerbehebung
- Roadmap
- Mitwirken
- Support
- Lizenz
- Danksagungen

## ✨ Überblick

LazyEdit basiert auf einem Tornado-Backend (`app.py`) und einem Expo-Frontend (`app/`).

> Hinweis: Wenn sich Repo-/Laufzeitdetails zwischen Maschinen unterscheiden, die vorhandenen Defaults beibehalten und stattdessen maschinenspezifische Werte per Umgebungsvariablen überschreiben.

| Warum Teams es nutzen | Praktischer Nutzen |
| --- | --- |
| Einheitlicher Operator-Flow | Upload, Generierung, Remixen und Veröffentlichung aus einem einzigen Workflow |
| API-first-Design | Einfach zu skripten und in andere Tools integrierbar |
| Local-first Laufzeit | Funktioniert mit `tmux`- und Service-basierten Bereitstellungsmustern |

| Schritt | Was passiert |
| --- | --- |
| 1 | Video hochladen oder generieren |
| 2 | Transkribieren und Untertitel optional übersetzen |
| 3 | Mehrsprachige Untertitel mit Layouteinstellungen einbrennen |
| 4 | Keyframes, Captions und Metadaten erzeugen |
| 5 | Paket erstellen und optional über AutoPublish veröffentlichen |

### Pipeline-Fokus

- Upload, Generierung, Remixen und Bibliotheksverwaltung aus einer einzelnen Bedienoberfläche.
- API-first-Verarbeitungsfluss für Transkription, Untertitel-Politur/Übersetzung, Burn-in und Metadaten.
- Optionale Integrationen für Generierungsprovider (Veo / Venice / A2E / Sora-Helfer in `agi/`).
- Optionale Publishing-Übergabe über `AutoPublish`.

## 🎯 Kurzüberblick

| Bereich | In LazyEdit enthalten | Status |
| --- | --- | --- |
| Kernanwendung | Tornado-API-Backend + Expo-Web-/Mobile-Frontend | ✅ |
| Medienpipeline | ASR, Untertitelübersetzung/-politur, Burn-in, Keyframes, Captions, Metadaten | ✅ |
| Generierung | Stage A/B/C und Provider-Helper-Routen (`agi/`) | ✅ |
| Distribution | Optionale Übergabe an AutoPublish | 🟡 Optional |
| Laufzeitmodell | Lokale Skripte, tmux-Workflows, optionaler systemd-Service | ✅ |

## 🏗️ Architektur-Snapshot

Das Repository ist als API-first-Medienpipeline mit UI-Schicht organisiert:

- `app.py` ist der Tornado-Einstiegspunkt und Orchestrator für Upload, Verarbeitung, Generierung, Publishing-Übergabe und Media Serving.
- `lazyedit/` enthält modulare Pipeline-Bausteine (DB-Persistenz, Übersetzung, Untertitel-Rendering, Captions, Metadaten, Provider-Adapter).
- `app/` ist eine Expo Router-App (Web/Mobile), die Upload-, Verarbeitungs-, Vorschau- und Publishing-Flows steuert.
- `config.py` zentralisiert das Laden von Umgebungsvariablen und Standard-/Fallback-Pfade.
- `start_lazyedit.sh` und `lazyedit_config.sh` bieten reproduzierbare tmux-basierte lokale/deployte Betriebsarten.

| Schicht | Hauptpfade | Verantwortung |
| --- | --- | --- |
| API & Orchestrierung | `app.py`, `config.py` | Endpunkte, Routing, Auflösung von Umgebungswerten |
| Verarbeitungskern | `lazyedit/`, `agi/` | Untertitel-/Caption-/Metadaten-Pipeline + Provider |
| UI | `app/` | Bedieneroberfläche (Web/Mobile über Expo) |
| Laufzeitskripte | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Lokaler/service-basierter Start und Betrieb |

High-Level-Fluss:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

Die Screens unten zeigen den Hauptprozess von der Aufnahme bis zur Metadatenerstellung.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Start · Upload</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Start · Generieren</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Start · Remixen</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Bibliothek</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Videoübersicht</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Übersetzungsvorschau</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Burn Slots</sub>
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
      <br /><sub>Metadatengenerator</sub>
    </td>
  </tr>
</table>

## 🧩 Funktionen

- ✨ Prompt-basierter Generierungsworkflow (Stage A/B/C) mit Integrationspfaden für Sora und Veo.
- 🧵 Vollständige Verarbeitungspipeline: Transkription -> Untertitel-Politur/Übersetzung -> Burn-in -> Keyframes -> Captions -> Metadaten.
- 🌏 Multilinguale Untertitelerstellung mit Unterstützungspfaden für Furigana/IPA/Romaji.
- 🔌 API-first-Backend mit Upload-, Verarbeitungs-, Medienbereitstellungs- und Publish-Queue-Endpunkten.
- 🚚 Optionale AutoPublish-Integration für Übergaben an Social-Plattformen.
- 🖥️ Kombinierter Backend- + Expo-Workflow über tmux-Startskripte.

## 🌍 Dokumentation & i18n


- Kanonische Quelle: `README.md`
- Sprachvarianten: `i18n/README.*.md`
- Sprachnavigation: In jeder README bleibt eine einzelne Sprachoptionen-Zeile am Anfang erhalten (keine Duplikate).
- Aktuelle Sprachen in diesem Repo: Arabisch, Deutsch, Englisch, Spanisch, Französisch, Japanisch, Koreanisch, Russisch, Vietnamesisch, vereinfachtes Chinesisch, traditionelles Chinesisch.

Wenn es Inkonsistenzen zwischen Übersetzungen und der englischen Dokumentation gibt, gilt die englische README als verbindliche Quelle. Danach werden die jeweiligen Sprachdateien einzeln aktualisiert.

| i18n-Richtlinie | Regel |
| --- | --- |
| Kanonische Quelle | `README.md` als Source-of-Truth |
| Sprachleiste | Genau eine Sprachauswahlzeile am Anfang |

## 🗂️ Projektstruktur

```text
LazyEdit/
├── app.py                           # Tornado-Backend-Einstiegspunkt und API-Orchestrierung
├── app/                             # Expo-Frontend (web/mobile)
├── lazyedit/                        # Kernmodule der Pipeline (Übersetzung, Metadaten, Burner, DB, Templates)
├── agi/                             # Abstraktion der Generierungsprovider (Routen für Sora/Veo/A2E/Venice)
├── DATA/                            # Laufzeitmedien (Ein-/Ausgabe), hier in diesem Workspace Symlink
├── translation_logs/                 # Übersetzungsprotokolle
├── temp/                            # Temporäre Laufzeitdateien
├── install_lazyedit.sh              # systemd-Installer (erwartet vorhandene Konfigurations-/Start/Stop-Skripte)
├── start_lazyedit.sh                # tmux-Launcher für Backend + Expo
├── stop_lazyedit.sh                 # Hilfs-Skript zum Stoppen des tmux-Starts
├── lazyedit_config.sh               # Deployment-/Laufzeit-Shellkonfiguration
├── config.py                        # Auflösung von Umgebung/Config (Ports, Pfade, AutoPublish-URL)
├── .env.example                     # Template für Umgebungsüberschreibungen
├── references/                      # Ergänzende Dokumentation (API-Guide, Quickstart, Deployment-Notizen)
├── AutoPublish/                     # Submodul (optionale Publishing-Pipeline)
├── AutoPubMonitor/                  # Submodul (Monitor-/Sync-Automation)
├── whisper_with_lang_detect/        # Submodul (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodul (primäre Caption-Erstellung)
├── clip-gpt-captioning/             # Submodul (Fallback-Captioner)
└── furigana/                        # Externe Abhängigkeit im Workflow (in diesem Checkout als Submodul)
```

Hinweis zu Submodulen/externen Abhängigkeiten:
- Git-Submodule in diesem Repo sind `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` und `furigana`.
- In diesem Repo wird `furigana` und manchmal `echomind` als externe, nur lesbare Abhängigkeit betrachtet. Bei Unsicherheit: upstream belassen und nicht vor Ort editieren.

## ✅ Voraussetzungen

| Abhängigkeit | Hinweise |
| --- | --- |
| Linux-Umgebung | Skripte für `systemd`/`tmux` sind auf Linux ausgerichtet |
| Python 3.10+ | Nutze die Conda-Umgebung `lazyedit` |
| Node.js 20+ + npm | Für die Expo-App in `app/` erforderlich |
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

3. Optionale Systeminstallation (Service-Modus):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Kurze Installationshinweise:
- `install_lazyedit.sh` installiert `ffmpeg` und `tmux`, anschließend wird `lazyedit.service` erstellt.
- Skript erzeugt `lazyedit_config.sh`, `start_lazyedit.sh` oder `stop_lazyedit.sh` nicht neu; diese Dateien müssen bereits existieren und korrekt sein.

## ⚡ Schnellstart

Start von Backend und Frontend lokal (minimaler Pfad):

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

In einem zweiten Terminal:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Optionaler lokaler Datenbank-Bootstrap:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Laufzeitprofile

| Profil | Startbefehl | Standard-Backend | Standard-Frontend |
| --- | --- | --- | --- |
| Lokale Entwicklung (manuell) | `python app.py` + Expo-Befehl | `8787` | `8091` (Beispielbefehl) |
| Tmux-orchestriert | `./start_lazyedit.sh` | `18787` | `18791` |
| Systemd-Service | `sudo systemctl start lazyedit.service` | Konfigurations-/Umgebungsabhängig | N/A |

## 🧭 Command Cheat Sheet

| Aufgabe | Befehl |
| --- | --- |
| Submodule initialisieren | `git submodule update --init --recursive` |
| Nur Backend starten | `python app.py` |
| Backend + Expo (tmux) | `./start_lazyedit.sh` |
| tmux-Run stoppen | `./stop_lazyedit.sh` |
| tmux-Session öffnen | `tmux attach -t lazyedit` |
| Service-Status | `sudo systemctl status lazyedit.service` |
| Service-Logs | `sudo journalctl -u lazyedit.service` |
| DB-Smoke-Test | `python db_smoke_test.py` |
| Pytest-Smoke-Test | `pytest tests/test_db_smoke.py` |

## 🛠️ Nutzung

### Entwicklung: Nur Backend

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Alternativer Einstiegspunkt aus den aktuellen Deploy-Skripten:

```bash
python app.py -m lazyedit
```

Standard-URL des Backends: `http://localhost:8787` (laut `config.py`, überschreibbar via `PORT` oder `LAZYEDIT_PORT`).

### Entwicklung: Backend + Expo-App (tmux)

```bash
./start_lazyedit.sh
```

Standard-Ports von `start_lazyedit.sh`:
- Backend: `18787`
- Expo Web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Session anhängen:

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

Hinweis zur Konfigurationspriorität:

- `config.py` lädt Werte aus `.env`, sofern vorhanden, und setzt nur Schlüssel, die nicht bereits in der Shell exportiert sind.
- Laufzeitwerte können daher kommen von: shell-exportierte Env-Variablen -> `.env` -> Code-Defaults.
- Für `tmux`/Service-Läufe steuert `lazyedit_config.sh` die Start-/Session-Parameter (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, Ports via Startup-Skript).

### Wichtige Variablen

| Variable | Zweck | Standard/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Backend-Port | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Medien-Stammverzeichnis | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Lokaler Fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish-Endpunkt | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish-Timeout in Sekunden | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Pfad zu Whisper/VAD-Skript | Umgebungsabhängig |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR-Modellnamen | `large-v3` / `large-v2` (Beispiel) |
| `LAZYEDIT_CAPTION_PYTHON` | Python-Runtime für Caption-Pipeline | Umgebungsspezifisch |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Primärer Caption-Pfad/-Skript | Umgebungsspezifisch |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Fallback-Caption-Pfad/Skript/CWD | Umgebungsspezifisch |
| `GRSAI_API_*` | Veo/GRSAI-Integrationskonfiguration | Umgebungsspezifisch |
| `VENICE_*`, `A2E_*` | Venice/A2E-Integrationskonfiguration | Umgebungsspezifisch |
| `OPENAI_API_KEY` | Erforderlich für OpenAI-gestützte Funktionen | Nicht gesetzt |

Hinweise zu maschinenspezifischen Werten:
- `app.py` kann das CUDA-Verhalten setzen (`CUDA_VISIBLE_DEVICES` im Codekontext).
- Einige Standardpfade sind werkstationsspezifisch; nutze `.env`-Overrides für portablere Setups.
- `lazyedit_config.sh` steuert bei Deployment-Skripten die tmux-/Session-Variablen.

## 🧾 Konfigurationsdateien

| Datei | Zweck |
| --- | --- |
| `.env.example` | Vorlage für Umgebungsvariablen, die Backend/Services verwenden |
| `.env` | Maschinenlokale Overrides; wird von `config.py`/`app.py` geladen, wenn vorhanden |
| `config.py` | Backend-Defaults und Umgebungsauflösung |
| `lazyedit_config.sh` | tmux/service-Runtime-Profil (Deploy-Pfad, Conda-Env, App-Args, Session-Name) |
| `start_lazyedit.sh` | Startet Backend + Expo im tmux mit gewählten Ports |
| `install_lazyedit.sh` | Erstellt `lazyedit.service` und prüft bestehende Skripte/Config |

Empfohlene Aktualisierungsreihenfolge für Portabilität:
1. `.env.example` nach `.env` kopieren.
2. `LAZYEDIT_*`-Werte für Pfade und APIs in `.env` setzen.
3. `lazyedit_config.sh` nur bei tmux-/Service-Betriebsverhalten anpassen.

## 🔌 API-Beispiele

Base-URL-Beispiele gehen von `http://localhost:8787` aus.

| API-Gruppe | Typische Endpunkte |
| --- | --- |
| Upload und Medien | `/upload`, `/upload-stream`, `/media/*` |
| Videodatensätze | `/api/videos`, `/api/videos/{id}` |
| Verarbeitung | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publishing | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generierung | `/api/videos/generate` (+ Provider-Routen in `app.py`) |

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Durchgängiger Prozess:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Video-Listen:

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

Wichtige Endpoint-Gruppen, die typischerweise genutzt werden:
- Video-Lebenszyklus: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Verarbeitung: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Generierung/Provider-Pfade: `/api/videos/generate` plus Venice/A2E-Routen in `app.py`
- Distribution: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Beispiele

### Frontend lokal starten (Web)

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

### Optionaler Sora-Generierungshelfer

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Unterstützte Sekunden: `4`, `8`, `12`.
Unterstützte Größen: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Entwicklungsnotizen

- Verwende `python` aus der Conda-Umgebung `lazyedit` (nicht pauschal System-`python3` annehmen).
- Halte große Mediendateien aus Git raus; speichere Laufzeitmedien in `DATA/` oder extern.
- Initialisiere/aktualisiere Submodule, wenn Pipelinebestandteile nicht auflösbar sind.
- Halte Änderungen fokussiert; vermeide große Formatierungsänderungen außerhalb des Ziels.
- Für Frontend-Arbeit wird die API-URL vom `EXPO_PUBLIC_API_URL` gesteuert.
- CORS ist für App-Entwicklung im Backend offen.

Submodule- und externe-Dependency-Policy:
- Externe Abhängigkeiten als Upstream-Paket betrachten. In diesem Repository-Prozess werden Submodule nicht bearbeitet, außer wenn bewusst im jeweiligen Projekt gearbeitet wird.
- Das operative Vorgehen behandelt `furigana` (und gelegentlich `echomind` in manchen Setups) als externe, unveränderte Abhängigkeit; im Zweifel: upstream beibehalten und nicht lokal anpassen.

Nützliche Referenzen:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Sicherheits-/Konfigurations-Hygiene:
- Halte API-Keys und Secrets in Umgebungsvariablen; keine Credentials im Repo.
- Bevorzuge `.env` für maschinenlokale Overrides und halte `.env.example` als öffentliche Vorlage.
- Falls sich CUDA/GPU-Verhalten je Host unterscheidet, ändere Umgebungswerte statt harteingetippte Maschinenwerte.

## ✅ Tests

Die aktuelle formale Testabdeckung ist minimal und stark DB-orientiert.

| Prüfschicht | Befehl/Methode |
| --- | --- |
| DB Smoke | `python db_smoke_test.py` |
| Pytest DB-Check | `pytest tests/test_db_smoke.py` |
| Funktionaler Ablauf | Web-UI + API-Run mit kurzem Clip in `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Für funktionale Validierung nutze Web-UI und API-Fluss mit einem kurzen Beispielclip in `DATA/`.

Portabilitäts- und Annahmen-Hinweise:
- Einige Standardpfade im Code sind werkstationsspezifische Fallbacks; das ist im aktuellen Repo-Stand zu erwarten.
- Wenn ein Standardpfad nicht auf deiner Maschine existiert, setze die entsprechende `LAZYEDIT_*`-Variable in `.env`.
- Bei Unklarheit zu einem Maschinenwert: Standard beibehalten und explizite Overrides setzen, statt Defaults zu löschen.

## 🧱 Annahmen & bekannte Grenzen

- Die Backend-Abhängigkeiten sind im Root nicht per Lockfile versioniert; die Reproduzierbarkeit hängt derzeit vom lokalen Setup ab.
- `app.py` ist im aktuellen Repo-Stand absichtlich monolithisch und enthält eine große Endpoint-Fläche.
- Die meiste Pipeline-Verifikation ist Integrations-/Manuell (UI + API + Beispielmedien), mit begrenzter automatisierter Testabdeckung.
- Laufzeitverzeichnisse (`DATA/`, `temp/`, `translation_logs/`) sind operative Outputs und können deutlich wachsen.
- Für vollständige Funktionalität werden Submodule benötigt; unvollständige Checkouts verursachen meist fehlende Script-Fehler.

## 🚢 Deployment- & Sync-Notizen

Aktuelle bekannte Pfade und Sync-Flow (aus den Betriebsunterlagen):

- Entwicklungs-Workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit Backend + App: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing-System auf Host: `/home/lachlan/Projects/auto-publish` auf `lazyingart`

| Umgebung | Pfad | Hinweise |
| --- | --- | --- |
| Dev-Workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Hauptquelle + Submodule |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` in den Ops-Dokumenten |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Monitor-/Sync-/Process-Sessions |
| Publishing-Host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull nach Submodul-Updates |

Nach dem Push von `AutoPublish/`-Änderungen aus diesem Repo auf dem Publishing-Host:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Fehlerbehebung

| Problem | Prüfen / Beheben |
| --- | --- |
| Fehlende Pipeline-Module oder Skripte | `git submodule update --init --recursive` ausführen |
| FFmpeg nicht gefunden | FFmpeg installieren und `ffmpeg -version` prüfen |
| Portkonflikte | Backend läuft standardmäßig auf `8787`; `start_lazyedit.sh` auf `18787`; setze `LAZYEDIT_PORT` oder `PORT` explizit |
| Expo erreicht Backend nicht | Sicherstellen, dass `EXPO_PUBLIC_API_URL` auf aktiven Backend-Host/Port zeigt |
| Datenbank-Verbindungsprobleme | PostgreSQL + DSN/Env-Variablen prüfen; optionaler Smoke-Check: `python db_smoke_test.py` |
| GPU/CUDA-Probleme | Treiber-/CUDA-Kompatibilität mit installiertem Torch-Stack prüfen |
| Service-Skript bricht bei Installation ab | Vor dem Installer `lazyedit_config.sh`, `start_lazyedit.sh` und `stop_lazyedit.sh` prüfen |

## 🗺️ Roadmap

- In-App-Editing für Untertitel/Segmente mit A/B-Vorschau und Zeilenkontrollen.
- Stärkere End-to-End-Testabdeckung für zentrale API-Flows.
- Dokumentationsangleichung über i18n-README-Varianten und Bereitstellungsmodi.
- Mehr Workflow-Härtung für Retry-Logik und Statustransparenz bei Generierungsprovidern.

## 🤝 Mitwirken

Beiträge sind willkommen.

1. Forken und Feature-Branch anlegen.
2. Commits fokussiert und im Scope halten.
3. Änderungen lokal prüfen (`python app.py`, wichtiger API-Flow und App-Integration, falls relevant).
4. PR mit Ziel, Reproduktionsschritten und Vorher/Nachher-Notizen erstellen (Screenshots bei UI-Änderungen).

Praktische Richtlinien:
- Halte dich an Python-Stil (PEP 8, 4 Leerzeichen, snake_case).
- Keine Credentials oder großen Binärdateien committen.
- Aktualisiere Dokumentation und Config-Dateien bei Verhaltensänderungen.
- Bevorzugter Commit-Stil: kurz, imperativ, scoped (z. B. `fix ffmpeg 7 compatibility`).



## 📄 Lizenz

[Apache-2.0](LICENSE)

## 🙏 Danksagungen

LazyEdit baut auf Open-Source-Bibliotheken und Diensten auf, darunter:
- FFmpeg für Medienverarbeitung
- Tornado für Backend-APIs
- MoviePy für Bearbeitungsworkflows
- OpenAI-Modelle für KI-gestützte Pipeline-Aufgaben
- CJKWrap und mehrsprachige Textwerkzeuge in Untertitelworkflows


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
