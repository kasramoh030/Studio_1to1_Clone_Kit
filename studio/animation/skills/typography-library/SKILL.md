---
name: typography-library
description: Studio Typography Arsenal — 420 named, render-ready typography presets for YouTube 16:9, YouTube Thumbnails, YouTube Shorts, Instagram Reels, Instagram Stories, Instagram Carousels and TikTok, generated from 32 verified Persian-RTL fonts x 18 Latin display/mono fonts x 14 layouts x 9 fills x 10 effects x 16 GSAP motions x 15 palettes.
---

# کتابخانه تایپوگرافی استودیو (Studio Typography Arsenal)

**۴۲۰ پریست نام‌دار، آماده‌ی رندر و مستندشده** برای ۷ پلتفرم — تولیدشده توسط
`tools/typography_engine.py` و بازبینی‌شده با شیت‌های نمونه واقعی
(`specimens/typography_specimen_sheet_01..04.jpg`) که متن فارسی را با **HarfBuzz/raqm** واقعی شکل می‌دهند.

## فایل‌ها
| فایل | نقش |
|---|---|
| `catalog.json` | کاتالوگ کامل ماشین‌خوان: هر پریست با `id`, `platform`, `canvas`, `safe_zone_px`, `fonts` (فایل TTF دقیق), `sizes`, `palette`, `layout`, `fill`, `effect`, `motion`, `css` و رسیپی `gsap`. |
| `INDEX.md` | فهرست خوانا، جدول پالت‌ها و جدول موشن‌ها + جدول کامل ۴۲۰ پریست به تفکیک پلتفرم. |
| `specimens/*.jpg` | ۴ شیت نمونه‌ی چشمی برای کنترل کیفیت و انتخاب سریع سبک. |

## ۷ پلتفرم و محدوده‌های امن
| کلید | ابعاد | محدوده امن (T/R/B/L) | حداکثر کاراکتر |
|---|---|---|---|
| `yt_16x9` | 1920×1080 | 96/96/96/160 | 34 |
| `yt_thumb` | 1920×1080 | 80/80/120/220 | 22 |
| `yt_shorts` | 1080×1920 | 88/88/300/420 | 24 |
| `ig_reels` | 1080×1920 | 96/96/280/440 | 24 |
| `ig_story` | 1080×1920 | 120/120/250/380 | 26 |
| `ig_carousel` | 1080×1350 | 80/80/120/180 | 30 |
| `tiktok` | 1080×1920 | 100/100/360/480 | 22 |

## ۱۴ لایه‌بندی (Layouts)
`stacked_center` · `strip_highlight` · `split_diagonal` · `big_number_hero` · `quote_card` · `lower_third` · `kinetic_list` · `vertical_stack_side` · `badge_burst` · `outline_extrude` · `marquee_band` · `sticker_collage` · `caption_bar` · `giant_bleed_word`

## ۹ حالت پرشدگی (Fills)
`solid` · `grad_neon` · `duotone_split` · `highlighter` · `outline_only` · `stroke_fill` · `chrome` · `paper_cut` · `hollow_shadow`

## ۱۰ افکت (Effects)
`hard_shadow` · `long_shadow` · `glow` · `chroma` · `bevel` · `ink_bleed` · `neon_tube` · `sticker_border` · `glitch_slice` · `halftone`

## ۱۶ موشن GSAP (همگی فریم‌دقیق و کلید‌محور)
`mask_wipe_rtl` · `per_word_pop` · `flip_3d_y` · `blur_in` · `elastic_scale` · `typewriter_caret` · `rise_stagger` · `letter_stagger` · `velocity_skew` · `odometer` · `split_curtain` · `tracker_snap` · `punch_in` · `shake_settle` · `mask_lines` · `drop_in_gravity`

## ۱۵ پالت
`crimson_alert` · `gold_black` · `electric_cyan` · `acid_lime` · `violet_pulse` · `orange_heat` · `paper_bone` · `mint_bank` · `steel_graphite` · `rose_shock` · `amber_tape` · `ultramarine` · `terminal_green` · `sand_ink` · `white_void`

## آرژانت فونت (۵۰ فونت TTF، همگی تأییدشده)
- **فارسیٔ کامل (۳۲):** Lalezar, Vazirmatn (۹ وزن), Sahel, Samim, Parastoo, Tanha, Estedad (۵ وزن), Shabnam-FD (۳), Changa, Harmattan, Markazi Text, Mirza, Rubik, Alexandria, Noto Nastaliq Urdu, Vazir-Code-FD, Vazir-Code-Hack-FD
- **Display لاتین (۱۴):** Anton, Bebas Neue, Archivo Black, Inter Tight XBold, Space Grotesk, Oswald, Syne, Montserrat, Doto Black, Instrument Serif, Fraunces, Space Mono
- **Mono/تلمتری (۵):** JetBrains Mono, Fira Code, IBM Plex Mono, Vazir Code, Vazir Code Hack

## استفاده در پایپ‌لاین رندر
```bash
# فهرست/بازسازی کاتالوگ
python3 /home/user/animation-studio/tools/typography_engine.py --build
# CSS + رسیپی GSAP یک پریست
python3 /home/user/animation-studio/tools/typography_engine.py --css yt_thumb__youtube_poster__strip_highlight__highlighter__07
```
در نسل ریتم تصویر: پریست را از `catalog.json` بردار، `css` را داخل `stage.html` تزریق کن،
`fonts[].fa_file` و `fonts[].en_file` را با `@font-face` بومی لود کن و رسیپی `gsap` را با
`window.renderFrame(t, frame, total)` هم‌زمان کن. متن هرگز نباید از `safe_zone_px` بیرون بزند.

> **قانون**: هر متن فارسی فقط با فونت‌های «فارسی کامل» بالا؛ فونت‌های Display لاتین مجاز به رندر
> حروف فارسی نیستند. الفبای لاتین/عدد فقط با `EN_DISPLAY` و `mono` رندر می‌شود.
