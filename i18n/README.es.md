[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>Flujo de trabajo de vídeo asistido por IA</b> para generación, procesamiento de subtítulos, metadatos y publicación opcional.
  <br />
  <sub>Subir o generar -> transcribir -> traducir/pulir -> incrustar subtítulos -> keyframes/captions -> metadatos -> publicar</sub>
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

## 📌 Hechos rápidos

LazyEdit es un flujo de trabajo integral asistido por IA para creación, procesamiento y publicación opcional. Combina generación basada en prompts (Stage A/B/C), APIs de procesamiento de medios, renderizado de subtítulos, subtítulos por tramos clave, generación de metadatos e integración opcional con AutoPublish.

| Hecho clave | Valor |
| --- | --- |
| 📘 README canónico | `README.md` (este archivo) |
| 🌐 Variantes de idioma | `i18n/README.*.md` (se mantiene una sola barra de idiomas en la parte superior) |
| 🧠 Punto de entrada del backend | `app.py` (Tornado) |
| 🖥️ Aplicación frontend | `app/` (Expo web/móvil) |
| 🧩 Modos de ejecución | `python app.py` (manual), `./start_lazyedit.sh` (tmux), `lazyedit.service` opcional |
| 🎯 Fuentes de referencia | `README.md`, `references/QUICKSTART.md`, `references/API_GUIDE.md`, `references/APP_GUIDE.md` |

## 🧭 Contenido

- [Descripción general](#descripción-general)
- [Hechos rápidos](#-hechos-rápidos)
- [Resumen](#-resumen)
- [Instantánea de arquitectura](#-instantánea-de-arquitectura)
- [Demostraciones](#-demos)
- [Características](#-características)
- [Documentación e internacionalización](#-documentación-e-internacionalización)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Inicio rápido](#-inicio-rápido)
- [Guía rápida de comandos](#-guía-rápida-de-comandos)
- [Uso](#-uso)
- [Configuración](#-configuración)
- [Archivos de configuración](#-archivos-de-configuración)
- [Ejemplos de API](#-ejemplos-de-api)
- [Ejemplos](#-ejemplos)
- [Notas de desarrollo](#-notas-de-desarrollo)
- [Pruebas](#-pruebas)
- [Supuestos y límites conocidos](#-supuestos-y-límites-conocidos)
- [Notas de despliegue y sincronización](#-notas-de-despliegue-y-sincronización)
- [Solución de problemas](#-solución-de-problemas)
- [Hoja de ruta](#-hoja-de-ruta)
- [Contribuir](#-contribuir)
- [Soporte](#-support)
- [Licencia](#-license)
- [Agradecimientos](#-agradecimientos)

## ✨ Descripción general

LazyEdit se construye alrededor de un backend Tornado (`app.py`) y un frontend Expo (`app/`).

> Nota: Si los detalles del repo o del entorno cambian por máquina, conserva los valores por defecto existentes y sobrescríbelos mediante variables de entorno en lugar de eliminar los fallbacks específicos de la máquina.

| Por qué los equipos lo usan | Resultado práctico |
| --- | --- |
| Flujo unificado para el operador | Subir/generar/remix/publicar desde un único flujo |
| Diseño API-first | Sencillo de automatizar e integrar con otras herramientas |
| Ejecución local-first | Funciona con patrones de despliegue por tmux + servicio |

| Paso | Qué ocurre |
| --- | --- |
| 1 | Subir o generar vídeo |
| 2 | Transcribir y traducir subtítulos de forma opcional |
| 3 | Incrustar subtítulos multilingües con controles de diseño |
| 4 | Generar keyframes, captions y metadatos |
| 5 | Empaquetar y publicar opcionalmente vía AutoPublish |

### Enfoque del pipeline

- Subida, generación, remix y administración de biblioteca desde una sola UI de operador.
- Flujo de procesamiento API-first para transcripción, pulido/traducción de subtítulos, incrustado y metadatos.
- Integraciones opcionales de proveedores de generación (helpers de Veo / Venice / A2E / Sora en `agi/`).
- Entrega opcional a publicación mediante `AutoPublish`.

## 🎯 Resumen

| Área | Incluido en LazyEdit | Estado |
| --- | --- | --- |
| App principal | Backend API Tornado + frontend Expo web/móvil | ✅ |
| Pipeline multimedia | ASR, traducción/pulido de subtítulos, incrustado, keyframes, captions, metadatos | ✅ |
| Generación | Etapas A/B/C y rutas auxiliares de proveedor (`agi/`) | ✅ |
| Distribución | Entrega opcional con AutoPublish | 🟡 Opcional |
| Modelo de ejecución | Scripts local-first, flujos tmux, servicio systemd opcional | ✅ |

## 🏗️ Instantánea de arquitectura

El repositorio está organizado como un pipeline multimedia API-first con una capa UI:

- `app.py` es el punto de entrada de Tornado y el orquestador de rutas para subida, procesamiento, generación, entrega a publicación y servicio de medios.
- `lazyedit/` contiene bloques modulares del pipeline (persistencia de BD, traducción, render de subtítulos, captions, metadatos, adaptadores de proveedores).
- `app/` es una app Expo Router (web/móvil) que maneja subida, procesamiento, vista previa y flujos de publicación.
- `config.py` centraliza la carga de configuración y rutas por defecto de entorno.
- `start_lazyedit.sh` y `lazyedit_config.sh` permiten modos de ejecución reproducibles locales/desplegados con tmux.

| Capa | Rutas principales | Responsabilidad |
| --- | --- | --- |
| API y orquestación | `app.py`, `config.py` | Endpoints, enrutado, resolución de entorno |
| Núcleo de procesamiento | `lazyedit/`, `agi/` | Pipeline de subtítulos/captions/metadatos + proveedores |
| UI | `app/` | Experiencia del operador (web/móvil vía Expo) |
| Scripts de ejecución | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Inicio local/servicio y operación |

Flujo de alto nivel:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

Las imágenes de abajo muestran la ruta principal de operación desde la ingesta hasta la generación de metadatos.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Inicio · Subir</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Inicio · Generar</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Inicio · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Biblioteca</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Resumen de vídeo</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Vista previa de traducción</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Slots de incrustado</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Diseño de incrustado</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Keyframes + captions</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Generador de metadatos</sub>
    </td>
  </tr>
</table>

## 🧩 Características

- ✨ Flujo de generación basado en prompts (Stage A/B/C) con rutas de integración de Sora y Veo.
- 🧵 Pipeline completo de procesamiento: transcripción -> pulido/traducción de subtítulos -> incrustado -> keyframes -> captions -> metadatos.
- 🌏 Composición multilingüe de subtítulos con rutas de soporte para furigana/IPA/romaji.
- 🔌 Backend API-first con endpoints de subida, procesamiento, servicio de medios y cola de publicación.
- 🚚 Integración opcional con AutoPublish para el traspaso a plataformas sociales.
- 🖥️ Flujo combinado backend + Expo soportado por scripts de arranque con tmux.

## 🌍 Documentación e i18n


- Fuente canónica: `README.md`
- Variantes de idioma: `i18n/README.*.md`
- Barra de idiomas: mantener una sola línea de opciones de idioma en la parte superior de cada README (sin duplicados)
- Idiomas actuales en este repo: árabe, alemán, inglés, español, francés, japonés, coreano, ruso, vietnamita, chino simplificado, chino tradicional

Si en algún momento hay una diferencia entre las traducciones y la documentación en inglés, trata `README.md` como la fuente de verdad y actualiza cada idioma uno por uno.

| Política i18n | Regla |
| --- | --- |
| Fuente canónica | Mantener `README.md` como fuente de verdad |
| Barra de idiomas | Exactamente una línea de opciones de idioma |

## 🗂️ Estructura del proyecto

```text
LazyEdit/
├── app.py                           # Punto de entrada del backend Tornado y orquestación de API
├── app/                             # Frontend Expo (web/móvil)
├── lazyedit/                        # Módulos principales del pipeline (traducción, metadatos, burner, BD, plantillas)
├── agi/                             # Abstracción de proveedores de generación (rutas Sora/Veo/A2E/Venice)
├── DATA/                            # Entradas/salidas de medios en tiempo de ejecución (symlink en este workspace)
├── translation_logs/                # Registros de traducción
├── temp/                            # Archivos temporales de ejecución
├── install_lazyedit.sh              # Instalador de systemd (requiere scripts config/start/stop)
├── start_lazyedit.sh                # Lanzador tmux para backend + Expo
├── stop_lazyedit.sh                 # Utilidad para detener tmux
├── lazyedit_config.sh               # Configuración shell de despliegue/runtime
├── config.py                        # Resolución de entorno/config (puertos, rutas, URL de autopublicación)
├── .env.example                     # Plantilla para sobrescritura de entorno
├── references/                      # Docs adicionales (guía API, quickstart, notas de despliegue)
├── AutoPublish/                     # Submódulo (pipeline de publicación opcional)
├── AutoPubMonitor/                  # Submódulo (automatización monitor/sync)
├── whisper_with_lang_detect/        # Submódulo (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submódulo (captions principal)
├── clip-gpt-captioning/             # Submódulo (captions alternativo)
└── furigana/                        # Dependencia externa en el flujo (submódulo symlink en este checkout)
```

Nota de submódulos/dependencias externas:
- Los submódulos Git en este repositorio incluyen `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` y `furigana`.
- La guía operativa trata `furigana` y `echomind` como dependencias externas de solo lectura en este flujo. Si hay dudas, conserva upstream y evita editar in situ.

## ✅ Requisitos previos

| Dependencia | Notas |
| --- | --- |
| Entorno Linux | Los scripts de `systemd`/`tmux` están orientados a Linux |
| Python 3.10+ | Usa el entorno Conda `lazyedit` |
| Node.js 20+ + npm | Requerido para la app Expo en `app/` |
| FFmpeg | Debe estar disponible en `PATH` |
| PostgreSQL | Autenticación peer local o conexión DSN |
| Submódulos Git | Requeridos para los pipelines clave |

## 🚀 Instalación

1. Clonar e inicializar submódulos:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Activar entorno Conda:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Instalación opcional a nivel sistema (modo servicio):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Notas de instalación del servicio:
- `install_lazyedit.sh` instala `ffmpeg` y `tmux`, y luego crea `lazyedit.service`.
- No genera `lazyedit_config.sh`, `start_lazyedit.sh` ni `stop_lazyedit.sh`; deben existir y estar correctos.

## ⚡ Inicio rápido

Inicio mínimo de backend + frontend local:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

En una segunda terminal:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Bootstrap opcional de base de datos local:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Perfiles de ejecución

| Perfil | Comando de inicio | Backend predeterminado | Frontend predeterminado |
| --- | --- | --- | --- |
| Desarrollo local (manual) | `python app.py` + comando Expo | `8787` | `8091` (comando de ejemplo) |
| Orquestado con tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| Servicio systemd | `sudo systemctl start lazyedit.service` | Configurado por config/env | N/A |

## 🧭 Guía rápida de comandos

| Tarea | Comando |
| --- | --- |
| Inicializar submódulos | `git submodule update --init --recursive` |
| Iniciar solo backend | `python app.py` |
| Iniciar backend + Expo (tmux) | `./start_lazyedit.sh` |
| Detener ejecución tmux | `./stop_lazyedit.sh` |
| Abrir sesión tmux | `tmux attach -t lazyedit` |
| Estado del servicio | `sudo systemctl status lazyedit.service` |
| Logs del servicio | `sudo journalctl -u lazyedit.service` |
| Smoke test BD | `python db_smoke_test.py` |
| Smoke test con Pytest | `pytest tests/test_db_smoke.py` |

## 🛠️ Uso

### Desarrollo: solo backend

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Entrada alternativa usada en scripts de despliegue actuales:

```bash
python app.py -m lazyedit
```

URL predeterminada del backend: `http://localhost:8787` (desde `config.py`, sobrescribe con `PORT` o `LAZYEDIT_PORT`).

### Desarrollo: backend + app Expo (tmux)

```bash
./start_lazyedit.sh
```

Puertos predeterminados de `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Adjuntarse a la sesión:

```bash
tmux attach -t lazyedit
```

Detener sesión:

```bash
./stop_lazyedit.sh
```

### Gestión de servicio

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Configuración

Copia `.env.example` a `.env` y actualiza rutas/secrets:

```bash
cp .env.example .env
```

Nota de precedencia de configuración:

- `config.py` carga los valores de `.env` si existen y solo define claves que no estén ya exportadas en la shell.
- Los valores en tiempo de ejecución pueden venir de: vars exportadas en shell -> `.env` -> defaults de código.
- Para ejecuciones tmux/servicio, `lazyedit_config.sh` controla parámetros de inicio/sesión (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, puertos desde script de arranque).

### Variables clave

| Variable | Propósito | Predeterminado/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Puerto del backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Directorio raíz de medios | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN de PostgreSQL | Fallback local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint de AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Tiempo de espera de solicitud AutoPublish (segundos) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Ruta del script Whisper/VAD | Dependiente del entorno |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Nombres de modelos ASR | `large-v3` / `large-v2` (ejemplo) |
| `LAZYEDIT_CAPTION_PYTHON` | Python de ejecución para pipeline de captions | Dependiente del entorno |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Ruta/script de captions principal | Dependiente del entorno |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Ruta/script/cwd de captions fallback | Dependiente del entorno |
| `GRSAI_API_*` | Ajustes de integración Veo/GRSAI | Dependiente del entorno |
| `VENICE_*`, `A2E_*` | Ajustes de integración Venice/A2E | Dependiente del entorno |
| `OPENAI_API_KEY` | Requerida para funcionalidades basadas en OpenAI | Ninguna |

Notas específicas de máquina:
- `app.py` puede definir comportamiento CUDA (`uso de CUDA_VISIBLE_DEVICES` en el código).
- Algunas rutas por defecto son específicas de un equipo; usa `.env` para sobrescrituras portables.
- `lazyedit_config.sh` controla variables de inicio/sesión tmux para despliegues.

## 🧾 Archivos de configuración

| Archivo | Propósito |
| --- | --- |
| `.env.example` | Plantilla de variables de entorno usada por backend/servicios |
| `.env` | Sobrescrituras locales de máquina; cargadas por `config.py`/`app.py` si existen |
| `config.py` | Defaults del backend y resolución de entorno |
| `lazyedit_config.sh` | Perfil runtime de tmux/servicio (ruta de despliegue, entorno conda, app args, nombre de sesión) |
| `start_lazyedit.sh` | Lanza backend + Expo en tmux con puertos seleccionados |
| `install_lazyedit.sh` | Crea `lazyedit.service` y valida scripts/config existentes |

Orden recomendado para portabilidad entre máquinas:
1. Copia `.env.example` a `.env`.
2. Configura valores `LAZYEDIT_*` de rutas y APIs en `.env`.
3. Ajusta `lazyedit_config.sh` solo para comportamiento de arranque tmux/servicio.

## 🔌 Ejemplos de API

Las URL base de ejemplo asumen `http://localhost:8787`.

| Grupo API | Endpoints representativos |
| --- | --- |
| Subida y medios | `/upload`, `/upload-stream`, `/media/*` |
| Registros de vídeo | `/api/videos`, `/api/videos/{id}` |
| Procesamiento | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publicación | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generación | `/api/videos/generate` (+ rutas de proveedor en `app.py`) |

Subida:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Proceso extremo a extremo:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Listar vídeos:

```bash
curl http://localhost:8787/api/videos
```

Publicar paquete:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Más endpoints y detalles de payload: `references/API_GUIDE.md`.

Grupos de endpoints relacionados que probablemente uses:
- Ciclo de vida de vídeo: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Acciones de procesamiento: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Rutas de generación/proveedor: `/api/videos/generate` más rutas de Venice/A2E expuestas en `app.py`
- Distribución: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Ejemplos

### Ejecución local de frontend (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Si el backend está en `8887`:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Emulador Android

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### Simulador iOS (macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### Helper opcional de generación Sora

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Segundos compatibles: `4`, `8`, `12`.
Tamaños compatibles: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Notas de desarrollo

- Usa `python` del entorno Conda `lazyedit` (no des por sentado `python3` del sistema).
- Mantén los archivos de medios grandes fuera de Git; guarda media de runtime en `DATA/` o almacenamiento externo.
- Inicializa/actualiza submódulos cuando componentes del pipeline fallen.
- Mantén cambios acotados; evita reformateos no relacionados de gran alcance.
- Para frontend, la URL del backend la controla `EXPO_PUBLIC_API_URL`.
- CORS está abierto en el backend para desarrollo de la app.

Política para submódulos y dependencias externas:
- Trata dependencias externas como mantenidas por upstream. En el flujo de este repositorio, evita editar internos de submódulos salvo que estés trabajando explícitamente en esos proyectos.
- La guía operativa trata `furigana` (y en algunos entornos `echomind`) como dependencias externas; si hay dudas, conserva upstream y evita editar localmente.

Referencias útiles:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Seguridad y configuración:
- Mantén las claves de API y secretos en variables de entorno; no hacer commit de credenciales.
- Prefiere `.env` para sobrescrituras locales y deja `.env.example` como plantilla pública.
- Si el comportamiento de CUDA/GPU cambia por host, sobrescribe mediante entorno en vez de fijar valores de máquina en código.

## ✅ Pruebas

La cobertura formal de pruebas actual es mínima y orientada a BD.

| Capa de validación | Comando o método |
| --- | --- |
| Smoke DB | `python db_smoke_test.py` |
| Comprobación BD con Pytest | `pytest tests/test_db_smoke.py` |
| Flujo funcional | UI web + API usando una muestra corta en `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Para validación funcional, usa la UI y el flujo API con un clip corto en `DATA/`.

Supuestos y notas de portabilidad:
- Algunas rutas por defecto en el código son fallbacks específicos de una estación de trabajo; esto es esperado en el estado actual del repositorio.
- Si una ruta por defecto no existe en tu máquina, configura la variable `LAZYEDIT_*` correspondiente en `.env`.
- Si no estás seguro sobre un valor de máquina, conserva la configuración existente y añade sobrescrituras explícitas en vez de eliminar defaults.

## 🧱 Supuestos y límites conocidos

- El set de dependencias del backend no está fijado por un lockfile raíz; la reproducibilidad depende de la disciplina local del entorno.
- `app.py` es deliberadamente monolítico en este estado y contiene una gran superficie de rutas.
- La mayoría de la validación del pipeline es integración/manual (UI + API + muestra multimedia), con pocas pruebas automatizadas formales.
- Los directorios de ejecución (`DATA/`, `temp/`, `translation_logs/`) son salidas operativas y pueden crecer considerablemente.
- Los submódulos son necesarios para funcionalidad completa; un checkout parcial suele provocar errores de scripts faltantes.

## 🚢 Notas de despliegue y sincronización

Rutas y flujo de sincronización conocidos (según documentación operativa):

- Espacio de trabajo de desarrollo: `/home/lachlan/ProjectsLFS/LazyEdit`
- Backend + app LazyEdit desplegados: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor desplegado: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Sistema de publicación: `/home/lachlan/Projects/auto-publish` en `lazyingart`

| Entorno | Ruta | Notas |
| --- | --- | --- |
| Workspace de desarrollo | `/home/lachlan/ProjectsLFS/LazyEdit` | Código fuente principal + submódulos |
| LazyEdit desplegado | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` en docs de ops |
| AutoPubMonitor desplegado | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Sesiones monitor/sync/process |
| Host de publicación | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Pull después de actualizaciones de submódulos |

Después de enviar cambios de `AutoPublish/` desde este repo, hacer pull en el host de publicación:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Solución de problemas

| Problema | Verificación / corrección |
| --- | --- |
| Faltan módulos o scripts del pipeline | Ejecuta `git submodule update --init --recursive` |
| FFmpeg no encontrado | Instala FFmpeg y verifica que `ffmpeg -version` funcione |
| Conflicto de puertos | El backend usa `8787` por defecto; `start_lazyedit.sh` usa `18787`; configura `LAZYEDIT_PORT` o `PORT` explícitamente |
| Expo no alcanza al backend | Asegúrate de que `EXPO_PUBLIC_API_URL` apunte al host/puerto activo del backend |
| Problemas de conexión a BD | Verifica PostgreSQL + variables DSN/entorno; opcionalmente `python db_smoke_test.py` |
| Problemas de GPU/CUDA | Confirma compatibilidad de driver/CUDA con el stack de Torch instalado |
| Fallo del script de servicio al instalar | Asegura que `lazyedit_config.sh`, `start_lazyedit.sh` y `stop_lazyedit.sh` existan antes del instalador |

## 🗺️ Hoja de ruta

- Edición de subtítulos/segmentos dentro de la app con preview A/B y controles por línea.
- Mayor cobertura de pruebas end-to-end para flujos clave de API.
- Convergencia documental entre variantes i18n y modos de despliegue.
- Endurecimiento adicional del pipeline para reintentos de proveedores de generación y visibilidad de estado.

## 🤝 Contribuir

Las contribuciones son bienvenidas.

1. Haz fork y crea una rama de funciones.
2. Mantén commits enfocados y acotados.
3. Valida cambios localmente (`python app.py`, flujo API clave y la integración de app si aplica).
4. Abre un PR con objetivo, pasos de reproducción y notas antes/después (capturas para cambios de UI).

Pautas prácticas:
- Sigue el estilo Python (PEP 8, 4 espacios, `snake_case`).
- Evita commitear credenciales o binarios grandes.
- Actualiza documentación/scripts de config cuando cambie el comportamiento.
- Estilo de commit preferido: corto, imperativo y acotado (por ejemplo: `fix ffmpeg 7 compatibility`).



## 📄 Licencia

[Apache-2.0](LICENSE)

## 🙏 Agradecimientos

LazyEdit se basa en librerías y servicios de código abierto, incluyendo:
- FFmpeg para procesamiento multimedia
- Tornado para APIs backend
- MoviePy para flujos de edición
- Modelos de OpenAI para tareas de pipeline asistidas por IA
- CJKWrap y herramientas de texto multilingüe en flujos de subtítulos


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
