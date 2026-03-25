[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)



[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyEdit

<p align="center">
  <b>AI-ассистированный видеопайплайн</b> для генерации, обработки субтитров, метаданных и публикации по желанию.
  <br />
  <sub>Загрузить или сгенерировать -> транскрибировать -> перевести/отшлифовать -> вшить субтитры -> подписи/ключевые кадры -> метаданные -> опционально опубликовать</sub>
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

## 📌 Быстрые факты

LazyEdit — это сквозной AI-ассистированный видеопайплайн для создания, обработки и публикации по желанию. Он объединяет генерацию по prompt (Stage A/B/C), API для обработки медиа, рендеринг субтитров, подписи ключевых кадров, генерацию метаданных и передачу в AutoPublish.

| Быстрый факт | Значение |
| --- | --- |
| 📘 Канонический README | `README.md` (этот файл) |
| 🌐 Языковые версии | `i18n/README.*.md` (в каждой версии вверху сохранена одна строка выбора языка) |
| 🧠 Точка входа backend | `app.py` (Tornado) |
| 🖥️ Frontend-приложение | `app/` (Expo web/mobile) |
| 🧩 Режимы запуска | `python app.py` (ручной), `./start_lazyedit.sh` (tmux), опционально `lazyedit.service` |
| 🎯 Основные ссылки | `README.md`, `references/QUICKSTART.md`, `references/API_GUIDE.md`, `references/APP_GUIDE.md` |

## 🧭 Содержание

- [Обзор](#-обзор)
- [Быстрые факты](#-быстрые-факты)
- [Взгляд поверхностно](#-взгляд-поверхностно)
- [Архитектурный снимок](#-архитектурный-снимок)
- [Демо](#-демо)
- [Возможности](#-возможности)
- [Документация и i18n](#-документация-и-i18n)
- [Структура проекта](#-структура-проекта)
- [Предварительные требования](#-предварительные-требования)
- [Установка](#-установка)
- [Быстрый старт](#-быстрый-старт)
- [Шпаргалка по командам](#-шпаргалка-по-командам)
- [Использование](#-использование)
- [Конфигурация](#-конфигурация)
- [Файлы конфигурации](#-файлы-конфигурации)
- [Примеры API](#-примеры-api)
- [Примеры](#-примеры)
- [Заметки по разработке](#-заметки-по-разработке)
- [Тестирование](#-тестирование)
- [Предположения и ограничения](#-предположения-и-ограничения)
- [Заметки по развертыванию и синхронизации](#-заметки-по-развертыванию-и-синхронизации)
- [Устранение неполадок](#-устранение-неполадок)
- [Дорожная карта](#-дорожная-карта)
- [Участие](#-участие)
- [Support](#-support)
- [Лицензия](#-лицензия)
- [Благодарности](#-благодарности)

## ✨ Обзор

LazyEdit построен на Tornado backend (`app.py`) и Expo frontend (`app/`).

> Примечание: если параметры репозитория/рантайма отличаются между машинами, оставляйте существующие значения по умолчанию и переопределяйте их через переменные окружения, а не удаляйте fallback для конкретной машины.

| Почему команды это используют | Практический результат |
| --- | --- |
| Единый операторский поток | Загрузка, генерация, ремикс и публикация в одном пайплайне |
| API-first дизайн | Легко скриптить и интегрировать с другими инструментами |
| Local-first рантайм | Работает с tmux + сценариями развертывания через сервис |

| Шаг | Что происходит |
| --- | --- |
| 1 | Загрузка или генерация видео |
| 2 | Транскрипция и при необходимости перевод субтитров |
| 3 | Вшивание многоязычных субтитров с контролем компоновки |
| 4 | Генерация keyframes, captions и метаданных |
| 5 | Пакетирование и опциональная публикация через AutoPublish |

### Фокус пайплайна

- Загрузка, генерация, ремикс и управление библиотекой из единого интерфейса оператора.
- API-first поток для транскрипции, полировки/перевода субтитров, burn-in и метаданных.
- Опциональные интеграции с провайдерами генерации (Veo / Venice / A2E / Sora в `agi/`).
- Опциональная передача публикации через `AutoPublish`.

## 🎯 Взгляд поверхностно

| Область | Есть в LazyEdit | Статус |
| --- | --- | --- |
| Ядро приложения | Tornado API backend + Expo web/mobile frontend | ✅ |
| Медиа-пайплайн | ASR, перевод/полировка субтитров, burn-in, keyframes, captions, метаданные | ✅ |
| Генерация | Stage A/B/C и маршруты-обработчики провайдеров (`agi/`) | ✅ |
| Распространение | Опциональная передача в AutoPublish | 🟡 Опционально |
| Модель исполнения | Local-first скрипты, tmux-потоки, опциональный systemd service | ✅ |

## 🏗️ Архитектурный снимок

Репозиторий организован как медиа-пайплайн с API-first подходом и UI-слоем:

- `app.py` — точка входа Tornado и оркестратор маршрутов для загрузки, обработки, генерации, передачи публикации и отдачи медиа.
- `lazyedit/` содержит модульные блоки пайплайна (хранение в БД, перевод, burn-in субтитров, captions, метаданные, адаптеры провайдеров).
- `app/` — приложение Expo Router (web/mobile), управляющее загрузкой, обработкой, предпросмотром и публикацией.
- `config.py` централизует загрузку env и пути по умолчанию.
- `start_lazyedit.sh` и `lazyedit_config.sh` обеспечивают воспроизводимые локальные и production режимы запуска через tmux.

| Слой | Основные пути | Ответственность |
| --- | --- | --- |
| API и оркестрация | `app.py`, `config.py` | Точки доступа, маршрутизация, разрешение env |
| Ядро обработки | `lazyedit/`, `agi/` | Конвейер subtitle/caption/metadata + провайдеры |
| UI | `app/` | Операторский опыт (web/mobile через Expo) |
| Скрипты рантайма | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Локальный запуск и эксплуатация через сервис |

High-level flow:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Демо

Ниже показан основной путь оператора от загрузки до генерации метаданных.

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

## 🧩 Возможности

- ✨ Workflow генерации по prompt (Stage A/B/C) с путями интеграции Sora и Veo.
- 🧵 Полный конвейер обработки: транскрипция -> перевод/полировка субтитров -> burn-in -> keyframes -> captions -> метаданные.
- 🌏 Многоязычная сборка субтитров с поддержкой furigana/IPA/romaji.
- 🔌 API-first backend с endpointами для upload, обработки, отдачи медиа и очереди публикации.
- 🚚 Опциональная интеграция AutoPublish для передачи контента в соцсети.
- 🖥️ Единый backend + Expo workflow через запуск в tmux.

## 🌍 Документация и i18n


- Канонический источник: `README.md`
- Языковые версии: `i18n/README.*.md`
- Панель выбора языка: в каждом README одна строка выбора языка в начале, без дубликатов.

Если есть расхождение между переводами и английской документацией, считайте `README.md` источником истины, затем обновляйте языковые файлы по очереди.

| Политика i18n | Правило |
| --- | --- |
| Канонический источник | Сохранять `README.md` как source of truth |
| Language bar | Ровно одна строка выбора языка вверху |

## 🗂️ Структура проекта

```text
LazyEdit/
├── app.py                           # Точка входа backend Tornado и API-оркестрации
├── app/                             # Expo frontend (web/mobile)
├── lazyedit/                        # Ядро pipeline (translation, metadata, burner, DB, templates)
├── agi/                             # Абстракции провайдеров генерации (Sora/Veo/A2E/Venice маршруты в `agi/`)
├── DATA/                            # Runtime media input/output (symlink в этой рабочей среде)
├── translation_logs/                # Логи переводов
├── temp/                            # Временные runtime-файлы
├── install_lazyedit.sh              # Установщик systemd (ожидает корректные скрипты config/start/stop)
├── start_lazyedit.sh                # tmux launcher для backend + Expo
├── stop_lazyedit.sh                 # Помощник остановки tmux
├── lazyedit_config.sh               # Shell-конфиг деплоя/рантайма
├── config.py                        # Разрешение env (порты, пути, autopublish URL)
├── .env.example                     # Шаблон переопределений окружения
├── references/                      # Дополнительная документация (API guide, quickstart, deployment notes)
├── AutoPublish/                     # Submodule (optional publishing pipeline)
├── AutoPubMonitor/                  # Submodule (мониторинг/синхронизация)
├── whisper_with_lang_detect/        # Submodule (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule (основной captioner)
├── clip-gpt-captioning/             # Submodule (fallback captioner)
└── furigana/                        # External dependency в workflow (submodule в этом checkout)
```

Примечание по submodule/внешней зависимости:
- Submodule-ы в этом репозитории: `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` и `furigana`.
- В операционных инструкциях `furigana` и `echomind` рассматриваются как внешние/read-only зависимости. При сомнениях используйте апстрим и не редактируйте здесь.

## ✅ Предварительные требования

| Зависимость | Примечание |
| --- | --- |
| Linux окружение | Скрипты `systemd`/`tmux` ориентированы на Linux |
| Python 3.10+ | Используйте Conda env `lazyedit` |
| Node.js 20+ + npm | Требуются для Expo-приложения в `app/` |
| FFmpeg | Должен быть в `PATH` |
| PostgreSQL | Локальный peer auth или DSN-подключение |
| Git submodules | Требуются для ключевых частей pipeline |

## 🚀 Установка

1. Клонировать и инициализировать submodules:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Активировать Conda окружение:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Опциональная установка на уровне системы (service mode):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Замечания по установке сервиса:
- `install_lazyedit.sh` устанавливает `ffmpeg` и `tmux`, затем создает `lazyedit.service`.
- Он не создает `lazyedit_config.sh`, `start_lazyedit.sh` и `stop_lazyedit.sh`; эти файлы должны уже существовать и быть корректными.

## ⚡ Быстрый старт

Локальный запуск backend + frontend (минимальный путь):

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Во втором окне терминала:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Опциональный локальный bootstrap БД:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Профили запуска

| Профиль | Команда запуска | Backend по умолчанию | Frontend по умолчанию |
| --- | --- | --- | --- |
| Локальная разработка (ручная) | `python app.py` + команда Expo | `8787` | `8091` (пример команды) |
| Orchestrated через tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd service | `sudo systemctl start lazyedit.service` | Из конфига/env | N/A |

## 🧭 Шпаргалка по командам

| Задача | Команда |
| --- | --- |
| Инициализация submodule | `git submodule update --init --recursive` |
| Запуск только backend | `python app.py` |
| Запуск backend + Expo (tmux) | `./start_lazyedit.sh` |
| Остановка tmux запуска | `./stop_lazyedit.sh` |
| Подключиться к сессии tmux | `tmux attach -t lazyedit` |
| Статус сервиса | `sudo systemctl status lazyedit.service` |
| Логи сервиса | `sudo journalctl -u lazyedit.service` |
| DB smoke test | `python db_smoke_test.py` |
| Pytest smoke test | `pytest tests/test_db_smoke.py` |

## 🛠️ Использование

### Разработка: только backend

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Альтернативная точка входа, используемая в текущих deployment-сценариях:

```bash
python app.py -m lazyedit
```

URL backend по умолчанию: `http://localhost:8787` (из `config.py`, переопределяется через `PORT` или `LAZYEDIT_PORT`).

### Разработка: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Порты по умолчанию для `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Подключиться к сессии:

```bash
tmux attach -t lazyedit
```

Остановка сессии:

```bash
./stop_lazyedit.sh
```

### Управление сервисом

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Конфигурация

Скопируйте `.env.example` в `.env` и обновите пути/секреты:

```bash
cp .env.example .env
```

Примечание о приоритете конфигурации:

- `config.py` загружает значения из `.env`, если они есть, и перезаписывает только ключи, которые уже не экспортированы в shell.
- Поэтому runtime-переменные могут приходить из: переменных в shell -> `.env` -> значения по умолчанию в коде.
- Для запусков под tmux/service параметры задаются через `lazyedit_config.sh` (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, порты через env startup-скрипта).

### Ключевые переменные

| Переменная | Назначение | Значение по умолчанию/фолбэк |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Порт backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Корень медиа | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Локальный фолбэк `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | AutoPublish endpoint | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Таймаут запросов AutoPublish (сек) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Путь к Whisper/VAD скрипту | Зависит от окружения |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Названия ASR моделей | `large-v3` / `large-v2` (пример) |
| `LAZYEDIT_CAPTION_PYTHON` | Python runtime для caption-пайплайна | Зависит от окружения |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Основной путь/скрипт captioning | Зависит от окружения |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Путь скрипта резервного captioning и cwd | Зависит от окружения |
| `GRSAI_API_*` | Настройки интеграции Veo/GRSAI | Зависит от окружения |
| `VENICE_*`, `A2E_*` | Настройки интеграции Venice/A2E | Зависит от окружения |
| `OPENAI_API_KEY` | Нужен для функций на OpenAI | Нет |

Machine-specific notes:
- `app.py` может устанавливать поведение CUDA (`CUDA_VISIBLE_DEVICES` в контексте codebase).
- Некоторые пути в дефолтных значениях завязаны на конкретную машину; используйте переопределения в `.env` для переносимых конфигураций.
- `lazyedit_config.sh` управляет переменными запуска tmux/session для сценариев развертывания.

## 🧾 Файлы конфигурации

| Файл | Назначение |
| --- | --- |
| `.env.example` | Шаблон переменных окружения для backend/services |
| `.env` | Локальные переопределения машины; загружаются `config.py`/`app.py`, если существуют |
| `config.py` | Значения по умолчанию backend и разрешение переменных окружения |
| `lazyedit_config.sh` | Профиль tmux/service runtime (deploy path, conda env, app args, название сессии) |
| `start_lazyedit.sh` | Запускает backend + Expo в tmux с выбранными портами |
| `install_lazyedit.sh` | Создает `lazyedit.service` и валидирует существующие scripts/config |

Рекомендуемый порядок обновлений для переносимости между машинами:
1. Скопируйте `.env.example` в `.env`.
2. Задайте в `.env` пути и API-переменные `LAZYEDIT_*`.
3. Меняйте `lazyedit_config.sh` только для поведения tmux/service.

## 🔌 Примеры API

Примеры базового URL предполагают `http://localhost:8787`.

| Группа API | Ключевые endpoints |
| --- | --- |
| Upload и media | `/upload`, `/upload-stream`, `/media/*` |
| Video records | `/api/videos`, `/api/videos/{id}` |
| Processing | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Publish | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Generation | `/api/videos/generate` (+ provider routes в `app.py`) |

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

End-to-end process:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

List videos:

```bash
curl http://localhost:8787/api/videos
```

Publish package:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Подробнее по endpoint-ам и payload-ам: `references/API_GUIDE.md`.

Связанные группы endpoint-ов, которые будут использоваться чаще всего:
- Жизненный цикл видео: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Действия обработки: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Пути генерации/провайдеров: `/api/videos/generate` и маршруты Venice/A2E из `app.py`
- Распространение: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Примеры

### Frontend local run (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Если backend на `8887`:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android emulator

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS simulator (macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### Опциональный Sora generation helper

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Поддерживаемые длительности: `4`, `8`, `12`.
Поддерживаемые размеры: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Заметки по разработке

- Используйте `python` из Conda env `lazyedit` (не предполагается наличие системного `python3`).
- Не добавляйте большие медиа в Git; храните runtime медиа в `DATA/` или внешнем хранилище.
- Инициализируйте/обновляйте submodule при сбоях в разрешении компонентов пайплайна.
- Не делайте чрезмерно крупных рефакторов в одну итерацию; держите изменения сфокусированными.
- Для фронтенда URL API задается через `EXPO_PUBLIC_API_URL`.
- Для разработки backend API CORS открыт.

Политика по submodule и внешним зависимостям:
- Рассматривайте внешние зависимости как управляемые upstream; в этом репозитории избегайте изменений в submodule, если вы сознательно не работаете в них.
- В операционных инструкциях `furigana` (и иногда `echomind` в локальных установках) считаются внешними зависимостями; если есть сомнения, сохраняйте upstream и не правьте файлы в месте.

Полезные ссылки:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Безопасность и конфигурация:
- Храните API-ключи и секреты в переменных окружения; не коммитьте креды.
- Предпочитайте `.env` для локальных переопределений и оставляйте `.env.example` публичным шаблоном.
- Если поведение CUDA/GPU разное на разных хостах, переопределяйте через env, а не хардкодьте значения для конкретной машины.

## ✅ Тестирование

Current formal test surface is minimal and DB-oriented.

| Validation layer | Команда или метод |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Проверка Pytest DB | `pytest tests/test_db_smoke.py` |
| Интеграционный flow | Web UI + API с коротким sample из `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Для функциональной проверки используйте web UI и API flow с коротким sample-клиптом в `DATA/`.

Assumptions and portability notes:
- Некоторые пути в коде завязаны на рабочую станцию; это ожидаемое состояние в текущем репозитории.
- Если путь по умолчанию отсутствует на вашей машине, задайте соответствующую переменную `LAZYEDIT_*` в `.env`.
- Если сомневаетесь в machine-specific значении, сохраняйте существующие настройки и добавляйте явные переопределения, вместо удаления дефолтов.

## 🧱 Предположения и известные ограничения

- Набор backend зависимостей не зафиксирован root lockfile; воспроизводимость окружения сейчас зависит от локальной дисциплины.
- `app.py` в текущем виде намеренно монолитен и содержит большой набор маршрутов.
- Большая часть валидации — интеграционная/ручная (UI + API + sample media), с ограниченным числом формальных автоматических тестов.
- Runtime-папки (`DATA/`, `temp/`, `translation_logs/`) — это рабочие выходы и они могут существенно расти.
- Для полной функциональности нужны submodule; неполный checkout часто приводит к ошибкам из-за отсутствующих скриптов.

## 🚢 Заметки по развертыванию и синхронизации

Текущие известные пути и поток синхронизации (из оперативной документации):

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` на `lazyingart`

| Окружение | Путь | Примечание |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Основной исходный код + submodule |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` в ops docs |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Monitor/sync/process сессии |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | После апдейта submodule выполнить pull |

После пуша изменений `AutoPublish/` из этого репозитория, выполните pull на host публикации:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Устранение неполадок

| Проблема | Проверка / Исправление |
| --- | --- |
| Не хватает модулей пайплайна или скриптов | Выполните `git submodule update --init --recursive` |
| FFmpeg не найден | Установите FFmpeg и проверьте, что `ffmpeg -version` выполняется |
| Конфликт портов | По умолчанию backend `8787`, `start_lazyedit.sh` — `18787`; явно задайте `LAZYEDIT_PORT` или `PORT` |
| Expo не может достучаться до backend | Убедитесь, что `EXPO_PUBLIC_API_URL` указывает на активный backend-хост/порт |
| Проблемы с БД | Проверьте PostgreSQL + DSN/env-переменные; дополнительная дымовая проверка: `python db_smoke_test.py` |
| Проблемы с GPU/CUDA | Проверьте драйвер/CUDA совместимость с установленным Torch |
| Ошибки service-скриптов при установке | Убедитесь, что `lazyedit_config.sh`, `start_lazyedit.sh` и `stop_lazyedit.sh` существуют перед запуском установщика |

## 🗺️ Дорожная карта

- Редактирование субтитров/сегментов в приложении с A/B-просмотром и управлением на уровне строк.
- Более широкое покрытие end-to-end тестов для базовых API flow.
- Сверка документации между i18n-версиями README и режимами деплоя.
- Дополнительное усложнение устойчивости с retry и наблюдаемостью для провайдеров генерации.

## 🤝 Участие

Welcome to contributions.

1. Сделайте fork и создайте feature branch.
2. Держите коммиты сфокусированными и ограниченными по объему.
3. Проверяйте изменения локально (`python app.py`, ключевые API flow, интеграцию с app при необходимости).
4. Открывайте PR с описанием задачи, шагами для воспроизведения и заметками before/after (скриншоты для изменений UI).

Практические рекомендации:
- Следуйте Python-стилю (PEP 8, 4 пробела, именование snake_case).
- Не коммитьте credentials или большие бинарные файлы.
- Обновляйте документацию/конфиг/скрипты при изменении поведения.
- Рекомендуемый стиль коммита: короткий, императивный, ограниченный (например: `fix ffmpeg 7 compatibility`).



## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Благодарности

LazyEdit строится на базе open-source библиотек и сервисов, в том числе:
- FFmpeg для обработки медиа
- Tornado для backend API
- MoviePy для редакционных workflow
- OpenAI models для AI-ассистированных задач пайплайна
- CJKWrap и мультиязычные text toolchain в пайплайне субтитров
