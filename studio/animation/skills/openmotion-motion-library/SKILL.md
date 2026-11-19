---
name: openmotion-motion-library
description: 287 Motion.md creative specs + 24 runnable HTML/CSS/JS implementations extracted from OpenMotion's template catalog — a browsable library of real motion studies (palettes, durations, beat structures) for reference and remix.
---

# OpenMotion Motion Library (۲۸۷ اسپک + ۲۴ پیاده‌سازی)

منبع: `nexu-io/openmotion` → `library/templates/catalog`

- `index.json` — فهرست ماشین‌خوان ۲۸۷ استادی موشن: `id`, `title`, `duration_s`, `palette[]`, `has_source`, مسیر `motion.md`
- `specs/*.md` — متن کامل Motion.md هر استادی (ترتیب reveal، دوربین، ریتم خواندن، صدا)
- `implementations/<id>/` — ۲۴ پیاده‌سازی واقعی HTML/CSS/JS برای موشن‌های سبک‌تر (بدون تصویر) به‌عنوان مرجع کد

## نحوه استفاده
1. با `index.json` یک استادی هم‌خانواده با موضوع قسمت انتخاب کن (مثلاً داده‌محور، تایپوگرافی مونو، ریویل شبکه‌ای).
2. `specs/<id>.md` را بخوان و **زبان موشن** را (نسبت‌ها، ترتیب، تایمینگ) استخراج کن.
3. اگر `implementations/<id>/` وجود داشت، ساختار DOM/GSAP را الگو بگیر؛ در غیر این صورت با `motion-craft` بازسازی کن.
4. پالت و مدت‌زمان را با `typography-library` و پالت‌های استودیو هم‌تراز کن.

> این کتابخانه مرجع **الهام و ساختار** است؛ متن و برند همیشه فارسی و مخصوص کانال خودمان بازنویسی می‌شود. هیچ صدای محلی مجاز نیست (`voice-05` فقط).
