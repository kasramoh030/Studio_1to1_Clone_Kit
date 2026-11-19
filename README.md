# Studio_1to1_Clone_Kit — موتور تولید کلیپ (Motion Graphics Studio)

این ریپازیتوری یک موتور کامل تولید ویدیو/موشن‑گرافیک برای اینستاگرام و یوتیوب است که شامل **دو استودیو ادغام‌شده** می‌باشد:

1. **استودیوی اصلی** (این ریپازیتوری) — 엔진 تولید کلیپ، SFX، BGM، ۵ اسکیل پردازش و اسکریپت یادآور چت
2. **استودیوی انیمیشن** (از ZIP پیوست) — ۵۶ فونت فارسی/لاتین، ۲۶۵ ترنزیشن GPU (`gl-transitions`)، ۳۷۸ ماژول `LYGIA`، ابزار رندر ۳ بعدی و ۳۲ پکیج مهارتی تخصصی

## ساختار فایل‌ها

```
studio/
  animation/          # استودیوی انیمیشن (از ZIP)
    vfx-repos/
      gl-transitions/ # ۲۶۵ شیدتر ترنزیشن OpenGL GLSL
      lygia/          # ۳۷۸ ماژول شیدتر سینمایی LYGIA
    assets/
      fonts/          # ۵۶ فونت (Vazirmatn, Lalezar, Estedad, Sahel, Shabnam و...)
      geo/            # نقشه‌های برداری ایران و جهان
    tools/, skills/, runtime/, vendor/
  _handoff/           # ابزارهای انتقال چت (handoff.py, recover_chat.py, AGENTS.md...)
engine/               # اینجن تولید کلیپ (۵ اسکیل)
  pipeline/
    warm_analog_vocal_mastering.py   # اسکیل ۱ — مسترینگ voz ۲۴k→۴۸k استریو
    italo_funk_120bpm_composer.py   # اسکیل ۲ — بدموزیک ۱۲۰ BPM
    six_sfx_cinema_vault.py          # اسکیل ۳ — ۶ SFX استریو ۴۸kHz
    whisper_word_sync_director.py    # اسکیل ۴ — همگام‌سازی کلمه‌به‌کلمه
    morph_broll_shader_engine.py     # اسکیل ۵ — ترنزیشن/مورف تصویر
  cli.py
assets/
  sfx/               # paper_slide, checklist_tick, epic_whoosh, impact, coin, bell_notification
  music/             # bgm_italo_funk_120bpm (Loop ۳۲s + ۱۵s)
scripts/
  install.sh                         # نصب وابستگی‌ها
  chat_reminder/chat_reminder.py     # یادآور محدودیت صفحه چت
  make_assets.py                     # تولید فایل‌های صدا (بدون ffmpeg)
```

## ۵ اسکیل پردازش (برasen بر STUDIO_PORTABLE_BLUEPRINT.md)

| # | اسکیل | وظیفه |
|---|-------|--------|
| ۱ | Warm Analog Vocal Mastering | تبدیل ۲۴kHz مونو → ۴۸kHz استریو، LADSPA + Pedalboard، قفل روی -۱۶ LUFS |
| ۲ | Italo-Funk 120 BPM Composer | بدموزیک چندتراک ۱۲۰ BPM (FluidSynth GM) |
| ۳ | Six-SFX Cinema Vault | ۶ افeket استریو ۴۸kHz (SFX) |
| ۴ | Whisper Word-Sync Director | همگام‌سازی کلمه‌به‌کلمه (faster-whisper) |
| ۵ | Morph B-Roll Shader Engine | frei0r + gl-transitions + LYGIA (ترنزیشن و مورف تصویر) |

## راه‌اندازی سریع

```bash
# ۱. نصب وابستگی‌ها
bash scripts/install.sh

# ۲. بررسی موتورها
python3 -m engine cli check-engines

# ۳. لیست افکت‌های صوتی
python3 -m engine cli list-sfx

# ۴. لیست ترنزیشن‌های GPU
python3 -m engine cli list-transitions

# ۵. رندر نمونه (اگر ffmpeg نصب باشد)
python3 -m engine cli render-sample --out /tmp/demo.mp4
```

## یادآور محدودیت صفحه چت

اگر صفحه چت به ليمیت برسد:

```bash
python3 scripts/chat_reminder/chat_reminder.py --check studio/_handoff/SESSION_STATE_LEDGER.json
```

سپس فایل `studio/_handoff/STUDIO_ARCHITECTURE_AND_TRAINING_GUIDE.md` را در چت جدید آپلود کنید و از `recover_chat.py --full-auto` برای بازیابی كامل ساختار استفاده کنید.

## نیازهای بیشتر؟

اگر ابزار یا اسکیل دیگری (مثلاً بلندر هدرلس، کپ‌кат‌قدرتی ۳ بعدی، افکت/Image/Video Morph بیشتر، افزودن موسیقی جدید و ...) نیاز دارید، بگویید تا اضافه کنیم.

---

ساخته شده برای إنتاج محتوای حرفه‌ای اینستاگرام ریلز و یوتیوب شورتس/ویدیو.
