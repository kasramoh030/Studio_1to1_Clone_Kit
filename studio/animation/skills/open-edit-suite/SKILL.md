---
name: open-edit-suite
description: VEED Open Edit agent skill — EDL-driven editing, cut procedure, fabrication constraints, transcription pipeline and export checks (CLI login not required to use the editorial doctrine).
---

# Open Edit Suite (VEED)

منبع: `https://github.com/veedstudio/open-edit`

| فایل | نقش |
|---|---|
| `open-edit/SKILL.md` | رویه کامل ادیت با EDL: انتخاب تیک، ساخت EDL، اعمال، رندر |
| `open-edit/CUT.md` | قواعد برش: نگه‌داشتن مرز کلمات، حذف سکوت، ریتم |
| `open-edit/FABRIC.md` | محدودیت‌های ساخت (عدم جعل فریم، عدم کشش زمان) |
| `open-edit/TRANSCRIPTION.md` | پایپ‌لاین رونویسی و تایمینگ کلمه برای زیرنویس |
| `open-edit/VEED.md` | سطح دستورات CLI و ورودی/خروجی |
| `_core/` | `README.md`, `SETUP.md`, `AGENTS.md` |

## استفاده در استودیو
- **بدون نیاز به لاگین VEED**: فقط دکترین برش/EDL و چک‌لیست خروجی استفاده می‌شود؛ رندر ما همان `HTML→Chromium→FFmpeg` است.
- قاعده `CUT.md` برای برش نریشن `voice-05` روی مرز جمله و ساخت `EDL` برای بازسازی سریع تایم‌لاین به کار می‌رود.
