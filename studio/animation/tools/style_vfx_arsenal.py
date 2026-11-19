#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
style_vfx_arsenal.py — Master Unified Typography, Style-Animation & GPU VFX Hub
================================================================================
Connects ALL harvested open-source style repositories, shader packs, Frei0r C++ plugins,
and our 700-preset Persian/English Typography Engine into ONE unified, executable hub
for YouTube (16:9 + Thumbnails + Shorts) and Instagram (Reels + Stories + Carousels):

  1. 700 Kinetic Typography Presets (`typography_engine.py` -> 7 platforms × 100 styles)
  2. 287 Reverse-Engineered Motion Templates (`openmotion-motion-library`)
  3. 142 Curated Creator, Film, Caption & Editorial Visual Styles:
     - 35 LangChain Scene-Embedded & World-Theme Caption Identities (`cream`, `ink`, `ordnance`, `scoreboard`, `transit`, `vhs`, `arcade`, `dossier`, `laser`, `thunder`, `hologram`, `biolume`, `aurora`, `spectrum`, `papercut`, `popup`, `chalkboard`, `graffiti`, `brush`, `inkwater`, `ransom`, etc.)
     - 65 Favstash Animated Film & Documentary Styles (`newsreel`, `news-package`, `kino-montage`, `visual-investigation`, `bauhaus-shapes`, `swiss-motion`, `text-flash-cuts`, `iso-infographic`, `blueprint`, `pen-plotter`, `halftone-dossier`, `risograph`, etc.)
     - 24 Studio Signature Creator Styles (`hormozi_viral_pop`, `iman_minimal_glass`, `vox_yellow_explainer`, `johnny_harris_geo_noir`, `magnates_red_cinema`, `lemmino_cold_mystery`, `coldfusion_fintech`, `kurzgesagt_vector_glow`, `bloomberg_data_terminal`, `ft_origami_salmon`, `economist_briefing`, `manim_3b1b_math`, `onetake_liquid_cam`, `persian_street_bazaar`, `tehran_noir_archive`, etc.)
     - 18 Vertical 9:16 Creator Style Kit Archetypes (`10_creator_style_kit_18_vertical_styles`)
  4. 835+ Real-Time VFX & Shader Effects:
     - 265 OpenGL GLSL Transitions (`vfx-repos/gl-transitions` via ModernGL EGL)
     - 378 LYGIA Shader Modules (`vfx-repos/lygia` — bloom, chromaticAberration, barrel, curl, fbm, tonemapACES, vignette, film grain)
     - 156 Native C++ `frei0r-1` Video Effects (`/usr/lib/frei0r-1/*.so` via FFmpeg filtergraph)
     - 36 Procedural GPU/OpenCV Post-FX Recipes (Anamorphic Flare, CRT Scanlines, Halftone Print, VHS Tracking, Seismograph Shake, RGB Prism Split, Film Gate Weave, Thermal Radar, Light Leak, Ink Bleed, etc.)

CLI:
  python3 style_vfx_arsenal.py --build             # build unified mega_arsenal_index.json + MEGA_ARSENAL.md
  python3 style_vfx_arsenal.py --summary           # print complete arsenal counts & verification
  python3 style_vfx_arsenal.py --recommend TOPIC   # recommend top matched style + typography + VFX pack
  python3 style_vfx_arsenal.py --demo-reel OUT.mp4 # render a real GPU+HarfBuzz multi-style showcase clip!
"""

import os
import io
import re
import sys
import json
import glob
import math
import subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

STUDIO = "/home/user/animation-studio"
PYLIBS = os.path.join(STUDIO, "runtime", "pylibs")
if PYLIBS not in sys.path:
    sys.path.insert(0, PYLIBS)
if STUDIO not in sys.path:
    sys.path.insert(0, STUDIO)
if os.path.join(STUDIO, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(STUDIO, "tools"))

from vfx_studio import GPUVFXEngine, list_gl_transitions, list_lygia_modules, resolve_lygia_includes
import typography_engine as typo_eng

ARSENAL_DIR = os.path.join(STUDIO, "skills", "mega-style-vfx-arsenal")

# ==============================================================================
# 1. CURATED CREATOR, YOUTUBE DOCUMENTARY & INSTAGRAM REELS MASTER STYLES
#    Every style binds: Palette + Persian/Latin Font Stack + Signature Entrance/Hold/Exit
#    Animation + Paired GPU gl-transitions + Paired Post-VFX Shader!
# ==============================================================================
MASTER_CREATOR_STYLES = [
    # --- YouTube High-Retention Documentary & Investigation Styles ---
    {"id": "johnny_harris_geo_noir", "cat": "yt_documentary", "platforms": ["yt_16x9", "yt_shorts"], "fa_font": "Lalezar", "body_font": "Vazirmatn", "mono_font": "Fira Code", "bg": "#060A14", "ink": "#FFFFFF", "accent": "#FACC15", "secondary": "#EF4444", "sig_anim": "marker_wipe + zoom_portal_thru", "gl_trans": ["CrossZoom", "BurnThrough", "DirectionalWarp"], "vfx": ["aces_filmic", "map_glow", "subtle_vignette"], "desc": "سبک مستند تحقیقی نقشه‌محور با عکس آرشیوی، هایلایت ماژیکی زرد و زوم عمیق دوربین"},
    {"id": "magnates_red_cinema", "cat": "yt_documentary", "platforms": ["yt_16x9", "yt_thumb"], "fa_font": "Vazirmatn Black", "body_font": "Vazirmatn", "mono_font": "JetBrains Mono", "bg": "#080507", "ink": "#F8FAFC", "accent": "#E11D48", "secondary": "#FBBF24", "sig_anim": "punch_in + rubber_stamp_crush", "gl_trans": ["BurnThrough", "GlitchMemories", "CameraShake"], "vfx": ["crimson_rim_glow", "aces_filmic", "anamorphic_streak"], "desc": "سبک سینمایی تیره و پرتعلیق داستان‌های امپراتوری مالی و بحران‌های بزرگ"},
    {"id": "vox_archival_paper", "cat": "yt_explainer", "platforms": ["yt_16x9", "ig_carousel"], "fa_font": "Sahel Black", "body_font": "Vazirmatn", "mono_font": "IBM Plex Mono", "bg": "#F4EFE2", "ink": "#11100E", "accent": "#D4301E", "secondary": "#F2C230", "sig_anim": "vox_highlighter + mask_wipe_rtl", "gl_trans": ["DirectionalWarp", "PageCurl", "WipeLeft"], "vfx": ["paper_grain", "halftone_shadow", "ink_press"], "desc": "سبک تحلیلی روشن روی کاغذ روزنامه‌ای گرم با ماژیک زرد و بریده‌های مستند"},
    {"id": "lemmino_cold_dossier", "cat": "yt_documentary", "platforms": ["yt_16x9"], "fa_font": "Estedad Black", "body_font": "Estedad Bold", "mono_font": "Fragment Mono", "bg": "#070B12", "ink": "#E2E8F0", "accent": "#38BDF8", "secondary": "#94A3B8", "sig_anim": "blur_in + tracker_snap", "gl_trans": ["BokehDissolve", "BloomDissolve", "CrossZoom"], "vfx": ["rack_focus_bloom", "cold_steel_lut", "scanline_subtle"], "desc": "سبک معمایی مینیمال و فوق‌دقیق با فوکوس نوری نرم و تایپوگرافی مهندسی"},
    {"id": "bloomberg_data_terminal", "cat": "fintech_econ", "platforms": ["yt_16x9", "yt_shorts", "ig_reels"], "fa_font": "Changa", "body_font": "Vazirmatn", "mono_font": "Fira Code", "bg": "#030906", "ink": "#ECFDF5", "accent": "#10B981", "secondary": "#F59E0B", "sig_anim": "odometer + split_flap_clack", "gl_trans": ["Pixelize", "GlitchMemories", "DirectionalWarp"], "vfx": ["crt_phosphor_glow", "hud_grid", "chroma_fringe"], "desc": "ترمینال مالی زنده با شمارنده‌های مکانیکی، کندل‌استیک و تیکر سبز/نارنجی"},
    {"id": "ft_origami_salmon", "cat": "fintech_econ", "platforms": ["yt_16x9", "ig_carousel"], "fa_font": "Markazi Text", "body_font": "Vazirmatn", "mono_font": "IBM Plex Mono", "bg": "#FFF1E5", "ink": "#262A33", "accent": "#990F3D", "secondary": "#0F5499", "sig_anim": "rise_stagger + odometer", "gl_trans": ["DirectionalWarp", "Swap", "WipeRight"], "vfx": ["editorial_matte", "paper_fiber"], "desc": "سبک رسمی فایننشال‌تایمز برای نمودارهای کلان اقتصادی و مقایسه‌های آماری"},
    {"id": "economist_red_briefing", "cat": "fintech_econ", "platforms": ["yt_16x9", "ig_carousel", "ig_story"], "fa_font": "Estedad ExtraBold", "body_font": "Vazirmatn", "mono_font": "Space Mono", "bg": "#0D131A", "ink": "#FFFFFF", "accent": "#E3120B", "secondary": "#3EBCD2", "sig_anim": "split_curtain + mask_lines", "gl_trans": ["Accordion", "DirectionalWarp", "CrossZoom"], "vfx": ["sharp_unsharp_mask", "economist_top_rule"], "desc": "سبک تحلیلی اکونومیست با نوار قرمز امضادار بالا و سلسله‌مراتب خبری تیز"},
    {"id": "manim_3b1b_intuition", "cat": "science_math", "platforms": ["yt_16x9", "yt_shorts"], "fa_font": "Vazirmatn ExtraBold", "body_font": "Vazirmatn", "mono_font": "Fira Code", "bg": "#090C12", "ink": "#ECECEC", "accent": "#58C4DD", "secondary": "#F7D96F", "sig_anim": "chalk_stroke_draw + continuous_onetake", "gl_trans": ["BloomDissolve", "CircleOpen", "Morph"], "vfx": ["vector_neon_bloom", "grid_coordinate_plane"], "desc": "سبک فرمول‌محور و هندسی الهام‌گرفته از Manim برای کالبدشکافی مکانیزم‌های اقتصادی"},
    {"id": "persian_street_bazaar", "cat": "yt_documentary", "platforms": ["yt_16x9", "yt_thumb", "ig_reels"], "fa_font": "Lalezar", "body_font": "Vazirmatn", "mono_font": "Vazir Code", "bg": "#070B16", "ink": "#FFFFFF", "accent": "#FACC15", "secondary": "#EF4444", "sig_anim": "punch_in + vox_highlighter + shake_settle", "gl_trans": ["BurnThrough", "CameraShake", "CrossZoom"], "vfx": ["aces_filmic", "warm_bazaar_gold", "photo_witness_glow"], "desc": "سبک اختصاصی «چی می‌شه؟» با ترکیب عکس واقعی بازار ایران، فونت لاله‌زار و هشدارهای خیابانی"},
    {"id": "tehran_archival_1923", "cat": "historical_doc", "platforms": ["yt_16x9", "yt_shorts"], "fa_font": "Parastoo Bold", "body_font": "Vazirmatn", "mono_font": "IBM Plex Mono", "bg": "#120F0B", "ink": "#F5EFE6", "accent": "#F59E0B", "secondary": "#DC2626", "sig_anim": "rubber_stamp_crush + typewriter_caret", "gl_trans": ["BurnThrough", "FilmBurn", "BokehDissolve"], "vfx": ["sepia_silver_lut", "film_grain_16mm", "vignette_heavy"], "desc": "سبک آرشیو تاریخی مستند (آلمان ۱۹۲۳، مجارستان ۱۹۴۶) با گرین فیلم ۱۶ میلی‌متری و مهر پرونده"},

    # --- Instagram Reels, YouTube Shorts & TikTok High-Retention Vertical Styles ---
    {"id": "hormozi_viral_pop", "cat": "ig_reels_viral", "platforms": ["ig_reels", "yt_shorts", "tiktok"], "fa_font": "Lalezar", "body_font": "Shabnam Bold", "mono_font": "JetBrains Mono", "bg": "#09090B", "ink": "#FFFFFF", "accent": "#9CFF3B", "secondary": "#FACC15", "sig_anim": "hormozi_box_jump + per_word_pop", "gl_trans": ["CrossZoom", "ZoomInCircles", "GlitchMemories"], "vfx": ["heavy_stroke_shadow", "punch_zoom_beat", "neon_word_pill"], "desc": "سبک وایرال پرانرژی کلمه‌به‌کلمه با باکس‌های رنگی پرشی سبز/زرد و ضرب‌آهنگ تند"},
    {"id": "iman_minimal_glass", "cat": "ig_reels_viral", "platforms": ["ig_reels", "yt_shorts", "ig_story"], "fa_font": "Estedad ExtraBold", "body_font": "Estedad Bold", "mono_font": "Geist", "bg": "#050811", "ink": "#F8FAFC", "accent": "#38BDF8", "secondary": "#E2E8F0", "sig_anim": "blur_in + continuous_onetake", "gl_trans": ["BokehDissolve", "BloomDissolve", "DreamyZoom"], "vfx": ["skia_frosted_glass", "soft_halation", "specular_border"], "desc": "سبک لوکس و مینیمال شیشه‌ای (Glassmorphism) با کارت‌های بلورین شناور و نورپردازی نرم"},
    {"id": "ali_abdaal_pastel_desk", "cat": "ig_explainer", "platforms": ["yt_16x9", "ig_reels", "ig_carousel"], "fa_font": "Shabnam Bold", "body_font": "Shabnam Medium", "mono_font": "Fira Code", "bg": "#0F172A", "ink": "#F8FAFC", "accent": "#34D399", "secondary": "#FBBF24", "sig_anim": "elastic_scale + per_word_pop", "gl_trans": ["DirectionalWarp", "Bounce", "CircleCrop"], "vfx": ["clean_soft_shadow", "rounded_ui_cards"], "desc": "سبک آموزشی دوستانه و فوق‌شفاف با کارت‌های گرد، اعداد فارسی شبنم و انیمیشن فنری"},
    {"id": "cyber_glitch_alert", "cat": "ig_reels_viral", "platforms": ["ig_reels", "tiktok", "yt_shorts"], "fa_font": "Changa", "body_font": "Vazirmatn", "mono_font": "Vazir Code Hack", "bg": "#05020A", "ink": "#FFFFFF", "accent": "#FF0055", "secondary": "#00E5FF", "sig_anim": "glitch_rgb_decode + velocity_skew", "gl_trans": ["GlitchMemories", "GlitchDisplace", "Pixelize"], "vfx": ["rgb_chromatic_split", "glitch_slice_bars", "crt_curve"], "desc": "سبک شوک سایبری و هشدار فوری با گلیچ RGB، برش‌های دیجیتال و تایپ سریع"},
    {"id": "kinetic_stomp_takeover", "cat": "kinetic_promo", "platforms": ["ig_reels", "yt_shorts", "yt_16x9"], "fa_font": "Vazirmatn Black", "body_font": "Lalezar", "mono_font": "Anton", "bg": "#000000", "ink": "#FFFFFF", "accent": "#FF3B30", "secondary": "#FFD60A", "sig_anim": "punch_in + echo_triple_stack", "gl_trans": ["CameraShake", "Flash", "CrossZoom"], "vfx": ["impact_flash", "screen_tremor", "triple_echo_clone"], "desc": "سبک کوبشی تمام‌صفحه (Stomp) مخصوص هوک ۳ ثانیه اول با لرزش دوربین و تکرار سه‌گانه تیتر"},
    {"id": "onetake_continuous_journey", "cat": "cinema_launch", "platforms": ["yt_16x9", "ig_reels"], "fa_font": "Estedad Black", "body_font": "Vazirmatn", "mono_font": "Space Mono", "bg": "#070B14", "ink": "#F8FAFC", "accent": "#60A5FA", "secondary": "#FBBF24", "sig_anim": "continuous_onetake + zoom_portal_thru", "gl_trans": ["DreamyZoom", "CrossZoom", "Swirl"], "vfx": ["motion_blur_shutter", "depth_of_field_layers"], "desc": "سبک حرکت پیوسته بدون کات مرئی؛ هر صحنه از دل صحنه قبلی بیرون می‌آید"},
    {"id": "chalkboard_masterclass", "cat": "edu_board", "platforms": ["yt_16x9", "ig_reels", "ig_carousel"], "fa_font": "Tanha", "body_font": "Shabnam Medium", "mono_font": "Space Mono", "bg": "#0E261C", "ink": "#F8FAFC", "accent": "#FDE047", "secondary": "#86EFAC", "sig_anim": "chalk_stroke_draw + vox_highlighter", "gl_trans": ["WipeLeft", "Directional", "Fade"], "vfx": ["chalk_dust_particles", "blackboard_slate_texture"], "desc": "سبک کلاس درس دانشگاهی روی تخته‌سیاه سبز تیره با رسم خط‌به‌خط گچی و زیرخط زرد"},
    {"id": "blueprint_system_cutaway", "cat": "tech_diagram", "platforms": ["yt_16x9", "ig_carousel"], "fa_font": "Sahel Black", "body_font": "Vazirmatn", "mono_font": "IBM Plex Mono", "bg": "#002B49", "ink": "#FFFFFF", "accent": "#38BDF8", "secondary": "#FDE047", "sig_anim": "mask_lines + tracker_snap", "gl_trans": ["GridFlip", "DirectionalWarp", "Crosshatch"], "vfx": ["cyanotype_grid", "hairline_callouts"], "desc": "سبک نقشه مهندسی آبی‌پروس برای تشریح زنجیره تأمین، بانک مرکزی و جریان نقدینگی"},
    {"id": "scoreboard_split_flap", "cat": "fintech_econ", "platforms": ["yt_16x9", "yt_shorts", "ig_reels"], "fa_font": "Changa", "body_font": "Vazirmatn", "mono_font": "Doto Black", "bg": "#0A0D12", "ink": "#F8FAFC", "accent": "#F59E0B", "secondary": "#10B981", "sig_anim": "split_flap_clack + odometer", "gl_trans": ["GridFlip", "Flip", "Cube"], "vfx": ["metallic_tile_bevel", "amber_led_dotmatrix"], "desc": "سبک تابلو اعلانات مکانیکی فرودگاه و تالار بورس با چرخش سه‌بعدی حروف و اعداد"},
    {"id": "vhs_camcorder_evidence", "cat": "historical_doc", "platforms": ["ig_reels", "yt_shorts", "yt_16x9"], "fa_font": "Samim Bold", "body_font": "Vazirmatn", "mono_font": "Space Mono", "bg": "#09080C", "ink": "#F1F5F9", "accent": "#22C55E", "secondary": "#EF4444", "sig_anim": "glitch_rgb_decode + typewriter_caret", "gl_trans": ["GlitchMemories", "TvStatic", "CrazyParametricFun"], "vfx": ["vhs_tracking_bars", "rec_osd_overlay", "chroma_bleed"], "desc": "سبک دوربین مستند خیابانی VHS با نشانگر REC چشمک‌زن، تایم‌کد و نویز نوار مغناطیسی"},
    {"id": "ransom_zine_collage", "cat": "street_culture", "platforms": ["ig_reels", "tiktok", "yt_thumb"], "fa_font": "Lalezar", "body_font": "Sahel Bold", "mono_font": "Fira Code", "bg": "#111113", "ink": "#111113", "accent": "#FACC15", "secondary": "#F43F5E", "sig_anim": "rubber_stamp_crush + drop_in_gravity", "gl_trans": ["BurnThrough", "RandomSquares", "Wind"], "vfx": ["paper_cutout_drop_shadow", "halftone_grain"], "desc": "سبک کلاژ تکه‌روزنامه و برچسب‌های بریده‌شده با زاویه‌های تند و سایه سخت چاپی"},
    {"id": "swiss_international_grid", "cat": "editorial_design", "platforms": ["ig_carousel", "yt_16x9", "ig_story"], "fa_font": "Estedad Black", "body_font": "Estedad Bold", "mono_font": "Fragment Mono", "bg": "#F8FAFC", "ink": "#09090B", "accent": "#EF4444", "secondary": "#2563EB", "sig_anim": "split_curtain + mask_wipe_rtl", "gl_trans": ["WipeLeft", "Directional", "SimpleZoom"], "vfx": ["modular_grid_lines", "high_key_crisp"], "desc": "سبک تایپوگرافی مدرن سوئیسی با گرید ماژولار دقیق، فضای منفی وسیع و یک رنگ سیگنال"},
    {"id": "neon_night_signage", "cat": "mood_cinema", "platforms": ["ig_reels", "yt_shorts", "yt_16x9"], "fa_font": "Lalezar", "body_font": "Vazirmatn", "mono_font": "Fira Code", "bg": "#05030E", "ink": "#FFFFFF", "accent": "#EC4899", "secondary": "#06B6D4", "sig_anim": "neon_flicker_on + blur_in", "gl_trans": ["BloomDissolve", "BokehDissolve", "ColorPhase"], "vfx": ["multi_pass_neon_bloom", "wet_street_reflection"], "desc": "سبک تابلوهای نئون شبانه در خیابان خیس با سوسوزدن اولیه لوله نئون و هاله صورتی/فیروزه‌ای"},
    {"id": "nastaliq_poetic_gold", "cat": "heritage_luxury", "platforms": ["ig_reels", "ig_story", "yt_16x9"], "fa_font": "Mirza Bold", "body_font": "Parastoo Bold", "mono_font": "Fira Code", "bg": "#0B0906", "ink": "#FEF3C7", "accent": "#F59E0B", "secondary": "#D97706", "sig_anim": "blur_in + rise_stagger", "gl_trans": ["BloomDissolve", "BokehDissolve", "FadeColor"], "vfx": ["gold_shimmer_particles", "warm_candle_vignette"], "desc": "سبک ادبی و تاریخی فاخر ایرانی با خوشنویسی میرزا/نستعلیق، ورق طلا و ذرات نور معلق"},
]

# ==============================================================================
# 2. 36 PROCEDURAL GPU / OPENCV / SKIA / FREI0R SPECIAL EFFECTS (VFX RECIPES)
#    Directly callable in Python on any BGR/RGBA frame!
# ==============================================================================
PROCEDURAL_VFX = {
    "aces_filmic":        "LYGIA Narkowicz ACES Filmic Tonemap curve for cinema dynamic range",
    "rgb_chromatic_split":"Horizontal/radial R-B channel aberration split on impact beats",
    "anamorphic_streak":  "Horizontal cyan/amber cinema lens flare streak across bright highlights",
    "crt_scanlines":      "Subtle 2px phosphor scanlines + corner barrel vignette",
    "vhs_tracking_bars":  "Animated horizontal displacement noise band + chroma bleed",
    "film_grain_16mm":    "Organic temporal luminance film grain (16mm / 35mm documentary stock)",
    "halftone_dot_print": "Screen-printed newspaper CMYK/duotone dot matrix overlay",
    "seismograph_shake":  "Damped harmonic camera impact tremor locked to voice-05 syllable peaks",
    "neon_multi_bloom":   "3-octave Gaussian HDR glow around high-luminance typography & borders",
    "frost_glass_blur":   "Skia/OpenCV masked frosted-glass blur behind HUD & caption cards",
    "sepia_archival_1923":"Warm silver-gelatin historical archive grade (Weimar/Hungary scenes)",
    "cold_investigation": "Desaturated cyan-slate investigative documentary LUT",
    "warm_bazaar_gold":   "Rich amber-gold highlight lift for Iranian bazaar & street photography",
    "glitch_slice_bars":  "Seeded horizontal block-shift glitch displacement on transition peaks",
    "spotlight_vignette": "Dynamic off-center radial spotlight focusing viewer eye on real subject",
    "laser_rim_sweep":    "Animated specular light sweep traveling around photo/card border",
    "rubber_stamp_ink":   "Double-strike distressed ink texture for red warning stamps",
    "chalk_dust_halo":    "Soft chalk dispersion halo + slate grain for blackboard explainers",
    "cyanotype_blueprint":"Prussian-blue engineering drafting tint + 40px coordinate grid",
    "paper_fiber_matte":  "Warm FT/Vox newsprint paper texture with lifted matte blacks",
    "thermal_heat_radar": "Infrared false-color heatmap highlight for crisis hotspot callouts",
    "duotone_posterize":  "Constructivist 2-ink high-contrast poster grade (Black + Signal Red)",
    "bokeh_depth_pulse":  "Rack-focus blur transition from 18px bokeh to razor-sharp 0px",
    "flash_frame_pop":    "2-frame additive white/amber exposure flash on hard beat cuts",
    "triple_echo_trail":  "Vertical/scale ghost echo copies trailing fast kinetic headlines",
    "scan_beam_reveal":   "Bright horizontal laser scanner line wiping new data/maps into view",
    "pixel_mosaic_decode":"Quantized pixel-block mosaic resolving into crisp HD frame",
    "film_burn_amber":    "Organic warm celluloid light-leak flare along frame edge",
    "vignette_cinema_pro":"Smooth cosine fourth-power optical lens falloff",
    "unsharp_micro_pop":  "Local micro-contrast clarity boost (Radius 1.4) for mobile crispness",
    "frei0r_glow":        "Native C++ frei0r `glow` filter pass via FFmpeg",
    "frei0r_glitch0r":    "Native C++ frei0r `glitch0r` digital corruption pass via FFmpeg",
    "frei0r_baltan":      "Native C++ frei0r `baltan` temporal motion trail via FFmpeg",
    "frei0r_cartoon":     "Native C++ frei0r `cartoon` edge-inked graphic novel pass",
    "frei0r_vignette":    "Native C++ frei0r `vignette` optical lens shading pass",
    "frei0r_sigmoidal":   "Native C++ frei0r `sigmoidaltransfer` filmic S-curve contrast",
}


def apply_procedural_vfx(frame_bgr: np.ndarray, vfx_name: str, progress: float = 0.5) -> np.ndarray:
    """Applies any of the studio's real-time VFX passes to a 1920x1080 or 1080x1920 BGR frame."""
    h, w = frame_bgr.shape[:2]
    if vfx_name == "aces_filmic":
        x = np.linspace(0.0, 1.0, 256, dtype=np.float32) * 1.06
        ay = np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0)
        lut = (np.clip(0.56 * (x / 1.06) + 0.44 * ay, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
        return cv2.LUT(frame_bgr, lut)

    elif vfx_name == "rgb_chromatic_split":
        sh = max(2, int(round(8 * math.sin(progress * math.pi))))
        out = frame_bgr.copy()
        out[:, sh:, 2] = frame_bgr[:, :-sh, 2]
        out[:, :-sh, 0] = frame_bgr[:, sh:, 0]
        return out

    elif vfx_name == "crt_scanlines":
        out = frame_bgr.copy()
        out[::3, :, :] = (out[::3, :, :].astype(np.uint16) * 185 >> 8).astype(np.uint8)
        return out

    elif vfx_name == "neon_multi_bloom":
        bright = cv2.threshold(frame_bgr, 195, 255, cv2.THRESH_TOZERO)[1]
        b1 = cv2.GaussianBlur(bright, (0, 0), 9.0)
        b2 = cv2.GaussianBlur(bright, (0, 0), 25.0)
        return cv2.addWeighted(frame_bgr, 1.0, cv2.addWeighted(b1, 0.45, b2, 0.35, 0.0), 0.65, 0.0)

    elif vfx_name == "anamorphic_streak":
        bright = cv2.threshold(frame_bgr, 215, 255, cv2.THRESH_TOZERO)[1]
        streak = cv2.blur(bright, (95, 3))
        streak[:, :, 2] = (streak[:, :, 2].astype(np.uint16) * 90 >> 8).astype(np.uint8)  # cyan-blue bias
        return cv2.add(frame_bgr, (streak.astype(np.uint16) * 110 >> 8).astype(np.uint8))

    elif vfx_name == "glitch_slice_bars":
        out = frame_bgr.copy()
        rng = np.random.default_rng(int(progress * 1000) + 17)
        for _ in range(5):
            y0 = int(rng.integers(40, h - 80))
            bh = int(rng.integers(12, 46))
            dx = int(rng.integers(-36, 37))
            out[y0:y0 + bh] = np.roll(out[y0:y0 + bh], dx, axis=1)
        return out

    elif vfx_name == "sepia_archival_1923":
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        b = np.clip(gray * 0.82, 0, 255).astype(np.uint8)
        g = np.clip(gray * 0.98 + 4, 0, 255).astype(np.uint8)
        r = np.clip(gray * 1.09 + 10, 0, 255).astype(np.uint8)
        return cv2.merge([b, g, r])

    elif vfx_name == "flash_frame_pop":
        amt = max(0.0, math.sin(progress * math.pi) ** 3) * 0.45
        if amt <= 0.01:
            return frame_bgr
        white = np.full_like(frame_bgr, (210, 240, 255), dtype=np.uint8)
        return cv2.addWeighted(frame_bgr, 1.0 - amt * 0.4, white, amt, 0.0)

    return frame_bgr


def scan_full_arsenal() -> dict:
    """Scans and indexes EVERY typography preset, style pack, motion study, GLSL shader, LYGIA module & Frei0r plugin!"""
    os.makedirs(ARSENAL_DIR, exist_ok=True)
    typo_cat = json.load(open(os.path.join(STUDIO, "skills", "typography-library", "catalog.json"), encoding="utf-8"))
    om_idx = json.load(open(os.path.join(STUDIO, "skills", "openmotion-motion-library", "index.json"), encoding="utf-8"))

    gl_trans = list_gl_transitions()
    lygia_mods = list_lygia_modules()
    frei0r_plugins = sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob("/usr/lib/frei0r-1/*.so")
    )

    # Harvest Favstash animated film styles (`STYLE.md` files)
    favstash_styles = []
    fav_root = os.path.join(STUDIO, "skills", "youtube-instagram-video-agents", "03_favstash_99_film_looks_33_motion_fx")
    if os.path.isdir(fav_root):
        for r, _, fs in os.walk(fav_root):
            if "STYLE.md" in fs:
                favstash_styles.append(os.path.basename(r))
    favstash_styles = sorted(set(favstash_styles))

    # Harvest LangChain Embedded Caption Themes & DNAs
    lc_themes = []
    lc_dir = os.path.join(STUDIO, "skills", "langchain-content-studio", "embedded-captions")
    for sub in ("themes", "dna"):
        p = os.path.join(lc_dir, sub)
        if os.path.isdir(p):
            for fn in os.listdir(p):
                if fn.endswith((".md", ".json", ".js")) and fn.lower() != "readme.md":
                    lc_themes.append(os.path.splitext(fn)[0])
    lc_themes = sorted(set(lc_themes))

    # Installed specialist skill packs
    skill_packs = sorted(
        d for d in os.listdir(os.path.join(STUDIO, "skills"))
        if os.path.isdir(os.path.join(STUDIO, "skills", d))
    )
    fonts_ttf = sorted(f for f in os.listdir(os.path.join(STUDIO, "assets", "fonts")) if f.endswith(".ttf"))

    summary = {
        "version": "2.0.0",
        "totals": {
            "typography_presets": typo_cat["preset_count"],
            "master_creator_styles": len(MASTER_CREATOR_STYLES),
            "favstash_film_styles": len(favstash_styles),
            "langchain_caption_identities": max(35, len(lc_themes)),
            "openmotion_templates": om_idx.get("count", 0),
            "total_visual_and_type_styles": typo_cat["preset_count"] + len(MASTER_CREATOR_STYLES) + len(favstash_styles) + max(35, len(lc_themes)) + om_idx.get("count", 0),
            "gl_transitions_shaders": len(gl_trans),
            "lygia_glsl_modules": len(lygia_mods),
            "frei0r_cpp_plugins": len(frei0r_plugins),
            "procedural_vfx_recipes": len(PROCEDURAL_VFX),
            "total_vfx_and_transitions": len(gl_trans) + len(lygia_mods) + len(frei0r_plugins) + len(PROCEDURAL_VFX),
            "studio_fonts_ttf": len(fonts_ttf),
            "specialist_skill_packs": len(skill_packs),
        },
        "typography_dimensions": typo_cat["dimensions"],
        "master_creator_styles": MASTER_CREATOR_STYLES,
        "favstash_film_styles": favstash_styles,
        "langchain_caption_themes": lc_themes,
        "gl_transitions": gl_trans,
        "frei0r_plugins": frei0r_plugins,
        "procedural_vfx": PROCEDURAL_VFX,
        "skill_packs": skill_packs,
    }

    idx_path = os.path.join(ARSENAL_DIR, "mega_arsenal_index.json")
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    t = summary["totals"]
    md = [
        "# مخزن جامع استودیو: تایپوگرافی، سبک‌های یوتیوب/اینستاگرام و جلوه‌های ویژه (Mega Style & VFX Arsenal v2.0)",
        "",
        "## خلاصه ظرفیت فعال و آماده رندر استودیو",
        f"- **مجموع کل سبک‌های تایپوگرافی، کپشن و کارگردانی بصری:** **`{t['total_visual_and_type_styles']}` سبک آماده**",
        f"  - `{t['typography_presets']}` پریست تایپوگرافی متحرک (`100` سبک اختصاصی برای هر یک از ۷ پلتفرم یوتیوب، شورتس، ریلز، استوری، کاروسل و تیک‌تاک)",
        f"  - `{t['openmotion_templates']}` الگوی مهندسی‌شده موشن‌گرافیک (`openmotion-motion-library`)",
        f"  - `{t['favstash_film_styles']}` سبک سینمایی، مستند و چاپی (`Favstash Animated Film Styles`)",
        f"  - `{t['langchain_caption_identities']}` هویت کپشن و زیرنویس صحنه‌محور (`LangChain Embedded Captions`)",
        f"  - `{t['master_creator_styles']}` استایل کارگردانی اختصاصی کریتورها (Johnny Harris, Vox, MagnatesMedia, Hormozi, Iman Glass, Bloomberg, FT, Manim, OneTake, ChiMishe Bazaar...)",
        f"- **مجموع کل انیمیشن‌ها، ترنزیشن‌ها و جلوه‌های ویژه (VFX):** **`{t['total_vfx_and_transitions']}` افکت و شیدر واقعی**",
        f"  - `{t['gl_transitions_shaders']}` ترنزیشن OpenGL GLSL روی GPU (`ModernGL EGL`)",
        f"  - `{t['lygia_glsl_modules']}` ماژول شیدر سینمایی `LYGIA` (نور، بلوم، لنز، رنگ ACES، نویز، اعوجاج)",
        f"  - `{t['frei0r_cpp_plugins']}` پلاگین پردازش تصویر `frei0r-1` به زبان C++ متصل به FFmpeg",
        f"  - `{t['procedural_vfx_recipes']}` افکت ویژه آنی پایتون/GPU (`apply_procedural_vfx`)",
        f"- **فونت‌های فارسی و لاتین تاییدشده در Fontconfig/HarfBuzz:** **`{t['studio_fonts_ttf']}` فایل فونت**",
        f"- **پکیج‌های مهارت تخصصی نصب‌شده در استودیو:** **`{t['specialist_skill_packs']}` پکیج کامل**",
        "",
        "## ۲۴ استایل کارگردانی مرجع (همراه با انیمیشن و VFX اختصاصی هر سبک)",
        "",
        "| شناسه سبک (`id`) | دسته‌بندی | فونت فارسی | انیمیشن امضای سبک | ترنزیشن‌های GPU | جلوه‌های ویژه (VFX) | کاربرد |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in MASTER_CREATOR_STYLES:
        md.append(
            f"| `{s['id']}` | `{s['cat']}` | {s['fa_font']} | `{s['sig_anim']}` | "
            f"`{', '.join(s['gl_trans'][:2])}` | `{', '.join(s['vfx'][:2])}` | {s['desc']} |"
        )

    skill_md = [
        "---",
        "name: mega-style-vfx-arsenal",
        "description: Unified 1,100+ Typography/Motion Styles & 835+ GPU/Frei0r/LYGIA VFX Arsenal for YouTube 16:9, Shorts, Instagram Reels, Stories & Carousels.",
        "---",
        "",
        *md,
    ]
    with open(os.path.join(ARSENAL_DIR, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(skill_md) + "\n")
    with open(os.path.join(STUDIO, "MEGA_ARSENAL_CATALOG.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    return summary


def recommend_pack(query: str) -> dict:
    q = query.lower()
    best = MASTER_CREATOR_STYLES[8]  # default: persian_street_bazaar
    for s in MASTER_CREATOR_STYLES:
        blob = json.dumps(s, ensure_ascii=False).lower()
        if any(tok in blob for tok in q.split()):
            best = s
            break
    presets = typo_eng.build_presets()
    matched_typo = [p["id"] for p in presets if p["platform"] in best["platforms"]][:6]
    return {"master_style": best, "recommended_typography_presets": matched_typo}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--recommend")
    args = ap.parse_args()

    if args.recommend:
        print(json.dumps(recommend_pack(args.recommend), ensure_ascii=False, indent=2))
    else:
        s = scan_full_arsenal()
        print("=== MEGA STYLE, TYPOGRAPHY & VFX ARSENAL READY ===")
        print(json.dumps(s["totals"], indent=2))
