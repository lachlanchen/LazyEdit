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
  <b>سير عمل فيديو مدعوم بالذكاء الاصطناعي</b> للإنشاء، ومعالجة الترجمة، والبيانات الوصفية، والنشر الاختياري.
  <br />
  <sub>رفع أو توليد -> تفريغ -> ترجمة/تحسين -> حرق الترجمة -> تعليقات/إطارات مفتاحية -> بيانات وصفية -> نشر</sub>
</p>

# LazyEdit

LazyEdit هو سير عمل فيديو متكامل ومدعوم بالذكاء الاصطناعي للإنشاء والمعالجة والنشر الاختياري. يجمع بين التوليد المعتمد على المطالبات (Stage A/B/C)، وواجهات معالجة الوسائط، ورسم الترجمات على الفيديو، وتعليقات الإطارات المفتاحية، وتوليد البيانات الوصفية، والتسليم إلى AutoPublish.

| معلومة سريعة | القيمة |
| --- | --- |
| 📘 README المرجعي | `README.md` (هذا الملف) |
| 🌐 نسخ اللغات | `i18n/README.*.md` (يُحافَظ عمدًا على شريط لغات واحد في الأعلى) |
| 🧠 نقطة دخول الخلفية | `app.py` (Tornado) |
| 🖥️ تطبيق الواجهة | `app/` (Expo ويب/موبايل) |

## 🧭 المحتويات

- [Overview](#overview)
- [At a Glance](#at-a-glance)
- [Architecture Snapshot](#architecture-snapshot)
- [Demos](#demos)
- [Features](#features)
- [Documentation & i18n](#-documentation--i18n)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Cheat Sheet](#-command-cheat-sheet)
- [Usage](#usage)
- [Configuration](#configuration)
- [Configuration Files](#-configuration-files)
- [API Examples](#api-examples)
- [Examples](#examples)
- [Development Notes](#development-notes)
- [Testing](#testing)
- [Assumptions & Known Limits](#-assumptions--known-limits)
- [Deployment & Sync Notes](#deployment--sync-notes)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Support](#-support)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## ✨ Overview

تم بناء LazyEdit حول خلفية Tornado (`app.py`) وواجهة Expo (`app/`).

> ملاحظة: إذا اختلفت تفاصيل المستودع/التشغيل بين الأجهزة، فاحتفِظ بالإعدادات الافتراضية الحالية واستخدم متغيرات البيئة للتجاوز بدل حذف البدائل الخاصة بالجهاز.

| لماذا تستخدمه الفرق | النتيجة العملية |
| --- | --- |
| تدفق موحّد للمشغّل | رفع/توليد/ريمكس/نشر من سير عمل واحد |
| تصميم API-first | سهل للأتمتة والدمج مع أدوات أخرى |
| تشغيل محلي أولًا | يعمل مع أنماط نشر تعتمد على tmux والخدمات |

| الخطوة | ما الذي يحدث |
| --- | --- |
| 1 | رفع الفيديو أو توليده |
| 2 | تفريغ الكلام إلى نص مع ترجمة اختيارية للترجمة |
| 3 | حرق ترجمات متعددة اللغات مع عناصر تحكم في التنسيق |
| 4 | توليد إطارات مفتاحية وتعليقات وبيانات وصفية |
| 5 | تجهيز الحزمة ثم النشر اختياريًا عبر AutoPublish |

### تركيز خط المعالجة

- رفع، وتوليد، وريمكس، وإدارة مكتبة من واجهة تشغيل واحدة.
- تدفق معالجة API-first للتفريغ، وتحسين/ترجمة الترجمة، والحرق داخل الفيديو، والبيانات الوصفية.
- تكاملات اختيارية لمزوّدي التوليد (Veo / Venice / A2E / Sora helpers في `agi/`).
- تسليم نشر اختياري عبر `AutoPublish`.

## 🎯 At a Glance

| المجال | ما يتضمنه LazyEdit | الحالة |
| --- | --- | --- |
| التطبيق الأساسي | خلفية API بـ Tornado + واجهة Expo ويب/موبايل | ✅ |
| خط الوسائط | ASR، ترجمة/تحسين الترجمة، حرق داخل الفيديو، إطارات مفتاحية، تعليقات، بيانات وصفية | ✅ |
| التوليد | Stage A/B/C ومسارات مساعد المزوّد (`agi/`) | ✅ |
| التوزيع | تسليم اختياري إلى AutoPublish | 🟡 اختياري |
| نموذج التشغيل | سكربتات محلية أولًا، سير عمل tmux، وخدمة systemd اختيارية | ✅ |

## 🏗️ Architecture Snapshot

يُنظَّم المستودع كخط وسائط API-first مع طبقة واجهة:

- `app.py` هو نقطة دخول Tornado ومنسّق المسارات للرفع والمعالجة والتوليد والتسليم للنشر وتقديم الوسائط.
- `lazyedit/` يحتوي على وحدات معيارية لخط المعالجة (حفظ قاعدة البيانات، الترجمة، حرق الترجمة، التعليقات، البيانات الوصفية، موائمات المزوّدين).
- `app/` تطبيق Expo Router (ويب/موبايل) يدير تدفقات الرفع والمعالجة والمعاينة والنشر.
- `config.py` يركّز تحميل البيئة ومسارات التشغيل الافتراضية/الاحتياطية.
- `start_lazyedit.sh` و`lazyedit_config.sh` يوفّران أوضاع تشغيل محلية/منشورة قابلة لإعادة الإنتاج عبر tmux.

| الطبقة | المسارات الرئيسية | المسؤولية |
| --- | --- | --- |
| API والتنظيم | `app.py`, `config.py` | نقاط النهاية، التوجيه، حل متغيرات البيئة |
| نواة المعالجة | `lazyedit/`, `agi/` | خط الترجمة/التعليقات/البيانات الوصفية + المزوّدون |
| الواجهة | `app/` | تجربة المشغّل (ويب/موبايل عبر Expo) |
| سكربتات التشغيل | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | بدء محلي/خدمي وعمليات التشغيل |

التدفق عالي المستوى:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

## 🎬 Demos

الصور أدناه تعرض المسار الرئيسي للمشغّل من الإدخال وحتى توليد البيانات الوصفية.

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

## 🧩 Features

- ✨ سير عمل توليد مبني على المطالبات (Stage A/B/C) مع مسارات تكامل Sora وVeo.
- 🧵 خط معالجة كامل: تفريغ -> تحسين/ترجمة الترجمة -> حرق داخل الفيديو -> إطارات مفتاحية -> تعليقات -> بيانات وصفية.
- 🌏 تركيب ترجمة متعددة اللغات مع مسارات دعم مرتبطة بـ furigana/IPA/romaji.
- 🔌 خلفية API-first مع نقاط نهاية للرفع والمعالجة وتقديم الوسائط وصفوف النشر.
- 🚚 تكامل اختياري مع AutoPublish للتسليم إلى المنصات الاجتماعية.
- 🖥️ سير عمل موحّد للخلفية + Expo ومدعوم عبر سكربتات تشغيل tmux.

## 🌍 Documentation & i18n

يحافظ LazyEdit على README إنجليزي مرجعي واحد (`README.md`) ونسخ لغوية في `i18n/`.

- المصدر المرجعي: `README.md`
- نسخ اللغات: `i18n/README.*.md`
- شريط اللغات: احتفظ بسطر خيارات لغة واحد فقط أعلى كل README (بدون تكرار أشرطة اللغات)

إذا حدث أي تعارض بين الترجمات والوثائق الإنجليزية، فاعتبر README الإنجليزي هذا هو مصدر الحقيقة، ثم حدّث كل ملف لغة واحدًا تلو الآخر.

| سياسة i18n | القاعدة |
| --- | --- |
| المصدر المرجعي | `README.md` يظل مصدر الحقيقة |
| شريط اللغة | سطر خيارات لغة واحد تمامًا في الأعلى |
| ترتيب التحديث | الإنجليزية أولًا، ثم كل `i18n/README.*.md` واحدًا تلو الآخر |

## 🗂️ Project Structure

```text
LazyEdit/
├── app.py                           # Tornado backend entrypoint and API orchestration
├── app/                             # Expo frontend (web/mobile)
├── lazyedit/                        # Core pipeline modules (translation, metadata, burner, DB, templates)
├── agi/                             # Generation provider abstraction (Sora/Veo/A2E/Venice routes)
├── DATA/                            # Runtime media input/output (symlink in this workspace)
├── translation_logs/                # Translation logs
├── temp/                            # Temporary runtime files
├── install_lazyedit.sh              # systemd installer (expects config/start/stop scripts)
├── start_lazyedit.sh                # tmux launcher for backend + Expo
├── stop_lazyedit.sh                 # tmux stop helper
├── lazyedit_config.sh               # Deployment/runtime shell config
├── config.py                        # Environment/config resolution (ports, paths, autopublish URL)
├── .env.example                     # Environment override template
├── references/                      # Additional docs (API guide, quickstart, deployment notes)
├── AutoPublish/                     # Submodule (optional publishing pipeline)
├── AutoPubMonitor/                  # Submodule (monitor/sync automation)
├── whisper_with_lang_detect/        # Submodule (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule (primary captioner)
├── clip-gpt-captioning/             # Submodule (fallback captioner)
└── furigana/                        # External dependency in workflow (tracked submodule in this checkout)
```

ملاحظة حول الوحدات الفرعية/الاعتماديات الخارجية:
- تتضمن وحدات Git الفرعية في هذا المستودع `AutoPublish` و`AutoPubMonitor` و`whisper_with_lang_detect` و`vit-gpt2-image-captioning` و`clip-gpt-captioning` و`furigana`.
- تتعامل الإرشادات التشغيلية مع `furigana` و`echomind` كاعتماديات خارجية/للقراءة فقط في سير عمل هذا المستودع. عند الشك، حافظ على المصدر upstream وتجنب التعديل المباشر.

## ✅ Prerequisites

| الاعتمادية | ملاحظات |
| --- | --- |
| بيئة Linux | سكربتات `systemd`/`tmux` موجّهة للينكس |
| Python 3.10+ | استخدم بيئة Conda باسم `lazyedit` |
| Node.js 20+ + npm | مطلوب لتطبيق Expo في `app/` |
| FFmpeg | يجب أن يكون متاحًا على `PATH` |
| PostgreSQL | توثيق peer محلي أو اتصال عبر DSN |
| Git submodules | مطلوبة لخطوط المعالجة الأساسية |

## 🚀 Installation

1. استنسخ المستودع وهيّئ الوحدات الفرعية:

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. فعّل بيئة Conda:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. تثبيت اختياري على مستوى النظام (وضع الخدمة):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

ملاحظات تثبيت الخدمة:
- `install_lazyedit.sh` يثبت `ffmpeg` و`tmux` ثم ينشئ `lazyedit.service`.
- لا ينشئ `lazyedit_config.sh` أو `start_lazyedit.sh` أو `stop_lazyedit.sh`؛ يجب أن تكون موجودة وصحيحة مسبقًا.

## ⚡ Quick Start

تشغيل محلي للخلفية + الواجهة (المسار الأدنى):

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

في نافذة طرفية ثانية:

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

تهيئة محلية اختيارية سريعة لقاعدة البيانات:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### Runtime profiles

| الملف التشغيلي | أمر البدء | الخلفية الافتراضية | الواجهة الافتراضية |
| --- | --- | --- | --- |
| تطوير محلي (يدوي) | `python app.py` + أمر Expo | `8787` | `8091` (مثال أمر) |
| مُدار عبر tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| خدمة systemd | `sudo systemctl start lazyedit.service` | حسب config/env | N/A |

## 🧭 Command Cheat Sheet

| المهمة | الأمر |
| --- | --- |
| تهيئة الوحدات الفرعية | `git submodule update --init --recursive` |
| تشغيل الخلفية فقط | `python app.py` |
| تشغيل الخلفية + Expo (tmux) | `./start_lazyedit.sh` |
| إيقاف تشغيل tmux | `./stop_lazyedit.sh` |
| فتح جلسة tmux | `tmux attach -t lazyedit` |
| حالة الخدمة | `sudo systemctl status lazyedit.service` |
| سجلات الخدمة | `sudo journalctl -u lazyedit.service` |
| اختبار DB سريع | `python db_smoke_test.py` |
| اختبار Pytest سريع | `pytest tests/test_db_smoke.py` |

## 🛠️ Usage

### التطوير: الخلفية فقط

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

مدخل بديل مستخدم في سكربتات النشر الحالية:

```bash
python app.py -m lazyedit
```

رابط الخلفية الافتراضي: `http://localhost:8787` (من `config.py`، مع إمكانية التجاوز عبر `PORT` أو `LAZYEDIT_PORT`).

### التطوير: الخلفية + تطبيق Expo (tmux)

```bash
./start_lazyedit.sh
```

المنافذ الافتراضية في `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

الاتصال بالجلسة:

```bash
tmux attach -t lazyedit
```

إيقاف الجلسة:

```bash
./stop_lazyedit.sh
```

### Service management

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ Configuration

انسخ `.env.example` إلى `.env` وحدّث المسارات/الأسرار:

```bash
cp .env.example .env
```

ملاحظة أسبقية الإعدادات:

- يقوم `config.py` بتحميل قيم `.env` عند وجودها، ويضبط فقط المفاتيح غير المصدّرة مسبقًا في الصدفة.
- لذلك قد تأتي قيم وقت التشغيل من: متغيرات بيئة مصدّرة في الصدفة -> `.env` -> القيم الافتراضية في الكود.
- في تشغيل tmux/service، يتحكم `lazyedit_config.sh` في معلمات البدء/الجلسة (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, والمنافذ عبر متغيرات بيئة سكربت البدء).

### المتغيرات الأساسية

| المتغير | الغرض | الافتراضي/الاحتياطي |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | منفذ الخلفية | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | مجلد الوسائط الجذري | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | احتياطي DB محلي `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | نقطة نهاية AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | مهلة طلب AutoPublish (بالثواني) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | مسار سكربت Whisper/VAD | يعتمد على البيئة |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | أسماء نماذج ASR | `large-v3` / `large-v2` (مثال) |
| `LAZYEDIT_CAPTION_PYTHON` | Python runtime لخط التعليقات | يعتمد على البيئة |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | المسار/السكربت الأساسي للتعليقات | يعتمد على البيئة |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | مسار/سكربت/cwd احتياطي للتعليقات | يعتمد على البيئة |
| `GRSAI_API_*` | إعدادات تكامل Veo/GRSAI | يعتمد على البيئة |
| `VENICE_*`, `A2E_*` | إعدادات تكامل Venice/A2E | يعتمد على البيئة |
| `OPENAI_API_KEY` | مطلوب لميزات تعتمد على OpenAI | لا يوجد |

ملاحظات خاصة بالجهاز:
- قد يضبط `app.py` سلوك CUDA (استخدام `CUDA_VISIBLE_DEVICES` ضمن سياق هذا الكود).
- بعض المسارات الافتراضية خاصة بمحطات عمل محددة؛ استخدم تجاوزات `.env` لإعدادات قابلة للنقل.
- يتحكم `lazyedit_config.sh` في متغيرات بدء tmux/session ضمن سكربتات النشر.

## 🧾 Configuration Files

| الملف | الغرض |
| --- | --- |
| `.env.example` | قالب لمتغيرات البيئة المستخدمة بواسطة الخلفية/الخدمات |
| `.env` | تجاوزات محلية للجهاز؛ يحمّلها `config.py`/`app.py` عند وجودها |
| `config.py` | القيم الافتراضية في الخلفية وحل متغيرات البيئة |
| `lazyedit_config.sh` | ملف تشغيل tmux/service (مسار النشر، بيئة conda، وسائط التطبيق، اسم الجلسة) |
| `start_lazyedit.sh` | يشغّل الخلفية + Expo عبر tmux بالمنافذ المحددة |
| `install_lazyedit.sh` | ينشئ `lazyedit.service` ويتحقق من السكربتات/الإعدادات الموجودة |

الترتيب المقترح للتحديث من أجل قابلية النقل بين الأجهزة:
1. انسخ `.env.example` إلى `.env`.
2. اضبط قيم `LAZYEDIT_*` المتعلقة بالمسارات وواجهات API في `.env`.
3. عدّل `lazyedit_config.sh` فقط لسلوك النشر عبر tmux/service.

## 🔌 API Examples

أمثلة Base URL تفترض `http://localhost:8787`.

| مجموعة API | نقاط نهاية تمثيلية |
| --- | --- |
| الرفع والوسائط | `/upload`, `/upload-stream`, `/media/*` |
| سجلات الفيديو | `/api/videos`, `/api/videos/{id}` |
| المعالجة | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| النشر | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| التوليد | `/api/videos/generate` (+ مسارات المزوّد في `app.py`) |

رفع ملف:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

معالجة كاملة end-to-end:

```bash
curl -X POST \
  -d "file_path=/abs/path/to/DATA/my_video/video.mp4" \
  -d "use_translation_cache=true" \
  -d "use_metadata_cache=true" \
  http://localhost:8787/video-processing
```

عرض قائمة الفيديوهات:

```bash
curl http://localhost:8787/api/videos
```

حزمة نشر:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

لمزيد من نقاط النهاية وتفاصيل payload: `references/API_GUIDE.md`.

مجموعات نقاط نهاية مرتبطة غالبًا بالاستخدام:
- دورة حياة الفيديو: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- إجراءات المعالجة: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- مسارات التوليد/المزوّد: `/api/videos/generate` بالإضافة إلى مسارات Venice/A2E المكشوفة في `app.py`
- التوزيع: `/api/videos/{id}/publish`, `/api/autopublish/queue`

## 🧪 Examples

### تشغيل الواجهة محليًا (ويب)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

إذا كانت الخلفية على `8887`:

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

### مساعد توليد Sora اختياري

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

الثواني المدعومة: `4`, `8`, `12`.
الأحجام المدعومة: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 Development Notes

- استخدم `python` من بيئة Conda `lazyedit` (ولا تفترض `python3` الخاص بالنظام).
- أبقِ ملفات الوسائط الكبيرة خارج Git؛ خزّن الوسائط التشغيلية في `DATA/` أو في تخزين خارجي.
- هيّئ/حدّث الوحدات الفرعية كلما تعذّر حل مكونات خط المعالجة.
- اجعل التعديلات محددة النطاق؛ وتجنّب تغييرات التنسيق الواسعة غير المرتبطة.
- في أعمال الواجهة، يتحكم `EXPO_PUBLIC_API_URL` بعنوان API الخلفي.
- إعداد CORS في الخلفية مفتوح لتطوير التطبيق.

سياسة الوحدات الفرعية والاعتماديات الخارجية:
- تُعامل الاعتماديات الخارجية كملكيات upstream. في سير عمل هذا المستودع، تجنّب تعديل تفاصيل الوحدات الفرعية إلا إذا كنت تعمل عليها عمدًا.
- تعتبر الإرشادات التشغيلية هنا `furigana` (وأحيانًا `echomind` في الإعدادات المحلية) مسارات اعتماديات خارجية؛ وعند الشك حافظ على المصدر upstream وتجنب التعديل المباشر.

مراجع مفيدة:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

نظافة الأمان/الإعداد:
- احتفظ بمفاتيح API والأسرار في متغيرات البيئة؛ ولا ترفع بيانات اعتماد إلى المستودع.
- يفضّل استخدام `.env` لتجاوزات الجهاز المحلي مع إبقاء `.env.example` كقالب عام.
- إذا اختلف سلوك CUDA/GPU حسب الجهاز، فاستخدم متغيرات البيئة بدل التثبيت الصلب لقيم خاصة بجهاز بعينه.

## ✅ Testing

سطح الاختبارات الرسمي الحالي محدود ويركّز على قاعدة البيانات.

| طبقة التحقق | الأمر أو الطريقة |
| --- | --- |
| اختبار DB سريع | `python db_smoke_test.py` |
| فحص Pytest لقاعدة البيانات | `pytest tests/test_db_smoke.py` |
| التدفق الوظيفي | واجهة الويب + API باستخدام عينة قصيرة في `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

للتحقق الوظيفي، استخدم واجهة الويب وتدفق API مع مقطع عينة قصير في `DATA/`.

افتراضات وملاحظات قابلية النقل:
- بعض المسارات الافتراضية في الكود بدائل خاصة بمحطات عمل معينة؛ وهذا متوقع في الحالة الحالية للمستودع.
- إذا لم يكن مسار افتراضي موجودًا على جهازك، اضبط متغير `LAZYEDIT_*` المقابل في `.env`.
- عند الشك في قيمة خاصة بجهاز، احتفظ بالإعدادات الحالية وأضف تجاوزات صريحة بدل حذف القيم الافتراضية.

## 🧱 Assumptions & Known Limits

- مجموعة اعتماديات الخلفية غير مثبتة عبر lockfile جذري؛ لذا تعتمد قابلية إعادة إنتاج البيئة حاليًا على الانضباط في الإعداد المحلي.
- `app.py` أحادي (monolithic) عمدًا في الحالة الحالية للمستودع ويحتوي على مساحة كبيرة من المسارات.
- معظم التحقق من خط المعالجة تكاملي/يدوي (UI + API + وسائط عينة)، مع اختبارات آلية رسمية محدودة.
- مجلدات التشغيل (`DATA/`, `temp/`, `translation_logs/`) هي مخرجات تشغيلية وقد تنمو بشكل كبير.
- الوحدات الفرعية مطلوبة للوظائف الكاملة؛ والاكتفاء بجلب جزئي غالبًا يؤدي إلى أخطاء سكربتات مفقودة.

## 🚢 Deployment & Sync Notes

المسارات المعروفة حاليًا وتدفق المزامنة (بحسب وثائق عمليات المستودع):

- مساحة التطوير: `/home/lachlan/ProjectsLFS/LazyEdit`
- LazyEdit المنشور (الخلفية + التطبيق): `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor المنشور: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- مضيف نظام النشر: `/home/lachlan/Projects/auto-publish` على `lazyingart`

| البيئة | المسار | ملاحظات |
| --- | --- | --- |
| مساحة التطوير | `/home/lachlan/ProjectsLFS/LazyEdit` | المصدر الرئيسي + submodules |
| LazyEdit المنشور | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` في وثائق التشغيل |
| AutoPubMonitor المنشور | `/home/lachlan/DiskMech/Projects/autopub-monitor` | جلسات monitor/sync/process |
| مضيف النشر | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | اسحب بعد تحديثات submodule |

بعد دفع تحديثات `AutoPublish/` من هذا المستودع، اسحبها على مضيف النشر:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 Troubleshooting

| المشكلة | الفحص / الحل |
| --- | --- |
| وحدات أو سكربتات خط معالجة مفقودة | شغّل `git submodule update --init --recursive` |
| FFmpeg غير موجود | ثبّت FFmpeg وتأكد أن `ffmpeg -version` يعمل |
| تعارض منافذ | الخلفية افتراضيًا `8787`؛ و`start_lazyedit.sh` افتراضيًا `18787`؛ اضبط `LAZYEDIT_PORT` أو `PORT` صراحة |
| Expo لا يستطيع الوصول للخلفية | تأكد أن `EXPO_PUBLIC_API_URL` يشير إلى المضيف/المنفذ النشطين |
| مشاكل اتصال قاعدة البيانات | تحقق من PostgreSQL + DSN/env vars؛ فحص اختياري: `python db_smoke_test.py` |
| مشاكل GPU/CUDA | تحقق من توافق التعريف/CUDA مع حزمة Torch المثبتة |
| فشل سكربت الخدمة أثناء التثبيت | تأكد من وجود `lazyedit_config.sh` و`start_lazyedit.sh` و`stop_lazyedit.sh` قبل تشغيل المُثبّت |

## 🗺️ Roadmap

- تحرير الترجمة/المقاطع داخل التطبيق مع معاينة A/B وتحكم لكل سطر.
- تغطية اختبار end-to-end أقوى لتدفقات API الأساسية.
- توحيد التوثيق عبر نسخ README متعددة اللغات وأوضاع النشر.
- تعزيز متانة سير العمل لإعادة محاولات مزوّدي التوليد وإظهار الحالة.

## 🤝 Contributing

المساهمات مرحّب بها.

1. قم بعمل Fork وأنشئ فرع ميزة.
2. اجعل الالتزامات مركزة ومحددة.
3. تحقّق من التغييرات محليًا (`python app.py`، تدفق API الأساسي، وتكامل التطبيق عند الحاجة).
4. افتح PR يتضمن الهدف وخطوات إعادة الإنتاج وملاحظات قبل/بعد (مع لقطات شاشة لتغييرات الواجهة).

إرشادات عملية:
- التزم بأسلوب Python (PEP 8، 4 مسافات، أسماء snake_case).
- تجنب رفع بيانات اعتماد أو ملفات ثنائية كبيرة.
- حدّث التوثيق/سكربتات الإعداد عند تغيّر السلوك.
- أسلوب الالتزام المفضّل: قصير، بصيغة الأمر، ومحدّد النطاق (مثل: `fix ffmpeg 7 compatibility`).

## ❤️ Support

| Donate | PayPal | Stripe |
|---|---|---|
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=ko-fi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

## 📄 License

[Apache-2.0](LICENSE)

## 🙏 Acknowledgements

يعتمد LazyEdit على مكتبات وخدمات مفتوحة المصدر، بما في ذلك:
- FFmpeg لمعالجة الوسائط
- Tornado لواجهات API الخلفية
- MoviePy لسير عمل التحرير
- نماذج OpenAI لمهام خط المعالجة المدعوم بالذكاء الاصطناعي
- CJKWrap وأدوات النصوص متعددة اللغات ضمن سير عمل الترجمة
