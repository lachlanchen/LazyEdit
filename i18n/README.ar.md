[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)




[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

<p align="center">
  <b>سير عمل فيديو مدعوم بالذكاء الاصطناعي</b> للتوليد، ومعالجة الترجمات، والبيانات الوصفية، والنشر الاختياري.
  <br />
  <sub>رفع أو توليد -> تفريغ -> ترجمة/تحسين -> حرق الترجمة -> تعليقات/إطارات مفتاحية -> بيانات وصفية -> نشر</sub>
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

<a id="top"></a>
# LazyEdit

<a id="-overview"></a>
## ✅ حقائق سريعة

لـLazyEdit سير عمل فيديو شامل مدعوم بالذكاء الاصطناعي للإنشاء والمعالجة والنشر الاختياري. يجمع بين التوليد المبني على المطالبات (Stage A/B/C)، وواجهات معالجة الوسائط، وعرض الترجمات على الفيديو، وتعليقات الإطارات المفتاحية، وتوليد البيانات الوصفية، وتسليم المهمة إلى AutoPublish.

| المعلومة السريعة | القيمة |
| --- | --- |
| 📘 README الأساسي | `README.md` (هذا الملف) |
| 🌐 إصدارات اللغات | `i18n/README.*.md` (يُحافَظ عمدًا على شريط لغات واحد في الأعلى) |
| 🧠 نقطة دخول الخلفية | `app.py` (Tornado) |
| 🖥️ تطبيق الواجهة | `app/` (Expo ويب/موبايل) |

<a id="overview"></a>
## ✨ نبذة عامة

LazyEdit مبني حول خلفية Tornado (`app.py`) وواجهة Expo (`app/`).

> ملاحظة: إذا اختلفت تفاصيل المستودع/بيئة التشغيل باختلاف الجهاز، احتفظ بالإعدادات الافتراضية الحالية واستخدم متغيرات البيئة للتجاوز بدل حذف البدائل المخصصة للجهاز.

| لماذا يستخدمه الفريق | النتيجة العملية |
| --- | --- |
| تدفق موحّد للمشغّل | رفع/توليد/إعادة مزج/نشر من سير عمل واحد |
| تصميم API-first | سهولة كتابة السكربتات والتكامل مع أدوات أخرى |
| تشغيل محلي أولًا | يعمل مع أنماط tmux والتشغيل عبر الخدمات |

| الخطوة | ما يحدث |
| --- | --- |
| 1 | رفع الفيديو أو توليده |
| 2 | تفريغ النصوص وترجمة الترجمات اختياريًا |
| 3 | حرق ترجمات متعددة اللغات مع عناصر التحكم في التخطيط |
| 4 | توليد إطارات مفتاحية وتعليقات وبيانات وصفية |
| 5 | تجميع الحزمة ونشرها اختياريًا عبر AutoPublish |

### تركيز خط الأنابيب

- رفع وتوليد وإعادة مزج وإدارة مكتبة الفيديو من واجهة تشغيل واحدة.
- تدفق معالجة أولية قائم على API للتفريغ، تنقيح/ترجمة الترجمات، حرق النص، والبيانات الوصفية.
- تكاملات اختيارية لمزودي التوليد (helpers لـ Veo / Venice / A2E / Sora في `agi/`).
- تحويل النشر الاختياري عبر `AutoPublish`.

<a id="at-a-glance"></a>
## 🎯 لمحة سريعة

| المجال | مضمَّن في LazyEdit | الحالة |
| --- | --- | --- |
| التطبيق الأساسي | واجهة API بـ Tornado + واجهة Expo ويب/موبايل | ✅ |
| خط الوسائط | ASR، ترجمة/تنقيح الترجمة، حرق الترجمات، إطارات مفتاحية، تعليقات، بيانات وصفية | ✅ |
| التوليد | Stage A/B/C ومسارات مزوّد (`agi/`) | ✅ |
| التوزيع | تحويل لـ AutoPublish اختياري | 🟡 اختياري |
| نموذج التشغيل | سكربتات محلية أولًا، تدفقات tmux، خدمة systemd اختيارية | ✅ |

<a id="architecture-snapshot"></a>
## 🏗️ لقطة معمارية

المستودع منظَّم كسلسلة وسائط تعتمد على API مع طبقة واجهة مستخدم:

- `app.py` هو مدخل Tornado ومنسق المسارات لعمليات الرفع، المعالجة، التوليد، تحويل النشر، وتقديم الوسائط.
- `lazyedit/` يحتوي على مكوّنات خط المعالجة بنمط وحدات (استمرارية DB، ترجمة، حرق الترجمات، التعليقات، البيانات الوصفية، ومحولات المزودين).
- `app/` هو تطبيق Expo Router (ويب/موبايل) يدير مسارات الرفع والمعالجة والمعاينة والنشر.
- `config.py` يجمع تحميل المتغيرات البيئية والمسارات الافتراضية/الاحتياطية.
- `start_lazyedit.sh` و`lazyedit_config.sh` يوفران أنماط تشغيل محلي/نشر قابلة لإعادة الإنتاج عبر tmux.

| الطبقة | المسارات الرئيسية | المسؤولية |
| --- | --- | --- |
| API والتنسيق | `app.py`, `config.py` | نقاط النهاية، التوجيه، حل المتغيرات البيئية |
| نواة المعالجة | `lazyedit/`, `agi/` | سلسلة الترجمات/التعليقات/البيانات الوصفية + مزودات الحزمة |
| الواجهة | `app/` | تجربة المشغّل (ويب/موبايل عبر Expo) |
| سكربتات التشغيل | `start_lazyedit.sh`, `lazyedit_config.sh`, `install_lazyedit.sh` | تشغيل محلي وخدمي/إجراءات صيانة |

تدفّق عالي المستوى:

`Upload/Generate -> Transcribe -> Translate/Polish -> Burn Subtitles -> Keyframes/Captions -> Metadata -> Optional AutoPublish`

<a id="demos"></a>
## 🎬 العروض التوضيحية

العرض أدناه يبين المسار الأساسي للمشغّل من الاستقبال إلى إنشاء البيانات الوصفية.

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>الصفحة الرئيسية · رفع</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>الصفحة الرئيسية · توليد</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>الصفحة الرئيسية · إعادة مزج</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>المكتبة</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>نظرة عامة على الفيديو</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>معاينة الترجمة</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>مواضع الحرق</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>تخطيط الحرق</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>الإطارات المفتاحية + التعليقات</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>مولّد البيانات الوصفية</sub>
    </td>
  </tr>
</table>

<a id="features"></a>
## 🧩 المميزات

- ✨ سير عمل التوليد المعتمد على المطالبات (Stage A/B/C) مع مسارات دمج Sora وVeo.
- 🧵 سلسلة معالجة كاملة: تفريغ -> تنقيح/ترجمة الترجمات -> حرق -> إطارات مفتاحية -> تعليقات -> بيانات وصفية.
- 🌏 تأليف ترجمات متعددة اللغات مع مسارات دعم ذات صلة بـ furigana/IPA/romaji.
- 🔌 واجهة backend أولى في API تشمل رفعًا، معالجة، تقديم وسائط، وطوابير نشر.
- 🚚 تكامل AutoPublish اختياري لتحويل العمل إلى منصات اجتماعية.
- 🖥️ تدفق backend + Expo يعمل مع سكربتات تشغيل tmux.

<a id="-documentation--i18n"></a>
## 🌍 التوثيق و i18n

- المصدر الرسمي: `README.md`
- إصدارات اللغات: `i18n/README.*.md`
- شريط اللغات: احرص على وجود سطر واحد فقط لشريط اختيار اللغة أعلى كل README (لا تكرارات)

إذا وُجد أي اختلاف بين الترجمة والإنجليزية، اعتبر `README.md` هو المصدر الرسمي، ثم حدّث كل ملف لغة على حدة.

| سياسة i18n | القاعدة |
| --- | --- |
| المصدر الرسمي | الحفاظ على `README.md` كمصدر للحقيقة |
| شريط اللغات | سطر واحد فقط لاختيارات اللغة |

<a id="project-structure"></a>
## 🗂️ بنية المشروع

```text
LazyEdit/
├── app.py                           # مدخل backend لـ Tornado وتنظيم API
├── app/                             # واجهة Expo (ويب/موبايل)
├── lazyedit/                        # وحدات خط المعالجة (ترجمة، بيانات وصفية، burn، DB، قوالب)
├── agi/                             # تجريد مزودي التوليد (مسارات Sora/Veo/A2E/Venice)
├── DATA/                            # مخرجات/مدخلات الوسائط وقت التشغيل (symlink ضمن workspace)
├── translation_logs/                # سجلات الترجمة
├── temp/                            # ملفات زمنية أثناء التشغيل
├── install_lazyedit.sh              # مثبت systemd (يتوقع وجود سكربتات config/start/stop)
├── start_lazyedit.sh                # مُشغّل tmux لـ backend + Expo
├── stop_lazyedit.sh                 # مساعد إيقاف tmux
├── lazyedit_config.sh               # إعدادات shell للتشغيل/النشر
├── config.py                        # حل المتغيرات والبيئة (منافذ، مسارات، رابط autopublish)
├── .env.example                     # قالب تجاوز البيئة
├── references/                      # وثائق إضافية (دليل API، البدء السريع، ملاحظات النشر)
├── AutoPublish/                     # Submodule فرعي (pipeline نشر اختياري)
├── AutoPubMonitor/                  # Submodule فرعي (مراقبة/مزامنة تلقائية)
├── whisper_with_lang_detect/        # Submodule فرعي (ASR/VAD)
├── vit-gpt2-image-captioning/       # Submodule فرعي (مولّد التعليقات الرئيسي)
├── clip-gpt-captioning/             # Submodule فرعي (مولّد تعليقات احتياطي)
└── furigana/                        # اعتماد خارجي في سير العمل (submodule متتبع في هذا checkout)
```

ملاحظة حول submodules/اعتمادات خارجية:
- تشمل Git submodules في هذا المستودع: `AutoPublish`, `AutoPubMonitor`, `whisper_with_lang_detect`, `vit-gpt2-image-captioning`, `clip-gpt-captioning`, و`furigana`.
- التوجيه التشغيلي يعامل `furigana` و`echomind` كاعتماد خارجي/قراءة فقط في سير عمل هذا المستودع. إذا كان هناك شك، احتفظ بالإصدار الأصلي وامتنع عن التعديل داخل مكانه.

<a id="prerequisites"></a>
## ✅ المتطلبات المسبقة

| الاعتماد | ملاحظات |
| --- | --- |
| بيئة Linux | سكربتات `systemd`/`tmux` مصممة لبيئة Linux |
| Python 3.10+ | استخدم بيئة Conda `lazyedit` |
| Node.js 20+ + npm | مطلوب لتشغيل تطبيق `app/` |
| FFmpeg | يجب أن يكون متاحًا في `PATH` |
| PostgreSQL | اتصال محلي peer auth أو DSN |
| Git submodules | مطلوبة للمهام الرئيسية |

<a id="installation"></a>
## 🚀 التثبيت

1. استنساخ وتهيئة submodules:

```bash
 git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive
```

2. تفعيل بيئة Conda:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
```

3. تثبيت اختياري على مستوى النظام (وضع الخدمة):

```bash
chmod +x install_lazyedit.sh
sudo ./install_lazyedit.sh /path/to/lazyedit
```

ملاحظات التثبيت الخدمي:
- `install_lazyedit.sh` يثبت `ffmpeg` و`tmux`، ثم ينشئ `lazyedit.service`.
- لا يولّد `lazyedit_config.sh` أو `start_lazyedit.sh` أو `stop_lazyedit.sh`؛ يجب أن تكون موجودة وصحيحة مسبقًا.

<a id="quick-start"></a>
## ⚡ البدء السريع

تشغيل backend + frontend محليًا (المسار المبسط):

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

إعداد قاعدة بيانات محلية اختياري:

```bash
createdb lazyedit_db || true
psql -d lazyedit_db -tAc "SELECT 'ok'"
```

### ملفات الملفّات التنفيذية

| الملف | أمر البدء | backend الافتراضي | frontend الافتراضي |
| --- | --- | --- | --- |
| تطوير محلي (يدوي) | `python app.py` + أمر Expo | `8787` | `8091` (مثال أمر) |
| Orchestrated بـ tmux | `./start_lazyedit.sh` | `18787` | `18791` |
| خدمة systemd | `sudo systemctl start lazyedit.service` | بناءً على config/env | غير متاح |

<a id="-command-cheat-sheet"></a>
## 🧭 دليل الأوامر السريع

| المهمة | الأمر |
| --- | --- |
| تهيئة submodules | `git submodule update --init --recursive` |
| تشغيل backend فقط | `python app.py` |
| تشغيل backend + Expo عبر tmux | `./start_lazyedit.sh` |
| إيقاف تشغيل tmux | `./stop_lazyedit.sh` |
| فتح جلسة tmux | `tmux attach -t lazyedit` |
| حالة الخدمة | `sudo systemctl status lazyedit.service` |
| سجلات الخدمة | `sudo journalctl -u lazyedit.service` |
| فحص DB | `python db_smoke_test.py` |
| فحص Pytest | `pytest tests/test_db_smoke.py` |

<a id="usage"></a>
## 🛠️ طريقة الاستخدام

### تطوير: backend فقط

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

أمر بديل مستخدم في سكربتات النشر الحالية:

```bash
python app.py -m lazyedit
```

رابط backend الافتراضي: `http://localhost:8787` (من `config.py`، ويمكن تجاوزه بـ `PORT` أو `LAZYEDIT_PORT`).

### تطوير: backend + Expo app (tmux)

```bash
./start_lazyedit.sh
```

المنافذ الافتراضية لـ `start_lazyedit.sh`:
- Backend: `18787`
- Expo web: `18791`
- `EXPO_PUBLIC_API_URL=http://localhost:18787`

الانضمام للجلسة:

```bash
tmux attach -t lazyedit
```

إيقاف الجلسة:

```bash
./stop_lazyedit.sh
```

### إدارة الخدمة

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

<a id="configuration"></a>
## ⚙️ الإعدادات

انسخ `.env.example` إلى `.env` وحدث المسارات/الأسرار:

```bash
cp .env.example .env
```

ملاحظات الأولوية للإعدادات:

- `config.py` يحمل قيم `.env` إذا وجدت ويملأ فقط المفاتيح غير المصدّرة حاليًا من الشل.
- القيم الفعلية أثناء التشغيل قد تأتي من: متغيرات البيئة المصدرة في الشل -> `.env` -> القيم الافتراضية في الكود.
- لعمليات tmux/الخدمة، يتحكم `lazyedit_config.sh` بمعلمات الإقلاع/الجلسة (`LAZYEDIT_DIR`, `CONDA_ENV`, `APP_ARGS`, المنافذ عبر متغيرات السكربت).

### المتغيرات الرئيسية

| المتغير | الغرض | القيمة الافتراضية/الاحتياطية |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | منفذ الخلفية | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | جذر دليل الوسائط | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | DSN PostgreSQL | احتياطي DB محلي `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | نقطة نهاية AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | مهلة طلب AutoPublish بالثواني | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | مسار سكربت Whisper/VAD | حسب البيئة |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | أسماء نماذج ASR | `large-v3` / `large-v2` (مثال) |
| `LAZYEDIT_CAPTION_PYTHON` | نسخة Python لمسار التعليق | حسب البيئة |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | المسار/السكربت الأساسي للتعليق | حسب البيئة |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | سكربت fallback وcwd التعليق الاحتياطي | حسب البيئة |
| `GRSAI_API_*` | إعدادات تكامل Veo/GRSAI | حسب البيئة |
| `VENICE_*`, `A2E_*` | إعدادات تكامل Venice/A2E | حسب البيئة |
| `OPENAI_API_KEY` | مطلوب لميزات OpenAI | لا شيء |

ملاحظات حسب الجهاز:
- قد يضبط `app.py` سلوك CUDA (`استخدام CUDA_VISIBLE_DEVICES` في سياق الكود).
- بعض المسارات الافتراضية خاصة بجهاز العمل؛ استخدم تجاوزه عبر `.env` لإعدادات قابلة للنقل.
- يتحكم `lazyedit_config.sh` بمتغيرات بدء جلسة tmux/النشر لسكربتات التشغيل.

<a id="-configuration-files"></a>
## 🧾 ملفات الإعداد

| الملف | الغرض |
| --- | --- |
| `.env.example` | قالب متغيرات البيئة المستخدمة من backend/services |
| `.env` | تجاوزات محلية حسب الجهاز؛ يحمله `config.py`/`app.py` إذا موجود |
| `config.py` | إعدادات خلفية الحلول وقرارات البيئة |
| `lazyedit_config.sh` | ملف إعداد tmux/الخدمة (مسار النشر، بيئة Conda، app args، اسم الجلسة) |
| `start_lazyedit.sh` | يشغّل backend + Expo في tmux مع المنافذ المختارة |
| `install_lazyedit.sh` | ينشئ `lazyedit.service` ويفحص وجود scripts/settings |

ترتيب التحديث الموصى به لقابلية النقل:
1. انسخ `.env.example` إلى `.env`.
2. عيّن قيم `LAZYEDIT_*` الخاصة بالمسارات والـ API في `.env`.
3. عدّل `lazyedit_config.sh` فقط لسلوك النشر/tmux.

<a id="api-examples"></a>
## 🔌 أمثلة API

أمثلة URL الأساسية تفترض `http://localhost:8787`.

| مجموعة API | نقاط نهاية تمثيلية |
| --- | --- |
| الرفع والوسائط | `/upload`, `/upload-stream`, `/media/*` |
| سجلات الفيديو | `/api/videos`, `/api/videos/{id}` |
| المعالجة | `/api/videos/{id}/transcribe`, `/translate`, `/burn-subtitles`, `/caption`, `/metadata`, `/process` |
| النشر | `/api/videos/{id}/publish`, `/api/autopublish/queue` |
| التوليد | `/api/videos/generate` (+ مسارات المزود في `app.py`) |

رفع:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

معالجة من النهاية إلى النهاية:

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

نشر الحزمة:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"platforms":{"xiaohongshu":true,"douyin":true}}' \
  http://localhost:8787/api/videos/123/publish
```

المزيد من نقاط النهاية وتفاصيل الـ payload: `references/API_GUIDE.md`.

مجموعات النقاط ذات الصلة التي قد تستخدمها غالبًا:
- دورة حياة الفيديو: `/upload`, `/upload-stream`, `/api/videos`, `/api/videos/{id}`, `/media/*`
- أفعال المعالجة: `/api/videos/{id}/transcribe`, `/api/videos/{id}/translate`, `/api/videos/{id}/burn-subtitles`, `/api/videos/{id}/metadata`, `/api/videos/{id}/caption`, `/api/videos/{id}/process`
- مسارات التوليد/المزود: `/api/videos/generate` بالإضافة لمسارات Venice/A2E المعروضة في `app.py`
- النشر: `/api/videos/{id}/publish`, `/api/autopublish/queue`

<a id="examples"></a>
## 🧪 الأمثلة

### تشغيل الواجهة محليًا (ويب)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

إذا كان backend على `8887`:

```bash
EXPO_PUBLIC_API_URL="http://localhost:8887" npx expo start --web --port 8091
```

### محاكي Android

```bash
EXPO_PUBLIC_API_URL="http://10.0.2.2:8787" npx expo start --android
```

### جهاز iOS (macOS)

```bash
EXPO_PUBLIC_API_URL="http://127.0.0.1:8787" npx expo start --ios
```

### مساعد توليد Sora اختياري

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

الثواني المدعومة: `4`, `8`, `12`.
الأحجام المدعومة: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

<a id="development-notes"></a>
## 🧪 ملاحظات التطوير

- استخدم `python` من بيئة Conda `lazyedit` (لا تعتمد على `python3` النظام).
- احتفظ بالوسائط الكبيرة خارج Git؛ خزّن وسائط التشغيل في `DATA/` أو تخزين خارجي.
- ابدأ أو حدّث submodules عندما تفشل مكونات خط المعالجة في الحل.
- أبقِ التغييرات مركزة وتجنب تعديلات التنسيق الواسعة غير المرتبطة.
- لعمل واجهة المستخدم، تحدد `EXPO_PUBLIC_API_URL` عنوان backend.
- CORS مفتوح في backend أثناء تطوير التطبيق.

سياسة submodule والاعتماد الخارجي:
- تعامل مع الاعتمادات الخارجية كمرتبطة بالـ upstream. في هذا المستودع، تجنب تعديل ملفات submodules ما لم تعمل عمدا في تلك المشاريع.
- التوجيه التشغيلي هنا يعتبر `furigana` (وأحيانًا `echomind` في بعض البيئات) كمسارات اعتماد خارجية؛ إذا لم تكن متأكدًا، احتفظ بالإصدار الأصلي وتجنب التعديلات داخلها.

مراجع مفيدة:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

نظافة الأمن/الإعداد:
- احتفظ بمفاتيح الـ API والأسرار داخل متغيرات البيئة؛ لا تُدخِل الشهادات في الكود.
- استخدم `.env` لتجاوزات محلية حسب الجهاز واترك `.env.example` كقالب عام.
- إذا اختلف سلوك CUDA/GPU بين المضيفات، استخدم البيئة لتجاوز القيم بدل تثبيت قيم جهازية في الكود.

<a id="testing"></a>
## ✅ الاختبار

الواجهة الرسمية للـ testing حالياً محدودة وموجّهة لقاعدة البيانات.

| طبقة التحقق | الأمر أو الطريقة |
| --- | --- |
| Smoke DB | `python db_smoke_test.py` |
| فحص DB عبر Pytest | `pytest tests/test_db_smoke.py` |
| مسار وظيفي | واجهة الويب + تدفق API باستخدام مقطع قصير في `DATA/` |

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

للتحقق الوظيفي، استخدم واجهة الويب ومسار الـ API مع عينة فيديو قصيرة في `DATA/`.

الافتراضات وملاحظات قابلية النقل:
- بعض المسارات الافتراضية في الكود احتياطية خاصة بمحطة العمل؛ هذا متوقع حاليًا.
- إذا لم يوجد مسار افتراضي على جهازك، فعّل المتغير المقابل `LAZYEDIT_*` في `.env`.
- إذا لم تكن متأكدًا من قيمة جهازية، احتفظ بالإعدادات الحالية و أضف تجاوزًا صريحًا بدل حذف القيم الافتراضية.

<a id="-assumptions--known-limits"></a>
## 🧱 الافتراضات والحدود المعروفة

- مجموعة تبعيات backend ليست مثبتة بقفل root lockfile؛ الاعتماد على الاستقرار البيئي يعتمد على إعدادات محلية.
- `app.py` أحادي البنية عمليًا حالياً ويحتوي على سطح مسارات كبير.
- أغلب التحقق التشغيلي تكاملي/يدوي (UI + API + media عينة)، مع اختبارات آلية رسمية محدودة.
- أدلة التشغيل (`DATA/`, `temp/`, `translation_logs/`) هي مخرجات زمنية وقد تكبر سريعًا.
- submodules مطلوبة للوظائف الكاملة؛ استخراج جزئي غالبًا يسبب أخطاء سكربتات مفقودة.

<a id="deployment--sync-notes"></a>
## 🚢 ملاحظات النشر والمزامنة

المسارات المعروفة الحالية وتدفق المزامنة (بحسب وثائق التشغيل):

- مساحة العمل: `/home/lachlan/ProjectsLFS/LazyEdit`
- backend + app لـ LazyEdit المنشور: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor المنشور: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- منصة النشر: `/home/lachlan/Projects/auto-publish` على المضيف `lazyingart`

| البيئة | المسار | الملاحظات |
| --- | --- | --- |
| بيئة التطوير | `/home/lachlan/ProjectsLFS/LazyEdit` | المصدر الرئيسي + submodules |
| LazyEdit المنشور | `/home/lachlan/DiskMech/Projects/lazyedit` | tmux `la-lazyedit` في توثيق العمليات |
| AutoPubMonitor المنشور | `/home/lachlan/DiskMech/Projects/autopub-monitor` | جلسات مراقبة/مزامنة/معالجة |
| مضيف النشر | `/home/lachlan/Projects/auto-publish` (`lazyingart`) | اسحب بعد تحديث submodule |

بعد دفع تغييرات `AutoPublish/` من هذا المستودع، اسحبها في مضيف النشر:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

<a id="troubleshooting"></a>
## 🧯 استكشاف الأخطاء

| المشكلة | فحص / إصلاح |
| --- | --- |
| موديولات/سكربتات pipeline مفقودة | شغّل `git submodule update --init --recursive` |
| FFmpeg غير موجود | ثبّت FFmpeg وتأكد أن `ffmpeg -version` يعمل |
| تعارض منافذ | backend افتراضي `8787` و `start_lazyedit.sh` على `18787`; عيّن `LAZYEDIT_PORT` أو `PORT` صراحة |
| Expo لا يصل لـ backend | تأكد أن `EXPO_PUBLIC_API_URL` يشير إلى host/port backend النشط |
| مشاكل اتصال DB | تحقق من PostgreSQL + DSN/المتغيرات؛ فحص smoke اختياري: `python db_smoke_test.py` |
| مشاكل GPU/CUDA | تأكد توافق الدرايفر/CUDA مع نسخة Torch المثبتة |
| فشل سكربت الخدمة أثناء التثبيت | تأكد أن `lazyedit_config.sh` و`start_lazyedit.sh` و`stop_lazyedit.sh` موجودة قبل تشغيل المثبت |

<a id="roadmap"></a>
## 🗺️ خارطة الطريق

- تحرير تعليقات/مقاطع الفيديو داخل التطبيق مع معاينة A/B وتحكم سطري.
- تغطية اختبار نهاية-إلى-نهاية أقوى لتدفقات API الأساسية.
- توحيد الوثائق بين إصدارات README متعدد اللغات وأوضاع النشر.
- تقوية إضافية لمسار التوليد عبر المزودات (إعادة المحاولة ووضوح الحالة).

<a id="contributing"></a>
## 🤝 المساهمة

المساهمات مرحب بها.

1. Fork ثم أنشئ فرع ميزة.
2. اجعل الالتزامات مركزة ونطاقية.
3. تحقق محليًا (`python app.py`، مسار API أساسي، وتكامل app إن كان مناسبًا).
4. افتح PR يحتوي الهدف، خطوات التكرار، وملاحظات قبل/بعد (لقطات شاشة للتغييرات UI).

إرشادات عملية:
- اتبع أسلوب Python (PEP 8، 4 مسافات، snake_case).
- تجنب تضمين مفاتيح/بيانات حساسة أو ملفات ضخمة.
- حدّث docs/scripts عند تغيّر السلوك.
- نمط commit المفضل: قصير، أمر مباشر ومحدود (مثل: `fix ffmpeg 7 compatibility`).

<a id="-support"></a>
## 📄 الترخيص

[Apache-2.0](LICENSE)

<a id="acknowledgements"></a>
## 🙏 الشكر والتقدير

LazyEdit تبني على مكتبات وخدمات مفتوحة المصدر، بما في ذلك:
- FFmpeg لمعالجة الوسائط
- Tornado لـ backend APIs
- MoviePy لمسارات التحرير
- نماذج OpenAI لمهام خط المعالجة المدعومة بالذكاء الاصطناعي
- CJKWrap وأدوات النص متعدد اللغات في سير عمل الترجمة


## ❤️ Support

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://camo.githubusercontent.com/24a4914f0b42c6f435f9e101621f1e52535b02c225764b2f6cc99416926004b7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446f6e6174652d4c617a79696e674172742d3045413545393f7374796c653d666f722d7468652d6261646765266c6f676f3d6b6f2d6669266c6f676f436f6c6f723d7768697465)](https://chat.lazying.art/donate) | [![PayPal](https://camo.githubusercontent.com/d0f57e8b016517a4b06961b24d0ca87d62fdba16e18bbdb6aba28e978dc0ea21/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f50617950616c2d526f6e677a686f754368656e2d3030343537433f7374796c653d666f722d7468652d6261646765266c6f676f3d70617970616c266c6f676f436f6c6f723d7768697465)](https://paypal.me/RongzhouChen) | [![Stripe](https://camo.githubusercontent.com/1152dfe04b6943afe3a8d2953676749603fb9f95e24088c92c97a01a897b4942/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f5374726970652d446f6e6174652d3633354246463f7374796c653d666f722d7468652d6261646765266c6f676f3d737472697065266c6f676f436f6c6f723d7768697465)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |
