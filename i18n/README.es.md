[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>Flujo de trabajo de vídeo asistido por IA</b> para generación, procesamiento de subtítulos, metadatos y publicación opcional.
  <br />
  <sub>Subir o generar -> transcribir -> traducir/ pulir -> incrustar subtítulos -> keyframes/captions -> metadata -> publicar</sub>
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

## 📌 Hechos rapidos

LazyEdit es un flujo de trabajo integral asistido por IA para creacion, procesamiento y publicacion opcional. Combina generacion basada en prompts (Stage A/B/C), APIs de procesamiento de medios, renderizado de subtitulos, composicion de keyframes/captions y generacion de metadatos, y entrega a AutoPublish.

| Dato rapido | Valor |
| --- | --- |
| 📘 README canónico | `README.md` (este archivo) |
| 🌐 Variantes de idioma | `i18n/README.*.md` (se mantiene una sola barra de idiomas en la parte superior) |
| 🧠 Punto de entrada del backend | `app.py` (Tornado) |
| 🖥️ Aplicacion frontend | `app/` (Expo web/movil) |

## 🧭 Contenido

- Resumen
- Hechos rapidos
- De un vistazo
- Vista general de arquitectura
- Demos
- Caracteristicas
- Documentacion e i18n
- Estructura del proyecto
- Requisitos previos
- Instalacion
- Inicio rapido
- Guía rapida de comandos
- Uso
- Configuracion
- Archivos de configuracion
- Ejemplos de API
- Ejemplos
- Notas de desarrollo
- Pruebas
- Supuestos y limites conocidos
- Notas de despliegue y sincronizacion
- Solucion de problemas
- Hoja de ruta
- Contribuir
- Support
- Licencia
- Agradecimientos

## ✨ Resumen

LazyEdit esta construido alrededor de un backend Tornado (`app.py`) y un frontend Expo (`app/`).

> Nota: Si los detalles del repositorio o del entorno de ejecucion difieren segun la maquina, conserva los valores por defecto actuales y sobrescribe mediante variables de entorno en lugar de eliminar los fallback especificos de la maquina.

| Por que los equipos lo usan | Resultado practico |
| --- | --- |
| Flujo unificado para el operador | Subir/generar/editar y publicar desde un mismo flujo |
| Diseno API-first | Facilita el scripting e integracion con otras herramientas |
| Ejecucion local-first | Funciona con tmux + despliegues basados en servicios |

| Paso | Que ocurre |
| --- | --- |
| 1 | Subir o generar video |
| 2 | Transcribir y traducir subtitulos de forma opcional |
| 3 | Incrustar subtitulos multilingues con controles de diseño |
| 4 | Generar keyframes, captions y metadatos |
| 5 | Empaquetar y publicar opcionalmente via AutoPublish |

### Enfoque del pipeline

- Subida, generacion, remix y gestion de biblioteca desde una sola UI de operador.
- Flujo de procesamiento API-first para transcripcion, pulido/traduccion de subtitulos, quemado y metadata.
- Integraciones opcionales con proveedores de generacion (ayudantes Veo / Venice / A2E / Sora en `agi/`).
- Entrega opcional a publicacion por `AutoPublish`.

## 🎯 De un vistazo

| Area | Incluido en LazyEdit | Estado |
| --- | --- | --- |
| Aplicacion principal | Backend de API Tornado + frontend Expo web/movil | ✅ |
| Pipeline multimedia | ASR, traduccion/pulido de subtitulos, quemado, keyframes, captions, metadata | ✅ |
| Generacion | Stage A/B/C y rutas auxiliares de proveedor (`agi/`) | ✅ |
| Distribucion | Entrega opcional a AutoPublish | 🟡 Opcional |
| Modelo de ejecucion | Scripts local-first, flujos tmux, servicio systemd opcional | ✅ |

## 🏗️ Resumen de arquitectura

El repositorio esta organizado como un pipeline multimedia con enfoque API-first y una capa de UI:

- `app.py` es el punto de entrada de Tornado y el orquestador de rutas para subida, procesamiento, generacion, entrega a publicacion y servicio de medios.
- `lazyedit/` contiene bloques modulares del pipeline (persistencia de DB, traduccion, quemado de subtitulos, captions, metadata, adaptadores de proveedores).
- `app/` es una aplicacion Expo Router (web/movil) que maneja subida, procesamiento, vista previa y flujos de publicacion.
- `config.py` centraliza la carga de entorno y los caminos/rutas de fallback.
- `start_lazyedit.sh` y `lazyedit_config.sh` ofrecen modos de ejecucion local/despliegue reproducibles con tmux.

| Capa | Rutas principales | Responsabilidad |
| --- | --- | --- |
| API y orquestacion | `app.py`, `config.py` | Endpoints, enrutado, resolucion de entorno |
| Core de procesamiento | `lazyedit/`, `agi/` | Pipeline de subtitulos/captions/metadata + proveedores |
| UI | `app/` | Experiencia de operador (web/movil via Expo) |
| Scripts runtime | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Inicio local/servicio y operacion |

Flujo de alto nivel:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

A continuacion se muestran capturas del flujo principal de operador, desde ingesta hasta generacion de metadata.

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

## 🧩 Caracteristicas

- ✨ Flujo de generacion por prompts (Stage A/B/C) con rutas de integracion Sora y Veo.
- 🧵 Pipeline completo de procesamiento: transcripcion -> pulido/traduccion de subtitulos -> quemado -> keyframes -> captions -> metadata.
- 🌏 Composicion multilingue de subtitulos con rutas de soporte vinculadas a furigana/IPA/romaji.
- 🔌 Backend API-first con endpoints de subida, procesamiento, servicio de medios y colas de publicacion.
- 🚚 Integracion opcional con AutoPublish para traspaso a plataformas sociales.
- 🖥️ Workflow backend + Expo soportado mediante scripts de arranque con tmux.

## 🌍 Documentacion e i18n

- Fuente canónica: `README.md`
- Variantes de idioma: `i18n/README.*.md`
- Barra de idiomas: mantener una sola linea de opciones de idioma al comienzo de cada README (sin barras duplicadas)
- Idiomas actuales en este repositorio: Arabe, Aleman, English, Espanol, Frances, Japon, Coreano, Ruso, Vietnamita, Chino simplificado, Chino tradicional

Si alguna vez hay desajuste entre estas traducciones y la documentacion en ingles, trata `README.md` como fuente de verdad y actualiza los idiomas uno por uno.

| Politica i18n | Regla |
| --- | --- |
| Fuente canónica | Mantener `README.md` como verdad principal |
| Barra de idiomas | Exactamente una sola linea de opciones de idioma |

## 🗂️ Estructura del proyecto

```text
LazyEdit/
├── app.py                           # Punto de entrada de backend Tornado y orquestacion de API
├── app/                             # Frontend Expo (web/movil)
├── lazyedit/                        # Modulos principales del pipeline (traduccion, metadata, burner, DB, templates)
├── agi/                             # Abstraccion de proveedores de generacion (rutas Sora/Veo/A2E/Venice)
├── DATA/                            # Entradas/salidas multimedia en tiempo de ejecucion (symlink en este workspace)
├── translation_logs/                # Logs de traduccion
├── temp/                            # Archivos temporales runtime
├── install_lazyedit.sh              # Instalador de systemd (espera scripts de config/start/stop)
├── start_lazyedit.sh                # Lanzador tmux para backend + Expo
├── stop_lazyedit.sh                 # Helper para detener tmux
├── lazyedit_config.sh               # Configuracion shell de despliegue/runtime
├── config.py                        # Resolucion de entorno/configuracion (puertos, rutas, URL de autopublish)
├── .env.example                     # Plantilla para sobreescritura de entorno
├── references/                      # Docs adicionales (guia API, quickstart, notas de despliegue)
├── AutoPublish/                     # Submodulo (pipeline de publicacion opcional)
├── AutoPubMonitor/                  # Submodulo (automatizacion de monitor/sync)
├── whisper_with_lang_detect/        # Submodulo (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodulo (captioner principal)
├── clip-gpt-captioning/             # Submodulo (captioner alternativo)
└── furigana/                        # Dependencia externa en el flujo (submodulo rastreado en este checkout)
```

Nota sobre submodulos y dependencias externas:
- Los submodulos Git en este repositorio incluyen `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` y `furigana`.
- La guia operativa trata `furigana` y `echomind` como dependencias externas/solo-lectura en este flujo. Si hay duda, conserva upstream y evita editar in situ.

## ✅ Requisitos previos

| Dependencia | Notas |
| --- | --- |
| Entorno Linux | Scripts de `systemd`/`tmux` estan orientados a Linux |
| Python 3.10+ | Usa el entorno Conda `lazyedit` |
| Node.js 20+ + npm | Requerido para la app Expo en `app/` |
| FFmpeg | Debe estar disponible en `PATH` |
| PostgreSQL | Autenticacion peer local o conexion por DSN |
| Submodulos Git | Necesarios para pipelines clave |

## 🚀 Instalacion

1. Clonar e inicializar submodulos:

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

3. Instalacion opcional a nivel sistema (modo servicio):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Notas de instalacion de servicio:
- `install_lazyedit.sh` instala `ffmpeg` y `tmux`, y luego crea `lazyedit.service`.
- No genera `lazyedit_config.sh`, `start_lazyedit.sh` ni `stop_lazyedit.sh`; deben existir y ser correctos.

## ⚡ Inicio rapido

Ejecucion local backend + frontend (ruta minima):

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

En una segunda shell:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Bootstrap local opcional de base de datos:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Perfiles de ejecucion

| Perfil | Comando de inicio | Backend predeterminado | Frontend predeterminado |
| --- | --- | --- | --- |
| Desarrollo local (manual) | `python app.py` + comando Expo | `8787` | `8091` (comando de ejemplo) |
| Orquestado por tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| Servicio systemd | `sudo systemctl start lazyedit.service` | Configurable por config/env | N/A |

## 🛠️ Guía rapida de comandos

| Tarea | Comando |
| --- | --- |
| Inicializar submodulos | `git submodule update --init --recursive` |
| Iniciar solo backend | `python app.py` |
| Iniciar backend + Expo (tmux) | `./start_lazyedit.sh` |
| Detener ejecucion tmux | `./stop_lazyedit.sh` |
| Abrir sesion tmux | `tmux attach -t lazyedit` |
| Estado del servicio | `sudo systemctl status lazyedit.service` |
| Logs del servicio | `sudo journalctl -u lazyedit.service` |
| Smoke test DB | `python db_smoke_test.py` |
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

Adjuntarse a la sesion:

```bash
tmux attach -t lazyedit
```

Detener sesion:

```bash
./stop_lazyedit.sh
```

### Gestion de servicio

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Configuracion

Copia `.env.example` a `.env` y actualiza rutas/secrets:

```bash
cp .env.example .env
```

Nota sobre precedencia de configuración:

- `config.py` carga los valores de `.env` si existen y solo define claves que no esten ya exportadas en la shell.
- Por eso, los valores runtime pueden provenir de: vars de entorno exportadas -> `.env` -> defaults del codigo.
- Para ejecuciones tmux/servicio, `lazyedit_config.sh` controla variables de inicio/sesion (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, puertos via script de inicio).

### Variables clave

| Variable | Proposito | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Puerto del backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Directorio raiz de medios | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN de PostgreSQL | Fallback local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint de AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout de solicitud AutoPublish (segundos) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Ruta de script Whisper/VAD | Dependiente del entorno |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Nombres de modelos ASR | `large-v3` / `large-v2` (ejemplo) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime Python para pipeline de captions | Dependiente del entorno |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Ruta/script de captions principal | Dependiente del entorno |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Ruta/script/cwd de captions fallback | Dependiente del entorno |
| `GRSAI_API_*` | Configuracion de integracion Veo/GRSAI | Dependiente del entorno |
| `VENICE_*`, `A2E_*` | Configuracion de integracion Venice/A2E | Dependiente del entorno |
| `OPENAI_API_KEY` | Requerida para funcionalidades de OpenAI | Ninguna |

Notas especificas de maquina:
- `app.py` puede definir comportamiento CUDA (`CUDA_VISIBLE_DEVICES` en el codigo).
- Algunas rutas en defaults son especificas de un workstation; usa `.env` para sobrescrituras portables.
- `lazyedit_config.sh` controla variables de inicio/sesion de tmux para despliegue.

## 🧾 Archivos de configuracion

| Archivo | Proposito |
| --- | --- |
| `.env.example` | Plantilla de variables de entorno usada por backend/servicios |
| `.env` | Sobrescrituras locales por maquina; cargado por `config.py`/`app.py` si existe |
| `config.py` | Defaults del backend y resolucion de entorno |
| `lazyedit_config.sh` | Perfil runtime para tmux/servicio (ruta de despliegue, conda env, app args, nombre de sesion) |
| `start_lazyedit.sh` | Lanza backend + Expo en tmux con puertos seleccionados |
| `install_lazyedit.sh` | Crea `lazyedit.service` y valida scripts/config existentes |

Orden recomendado para portabilidad de maquina:
1. Copia `.env.example` a `.env`.
2. Configura valores `LAZYEDIT_*` de rutas y APIs en `.env`.
3. Ajusta `lazyedit_config.sh` solo para comportamiento de arranque tmux/servicio.

## 🔌 Ejemplos de API

Los ejemplos de URL base asumen `http://localhost:8787`.

| Grupo API | Endpoints representativos |
| --- | --- |
| Subida y medios | `/upload`, `/upload-stream`, `/media/*` |
| Registros de video | `/api/videos`, `/api/videos/{id}` |
| Procesamiento | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publicacion | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generacion | `/api/videos/generate` (+ rutas de proveedor en `app.py`) |

Subida:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Proceso end-to-end:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Listar videos:

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

Para mas endpoints y detalle de payloads: `references/API_GUIDE.md`.

Grupos de endpoints relacionados que probablemente uses:
- Ciclo de vida de video: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Acciones de procesamiento: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Rutas de generacion/proveedor: `/api/videos/generate` + rutas Venice/A2E expuestas en `app.py`
- Distribucion: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Ejemplos

### Ejecucion local de frontend (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Si el backend esta en `8887`:

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

### Helper opcional de generacion Sora

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Segundos compatibles: `4`, `8`, `12`.
Tamaños compatibles: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Notas de desarrollo

- Usa `python` del entorno Conda `lazyedit` (no asumas `python3` del sistema).
- Mantén los medios grandes fuera de Git; guarda runtime media en `DATA/` o almacenamiento externo.
- Inicializa/actualiza submodulos cuando componentes del pipeline fallen.
- Mantén cambios acotados; evita reformateos no relacionados de gran alcance.
- Para frontend, la URL del backend la controla `EXPO_PUBLIC_API_URL`.
- CORS esta abierto en backend para desarrollo de app.

Politica para submodulos y dependencias externas:
- Trata dependencias externas como mantenidas por upstream. En este flujo de repositorio, evita editar internals de submodulos a menos que trabajes intencionalmente en esos proyectos.
- La guia operativa trata `furigana` (y ocasionalmente `echomind` en setups locales) como rutas externas; si hay dudas, conserva upstream y evita ediciones in situ.

Referencias utiles:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Higiene de seguridad/configuracion:
- Mantén claves API y secretos en variables de entorno; no hagas commit de credenciales.
- Prefiere `.env` para sobrescrituras locales y deja `.env.example` como plantilla publica.
- Si el comportamiento CUDA/GPU difiere por host, sobrescribe via entorno en lugar de fijar valores de maquina en codigo.

## ✅ Pruebas

La superficie formal de pruebas actual es minima y orientada a DB.

| Capa de validacion | Comando o metodo |
| --- | --- |
| Smoke DB | `python db_smoke_test.py` |
| Chequeo DB con Pytest | `pytest tests/test_db_smoke.py` |
| Flujo funcional | UI web + ejecucion API con clip corto en `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Para validacion funcional, usa la UI web y el flujo API con un clip de muestra breve en `DATA/`.

Supuestos y notas de portabilidad:
- Algunas rutas por defecto en el codigo son fallbacks especificos de workstation; esto es esperado.
- Si un path por defecto no existe en tu maquina, ajusta la variable `LAZYEDIT_*` correspondiente en `.env`.
- Si no estas seguro de un valor especifico de maquina, conserva la configuracion existente y agrega sobrescrituras explicitas antes que eliminar defaults.

## 🧱 Supuestos y limites conocidos

- El set de dependencias del backend no esta bloqueado por un lockfile raiz; la reproducibilidad depende actualmente de la disciplina local de entorno.
- `app.py` es intencionalmente monolitico en el estado actual del repositorio y concentra una gran superficie de rutas.
- La mayoria de validacion de pipeline es integracion/manual (UI + API + media de muestra), con pocas pruebas automatizadas formales.
- Directorios runtime (`DATA/`, `temp/`, `translation_logs/`) son salidas operativas y pueden crecer mucho.
- Los submodulos son necesarios para funcionalidad completa; un checkout parcial suele generar errores por scripts faltantes.

## 🚢 Notas de despliegue y sincronizacion

Rutas y flujo de sincronizacion actuales (segun docs operativos):

- Workspace de desarrollo: `/home/lachlan/ProjectsLFS/LazyEdit`
- Backend + app LazyEdit desplegados: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor desplegado: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Host del sistema de publicacion: `/home/lachlan/Projects/auto-publish` en `lazyingart`

| Entorno | Ruta | Notas |
| --- | --- | --- |
| Workspace dev | `/home/lachlan/ProjectsLFS/LazyEdit` | Codigo fuente principal + submodulos |
| LazyEdit desplegado | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` en docs de ops |
| AutoPubMonitor desplegado | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Sesiones monitor/sync/process |
| Host de publicacion | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Hacer pull tras cambios de submodulo |

Tras hacer push de cambios en `AutoPublish/` desde este repo, haz pull en el host de publicacion:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Solucion de problemas

| Problema | Verificacion / correccion |
| --- | --- |
| Faltan modulos o scripts del pipeline | Ejecuta `git submodule update --init --recursive` |
| FFmpeg no encontrado | Instala FFmpeg y verifica que `ffmpeg -version` funcione |
| Conflicto de puertos | Backend por defecto `8787`; `start_lazyedit.sh` por defecto `18787`; setea `LAZYEDIT_PORT` o `PORT` explicitamente |
| Expo no conecta con backend | Asegurate de que `EXPO_PUBLIC_API_URL` apunte al host/puerto activo del backend |
| Problemas de conexion a DB | Verifica PostgreSQL + DSN/vars de entorno; opcional smoke check: `python db_smoke_test.py` |
| Problemas GPU/CUDA | Confirma compatibilidad de driver/CUDA con el stack de Torch instalado |
| Fallo del script de servicio al instalar | Asegura que `lazyedit_config.sh`, `start_lazyedit.sh` y `stop_lazyedit.sh` existan antes de ejecutar el instalador |

## 🗺️ Hoja de ruta

- Edicion de subtitulos/segmentos dentro de app con preview A/B y controles por linea.
- Cobertura de pruebas end-to-end mas robusta para flujos principales de API.
- Convergencia documental entre variantes i18n del README y modos de despliegue.
- Endurecimiento adicional del pipeline para reintentos de proveedores de generacion y visibilidad de estado.

## 🤝 Contribuir

Las contribuciones son bienvenidas.

1. Crea fork y rama de funcionalidad.
2. Mantén commits enfocados y acotados.
3. Valida cambios localmente (`python app.py`, flujo API clave, e integracion de app si aplica).
4. Abre un PR con objetivo, pasos de reproduccion y notas antes/despues (capturas para cambios de UI).

Guia practica:
- Sigue el estilo Python (PEP 8, 4 espacios, snake_case).
- Evita commitear credenciales o binarios grandes.
- Actualiza docs/scripts de config cuando cambie el comportamiento.
- Estilo de commit preferido: corto, imperativo y acotado (por ejemplo: `fix ffmpeg 7 compatibility`).



## 📄 Licencia

[Apache-2.0](LICENSE)

## 🙏 Agradecimientos

LazyEdit se basa en librerias y servicios open-source, incluyendo:
- FFmpeg para procesamiento multimedia
- Tornado para APIs backend
- MoviePy para flujos de edicion
- Modelos de OpenAI para tareas de pipeline asistidas por IA
- CJKWrap y herramientas de texto multilenguaje en flujos de subtitulos


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
