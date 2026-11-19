# مخزن جامع ۷۰۰ سبک تایپوگرافی و انیمیشن یوتیوب و اینستاگرام (v2.0 Mega Arsenal)

- **تعداد کل پریست‌های آماده رندر:** `700` سبک مجزا (`100` سبک اختصاصی برای هر یک از ۷ پلتفرم)
- **ماتریس طراحی:** `18` خانواده سبکی × `24` الگوی صفحه‌آرایی × `14` متریال رنگ × `16` افکت نوری/چاپی × `28` منحنی حرکتی GSAP/GPU × `24` پالت رنگی استاندارد

| پلتفرم | تعداد سبک | ابعاد | محدوده امن (Safe Zone) |
|---|---|---|---|
| `yt_16x9` — YouTube 16:9 Documentary (1920x1080) | **100** | `1920×1080` | `T:90 R:96 B:110 L:140` |
| `yt_thumb` — YouTube High-CTR Thumbnail (1920x1080) | **100** | `1920×1080` | `T:72 R:76 B:120 L:200` |
| `yt_shorts` — YouTube Shorts 9:16 (1080x1920) | **100** | `1080×1920` | `T:140 R:88 B:340 L:88` |
| `ig_reels` — Instagram Reels 9:16 (1080x1920) | **100** | `1080×1920` | `T:150 R:92 B:360 L:92` |
| `ig_story` — Instagram Story 9:16 (1080x1920) | **100** | `1080×1920` | `T:160 R:96 B:300 L:96` |
| `ig_carousel` — Instagram Carousel 4:5 (1080x1350) | **100** | `1080×1350` | `T:84 R:84 B:130 L:84` |
| `tiktok` — TikTok Vertical 9:16 (1080x1920) | **100** | `1080×1920` | `T:150 R:96 B:380 L:96` |

## ۱۸ خانواده سبکی (Style Families) و انیمیشن‌های امضای هر سبک

| خانواده سبکی | فونت‌های فارسی منتخب | انیمیشن‌های اختصاصی هر سبک |
|---|---|---|
| `broadcast_hard` | Lalezar, Vazirmatn Black, Sahel Black | `punch_in`, `mask_wipe_rtl`, `split_curtain` |
| `youtube_poster` | Lalezar, Vazirmatn Black, Estedad Black | `punch_in`, `shake_settle`, `elastic_scale` |
| `vox_editorial` | Markazi Text, Vazirmatn Bold, Sahel Black | `vox_highlighter`, `mask_wipe_rtl`, `rise_stagger` |
| `hormozi_reels_pop` | Lalezar, Vazirmatn Black, Shabnam Bold | `hormozi_box_jump`, `per_word_pop`, `elastic_scale` |
| `news_ticker` | Samim Bold, Shabnam Bold, Changa | `velocity_skew`, `mask_lines`, `tracker_snap` |
| `fintech_ui` | Vazirmatn Black, Estedad Black, Vazirmatn SemiBold | `odometer`, `blur_in`, `continuous_onetake` |
| `street_sticker` | Lalezar, Shabnam Bold, Tanha | `rubber_stamp_crush`, `per_word_pop`, `shake_settle` |
| `telemetry_code` | Vazir Code, Vazir Code Hack, Changa | `typewriter_caret`, `glitch_rgb_decode`, `split_flap_clack` |
| `cinema_trailer` | Vazirmatn Black, Estedad ExtraBold, Sahel Black | `zoom_portal_thru`, `prism_shatter_in`, `blur_in` |
| `calligraphic_heritage` | Noto Nastaliq Urdu, Mirza Bold, Parastoo Bold | `blur_in`, `rise_stagger`, `continuous_onetake` |
| `playful_energy` | Shabnam Bold, Tanha, Lalezar | `drop_in_gravity`, `elastic_scale`, `pendulum_swing_in` |
| `noir_investigation` | Markazi Text, Sahel Black, Parastoo Bold | `rubber_stamp_crush`, `typewriter_caret`, `mask_wipe_rtl` |
| `ft_data_journalism` | Markazi Text, Vazirmatn Bold, Estedad Bold | `odometer`, `vox_highlighter`, `rise_stagger` |
| `neon_cyber_night` | Estedad Black, Changa, Vazirmatn Black | `neon_flicker_on`, `glitch_rgb_decode`, `echo_triple_stack` |
| `chalk_lecture` | Shabnam Bold, Shabnam Medium, Tanha | `chalk_stroke_draw`, `mask_wipe_rtl`, `rise_stagger` |
| `swiss_grid_modern` | Estedad Black, Estedad ExtraBold, Vazirmatn Bold | `split_curtain`, `mask_lines`, `tracker_snap` |
| `scoreboard_transit` | Changa, Vazirmatn Black, Vazir Code | `split_flap_clack`, `odometer`, `flip_3d_y` |
| `onetake_fluid_cam` | Vazirmatn ExtraBold, Estedad Black, Vazirmatn SemiBold | `continuous_onetake`, `zoom_portal_thru`, `velocity_skew` |

## ۲۸ موتور انیمیشن تایپوگرافی (GSAP + Python/GPU Curves)

| کد موشن | منحنی GPU/Python | مدت | Ease |
|---|---|---|---|
| `mask_wipe_rtl` | `wipe_rtl` | `0.52s` | `power4.out` |
| `per_word_pop` | `spring_pop` | `0.4s` | `back.out(2.4)` |
| `flip_3d_y` | `flip_3d` | `0.6s` | `expo.out` |
| `blur_in` | `rack_focus` | `0.66s` | `power3.out` |
| `elastic_scale` | `elastic_bounce` | `0.85s` | `elastic.out(1, 0.45)` |
| `typewriter_caret` | `typewriter` | `0.03s` | `none` |
| `rise_stagger` | `rise_up` | `0.52s` | `power3.out` |
| `letter_stagger` | `cascade` | `0.36s` | `power2.out` |
| `velocity_skew` | `whip_skew` | `0.48s` | `power4.inOut` |
| `odometer` | `odometer_roll` | `1.2s` | `power2.out` |
| `split_curtain` | `slice_pincer` | `0.68s` | `expo.inOut` |
| `tracker_snap` | `snap_lock` | `0.34s` | `back.out(3)` |
| `punch_in` | `stomp_slam` | `0.44s` | `power4.out` |
| `shake_settle` | `impact_tremor` | `0.76s` | `elastic.out(1.1, 0.32)` |
| `mask_lines` | `shutter_down` | `0.58s` | `power3.inOut` |
| `drop_in_gravity` | `gravity_drop` | `0.65s` | `bounce.out` |
| `hormozi_box_jump` | `karaoke_pop` | `0.28s` | `back.out(2.8)` |
| `vox_highlighter` | `marker_wipe` | `0.5s` | `expo.out` |
| `rubber_stamp_crush` | `stamp_slam` | `0.32s` | `power4.in` |
| `glitch_rgb_decode` | `glitch_rgb` | `0.42s` | `steps(6)` |
| `echo_triple_stack` | `echo_stack` | `0.56s` | `expo.out` |
| `zoom_portal_thru` | `zoom_through` | `0.62s` | `expo.inOut` |
| `split_flap_clack` | `split_flap` | `0.46s` | `steps(8)` |
| `neon_flicker_on` | `neon_ignite` | `0.54s` | `rough` |
| `chalk_stroke_draw` | `chalk_write` | `0.64s` | `power2.inOut` |
| `pendulum_swing_in` | `pendulum` | `0.74s` | `elastic.out(1, 0.5)` |
| `prism_shatter_in` | `prism_lock` | `0.5s` | `power4.out` |
| `continuous_onetake` | `onetake_glide` | `0.78s` | `power3.inOut` |
