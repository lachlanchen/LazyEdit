[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0" /></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Backend-Tornado-222222" alt="Backend: Tornado" />
  <img src="https://img.shields.io/badge/Frontend-Expo-000020?logo=expo&logoColor=white" alt="Frontend: Expo" />
  <img src="https://img.shields.io/badge/Platform-Linux-informational?logo=linux&logoColor=white" alt="Plattform: Linux" />
  <img src="https://img.shields.io/badge/FFmpeg-required-0A0A0A?logo=ffmpeg&logoColor=white" alt="FFmpeg erforderlich" />
  <img src="https://img.shields.io/badge/PostgreSQL-supported-336791?logo=postgresql&logoColor=white" alt="PostgreSQL unterstützt" />
  <img src="https://img.shields.io/badge/Stage_A%2FB%2FC-enabled-0f766e" alt="Stage A/B/C aktiviert" />
  <img src="https://img.shields.io/badge/AutoPublish-optional-orange" alt="AutoPublish optional" />
  <img src="https://img.shields.io/badge/i18n-11%20languages-1f883d" alt="i18n: 11 Sprachen" />
</p>

<p align="center">
  <b>KI-unterstützter Video-Workflow</b> für Generierung, Untertitelverarbeitung, Metadaten und optionales Publishing.
  <br />
  <sub>Upload oder Generierung -> Transkription -> Übersetzen/Polieren -> Untertitel einbrennen -> Captioning/Keyframes -> Metadaten -> Veröffentlichung</sub>
</p>

# LazyEdit

LazyEdit ist ein durchgängiger, KI-gestützter Video-Workflow für Erstellung, Verarbeitung und optionales Publishing. Es kombiniert promptbasierte Generierung (Stage A/B/C), Medienverarbeitungs-APIs, Untertitel-Rendering, Keyframe-Captioning, Metadaten-Generierung und die Übergabe an AutoPublish.

| Kurzinfo | Wert |
| --- | --- |
| 📘 Kanonischer README | `README.md` (englische Originalfassung) |
| 🌐 Sprachvarianten | `i18n/README.*.md` (in jeder README befindet sich genau eine Sprachleiste oben) |
| 🧠 Backend-Entrypoint | `app.py` (Tornado) |
| 🖥️ Frontend-App | `app/` (Expo web/mobile) |

## 🧭 Inhaltsverzeichnis

- Überblick
- Auf einen Blick
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
- Annahmen & bekannte Grenzen
- Deployment & Synchronisationsnotizen
- Fehlerbehebung
- Roadmap
- Beiträge
- Support
- Lizenz
- Danksagungen

## ✨ Überblick

LazyEdit basiert auf einem Tornado-Backend (`app.py`) und einem Expo-Frontend (`app/`).

> Hinweis: Wenn Repo-/Laufzeitdetails von Maschine zu Maschine variieren, die vorhandenen Defaults beibehalten und maschinenspezifische Werte stattdessen per Umgebungsvariablen überschreiben.

| Warum Teams es nutzen | Praktischer Effekt |
| --- | --- |
| Einheitlicher Operator-Flow | Hochladen/Generieren/Remixen/Veröffentlichen in einem Workflow |
| API-first-Design | Leicht zu skripten und in andere Tools integrierbar |
| Local-first-Laufzeit | Funktioniert mit tmux + service-basierten Deployment-Mustern |

| Schritt | Was passiert |
| --- | --- |
| 1 | Video hochladen oder generieren |
| 2 | Transkription und optionales Übersetzen der Untertitel |
| 3 | Multilinguale Untertitel mit Layout-Steuerung einbrennen |
| 4 | Keyframes, Captions und Metadaten erzeugen |
| 5 | Paket erstellen und optional über AutoPublish veröffentlichen |

### Pipeline-Fokus

- Upload, Generierung, Remixen und Bibliotheksverwaltung aus einer einheitlichen Operator-Oberfläche.
- API-first-Verarbeitungsfluss für Transkription, Untertitel-Politur/Übersetzung, Burn-in und Metadaten.
- Optionale Provider-Integrationen (Veo / Venice / A2E / Sora-Helpers in `agi/`).
- Optionale Publishing-Übergabe über `AutoPublish`.

## 🎯 Auf einen Blick

| Bereich | In LazyEdit enthalten | Status |
| --- | --- | --- |
| Kernanwendung | Tornado-API-Backend + Expo-Web/Mobile-Frontend | ✅ |
| Medien-Pipeline | ASR, Untertitel-Übersetzung/Politur, Burn-in, Keyframes, Captions, Metadaten | ✅ |
| Generierung | Stage A/B/C und Provider-Helper-Routen (`agi/`) | ✅ |
| Distribution | Optionale AutoPublish-Übergabe | 🟡 Optional |
| Laufzeitmodell | Local-first-Skripte, tmux-Workflows, optionaler systemd-Service | ✅ |

## 🏗️ Architektur-Snapshot

Das Repository ist als API-first-Medienpipeline mit UI-Schicht organisiert:

- `app.py` ist der Tornado-Einstiegspunkt und Orchestrator für Upload, Verarbeitung, Generierung, Publishing-Übergabe und Medien-Serving.
- `lazyedit/` enthält modulare Pipeline-Bausteine (DB-Persistenz, Übersetzung, Untertitel-Rendering, Captions, Metadaten, Provider-Adapter).
- `app/` ist eine Expo-Router-App (web/mobile), die Upload-, Verarbeitungs-, Vorschau- und Publishing-Flows steuert.
- `config.py` bündelt das Laden von Umgebungskonfiguration und Standard-/Fallback-Pfaden.
- `start_lazyedit.sh` und `lazyedit_config.sh` liefern reproduzierbare lokale/deployte Betriebsmodi über tmux.

| Schicht | Hauptpfade | Verantwortlichkeit |
| --- | --- | --- |
| API & Orchestrierung | `app.py`, `config.py` | Endpunkte, Routing, Umgebungsauflösung |
| Verarbeitungs-Kern | `lazyedit/`, `agi/` | Untertitel-/Caption-/Metadaten-Pipeline + Provider |
| UI | `app/` | Operator-Erlebnis (web/mobile über Expo) |
| Laufzeitskripte | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Lokaler/service-basierter Start und Betrieb |

High-Level-Fluss:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

Die Screens unten zeigen den Hauptweg von der Aufnahme bis zur Metadaten-Generierung.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Home · Upload</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Home · Generieren</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Home · Remixen</sub>
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
      <br /><sub>Metadaten-Generator</sub>
    </td>
  </tr>
</table>

## 🧩 Funktionen

- ✨ Promptbasierter Generierungs-Workflow (Stage A/B/C) mit Integrationspfaden für Sora und Veo.
- 🧵 Vollständige Verarbeitungspipeline: Transkription -> Untertitel-Politur/Übersetzung -> Burn-in -> Keyframes -> Captions -> Metadaten.
- 🌏 Multilinguale Untertitelzusammenstellung mit furigana/IPA/Romaji-bezogenen Verarbeitungswegen.
- 🔌 API-first-Backend mit Upload-, Verarbeitungs-, Medienauslieferungs- und Publish-Queue-Endpunkten.
- 🚚 Optionale AutoPublish-Integration für Social-Platform-Übergabe.
- 🖥️ Kombinierter Backend- + Expo-Workflow, bereitgestellt über tmux-Startskripte.

## 🌍 Dokumentation & i18n

LazyEdit hält ein kanonisches englisches README (`README.md`) und Sprachvarianten unter `i18n/`.

- Kanonische Quelle: `README.md`
- Sprachvarianten: `i18n/README.*.md`
- Sprachnavigation: In jeder README genau eine Sprach-Option-Leiste am Anfang (keine Duplikate).
- Derzeitige Sprachen im Repo: Arabisch, Deutsch, Englisch, Spanisch, Französisch, Japanisch, Koreanisch, Russisch, Vietnamesisch, vereinfachtes Chinesisch, traditionelles Chinesisch.

Bei Widersprüchen zwischen Übersetzungen und englischer Dokumentation gilt stets die englische Fassung als Quelle, danach wird pro Sprache aktualisiert.

| i18n-Richtlinie | Regel |
| --- | --- |
| Kanonische Quelle | `README.md` als Source-of-Truth |
| Sprachleiste | Genau eine Sprach-Optionszeile am Anfang |
| Reihenfolge | Zuerst Englisch, dann jede `i18n/README.*.md` nacheinander |

## 🗂️ Projektstruktur

```text
LazyEdit/
├── app.py                           # Tornado-Backend-Einstiegspunkt und API-Orchestrierung
├── app/                             # Expo-Frontend (web/mobile)
├── lazyedit/                        # Kernpipeline-Module (Übersetzung, Metadaten, Burner, DB, Templates)
├── agi/                             # Abstraktion der Generierungsprovider (Sora/Veo/A2E/Venice-Routen)
├── DATA/                            # Laufzeit-Medien Ein-/Ausgabe (Symlink in diesem Workspace)
├── translation_logs/                 # Übersetzungsprotokolle
├── temp/                            # Temporäre Laufzeitdateien
├── install_lazyedit.sh              # systemd-Installer (erwartet config/start/stop-Skripte)
├── start_lazyedit.sh                # tmux-Launcher für Backend + Expo
├── stop_lazyedit.sh                 # tmux-Stop-Helfer
├── lazyedit_config.sh               # Deployment-/Laufzeit-Shell-Konfiguration
├── config.py                        # Umgebungs-/Konfigurationsauflösung (Ports, Pfade, AutoPublish-URL)
├── .env.example                     # Template für Umgebungsüberschreibung
├── references/                      # Zusatzdokumente (API-Leitfaden, Schnellstart, Deployment-Notizen)
├── AutoPublish/                     # Submodul (optionale Publishing-Pipeline)
├── AutoPubMonitor/                  # Submodul (Monitor-/Sync-Automation)
├── whisper_with_lang_detect/         # Submodul (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodul (primärer Captioner)
├── clip-gpt-captioning/             # Submodul (Fallback-Captioner)
└── furigana/                        # Externe Abhängigkeit im Workflow (als Submodul in diesem Checkout)
```

Hinweis zu Submodulen/externen Abhängigkeiten:
- Git-Submodule in diesem Repository sind `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` und `furigana`.
- Operative Hinweise behandeln `furigana` und `echomind` als externe/read-only-Abhängigkeit im Repo-Workflow. Wenn unklar, upstream behalten und nicht vor Ort editieren.

## ✅ Voraussetzungen

| Abhängigkeit | Hinweise |
| --- | --- |
| Linux-Umgebung | `systemd`/`tmux`-Skripte sind Linux-orientiert |
| Python 3.10+ | Nutze die Conda-Umgebung `lazyedit` |
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

3. Optionale systemweite Installation (Service-Modus):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Hinweise zur Service-Installation:
- `install_lazyedit.sh` installiert `ffmpeg` und `tmux`, anschließend wird `lazyedit.service` erstellt.
- `lazyedit_config.sh`, `start_lazyedit.sh` und `stop_lazyedit.sh` werden nicht erzeugt; sie müssen bereits existieren und korrekt sein.

## ⚡ Schnellstart

Lokaler Backend + Frontend Start (minimaler Pfad):

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

In einem zweiten Shell-Fenster:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Optionales lokales Datenbank-Bootstrapping:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime-Profile

| Profil | Startbefehl | Standard-Backend | Standard-Frontend |
| --- | --- | --- | --- |
| Lokale Entwicklung (manuell) | `python app.py` + Expo-Befehl | `8787` | `8091` (Beispielbefehl) |
| Tmux-orchestriert | `./start_lazyedit.sh` | `18787` | `18791` |
| Systemd-Service | `sudo systemctl start lazyedit.service` | Konfigurations-/env-gesteuert | N/A |

## 🧭 Command Cheat Sheet

| Aufgabe | Befehl |
| --- | --- |
| Submodule initialisieren | `git submodule update --init --recursive` |
| Nur Backend starten | `python app.py` |
| Backend + Expo (tmux) starten | `./start_lazyedit.sh` |
| Tmux-Start stoppen | `./stop_lazyedit.sh` |
| Tmux-Session öffnen | `tmux attach -t lazyedit` |
| Service-Status | `sudo systemctl status lazyedit.service` |
| Service-Logs | `sudo journalctl -u lazyedit.service` |
| DB-Smoke-Test | `python db_smoke_test.py` |
| Pytest-Smoke-Test | `pytest tests/test_db_smoke.py` |

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

Standard-Backend-URL: `http://localhost:8787` (aus `config.py`, überschreibbar mit `PORT` oder `LAZYEDIT_PORT`).

### Entwicklung: Backend + Expo-App (tmux)

```bash
./start_lazyedit.sh
```

Standard-Ports in `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Zu der Session verbinden:

```bash
tmux attach -t lazyedit
```

Session stoppen:

```bash
./stop_lazyedit.sh
```

### Service-Management

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

Hinweis zur Konfigurationsreihenfolge:

- `config.py` lädt `.env`-Werte, wenn vorhanden, und setzt nur Schlüssel, die nicht bereits im Shell-Environment exportiert sind.
- Laufzeitwerte kommen damit aus: Shell-Exports -> `.env` -> Code-Defaults.
- Für tmux-/Service-Starts steuert `lazyedit_config.sh` die Start-/Session-Parameter (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, Ports über das Startskript-Environment).

### Schlüsselvariablen

| Variable | Zweck | Standard/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Backend-Port | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Medien-Root-Verzeichnis | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Lokaler DB-Fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish-Endpunkt | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | AutoPublish-Anforderungs-Timeout (Sekunden) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Whisper/VAD-Skriptpfad | Umgebungsspezifisch |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | ASR-Modellnamen | `large-v3` / `large-v2` (Beispiel) |
| `LAZYEDIT_CAPTION_PYTHON` | Python-Laufzeit für Caption-Pipeline | Umgebungsspezifisch |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Primärer Captioning-Pfad/-Skript | Umgebungsspezifisch |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Fallback-Captioning-Pfad/-Skript/-cwd | Umgebungsspezifisch |
| `GRSAI_API_*` | Veo/GRSAI-Integrations-Einstellungen | Umgebungsspezifisch |
| `VENICE_*`, `A2E_*` | Venice/A2E-Integrations-Einstellungen | Umgebungsspezifisch |
| `OPENAI_API_KEY` | Für OpenAI-gestützte Features erforderlich | None |

Hinweise zu maschinenspezifischen Einstellungen:
- `app.py` kann CUDA-Verhalten steuern (`CUDA_VISIBLE_DEVICES` Nutzung im Codekontext).
- Einige Standardpfade sind workstation-spezifisch; für portable Setups `.env`-Überschreibungen verwenden.
- `lazyedit_config.sh` steuert tmux/Session-Startvariablen für Deployment-Skripte.

## 🧾 Konfigurationsdateien

| Datei | Zweck |
| --- | --- |
| `.env.example` | Vorlage für Umgebungsvariablen, die von Backend/Services genutzt werden |
| `.env` | Maschinenlokale Überschreibungen; geladen von `config.py`/`app.py` wenn vorhanden |
| `config.py` | Backend-Defaults und Umgebungsauflösung |
| `lazyedit_config.sh` | tmux-/Service-Laufzeitprofil (Deploy-Pfad, Conda-Env, App-Args, Session-Name) |
| `start_lazyedit.sh` | Startet Backend + Expo in tmux mit ausgewählten Ports |
| `install_lazyedit.sh` | Erstellt `lazyedit.service` und prüft vorhandene Skripte/Config |

Empfohlene Reihenfolge für portablen Betrieb:
1. Kopiere `.env.example` nach `.env`.
2. Setze in `.env` pfad- und API-bezogene `LAZYEDIT_*`-Werte.
3. Passe `lazyedit_config.sh` nur für Verhalten von tmux/service Deployment-Starts an.

## 🔌 API-Beispiele

Basis-URL-Beispiele gehen von `http://localhost:8787` aus.

| API-Gruppe | Repräsentative Endpunkte |
| --- | --- |
| Upload und Medien | `/upload`, `/upload-stream`, `/media/*` |
| Videodatensätze | `/api/videos`, `/api/videos/{id}` |
| Verarbeitung | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Veröffentlichung | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generierung | `/api/videos/generate` (+ Provider-Routen in `app.py`) |

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

End-to-End-Prozess:

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

Verwendete Endpunktgruppen:
- Video-Lebenszyklus: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Verarbeitungsaktionen: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Generierung/Provider-Pfade: `/api/videos/generate` plus Venice/A2E-Routen, die in `app.py` exponiert sind
- Distribution: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Beispiele

### Frontend lokal ausführen (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Wenn das Backend auf `8887` läuft:

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

Unterstützte Sekunden: `4`, `8`, `12`.
Unterstützte Größen: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Entwicklungsnotizen

- Nutze `python` aus der Conda-Umgebung `lazyedit` (nicht von System-`python3` ausgehen).
- Halte große Mediendateien außerhalb von Git; speichere Laufzeitmedien in `DATA/` oder externem Storage.
- Initialisiere/aktualisiere Submodule, sobald Pipeline-Komponenten nicht auflösbar sind.
- Halte Änderungen fokussiert; vermeide unzusammenhängende große Formatierungsänderungen.
- Für Frontend-Arbeit wird die Backend-API-URL von `EXPO_PUBLIC_API_URL` gesteuert.
- CORS ist im Backend für die App-Entwicklung offen.

Richtlinie zu Submodulen und externen Abhängigkeiten:
- Behandle externe Abhängigkeiten als upstream-owned. In diesem Repo-Workflow sollten intern keine Submodule bearbeitet werden, außer wenn du bewusst in diesen Projekten arbeitest.
- Operative Hinweise behandeln `furigana` (und manchmal `echomind` in lokalen Setups) als externe Abhängigkeitspfade; im Zweifel upstream unverändert lassen und keine In-Place-Edits vornehmen.

Nützliche Referenzen:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Sicherheits-/Config-Hygiene:
- Halte API-Keys und Secrets in Umgebungsvariablen; committe keine Credentials.
- Bevorzuge `.env` für maschinenspezifische Überschreibungen und halte `.env.example` als öffentliche Vorlage.
- Wenn sich CUDA/GPU-Verhalten je Host unterscheidet, überschreibe über die Umgebung statt harte Werte im Code zu setzen.

## ✅ Tests

Aktuelle formale Testfläche ist minimal und DB-orientiert.

| Validierungsebene | Befehl oder Methode |
| --- | --- |
| DB-Smoke-Test | `python db_smoke_test.py` |
| Pytest-DB-Prüfung | `pytest tests/test_db_smoke.py` |
| Funktionale Flows | Web-UI + API mit kurzem Clip in `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Für funktionale Validierung nutze Web-UI und API-Fluss mit einer kurzen Beispieldatei in `DATA/`.

Annahmen und Portabilitätsnotizen:
- Einige Standardpfade im Code sind workstation-spezifisch; das ist im aktuellen Zustand erwartet.
- Wenn ein Standardpfad auf deiner Maschine nicht existiert, setze die entsprechende `LAZYEDIT_*`-Variable in `.env`.
- Bei Unsicherheit über maschinenspezifische Werte lieber Defaults erhalten und explizite Overrides ergänzen, statt Defaults zu löschen.

## 🧱 Annahmen & bekannte Grenzen

- Das Backend-Dependency-Set ist nicht per Root-Lockfile gepinnt; Reproduzierbarkeit hängt derzeit von der lokalen Setup-Disziplin ab.
- `app.py` ist im aktuellen Repo-Zustand absichtlich monolithisch und enthält eine große Routenfläche.
- Die meiste Pipeline-Validierung ist Integration/manuell (UI + API + Beispiel-Medien), mit begrenzter formaler Automatisierung.
- Laufzeitverzeichnisse (`DATA/`, `temp/`, `translation_logs/`) sind operationelle Ausgaben und können stark wachsen.
- Submodule sind für vollständige Funktionalität erforderlich; Teil-Checkouts führen oft zu fehlenden Script-Fehlern.

## 🚢 Deployment & Sync-Notizen

Aktuelle bekannte Pfade und Sync-Fluss (laut Repositoriums-Betriebsdokumentation):

- Entwicklungs-Workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit Backend + App: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing-System-Host: `/home/lachlan/Projects/auto-publish` auf `lazyingart`

| Umgebung | Pfad | Hinweise |
| --- | --- | --- |
| Dev-Workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Hauptquelle + Submodule |
| Deploytes LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` in Ops-Dokumenten |
| Deploytes AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Monitor/Sync/Process-Sessions |
| Publishing-Host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull nach Submodul-Updates |

Nach Push von `AutoPublish/`-Änderungen aus diesem Repo auf den Publishing-Host ziehen:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Fehlerbehebung

| Problem | Prüfung / Lösung |
| --- | --- |
| Fehlende Pipeline-Module oder Skripte | `git submodule update --init --recursive` |
| FFmpeg nicht gefunden | FFmpeg installieren und prüfen, dass `ffmpeg -version` funktioniert |
| Port-Konflikte | Backend standardmäßig `8787`; `start_lazyedit.sh` standardmäßig `18787`; setze `LAZYEDIT_PORT` oder `PORT` explizit |
| Expo erreicht Backend nicht | Sicherstellen, dass `EXPO_PUBLIC_API_URL` auf aktiven Backend-Host/Port zeigt |
| Datenbankverbindungsprobleme | PostgreSQL + DSN/Env-Variablen prüfen; optionaler Smoke-Check: `python db_smoke_test.py` |
| GPU/CUDA-Probleme | Treiber-/CUDA-Kompatibilität mit installiertem Torch-Stack prüfen |
| Service-Skript bei Installation fehlerhaft | Sicherstellen, dass `lazyedit_config.sh`, `start_lazyedit.sh` und `stop_lazyedit.sh` vor dem Installer existieren |

## 🗺️ Roadmap

- In-App-Untertitel-/Segmentbearbeitung mit A/B-Vorschau und Kontrollen pro Zeile.
- Stärkere End-to-End-Testabdeckung für Kern-API-Flows.
- Dokumentationsangleichung über i18n-README-Varianten und Deployments.
- Zusätzliche Workflow-Härtung für Generierungsprovider-Retries und Statussichtbarkeit.

## 🤝 Beiträge

Beiträge sind willkommen.

1. Forken und einen Feature-Branch erstellen.
2. Commits fokussiert und gezielt halten.
3. Änderungen lokal prüfen (`python app.py`, zentraler API-Flow, App-Integration falls relevant).
4. PR mit Zweck, Reproduktionsschritten und Vorher-/Nachher-Notizen eröffnen (bei UI-Änderungen Screenshots).

Praktische Richtlinien:
- Befolge den Python-Stil (PEP 8, 4 Leerzeichen, snake_case).
- Vermeide das Commiten von Credentials oder großen Binärdateien.
- Aktualisiere Doku-/Config-Skripte, wenn sich Verhalten ändert.
- Bevorzugter Commit-Stil: kurz, prägnant, scoped (z. B. `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 Lizenz

[Apache-2.0](LICENSE)

## 🙏 Danksagung

LazyEdit baut auf Open-Source-Bibliotheken und Diensten auf, darunter:
- FFmpeg für Medienverarbeitung
- Tornado für Backend-APIs
- MoviePy für Bearbeitungs-Workflows
- OpenAI-Modelle für KI-unterstützte Pipeline-Aufgaben
- CJKWrap und mehrsprachige Text-Tools in Untertitel-Workflows
