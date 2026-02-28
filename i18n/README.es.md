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

LazyEdit es un flujo de trabajo integral de video asistido por IA para creación, procesamiento y publicación opcional. Combina generación basada en prompts (Stage A/B/C), APIs de procesamiento multimedia, renderizado de subtítulos, subtitulado por fotogramas clave, generación de metadatos y traspaso a AutoPublish.

## ✨ Resumen

LazyEdit está construido alrededor de un backend Tornado (`app.py`) y un frontend Expo (`app/`).

| Paso | Qué ocurre |
| --- | --- |
| 1 | Subir o generar video |
| 2 | Transcribir y traducir subtítulos opcionalmente |
| 3 | Incrustar subtítulos multilingües con controles de diseño |
| 4 | Generar fotogramas clave, captions y metadatos |
| 5 | Empaquetar y publicar opcionalmente mediante AutoPublish |

### Enfoque del pipeline

- Subida, generación, remix y gestión de biblioteca desde una sola UI de operación.
- Flujo de procesamiento API-first para transcripción, pulido/traducción de subtítulos, burn-in y metadatos.
- Integraciones opcionales con proveedores de generación (helpers de Veo / Venice / A2E / Sora en `agi/`).
- Traspaso de publicación opcional mediante `AutoPublish`.

## 🎯 Vista rápida

| Área | Incluido en LazyEdit |
| --- | --- |
| App principal | Backend API Tornado + frontend Expo web/móvil |
| Pipeline multimedia | ASR, traducción/pulido de subtítulos, burn-in, fotogramas clave, captions, metadatos |
| Generación | Stage A/B/C y rutas helper de proveedores (`agi/`) |
| Distribución | Traspaso opcional a AutoPublish |
| Modelo de ejecución | Scripts local-first, flujos tmux, servicio systemd opcional |

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
      <br /><sub>Resumen del video</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Vista previa de traducción</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Slots de burn-in</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Diseño de burn-in</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Fotogramas clave + captions</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Generador de metadatos</sub>
    </td>
  </tr>
</table>

## 🧩 Características

- Flujo de generación basado en prompts (Stage A/B/C) con rutas de integración Sora y Veo.
- Pipeline completo de procesamiento: transcripción -> pulido/traducción de subtítulos -> burn-in -> fotogramas clave -> captions -> metadatos.
- Composición de subtítulos multilingüe con rutas de soporte relacionadas con furigana/IPA/romaji.
- Backend API-first con endpoints de subida, procesamiento, servido de medios y cola de publicación.
- Integración opcional con AutoPublish para traspaso a plataformas sociales.
- Flujo combinado backend + Expo compatible mediante scripts de arranque tmux.

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
├── install_lazyedit.sh              # Instalador systemd (espera scripts de config/start/stop)
├── start_lazyedit.sh                # Lanzador tmux para backend + Expo
├── stop_lazyedit.sh                 # Helper para detener tmux
├── lazyedit_config.sh               # Configuración shell de despliegue/ejecución
├── config.py                        # Resolución de entorno/config (puertos, rutas, URL autopublish)
├── .env.example                     # Plantilla de override de entorno
├── references/                      # Documentación adicional (guía API, inicio rápido, notas de despliegue)
├── AutoPublish/                     # Submódulo (pipeline de publicación opcional)
├── AutoPubMonitor/                  # Submódulo (automatización de monitor/sync)
├── whisper_with_lang_detect/        # Submódulo (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submódulo (captioner principal)
├── clip-gpt-captioning/             # Submódulo (captioner de respaldo)
└── furigana/                        # Dependencia externa en el flujo (submódulo rastreado en este checkout)
```

## ✅ Requisitos previos

| Dependencia | Notas |
| --- | --- |
| Entorno Linux | Los scripts `systemd`/`tmux` están orientados a Linux |
| Python 3.10+ | Usa el entorno Conda `lazyedit` |
| Node.js 20+ + npm | Requerido para la app Expo en `app/` |
| FFmpeg | Debe estar disponible en `PATH` |
| PostgreSQL | Autenticación local peer o conexión basada en DSN |
| Submódulos Git | Requeridos para pipelines clave |

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
- No genera `lazyedit_config.sh`, `start_lazyedit.sh` ni `stop_lazyedit.sh`; esos archivos ya deben existir y ser correctos.

## 🛠️ Uso

### Desarrollo: solo backend

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Entrada alternativa usada en los scripts de despliegue actuales:

```bash
python app.py -m lazyedit
```

URL por defecto del backend: `http://localhost:8787` (desde `config.py`, anulable con `PORT` o `LAZYEDIT_PORT`).

### Desarrollo: backend + app Expo (tmux)

```bash
./start_lazyedit.sh
```

Puertos por defecto de `start_lazyedit.sh`:
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

### Gestión del servicio

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

### Variables clave

| Variable | Propósito | Valor por defecto/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Puerto del backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Directorio raíz de medios | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN de PostgreSQL | Fallback DB local `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint de AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Timeout de solicitud AutoPublish (segundos) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Ruta del script Whisper/VAD | Dependiente del entorno |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Nombres de modelos ASR | `large-v3` / `large-v2` (ejemplo) |
| `LAZYEDIT_CAPTION_PYTHON` | Runtime de Python para pipeline de captions | Dependiente del entorno |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Ruta/script de captioning principal | Dependiente del entorno |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Ruta/script/cwd de captioning de respaldo | Dependiente del entorno |
| `GRSAI_API_*` | Ajustes de integración Veo/GRSAI | Dependiente del entorno |
| `VENICE_*`, `A2E_*` | Ajustes de integración Venice/A2E | Dependiente del entorno |
| `OPENAI_API_KEY` | Requerida para funciones respaldadas por OpenAI | Ninguno |

Notas específicas de máquina:
- `app.py` puede definir comportamiento CUDA (uso de `CUDA_VISIBLE_DEVICES` en el contexto del código).
- Algunas rutas por defecto son específicas de estaciones de trabajo; usa overrides de `.env` para configuraciones portables.
- `lazyedit_config.sh` controla variables de arranque de sesión/tmux para scripts de despliegue.

## 🔌 Ejemplos de API

Los ejemplos asumen como base URL `http://localhost:8787`.

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

Más endpoints y detalles de payload: `references/API_GUIDE.md`.

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

### Helper opcional de generación con Sora

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Segundos compatibles: `4`, `8`, `12`.
Tamaños compatibles: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Notas de desarrollo

- Usa `python` del entorno Conda `lazyedit` (no asumas `python3` del sistema).
- Mantén los medios grandes fuera de Git; guarda medios de ejecución en `DATA/` o almacenamiento externo.
- Inicializa/actualiza submódulos siempre que componentes del pipeline no se puedan resolver.
- Mantén los cambios acotados; evita grandes cambios de formato no relacionados.
- Para frontend, la URL de API backend se controla con `EXPO_PUBLIC_API_URL`.
- CORS está abierto en el backend para desarrollo de la app.

Política de submódulos y dependencias externas:
- Trata las dependencias externas como proyectos mantenidos upstream. En este flujo de trabajo del repositorio, evita editar internamente submódulos salvo que estés trabajando intencionalmente en esos proyectos.
- La guía operativa de este repo trata `furigana` (y en algunos entornos locales también `echomind`) como rutas de dependencias externas; ante la duda, preserva upstream y evita ediciones in-place.

Referencias útiles:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ Pruebas

La cobertura de pruebas formal actual es mínima y orientada a BD.

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Para validación funcional, usa el flujo de UI web y API con un clip de muestra corto en `DATA/`.

## 🚢 Notas de despliegue y sincronización

Rutas conocidas actuales y flujo de sincronización (desde la documentación operativa del repositorio):

- Workspace de desarrollo: `/home/lachlan/ProjectsLFS/LazyEdit`
- Backend + app LazyEdit desplegados: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor desplegado: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Host del sistema de publicación: `/home/lachlan/Projects/auto-publish` en `lazyingart`

Después de hacer push de actualizaciones de `AutoPublish/` desde este repo, haz pull en el host de publicación:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Solución de problemas

| Problema | Verificar / Corregir |
| --- | --- |
| Faltan módulos o scripts del pipeline | Ejecuta `git submodule update --init --recursive` |
| FFmpeg no encontrado | Instala FFmpeg y confirma que `ffmpeg -version` funciona |
| Conflictos de puertos | El backend usa `8787` por defecto; `start_lazyedit.sh` usa `18787`; define `LAZYEDIT_PORT` o `PORT` explícitamente |
| Expo no alcanza el backend | Asegura que `EXPO_PUBLIC_API_URL` apunte al host/puerto backend activos |
| Problemas de conexión a base de datos | Verifica PostgreSQL + DSN/variables de entorno; verificación opcional: `python db_smoke_test.py` |
| Problemas de GPU/CUDA | Confirma compatibilidad de driver/CUDA con el stack de Torch instalado |
| Fallo del script de servicio durante instalación | Asegura que `lazyedit_config.sh`, `start_lazyedit.sh` y `stop_lazyedit.sh` existan antes de ejecutar el instalador |

## 🗺️ Hoja de ruta

- Edición de subtítulos/segmentos en la app con vista previa A/B y controles por línea.
- Cobertura de pruebas end-to-end más sólida para flujos de API centrales.
- Convergencia de documentación entre variantes README i18n y modos de despliegue.
- Mayor robustez del flujo para reintentos de proveedores de generación y visibilidad de estado.

## 🤝 Contribuciones

Las contribuciones son bienvenidas.

1. Haz un fork y crea una rama de funcionalidad.
2. Mantén commits enfocados y acotados.
3. Valida cambios localmente (`python app.py`, flujo API clave e integración de app si aplica).
4. Abre un PR con propósito, pasos de reproducción y notas de antes/después (capturas para cambios de UI).

Guías prácticas:
- Sigue estilo Python (PEP 8, 4 espacios, nomenclatura snake_case).
- Evita commitear credenciales o binarios grandes.
- Actualiza docs/scripts de configuración cuando cambie el comportamiento.
- Estilo de commit preferido: corto, imperativo, acotado (por ejemplo: `fix ffmpeg 7 compatibility`).

## ❤️ Lo que tu apoyo hace posible

- <b>Mantener herramientas abiertas</b>: hosting, inferencia, almacenamiento de datos y operaciones de comunidad.  
- <b>Lanzar más rápido</b>: semanas de tiempo open-source enfocado en EchoMind, LazyEdit y MultilingualWhisper.  
- <b>Prototipar wearables</b>: óptica, sensores y componentes neuromórficos/edge para IdeasGlass + LightMind.  
- <b>Acceso para todos</b>: despliegues subvencionados para estudiantes, creadores y grupos comunitarios.

### Donar

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

## 📄 Licencia

[Apache-2.0](LICENSE)

## 🙏 Agradecimientos

LazyEdit se apoya en bibliotecas y servicios open-source, incluyendo:
- FFmpeg para procesamiento multimedia
- Tornado para APIs backend
- MoviePy para flujos de edición
- Modelos de OpenAI para tareas del pipeline asistidas por IA
- CJKWrap y herramientas de texto multilingüe en flujos de subtítulos
