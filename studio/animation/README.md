# استودیوی انیمیشن‌سازی حرفه‌ای (Animation Studio)

این ورک‌اسپیس به همراه ابزارهای سیستمی خارج از ورک‌اسپیس برای تولید انواع انیمیشن‌های دوبعدی، سه‌بعدی، موشن‌گرافیک، علمی/ریاضی و شیدر محور آماده شده است.

## موتورها و ابزارهای نصب‌شده

### ۱. موتورهای سیستمی و رندرینگ (خارج از ورک‌اسپیس)
- **FFmpeg 7.1**: کدک‌های H.264، H.265/HEVC، VP9/WebM، ProRes، فیلترهای پیشرفته کامپوزیت و میکس صدا
- **Blender 4.3 (Headless CLI)**: رندر سه‌بعدی واقعی با موتورهای Cycles و EEVEE، سیستم ذرات و Geometry Nodes
- **Chromium 156 + WebGL2 (SwiftShader/ANGLE) + Xvfb**: رندر فریم‌به‌فریم ۶۰ فریم‌برثانیه صحنه‌های وب، شیدرهای GLSL و Three.js
- **Cairo, Pango, Librsvg, ImageMagick, Potrace**: پردازش برداری (SVG) و رندر متن‌های فارسی/لاتین
- **TeX Live + dvisvgm**: رندر فرمول‌ها و انیمیشن‌های علمی در Manim
- **SoX + Librosa + Pydub**: طراحی افکت صوتی (SFX) و انیمیشن‌های Audio-Reactive هماهنگ با موج صدا
- **فونت‌های فارسی و انگلیسی**: خانواده کامل `Vazirmatn`، `Noto`، `Noto Color Emoji` و `Fira Code`

### ۲. پشته پایتون (Python 3.13)
- `manim` (نسخه ۰.۲۲) + `ManimPango` برای انیمیشن‌های برداری، سینمایی و آموزشی
- `moviepy`، `av` (PyAV)، `imageio-ffmpeg`، `opencv-python` برای تدوین و پردازش ویدیو
- `moderngl` + `trimesh` برای رندر شیدرهای OpenGL و هندسه سه‌بعدی
- `pycairo`، `cairosvg`، `drawsvg`، `svgpathtools`، `shapely`، `lottie` برای گرافیک برداری و مورفینگ
- `arabic-reshaper` و `python-bidi` برای اتصال صحیح حروف فارسی در تمام موتورهای گرافیکی
- `opensimplex` برای حرکت‌های ارگانیک و نویز رویه‌ای (Procedural Noise)
- `playwright` برای اتوماسیون و ضبط صحنه‌ها

### ۳. پشته وب، موشن‌گرافیک و سه‌بعدی (`animation-studio/`)
- **Remotion 4.0** (`remotion`, `@remotion/cli`, `@remotion/three`, `@remotion/transitions`, `@remotion/motion-blur`, `@remotion/shapes`, `@remotion/paths`, `@remotion/noise`)
- **Three.js + React Three Fiber + Drei + Postprocessing** (بلوم، عمق میدان، شیدرهای سه‌بعدی)
- **GSAP 3** (به همراه `CustomEase` و `MotionPathPlugin`)
- **PixiJS 8**، **Framer Motion**، **Anime.js**، **Lottie-Web**، **D3.js**
- پوشه `vendor/` و `assets/fonts/` برای اجرای آفلاین و پایدار فایل‌ها در پیش‌نمایش

## ابزارهای کمکی آماده در پروژه
- `tools/render_web_video.mjs`: تبدیل قطعی (Deterministic Frame-by-Frame) انیمیشن‌های HTML/Canvas/Three.js/GSAP به ویدیوی `MP4` با کیفیت بالا و نرخ ۶۰ فریم‌برثانیه
- `tools/persian_text.py`: ماژول آماده‌سازی متن فارسی و مسیر فونت‌های وزیرمتن
- `setup.sh`: اسکریپت نصب مجدد خودکار در صورت ری‌استارت محیط سیستم‌عامل
