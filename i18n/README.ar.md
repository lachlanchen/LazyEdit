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

LazyEdit أداة تحرير فيديو تلقائية مدعومة بالذكاء الاصطناعي. تقوم بإنشاء ترجمات، إبرازات، بطاقات كلمات، وبيانات وصفية بجودة احترافية لتبسيط سير العمل.

## المميزات

- **تفريغ صوتي تلقائي**: تحويل الصوت إلى نص باستخدام الذكاء الاصطناعي
- **تعليقات تلقائية**: إنشاء وصف للمحتوى المرئي
- **ترجمات تلقائية**: إنشاء وحرق الترجمات داخل الفيديو
- **إبراز تلقائي**: تمييز الكلمات المهمة أثناء التشغيل
- **بيانات وصفية تلقائية**: استخراج وإنشاء بيانات وصفية للفيديو
- **بطاقات كلمات**: إضافة بطاقات تعليمية للكلمات
- **إنشاء teaser**: تكرار المقاطع المهمة في البداية
- **دعم متعدد اللغات**: يدعم عدة لغات منها الإنجليزية والصينية
- **إنشاء غلاف**: استخراج أفضل لقطة كغلاف مع نص

## التثبيت

### المتطلبات

- Python 3.10 أو أعلى
- FFmpeg
- GPU يدعم CUDA (لتسريع التفريغ الصوتي)
- مدير بيئات Conda

### خطوات التثبيت

1. استنساخ المستودع:
   ```bash
   git clone <repository_url>
   cd lazyedit
   ```

2. تشغيل سكربت التثبيت:
   ```bash
   chmod +x install_lazyedit.sh
   ./install_lazyedit.sh
   ```

يقوم السكربت بـ:
- تثبيت الحزم اللازمة (ffmpeg, tmux)
- إنشاء بيئة conda باسم "lazyedit"
- إعداد خدمة systemd للتشغيل التلقائي
- ضبط الأذونات المطلوبة

## الاستخدام

يعمل LazyEdit كتطبيق ويب ويمكن الوصول إليه عبر http://localhost:8081

### معالجة فيديو

1. رفع الفيديو من واجهة الويب
2. سيقوم LazyEdit تلقائيًا بـ:
   - التفريغ الصوتي وإنشاء التعليقات
   - إنشاء البيانات الوصفية والمحتوى التعليمي
   - إنشاء الترجمات حسب اللغة المكتشفة
   - إبراز الكلمات المهمة
   - إنشاء teaser
   - إنشاء صورة غلاف
   - تجميع النتائج وإرجاعها

### سطر الأوامر

يمكن تشغيله مباشرة:

```bash
conda activate lazyedit
cd /path/to/lazyedit
python app.py -m lazyedit
```

## هيكل المشروع

- `app.py` - نقطة الدخول الرئيسية
- `lazyedit/` - مجلد الوحدات الأساسية
  - `autocut_processor.py` - تقسيم الفيديو والتفريغ الصوتي
  - `subtitle_metadata.py` - إنشاء البيانات الوصفية من الترجمات
  - `subtitle_translate.py` - ترجمة الترجمات
  - `video_captioner.py` - إنشاء تعليقات مرئية
  - `words_card.py` - إنشاء بطاقات الكلمات
  - `utils.py` - أدوات مساعدة
  - `openai_version_check.py` - طبقة توافق OpenAI API

## الإعداد

يتم إنشاء خدمة systemd في `/etc/systemd/system/lazyedit.service`.

يستخدم LazyEdit جلسة tmux باسم "lazyedit" للاستمرار في العمل بالخلفية.

## إدارة الخدمة

- تشغيل الخدمة: `sudo systemctl start lazyedit.service`
- إيقاف الخدمة: `sudo systemctl stop lazyedit.service`
- الحالة: `sudo systemctl status lazyedit.service`
- السجلات: `sudo journalctl -u lazyedit.service`

## استخدام متقدم

يمكن تخصيص:
- طول ومكان الـ teaser
- أنماط إبراز الكلمات
- خطوط ومواقع الترجمة
- هيكل مجلد الإخراج
- اختيار GPU

## استكشاف الأعطال

- إذا لم يبدأ التطبيق، تحقق من حالة systemd والسجلات
- عند فشل المعالجة، تأكد من تثبيت FFmpeg
- مشاكل GPU: تحقق من CUDA وتوفر GPU
- تأكد من تفعيل بيئة conda

## الترخيص

[أضف الترخيص هنا]

## الشكر والتقدير

يعتمد LazyEdit على أدوات مفتوحة المصدر، منها:
- FFmpeg لمعالجة الفيديو
- نماذج OpenAI للذكاء الاصطناعي
- Tornado لإطار الويب
- MoviePy لتحرير الفيديو
- CJKWrap لمعالجة النص متعدد اللغات
