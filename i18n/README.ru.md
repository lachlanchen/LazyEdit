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

LazyEdit — это сквозной AI-ассистированный видеопайплайн для создания, обработки и при необходимости публикации контента. Он объединяет генерацию по промптам (Stage A/B/C), API обработки медиа, рендеринг субтитров, подписи к ключевым кадрам, генерацию метаданных и передачу в AutoPublish.

## ✨ Обзор

LazyEdit построен вокруг backend на Tornado (`app.py`) и frontend на Expo (`app/`).

| Шаг | Что происходит |
| --- | --- |
| 1 | Загрузка или генерация видео |
| 2 | Транскрибация и при необходимости перевод субтитров |
| 3 | Вшивание многоязычных субтитров с контролем макета |
| 4 | Генерация ключевых кадров, подписей и метаданных |
| 5 | Сборка пакета и, при необходимости, публикация через AutoPublish |

### Фокус пайплайна

- Загрузка, генерация, ремикс и управление библиотекой в одном операторском UI.
- API-first поток обработки: транскрибация, полировка/перевод субтитров, вшивание и генерация метаданных.
- Опциональные интеграции провайдеров генерации (хелперы Veo / Venice / A2E / Sora в `agi/`).
- Опциональная передача на публикацию через `AutoPublish`.

## 🎯 Кратко

| Область | Что включает LazyEdit |
| --- | --- |
| Основное приложение | Tornado API backend + Expo frontend (web/mobile) |
| Медиа-пайплайн | ASR, перевод/полировка субтитров, вшивание, ключевые кадры, подписи, метаданные |
| Генерация | Stage A/B/C и маршруты-хелперы провайдеров (`agi/`) |
| Дистрибуция | Опциональная передача в AutoPublish |
| Модель запуска | Local-first скрипты, tmux-процессы, опциональный systemd-сервис |

## 🎬 Демо

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

- Генеративный workflow по промптам (Stage A/B/C) с путями интеграции Sora и Veo.
- Полный пайплайн обработки: transcription -> subtitle polish/translation -> burn-in -> keyframes -> captions -> metadata.
- Многоязычная компоновка субтитров с путями поддержки, связанными с furigana/IPA/romaji.
- API-first backend с endpoint'ами для загрузки, обработки, выдачи медиа и очереди публикации.
- Опциональная интеграция AutoPublish для передачи в соцплатформы.
- Единый backend + Expo workflow с запуском через tmux-скрипты.

## 🗂️ Структура проекта

```text
LazyEdit/
├── app.py                           # Точка входа Tornado backend и оркестрация API
├── app/                             # Expo frontend (web/mobile)
├── lazyedit/                        # Основные модули пайплайна (перевод, метаданные, burner, DB, шаблоны)
├── agi/                             # Абстракция провайдеров генерации (маршруты Sora/Veo/A2E/Venice)
├── DATA/                            # Вход/выход runtime-медиа (symlink в этом workspace)
├── translation_logs/                # Логи перевода
├── temp/                            # Временные runtime-файлы
├── install_lazyedit.sh              # Инсталлятор systemd (ожидает config/start/stop скрипты)
├── start_lazyedit.sh                # tmux-лаунчер для backend + Expo
├── stop_lazyedit.sh                 # Помощник остановки tmux
├── lazyedit_config.sh               # Shell-конфигурация деплоя/runtime
├── config.py                        # Разрешение env/config (порты, пути, URL autopublish)
├── .env.example                     # Шаблон переопределений окружения
├── references/                      # Дополнительная документация (API guide, quickstart, deployment notes)
├── AutoPublish/                     # Submodule (опциональный пайплайн публикации)
├── AutoPubMonitor/                  # Submodule (автоматизация monitor/sync)
├── whisper_with_lang_detect/        # Submodule (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule (основной captioner)
├── clip-gpt-captioning/             # Submodule (резервный captioner)
└── furigana/                        # Внешняя зависимость в workflow (в этом checkout отслеживается как submodule)
```

## ✅ Предварительные требования

| Зависимость | Примечания |
| --- | --- |
| Linux-среда | Скрипты `systemd`/`tmux` ориентированы на Linux |
| Python 3.10+ | Используйте Conda env `lazyedit` |
| Node.js 20+ + npm | Требуется для Expo-приложения в `app/` |
| FFmpeg | Должен быть доступен в `PATH` |
| PostgreSQL | Локальная peer auth или подключение через DSN |
| Git submodules | Нужны для ключевых частей пайплайна |

## 🚀 Установка

1. Клонируйте репозиторий и инициализируйте submodules:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. Активируйте Conda-окружение:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. Опциональная системная установка (режим сервиса):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Примечания по установке сервиса:
- `install_lazyedit.sh` устанавливает `ffmpeg` и `tmux`, затем создаёт `lazyedit.service`.
- Он не генерирует `lazyedit_config.sh`, `start_lazyedit.sh` или `stop_lazyedit.sh`; эти файлы должны уже существовать и быть корректными.

## 🛠️ Использование

### Разработка: только backend

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

Альтернативная точка входа, используемая в текущих deployment-скриптах:

```bash
python app.py -m lazyedit
```

URL backend по умолчанию: `http://localhost:8787` (из `config.py`, можно переопределить через `PORT` или `LAZYEDIT_PORT`).

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

### Ключевые переменные

| Переменная | Назначение | Значение по умолчанию/резерв |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | Порт backend | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | Корневая директория медиа | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | Локальный DB fallback `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | Endpoint AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | Таймаут запроса AutoPublish (секунды) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | Путь к Whisper/VAD-скрипту | Зависит от окружения |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | Имена ASR-моделей | `large-v3` / `large-v2` (пример) |
| `LAZYEDIT_CAPTION_PYTHON` | Python runtime для пайплайна подписей | Зависит от окружения |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | Путь/скрипт основного captioning | Зависит от окружения |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | Путь/скрипт/cwd резервного captioning | Зависит от окружения |
| `GRSAI_API_*` | Настройки интеграции Veo/GRSAI | Зависит от окружения |
| `VENICE_*`, `A2E_*` | Настройки интеграции Venice/A2E | Зависит от окружения |
| `OPENAI_API_KEY` | Нужен для функций на базе OpenAI | Нет |

Примечания по machine-specific настройкам:
- `app.py` может задавать поведение CUDA (использование `CUDA_VISIBLE_DEVICES` в контексте кодовой базы).
- Некоторые пути в значениях по умолчанию завязаны на конкретную рабочую станцию; для переносимой конфигурации используйте переопределения в `.env`.
- `lazyedit_config.sh` управляет переменными запуска tmux/сессий для deployment-скриптов.

## 🔌 Примеры API

Примеры Base URL предполагают `http://localhost:8787`.

Загрузка:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

Сквозная обработка:

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

Больше endpoint'ов и деталей payload: `references/API_GUIDE.md`.

## 🧪 Примеры

### Локальный запуск frontend (web)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

Если backend работает на `8887`:

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

### Опциональный Sora helper для генерации

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

Поддерживаемая длительность (seconds): `4`, `8`, `12`.
Поддерживаемые размеры (sizes): `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Заметки для разработки

- Используйте `python` из Conda env `lazyedit` (не полагайтесь на системный `python3`).
- Не храните крупные медиафайлы в Git; размещайте runtime-медиа в `DATA/` или внешнем хранилище.
- Инициализируйте/обновляйте submodules, если компоненты пайплайна не находятся.
- Делайте изменения точечно; избегайте несвязанных массовых форматирований.
- Для frontend API URL backend задаётся через `EXPO_PUBLIC_API_URL`.
- Для разработки приложения на backend открыт CORS.

Политика submodule и внешних зависимостей:
- Считайте внешние зависимости проектами, которыми владеют upstream-авторы. В рамках этого репозитория избегайте правок внутри submodule, если вы не работаете в этих проектах целенаправленно.
- Операционные правила этого репозитория рассматривают `furigana` (а иногда и `echomind` в локальных конфигурациях) как пути внешних зависимостей; если есть сомнения, сохраняйте upstream-состояние и избегайте правок на месте.

Полезные материалы:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ Тестирование

Сейчас формальный набор тестов минимальный и в основном связан с БД.

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

Для функциональной проверки используйте web UI и API-поток с коротким sample-клипом в `DATA/`.

## 🚢 Заметки по деплою и синхронизации

Текущие известные пути и поток синхронизации (из операционной документации репозитория):

- Development workspace: `/home/lachlan/ProjectsLFS/LazyEdit`
- Deployed LazyEdit backend + app: `/home/lachlan/DiskMech/Projects/lazyedit`
- Deployed AutoPubMonitor: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- Publishing system host: `/home/lachlan/Projects/auto-publish` on `lazyingart`

После отправки обновлений `AutoPublish/` из этого репозитория выполните pull на publishing-host:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Устранение неполадок

| Проблема | Проверка / Решение |
| --- | --- |
| Отсутствуют модули/скрипты пайплайна | Выполните `git submodule update --init --recursive` |
| FFmpeg не найден | Установите FFmpeg и проверьте, что работает `ffmpeg -version` |
| Конфликт портов | Backend по умолчанию `8787`; `start_lazyedit.sh` по умолчанию `18787`; задайте `LAZYEDIT_PORT` или `PORT` явно |
| Expo не может подключиться к backend | Проверьте, что `EXPO_PUBLIC_API_URL` указывает на активный host/port backend |
| Проблемы с подключением к базе | Проверьте PostgreSQL + DSN/env vars; опциональная smoke-проверка: `python db_smoke_test.py` |
| Проблемы GPU/CUDA | Проверьте совместимость драйвера/CUDA с установленным стеком Torch |
| Ошибка service-скрипта при установке | Перед запуском инсталлятора убедитесь, что существуют `lazyedit_config.sh`, `start_lazyedit.sh` и `stop_lazyedit.sh` |

## 🗺️ Дорожная карта

- Редактирование субтитров/сегментов в приложении с A/B-превью и построчным управлением.
- Более сильное покрытие сквозными тестами для ключевых API-потоков.
- Сближение документации между i18n-вариантами README и режимами деплоя.
- Дополнительное усиление workflow для ретраев у провайдеров генерации и видимости статусов.

## 🤝 Вклад в проект

Вклад приветствуется.

1. Сделайте fork и создайте feature-ветку.
2. Держите коммиты сфокусированными и ограниченными по области изменений.
3. Проверьте изменения локально (`python app.py`, ключевой API-поток и интеграцию приложения, если применимо).
4. Откройте PR с целью, шагами воспроизведения и заметками до/после (для UI-изменений добавьте скриншоты).

Практические рекомендации:
- Следуйте стилю Python (PEP 8, 4 пробела, snake_case-именование).
- Не коммитьте учётные данные и крупные бинарные файлы.
- Обновляйте docs/config-скрипты при изменении поведения.
- Предпочтительный стиль коммита: коротко, в повелительном наклонении, с указанием области (например: `fix ffmpeg 7 compatibility`).

## ❤️ Что делает возможной ваша поддержка

- <b>Сохранять инструменты открытыми</b>: хостинг, инференс, хранение данных и поддержка сообщества.  
- <b>Выпускать быстрее</b>: недели сфокусированного open-source времени на EchoMind, LazyEdit и MultilingualWhisper.  
- <b>Прототипировать wearable-устройства</b>: оптика, сенсоры и нейроморфные/edge-компоненты для IdeasGlass + LightMind.  
- <b>Давать доступ всем</b>: субсидированные развёртывания для студентов, креаторов и сообществ.

### Donate

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

## 📄 Лицензия

[Apache-2.0](LICENSE)

## 🙏 Благодарности

LazyEdit опирается на open-source библиотеки и сервисы, включая:
- FFmpeg для обработки медиа
- Tornado для backend API
- MoviePy для workflow редактирования
- OpenAI models для задач AI-ассистированного пайплайна
- CJKWrap и многоязычные инструменты текста в workflow субтитров
