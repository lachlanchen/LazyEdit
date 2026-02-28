[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

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

<p align="center">
  <b>Flujo de video asistido por IA</b> para generación, procesamiento de subtítulos, metadatos y publicación opcional.
</p>

# LazyEdit

LazyEdit es un flujo integral de video asistido por IA para creación, procesamiento y publicación opcional. Combina generación basada en prompts (Stage A/B/C), APIs de procesamiento multimedia, renderizado de subtítulos, subtitulado de fotogramas clave, generación de metadatos y traspaso a AutoPublish.

| Dato rápido | Valor |
| --- | --- |
| README canónico | `README.md` (este archivo) |
| Variantes de idioma | `i18n/README.*.md` (se mantiene intencionalmente una sola barra de idiomas al inicio) |
| Punto de entrada del backend | `app.py` (Tornado) |
| App de frontend | `app/` (Expo web/móvil) |

## Contenido

- [Resumen](#-resumen)
- [De un vistazo](#-de-un-vistazo)
- [Vista general de arquitectura](#-vista-general-de-arquitectura)
- [Demos](#-demos)
- [Características](#-características)
- [Estructura del proyecto](#️-estructura-del-proyecto)
- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Inicio rápido](#-inicio-rápido)
- [Uso](#️-uso)
- [Configuración](#️-configuración)
- [Ejemplos de API](#-ejemplos-de-api)
- [Ejemplos](#-ejemplos)
- [Notas de desarrollo](#-notas-de-desarrollo)
- [Pruebas](#-pruebas)
- [Notas de despliegue y sincronización](#-notas-de-despliegue-y-sincronización)
- [Solución de problemas](#-solución-de-problemas)
- [Hoja de ruta](#️-hoja-de-ruta)
- [Contribuir](#-contribuir)
- [Support](#-support)
- [Licencia](#-licencia)
- [Agradecimientos](#-agradecimientos)

## ✨ Resumen

LazyEdit está construido alrededor de un backend Tornado (`app.py`) y un frontend Expo (`app/`).

> Nota: Si los detalles del repositorio/entorno de ejecución difieren según la máquina, conserva los valores predeterminados existentes y sobrescribe mediante variables de entorno en lugar de eliminar los fallbacks específicos de máquina.

| Paso | Qué sucede |
| --- | --- |
| 1 | Subir o generar video |
| 2 | Transcribir y traducir subtítulos opcionalmente |
| 3 | Incrustar subtítulos multilingües con controles de diseño |
| 4 | Generar fotogramas clave, subtítulos y metadatos |
| 5 | Empaquetar y publicar opcionalmente mediante AutoPublish |

### Enfoque del pipeline

- Subida, generación, remix y gestión de biblioteca desde una sola UI de operador.
- Flujo de procesamiento API-first para transcripción, mejora/traducción de subtítulos, incrustación y metadatos.
- Integraciones opcionales de proveedores de generación (ayudantes Veo / Venice / A2E / Sora en `agi/`).
- Traspaso opcional de publicación mediante `AutoPublish`.

## 🎯 De un vistazo

| Área | Incluido en LazyEdit |
| --- | --- |
| App principal | Backend de API Tornado + frontend Expo web/móvil |
| Pipeline multimedia | ASR, traducción/mejora de subtítulos, incrustación, fotogramas clave, subtítulos, metadatos |
| Generación | Stage A/B/C y rutas auxiliares de proveedor (`agi/`) |
| Distribución | Traspaso opcional a AutoPublish |
| Modelo de ejecución | Scripts local-first, flujos con tmux, servicio systemd opcional |

## 🏗️ Vista general de arquitectura

El repositorio está organizado como un pipeline multimedia API-first con una capa de UI:

- `app.py` es el punto de entrada Tornado y orquestador de rutas para subida, procesamiento, generación, traspaso de publicación y entrega de medios.
- `lazyedit/` contiene bloques modulares del pipeline (persistencia DB, traducción, incrustación de subtítulos, captions, metadatos, adaptadores de proveedores).
- `app/` es una app Expo Router (web/móvil) que gestiona los flujos de subida, procesamiento, vista previa y publicación.
- `config.py` centraliza la carga del entorno y las rutas de ejecución predeterminadas/fallback.
- `start_lazyedit.sh` y `lazyedit_config.sh` proporcionan modos de ejecución local/despliegue reproducibles basados en tmux.

Flujo de alto nivel:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

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
      <br /><sub>Vista general del video</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Vista previa de traducción</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Slots de incrustación</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Diseño de incrustación</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Fotogramas clave + subtítulos</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Generador de metadatos</sub>
    </td>
  </tr>
</table>

## 🧩 Características

- Flujo de generación basado en prompts (Stage A/B/C) con rutas de integración Sora y Veo.
- Pipeline completo de procesamiento: transcripción -> mejora/traducción de subtítulos -> incrustación -> fotogramas clave -> subtítulos -> metadatos.
- Composición de subtítulos multilingües con rutas de soporte relacionadas con furigana/IPA/romaji.
- Backend API-first con endpoints de subida, procesamiento, entrega de medios y cola de publicación.
- Integración opcional con AutoPublish para traspaso a plataformas sociales.
- Flujo combinado backend + Expo compatible con scripts de lanzamiento en tmux.

## 🗂️ Estructura del proyecto

```text
LazyEdit/
├── app.py                           # Punto de entrada del backend Tornado y orquestación de API
├── app/                             # Frontend Expo (web/móvil)
├── lazyedit/                        # Módulos principales del pipeline (traducción, metadatos, burner, DB, plantillas)
├── agi/                             # Abstracción de proveedores de generación (rutas Sora/Veo/A2E/Venice)
├── DATA/                            # Entrada/salida multimedia en ejecución (symlink en este workspace)
├── translation_logs/                # Registros de traducción
├── temp/                            # Archivos temporales de ejecución
├── install_lazyedit.sh              # Instalador systemd (espera scripts config/start/stop)
├── start_lazyedit.sh                # Lanzador tmux para backend + Expo
├── stop_lazyedit.sh                 # Helper para detener tmux
├── lazyedit_config.sh               # Configuración shell de despliegue/ejecución
├── config.py                        # Resolución de entorno/configuración (puertos, rutas, URL autopublish)
├── .env.example                     # Plantilla de sobrescritura de entorno
├── references/                      # Documentación adicional (guía API, inicio rápido, notas de despliegue)
├── AutoPublish/                     # Submódulo (pipeline de publicación opcional)
├── AutoPubMonitor/                  # Submódulo (automatización de monitorización/sincronización)
├── whisper_with_lang_detect/        # Submódulo (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submódulo (captioner principal)
├── clip-gpt-captioning/             # Submódulo (captioner fallback)
└── furigana/                        # Dependencia externa en el flujo (submódulo rastreado en este checkout)
```

Nota sobre submódulos/dependencias externas:
- Los submódulos Git en este repositorio incluyen `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` y `furigana`.
- La guía operativa trata `furigana` y `echomind` como externos/de solo lectura en este flujo del repositorio. Si tienes dudas, conserva upstream y evita editar in situ.

## ✅ Requisitos previos

| Dependencia | Notas |
| --- | --- |
| Entorno Linux | Los scripts `systemd`/`tmux` están orientados a Linux |
| Python 3.10+ | Usa el entorno Conda `lazyedit` |
| Node.js 20+ + npm | Necesario para la app Expo en `app/` |
| FFmpeg | Debe estar disponible en `PATH` |
| PostgreSQL | Autenticación local peer o conexión basada en DSN |
| Submódulos Git | Necesarios para pipelines clave |

## 🚀 Instalación

1. Clona e inicializa submódulos:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Activa el entorno Conda:

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
- No genera `lazyedit_config.sh`, `start_lazyedit.sh` ni `stop_lazyedit.sh`; estos deben existir previamente y ser correctos.

## ⚡ Inicio rápido

Ejecución local backend + frontend (ruta mínima):

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
| Servicio systemd | `sudo systemctl start lazyedit.service` | Guiado por config/env | N/A |

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

Nota sobre precedencia de configuración:

- `config.py` carga valores de `.env` si existen y solo define claves que aún no estén exportadas en la shell.
- Por lo tanto, los valores de ejecución pueden provenir de: variables de entorno exportadas en shell -> `.env` -> valores predeterminados del código.
- Para ejecuciones en tmux/servicio, `lazyedit_config.sh` controla los parámetros de inicio/sesión (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, puertos mediante variables del script de inicio).

### Variables clave

| Variable | Propósito | Predeterminado/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Puerto del backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Directorio raíz de medios | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN de PostgreSQL | Fallback DB local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Tiempo de espera de solicitud AutoPublish (segundos) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Ruta del script Whisper/VAD | Dependiente del entorno |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Nombres de modelo ASR | `large-v3` / `large-v2` (ejemplo) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime de Python para pipeline de subtítulos | Dependiente del entorno |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Ruta/script de subtitulado principal | Dependiente del entorno |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Ruta/script/cwd de subtitulado fallback | Dependiente del entorno |
| `GRSAI_API_*` | Configuración de integración Veo/GRSAI | Dependiente del entorno |
| `VENICE_*`, `A2E_*` | Configuración de integración Venice/A2E | Dependiente del entorno |
| `OPENAI_API_KEY` | Requerida para funciones respaldadas por OpenAI | Ninguna |

Notas específicas de máquina:
- `app.py` puede establecer comportamiento CUDA (uso de `CUDA_VISIBLE_DEVICES` en el contexto del codebase).
- Algunas rutas en los predeterminados son específicas de estación de trabajo; usa sobrescrituras en `.env` para configuraciones portables.
- `lazyedit_config.sh` controla variables de inicio de tmux/sesión para scripts de despliegue.

## 🔌 Ejemplos de API

Los ejemplos de URL base asumen `http://localhost:8787`.

| Grupo de API | Endpoints representativos |
| --- | --- |
| Subida y medios | `/upload`, `/upload-stream`, `/media/*` |
| Registros de video | `/api/videos`, `/api/videos/{id}` |
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

Proceso de extremo a extremo:

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

Más endpoints y detalles de payload: `references/API_GUIDE.md`.

Grupos de endpoints relacionados que probablemente usarás:
- Ciclo de vida del video: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Acciones de procesamiento: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Rutas de generación/proveedor: `/api/videos/generate` más rutas Venice/A2E expuestas en `app.py`
- Distribución: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Ejemplos

### Ejecución local del frontend (web)

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

### Helper opcional para generación con Sora

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Segundos compatibles: `4`, `8`, `12`.
Tamaños compatibles: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Notas de desarrollo

- Usa `python` desde el entorno Conda `lazyedit` (no asumas `python3` del sistema).
- Mantén medios grandes fuera de Git; guarda medios de ejecución en `DATA/` o almacenamiento externo.
- Inicializa/actualiza submódulos cuando los componentes del pipeline no se resuelvan.
- Mantén los cambios acotados; evita cambios de formato grandes no relacionados.
- Para trabajo de frontend, la URL del backend se controla con `EXPO_PUBLIC_API_URL`.
- CORS está abierto en el backend para desarrollo de la app.

Política sobre submódulos y dependencias externas:
- Trata las dependencias externas como mantenidas por upstream. En este flujo de repositorio, evita editar internals de submódulos salvo que estés trabajando intencionalmente en esos proyectos.
- La guía operativa de este repositorio trata `furigana` (y a veces `echomind` en entornos locales) como rutas de dependencia externa; si tienes dudas, conserva upstream y evita ediciones in situ.

Referencias útiles:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Higiene de seguridad/configuración:
- Mantén claves API y secretos en variables de entorno; no hagas commit de credenciales.
- Prefiere `.env` para sobrescrituras locales de máquina y deja `.env.example` como plantilla pública.
- Si el comportamiento CUDA/GPU difiere por host, sobrescribe por entorno en vez de fijar valores específicos de máquina en código.

## ✅ Pruebas

La superficie formal actual de pruebas es mínima y orientada a DB.

| Capa de validación | Comando o método |
| --- | --- |
| Smoke de DB | `python db_smoke_test.py` |
| Verificación DB con Pytest | `pytest tests/test_db_smoke.py` |
| Flujo funcional | UI web + ejecución API con muestra corta en `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Para validación funcional, usa la UI web y el flujo API con un clip de muestra corto en `DATA/`.

Supuestos y notas de portabilidad:
- Algunas rutas predeterminadas en código son fallbacks específicos de estación de trabajo; esto es esperable en el estado actual del repositorio.
- Si una ruta predeterminada no existe en tu máquina, define la variable `LAZYEDIT_*` correspondiente en `.env`.
- Si no tienes certeza sobre un valor específico de máquina, conserva la configuración existente y añade sobrescrituras explícitas en lugar de eliminar predeterminados.

## 🚢 Notas de despliegue y sincronización

Rutas conocidas actuales y flujo de sincronización (según docs operativas del repositorio):

- Workspace de desarrollo: `/home/lachlan/ProjectsLFS/LazyEdit`
- Backend + app LazyEdit desplegados: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor desplegado: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Host del sistema de publicación: `/home/lachlan/Projects/auto-publish` en `lazyingart`

| Entorno | Ruta | Notas |
| --- | --- | --- |
| Workspace dev | `/home/lachlan/ProjectsLFS/LazyEdit` | Código fuente principal + submódulos |
| LazyEdit desplegado | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` en docs operativas |
| AutoPubMonitor desplegado | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Sesiones monitor/sync/process |
| Host de publicación | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Hacer pull tras actualizaciones de submódulo |

Tras hacer push de actualizaciones en `AutoPublish/` desde este repositorio, haz pull en el host de publicación:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Solución de problemas

| Problema | Verificación / Solución |
| --- | --- |
| Faltan módulos o scripts del pipeline | Ejecuta `git submodule update --init --recursive` |
| FFmpeg no encontrado | Instala FFmpeg y confirma que `ffmpeg -version` funcione |
| Conflictos de puertos | El backend usa `8787`; `start_lazyedit.sh` usa `18787`; define `LAZYEDIT_PORT` o `PORT` explícitamente |
| Expo no puede alcanzar el backend | Asegura que `EXPO_PUBLIC_API_URL` apunte al host/puerto activos del backend |
| Problemas de conexión con base de datos | Verifica PostgreSQL + DSN/variables de entorno; smoke check opcional: `python db_smoke_test.py` |
| Problemas de GPU/CUDA | Confirma compatibilidad driver/CUDA con la pila Torch instalada |
| Fallo del script de servicio al instalar | Asegura que `lazyedit_config.sh`, `start_lazyedit.sh` y `stop_lazyedit.sh` existan antes de ejecutar el instalador |

## 🗺️ Hoja de ruta

- Edición en app de subtítulos/segmentos con vista previa A/B y controles por línea.
- Cobertura de pruebas end-to-end más robusta para flujos API principales.
- Convergencia documental entre variantes i18n del README y modos de despliegue.
- Endurecimiento adicional del flujo para reintentos de proveedores de generación y visibilidad de estado.

## 🤝 Contribuir

Las contribuciones son bienvenidas.

1. Haz un fork y crea una rama de funcionalidad.
2. Mantén commits enfocados y acotados.
3. Valida cambios localmente (`python app.py`, flujo API clave e integración de la app si corresponde).
4. Abre un PR con propósito, pasos de reproducción y notas antes/después (capturas para cambios de UI).

Guías prácticas:
- Sigue el estilo Python (PEP 8, 4 espacios, naming snake_case).
- Evita hacer commit de credenciales o binarios grandes.
- Actualiza docs/scripts de configuración cuando cambie el comportamiento.
- Estilo de commit preferido: corto, imperativo y acotado (por ejemplo: `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 Licencia

[Apache-2.0](LICENSE)

## 🙏 Agradecimientos

LazyEdit se apoya en bibliotecas y servicios de código abierto, incluidos:
- FFmpeg para procesamiento multimedia
- Tornado para APIs backend
- MoviePy para flujos de edición
- Modelos de OpenAI para tareas del pipeline asistidas por IA
- CJKWrap y herramientas de texto multilingüe en flujos de subtítulos
