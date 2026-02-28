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

LazyEdit هو سير عمل متكامل لصناعة الفيديو بمساعدة الذكاء الاصطناعي، يغطي الإنشاء والمعالجة والنشر الاختياري. يجمع بين التوليد المعتمد على الـ prompt (Stage A/B/C)، وواجهات معالجة الوسائط، ورسم الترجمة على الفيديو، وتعليقات الإطارات المفتاحية، وتوليد البيانات الوصفية، والتسليم إلى AutoPublish.

## ✨ نظرة عامة

يعتمد LazyEdit على واجهة خلفية Tornado (`app.py`) وواجهة أمامية Expo (`app/`).

| الخطوة | ما الذي يحدث |
| --- | --- |
| 1 | رفع فيديو أو توليده |
| 2 | تفريغ الكلام إلى نص وترجمة الترجمة الفرعية اختياريًا |
| 3 | حرق ترجمة متعددة اللغات مع عناصر تحكم في التخطيط |
| 4 | توليد الإطارات المفتاحية والتعليقات والبيانات الوصفية |
| 5 | تجهيز الحزمة والنشر اختياريًا عبر AutoPublish |

### تركيز خط الأنابيب

- الرفع، والتوليد، وإعادة المزج، وإدارة المكتبة من واجهة تشغيل واحدة.
- تدفق معالجة يعتمد على API للتفريغ الصوتي، وتحسين/ترجمة الترجمة، والحرق داخل الفيديو، والبيانات الوصفية.
- تكاملات اختيارية مع مزودي التوليد (مساعدات Veo / Venice / A2E / Sora داخل `agi/`).
- تسليم اختياري للنشر عبر `AutoPublish`.

## 🎯 لمحة سريعة

| المجال | ما يتضمنه LazyEdit |
| --- | --- |
| التطبيق الأساسي | واجهة خلفية Tornado API + واجهة Expo للويب/الجوال |
| خط الوسائط | ASR، ترجمة/تحسين الترجمة الفرعية، الحرق داخل الفيديو، الإطارات المفتاحية، التعليقات، البيانات الوصفية |
| التوليد | Stage A/B/C ومسارات مساعدة المزود (`agi/`) |
| التوزيع | تسليم اختياري إلى AutoPublish |
| نموذج التشغيل | سكربتات Local-first، تدفقات tmux، وخدمة systemd اختيارية |

## 🎬 عروض توضيحية

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

## 🧩 الميزات

- سير عمل توليد قائم على الـ prompt (Stage A/B/C) مع مسارات تكامل Sora وVeo.
- خط معالجة كامل: التفريغ -> تحسين/ترجمة الترجمة -> الحرق داخل الفيديو -> الإطارات المفتاحية -> التعليقات -> البيانات الوصفية.
- تركيب ترجمة فرعية متعددة اللغات مع مسارات دعم متعلقة بـ furigana/IPA/romaji.
- واجهة خلفية API-first مع نقاط نهاية للرفع والمعالجة وخدمة الوسائط وطابور النشر.
- تكامل اختياري مع AutoPublish للتسليم إلى منصات التواصل.
- سير عمل موحد للواجهة الخلفية + Expo مدعوم عبر سكربتات تشغيل tmux.

## 🗂️ بنية المشروع

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

## ✅ المتطلبات المسبقة

| الاعتماد | ملاحظات |
| --- | --- |
| بيئة Linux | سكربتات `systemd`/`tmux` موجهة لنظام Linux |
| Python 3.10+ | استخدم بيئة Conda باسم `lazyedit` |
| Node.js 20+ + npm | مطلوب لتطبيق Expo داخل `app/` |
| FFmpeg | يجب أن يكون متاحًا على `PATH` |
| PostgreSQL | مصادقة peer محلية أو اتصال عبر DSN |
| Git submodules | مطلوبة لخطوط الأنابيب الأساسية |

## 🚀 التثبيت

1. استنسخ المستودع وابدأ submodules:

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
- يقوم `install_lazyedit.sh` بتثبيت `ffmpeg` و`tmux` ثم إنشاء `lazyedit.service`.
- لا يقوم بإنشاء `lazyedit_config.sh` أو `start_lazyedit.sh` أو `stop_lazyedit.sh`؛ يجب أن تكون هذه الملفات موجودة مسبقًا وصحيحة.

## 🛠️ الاستخدام

### التطوير: الواجهة الخلفية فقط

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python app.py
```

مدخل بديل مستخدم في سكربتات النشر الحالية:

```bash
python app.py -m lazyedit
```

رابط الواجهة الخلفية الافتراضي: `http://localhost:8787` (من `config.py`، ويمكن التعديل عبر `PORT` أو `LAZYEDIT_PORT`).

### التطوير: الواجهة الخلفية + تطبيق Expo (tmux)

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

### إدارة الخدمة

```bash
sudo systemctl start lazyedit.service
sudo systemctl stop lazyedit.service
sudo systemctl status lazyedit.service
sudo journalctl -u lazyedit.service
```

## ⚙️ الإعداد

انسخ `.env.example` إلى `.env` وحدّث المسارات/الأسرار:

```bash
cp .env.example .env
```

### المتغيرات الأساسية

| المتغير | الغرض | الافتراضي/البديل |
| --- | --- | --- |
| `PORT`, `LAZYEDIT_PORT` | منفذ الواجهة الخلفية | `8787` |
| `LAZYEDIT_UPLOAD_DIR` | المجلد الجذر للوسائط | `DATA/` |
| `LAZYEDIT_DATABASE_URL`, `DATABASE_URL` | PostgreSQL DSN | بديل قاعدة محلية `lazyedit_db` |
| `LAZYEDIT_AUTOPUBLISH_URL` | نقطة نهاية AutoPublish | `http://localhost:8081/publish` |
| `LAZYEDIT_AUTOPUBLISH_TIMEOUT` | مهلة طلب AutoPublish (ثوانٍ) | `60` |
| `LAZYEDIT_WHISPER_SCRIPT` | مسار سكربت Whisper/VAD | يعتمد على البيئة |
| `LAZYEDIT_WHISPER_MODEL`, `LAZYEDIT_WHISPER_FALLBACK_MODEL` | أسماء نماذج ASR | `large-v3` / `large-v2` (مثال) |
| `LAZYEDIT_CAPTION_PYTHON` | بيئة Python لخط التعليقات | يعتمد على البيئة |
| `LAZYEDIT_CAPTION_PRIMARY_ROOT`, `LAZYEDIT_CAPTION_PRIMARY_SCRIPT` | مسار/سكربت التعليقات الأساسي | يعتمد على البيئة |
| `LAZYEDIT_CAPTION_FALLBACK_SCRIPT`, `LAZYEDIT_CAPTION_FALLBACK_CWD` | مسار/سكربت/cwd للتعليقات الاحتياطية | يعتمد على البيئة |
| `GRSAI_API_*` | إعدادات تكامل Veo/GRSAI | يعتمد على البيئة |
| `VENICE_*`, `A2E_*` | إعدادات تكامل Venice/A2E | يعتمد على البيئة |
| `OPENAI_API_KEY` | مطلوب للميزات المبنية على OpenAI | لا يوجد |

ملاحظات خاصة بالجهاز:
- قد يضبط `app.py` سلوك CUDA (استخدام `CUDA_VISIBLE_DEVICES` في سياق الكود).
- بعض المسارات الافتراضية خاصة بمحطة عمل معينة؛ استخدم تعديلات `.env` لتهيئة قابلة للنقل.
- يتحكم `lazyedit_config.sh` بمتغيرات بدء التشغيل في tmux/الجلسات لسكربتات النشر.

## 🔌 أمثلة API

تفترض أمثلة Base URL استخدام `http://localhost:8787`.

الرفع:

```bash
curl -F "video=@/path/to/video.mp4" \
     -F "title=my_video" \
     -F "filename=video.mp4" \
     -F "source=api" \
     http://localhost:8787/upload
```

المعالجة من البداية للنهاية:

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

مزيد من نقاط النهاية وتفاصيل الحمولات: `references/API_GUIDE.md`.

## 🧪 أمثلة

### تشغيل الواجهة الأمامية محليًا (ويب)

```bash
cd app
npm install
EXPO_PUBLIC_API_URL="http://localhost:8787" npx expo start --web --port 8091
```

إذا كانت الواجهة الخلفية على `8887`:

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

### مساعد اختياري لتوليد Sora

```bash
python -m agi.demo_fantasy_woman --seconds 8 --size 1280x720 --output DATA/sora_oracle_valley.mp4
```

الثواني المدعومة: `4`, `8`, `12`.
المقاسات المدعومة: `720x1280`, `1280x720`, `1024x1792`, `1792x1024`.

## 🧪 ملاحظات التطوير

- استخدم `python` من بيئة Conda `lazyedit` (ولا تفترض استخدام `python3` من النظام).
- أبقِ ملفات الوسائط الكبيرة خارج Git؛ خزّن وسائط التشغيل في `DATA/` أو تخزين خارجي.
- ابدأ/حدّث submodules كلما فشل حل مكونات خط الأنابيب.
- أبقِ التعديلات مركزة؛ تجنب تغييرات تنسيق كبيرة غير مرتبطة.
- في عمل الواجهة الأمامية، عنوان API الخلفي يتحكم به `EXPO_PUBLIC_API_URL`.
- CORS مفتوح على الواجهة الخلفية لتطوير التطبيق.

سياسة submodules والاعتمادات الخارجية:
- تعامل مع الاعتمادات الخارجية على أنها مملوكة للمصدر upstream. في تدفق العمل لهذا المستودع، تجنب تعديل الأجزاء الداخلية للـ submodules إلا عند العمل عليها عمدًا.
- تعتبر إرشادات التشغيل في هذا المستودع `furigana` (وأحيانًا `echomind` في الإعدادات المحلية) مسارات اعتماد خارجية؛ عند الشك، حافظ على المصدر upstream وتجنب التعديل المباشر داخلها.

مراجع مفيدة:
- `references/QUICKSTART.md`
- `references/API_GUIDE.md`
- `references/APP_GUIDE.md`
- `references/DEPLOYMENT_SYSTEMS.md`
- `references/TMUX_SESSIONS.md`

## ✅ الاختبارات

سطح الاختبارات الرسمية الحالي محدود ويركز على قاعدة البيانات.

```bash
python db_smoke_test.py
pytest tests/test_db_smoke.py
```

للتحقق الوظيفي، استخدم واجهة الويب وتدفق API مع مقطع عينة قصير داخل `DATA/`.

## 🚢 ملاحظات النشر والمزامنة

المسارات المعروفة حاليًا وتدفق المزامنة (من وثائق تشغيل المستودع):

- مساحة عمل التطوير: `/home/lachlan/ProjectsLFS/LazyEdit`
- الواجهة الخلفية + التطبيق المنشودان لـ LazyEdit: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPubMonitor المنشور: `/home/lachlan/DiskMech/Projects/autopub-monitor`
- مضيف نظام النشر: `/home/lachlan/Projects/auto-publish` على `lazyingart`

بعد دفع تحديثات `AutoPublish/` من هذا المستودع، اسحب التحديثات على مضيف النشر:

```bash
ssh lachlan@lazyingart
cd ~/Projects/auto-publish
git pull github main
```

## 🧯 استكشاف الأخطاء وإصلاحها

| المشكلة | الفحص / الحل |
| --- | --- |
| نقص وحدات أو سكربتات خط الأنابيب | نفّذ `git submodule update --init --recursive` |
| FFmpeg غير موجود | ثبّت FFmpeg وتأكد أن `ffmpeg -version` يعمل |
| تعارض المنافذ | الواجهة الخلفية افتراضيًا `8787`؛ و`start_lazyedit.sh` افتراضيًا `18787`؛ اضبط `LAZYEDIT_PORT` أو `PORT` صراحةً |
| Expo لا يستطيع الوصول للواجهة الخلفية | تأكد أن `EXPO_PUBLIC_API_URL` يشير إلى المضيف/المنفذ الصحيحين |
| مشاكل اتصال قاعدة البيانات | تحقق من PostgreSQL + متغيرات DSN/env؛ فحص اختياري: `python db_smoke_test.py` |
| مشاكل GPU/CUDA | تحقق من توافق التعريف/CUDA مع حزمة Torch المثبتة |
| فشل سكربت الخدمة أثناء التثبيت | تأكد من وجود `lazyedit_config.sh` و`start_lazyedit.sh` و`stop_lazyedit.sh` قبل تشغيل المُثبِّت |

## 🗺️ خارطة الطريق

- تحرير الترجمة/المقاطع داخل التطبيق مع معاينة A/B وتحكم لكل سطر.
- تغطية اختبارات أشمل من البداية للنهاية لتدفقات API الأساسية.
- توحيد أفضل للتوثيق بين نسخ README متعددة اللغات وأنماط النشر المختلفة.
- تقوية إضافية لتدفق العمل الخاص بإعادة محاولات مزودي التوليد وإظهار الحالة.

## 🤝 المساهمة

المساهمات مرحّب بها.

1. قم بعمل Fork وأنشئ فرع ميزة.
2. أبقِ الـ commits مركزة ومحددة النطاق.
3. تحقق من التعديلات محليًا (`python app.py`، وتدفق API الأساسي، وتكامل التطبيق عند الحاجة).
4. افتح PR يتضمن الهدف، وخطوات إعادة الإنتاج، وملاحظات قبل/بعد (مع لقطات شاشة لتغييرات الواجهة).

إرشادات عملية:
- اتبع أسلوب Python (PEP 8، 4 مسافات، وتسمية snake_case).
- تجنب رفع بيانات اعتماد أو ملفات ثنائية كبيرة.
- حدّث مستندات/سكربتات الإعداد عند تغيّر السلوك.
- أسلوب commit المفضل: قصير، بصيغة الأمر، ومحدد النطاق (مثل: `fix ffmpeg 7 compatibility`).

## ❤️ ما الذي يتيحه دعمك

- <b>إبقاء الأدوات مفتوحة</b>: الاستضافة، والاستدلال، وتخزين البيانات، وتشغيل المجتمع.  
- <b>تسريع الإطلاق</b>: أسابيع من العمل المفتوح المصدر المركّز على EchoMind وLazyEdit وMultilingualWhisper.  
- <b>النماذج الأولية للأجهزة القابلة للارتداء</b>: بصريات، وحساسات، ومكوّنات neuromorphic/edge لمشروعي IdeasGlass + LightMind.  
- <b>إتاحة للجميع</b>: نشرات مدعومة للطلاب، وصنّاع المحتوى، والمجموعات المجتمعية.

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

## 📄 الترخيص

[Apache-2.0](LICENSE)

## 🙏 شكر وتقدير

يعتمد LazyEdit على مكتبات وخدمات مفتوحة المصدر، بما في ذلك:
- FFmpeg لمعالجة الوسائط
- Tornado لواجهات API الخلفية
- MoviePy لتدفقات التحرير
- نماذج OpenAI لمهام خط الأنابيب المدعومة بالذكاء الاصطناعي
- CJKWrap وأدوات نصية متعددة اللغات ضمن تدفقات الترجمة الفرعية
