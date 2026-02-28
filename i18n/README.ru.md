[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)


[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

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

<p align="center">
  <b>AI-ассистированный видеопоток</b> для генерации, обработки субтитров, метаданных и опциональной публикации.
  <br />
  <sub>Загрузить или сгенерировать -> транскрибировать -> перевести/отшлифовать -> вшить субтитры -> создать подписи/ключевые кадры -> метаданные -> опционально опубликовать</sub>
</p>

# LazyEdit

LazyEdit — это сквозной AI-ассистированный видеопайплайн для создания, обработки и (по желанию) публикации. Он объединяет генерацию по prompt (Stage A/B/C), API обработки медиа, рендеринг субтитров, создание keyframe-описаний, генерацию метаданных и передачу в AutoPublish.

| Коротко | Значение |
| --- | --- |
| 📘 Канонический README | `README.md` (этот файл) |
| 🌐 Языковые версии | `i18n/README.*.md` (в каждой версии ровно одна строка языковой навигации сверху) |
| 🧠 Точка входа backend | `app.py` (Tornado) |
| 🖥️ Frontend-приложение | `app/` (Expo web/mobile) |

## 🧭 Содержание

- Обзор
- В двух словах
- Архитектурная схема
- Демонстрации
- Возможности
- Документация и i18n
- Структура проекта
- Предпосылки
- Установка
- Быстрый старт
- Чек-лист команд
- Использование
- Конфигурация
- Файлы конфигурации
- Примеры API
- Примеры
- Заметки по разработке
- Тестирование
- Предположения и известные ограничения
- Заметки по развертыванию и синхронизации
- Устранение неполадок
- Дорожная карта
- Участие
- Support
- Лицензия
- Благодарности

## ✨ Обзор

LazyEdit построен на Tornado backend (`app.py`) и Expo frontend (`app/`).

> Примечание: если настройки репозитория/рантайма отличаются между машинами, оставляйте существующие значения по умолчанию и переопределяйте их через переменные окружения, а не удаляйте машинные fallback-пути.

| Зачем командам это нужно | Практический эффект |
| --- | --- |
| Единый операторский поток | Загрузка, генерация, ремикс и публикация в одном пайплайне |
| API-first дизайн | Удобно скриптовать и интегрировать с другими инструментами |
| Local-first рантайм | Работает с tmux и service-based сценариями развертывания |

| Шаг | Что происходит |
| --- | --- |
| 1 | Загрузка или генерация видео |
| 2 | Транскрипция и, при необходимости, перевод субтитров |
| 3 | Вшивание многоязычных субтитров с управлением макетом |
| 4 | Генерация keyframes, captions и метаданных |
| 5 | Упаковка и опциональная публикация через AutoPublish |

### Упор на пайплайн

- Загрузка, генерация, ремикс и управление библиотекой из одного интерфейса оператора.
- API-first поток для транскрипции, полировки/перевода субтитров, burn-in и метаданных.
- Опциональные интеграции с провайдерами генерации (хелперы Veo / Venice / A2E / Sora в `agi/`).
- Опциональная передача на публикацию через `AutoPublish`.

## 🎯 В двух словах

| Область | Есть в LazyEdit | Статус |
| --- | --- | --- |
| Основное приложение | Tornado API backend + Expo web/mobile frontend | ✅ |
| Медиа-пайплайн | ASR, перевод/шлифовка субтитров, burn-in, keyframes, captions, метаданные | ✅ |
| Генерация | Stage A/B/C и helper-маршруты провайдеров (`agi/`) | ✅ |
| Распространение | Опциональная передача в AutoPublish | 🟡 По желанию |
| Модель запуска | Local-first скрипты, tmux-workflow, optional systemd service | ✅ |

## 🏗️ Архитектурная схема

Репозиторий организован как media pipeline в формате API-first с UI-слоем:

- `app.py` — entrypoint Tornado и оркестратор маршрутов для загрузки, обработки, генерации, публикации и раздачи медиа.
- `lazyedit/` — модульные блоки пайплайна (хранение в БД, перевод, burn-in субтитров, captions, метаданные, адаптеры провайдеров).
- `app/` — Expo Router app (web/mobile), через которую происходят upload, processing, preview и публикация.
- `config.py` — централизованная загрузка окружения и путей по умолчанию.
- `start_lazyedit.sh` и `lazyedit_config.sh` — воспроизводимые режимы запуска через tmux для локальной и production эксплуатации.

| Слой | Основные пути | Роль |
| --- | --- | --- |
| API и оркестрация | `app.py`, `config.py` | Точки доступа, маршрутизация, разрешение переменных среды |
| Ядро обработки | `lazyedit/`, `agi/` | Конвейер subtitle/caption/metadata + провайдеры |
| UI | `app/` | Операторский интерфейс (web/mobile через Expo) |
| Скрипты запуска | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | Локальный и service запуск |

Высокоуровневый поток:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Демонстрации

Ниже показан основной путь оператора: от загрузки до генерации метаданных.

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

- ✨ Prompt-based генерационный workflow (Stage A/B/C) с путями интеграции Sora и Veo.
- 🧵 Полный пайплайн обработки: транскрипция -> polishing/перевод субтитров -> burn-in -> keyframes -> captions -> metadata.
- 🌏 Многоязычное составление субтитров с поддержкой furigana/IPA/romaji.
- 🔌 API-first backend с endpoint-ами для upload, обработки, выдачи медиа и очереди публикации.
- 🚚 Опциональная интеграция AutoPublish для передачи в social-платформы.
- 🖥️ Единый backend + Expo workflow через запуск скриптами tmux.

## 🌍 Документация и i18n

LazyEdit хранит канонический английский README (`README.md`) и переводы в `i18n/`.

- Канонический источник: `README.md`
- Языковые версии: `i18n/README.*.md`
- Языковая навигация: у каждой README ровно одна строка выбора языков сверху

Если есть расхождения между переводами и английской документацией, в таком случае английский `README.md` является источником истины, затем обновляйте файлы по одному.

| Политика i18n | Правило |
| --- | --- |
| Канонический источник | Держать `README.md` как source of truth |
| Языковая панель | Ровно одна строка выбора языка вверху |

## 🗂️ Структура проекта

```text
LazyEdit/
├── app.py                           # Точка входа Tornado backend и API-оркестрации
├── app/                             # Expo frontend (web/mobile)
├── lazyedit/                        # Ядро пайплайна (перевод, метаданные, burner, БД, шаблоны)
├── agi/                             # Абстракция провайдеров генерации (маршруты Sora/Veo/A2E/Venice в `agi/`)
├── DATA/                            # Runtime media input/output (симлинк в этой рабочей директории)
├── translation_logs/                # Логи перевода
├── temp/                            # Временные runtime-файлы
├── install_lazyedit.sh              # Установщик systemd (ожидает корректных config/start/stop скриптов)
├── start_lazyedit.sh                # tmux-лаунчер для backend + Expo
├── stop_lazyedit.sh                 # Помощник остановки tmux
├── lazyedit_config.sh               # Shell-конфиг деплоя/рантайма
├── config.py                        # Разрешение переменных окружения (порты, пути, autopublish URL)
├── .env.example                     # Шаблон override-переменных окружения
├── references/                      # Доп. документация (API guide, quickstart, notes по deploy)
├── AutoPublish/                     # Submodule (опциональный publishing pipeline)
├── AutoPubMonitor/                  # Submodule (мониторинг/синхронизация)
├── whisper_with_lang_detect/        # Submodule (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule (основной captioner)
├── clip-gpt-captioning/             # Submodule (резервный captioner)
└── furigana/                        # Внешняя зависимость в пайплайне (в этом checkout как submodule)
```

Примечание по submodule/внешним зависимостям:
- Git submodules этого репозитория: `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, и `furigana`.
- В рабочих инструкциях `furigana` и `echomind` считаются внешними/read-only зависимостями. Если есть сомнения, сохраняйте upstream и не редактируйте их здесь.

## ✅ Предпосылки

| Зависимость | Примечание |
| --- | --- |
| Linux-среда | Скрипты `systemd`/`tmux` ориентированы на Linux |
| Python 3.10+ | Используйте Conda env `lazyedit` |
| Node.js 20+ + npm | Нужен для Expo app в `app/` |
| FFmpeg | Должен быть в `PATH` |
| PostgreSQL | Локальный peer auth или DSN-подключение |
| Git submodules | Требуются для ключевых частей пайплайна |

## 🚀 Установка

1. Клонировать и инициализировать submodule:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Активировать Conda-окружение:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Опциональная установка на уровне системы (service mode):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Заметки по установке сервиса:
- `install_lazyedit.sh` ставит `ffmpeg` и `tmux`, затем создает `lazyedit.service`.
- Сценарий не создает `lazyedit_config.sh`, `start_lazyedit.sh` и `stop_lazyedit.sh`; эти файлы должны уже существовать и быть корректными.

## ⚡ Быстрый старт

Минимальный запуск backend + frontend локально:

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

Опциональное поднятие локальной базы данных:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Профили запуска

| Профиль | Команда запуска | Backend по умолчанию | Frontend по умолчанию |
| --- | --- | --- | --- |
| Локальная разработка (ручной) | `python app.py` + Expo-команда | `8787` | `8091` (пример) |
| Orchestrated через tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| systemd service | `sudo systemctl start lazyedit.service` | По config/env | N/A |

## 🧭 Чек-лист команд

| Задача | Команда |
| --- | --- |
| Инициализация submodules | `git submodule update --init --recursive` |
| Запустить только backend | `python app.py` |
| Запустить backend + Expo (tmux) | `./start_lazyedit.sh` |
| Остановить tmux-сессию | `./stop_lazyedit.sh` |
| Подключиться к tmux-сессии | `tmux attach -t lazyedit` |
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

Альтернативный entrypoint, используемый в текущих скриптах деплоя:

```bash
python app.py -m lazyedit
```

URL backend по умолчанию: `http://localhost:8787` (берется из `config.py`, переопределяется через `PORT` или `LAZYEDIT_PORT`).

### Разработка: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

Порты `start_lazyedit.sh` по умолчанию:
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

Примечание по приоритету конфигурации:

- `config.py` читает значения из `.env`, если файл есть, и задает только те ключи, которые еще не экспортированы в shell.
- Значения рантайма можно подставлять в цепочке: shell env -> `.env` -> дефолты в коде.
- Для запуска через tmux/service `lazyedit_config.sh` управляет параметрами запуска/сессии (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, порты через env запуска).

### Ключевые переменные

| Переменная | Назначение | Значение по умолчанию/резерв |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Порт backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Корневая директория медиа | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Локальный fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Таймаут AutoPublish (секунды) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Путь к скрипту Whisper/VAD | В зависимости от окружения |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Имена ASR-моделей | `large-v3` / `large-v2` (пример) |
| `LAZYEDIT_CAPTION_PYTHON` | Python runtime для caption-пайплайна | В зависимости от окружения |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Путь/скрипт primary captioning | В зависимости от окружения |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Путь/скрипт/рабочий каталог fallback captioning | В зависимости от окружения |
| `GRSAI_API_*` | Настройки интеграции Veo/GRSAI | В зависимости от окружения |
| `VENICE_*`, `A2E_*` | Настройки интеграции Venice/A2E | В зависимости от окружения |
| `OPENAI_API_KEY` | Нужен для OpenAI-опций | Нет |

Примечания по machine-specific параметрам:
- `app.py` может настраивать поведение CUDA (`CUDA_VISIBLE_DEVICES` в контексте кодовой базы).
- Некоторые дефолтные пути завязаны на конкретную рабочую станцию; для переносимой конфигурации используйте overrides в `.env`.
- `lazyedit_config.sh` управляет переменными запуска tmux/session для скриптов деплоя.

## 🧾 Файлы конфигурации

| Файл | Назначение |
| --- | --- |
| `.env.example` | Шаблон переменных окружения для backend/services |
| `.env` | Локальные overrides; загружаются `config.py`/`app.py` при наличии |
| `config.py` | Дефолты backend и резолв окружения |
| `lazyedit_config.sh` | Профиль tmux/service рантайма (deploy path, conda env, app args, session name) |
| `start_lazyedit.sh` | Запускает backend + Expo в tmux на выбранных портах |
| `install_lazyedit.sh` | Создает `lazyedit.service` и валидирует существующие скрипты/config |

Рекомендуемый порядок обновления для переносимости:
1. Скопируйте `.env.example` в `.env`.
2. Задайте путь/ключевые API значения `LAZYEDIT_*` в `.env`.
3. Меняйте `lazyedit_config.sh` только для поведения tmux/service в сценариях деплоя.

## 🔌 Примеры API

Базовый URL предполагает `http://localhost:8787`.

| Группа API | Представительные endpoints |
| --- | --- |
| Upload и медиа | `/upload`, `/upload-stream`, `/media/*` |
| Записи видео | `/api/videos`, `/api/videos/{id}` |
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

Публикация пакета:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

Дополнительные endpoints и детали payload: `references/API_GUIDE.md`.

Скорее всего, вы будете использовать такие группы:
- Жизненный цикл видео: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- Действия обработки: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- Порождение/provider-пути: `/api/videos/generate` и маршруты Venice/A2E в `app.py`
- Публикация: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Примеры

### Frontend локально (web)

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
Поддерживаемые разрешения: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Заметки по разработке

- Используйте `python` из Conda env `lazyedit` (не полагайтесь на `python3`).
- Не храните большие медиа в Git; помещайте runtime-медиа в `DATA/` или во внешнее хранилище.
- Инициализируйте/обновляйте submodules, если компоненты пайплайна не разрешаются.
- Держите изменения точечными; избегайте несвязанных крупных форматных правок.
- Для работы с frontend backend URL задается через `EXPO_PUBLIC_API_URL`.
- CORS открыт для app-разработки.

Политика по submodule и внешним зависимостям:
- Считайте внешние зависимости принадлежащими upstream. В этом репозитории избегайте редактирования submodule, если не работаете в них целенаправленно.
- Операционные инструкции рассматривают `furigana` и иногда `echomind` в локальных сетапах как внешние зависимости; если не уверены, сохраняйте upstream и не редактируйте на месте.

Полезные справки:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

Безопасность и hygiene настроек:
- Храните API-ключи и секреты в переменных окружения, не коммитьте креды.
- Предпочитайте `.env` для локальных overrides и держите `.env.example` публичным шаблоном.
- Если CUDA/GPU отличаются между хостами, переопределяйте через env, а не хардкодите значения.

## ✅ Тестирование

Текущая формальная тестовая поверхность минимальная и в основном DB-ориентирована.

| Уровень валидации | Команда или метод |
| --- | --- |
| DB smoke test | `python db_smoke_test.py` |
| Pytest DB check | `pytest tests/test_db_smoke.py` |
| Functional flow | Web UI + API с коротким sample-роликом из `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Для функциональной проверки используйте web UI и API-поток с коротким sample-клипа в `DATA/`.

Предпосылки и заметки по переносимости:
- Некоторые пути по умолчанию в коде завязаны на конкретную workstation; это ожидаемо в текущем состоянии.
- Если дефолтного пути нет на вашей машине, задайте соответствующую переменную `LAZYEDIT_*` в `.env`.
- При сомнениях о машинных значениях оставьте существующие настройки и добавьте явные overrides вместо удаления дефолтов.

## 🧱 Предположения и известные ограничения

- Набор backend зависимостей не фиксирован в root lockfile; воспроизводимость окружения зависит от локальной дисциплины.
- `app.py` сейчас намеренно монолитный и содержит большую поверхность роутов.
- Основная валидация пайплайна — интеграционная/ручная (UI + API + sample-медиа), с ограниченными формальными автоматическими тестами.
- Runtime каталоги (`DATA/`, `temp/`, `translation_logs/`) — это рабочие outputs и они могут существенно расти.
- Submodules необходимы для полной функциональности; частичная сборка часто приводит к ошибкам отсутствующих скриптов.

## 🚢 Заметки по развертыванию и синхронизации

Актуальные пути и sync flow (по документации репозитория):

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` на `lazyingart`

| Окружение | Путь | Примечание |
| --- | --- | --- |
| Dev workspace | `/home/lachlan/ProjectsLFS/LazyEdit` | Основной исходник + submodules |
| Deployed LazyEdit | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` в ops docs |
| Deployed AutoPubMonitor | `/home/lachlan/DiskMech/Projects/autopub-monitor` | Сессии monitor/sync/process |
| Publishing host | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | Делайте pull после изменений submodule |

После пуша изменений `AutoPublish/` из этого репозитория на publishing-хост:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Устранение неполадок

| Проблема | Проверка / исправление |
| --- | --- |
| Отсутствуют модули или скрипты пайплайна | Выполните `git submodule update --init --recursive` |
| FFmpeg не найден | Установите FFmpeg и проверьте `ffmpeg -version` |
| Конфликт портов | Backend по умолчанию `8787`; `start_lazyedit.sh` по умолчанию `18787`; задайте `LAZYEDIT_PORT` или `PORT` явно |
| Expo не достает backend | Убедитесь, что `EXPO_PUBLIC_API_URL` указывает на активный хост/порт backend |
| Проблемы подключения к БД | Проверьте PostgreSQL + DSN/env vars; опционально smoke check: `python db_smoke_test.py` |
| Проблемы GPU/CUDA | Проверьте совместимость драйвер/CUDA со стеком Torch |
| Service-скрипт падает на установке | Убедитесь, что `lazyedit_config.sh`, `start_lazyedit.sh` и `stop_lazyedit.sh` существуют перед запуском инсталлятора |

## 🗺️ Дорожная карта

- Редактирование субтитров/сегментов прямо в приложении с A/B preview и построчными контролами.
- Более сильное покрытие end-to-end тестами для ключевых API потоков.
- Сближение документации между i18n README вариантами и режимами deploy.
- Дополнительная hardening для retry-поведения генераторных провайдеров и прозрачности статусов.

## 🤝 Участие

Добро пожаловать к участию.

1. Сделайте fork и создайте feature branch.
2. Держите изменения сфокусированными и локализованными.
3. Проверяйте изменения локально (`python app.py`, key API flow, интеграцию app при необходимости).
4. Откройте PR с целью, шагами воспроизведения и заметками до/после (для UI-изменений добавляйте скриншоты).

Практические рекомендации:
- Соблюдайте Python style (PEP 8, 4 пробела, snake_case).
- Не коммитьте credentials и большие бинарные файлы.
- Обновляйте docs/config скрипты при изменении поведения.
- Рекомендуемый стиль коммита: короткий, повелительный, scoped (например: `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 Лицензия

[Apache-2.0](LICENSE)

## 🙏 Благодарности

LazyEdit строится на базе open-source библиотек и сервисов, включая:
- FFmpeg для обработки медиа
- Tornado для backend API
- MoviePy для видео-обработки
- OpenAI models для AI-ассистентных задач пайплайна
- CJKWrap и многоязычные инструменты текста в subtitle workflow
