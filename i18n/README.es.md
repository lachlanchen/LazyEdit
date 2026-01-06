<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

<p>
  <b>Languages:</b>
  <a href="../README.md">English</a>
  · <a href="README.zh-Hant.md">中文（繁體）</a>
  · <a href="README.zh-Hans.md">中文 (简体)</a>
  · <a href="README.ja.md">日本語</a>
  · <a href="README.ko.md">한국어</a>
  · <a href="README.vi.md">Tiếng Việt</a>
  · <a href="README.ar.md">العربية</a>
  · <a href="README.fr.md">Français</a>
  · <a href="README.es.md">Español</a>
</p>

# LazyEdit

LazyEdit es una herramienta de edición de video automática impulsada por IA. Genera subtítulos, resaltados, tarjetas de palabras y metadatos de calidad profesional para automatizar tareas de edición.

## Características

- **Transcripción automática**: convierte audio a texto con IA
- **Caption automático**: genera descripciones del contenido
- **Subtítulos automáticos**: crea y quema subtítulos en el video
- **Resaltado automático**: destaca palabras clave
- **Metadatos automáticos**: extrae y genera metadatos
- **Tarjetas de palabras**: añade tarjetas educativas
- **Generación de teaser**: repite segmentos clave al inicio
- **Soporte multilingüe**: varios idiomas incluyendo inglés y chino
- **Generación de portada**: extrae la mejor escena y añade texto

## Instalación

### Requisitos

- Python 3.10 o superior
- FFmpeg
- GPU compatible con CUDA (aceleración de transcripción)
- Gestor de entornos Conda

### Pasos de instalación

1. Clonar el repositorio:
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. Ejecutar el script de instalación:
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

El script:
- Instala paquetes del sistema (ffmpeg, tmux)
- Crea el entorno conda "lazyedit"
- Configura el servicio systemd para inicio automático
- Configura permisos necesarios

## Uso

LazyEdit se ejecuta como aplicación web en http://localhost:8081

### Procesar un video

1. Sube el video desde la interfaz web
2. LazyEdit hará automáticamente:
   - Transcripción y captions
   - Generación de metadatos y contenido educativo
   - Subtítulos en el idioma detectado
   - Resaltado de términos importantes
   - Creación de teaser
   - Generación de portada
   - Empaquetado y entrega del resultado

### Uso por línea de comandos

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## Estructura del proyecto

- `app.py` - entrada principal
- `lazyedit/` - módulos principales
  - `autocut_processor.py` - segmentación y transcripción
  - `subtitle_metadata.py` - metadatos desde subtítulos
  - `subtitle_translate.py` - traducción de subtítulos
  - `video_captioner.py` - captions de video
  - `words_card.py` - tarjetas de palabras
  - `utils.py` - utilidades
  - `openai_version_check.py` - compatibilidad API OpenAI

## Configuración

El servicio systemd se crea en `/etc/systemd/system/lazyedit.service`.

LazyEdit usa una sesión tmux llamada "lazyedit" para ejecutarse en segundo plano.

## Gestión del servicio

- Iniciar: `sudo systemctl start lazyedit.service`
- Detener: `sudo systemctl stop lazyedit.service`
- Estado: `sudo systemctl status lazyedit.service`
- Logs: `sudo journalctl -u lazyedit.service`

## Uso avanzado

Se puede personalizar:
- Longitud y posición del teaser
- Estilos de resaltado
- Fuentes y posición de subtítulos
- Estructura de salida
- Selección de GPU

## Solución de problemas

- Si no inicia, revisar estado y logs de systemd
- Si falla el procesamiento, verificar FFmpeg
- Para GPU, comprobar CUDA y disponibilidad
- Verificar que el entorno conda esté activo

## Licencia

[Indica la licencia aquí]

## Agradecimientos

LazyEdit utiliza:
- FFmpeg (procesamiento de video)
- Modelos OpenAI (IA)
- Tornado (framework web)
- MoviePy (edición de video)
- CJKWrap (texto multilingüe)
