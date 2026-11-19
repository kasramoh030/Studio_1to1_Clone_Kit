#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arsenal_pools.py — Live Workspace Asset Pool Builder & Real Audio/Visual Materializers
======================================================================================
Aggregates EVERY real tool, repository, shader, font, preset, C++ plugin, SoundFont,
and visual/chart/photo generator inside `/home/user/animation-studio` into 12 unified,
searchable, mood-tagged pools (each 100 to 700 items strong), plus real 48kHz WAV
music/SFX synthesizers and HarfBuzz+GPU moodboard specimen rendering.

STRICT STANDING RULES ENFORCED:
  - Narrator voice is ALWAYS locked to Arena `voice-05` (`generate_speech(voice_id="voice-05")`).
  - Zero local TTS engines are ever referenced or invoked.
  - Persian glyphs ALWAYS use verified Persian TTFs (`Lalezar`, `Vazirmatn`, `Sahel`, `Estedad`,
    `Shabnam`, `Changa`, `Samim`, `Parastoo`, `Markazi Text`, `Mirza`, `Tanha`, `Vazir Code`).
"""

import os
import re
import sys
import json
import glob
import math
import hashlib
import subprocess
from pathlib import Path
import numpy as np

STUDIO = "/home/user/animation-studio"
PYLIBS = os.path.join(STUDIO, "runtime", "pylibs")
for _p in (PYLIBS, STUDIO, os.path.join(STUDIO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from vfx_studio import list_gl_transitions, list_lygia_modules
import style_vfx_arsenal as sva
import typography_engine as typo_eng

SOUNDFONT_GM = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SR = 48000

# ==============================================================================
# 12 SEMANTIC MOOD AXES (Used across scenario analysis & all 12 asset pools)
# ==============================================================================
MOOD_AXES = [
    "crisis_economy",      # تورم، بودجه، حقوق، گرانی، بازار، بانک، دلار، ریال، معیشت
    "investigative_noir",  # پشت‌پرده، پرونده، راز، افشاگری، سند، مافیا، تاریک، هشدار
    "geopolitics_map",     # نقشه، کشور، مرز، تحریم، نفت، صادرات، استان، جهان، انرژی
    "historical_archive",  # تاریخ، سال ۱۹۲۳، مجارستان، قدیم، آرشیو، قرن، دهه، مستند تاریخی
    "fintech_data",        # آمار، درصد، نمودار، کندل، بورس، نقدینگی، ترازنامه، شاخص
    "science_system",      # مکانیزم، سیستم، فرمول، مهندسی، کالبدشکافی، زنجیره، چطور کار می‌کند
    "street_human",        # خیابان، مردم، مغازه، سفره، زندگی روزمره، اجاره، سوپرمارکت
    "viral_shock",         # شوک، فوری، باورکردنی نیست، ۳ ثانیه، انفجار، رکورد، عجیب
    "tech_cyber",          # هوش مصنوعی، سایبری، دیجیتال، کد، الگوریتم، آینده، تکنولوژی
    "educational_board",   # آموزش، درس، گام‌به‌گام، چک‌لیست، کلاس، راهنما، ساده
    "editorial_press",     # روزنامه، گزارش، تحلیل رسمی، اکونومیست، فایننشال، مقاله
    "poetic_heritage",     # فرهنگ، ادبیات، روایت انسانی، ایران، فلسفه، هنر، میراث
]

# Platform-first routing specifications
PLATFORM_SPECS = {
    "yt_16x9": {
        "id": "yt_16x9",
        "thumb_platform": "yt_thumb",
        "label_fa": "ویدیوی افقی یوتیوب (16:9 Long-Form / Mid-Form)",
        "resolution": [1920, 1080],
        "aspect": "16:9",
        "fps": 30,
        "safe_zone_px": {"top": 90, "right": 96, "bottom": 110, "left": 140},
        "thumb_timestamp_clear_px": {"w": 336, "h": 189, "corner": "bottom-right"},
        "cut_cadence_sec": [3.8, 6.8],
        "hook_window_sec": 5.0,
        "target_lufs": -14.0,
        "primary_skills": [
            "youtube-video-skills", "explainer-video-skills", "onetake-continuous-camera",
            "explainroo-canvas-engine", "data-animation-skills", "map-animation-skills",
            "b-roll-skills", "lower-thirds-skills", "openmotion-director-suite",
            "video-editing-kit", "mega-style-vfx-arsenal",
        ],
    },
    "yt_shorts": {
        "id": "yt_shorts",
        "thumb_platform": "yt_shorts",
        "label_fa": "یوتیوب شورتس عمودی (9:16 YouTube Shorts)",
        "resolution": [1080, 1920],
        "aspect": "9:16",
        "fps": 30,
        "safe_zone_px": {"top": 140, "right": 88, "bottom": 340, "left": 88},
        "cut_cadence_sec": [1.8, 3.4],
        "hook_window_sec": 2.2,
        "target_lufs": -14.0,
        "primary_skills": [
            "tiktok-video-skills", "reelforge", "kinetic-typography-rtl",
            "youtube-instagram-video-agents", "langchain-content-studio",
            "ad-video-skills", "open-edit-suite", "mega-style-vfx-arsenal",
        ],
    },
    "ig_reels": {
        "id": "ig_reels",
        "thumb_platform": "ig_reels",
        "label_fa": "ریلز اینستاگرام عمودی (9:16 Instagram Reels)",
        "resolution": [1080, 1920],
        "aspect": "9:16",
        "fps": 30,
        "safe_zone_px": {"top": 150, "right": 92, "bottom": 360, "left": 92},
        "cut_cadence_sec": [1.6, 3.2],
        "hook_window_sec": 2.0,
        "target_lufs": -14.0,
        "primary_skills": [
            "reelforge", "tiktok-video-skills", "youtube-instagram-video-agents",
            "kinetic-typography-rtl", "langchain-content-studio", "text-message-video-skills",
            "ad-video-skills", "mega-style-vfx-arsenal",
        ],
    },
    "ig_story": {
        "id": "ig_story",
        "thumb_platform": "ig_story",
        "label_fa": "استوری تعاملی اینستاگرام (9:16 Instagram Story)",
        "resolution": [1080, 1920],
        "aspect": "9:16",
        "fps": 30,
        "safe_zone_px": {"top": 160, "right": 96, "bottom": 300, "left": 96},
        "cut_cadence_sec": [2.0, 4.0],
        "hook_window_sec": 2.0,
        "target_lufs": -14.0,
        "primary_skills": [
            "reelforge", "kinetic-type-skills", "youtube-instagram-video-agents",
            "text-message-video-skills", "mega-style-vfx-arsenal",
        ],
    },
    "ig_carousel": {
        "id": "ig_carousel",
        "thumb_platform": "ig_carousel",
        "label_fa": "پست اسلایدی / ویدیویی اینستاگرام (4:5 Carousel)",
        "resolution": [1080, 1350],
        "aspect": "4:5",
        "fps": 30,
        "safe_zone_px": {"top": 84, "right": 84, "bottom": 130, "left": 84},
        "cut_cadence_sec": [2.5, 4.5],
        "hook_window_sec": 2.5,
        "target_lufs": -14.0,
        "primary_skills": [
            "data-animation-skills", "explainer-video-skills", "typography-library",
            "generative-illustration-skills", "mega-style-vfx-arsenal",
        ],
    },
    "tiktok": {
        "id": "tiktok",
        "thumb_platform": "tiktok",
        "label_fa": "ویدیوی وایرال تیک‌تاک (9:16 TikTok)",
        "resolution": [1080, 1920],
        "aspect": "9:16",
        "fps": 30,
        "safe_zone_px": {"top": 150, "right": 96, "bottom": 380, "left": 96},
        "cut_cadence_sec": [1.5, 2.8],
        "hook_window_sec": 1.8,
        "target_lufs": -14.0,
        "primary_skills": [
            "tiktok-video-skills", "reelforge", "kinetic-typography-rtl",
            "langchain-content-studio", "mega-style-vfx-arsenal",
        ],
    },
}


def _det_hash(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:12], 16)


def _infer_moods_from_tokens(text: str) -> list[str]:
    """Maps style/shader/preset names & descriptions onto our 12 semantic mood axes."""
    t = text.lower()
    moods = []
    rules = [
        ("crisis_economy", ["crimson", "red", "alert", "burn", "crisis", "econom", "inflation", "bazaar", "heat", "stamp", "shock", "shake", "warning", "budget", "gold_black", "orange"]),
        ("investigative_noir", ["noir", "dossier", "lemmino", "magnates", "cold", "dark", "shadow", "archive", "evidence", "mystery", "vignette", "spotlight", "briefing", "redact"]),
        ("geopolitics_map", ["geo", "harris", "map", "ultramarine", "radar", "world", "globe", "transit", "arc", "border", "directional", "zoom_portal", "satellite"]),
        ("historical_archive", ["1923", "archival", "newsreel", "sepia", "vintage", "film", "16mm", "paper", "typewriter", "parastoo", "halftone", "sand_ink", "projector", "vhs"]),
        ("fintech_data", ["bloomberg", "terminal", "fintech", "data", "odometer", "scoreboard", "flap", "candlestick", "chart", "mint", "cyan", "hud", "telemetry", "ft_", "number"]),
        ("science_system", ["manim", "3b1b", "blueprint", "iso", "diagram", "system", "cutaway", "math", "vector", "grid", "assembly", "plotter", "onetake"]),
        ("street_human", ["street", "bazaar", "witness", "photo", "camcorder", "sticker", "ransom", "tape", "crowd", "chat", "bubble", "real", "human"]),
        ("viral_shock", ["hormozi", "viral", "stomp", "punch", "pop", "slam", "flash", "lime", "acid", "rose_shock", "glitch", "whip", "karaoke", "takeover"]),
        ("tech_cyber", ["cyber", "glitch", "neon", "ascii", "crt", "pixel", "hologram", "laser", "violet", "matrix", "code", "webgl", "prism", "digital"]),
        ("educational_board", ["chalk", "lecture", "abdaal", "pastel", "checklist", "list", "notebook", "explain", "board", "sketch", "clean", "step"]),
        ("editorial_press", ["vox", "economist", "ft_", "swiss", "newspaper", "editorial", "magazine", "salmon", "bone", "risograph", "bauhaus", "quote"]),
        ("poetic_heritage", ["nastaliq", "mirza", "poetic", "heritage", "gold", "inkwater", "brush", "calligraph", "bokeh", "dreamy", "aurora", "candle"]),
    ]
    for axis, kws in rules:
        if any(k in t for k in kws):
            moods.append(axis)
    if not moods:
        idx = _det_hash(t) % len(MOOD_AXES)
        moods = [MOOD_AXES[idx], MOOD_AXES[(idx + 4) % len(MOOD_AXES)]]
    return moods


# ==============================================================================
# POOL 1: VISUAL & CREATOR STYLE DIRECTIONS (153 Real Styles)
# ==============================================================================
def build_visual_styles_pool() -> list[dict]:
    mega_path = os.path.join(STUDIO, "skills", "mega-style-vfx-arsenal", "mega_arsenal_index.json")
    mega = json.load(open(mega_path, encoding="utf-8"))
    pool = []

    # 1A. 24 Master Creator Styles
    for s in mega.get("master_creator_styles", []):
        tone = "light" if s["bg"].upper() in ("#F4EFE2", "#FFF1E5", "#F8FAFC") else "dark"
        pool.append({
            "id": f"master::{s['id']}",
            "raw_id": s["id"],
            "source": "master_creator_styles",
            "title": s["id"].replace("_", " ").title(),
            "desc_fa": s["desc"],
            "platforms": s["platforms"],
            "tone": tone,
            "palette": {"bg": s["bg"], "ink": s["ink"], "accent": s["accent"], "secondary": s["secondary"]},
            "fa_font": s["fa_font"],
            "sig_anim": s["sig_anim"],
            "paired_gl": s["gl_trans"],
            "paired_vfx": s["vfx"],
            "moods": _infer_moods_from_tokens(f"{s['id']} {s['cat']} {s['sig_anim']} {s['desc']}"),
            "tier_bonus": 14.0,
        })

    # 1B. 99 Favstash Film & Documentary Styles
    fav_palettes = [
        ("#070B14", "#F8FAFC", "#FACC15", "#EF4444", "dark"),
        ("#09060A", "#FFF7F5", "#E11D48", "#38BDF8", "dark"),
        ("#F4EFE2", "#11100E", "#D4301E", "#2563EB", "light"),
        ("#04110D", "#ECFDF5", "#10B981", "#F59E0B", "dark"),
        ("#00233D", "#F8FAFC", "#38BDF8", "#FDE047", "dark"),
        ("#120E0A", "#F5EFE6", "#F59E0B", "#DC2626", "dark"),
    ]
    fa_choices = ["Lalezar", "Vazirmatn Black", "Estedad Black", "Sahel Black", "Changa", "Markazi Text", "Shabnam Bold"]
    for i, fid in enumerate(mega.get("favstash_film_styles", [])):
        bg, ink, acc, sec, tone = fav_palettes[i % len(fav_palettes)]
        if any(k in fid for k in ("paper", "newspaper", "risograph", "notebook", "swiss", "bauhaus", "editorial")):
            bg, ink, acc, sec, tone = ("#F4EFE2", "#11100E", "#D4301E", "#0F5499", "light")
        plats = ["yt_16x9", "yt_shorts", "ig_reels", "ig_carousel"]
        if any(k in fid for k in ("kinetic", "flash", "glitch", "neon", "pop", "vertical")):
            plats = ["ig_reels", "yt_shorts", "tiktok", "yt_16x9"]
        pool.append({
            "id": f"favstash::{fid}",
            "raw_id": fid,
            "source": "favstash_99_film_looks",
            "title": f"Film Look · {fid.replace('-', ' ').title()}",
            "desc_fa": f"استایل سینمایی/موشن «{fid}» از مخزن Favstash منطبق با کادر و ضرب‌آهنگ صحنه",
            "platforms": plats,
            "tone": tone,
            "palette": {"bg": bg, "ink": ink, "accent": acc, "secondary": sec},
            "fa_font": fa_choices[i % len(fa_choices)],
            "sig_anim": "mask_wipe_rtl + continuous_onetake",
            "paired_gl": ["DirectionalWarp", "CrossZoom", "BurnThrough"],
            "paired_vfx": ["aces_filmic", "vignette_cinema_pro"],
            "moods": _infer_moods_from_tokens(fid),
            "tier_bonus": 8.0,
        })

    # 1C. 18 Vertical Creator Style Kit Archetypes
    v18_dir = os.path.join(STUDIO, "skills", "youtube-instagram-video-agents", "10_creator_style_kit_18_vertical_styles", "sfx")
    v18_names = sorted(os.listdir(v18_dir)) if os.path.isdir(v18_dir) else []
    for i, vid in enumerate(v18_names):
        tone = "light" if "paper" in vid or "notebook" in vid or "swiss" in vid or "clay" in vid else "dark"
        bg = "#F5F0E6" if tone == "light" else "#070A12"
        ink = "#121316" if tone == "light" else "#F8FAFC"
        pool.append({
            "id": f"vertical18::{vid}",
            "raw_id": vid,
            "source": "creator_style_kit_18",
            "title": f"Creator Vertical · {vid.replace('-', ' ').title()}",
            "desc_fa": f"آرکیتایپ تخصصی ریلز/شورتس و گرافیک متحرک «{vid}» با پک SFX اختصاصی",
            "platforms": ["ig_reels", "yt_shorts", "tiktok", "ig_story", "ig_carousel", "yt_16x9"],
            "tone": tone,
            "palette": {"bg": bg, "ink": ink, "accent": "#FACC15" if tone == "dark" else "#E11D48", "secondary": "#38BDF8"},
            "fa_font": fa_choices[(i + 2) % len(fa_choices)],
            "sig_anim": "hormozi_box_jump + elastic_scale",
            "paired_gl": ["CrossZoom", "DirectionalWarp"],
            "paired_vfx": ["aces_filmic", "unsharp_micro_pop"],
            "moods": _infer_moods_from_tokens(vid),
            "tier_bonus": 10.0,
        })

    # 1D. 6 Onetake Continuous-Camera Looks + 6 Melvynx Short Looks
    ot_path = os.path.join(STUDIO, "skills", "onetake-continuous-camera", "looks", "looks.json")
    if os.path.isfile(ot_path):
        ot = json.load(open(ot_path, encoding="utf-8")).get("looks", {})
        for lid, lval in (ot.items() if isinstance(ot, dict) else []):
            tone = "light" if lid in ("paper", "riso", "tabletop") else "dark"
            pool.append({
                "id": f"onetake::{lid}",
                "raw_id": lid,
                "source": "onetake_continuous_camera",
                "title": f"Onetake Camera Look · {lid.title()}",
                "desc_fa": f"پالت و نورپردازی دوربین پیوسته Onetake («{lid}») بدون کات مرئی",
                "platforms": ["yt_16x9", "ig_reels", "yt_shorts"],
                "tone": tone,
                "palette": {"bg": "#F3EFE6" if tone == "light" else "#080C16", "ink": "#111215" if tone == "light" else "#F8FAFC", "accent": "#F97316", "secondary": "#38BDF8"},
                "fa_font": "Estedad Black",
                "sig_anim": "continuous_onetake + zoom_portal_thru",
                "paired_gl": ["DreamyZoom", "CrossZoom"],
                "paired_vfx": ["aces_filmic", "bokeh_depth_pulse"],
                "moods": _infer_moods_from_tokens(f"onetake {lid} {json.dumps(lval)[:120]}"),
                "tier_bonus": 10.0,
            })

    mv_path = os.path.join(STUDIO, "skills", "youtube-instagram-video-agents", "02_melvynx_youtube_insta_creator_suite", "short-editing", "assets", "looks.json")
    if os.path.isfile(mv_path):
        mv = json.load(open(mv_path, encoding="utf-8"))
        for lid in mv.keys():
            if lid.startswith("_"):
                continue
            tone = "light" if lid in ("papier", "classique") else "dark"
            pool.append({
                "id": f"melvynx::{lid}",
                "raw_id": lid,
                "source": "melvynx_creator_suite",
                "title": f"Creator Look · {lid.title()}",
                "desc_fa": f"استایل تدوین سریع یوتیوب/اینستاگرام Melvynx («{lid}»)",
                "platforms": ["ig_reels", "yt_shorts", "yt_16x9", "tiktok"],
                "tone": tone,
                "palette": {"bg": "#F6F1E7" if tone == "light" else "#090B10", "ink": "#141416" if tone == "light" else "#FFFFFF", "accent": "#FF2E86", "secondary": "#FACC15"},
                "fa_font": "Shabnam Bold",
                "sig_anim": "per_word_pop + vox_highlighter",
                "paired_gl": ["WhipPan", "CrossZoom"],
                "paired_vfx": ["aces_filmic", "flash_frame_pop"],
                "moods": _infer_moods_from_tokens(f"melvynx {lid} creator"),
                "tier_bonus": 9.0,
            })

    return pool


# ==============================================================================
# POOL 2 & 3: PLATFORM TYPOGRAPHY (100 per platform, 700 total) + THUMBNAIL (100)
# ==============================================================================
def load_typography_pool(platform: str) -> list[dict]:
    cat_path = os.path.join(STUDIO, "skills", "typography-library", "catalog.json")
    cat = json.load(open(cat_path, encoding="utf-8"))
    out = []
    for p in cat["presets"]:
        if p["platform"] != platform:
            continue
        tok = f"{p['family']} {p['layout']} {p['fill']} {p['effect']} {p['motion']} {p['palette']} {p['colors'].get('note', '')}"
        tone = "light" if p["palette"] in ("paper_bone", "sand_ink", "ft_salmon_paper", "riso_coral_teal") else "dark"
        out.append({
            **p,
            "title": f"{p['family']} · {p['layout']} · {p['motion']}",
            "desc_fa": f"{p['name_fa']} | فونت: {p['fonts']['fa']} | انیمیشن: {p['motion']} | پالت: {p['palette']}",
            "tone": tone,
            "moods": _infer_moods_from_tokens(tok),
            "tier_bonus": 10.0 if p["layout"] in ("big_number_hero", "photo_witness_split", "versus_duel_card", "karaoke_word_box", "strip_highlight", "dossier_stamp_card", "hud_telemetry_box") else 6.0,
        })
    return out


# ==============================================================================
# POOL 4: VERIFIED FONT STACK TRIOS + LANGCHAIN CAPTION IDENTITIES (120 Items)
# ==============================================================================
def build_font_and_caption_pool() -> list[dict]:
    lc_path = os.path.join(STUDIO, "skills", "mega-style-vfx-arsenal", "mega_arsenal_index.json")
    lc_themes = json.load(open(lc_path, encoding="utf-8")).get("langchain_caption_themes", [])
    if not lc_themes:
        lc_themes = ["cream", "ink", "dossier", "scoreboard", "vhs", "neon", "editorial", "chalkboard", "chrome", "aurora"]

    fa_heads = [
        f for f in (typo_eng.FA_DISPLAY + typo_eng.FA_EDITORIAL)
        if f[0] not in ("Changa", "Harmattan Bold")
    ]
    fa_bodies = typo_eng.FA_TEXT
    monos = typo_eng.FA_MONO + typo_eng.EN_MONO
    en_heads = typo_eng.EN_DISPLAY

    pool = []
    idx = 0
    for round_i in range(2):
        for hi, (h_name, h_file, h_note) in enumerate(fa_heads):
            for bi, (b_name, b_file, b_note) in enumerate(fa_bodies):
                if len(pool) >= 120:
                    break
                m_name, m_file, _ = monos[(hi + bi + round_i * 3) % len(monos)]
                e_name, e_file, _ = en_heads[(hi * 2 + bi + round_i * 5) % len(en_heads)]
                cap_theme = lc_themes[(idx + round_i * 11) % len(lc_themes)]
                idx += 1
                cid = f"fontstack_{idx:03d}__{h_name.lower().replace(' ', '_')}__{cap_theme}"
                pool.append({
                    "id": cid,
                    "family_pair": f"{h_name}+{cap_theme}",
                    "title": f"{h_name} + {b_name} + {m_name} (Caption: {cap_theme})",
                    "desc_fa": f"تیتر فارسی: {h_name} | متن: {b_name} | داده/کد: {m_name} | تم زیرنویس: {cap_theme}",
                    "fa_headline": {"name": h_name, "file": h_file, "role": h_note},
                    "fa_body": {"name": b_name, "file": b_file, "role": b_note},
                    "mono_font": {"name": m_name, "file": m_file},
                    "en_accent": {"name": e_name, "file": e_file},
                    "caption_dna": cap_theme,
                    "platforms": list(PLATFORM_SPECS.keys()),
                    "moods": _infer_moods_from_tokens(f"{h_name} {h_note} {b_note} {cap_theme}"),
                    "tier_bonus": 11.5 if h_name in ("Lalezar", "Vazirmatn Black", "Estedad Black", "Sahel Black", "Shabnam Bold", "Changa", "Markazi Text") else 7.5,
                })
    return pool


# ==============================================================================
# POOL 5: MOTION & CAMERA CHOREOGRAPHY ARSENAL (315 Real Templates & Engines)
# ==============================================================================
def build_motion_choreography_pool() -> list[dict]:
    om_path = os.path.join(STUDIO, "skills", "openmotion-motion-library", "index.json")
    om_entries = json.load(open(om_path, encoding="utf-8")).get("entries", [])
    pool = []

    # 5A. 28 Core Studio Kinetic & Camera Curves (Onetake + Explainroo + GSAP + Movis)
    camera_rigs = [
        ("onetake_continuous_f_t", "دوربین پیوسته Onetake f(t) با زوم، پن عمیق و شاتر موشن‌بلار"),
        ("explainroo_canvas_cues", "بوم هوشمند Explainroo با رسم زنده فلش‌ها، دیاگرام‌ها و کارت‌ها"),
        ("gsap_custom_ease_stagger", "موتور GSAP 3 + CustomEase با ورود پلکانی کلمات و اعداد"),
        ("movis_25d_parallax_rig", "دوربین ۲.۵بعدی پارالاکس چندلایه (پیش‌زمینه، سوژه واقعی، پس‌زمینه)"),
        ("moderngl_zoom_portal", "رندرینگ شتاب‌یافته GPU ModernGL با زوم از دل نقشه و نمودار"),
    ]
    for i, (m_key, m_val) in enumerate(typo_eng.MOTIONS.items()):
        rig_id, rig_desc = camera_rigs[i % len(camera_rigs)]
        pool.append({
            "id": f"kinetic_rig::{m_key}__{rig_id}",
            "source": "studio_kinetic_camera_rigs",
            "title": f"{m_key} + {rig_id}",
            "desc_fa": f"کوریوگرافی حرکتی «{m_key}» ({m_val['py_curve']}, {m_val['dur']}s) همراه با {rig_desc}",
            "motion_curve": m_key,
            "py_curve": m_val["py_curve"],
            "duration_s": m_val["dur"],
            "ease": m_val["ease"],
            "camera_rig": rig_id,
            "platforms": list(PLATFORM_SPECS.keys()),
            "moods": _infer_moods_from_tokens(f"{m_key} {m_val['py_curve']} {rig_id}"),
            "tier_bonus": 13.0,
        })

    # 5B. 287 OpenMotion Reverse-Engineered Motion Studies
    for i, e in enumerate(om_entries):
        dur = float(e.get("duration_s") or 18.0)
        rig_id, rig_desc = camera_rigs[i % len(camera_rigs)]
        m_keys = list(typo_eng.MOTIONS.keys())
        paired_curve = m_keys[i % len(m_keys)]
        plats = ["ig_reels", "yt_shorts", "tiktok", "yt_16x9"] if dur <= 22 else ["yt_16x9", "ig_reels", "yt_shorts"]
        pool.append({
            "id": f"openmotion::{e['id'][:22]}",
            "source": "openmotion_287_library",
            "title": f"OpenMotion Study · {e.get('title', e['id'][:16])} ({dur:.1f}s)",
            "desc_fa": f"الگوی مهندسی‌معکوس موشن «{e.get('title', e['id'][:12])}» ({dur:.1f} ثانیه) + {rig_desc}",
            "motion_md": e.get("motion_md", ""),
            "motion_curve": paired_curve,
            "camera_rig": rig_id,
            "study_duration_s": round(dur, 2),
            "platforms": plats,
            "moods": _infer_moods_from_tokens(f"{e.get('title', '')} {paired_curve} {rig_id}"),
            "tier_bonus": 8.5,
        })

    return pool


# ==============================================================================
# POOL 6: IMAGERY, REAL PHOTOGRAPHY, THUMBNAIL & 4K DATA-VIZ ARSENAL (108 Recipes)
# ==============================================================================
def build_imagery_and_viz_pool() -> list[dict]:
    archetypes = [
        ("real_photo_witness_kenburns", "عکس واقعی مستند بدون واترمارک + اصلاح رنگ سینمایی ACES + حرکت آرام Ken Burns", ["street_human", "crisis_economy", "investigative_noir"]),
        ("real_photo_split_duel", "قاب دوتایی عکس واقعی (تضاد اسمی در برابر واقعی / قبل و بعد) + تیتر کوبشی", ["crisis_economy", "viral_shock", "editorial_press"]),
        ("real_archival_16mm_dossier", "عکس واقعی تاریخی آرشیوی با بافت فیلم ۱۶ میلی‌متری، برچسب تاریخ و مهر پرونده", ["historical_archive", "investigative_noir"]),
        ("real_landmark_parallax_25d", "عکاسی واقعی بناهای کلیدی (بانک مرکزی، مجلس، بازار تهران) با جداسازی عمق و نور حاشیه‌ای", ["crisis_economy", "geopolitics_map", "editorial_press"]),
        ("geojson_iran_31_provinces_glow", "نقشه وکتور آفلاین ۳۱ استان ایران (`iran_provinces.min.geojson`) با هایلایت نئونی و کمان جریان", ["geopolitics_map", "crisis_economy", "fintech_data"]),
        ("geojson_world_180_arcs", "نقشه وکتور ۱۸۰ کشور جهان (`world_countries.geo.json`) با کمان‌های درخشان و پینگ راداری", ["geopolitics_map", "historical_archive", "fintech_data"]),
        ("mplfinance_4k_candlestick", "نمودار ۴K کندل‌استیک و حجم معاملات بازار (`mplfinance`) با میانگین متحرک طلایی/آبی", ["fintech_data", "crisis_economy"]),
        ("glow_multi_trend_4k", "نمودار روند چندگانه درخشان (شکاف حقوق و تورم / رشد نقدینگی) با شمارنده زنده", ["fintech_data", "crisis_economy", "educational_board"]),
        ("squarify_budget_treemap_4k", "نقشه درختی سهم‌بندی بودجه و هزینه‌ها (`squarify` Treemap) با برچسب فارسی HarfBuzz", ["fintech_data", "crisis_economy", "editorial_press"]),
        ("spider_radar_comparison_4k", "نمودار راداری چندمحوره مقایسه قدرت/شاخص‌ها (`studio_plugins.py` Radar)", ["geopolitics_map", "fintech_data", "science_system"]),
        ("networkx_flow_anatomy_4k", "گراف شبکه جریان پول، تحریم یا زنجیره تأمین (`networkx` + `d3-sankey`)", ["science_system", "investigative_noir", "fintech_data"]),
        ("skia_glass_hud_telemetry", "کارت‌های شیشه مات بلورین Google Skia C++ روی تصویر واقعی با آمار لحظه‌ای", ["fintech_data", "tech_cyber", "street_human"]),
        ("ai_cinema_broll_generate_image", "تصویرسازی سینمایی اختصاصی با ابزار `generate_image` (نورپردازی آنامورفیک ۳۵ میلی‌متری)", ["poetic_heritage", "tech_cyber", "viral_shock"]),
        ("newspaper_clipping_highlighter", "کلاژ بریده روزنامه و اسناد رسمی با حرکت ماژیک زرد Vox روی کلیدواژه", ["editorial_press", "investigative_noir", "historical_archive"]),
        ("explainroo_diagram_chalkboard", "رسم مرحله‌به‌مرحله دیاگرام علّی و معلولی با پیکان‌های دست‌کشیده و فرمول ساده", ["educational_board", "science_system"]),
        ("street_receipt_price_ticker", "تصویر واقعی اتیکت قیمت، فیش حقوقی و سبد خرید با زوم ماکرو روی اعداد", ["street_human", "crisis_economy", "viral_shock"]),
        ("thumb_real_photo_versus_monolith", "تامبنیل استاندارد CTR بالا: عکس واقعی + مقایسه دو عدد متضاد + قرص مشکی هوک پایین", ["crisis_economy", "viral_shock", "fintech_data"]),
        ("thumb_witness_red_arrow_shock", "تامبنیل مستند یوتیوب: سوژه واقعی با کنتراست بالا + پیکان/کادر زرد + تیتر ۳ کلمه‌ای لاله‌زار", ["street_human", "investigative_noir", "viral_shock"]),
    ]
    grades = [
        ("aces_storm_gold", "اصلاح رنگ طوفانی تیره با هایلایت طلایی"),
        ("crimson_thriller", "کنتراست بالای مشکی-یاقوتی بحران"),
        ("cold_cyan_dossier", "تونالیته سرد آبی-فولادی تحقیقی"),
        ("warm_vox_newsprint", "بافت گرم مطبوعاتی و مستند"),
        ("emerald_terminal", "نورپردازی سبز-طلایی تالار بورس"),
        ("archival_silver_1923", "گرید نقره-ژلاتین تاریخی ۱۹۲۳"),
    ]

    pool = []
    idx = 0
    for arch_id, arch_desc, arch_moods in archetypes:
        for gr_id, gr_desc in grades:
            idx += 1
            plats = list(PLATFORM_SPECS.keys())
            if arch_id.startswith("thumb_"):
                plats = ["yt_16x9", "yt_shorts", "ig_reels"]
            pool.append({
                "id": f"imgviz_{idx:03d}__{arch_id}__{gr_id}",
                "archetype": arch_id,
                "grade_treatment": gr_id,
                "title": f"{arch_id} ({gr_id})",
                "desc_fa": f"{arch_desc} — همراه با {gr_desc}",
                "uses_real_photography": ("real_" in arch_id or "street_" in arch_id or "thumb_" in arch_id),
                "platforms": plats,
                "moods": list(dict.fromkeys(arch_moods + _infer_moods_from_tokens(gr_id))),
                "tier_bonus": 14.0 if ("real_" in arch_id or "geojson_" in arch_id or "candlestick" in arch_id or "thumb_" in arch_id) else 9.0,
            })
    return pool


# ==============================================================================
# POOL 7: 265 GPU OPENGL GLSL TRANSITIONS (`gl-transitions`)
# ==============================================================================
def build_gl_transitions_pool() -> list[dict]:
    names = list_gl_transitions()
    curated_kings = {
        "CrossZoom", "BurnThrough", "DirectionalWarp", "CameraShake", "GlitchMemories",
        "BokehDissolve", "BloomDissolve", "DreamyZoom", "PageCurl", "WhipPan",
        "WhipTilt", "Flash", "FilmBurn", "Pixelize", "GridFlip", "Morph",
        "Swirl", "LumaWipe", "ShutterWipe", "PaperTear", "VhsTracking", "Shockwave",
    }
    pool = []
    for n in names:
        nl = n.lower()
        if any(k in nl for k in ("whip", "zoom", "flash", "shake", "shock", "slam", "punch")):
            energy = "high"
            plats = ["ig_reels", "yt_shorts", "tiktok", "yt_16x9"]
        elif any(k in nl for k in ("glitch", "vhs", "tv", "pixel", "ascii", "static", "datamosh")):
            energy = "glitch"
            plats = ["ig_reels", "yt_shorts", "tiktok", "yt_16x9"]
        elif any(k in nl for k in ("burn", "film", "bokeh", "bloom", "dream", "fade", "luma", "smoke", "ink", "paper")):
            energy = "cinema"
            plats = ["yt_16x9", "ig_reels", "yt_shorts", "ig_carousel"]
        else:
            energy = "editorial"
            plats = list(PLATFORM_SPECS.keys())

        pool.append({
            "id": f"gl::{n}",
            "shader_name": n,
            "shader_path": os.path.join(STUDIO, "vfx-repos", "gl-transitions", f"{n}.glsl"),
            "energy": energy,
            "title": f"GLSL Transition · {n} ({energy})",
            "desc_fa": f"ترنزیشن شتاب‌یافته GPU OpenGL «{n}» با انرژی حرکتی {energy}",
            "platforms": plats,
            "moods": _infer_moods_from_tokens(f"{n} {energy}"),
            "tier_bonus": 13.5 if n in curated_kings else 7.0,
        })
    return pool


# ==============================================================================
# POOL 8: 570 SPECIAL EFFECTS, LYGIA SHADERS & FREI0R C++ VIDEO PLUGINS
# ==============================================================================
def build_vfx_and_shaders_pool() -> list[dict]:
    pool = []

    # 8A. 36 Procedural Studio GPU/OpenCV/Skia VFX Recipes
    for k, desc in sva.PROCEDURAL_VFX.items():
        pool.append({
            "id": f"proc_vfx::{k}",
            "engine": "studio_procedural_gpu",
            "vfx_key": k,
            "title": f"Studio VFX · {k}",
            "desc_fa": f"افکت ویژه بی‌درنگ استودیو «{k}»: {desc}",
            "platforms": list(PLATFORM_SPECS.keys()),
            "moods": _infer_moods_from_tokens(f"{k} {desc}"),
            "tier_bonus": 14.0,
        })

    # 8B. 156 Native C++ Frei0r-1 Video Plugins
    useful_frei0r = {"glow", "glitch0r", "baltan", "cartoon", "vignette", "sigmoidaltransfer", "coloradj_RGB", "defish0r", "emboss", "halftone", "hqdn3d", "lenscorrection", "levels", "nervous", "nosync0r", "pixeliz0r", "posterize", "scanline0r", "sharpness", "sobel", "softglow", "tint0r", "vertigo"}
    for p in sorted(glob.glob("/usr/lib/frei0r-1/*.so")):
        fn = os.path.splitext(os.path.basename(p))[0]
        pool.append({
            "id": f"frei0r::{fn}",
            "engine": "ffmpeg_frei0r_cpp",
            "plugin_name": fn,
            "so_path": p,
            "title": f"Frei0r C++ Plugin · {fn}",
            "desc_fa": f"پلاگین پردازش تصویر C++ بومی `frei0r={fn}` در زنجیره فیلتر FFmpeg",
            "platforms": list(PLATFORM_SPECS.keys()),
            "moods": _infer_moods_from_tokens(f"frei0r {fn}"),
            "tier_bonus": 11.5 if fn in useful_frei0r else 5.0,
        })

    # 8C. 378 LYGIA GLSL Shader Modules
    priority_lygia_dirs = ("filter/", "color/tonemap", "distort/", "generative/")
    for rel in list_lygia_modules():
        bonus = 11.0 if any(rel.startswith(f"lygia/{d}") for d in priority_lygia_dirs) else 5.5
        pool.append({
            "id": f"lygia::{rel}",
            "engine": "moderngl_lygia_glsl",
            "module_path": rel,
            "title": f"LYGIA GLSL · {rel}",
            "desc_fa": f"ماژول شیدر سینمایی OpenGL LYGIA (`{rel}`) با پشتیبانی `#include` خودکار",
            "platforms": list(PLATFORM_SPECS.keys()),
            "moods": _infer_moods_from_tokens(rel),
            "tier_bonus": bonus,
        })

    return pool


# ==============================================================================
# POOL 9: VOICE (`voice-05` LOCKED) + 108 PEDALBOARD & LADSPA VOCAL DSP RACKS
# ==============================================================================
def build_voice_dsp_pool() -> list[dict]:
    ladspa_files = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob("/usr/lib/ladspa/*.so"))
    has_tube = "tap_tubewarmth" in ladspa_files

    archetypes = [
        ("cinema_investigative_authority", "صدای مستند تحقیقی عمیق و مقتدر (گرمای لامپی Pultec + شفافیت ۳.۵ کیلوهرتز)", 2.8, 3.6, 2.8, 0.16, 11, ["investigative_noir", "crisis_economy", "geopolitics_map"]),
        ("urgent_breaking_briefing", "صدای گزارش فوری خبری با حضور جلوآمده و کمپرس سریع بدون افت انرژی", 3.2, 2.2, 3.6, 0.10, 8, ["crisis_economy", "viral_shock", "editorial_press"]),
        ("warm_street_storyteller", "صدای صمیمی و انسانی روایت خیابانی با گرمای طبیعی سینه و اتاق مخملی", 2.4, 4.0, 2.2, 0.20, 14, ["street_human", "poetic_heritage", "historical_archive"]),
        ("viral_reels_punch_presence", "صدای فوق‌شفاف و پرانرژی مخصوص ریلز و شورتس (شنیده‌شدن عالی روی اسپیکر موبایل)", 3.5, 2.6, 4.1, 0.08, 7, ["viral_shock", "tech_cyber", "educational_board"]),
        ("bloomberg_precision_desk", "صدای تیز، تمیز و استودیویی میز تحلیل داده و اقتصاد کلان", 1.9, 2.5, 3.2, 0.12, 10, ["fintech_data", "editorial_press", "science_system"]),
        ("archival_documentary_velvet", "صدای گرم کلاسیک مستند تاریخی با اشباع آنالوگ نوار مغناطیسی نرم", 3.4, 3.8, 2.0, 0.24, 16, ["historical_archive", "poetic_heritage", "investigative_noir"]),
        ("chalkboard_mentor_clarity", "صدای آموزشی آرام، شمرده و بدون خستگی گوش برای ویدیوهای تحلیلی طولانی", 2.0, 3.0, 2.9, 0.15, 12, ["educational_board", "science_system"]),
        ("cyber_futurist_crisp", "صدای مدرن با هوای ابریشمی ۱۰ کیلوهرتز و تصویر استریوی Micro-Haas عریض", 2.6, 2.4, 3.5, 0.19, 15, ["tech_cyber", "science_system", "viral_shock"]),
        ("economist_editorial_dry", "صدای خشک و نزدیک رادیویی/پادکستی به سبک نیویورکر و اکونومیست", 1.8, 3.2, 2.6, 0.06, 6, ["editorial_press", "fintech_data"]),
    ]
    lufs_targets = [-13.8, -14.0, -14.2]
    comp_styles = [
        ("smooth_optocomp", 2.8, 14.0),
        ("broadcast_fet", 3.4, 9.0),
        ("punchy_vca", 4.0, 6.5),
        ("velvet_tube", 2.5, 18.0),
    ]

    pool = []
    idx = 0
    for a_id, a_desc, drive, low_db, pres_db, room, haas_ms, moods in archetypes:
        for c_id, ratio, atk_ms in comp_styles:
            for lufs in lufs_targets:
                idx += 1
                plats = list(PLATFORM_SPECS.keys())
                if "reels" in a_id:
                    plats = ["ig_reels", "yt_shorts", "tiktok", "ig_story"]
                pool.append({
                    "id": f"vocal_dsp_{idx:03d}__{a_id}__{c_id}_{abs(int(lufs*10))}",
                    "archetype": a_id,
                    "voice_id": "voice-05",  # PERMANENT ARENA VOICE MANDATE
                    "tts_tool": "Arena generate_speech(voice_id='voice-05')",
                    "local_tts_banned": True,
                    "ladspa_plugin": "tap_tubewarmth" if has_tube else "pedalboard_warmth",
                    "compressor_mode": c_id,
                    "params": {
                        "tube_drive": drive,
                        "low_shelf_128hz_db": low_db,
                        "presence_3450hz_db": pres_db,
                        "air_9800hz_db": 3.0,
                        "comp_ratio": ratio,
                        "comp_attack_ms": atk_ms,
                        "reverb_room": room,
                        "haas_delay_ms": haas_ms,
                        "target_lufs": lufs,
                    },
                    "title": f"voice-05 · {a_id} ({c_id}, {lufs} LUFS)",
                    "desc_fa": f"گوینده دائمی `voice-05` + پردازش C++ Pedalboard/LADSPA: {a_desc} ({lufs} LUFS)",
                    "platforms": plats,
                    "moods": moods,
                    "tier_bonus": 12.5 if lufs in (-13.8, -14.0) else 9.0,
                })
    return pool


# ==============================================================================
# POOL 10: 108 STEREO 48kHz CINEMA & FOLEY SFX SYNTHESIZER RECIPES
# ==============================================================================
def build_sfx_arsenal_pool() -> list[dict]:
    base_families = [
        ("imax_sub_drop", "فرود ساب‌بیس سینمایی عمیق برای هوک و شوک آماری", "impact", ["crisis_economy", "investigative_noir", "viral_shock"]),
        ("anamorphic_whoosh", "عبور هوای استریوی عریض همگام با ترنزیشن دوربین", "transition", ["geopolitics_map", "viral_shock", "tech_cyber"]),
        ("kinetic_stomp_slam", "ضربه کوبشی تیتر بزرگ همگام با اوج هجای گوینده", "impact", ["viral_shock", "crisis_economy", "street_human"]),
        ("split_flap_clack", "تق‌تق مکانیکی تابلو فرودگاهی و شمارنده ارقام اقتصادی", "data", ["fintech_data", "crisis_economy", "geopolitics_map"]),
        ("rubber_stamp_thud", "کوبش مهر سنگین روی پرونده و اسناد محرمانه", "accent", ["investigative_noir", "historical_archive", "editorial_press"]),
        ("typewriter_dossier_key", "ضربه ماشین‌تحریر کلاسیک برای تاریخ، مکان و برچسب آرشیو", "data", ["historical_archive", "investigative_noir", "editorial_press"]),
        ("radar_sonar_ping", "پینگ شفاف راداری برای نقاط داغ نقشه ایران و جهان", "data", ["geopolitics_map", "fintech_data", "science_system"]),
        ("tension_orchestral_riser", "خیزش تدریجی تنش صوتی پیش از افشای عدد یا اوج داستان", "riser", ["investigative_noir", "crisis_economy", "viral_shock"]),
        ("paper_rip_clipping", "صدای لمس و برش کاغذ روزنامه برای سبک Vox و اسناد", "transition", ["editorial_press", "historical_archive", "educational_board"]),
        ("camera_shutter_witness", "شاتر دوربین عکاسی مستند هنگام نمایش عکس واقعی خیابانی", "accent", ["street_human", "historical_archive", "investigative_noir"]),
        ("digital_hud_blip", "پالس ظریف دیجیتال برای نمودار کندل‌استیک و ترمینال داده", "data", ["fintech_data", "tech_cyber", "science_system"]),
        ("heartbeat_crisis_pulse", "ضربان قلب پایین‌گذر زیر روایت تعلیق و بحران معیشتی", "ambience", ["crisis_economy", "street_human", "investigative_noir"]),
        ("chalk_board_stroke", "خش‌خش نرم گچ روی تخته هنگام رسم دیاگرام آموزشی", "data", ["educational_board", "science_system"]),
        ("vhs_cassette_glitch", "کلیک مکانیکی و پرش نوار مغناطیسی VHS برای مستند خیابانی", "transition", ["street_human", "historical_archive", "tech_cyber"]),
        ("crystalline_shimmer", "درخشش هارمونیک لطیف برای نتیجه‌گیری، راه‌حل و جمع‌بندی", "reveal", ["poetic_heritage", "educational_board", "science_system"]),
        ("marker_highlighter_swipe", "کشیده‌شدن ماژیک هایلایتر روی کلیدواژه مهم", "accent", ["editorial_press", "educational_board", "fintech_data"]),
        ("cash_ticker_cascade", "ریزش سریع پالس شمارش پول و تورم نقطه‌به‌نقطه", "data", ["crisis_economy", "fintech_data", "street_human"]),
        ("whip_air_snap", "سیلی سریع هوا ویژه کات‌های ۱.۸ ثانیه‌ای ریلز و شورتس", "transition", ["viral_shock", "street_human", "tech_cyber"]),
    ]
    tunings = [
        ("deep_cinema", 0.82, 0.34, "کوک بم سینمایی تیره"),
        ("tight_broadcast", 1.00, 0.16, "کوتاه و تیز خبری"),
        ("bright_mobile", 1.18, 0.12, "شفاف ویژه اسپیکر موبایل"),
        ("hall_epic", 0.90, 0.45, "پژواک تالار بزرگ مستند"),
        ("analog_tape", 0.95, 0.22, "گرم آنالوگ اشباع‌شده"),
        ("crisp_minimal", 1.08, 0.09, "مینیمال و ظریف مدرن"),
    ]

    pool = []
    idx = 0
    for fam_id, fam_desc, role, moods in base_families:
        for tun_id, pitch_mul, rev_wet, tun_desc in tunings:
            idx += 1
            plats = list(PLATFORM_SPECS.keys())
            if tun_id == "bright_mobile":
                plats = ["ig_reels", "yt_shorts", "tiktok", "ig_story"]
            pool.append({
                "id": f"sfx_{idx:03d}__{fam_id}__{tun_id}",
                "family": fam_id,
                "role": role,
                "tuning": tun_id,
                "pitch_mul": pitch_mul,
                "reverb_wet": rev_wet,
                "title": f"{fam_id} · {tun_id} ({role})",
                "desc_fa": f"{fam_desc} — {tun_desc} (استریو ۴۸kHz با Pedalboard)",
                "platforms": plats,
                "moods": moods,
                "tier_bonus": 12.0 if role in ("impact", "transition", "data") else 9.5,
            })
    return pool


# ==============================================================================
# POOL 11: 108 PROCEDURAL SYMPHONIC / ELECTRONIC / PERSIAN-MODAL MUSIC SCORES
#          (`FluidR3_GM.sf2` 128 GM Instruments + `Spotify Pedalboard` + Ducking)
# ==============================================================================
def build_music_score_pool() -> list[dict]:
    # GM Program numbers (0-indexed MIDIUtil program_change):
    # 42=Cello, 48=String Ensemble 1, 49=Slow Strings, 45=Pizzicato Strings,
    # 0=Acoustic Grand Piano, 4=Electric Piano 1, 11=Vibraphone, 12=Marimba,
    # 38=Synth Bass 1, 39=Synth Bass 2, 88=Pad New Age, 89=Pad Warm, 95=Pad Sweep,
    # 15=Dulcimer (Santur-like), 46=Orchestral Harp, 73=Flute, 47=Timpani
    compositions = [
        ("noir_cello_sub_pulse", "ویولنسل سولو تیره + پالس ساب‌بیس و زهی‌های پرتعلیق (سبک مستند بحران)", 84, "d_harmonic_minor", [42, 48, 38], ["crisis_economy", "investigative_noir", "street_human"]),
        ("chahargah_santur_tension", "تِم مدال ایرانی الهام‌گرفته از چهارگاه/همایون با سنتور (Dulcimer)، ویولنسل و پد گرم", 78, "d_phrygian_dom", [15, 42, 89], ["crisis_economy", "street_human", "poetic_heritage", "historical_archive"]),
        ("johnny_harris_marimba_clock", "ماریمبای ریتمیک ساعت‌شمار + پیانو الکتریک و زهی استاکاتو (سبک مستند نقشه‌محور)", 104, "a_dorian", [12, 4, 45], ["geopolitics_map", "investigative_noir", "editorial_press"]),
        ("bloomberg_synth_arp_ledger", "آرپژ سینت‌بیس دقیق + ویبرافون شیشه‌ای و پد سرد ترمینال مالی", 112, "e_aeolian", [39, 11, 95], ["fintech_data", "tech_cyber", "crisis_economy"]),
        ("weimar_1923_felt_piano", "پیانوی نمدی اندوهگین و زهی‌های کشیده آرشیو تاریخی قرن بیستم", 70, "c_aeolian", [0, 49, 42], ["historical_archive", "poetic_heritage", "investigative_noir"]),
        ("vox_pizzicato_curiosity", "پیتزیکاتوی کنجکاو و هوشمندانه + ماریمبا و پیانو برای ویدیوهای تحلیلی و آموزشی", 98, "g_mixolydian", [45, 12, 0], ["editorial_press", "educational_board", "science_system"]),
        ("viral_reels_dark_drive", "بیس کوبنده ۱۲۴ BPM + زهی کوتاه پرتنش مخصوص ریلز و شورتس با نرخ نگهداشت بالا", 124, "f_minor_pent", [38, 48, 11], ["viral_shock", "crisis_economy", "tech_cyber"]),
        ("manim_3b1b_celestial_pad", "پد فضایی آرام، چنگ و پیانوی مینیمال به سبک 3Blue1Brown و کشف علمی", 82, "c_lydian", [88, 46, 0], ["science_system", "educational_board", "poetic_heritage"]),
        ("economist_urgent_strings", "استاکاتوی سریع ارکستر زهی و تیمپانی ملایم برای گزارش‌های کلان ژئوپلیتیک", 116, "d_aeolian", [48, 45, 47], ["geopolitics_map", "editorial_press", "crisis_economy"]),
        ("cyber_neon_pulsewave", "پالس سینتی‌سایزر نئونی شبانه و پد استریوی عریض برای موضوعات تکنولوژی و آینده", 118, "a_phrygian", [39, 95, 4], ["tech_cyber", "viral_shock", "fintech_data"]),
        ("tehran_dusk_acoustic", "پیانو، فلوت گرم و زهی نرم برای روایت‌های انسانی، فرهنگی و معیشت روزمره", 76, "e_harmonic_minor", [0, 73, 89], ["street_human", "poetic_heritage", "historical_archive"]),
        ("countdown_thriller_tick", "تیک‌تاک ساعت تعلیق + باس عمیق برای شمارش معکوس و افشای ۵ سیگنال خطر", 108, "c_locrian_noir", [11, 38, 49], ["investigative_noir", "crisis_economy", "viral_shock"]),
    ]
    arrangements = [
        ("sparse_narrator_bed", 0.36, -8.5, "خلوت و باز در محدوده فرکانسی صدای گوینده (۳۰۰ تا ۳۵۰۰ هرتز)"),
        ("cinematic_arc_build", 0.44, -7.5, "شروع مینیمال و اوج‌گیری ارکسترال در یک‌سوم پایانی کلیپ"),
        ("pulsing_heartbeat_bed", 0.42, -8.0, "همراه با پالس ریتمیک منظم زیر روایت"),
    ]
    mastering_colors = [
        ("velvet_hall", 0.72, 0.28, "ریورب تالار مخملی عمیق"),
        ("tight_modern_room", 0.38, 0.16, "اتاق مدرن خشک و دقیق ویژه موبایل"),
        ("warm_tape_chorus", 0.56, 0.22, "گرمای نوار آنالوگ و استریوی عریض"),
    ]

    pool = []
    idx = 0
    for c_id, c_desc, bpm, scale_id, progs, moods in compositions:
        for arr_id, base_gain, duck_db, arr_desc in arrangements:
            for m_id, room_sz, wet, m_desc in mastering_colors:
                idx += 1
                plats = list(PLATFORM_SPECS.keys())
                if bpm >= 118:
                    plats = ["ig_reels", "yt_shorts", "tiktok", "yt_16x9"]
                pool.append({
                    "id": f"score_{idx:03d}__{c_id}__{arr_id}__{m_id}",
                    "composition": c_id,
                    "arrangement": arr_id,
                    "mastering": m_id,
                    "bpm": bpm,
                    "scale": scale_id,
                    "gm_programs": progs,
                    "base_gain": base_gain,
                    "sidechain_duck_db": duck_db,
                    "reverb_room": room_sz,
                    "reverb_wet": wet,
                    "soundfont": SOUNDFONT_GM,
                    "title": f"{c_id} ({bpm} BPM · {arr_id} · {m_id})",
                    "desc_fa": f"{c_desc} | تنظیم: {arr_desc} | مسترینگ: {m_desc} (با Sidechain Ducking خودکار زیر `voice-05`)",
                    "platforms": plats,
                    "moods": moods,
                    "tier_bonus": 13.0 if arr_id in ("sparse_narrator_bed", "cinematic_arc_build") else 10.0,
                })
    return pool


# ==============================================================================
# POOL 12: PACING, RETENTION & EDITORIAL GRAMMAR TEMPLATES (100 Recipes)
# ==============================================================================
def build_editorial_grammar_pool() -> list[dict]:
    structures = [
        ("hook_shock_5signals_verdict", "هوک شوک ۳ ثانیه‌ای -> چرایی بحران -> ۵ سیگنال خیابانی/عددی -> جمع‌بندی و چک‌لیست مخاطب", ["crisis_economy", "street_human", "viral_shock"]),
        ("paradox_question_anatomy", "طرح تناقض ذهنی («چرا با وجود X، اتفاق Y می‌افتد؟») -> کالبدشکافی لایه‌به‌لایه -> پاسخ نهایی", ["science_system", "fintech_data", "editorial_press"]),
        ("historical_mirror_now", "سفر به نمونه تاریخی مستند («نمونه‌های تاریخی، نه پیش‌بینی») -> تطبیق مکانیزم -> درس امروز", ["historical_archive", "crisis_economy", "investigative_noir"]),
        ("versus_duel_expose", "رویارویی دو عدد متضاد (ظاهر رسمی در برابر واقعیت سفره) -> ریشه‌یابی -> نتیجه ملموس", ["crisis_economy", "fintech_data", "viral_shock"]),
        ("map_zoom_investigation", "زوم از نقشه جهان/ایران به خیابان -> ردیابی جریان پول و کالا -> گره‌گشایی", ["geopolitics_map", "investigative_noir", "fintech_data"]),
        ("rapid_fire_myth_buster", "رد کردن ۳ باور رایج اشتباه با داده واقعی و مهر قرمز -> حقیقت ماجرا", ["viral_shock", "educational_board", "editorial_press"]),
        ("day_in_the_life_wallet", "روایت اول‌شخص از جیب یک شهروند عادی در بازار -> ترجمه به اقتصاد کلان", ["street_human", "crisis_economy", "poetic_heritage"]),
        ("system_blueprint_walkthrough", "نمایش نقشه مهندسی کل سیستم روی یک بوم واحد و حرکت پیوسته بین اجزا", ["science_system", "educational_board", "fintech_data"]),
        ("dossier_evidence_chain", "گشودن پرونده تحقیقاتی با اسناد شماره‌دار (مدرک ۱ تا ۴) و نتیجه‌گیری بی‌طرفانه", ["investigative_noir", "historical_archive", "editorial_press"]),
        ("scoreboard_countdown_ladder", "رده‌بندی پله‌به‌پله از کم‌اثرترین تا مهم‌ترین عامل با تابلوی شمارشگر زنده", ["fintech_data", "viral_shock", "geopolitics_map"]),
    ]
    pacing_modes = [
        ("hyper_retention_2s", 2.2, "ریتم فوق‌سریع ۲.۲ ثانیه‌ای ویژه ریلز و شورتس"),
        ("punchy_creator_3s", 3.2, "ریتم پرانرژی ۳.۲ ثانیه‌ای با ریست بصری مداوم"),
        ("youtube_doc_5s", 5.0, "ریتم استاندارد مستند یوتیوب (هر ۵ ثانیه تغییر لایه یا زوم)"),
        ("cinema_breathing_6s", 6.2, "ریتم سینمایی عمیق با مکث‌های دراماتیک روی اعداد کلیدی"),
        ("onetake_fluid_4s", 4.2, "حرکت پیوسته دوربین هر ۴.۲ ثانیه به ایستگاه بعدی روی بوم"),
    ]
    hook_devices = [
        ("cold_stat_slam", "کوبش عدد شوکه‌کننده بدون سلام و مقدمه در ثانیه ۰.۰"),
        ("street_quote_witness", "شروع با یک جمله واقعی که همه در خیابان شنیده‌اند"),
    ]

    pool = []
    idx = 0
    for st_id, st_desc, moods in structures:
        for pm_id, cut_s, pm_desc in pacing_modes:
            for hk_id, hk_desc in hook_devices:
                idx += 1
                plats = ["ig_reels", "yt_shorts", "tiktok", "ig_story"] if cut_s <= 3.0 else ["yt_16x9", "ig_carousel", "yt_shorts", "ig_reels"]
                pool.append({
                    "id": f"grammar_{idx:03d}__{st_id}__{pm_id}__{hk_id}",
                    "structure": st_id,
                    "pacing_mode": pm_id,
                    "hook_device": hk_id,
                    "avg_beat_sec": cut_s,
                    "title": f"{st_id} · {pm_id} ({hk_id})",
                    "desc_fa": f"ساختار روایت: {st_desc} | ضرب‌آهنگ: {pm_desc} | شروع: {hk_desc}",
                    "platforms": plats,
                    "moods": moods,
                    "tier_bonus": 12.0,
                })
    return pool


# ==============================================================================
# REAL AUDIO & VISUAL MATERIALIZERS (Synthesize chosen SFX, Music & Moodboard!)
# ==============================================================================
def synthesize_sfx_wav(sfx_item: dict, out_wav: str) -> str:
    """Synthesizes a real 24-bit 48kHz stereo WAV for ANY chosen SFX recipe in Pool 10."""
    import soundfile as sf
    from scipy import signal
    from pedalboard import Pedalboard, Reverb, Compressor, LowShelfFilter, HighShelfFilter, Limiter

    fam = sfx_item["family"]
    pm = float(sfx_item.get("pitch_mul", 1.0))
    wet = float(sfx_item.get("reverb_wet", 0.2))
    rng = np.random.default_rng(_det_hash(sfx_item["id"]) % (2**31 - 1))

    dur_map = {
        "imax_sub_drop": 0.95, "anamorphic_whoosh": 0.52, "kinetic_stomp_slam": 0.40,
        "split_flap_clack": 0.28, "rubber_stamp_thud": 0.36, "typewriter_dossier_key": 0.18,
        "radar_sonar_ping": 0.65, "tension_orchestral_riser": 1.60, "paper_rip_clipping": 0.34,
        "camera_shutter_witness": 0.24, "digital_hud_blip": 0.20, "heartbeat_crisis_pulse": 0.90,
        "chalk_board_stroke": 0.42, "vhs_cassette_glitch": 0.30, "crystalline_shimmer": 1.15,
        "marker_highlighter_swipe": 0.32, "cash_ticker_cascade": 0.55, "whip_air_snap": 0.26,
    }
    dur = dur_map.get(fam, 0.45)
    n = int(SR * dur)
    t = np.linspace(0.0, dur, n, endpoint=False)

    if fam == "imax_sub_drop":
        freq = (95.0 * np.exp(-5.2 * t) + 31.0) * pm
        ph = 2 * np.pi * np.cumsum(freq) / SR
        sig = np.tanh((np.sin(ph) * np.exp(-2.6 * t) * 1.45 + rng.standard_normal(n) * np.exp(-36 * t) * 0.4))
        st = np.vstack([sig, np.roll(sig, 16)])
    elif fam in ("anamorphic_whoosh", "whip_air_snap", "marker_highlighter_swipe", "paper_rip_clipping", "chalk_board_stroke"):
        noise = rng.standard_normal((2, n))
        lo = 220 * pm if "whoosh" in fam else 650 * pm
        hi = min(18000, 4800 * pm if "whoosh" in fam else 9500 * pm)
        sos = signal.butter(3, [lo, hi], btype="bandpass", fs=SR, output="sos")
        env = np.sin(np.pi * (t / dur) ** 0.8) ** (2.6 if "whip" in fam else 1.8)
        st = signal.sosfilt(sos, noise, axis=1) * env * 1.9
        pan = np.linspace(0.2, 0.85, n)
        st[0] *= (1.05 - 0.55 * pan)
        st[1] *= (0.45 + 0.55 * pan)
    elif fam in ("split_flap_clack", "typewriter_dossier_key", "camera_shutter_witness", "vhs_cassette_glitch"):
        clicks = [0.0, 0.055, 0.11, 0.165] if fam == "split_flap_clack" else ([0.0, 0.07] if "shutter" in fam else [0.0])
        sig = np.zeros(n)
        for c in clicks:
            idx0 = int(c * SR)
            if idx0 < n:
                rem = n - idx0
                tc = t[:rem]
                burst = (rng.standard_normal(rem) * np.exp(-tc * 95) * 0.8 +
                         np.sin(2 * np.pi * 1450 * pm * tc) * np.exp(-tc * 65) * 0.5)
                sig[idx0:] += burst
        st = np.vstack([sig, np.roll(sig, 9)])
    elif fam in ("radar_sonar_ping", "digital_hud_blip", "cash_ticker_cascade"):
        steps = [0.0, 0.09, 0.18, 0.27, 0.36] if "cascade" in fam else [0.0]
        sig = np.zeros(n)
        base_f = 1320.0 * pm if "radar" in fam else 1760.0 * pm
        for si, c in enumerate(steps):
            idx0 = int(c * SR)
            if idx0 < n:
                rem = n - idx0
                tc = t[:rem]
                f = base_f * (1.0 + 0.08 * si)
                decay = 5.5 if "radar" in fam else 26.0
                sig[idx0:] += (0.7 * np.sin(2 * np.pi * f * tc) + 0.3 * np.sin(2 * np.pi * f * 1.5 * tc)) * np.exp(-tc * decay)
        st = np.vstack([sig * 0.75, np.roll(sig * 0.75, 24)])
    elif fam == "tension_orchestral_riser":
        f0, f1 = 85.0 * pm, 880.0 * pm
        freq = f0 * ((f1 / f0) ** ((t / dur) ** 1.8))
        ph = 2 * np.pi * np.cumsum(freq) / SR
        env = ((t / dur) ** 2.3) * np.hanning(n * 2)[:n]
        sig = (0.6 * np.sin(ph) + 0.3 * np.sin(2.01 * ph) + 0.2 * rng.standard_normal(n)) * env
        st = np.vstack([sig, np.roll(sig, 28)])
    elif fam == "heartbeat_crisis_pulse":
        sig = np.zeros(n)
        for beat_t, amp in [(0.04, 1.0), (0.30, 0.68)]:
            idx0 = int(beat_t * SR)
            if idx0 < n:
                tc = t[:n - idx0]
                sig[idx0:] += amp * np.sin(2 * np.pi * (62 * pm) * tc) * np.exp(-tc * 14.0)
        st = np.vstack([sig, sig])
    elif fam == "crystalline_shimmer":
        freqs = [523.25 * pm, 659.25 * pm, 783.99 * pm, 1046.5 * pm, 1318.5 * pm]
        sl, sr_c = np.zeros(n), np.zeros(n)
        for idx_f, f in enumerate(freqs):
            env = np.exp(-2.3 * np.maximum(0, t - idx_f * 0.045)) * np.minimum(1.0, t / 0.03)
            sl += np.sin(2 * np.pi * f * t) * env * 0.22
            sr_c += np.sin(2 * np.pi * (f * 1.004) * t + 0.5) * env * 0.22
        st = np.vstack([sl, sr_c])
    else:  # kinetic_stomp_slam / rubber_stamp_thud
        slam = (np.sin(2 * np.pi * (135 * pm * np.exp(-t * 13)) * t) * np.exp(-t * 9.0) +
                0.55 * rng.standard_normal(n) * np.exp(-t * 34.0))
        st = np.vstack([slam, np.roll(slam * 0.96, 11)])

    board = Pedalboard([
        LowShelfFilter(110.0, gain_db=3.0),
        HighShelfFilter(5800.0, gain_db=1.8),
        Compressor(threshold_db=-14.0, ratio=3.5),
        Reverb(room_size=min(0.85, 0.25 + wet), damping=0.5, wet_level=min(0.5, wet), dry_level=0.88),
        Limiter(threshold_db=-1.2),
    ])
    proc = board(st.astype(np.float32), SR).T
    os.makedirs(os.path.dirname(os.path.abspath(out_wav)), exist_ok=True)
    sf.write(out_wav, proc, SR, subtype="PCM_24")
    return out_wav


SCALES_SEMITONES = {
    "d_harmonic_minor": (50, [0, 2, 3, 5, 7, 8, 11]),
    "d_phrygian_dom":   (50, [0, 1, 4, 5, 7, 8, 10]),  # Persian Homayoun / Chahargah flavor
    "a_dorian":         (57, [0, 2, 3, 5, 7, 9, 10]),
    "e_aeolian":        (52, [0, 2, 3, 5, 7, 8, 10]),
    "c_aeolian":        (48, [0, 2, 3, 5, 7, 8, 10]),
    "g_mixolydian":     (55, [0, 2, 4, 5, 7, 9, 10]),
    "f_minor_pent":     (53, [0, 3, 5, 7, 10, 12, 15]),
    "c_lydian":         (48, [0, 2, 4, 6, 7, 9, 11]),
    "d_aeolian":        (50, [0, 2, 3, 5, 7, 8, 10]),
    "a_phrygian":       (57, [0, 1, 3, 5, 7, 8, 10]),
    "e_harmonic_minor": (52, [0, 2, 3, 5, 7, 8, 11]),
    "c_locrian_noir":   (48, [0, 1, 3, 5, 6, 8, 10]),
}


def synthesize_music_score_wav(score_item: dict, out_wav: str, duration_sec: float = 12.0) -> str:
    """Synthesizes a multi-track 48kHz stereo soundtrack from Pool 11 using FluidR3_GM.sf2 + Pedalboard."""
    from midiutil import MIDIFile
    import soundfile as sf
    from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Chorus, Reverb, Compressor, Limiter

    bpm = int(score_item.get("bpm", 96))
    root, intervals = SCALES_SEMITONES.get(score_item.get("scale", "d_harmonic_minor"), (50, [0, 2, 3, 5, 7, 8, 11]))
    progs = score_item.get("gm_programs", [42, 48, 38])
    rng = np.random.default_rng(_det_hash(score_item["id"]) % (2**31 - 1))

    beats_total = max(8, int(math.ceil((duration_sec * bpm) / 60.0)) + 2)
    mf = MIDIFile(3)
    for tr, prog in enumerate(progs[:3]):
        mf.addTempo(tr, 0, bpm)
        mf.addProgramChange(tr, tr, 0, int(prog))

    # Chord degree progression: i -> VI -> iv -> V (cinematic tension & resolution)
    prog_degrees = [0, 5, 3, 4]
    for bar in range(0, beats_total, 4):
        deg = prog_degrees[(bar // 4) % len(prog_degrees)]
        bass_note = root - 12 + intervals[deg % len(intervals)]
        # Track 2: Deep bass / pulse
        if score_item.get("arrangement") == "pulsing_heartbeat_bed":
            for sub in range(4):
                mf.addNote(2, 2, bass_note, bar + sub, 0.85, 68)
        else:
            mf.addNote(2, 2, bass_note, bar, 3.8, 64)

        # Track 1: Sustained harmonic strings / warm pad (carved away from vocal 1-3kHz via velocity)
        for tri in (0, 2, 4):
            n_pad = root + intervals[(deg + tri) % len(intervals)]
            mf.addNote(1, 1, n_pad, bar, 3.9, 54)

        # Track 0: Signature motif / ostinato
        motif_steps = [0, 2, 4, 2, 5, 4, 2, 1]
        for s_i in range(8):
            t_beat = bar + s_i * 0.5
            if t_beat >= beats_total:
                break
            if rng.random() < 0.18 and s_i % 2 == 1:
                continue
            step_deg = (deg + motif_steps[(s_i + int(rng.integers(0, 2))) % len(motif_steps)]) % len(intervals)
            vel = 62 + int(14 * (t_beat / max(1, beats_total))) if score_item.get("arrangement") == "cinematic_arc_build" else 64
            mf.addNote(0, 0, root + 12 + intervals[step_deg], t_beat, 0.44, min(88, vel))

    os.makedirs("/var/tmp", exist_ok=True)
    tmp_mid = f"/var/tmp/_score_{_det_hash(score_item['id']) % 99999}.mid"
    tmp_raw = f"/var/tmp/_score_{_det_hash(score_item['id']) % 99999}.raw.wav"
    with open(tmp_mid, "wb") as fh:
        mf.writeFile(fh)

    subprocess.run(
        ["fluidsynth", "-ni", "-g", "0.95", "-r", str(SR), "-F", tmp_raw, SOUNDFONT_GM, tmp_mid],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    audio, _ = sf.read(tmp_raw, dtype="float32")
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])
    target_n = int(SR * duration_sec)
    audio = audio[:target_n] if len(audio) >= target_n else np.pad(audio, ((0, target_n - len(audio)), (0, 0)))

    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=36.0),
        LowpassFilter(cutoff_frequency_hz=9500.0),  # Leaves crisp air sheen free for voice-05
        Chorus(rate_hz=0.45, depth=0.12, mix=0.14),
        Reverb(room_size=float(score_item.get("reverb_room", 0.65)), damping=0.48, wet_level=float(score_item.get("reverb_wet", 0.24)), dry_level=0.82),
        Compressor(threshold_db=-18.0, ratio=2.4, attack_ms=22.0, release_ms=190.0),
        Limiter(threshold_db=-2.0),
    ])
    polished = board(audio.T, SR).T
    fade = min(int(1.2 * SR), len(polished) // 4)
    if fade > 0:
        polished[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)[:, None]

    os.makedirs(os.path.dirname(os.path.abspath(out_wav)), exist_ok=True)
    sf.write(out_wav, polished, SR, subtype="PCM_24")
    Path(tmp_mid).unlink(missing_ok=True)
    Path(tmp_raw).unlink(missing_ok=True)
    return out_wav
