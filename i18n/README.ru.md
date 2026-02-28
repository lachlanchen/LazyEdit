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
</p>

## 📌 Быстрые факты

LazyEdit — это end-to-end AI-ассистированный видеопайплайн для создания, обработки и публикации по желанию. Он объединяет генерацию по prompt (Stage A/B/C), API для обработки медиа, рендеринг субтитров, подписи ключевых кадров, генерацию метаданных и передачу в AutoPublish.

| Быстрый факт | Значение |
| --- | --- |
| 📘 Канонический README | `README.md` (этот файл) |
| 🌐 Языковые версии | `i18n/README.*.md` (в каждой версии вверху сохранена одна строка выбора языка) |
| 🧠 Точка входа backend | `app.py` (Tornado) |
| 🖥️ Frontend-приложение | `app/` (Expo web/mobile) |

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
- [Чек-лист команд](#-чек-лист-команд)
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

| Зачем это нужно командам | Практический результат |
| --- | --- |
| Единый операторский поток | Загрузка, генерация, ремикс и публикация в одном пайплайне |
| API-first дизайн | Легко скриптить и интегрировать с другими инструментами |
| Local-first рантайм | Работает с tmux и сценариями развертывания через сервис |

| Шаг | Что происходит |
| --- | --- |
| 1 | Загрузка или генерация видео |
| 2 | Транскрипция и при необходимости перевод субтитров |
| 3 | Вшивание многоязычных субтитров с контролем компоновки |
| 4 | Генерация keyframes, captions и метаданных |
| 5 | Пакетирование и опциональная публикация через AutoPublish |

### Упор на pipeline

- Загрузка, генерация, ремикс и управление библиотекой из единого интерфейса оператора.
- API-first поток для транскрипции, полировки/перевода субтитров, burn-in и метаданных.
- Опциональные интеграции с провайдерами генерации (хелперы Veo / Venice / A2E / Sora в `agi/`).
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

- ✨ Prompt-based pipeline генерации (Stage A/B/C) с путями интеграции Sora и Veo.
- 🧵 Полный конвейер обработки: транскрипция -> polishing/перевод субтитров -> burn-in -> keyframes -> captions -> метаданные.
- 🌏 Многоязычное формирование субтитров с путями поддержки furigana/IPA/romaji.
- 🔌 API-first backend с endpointами для upload, обработки, выдачи медиа и очереди публикации.
- 🚚 Опциональная интеграция AutoPublish для передачи контента в соцсети.
- 🖥️ Единый backend + Expo workflow через запуск в tmux.

## 🌍 Документация и i18n

- Canonical source: `README.md`
- Language variants: `i18n/README.*.md`
- Language navigation: keep a single language-options line at the top of each README (no duplicate language bars)

Если есть расхождение между переводами и английской документацией, считайте `README.md` источником истины, затем обновляйте файлы языков по одному.

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
├── install_lazyedit.sh              # Установщик systemd (требует наличие корректных скриптов config/start/stop)
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
- Submodule-создачи в этом репозитории: `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning` и `furigana`.
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

Заметки по службе:
- `install_lazyedit.sh` устанавливает `ffmpeg` и `tmux`, затем создает `lazyedit.service`.
- `install_lazyedit.sh` не генерирует `lazyedit_config.sh`, `start_lazyedit.sh` или `stop_lazyedit.sh`; эти файлы должны уже существовать и быть корректными.

## ⚡ Быстрый старт

Минимальный путь для локального запуска backend + frontend:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Вторая консоль:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Опциональный bootstrap локальной БД:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Профили запуска

| Профиль | Команда запуска | Backend по умолчанию | Frontend по умолчанию |
| --- | --- | --- | --- |
| Локальная разработка (ручной) | `python app.py` + Expo-команда | `8787` | `8091` (пример команды) |
| Tmux-оркестрация | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd service | `sudo systemctl start lazyedit.service` | От config/env | N/A |

## 🧭 Чек-лист команд

| Задача | Команда |
| --- | --- |
| Инициализация submodules | `git submodule update --init --recursive` |
| Запуск только backend | `python app.py` |
| Запуск backend + Expo (tmux) | `./start_lazyedit.sh` |
| Остановка tmux-сессии | `./stop_lazyedit.sh` |
| Подключиться к сессии tmux | `tmux attach -t lazyedit` |
| Проверить статус сервиса | `sudo systemctl status lazyedit.service` |
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

Альтернативная entrypoint, используемая в текущих deployment-скриптах:

```bash
python app.py -m lazyedit
```

URL backend по умолчанию: `http://localhost:8787` (из `config.py`, переопределяется через `PORT` или `LAZYEDIT_PORT`).

### Разработка: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Порты по умолчанию в `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

Подключиться к сессии:

```bash
tmux attach -t lazyedit
```

Остановить сессию:

```bash
./stop_lazyedit.sh
```

### Управление службой

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

Особенности порядка конфигурации:

- `config.py` читает `.env`, если он существует, и задает только те ключи, которые еще не экспортированы в shell.
- Значения рантайма могут задаваться в цепочке: shell env -> `.env` -> дефолты кода.
- Для запусков через tmux/service `lazyedit_config.sh` управляет параметрами запуска/сессии (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, порты через env запуска).

### Ключевые переменные

| Variable | Назначение | Default/Fallback |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Порт backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Корневая папка медиа | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Локальный fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Таймаут запроса AutoPublish (секунды) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Путь к скрипту Whisper/VAD | Зависит от окружения |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Имена ASR-моделей | `large-v3` / `large-v2` (пример) |
| `LAZYEDIT_CAPTION_PYTHON` | Python runtime для caption pipeline | Зависит от окружения |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Основной путь/скрипт captioning | Зависит от окружения |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Путь/скрипт/рабочий каталог fallback captioning | Зависит от окружения |
| `GRSAI_API_*` | Параметры интеграции Veo/GRSAI | Зависит от окружения |
| `VENICE_*`, `A2E_*` | Параметры интеграции Venice/A2E | Зависит от окружения |
| `OPENAI_API_KEY` | Требуется для OpenAI-функций | None |

Заметки по machine-specific параметрам:
- `app.py` может настраивать поведение CUDA (`CUDA_VISIBLE_DEVICES` используется в контексте codebase).
- Некоторые пути по умолчанию завязаны на конкретную машину; для переносимости используйте overrides в `.env`.
- `lazyedit_config.sh` управляет переменными запуска tmux/session для сценариев деплоя.

## 🧾 Файлы конфигурации

| Файл | Назначение |
| --- | --- |
| `.env.example` | Шаблон переменных окружения для backend/services |
| `.env` | Локальные overrides; загружаются `config.py`/`app.py` при наличии |
| `config.py` | Дефолты backend и разрешение окружения |
| `lazyedit_config.sh` | Профиль tmux/service (deploy path, conda env, app args, session name) |
| `start_lazyedit.sh` | Запускает backend + Expo в tmux на выбранных портах |
| `install_lazyedit.sh` | Создает `lazyedit.service` и проверяет существующие scripts/config |

Рекомендуемый порядок обновления для переносимости:
1. Скопируйте `.env.example` в `.env`.
2. Установите значения `LAZYEDIT_*` в `.env` для путей и API.
3. Меняйте `lazyedit_config.sh` только под поведение tmux/service в сценариях деплоя.

## 🔌 Примеры API

Базовый URL предполагает `http://localhost:8787`.

| API группа | Представительные endpoints |
| --- | --- |
| Upload и медиа | `/upload`, `/upload-stream`, `/media/*` |
| Видео-записи | `/api/videos`, `/api/videos/{id}` |
| Обработка | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| Публикация | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| Генерация | `/api/videos/generate` (+ маршруты провайдеров в `app.py`) |

Upload:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

End-to-end процесс:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

Список видео:

```bash
curl http://localhost:8787/api/videos
```

Публикационный пакет:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Подробнее о endpoint-ах и payload: `references/API_GUIDE.md`.

Связанные группы endpoints, которые вы обычно будете использовать:
- Жизненный цикл видео: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Действия обработки: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Пути генерации/provider: `/api/videos/generate` и маршруты Venice/A2E в `app.py`
- Публикация: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Примеры

### Frontend локально (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Если backend работает на `8887`:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### Android-эмулятор

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### iOS-симулятор (macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### Опциональный Sora generation helper

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Поддерживаемые секунды: `4`, `8`, `12`.
Поддерживаемые размеры: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Заметки по разработке

- Используйте `python` из Conda env `lazyedit` (не предполагается системный `python3`).
- Не коммите большие медиа; храните runtime-медиа в `DATA/` или внешнем хранилище.
- Инициализируйте/обновляйте submodules при падении зависимостей pipeline.
- Оставляйте изменения точечными; избегайте несвязанных крупных правок форматирования.
- Для frontend-сценариев URL API контролируется переменной `EXPO_PUBLIC_API_URL`.
- CORS открыт на backend для разработки app.

Политика submodule и внешних зависимостей:
- Считайте внешние зависимости принадлежащими upstream. В рамках этого репозитория избегайте редактирования кода submodule, если только вы не работаете с ними целенаправленно.
- Операционные инструкции рассматривают `furigana` (и иногда `echomind` в некоторых локальных сетапах) как внешние пути зависимостей; при сомнении сохраняйте upstream и не редактируйте in-place.

Полезные ссылки:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Безопасность и hygiene конфигурации:
- Храните API-ключи и секреты в переменных окружения, не коммитьте credentials.
- Используйте `.env` для overrides машины и держите `.env.example` как публичный шаблон.
- Если поведение CUDA/GPU отличается между хостами, переопределяйте через env, не захардкоживайте значения.

## ✅ Тестирование

Текущий формальный тестовый охват минимальный и в основном ориентирован на БД.

| Уровень валидации | Команда или метод |
| --- | --- |
| DB smoke | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | Web UI + API с коротким sample из `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Для функциональной проверки используйте web UI и API flow с коротким sample-клипом из `DATA/`.

Предположения и заметки по переносимости:
- Некоторые пути по умолчанию в коде завязаны на конкретную рабочую станцию; это ожидаемо для текущего состояния.
- Если на вашей машине отсутствует путь по умолчанию, задайте соответствующую переменную `LAZYEDIT_*` в `.env`.
- Если сомневаетесь в machine-specific значения, оставьте текущие настройки и добавьте явные overrides вместо удаления дефолтов.

## 🧱 Предположения и известные ограничения

- Набор backend зависимостей не зафиксирован root lockfile; воспроизводимость окружения пока зависит от дисциплины локальной настройки.
- `app.py` сейчас намеренно монолитный и содержит большой маршрутный слой.
- Большая часть валидации — интеграционная/ручная (UI + API + sample media), с ограниченной автоматикой.
- Runtime каталоги (`DATA/`, `temp/`, `translation_logs/`) являются operational outputs и могут заметно расти.
- Submodules необходимы для полной функциональности; неполный checkout часто приводит к ошибкам из-за отсутствующих скриптов.

## 🚢 Заметки по развертыванию и синхронизации

Актуальные пути и поток синхронизации (по внутренней документации репозитория):

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` на `lazyingart`

| Окружение | Путь | Примечание |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Основной исходник + submodules |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` в операционных заметках |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Сессии monitor/sync/process |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Делайте pull после обновлений submodule |

После пуша обновлений `AutoPublish/` из этого репозитория на публикационный хост:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Устранение неполадок

| Проблема | Проверка / исправление |
| --- | --- |
| Отсутствуют модули/скрипты пайплайна | Запустите `git submodule update --init --recursive` |
| FFmpeg не найден | Установите FFmpeg и проверьте `ffmpeg -version` |
| Конфликт портов | Backend по умолчанию `8787`; `start_lazyedit.sh` по умолчанию `18787`; задайте `LAZYEDIT_PORT` или `PORT` явно |
| Expo не достает backend | Проверьте, что `EXPO_PUBLIC_API_URL` указывает на активный хост/порт backend |
| Проблемы с БД | Проверьте PostgreSQL + DSN/env vars; опциональный smoke check: `python db_smoke_test.py` |
| Проблемы GPU/CUDA | Проверьте совместимость драйверов/CUDA со стеком Torch |
| Service-скрипт падает на установке | Убедитесь, что `lazyedit_config.sh`, `start_lazyedit.sh` и `stop_lazyedit.sh` существуют перед запуском инсталлятора |

## 🗺️ Дорожная карта

- Редактирование субтитров/сегментов в приложении с A/B preview и построчными контролами.
- Более глубокое покрытие end-to-end-тестами для ключевых API потоков.
- Ближе привести i18n README к единообразию между версиями и режимами deploy.
- Дополнительное hardening для retry-логики провайдеров генерации и прозрачности статусов.

## 🤝 Участие

Добро пожаловать в контрибуцию.

1. Сделайте fork и создайте feature branch.
2. Держите изменения сфокусированными и сдержанными по масштабу.
3. Проверяйте локально (`python app.py`, ключевой API flow, интеграцию app при необходимости).
4. Откройте PR с целью, шагами repro и заметками до/после (для UI-изменений приложите скриншоты).

Практические рекомендации:
- Соблюдайте Python style (PEP 8, 4 пробела, snake_case).
- Не коммитьте credentials и большие бинарники.
- Обновляйте документацию и конфиги при изменении поведения.
- Предпочтительный стиль коммита: короткий, повелительный, scoped (например: `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Благодарности

LazyEdit строится на открытых библиотеках и сервисах, включая:
- FFmpeg для обработки медиа
- Tornado для backend API
- MoviePy для видео-обработки
- OpenAI models для AI-ассистентных задач пайплайна
- CJKWrap и многоязычные инструменты текста в subtitle workflow
