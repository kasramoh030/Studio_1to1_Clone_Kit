# کاتالوگ مخازن جلوه‌های ویژه نصب‌شده در استودیوی «چی میشه؟»

تمامی مخازن، شیدرها، موتورهای پایتونی و اسکیل‌های تخصصی زیر به صورت **دائمی (`Persistent`)** در مسیر `/home/user/animation-studio/` نصب، یکپارچه‌سازی و تست شده‌اند و برای ساخت تمام کلیپ‌های بعدی کانال آماده استفاده مستقیم هستند:

---

## ۱. مخزن ترنزیشن‌های سینمایی OpenGL (`gl-transitions` — ۲۶۵ شیدر GLSL)
- **مسیر:** `/home/user/animation-studio/vfx-repos/gl-transitions/`
- **کاربرد در کلیپ‌های ما:** کات‌های کوبشی و سینمایی بین صحنه‌های مستند بدون افت سرعت در GPU:
  - `BurnThrough.glsl` / `Burn.glsl`: سوختن تصویر اسکناس یا نمودار و ورود به صحنه بعد
  - `CameraShake.glsl` / `Impact`: لرزش سنگین لنز در لحظه اعلام اعداد شوک‌آور
  - `GlitchMemories.glsl` / `GlitchDisplace.glsl`: افکت گلیچ و بحران سایبری/مالی
  - `BloomDissolve.glsl` / `BokehDissolve.glsl`: فلاش نوری طلایی و بوکه سینمایی
  - `CrossZoom.glsl` / `DreamyZoom.glsl` / `ZoomInCircles.glsl`: زوم سرعتی (`Whip-Zoom`) بین نیویورک و تهران
  - `ApertureWipe.glsl` / `Radial.glsl` / `Swirl.glsl`: باز شدن دیافراگم دوربین و چرخش فضایی

---

## ۲. کتابخانه شیدرهای حرفه‌ای جلوه‌های نوری و ذرات (`LYGIA Shader Library` — ۳۷۸ ماژول GLSL)
- **مسیر:** `/home/user/animation-studio/vfx-repos/lygia/`
- **کاربرد در کلیپ‌های ما:**
  - `filter/bloom` و `filter/radialBlur`: درخشش شمش‌های طلا، شعله سکوهای نفتی و تاری حرکت شعاعی
  - `filter/chromaticAberration` و `distort/barrel`: خطای رنگی لنز آنامورفیک سینمایی در لبه‌های کادر
  - `generative/fbm` و `generative/curl`: تولید زنده دود، مه، آتش، صاعقه و میدان حرکت ذرات معلق
  - `color/tonemap` (`ACES` / `Filmic`): اصلاح رنگ سینمایی هالیوودی

---

## ۳. موتورهای رندر و کامپوزیت کدپایه (`ReelForge` + `Movis` + `vfx_studio.py`)
- **پل ارتباطی مستقیم GPU:** `/home/user/animation-studio/vfx_studio.py`
  - اجرای هر کدام از ۲۶۵ ترنزیشن و شیدرهای LYGIA با یک خط کد پایتون روی `ModernGL (EGL)`.
- **موتور `ReelForge` (`/home/user/animation-studio/skills/reelforge`):**
  - چارچوب ساخت ویدیو با پایتون و شیدرهای سه‌بعدی OpenGL، موشن‌بلور واقعی، بلوم و همگام‌سازی ضرب موسیقی (`BPM Grid`).
- **موتور `Movis` (`/home/user/animation-studio/runtime/pylibs/movis`):**
  - موتور لایه‌بندی مشابه After Effects در پایتون (Blending Modes، سایه، Glow، ماسک و کی‌فریم‌های نرم).

---

## ۴. پکیج اسکیل‌های تخصصی مستندسازی اقتصادی و ژئوپلیتیک (`/home/user/animation-studio/skills/`)
1. **`map-animation-skills` (نقشه‌های متحرک ژئوپلیتیک به سبک Vox / Johnny Harris):**
   - زوم ماهواره‌ای روی ایران، تنگه هرمز، نیویورک و مسیر نفتکش‌ها، هایلایت مرزها و خطوط راداری.
2. **`data-animation-skills` و `motion-design-skills/data-story-charts` (انیمیشن نمودارهای مالی):**
   - رسم زنده کندل‌های طلا و دلار، تغییر مقیاس ناگهانی محور نمودار برای ایجاد شوک (`Axis Rescale Surprise`) و نمودارهای مقایسه‌ای قدرت خرید.
3. **`motion-design-skills/system-diagram-animation` (دیاگرام جریان پول و تحریم):**
   - نمایش متحرک چرخه چاپ پول، بدهی بانک‌های مرکزی و انتقال سرمایه به طلا.
4. **`kinetic-type-skills` + `kinetic-typography-rtl` (۸۰ تکنیک تایپوگرافی جنبشی + نسخه بومی فارسی):**
   - کوبش (`Stomp Slam`)، برش تیغه‌ای (`Slice`)، شمارشگر زنده (`Odometer`)، گلیچ (`Glitch`)، هایلایتر راست‌به‌چپ (`Marker Wipe`) و پرواز کلمات به سمت دوربین (`Zoom-Through`).
5. **`webgl-animation-skills` و `b-roll-skills`:**
   - صحنه‌های سه‌بعدی WebGL/Three.js و موشن‌گرافیک‌های مکمل روی صدای گوینده.

---

## ۵. تکمیل ۵ حلقه مفقوده استودیو (نصب‌شده در دور دوم ممیزی)
1. **نقشه‌های برداری دقیق آفلاین ایران و جهان (`/home/user/animation-studio/assets/geo/`):**
   - `iran_provinces.min.geojson` (مرز دقیق هر **۳۱ استان ایران** با نام فارسی برای نقشه‌های گرمایی تورم/مسکن و زوم روی تنگه هرمز و خوزستان) + `world_countries.geo.json` (مرز **۱۸۰ کشور جهان**).
2. **فونت پوستر و تیتر سینمایی فارسی (`Lalezar-Regular.ttf`):**
   - ذخیره‌شده در `/home/user/animation-studio/assets/fonts/Lalezar-Regular.ttf` در کنار خانواده کامل `Vazirmatn` برای تیترهای کوبشی و تامبنیل.
3. **موتور سینت‌سایزر صدا و کارگردانی تدوین (`skill-motion-graphic` + `motion-video-director`):**
   - موتور تولید افکت صوتی و Beat-Grid (`synth.mjs` و `sound.md`) + کامل‌ترین پلی‌بوک کارگردانی تدوین، Punch-Zoom، کات‌های J/L و متن پشت سوژه (`Text Behind Subject`).
4. **پکیج برندینگ یوتیوب و ساخت YouTube Shorts وایرال (`youtube-video-skills` + `tiktok-video-skills`):**
   - طراحی اینترو ۳ ثانیه‌ای، صفحه پایانی استاندارد یوتیوب (`End Screen Safe Zones`)، تایمر شمارش معکوس و تبدیل هر مستند بلند به کلیپ‌های عمودی `9:16` با زیرنویس کلمه‌به‌کلمه و نرخ نگهداشت بالا.
5. **انیمیشن‌های ایزومتریک سه‌بعدی و وایت‌برد (`explainer-video-skills`):**
   - ساخت مقایسه‌های حجمی `2.5D Isometric` (مثلاً مقایسه برج بدهی ۴۰ تریلیون دلاری با ذخایر طلا) و فلوچارت‌های اقتصادی مرحله‌به‌مرحله.

