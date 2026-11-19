---
name: mega-style-vfx-arsenal
description: Unified 1,100+ Typography/Motion Styles & 835+ GPU/Frei0r/LYGIA VFX Arsenal for YouTube 16:9, Shorts, Instagram Reels, Stories & Carousels.
---

# مخزن جامع استودیو: تایپوگرافی، سبک‌های یوتیوب/اینستاگرام و جلوه‌های ویژه (Mega Style & VFX Arsenal v2.0)

## خلاصه ظرفیت فعال و آماده رندر استودیو
- **مجموع کل سبک‌های تایپوگرافی، کپشن و کارگردانی بصری:** **`1145` سبک آماده**
  - `700` پریست تایپوگرافی متحرک (`100` سبک اختصاصی برای هر یک از ۷ پلتفرم یوتیوب، شورتس، ریلز، استوری، کاروسل و تیک‌تاک)
  - `287` الگوی مهندسی‌شده موشن‌گرافیک (`openmotion-motion-library`)
  - `99` سبک سینمایی، مستند و چاپی (`Favstash Animated Film Styles`)
  - `35` هویت کپشن و زیرنویس صحنه‌محور (`LangChain Embedded Captions`)
  - `24` استایل کارگردانی اختصاصی کریتورها (Johnny Harris, Vox, MagnatesMedia, Hormozi, Iman Glass, Bloomberg, FT, Manim, OneTake, ChiMishe Bazaar...)
- **مجموع کل انیمیشن‌ها، ترنزیشن‌ها و جلوه‌های ویژه (VFX):** **`835` افکت و شیدر واقعی**
  - `265` ترنزیشن OpenGL GLSL روی GPU (`ModernGL EGL`)
  - `378` ماژول شیدر سینمایی `LYGIA` (نور، بلوم، لنز، رنگ ACES، نویز، اعوجاج)
  - `156` پلاگین پردازش تصویر `frei0r-1` به زبان C++ متصل به FFmpeg
  - `36` افکت ویژه آنی پایتون/GPU (`apply_procedural_vfx`)
- **فونت‌های فارسی و لاتین تاییدشده در Fontconfig/HarfBuzz:** **`56` فایل فونت**
- **پکیج‌های مهارت تخصصی نصب‌شده در استودیو:** **`32` پکیج کامل**

## ۲۴ استایل کارگردانی مرجع (همراه با انیمیشن و VFX اختصاصی هر سبک)

| شناسه سبک (`id`) | دسته‌بندی | فونت فارسی | انیمیشن امضای سبک | ترنزیشن‌های GPU | جلوه‌های ویژه (VFX) | کاربرد |
|---|---|---|---|---|---|---|
| `johnny_harris_geo_noir` | `yt_documentary` | Lalezar | `marker_wipe + zoom_portal_thru` | `CrossZoom, BurnThrough` | `aces_filmic, map_glow` | سبک مستند تحقیقی نقشه‌محور با عکس آرشیوی، هایلایت ماژیکی زرد و زوم عمیق دوربین |
| `magnates_red_cinema` | `yt_documentary` | Vazirmatn Black | `punch_in + rubber_stamp_crush` | `BurnThrough, GlitchMemories` | `crimson_rim_glow, aces_filmic` | سبک سینمایی تیره و پرتعلیق داستان‌های امپراتوری مالی و بحران‌های بزرگ |
| `vox_archival_paper` | `yt_explainer` | Sahel Black | `vox_highlighter + mask_wipe_rtl` | `DirectionalWarp, PageCurl` | `paper_grain, halftone_shadow` | سبک تحلیلی روشن روی کاغذ روزنامه‌ای گرم با ماژیک زرد و بریده‌های مستند |
| `lemmino_cold_dossier` | `yt_documentary` | Estedad Black | `blur_in + tracker_snap` | `BokehDissolve, BloomDissolve` | `rack_focus_bloom, cold_steel_lut` | سبک معمایی مینیمال و فوق‌دقیق با فوکوس نوری نرم و تایپوگرافی مهندسی |
| `bloomberg_data_terminal` | `fintech_econ` | Changa | `odometer + split_flap_clack` | `Pixelize, GlitchMemories` | `crt_phosphor_glow, hud_grid` | ترمینال مالی زنده با شمارنده‌های مکانیکی، کندل‌استیک و تیکر سبز/نارنجی |
| `ft_origami_salmon` | `fintech_econ` | Markazi Text | `rise_stagger + odometer` | `DirectionalWarp, Swap` | `editorial_matte, paper_fiber` | سبک رسمی فایننشال‌تایمز برای نمودارهای کلان اقتصادی و مقایسه‌های آماری |
| `economist_red_briefing` | `fintech_econ` | Estedad ExtraBold | `split_curtain + mask_lines` | `Accordion, DirectionalWarp` | `sharp_unsharp_mask, economist_top_rule` | سبک تحلیلی اکونومیست با نوار قرمز امضادار بالا و سلسله‌مراتب خبری تیز |
| `manim_3b1b_intuition` | `science_math` | Vazirmatn ExtraBold | `chalk_stroke_draw + continuous_onetake` | `BloomDissolve, CircleOpen` | `vector_neon_bloom, grid_coordinate_plane` | سبک فرمول‌محور و هندسی الهام‌گرفته از Manim برای کالبدشکافی مکانیزم‌های اقتصادی |
| `persian_street_bazaar` | `yt_documentary` | Lalezar | `punch_in + vox_highlighter + shake_settle` | `BurnThrough, CameraShake` | `aces_filmic, warm_bazaar_gold` | سبک اختصاصی «چی می‌شه؟» با ترکیب عکس واقعی بازار ایران، فونت لاله‌زار و هشدارهای خیابانی |
| `tehran_archival_1923` | `historical_doc` | Parastoo Bold | `rubber_stamp_crush + typewriter_caret` | `BurnThrough, FilmBurn` | `sepia_silver_lut, film_grain_16mm` | سبک آرشیو تاریخی مستند (آلمان ۱۹۲۳، مجارستان ۱۹۴۶) با گرین فیلم ۱۶ میلی‌متری و مهر پرونده |
| `hormozi_viral_pop` | `ig_reels_viral` | Lalezar | `hormozi_box_jump + per_word_pop` | `CrossZoom, ZoomInCircles` | `heavy_stroke_shadow, punch_zoom_beat` | سبک وایرال پرانرژی کلمه‌به‌کلمه با باکس‌های رنگی پرشی سبز/زرد و ضرب‌آهنگ تند |
| `iman_minimal_glass` | `ig_reels_viral` | Estedad ExtraBold | `blur_in + continuous_onetake` | `BokehDissolve, BloomDissolve` | `skia_frosted_glass, soft_halation` | سبک لوکس و مینیمال شیشه‌ای (Glassmorphism) با کارت‌های بلورین شناور و نورپردازی نرم |
| `ali_abdaal_pastel_desk` | `ig_explainer` | Shabnam Bold | `elastic_scale + per_word_pop` | `DirectionalWarp, Bounce` | `clean_soft_shadow, rounded_ui_cards` | سبک آموزشی دوستانه و فوق‌شفاف با کارت‌های گرد، اعداد فارسی شبنم و انیمیشن فنری |
| `cyber_glitch_alert` | `ig_reels_viral` | Changa | `glitch_rgb_decode + velocity_skew` | `GlitchMemories, GlitchDisplace` | `rgb_chromatic_split, glitch_slice_bars` | سبک شوک سایبری و هشدار فوری با گلیچ RGB، برش‌های دیجیتال و تایپ سریع |
| `kinetic_stomp_takeover` | `kinetic_promo` | Vazirmatn Black | `punch_in + echo_triple_stack` | `CameraShake, Flash` | `impact_flash, screen_tremor` | سبک کوبشی تمام‌صفحه (Stomp) مخصوص هوک ۳ ثانیه اول با لرزش دوربین و تکرار سه‌گانه تیتر |
| `onetake_continuous_journey` | `cinema_launch` | Estedad Black | `continuous_onetake + zoom_portal_thru` | `DreamyZoom, CrossZoom` | `motion_blur_shutter, depth_of_field_layers` | سبک حرکت پیوسته بدون کات مرئی؛ هر صحنه از دل صحنه قبلی بیرون می‌آید |
| `chalkboard_masterclass` | `edu_board` | Tanha | `chalk_stroke_draw + vox_highlighter` | `WipeLeft, Directional` | `chalk_dust_particles, blackboard_slate_texture` | سبک کلاس درس دانشگاهی روی تخته‌سیاه سبز تیره با رسم خط‌به‌خط گچی و زیرخط زرد |
| `blueprint_system_cutaway` | `tech_diagram` | Sahel Black | `mask_lines + tracker_snap` | `GridFlip, DirectionalWarp` | `cyanotype_grid, hairline_callouts` | سبک نقشه مهندسی آبی‌پروس برای تشریح زنجیره تأمین، بانک مرکزی و جریان نقدینگی |
| `scoreboard_split_flap` | `fintech_econ` | Changa | `split_flap_clack + odometer` | `GridFlip, Flip` | `metallic_tile_bevel, amber_led_dotmatrix` | سبک تابلو اعلانات مکانیکی فرودگاه و تالار بورس با چرخش سه‌بعدی حروف و اعداد |
| `vhs_camcorder_evidence` | `historical_doc` | Samim Bold | `glitch_rgb_decode + typewriter_caret` | `GlitchMemories, TvStatic` | `vhs_tracking_bars, rec_osd_overlay` | سبک دوربین مستند خیابانی VHS با نشانگر REC چشمک‌زن، تایم‌کد و نویز نوار مغناطیسی |
| `ransom_zine_collage` | `street_culture` | Lalezar | `rubber_stamp_crush + drop_in_gravity` | `BurnThrough, RandomSquares` | `paper_cutout_drop_shadow, halftone_grain` | سبک کلاژ تکه‌روزنامه و برچسب‌های بریده‌شده با زاویه‌های تند و سایه سخت چاپی |
| `swiss_international_grid` | `editorial_design` | Estedad Black | `split_curtain + mask_wipe_rtl` | `WipeLeft, Directional` | `modular_grid_lines, high_key_crisp` | سبک تایپوگرافی مدرن سوئیسی با گرید ماژولار دقیق، فضای منفی وسیع و یک رنگ سیگنال |
| `neon_night_signage` | `mood_cinema` | Lalezar | `neon_flicker_on + blur_in` | `BloomDissolve, BokehDissolve` | `multi_pass_neon_bloom, wet_street_reflection` | سبک تابلوهای نئون شبانه در خیابان خیس با سوسوزدن اولیه لوله نئون و هاله صورتی/فیروزه‌ای |
| `nastaliq_poetic_gold` | `heritage_luxury` | Mirza Bold | `blur_in + rise_stagger` | `BloomDissolve, BokehDissolve` | `gold_shimmer_particles, warm_candle_vignette` | سبک ادبی و تاریخی فاخر ایرانی با خوشنویسی میرزا/نستعلیق، ورق طلا و ذرات نور معلق |
