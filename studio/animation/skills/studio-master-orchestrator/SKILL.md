---
name: studio-master-orchestrator
description: SUPREME UNIVERSAL WORKSPACE MASTER ENFORCER ("شلاق‌زنِ سراسری کل استودیو") mandatory for EVERY video, documentary, explainer, promo, motion graphic, or Short/Reel produced in this workspace — regardless of channel, brand, topic, or aspect ratio. Forces 100% simultaneous utilization of ALL 14 installed skills, 265 gl-transitions shaders, 378 LYGIA shaders, Iran/World GeoJSON vector maps, 2.5D Isometric & Data-Story charts, Lalezar + Vazirmatn + FiraCode typography, multi-mode GPU Kinetic Shock Typography, broadcast SoX + FluidSynth -14 LUFS sound design, and blocks delivery via whip_enforcer.py if ANY component slacks off.
---

# ⚡ اسکیل فرمانده سراسری کل استودیو («شلاق‌زنِ اجباری تمام ویدیوهای این محیط کاری» — Universal Studio Master Orchestrator)

> **قانون آهنین، سراسری و غیرقابل مذاکره (فراتر از هر کانال خاص):**
> این قوانین برای **تک‌تک ویدیوهایی که در این محیط کاری (`/home/user`) ساخته می‌شوند** — اعم از مستند، موشن‌گرافیک، ویدیوی تحلیلی، تیزر تبلیغاتی، آموزشی، یوتیوب (`16:9`)، شورتس/ریلز/تیک‌تاک (`9:16`) یا مربعی (`1:1`) و برای **هر کانال، برند یا مخاطب** — به صورت ۱۰۰٪ اجباری حاکم است!
> تنبلی، میان‌بُر زدن و استفاده تک‌بعدی از یک ابزار در هیچ ویدیویی مجاز نیست؛ بازرس خودکار (`whip_enforcer.py`) اگر ببیند حتی **یکی** از دارایی‌ها، مخازن شیدر، نقشه‌ها، فونت‌ها یا اسکیل‌های نصب‌شده بیکار مانده، تحویل پروژه را با خطای قرمز متوقف می‌کند.

---

## ۰. ممنوعیت‌های مطلق همیشگی (خطوط قرمز کاربر)
1. **ممنوعیت مطلق تایم‌لاین (`ZERO TIMELINE BAR`):** تحت هیچ شرایطی نوار پیشرفت زمانی، تایم‌لاین بالا/پایین صفحه یا شمارنده مراحل ثابت داخل ویدیو قرار نده.
2. **ممنوعیت مطلق انیمیشن تمام-HTML (`NO WHOLE-VIDEO HTML`):** رندر کل ویدیو با HTML/CSS ممنوع است. موتور اصلی تصویر باید **GPU OpenGL 3.3 (`ModernGL EGL` + شیدرهای GLSL)** در ترکیب با لایه‌های برداری دقیق (`PyCairo` / `Shapely` / `<svg>` بیک‌شده برای متن فارسی) و کامپوزیت کدپایه (`vfx_studio.py` / `Movis` / `ReelForge`) باشد.
3. **ممنوعیت باکس‌های متنی ساکن و تامبنیل کارتونی:** هیچ نوشته یا کارتی حق ندارد بیش از ۷ ثانیه ساکن روی صفحه بماند؛ در تامبنیل نیز دورکادرهای مستطیلی کارتونی، حاشیه‌های حبابی ضخیم و فلش‌های کلیپ‌آرتی ممنوع است.

---

## ۱. هشت ستون اجباری که باید در هر کلیپ جدید به کار کشیده شوند!

### ستون ۱ — راه‌اندازی فوری تمام موتورهای استودیو (`ensure_engines.sh`)
قبل از نوشتن حتی یک خط کد تولید، اجرای دستور زیر الزامی است:
```bash
bash /home/user/animation-studio/ensure_engines.sh
```
این دستور حضور `FFmpeg`، `Blender`، `Chromium`، `SoX`، `FluidSynth`، `Cairo/Pango`، `Mesa EGL`، کتابخانه‌های `runtime/pylibs` و `puppeteer-core` را تضمین می‌کند.

---

### ستون ۲.۵ — کتابخانه ۴۲۰ پریست تایپوگرافی یوتیوب/اینستاگرام (`typography-library`)
- **اجبار انتخاب پریست پیش از طراحی هر صحنه متنی:** از `skills/typography-library/catalog.json` یک پریست متناسب با پلتفرم (`yt_16x9` / `yt_thumb` / `yt_shorts` / `ig_reels` / `ig_story` / `ig_carousel` / `tiktok`) بردار و `css` + رسیپی `gsap` آن را عیناً در `stage.html` تزریق کن.
- **۵۰ فونت تأییدشده** در `assets/fonts/`: فارسی کامل (`Lalezar`, ۹ وزن `Vazirmatn`, `Estedad`, `Shabnam-FD`, `Changa`, `Harmattan`, `Markazi Text`, `Mirza`, `Rubik`, `Alexandria`, `Noto Nastaliq Urdu`, `Sahel`, `Samim`, `Parastoo`, `Tanha`, `Vazir-Code-FD`) + Display لاتین (`Anton`, `Archivo Black`, `Bebas Neue`, `Space Grotesk`, `Inter Tight`, `Oswald`, `Syne`, `Montserrat`, `Doto`, `Instrument Serif`, `Fraunces`, `Space Mono`) + Mono (`JetBrains Mono`, `FiraCode`, `IBM Plex Mono`). **حروف فارسی هرگز با فونت لاتین رندر نمی‌شوند.**
- **محدوده امن اجباری:** هیچ کاراکتری از `safe_zone_px` پریست بیرون نمی‌زند؛ سایز `hero` پریست‌ها با متریک واقعی فونت به‌صورت خودکار fit شده است.
- **اعتبارسنجی سخت:** `python3 tools/typography_engine.py --validate` باید `VALIDATE PASS` بدهد (۴۲۰ پریست، پوشش ۱۴ لایه‌بندی / ۹ پرشدگی / ۱۰ افکت / ۱۲+ موشن / ۱۰+ پالت در هر پلتفرم، صفر CSS مخرب، صفر فونت گم‌شده).
- **پکیج‌های عامل تخصصی:** `skills/agency-agents-pack` (۴۲ عامل) و `skills/youtube-instagram-video-agents` (۱۰ مخزن، ۲۷۸ سند) منبع اجباری هوک، ساختار روایت، سبک بصری و SEO هستند.

### ستون ۲.۴ — پکیج‌های استودیویی تازه‌نصب (اجباری)
- **`langchain-content-studio`** (۳۶ مهارت): قبل از طراحی هر صحنه، `hyperframes-core` + `motion-direction` و برای تامبنیل `thumbnails` خوانده شود.
- **`openmotion-director-suite`**: `openmotion-director/references/motion-craft.md` و `motion-phrases.md` مرجع زبان موشن هر قسمت؛ `motion-review.md` چک‌لیست بازبینی پایانی.
- **`openmotion-motion-library`**: از `index.json` یک استادی هم‌خانواده انتخاب و `specs/<id>.md` را به‌عنوان مرجع ریتم/ترتیب مطالعه کن (۲۸۷ اسپک).
- **`open-edit-suite`**: `CUT.md` برای برش روی مرز کلمه، `TRANSCRIPTION.md` برای تایمینگ زیرنویس.
- **`video-editing-kit`**: قالب‌های `STORYBOARD.md`/`MOTION_PLAN.md`/`CUT_AUDIT.md` پر شود و پس از رندر `audit_visual_beats.py` + `verify_export.py` اجرا شود.

### ستون ۲ — سیستم سه‌فونته و تایپوگرافی جنبشی کوبشی (`kinetic-typography-rtl` + `kinetic-type-skills` + `motion-design-skills/kinetic-typography`)
- **اجبار ترکیب ۳ فونت استودیو (`/home/user/animation-studio/assets/fonts/`):**
  1. **`Lalezar-Regular.ttf`:** مخصوص تیترهای غول‌پیکر پوستری، برچسب‌های هشدار (`شوک اول!`, `فاجعه!`, `قانون ۱`) و تیترهای کوبشی.
  2. **`Vazirmatn-Black.ttf` و `Vazirmatn-Bold.ttf`:** مخصوص اعداد میلیونی و دلاری دقیق، فرمول‌ها و زیرنویس‌های هایلایت‌دار.
  3. **`FiraCode-Bold.ttf`:** مخصوص تگ‌های نهادی و تله‌متری بین‌المللی (`GOLDMAN SACHS • JPM • IMF 2027`).
- **اجبار تراکم ضربات (`Beat Density`):** گفتار گوینده باید با تحلیل انرژی موج صدا به ضربات **۴ تا ۶.۵ ثانیه‌ای** شکسته شود (حداقل ۱ ضربه جدید در هر ۷ ثانیه!).
- **اجبار تنوع حرکتی (`Minimum 5 Kinetic Modes`):** هر ویدیو موظف است حداقل **۵ تکنیک مختلف** از کاتالوگ ۸۰ تکنیکی `kinetic-type-skills` را روی GPU اجرا کند:
  1. `stomp_slam`: فرود کوبشی از مقیاس `2.85x → 0.93x → 1.0x` با تاری شعاعی (`Radial Motion Blur`) + لرزش دوربین.
  2. `spring_pop`: جهش فنری `0.12x → 1.26x → 1.0x` با زاویه تیلت پویا.
  3. `slice_pincer`: برش قطری کلمه با خط لیزر نورانی و قفل‌شدن دو نیمه در هم.
  4. `echo_stack`: همگرایی ۳ لایه پژواک نئونی پشت کلمه اصلی.
  5. `glitch_rgb`: برش افقی دیجیتال و شکاف نوری قرمز/سیان روی هشدارهای بحرانی.
  6. `odometer_roll`: شمارشگر زنده چرخان برای اعداد طلا/دلار/تورم پیش از ضربه نهایی.
  7. `marker_wipe` + `beat_pulse` + `light_sweep` + `zoom_through`: هایلایت راست‌به‌چپ (`RTL`)، تپش زنده روی ضرب موزیک، عبور برق فلزی از روی حروف و خروج انفجاری `1.0x → 3.6x` به سمت صورت مخاطب.

---

### ستون ۳ — نقشه برداری واقعی ژئوپلیتیک و استانی (`map-animation-skills` + `assets/geo/`)
هر کلیپ جدید **موظف است حداقل در ۱ صحنه** از داده‌های واقعی جغرافیایی موجود در `/home/user/animation-studio/assets/geo/` کار بکشد (فراخوانی مستقیم از `studio_harness.py`):
- **`iran_provinces.min.geojson` (مرز دقیق ۳۱ استان ایران با نام فارسی):** برای نمایش کانون‌های تورم، مسکن، انرژی (تهران، هرمزگان، خوزستان، بوشهر، اصفهان و...) به صورت نقشه گرمایی نئونی (`Choropleth Glow`).
- **`world_countries.geo.json` (مرز ۱۸۰ کشور جهان):** برای نمایش کریدورهای ژئوپلیتیک، جریان طلا/نفت/تحریم بین آمریکا، چین، اروپا، خلیج فارس و ایران همراه با کمان‌های نوری متحرک و امواج راداری در شیدر OpenGL.

---

### ستون ۴ — داده‌نگاری زنده مالی + مقایسه حجمی ۲.۵ بعدی و دیاگرام جریان (`data-animation-skills` + `data-story-charts` + `system-diagram-animation` + `explainer-video-skills`)
هر کلیپ جدید **موظف است حداقل ۲ لایه تحلیلی داده‌محور کدپایه** داشته باشد (فراخوانی از `studio_harness.py` + شیدر زنده):
1. **چارت مالی زنده با شوک تغییر مقیاس (`Live Financial Chart / Axis Rescale`):** رسم زنده منحنی/کندل با نقطه درخشان پیشرو روی GPU.
2. **مقایسه حجمی ایزومتریک ۲.۵ بعدی (`2.5D Isometric Extruded Towers`) یا دیاگرام جریان سیستم (`System Shock Flow`):** نمایش ملموس اختلاف اعداد (مثلاً ستون سه‌بعدی حقوق در برابر ستون غول‌پیکر سبد معیشت یا بدهی ۴۰ تریلیون دلاری) و فلش‌های زنجیره علیت اقتصادی.

---

### ستون ۵ — ترنزیشن‌های واقعی `gl-transitions` (۲۶۵ شیدر) + پردازش تصویر `LYGIA` (۳۷۸ شیدر) (`vfx_studio.py` + `reelforge` + `webgl-animation-skills` + `movis`)
- **ممنوعیت کات ساده بین صحنه‌ها!** در مرز بین صحنه‌های اصلی ویدیو، موتور رندر **موظف است از `GPUVFXEngine.render_transition()` در `/home/user/animation-studio/vfx_studio.py`** استفاده کند و حداقل **۴ ترنزیشن متفاوت** از مخزن ۲۶۵تایی `gl-transitions` را اجرا نماید (مانند: `BurnThrough`, `CameraShake`, `BloomDissolve`, `BokehDissolve`, `CrossZoom`, `GlitchMemories`, `DirectionalWarp`).
- **اجبار شیدرهای `LYGIA` و عمق سه‌بعدی:** فعال‌بودن پارالاکس عمق‌محور ۲.۵ بعدی (`Depth-Map Parallax`)، ذرات شیدر `O(1)` (اخگر، باران، غبار طلا، پرتوهای حجمی `God-Rays`)، خطای رنگی آنامورفیک (`Chromatic Aberration`) و اصلاح رنگ سینمایی **`LYGIA ACES Filmic Tonemapping`** روی تمام فریم‌ها الزامی است. (در یادداشت فنی: در OpenGL نگاشت مستقیم `v_uv = vec2(in_pos.x*0.5+0.5, in_pos.y*0.5+0.5)` حفظ شود تا تصویر بدون نیاز به `vflip` کاملاً صاف خروجی بگیرد).

---

### ستون ۶ — گوینده دائمی `voice-05` + افکت جذابیت صدای استودیویی (`vocal_fx_chain.py`) + سینت‌سایزر Beat-Grid (`SoX` + `FluidSynth`)
1. **قانون تغییرناپذیر گوینده همیشگی (`PERMANENT VOICE: voice-05`):**
   - تمامی ویدیوهای تولیدی موظف‌اند منحصراً از ابزار بومی `generate_speech` خودِ Arena با شناسه ثابت **`voice_id="voice-05"`** استفاده کنند (استفاده از هر موتور TTS محلی مطلقاً ممنوع است و فیلد `"narrator_voice_id": "voice-05"` در مانیفست توسط `whip_enforcer.py` بازرسی می‌شود).
2. **افکت اجباری جذابیت و عمق سه‌بعدی صدا (`/home/user/animation-studio/tools/vocal_fx_chain.py`):**
   - عبور تمام فایل‌های گفتار `voice-05` از ماژول `enhance_narrator_audio` در `tools/vocal_fx_chain.py` الزامی است: گرمای بم سینمایی (`125Hz +2.8dB`)، برش بوکسی (`390Hz -1.8dB`)، شفافیت و هوای ابریشمی کاندنسر (`3600Hz +2.2dB` و `9200Hz +2.4dB`)، کمپرسور اپتیکال نرم LA-2A و بازتاب سه‌بعدی گرم استودیویی (`18ms pre-delay`، بدون اکوهای هم‌پوشان و بدون برش انتهای کلمات) با فیلد `"vocal_fx_enhanced": true` در مانیفست!
2. **موسیقی متن چندبخشی روی شبکه ضرب (`BPM Beat-Grid`):** تولید موسیقی ارکسترال/الکترونیک چندحالته با `FluidSynth` (مثلاً `106 BPM` همگام با تپش کلمات روی تصویر) همراه با `Sidechain Ducking` خودکار زیر صدای گوینده.
3. **افکت صوتی اختصاصی برای تک‌تک ضربات تایپوگرافی و ترنزیشن‌ها:** هر ۴۰+ ضربه تایپوگرافی (`Slam`, `Pop`, `Slice`, `Glitch`, `Marker Wipe`, `Odometer`) و هر ترنزیشن `gl-transitions` باید افکت صوتی استریوی همگام (`Pan` شده به چپ/راست مطابق مکان متن!) داشته باشد و میکس نهایی دقیقاً روی استاندارد یوتیوب **`-14.0 LUFS`** مستر شود.

---

### ستون ۷ — معماری کارگردانی، هویت برند پویا و بسته‌بندی انتشار (`youtube-video-skills` + `tiktok-video-skills` + `b-roll-skills` + `motion-video-director`)
- **تطبیق هوشمند با هر کانال، برند یا فرمت هدف:** این استاندارد بر **تمام ویدیوهای محیط کاری** حاکم است (در صورت مشخص بودن برند یا کانال — مثلاً «چی میشه؟» `@ChiMisheTV` یا هر برند/پیج دیگر — روایت از زبان اول‌شخص همان رسانه انجام می‌شود و هرگز لحن گزارشگر خشک بیرونی ندارد).
- **پشتیبانی کامل از تمام ابعاد استاندارد:** افقی سینمایی/یوتیوب (`1920×1080`)، عمودی شورتس/ریلز/تیک‌تاک (`1080×1920` با رعایت نواحی امن رابط کاربری موبایل از `tiktok-video-skills`) و مربعی (`1080×1080`).
- **ساختار اجباری نگهداشت مخاطب:** **قلاب شوک ثانیه صفر (`0.0s Cold Open`)** ➔ **کالبدشکافی بصری و داده‌محور با برش‌های `J-Cut / L-Cut` و `Punch-Zoom`** ➔ **فراخوان تعاملی هوشمند (در صورت نیاز پلتفرم)** ➔ **اوج تحلیلی / جمع‌بندی کوبنده با رعایت `Safe Zones` پایانی**.
- در پروژه‌های پلتفرمی/یوتیوبی: تحویل کاور/تامبنیل سینمایی سه‌بعدی `<svg>` فلزی (تست‌شده در ابعاد کوچک موبایل) + پکیج سئو در صورت درخواست یا اقتضای پلتفرم.

---

### ستون ۸ — اجرای اجباری شلاق بازرس خودکار (`whip_enforcer.py`) + بازبینی بصری فریم‌ها (`read_file`)
هیچ کلیپی در این محیط کاری حق ارائه به کاربر (`present_file`) را ندارد مگر اینکه **هر دو مرحله بازرسی زیر با وضعیت `100% ALL GATES PASSED` ثبت شوند:**
1. اجرای بازرس خودکار سراسری استودیو:
   ```bash
   PYTHONPATH=/home/user/animation-studio/runtime/pylibs \
     python3 /home/user/animation-studio/skills/studio-master-orchestrator/whip_enforcer.py \
     --manifest /var/tmp/beats_manifest.json \
     --video /home/user/<OUTPUT_VIDEO>.mp4 \
     --thumb /home/user/<OUTPUT_THUMB>.jpg
   ```
   *(پارامتر `--thumb` در ویدیوهایی که کاور جداگانه دارند بررسی می‌شود و برای فرمت‌های `1920x1080`، `1080x1920` و `1080x1080` به صورت خودکار اعتبارسنجی می‌گردد.)*
2. استخراج حداقل **۴ فریم واقعی از فایل MP4 نهایی** (شامل صحنه نقشه، صحنه ایزومتریک/چارت، صحنه تایپوگرافی کوبشی و صحنه پایانی) + تصویر تامبنیل و مشاهده مستقیم آن‌ها با ابزار `read_file` پیش از پاک‌سازی `/var/tmp`.
