#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scenario_director.py — Smart Platform-First Top-K Mood & Workspace Arsenal Director
===================================================================================
For ANY scenario (short topic prompt or full Persian/English script), executes a
4-stage intelligent creative direction & asset funnel across the ENTIRE workspace:

  Stage 1 (Platform-First Routing):
    Detects or locks onto target platform (`yt_16x9`, `yt_shorts`, `ig_reels`,
    `ig_story`, `ig_carousel`, `tiktok`), loading that platform's native resolution,
    safe zones, cut cadence, specialist skills, and platform-specific pools FIRST.

  Stage 2 (Scenario & Beat Semantic Mood Profiling):
    Scores the scenario across 12 semantic mood axes (crisis_economy, investigative_noir,
    geopolitics_map, historical_archive, fintech_data, science_system, street_human,
    viral_shock, tech_cyber, educational_board, editorial_press, poetic_heritage),
    parses dramatic beats, and vocalizes Persian TTS traps (`اَبَر تَوَرُّم`, `می‌دَوَن`).

  Stage 3 (100–570 Pool Audit -> Top-K [K=10] Shortlist -> Coherent Weighted-Random Pick):
    Audits all 12 workspace asset domains (Visual Style, Hook Typography, Body/Data
    Typography, Thumbnail Typography, Font+Caption Stack, Motion & Camera Choreography,
    Imagery/Real-Photo/Data-Viz, 265 GLSL Transitions, 570 VFX/LYGIA/Frei0r Shaders,
    voice-05 + LADSPA/Pedalboard Vocal DSP, 108 Stereo SFX, 108 FluidSynth GM Music Scores),
    extracts the Top-K (default 10) best-matching candidates per element, and samples
    coherently with anti-repeat memory so every clip gets a fresh, tailor-made mood!

  Stage 4 (Scene-by-Scene Blueprint + Optional Real Audio/Visual Kit Materialization):
    Outputs `director_plan.json` + `DIRECTOR_SHEET.md`, and with `--materialize-kit DIR`
    renders the actual 48kHz stereo music WAV, 6 stereo SFX WAVs, and a HarfBuzz+ACES
    visual moodboard specimen JPG!

CLI Examples:
  python3 scenario_director.py --scenario "پشت‌پرده مالیات پنهان تورم روی سفره مردم" --platform yt_16x9
  python3 scenario_director.py --script /home/user/Script_ChiMishe_Hyperinflation_Signals_Ep2_5min.md --platform yt_16x9 --materialize-kit /var/tmp/ep_kit
  python3 scenario_director.py --scenario "چرا قراردادهای اجاره یک‌دفعه ۶ ماهه شد؟" --platform ig_reels --top-k 10
  python3 scenario_director.py --self-test
"""

import os
import re
import sys
import json
import math
import time
import random
import argparse
import subprocess
from pathlib import Path
import numpy as np
import cv2

STUDIO = "/home/user/animation-studio"
PYLIBS = os.path.join(STUDIO, "runtime", "pylibs")
for _p in (PYLIBS, STUDIO, os.path.join(STUDIO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import arsenal_pools as apools
import style_vfx_arsenal as sva

HISTORY_PATH = os.path.join(STUDIO, "skills", "mega-style-vfx-arsenal", "director_history.json")

# ==============================================================================
# STAGE 1 & 2: PLATFORM AUTO-DETECTOR + PERSIAN/ENGLISH SCENARIO MOOD ANALYZER
# ==============================================================================
LEXICON_FA_EN = {
    "crisis_economy": [
        "تورم", "ابرتورم", "گرانی", "بودجه", "حقوق", "دستمزد", "دلار", "ریال", "ارز", "سکه", "طلا",
        "نقدینگی", "بانک مرکزی", "قدرت خرید", "سفره", "جیب", "فقر", "رکود", "مالیات", "کسری",
        "قیمت", "چاپ پول", "بدهی", "یارانه", "معیشت", "سبد", "هزینه", "inflation", "budget", "crisis",
    ],
    "investigative_noir": [
        "پشت پرده", "پشت‌پرده", "راز", "پرونده", "محرمانه", "افشا", "مافیا", "سند", "مدرک",
        "تاریک", "پنهان", "تله", "خطر", "هشدار", "فاجعه", "سقوط", "فروپاشی", "دروغ", "واکاوی",
        "تحقیق", "کالبدشکافی", "ردپای", "شبکه", "secret", "dossier", "investigation", "expose",
    ],
    "geopolitics_map": [
        "نقشه", "کشور", "جهان", "مرز", "ایران", "تهران", "استان", "منطقه", "خاورمیانه", "تحریم",
        "نفت", "گاز", "صادرات", "واردات", "تنگه", "هرمز", "چین", "روسیه", "اروپا", "آمریکا",
        "ژئوپلیتیک", "مسیر", "کریدور", "تجارت جهانی", "map", "sanctions", "oil", "geopolitics",
    ],
    "historical_archive": [
        "تاریخ", "تاریخی", "سال ۱۹۲۳", "۱۹۲۳", "۱۹۴۶", "۱۹۹۰", "آلمان", "وایمار", "مجارستان",
        "زیمبابوه", "ونزوئلا", "یوگسلاوی", "قدیم", "دهه", "قرن", "آرشیو", "جنگ جهانی", "گذشته",
        "عبرت", "تجربه تاریخی", "history", "1923", "1946", "archive", "weimar",
    ],
    "fintech_data": [
        "درصد", "٪", "%", "آمار", "نمودار", "شاخص", "کندل", "بورس", "سهام", "ترازنامه", "نرخ",
        "میلیارد", "همت", "تریلیون", "رشد", "شکاف", "ضریب", "داده", "جدول", "مقایسه عددی",
        "data", "chart", "index", "market", "gdp", "percent",
    ],
    "science_system": [
        "مکانیزم", "سیستم", "فرمول", "چطور", "چگونه", "چرخه", "زنجیره", "مهندسی", "ساختار",
        "قانون", "سرعت گردش", "علت", "معلول", "الگو", "فیزیک", "ریاضی", "مدل", "system", "mechanism",
    ],
    "street_human": [
        "خیابان", "خیابانی", "بازار", "مغازه", "فروشنده", "خریدار", "مردم", "شهروند", "اجاره",
        "خانه", "مسکن", "سوپرمارکت", "نان", "گوشت", "لبنیات", "دارو", "تاکسی", "روزمره", "زندگی",
        "قرارداد", "فروش نداریم", "اتیکت", "فاکتور", "street", "people", "shop", "rent",
    ],
    "viral_shock": [
        "شوک", "فوری", "عجیب", "باورکردنی", "باورت", "۳ ثانیه", "انفجار", "رکورد", "ناگهان",
        "یک‌شبه", "یکدفعه", "وحشتناک", "بمب", "سیب‌زمینی داغ", "چی می‌شه", "چی میشه", "؟!", "!؟",
        "shock", "viral", "breaking",
    ],
    "tech_cyber": [
        "هوش مصنوعی", "سایبری", "دیجیتال", "کد", "الگوریتم", "ربات", "رمزارز", "بیت‌کوین",
        "تکنولوژی", "فناوری", "اینترنت", "پلتفرم", "چیپ", "آینده", "سخت‌افزار", "ai", "cyber", "tech",
    ],
    "educational_board": [
        "آموزش", "یاد بگیریم", "ساده", "گام‌به‌گام", "مرحله", "چک‌لیست", "نکته", "درس", "کلاس",
        "تعریف", "مثال", "راهنما", "چند نشانه", "۵ سیگنال", "سیگنال", "امتیاز", "guide", "lesson",
    ],
    "editorial_press": [
        "گزارش", "روزنامه", "تحلیل", "مقاله", "اکونومیست", "فایننشال", "رسمی", "بررسی",
        "نشریه", "تیتر", "مطبوعات", "سرمقاله", "report", "editorial", "analysis",
    ],
    "poetic_heritage": [
        "فرهنگ", "ادبیات", "شعر", "تمدن", "میراث", "هنر", "فلسفه", "انسان", "امید", "روایت",
        "داستان", "روح", "ایران باستان", "خوشنویسی", "heritage", "story", "culture",
    ],
}


def sanitize_persian_tts(text: str) -> str:
    """Enforces standing Persian TTS phonetic rules for Arena `voice-05`."""
    out = text
    out = re.sub(r"ابرتورمِ", "اَبَر تَوَرُّمِ", out)
    out = re.sub(r"ابرتورمه", "اَبَر تَوَرُّمه", out)
    out = re.sub(r"ابرتورم", "اَبَر تَوَرُّم", out)
    out = re.sub(r"اَبَرتورم", "اَبَر تَوَرُّم", out)
    out = re.sub(r"می‌دون\b", "می‌دَوَن", out)
    out = re.sub(r"میدون\b", "می‌دَوَن", out)
    return out


def detect_platform_from_text(text: str, explicit_platform: str | None = None) -> str:
    if explicit_platform and explicit_platform in apools.PLATFORM_SPECS:
        return explicit_platform
    t = text.lower()
    if any(k in t for k in ("ریلز", "اینستاگرام ریلز", "reels", "reel", "پست اینستا")):
        return "ig_reels"
    if any(k in t for k in ("شورتس", "یوتیوب شورت", "shorts", "short")):
        return "yt_shorts"
    if any(k in t for k in ("استوری", "story")):
        return "ig_story"
    if any(k in t for k in ("کاروسل", "اسلایدی", "carousel")):
        return "ig_carousel"
    if any(k in t for k in ("تیک‌تاک", "تیک تاک", "tiktok")):
        return "tiktok"
    return "yt_16x9"


def analyze_scenario(text: str, platform: str) -> dict:
    """Extracts 12-axis mood vector, visual triggers, and beat-by-beat breakdown."""
    raw_scores = {ax: 1.0 for ax in apools.MOOD_AXES}
    tl = text.lower()

    for ax, words in LEXICON_FA_EN.items():
        for w in words:
            cnt = len(re.findall(re.escape(w.lower()), tl))
            if cnt > 0:
                raw_scores[ax] += min(cnt, 6) * 3.2

    # Structural & regex boosters
    fa_en_nums = re.findall(r"[0-9۰-۹]+(?:\.[0-9۰-۹]+)?", text)
    has_pct = bool(re.search(r"[٪%]", text))
    has_years = bool(re.search(r"\b(19\d\d|20\d\d|۱۳\d\d|۱۴۰\d)\b", text))
    has_versus = bool(re.search(r"(در برابر|مقابل|در حالی که|اما|vs|در مقایسه)", tl))
    has_question = ("؟" in text or "?" in text)

    if len(fa_en_nums) >= 2 or has_pct:
        raw_scores["fintech_data"] += 7.5
    if has_years:
        raw_scores["historical_archive"] += 6.5
    if has_versus:
        raw_scores["crisis_economy"] += 4.0
        raw_scores["viral_shock"] += 3.5
    if has_question:
        raw_scores["viral_shock"] += 3.0
    if platform in ("ig_reels", "yt_shorts", "tiktok"):
        raw_scores["viral_shock"] += 4.5
    elif platform == "yt_16x9":
        raw_scores["investigative_noir"] += 2.5

    max_v = max(raw_scores.values()) or 1.0
    mood_vector = {k: round(v / max_v, 4) for k, v in raw_scores.items()}
    ranked_moods = sorted(mood_vector.items(), key=lambda kv: kv[1], reverse=True)

    # Parse beats from markdown sections/paragraphs/lines, or synthesize 5 dramatic beats for a short prompt
    clean_lines = [
        ln.strip() for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith(("```", "---", "|---"))
    ]
    paragraphs = []
    buf = []
    for ln in clean_lines:
        if ln.startswith("#"):
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
            paragraphs.append(ln.lstrip("#").strip())
        else:
            buf.append(ln)
    if buf:
        paragraphs.append(" ".join(buf))

    if len(paragraphs) <= 2:
        # Short topic prompt -> expand into a 5-beat platform-native dramatic structure
        topic_short = paragraphs[0][:110] if paragraphs else text[:110]
        raw_beats = [
            ("hook", f"هوک شوک و سؤال اصلی: {topic_short}"),
            ("context", f"چرایی و مکانیزم پنهان ماجرا در زندگی واقعی مردم"),
            ("data_evidence", f"مقایسه آماری، نمودار شکاف اعداد و شواهد مستند"),
            ("geo_or_history", f"بررسی نقشه اثرگذاری یا نمونه‌های تاریخی، نه پیش‌بینی"),
            ("verdict_cta", f"جمع‌بندی نهایی، چک‌لیست تشخیص و سؤال تعاملی از مخاطب"),
        ]
    else:
        raw_beats = []
        for idx, p in enumerate(paragraphs[:12]):
            if idx == 0:
                role = "hook"
            elif idx == len(paragraphs[:12]) - 1:
                role = "verdict_cta"
            elif re.search(r"(۱۹۲۳|۱۹۴۶|تاریخ|آلمان|مجارستان|قدیم)", p):
                role = "historical_case"
            elif re.search(r"(نقشه|کشور|ایران|تهران|استان|جهان)", p):
                role = "geo_map"
            elif re.search(r"([0-9۰-۹]+\s*[٪%]|نمودار|بودجه|حقوق|تورم)", p):
                role = "data_evidence"
            else:
                role = "context"
            raw_beats.append((role, p[:240]))

    beats = []
    for b_idx, (role, snippet) in enumerate(raw_beats, start=1):
        beats.append({
            "beat_index": b_idx,
            "role": role,
            "excerpt": snippet,
            "tts_vocalized_fa": sanitize_persian_tts(snippet),
            "triggers": {
                "numbers": bool(re.search(r"[0-9۰-۹]", snippet)),
                "percent": bool(re.search(r"[٪%]", snippet)),
                "geo": bool(re.search(r"(نقشه|کشور|ایران|تهران|استان|جهان|مرز)", snippet)),
                "history": bool(re.search(r"(۱۹\d\d|19\d\d|تاریخ|آرشیو|آلمان|مجارستان)", snippet)),
                "street": bool(re.search(r"(خیابان|بازار|مغازه|سفره|مردم|اجاره|فروش)", snippet)),
            },
        })

    return {
        "char_length": len(text),
        "word_count": len(text.split()),
        "numbers_detected": fa_en_nums[:12],
        "has_percentage": has_pct,
        "has_historical_years": has_years,
        "has_versus_contrast": has_versus,
        "dominant_moods": [k for k, _ in ranked_moods[:4]],
        "mood_vector": mood_vector,
        "beats": beats,
    }


# ==============================================================================
# STAGE 3: POOL SCORER -> TOP-K (K=10) FILTER -> COHERENT WEIGHTED-RANDOM PICKER
# ==============================================================================
def load_history() -> dict:
    if os.path.isfile(HISTORY_PATH):
        try:
            return json.load(open(HISTORY_PATH, encoding="utf-8"))
        except Exception:
            pass
    return {"recent_picks": {}}


def save_history(hist: dict):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as fh:
        json.dump(hist, fh, ensure_ascii=False, indent=2)


def score_and_select_top_k(
    domain_name: str,
    pool: list[dict],
    platform: str,
    mood_vector: dict[str, float],
    rng: random.Random,
    top_k: int = 10,
    temperature: float = 0.65,
    coherence_ctx: dict | None = None,
    recent_ids: list[str] | None = None,
    pick_count: int = 1,
    custom_bonus_fn=None,
    dedupe_key: str | None = None,
) -> dict:
    """
    1. Audits the entire `pool` (100–570 items).
    2. Filters/boosts for target `platform` FIRST.
    3. Computes 0–100 fitness score from Scenario Mood Vector + Aesthetic Coherence + Novelty.
    4. Extracts `Top-K` (default 10) distinct best candidates (deduplicating by `dedupe_key` if set).
    5. Performs softmax-weighted random selection inside `Top-K` without replacement!
    """
    coherence_ctx = coherence_ctx or {}
    recent_set = set(recent_ids or [])

    # Step 1: Platform-First Gate (keep platform-native items; fall back to all only if empty)
    plat_filtered = [
        item for item in pool
        if ("platforms" not in item) or (platform in item["platforms"]) or (item.get("platform") == platform)
    ]
    active_pool = plat_filtered if len(plat_filtered) >= top_k else pool

    scored = []
    for item in active_pool:
        # Base mood resonance (0..58 pts)
        item_moods = item.get("moods", [])
        if item_moods:
            weights = sorted([mood_vector.get(m, 0.15) for m in item_moods], reverse=True)
            top_w = weights[0]
            sec_w = weights[1] if len(weights) > 1 else top_w * 0.6
            mood_pts = (top_w * 38.0) + (sec_w * 20.0)
        else:
            mood_pts = 20.0

        # Platform primacy bonus (0..12 pts)
        plats = item.get("platforms", [item.get("platform", platform)])
        plat_pts = 12.0 if (plats and plats[0] == platform) else 8.5

        # Curated tier quality bonus (0..14 pts)
        tier_pts = float(item.get("tier_bonus", 8.0))

        # Cross-element coherence lock (0..14 pts)
        coh_pts = 0.0
        target_tone = coherence_ctx.get("tone")
        if target_tone and "tone" in item:
            coh_pts += 9.0 if item["tone"] == target_tone else -6.0
        preferred_gl = coherence_ctx.get("paired_gl", [])
        if preferred_gl and item.get("shader_name") in preferred_gl:
            coh_pts += 11.0
        preferred_vfx = coherence_ctx.get("paired_vfx", [])
        if preferred_vfx and item.get("vfx_key") in preferred_vfx:
            coh_pts += 11.0
        preferred_font = coherence_ctx.get("fa_font")
        if preferred_font:
            item_fa = item.get("fonts", {}).get("fa") or item.get("fa_headline", {}).get("name")
            if item_fa == preferred_font:
                coh_pts += 7.5

        # Optional domain-specific hook/body/thumb bonus
        extra_pts = float(custom_bonus_fn(item)) if custom_bonus_fn else 0.0

        # Anti-repetition penalty so consecutive videos stay fresh (checks both exact ID & family/composition)!
        grp_val = f"grp::{item.get(dedupe_key)}" if (dedupe_key and item.get(dedupe_key)) else None
        novelty_adj = -18.0 if (item["id"] in recent_set or (grp_val and grp_val in recent_set)) else 0.0

        # Tiny deterministic tie-breaker jitter (0..1.5 pts) so ties spread cleanly
        jitter = rng.uniform(0.0, 1.4)

        total = max(1.0, min(99.9, mood_pts + plat_pts + tier_pts + coh_pts + extra_pts + novelty_adj + jitter))
        scored.append((round(total, 2), item))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Extract Top-K with optional family/archetype diversity so all 10 candidates are distinct!
    shortlist = []
    if dedupe_key:
        seen_groups = set()
        overflow = []
        for sc, it in scored:
            grp = it.get(dedupe_key)
            if grp and grp not in seen_groups:
                seen_groups.add(grp)
                shortlist.append((sc, it))
                if len(shortlist) >= top_k:
                    break
            else:
                overflow.append((sc, it))
        if len(shortlist) < top_k:
            shortlist.extend(overflow[: top_k - len(shortlist)])
    else:
        shortlist = scored[:max(1, min(top_k, len(scored)))]

    # Softmax weighted random sampling WITHOUT replacement from Top-K
    remaining = list(shortlist)
    winners = []
    for _ in range(min(pick_count, len(remaining))):
        max_s = max(s for s, _ in remaining)
        temp = max(0.08, temperature) * 6.0
        exps = [math.exp((s - max_s) / temp) for s, _ in remaining]
        sum_e = sum(exps) or 1.0
        probs = [e / sum_e for e in exps]
        r = rng.random()
        cum = 0.0
        chosen_idx = 0
        for idx_p, pr in enumerate(probs):
            cum += pr
            if r <= cum:
                chosen_idx = idx_p
                break
        win_score, win_item = remaining.pop(chosen_idx)
        winners.append({"score": win_score, "item": win_item})

    return {
        "domain": domain_name,
        "total_pool_scanned": len(pool),
        "platform_matched_pool": len(active_pool),
        "top_k_size": len(shortlist),
        "top_k_candidates": [
            {
                "rank": idx_r + 1,
                "id": it["id"],
                "title": it.get("title", it["id"]),
                "score": sc,
                "desc_fa": it.get("desc_fa", ""),
            }
            for idx_r, (sc, it) in enumerate(shortlist)
        ],
        "selected": winners[0]["item"],
        "selected_score": winners[0]["score"],
        "selected_multi": [w["item"] for w in winners],
    }


def _trim_words(s: str, max_len: int) -> str:
    s = str(s).strip()
    if len(s) <= max_len:
        return s
    cut = s[: max_len - 1].rsplit(" ", 1)[0]
    return (cut if len(cut) >= max_len // 2 else s[: max_len - 1]) + "…"


# ==============================================================================
# STAGE 4: MOODBOARD SPECIMEN CARD RENDERER (HarfBuzz `rsvg-convert` + ACES VFX)
# ==============================================================================
def render_moodboard_specimen_jpg(plan: dict, out_jpg: str) -> str:
    """Renders a crisp visual Moodboard & Arsenal Direction Specimen Card via rsvg-convert + OpenCV VFX."""
    style = plan["selections"]["visual_style_pack"]["selected"]
    pal = style["palette"]
    hook_t = plan["selections"]["hook_typography"]["selected"]
    font_s = plan["selections"]["font_and_caption_stack"]["selected"]
    music_s = plan["selections"]["music_score"]["selected"]
    vfx_s = plan["selections"]["vfx_and_shaders"]["selected"]
    gl_s = plan["selections"]["gl_transitions"]["selected"]

    w, h = 1920, 1080
    bg = pal["bg"]
    ink = pal["ink"]
    acc = pal["accent"]
    sec = pal["secondary"]
    fa_font = font_s["fa_headline"]["name"]
    mono_font = font_s["mono_font"]["name"]

    dom_moods = " · ".join(plan["scenario_analysis"]["dominant_moods"][:3])
    plat_lbl = plan["platform_spec"]["label_fa"]
    beat1 = _trim_words(plan["beat_choreography"][0]["excerpt"], 54)
    fa_file = font_s["fa_headline"]["file"]
    hero_sz = apools.typo_eng.fit_hero_size(beat1, fa_file, 1520, 68, min_size=42)

    def _esc(s: str) -> str:
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    # Note: In librsvg (`rsvg-convert`), under `direction="rtl"`, `text-anchor="start"` anchors
    # the RIGHT edge of the Persian string so text flows cleanly leftwards inside each card!
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <radialGradient id="glowA" cx="78%" cy="24%" r="62%">
      <stop offset="0%" stop-color="{acc}" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="{bg}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowB" cx="18%" cy="82%" r="55%">
      <stop offset="0%" stop-color="{sec}" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="{bg}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="{bg}"/>
  <rect width="{w}" height="{h}" fill="url(#glowA)"/>
  <rect width="{w}" height="{h}" fill="url(#glowB)"/>

  <!-- Header Badge -->
  <rect x="96" y="68" width="1728" height="86" rx="18" fill="#0B1120" fill-opacity="0.88" stroke="{acc}" stroke-width="2.5"/>
  <text x="1786" y="122" text-anchor="start" direction="rtl" font-family="Vazirmatn" font-weight="800" font-size="28" fill="#F8FAFC">کارگردان هوشمند سناریو · {_esc(plat_lbl)}</text>
  <text x="132" y="121" text-anchor="start" direction="ltr" font-family="{_esc(mono_font)}, monospace" font-weight="700" font-size="23" fill="{acc}">TOP-{plan['director_config']['top_k']} FUNNEL · VOICE-05 · {plan['director_config']['total_workspace_candidates_scanned']} ASSETS</text>

  <!-- Hero Sample Headline -->
  <rect x="96" y="186" width="1728" height="336" rx="28" fill="#090D16" fill-opacity="0.72" stroke="{sec}" stroke-opacity="0.65" stroke-width="2"/>
  <text x="1772" y="252" text-anchor="start" direction="rtl" font-family="Vazirmatn" font-weight="700" font-size="25" fill="{acc}">نمونه تیتر هوک با فونت «{_esc(fa_font)}» و استایل «{_esc(style['raw_id'])}»:</text>
  <text x="960" y="382" text-anchor="middle" direction="rtl" font-family="{_esc(fa_font)}, Vazirmatn" font-weight="900" font-size="{hero_sz}" fill="{ink}">{_esc(beat1)}</text>
  <text x="960" y="476" text-anchor="middle" direction="ltr" font-family="{_esc(mono_font)}, monospace" font-weight="700" font-size="22" fill="{sec}">MOOD: {_esc(dom_moods.upper())}   |   TYPO: {_esc(_trim_words(hook_t['id'], 54))}</text>

  <!-- 4 Summary Arsenal Cards -->
  <g font-family="Vazirmatn">
    <rect x="96" y="556" width="844" height="202" rx="22" fill="#0B1120" fill-opacity="0.90" stroke="#334155" stroke-width="2"/>
    <text x="904" y="610" text-anchor="start" direction="rtl" font-weight="800" font-size="25" fill="{acc}">۱. هویت بصری و انیمیشن (از ۱۵۲ سبک + ۳۱۵ موشن)</text>
    <text x="132" y="662" text-anchor="start" direction="ltr" font-family="{_esc(mono_font)}, monospace" font-weight="700" font-size="21" fill="#F8FAFC">{_esc(_trim_words(style['title'], 48))}</text>
    <text x="904" y="716" text-anchor="start" direction="rtl" font-weight="500" font-size="20" fill="#CBD5E1">{_esc(_trim_words(style['desc_fa'], 62))}</text>

    <rect x="980" y="556" width="844" height="202" rx="22" fill="#0B1120" fill-opacity="0.90" stroke="#334155" stroke-width="2"/>
    <text x="1788" y="610" text-anchor="start" direction="rtl" font-weight="800" font-size="25" fill="{sec}">۲. جلوه ویژه و ترنزیشن GPU (از ۵۷۰ افکت + ۲۶۵ شیدر)</text>
    <text x="1016" y="662" text-anchor="start" direction="ltr" font-family="{_esc(mono_font)}, monospace" font-weight="700" font-size="21" fill="#F8FAFC">{_esc(_trim_words(vfx_s['id'] + ' + ' + gl_s['shader_name'], 50))}</text>
    <text x="1788" y="716" text-anchor="start" direction="rtl" font-weight="500" font-size="20" fill="#CBD5E1">{_esc(_trim_words(vfx_s['desc_fa'], 62))}</text>

    <rect x="96" y="786" width="844" height="202" rx="22" fill="#0B1120" fill-opacity="0.90" stroke="#334155" stroke-width="2"/>
    <text x="904" y="840" text-anchor="start" direction="rtl" font-weight="800" font-size="25" fill="#34D399">۳. موسیقی متن و پک ۶تایی SFX (از ۱۰۸ پارتیتور + ۱۰۸ فولی)</text>
    <text x="132" y="892" text-anchor="start" direction="ltr" font-family="{_esc(mono_font)}, monospace" font-weight="700" font-size="21" fill="#F8FAFC">{_esc(music_s['composition'])} ({music_s['bpm']} BPM · {_esc(music_s['scale'])})</text>
    <text x="904" y="946" text-anchor="start" direction="rtl" font-weight="500" font-size="20" fill="#CBD5E1">{_esc(_trim_words(music_s['desc_fa'], 62))}</text>

    <rect x="980" y="786" width="844" height="202" rx="22" fill="#0B1120" fill-opacity="0.90" stroke="#334155" stroke-width="2"/>
    <text x="1788" y="840" text-anchor="start" direction="rtl" font-weight="800" font-size="25" fill="#FBBF24">۴. صداپیشگی، تصویر واقعی و داده (voice-05 + عکاسی/نمودار)</text>
    <text x="1016" y="892" text-anchor="start" direction="ltr" font-family="{_esc(mono_font)}, monospace" font-weight="700" font-size="21" fill="#F8FAFC">{_esc(_trim_words(plan['selections']['voice_and_dsp']['selected']['title'], 50))}</text>
    <text x="1788" y="946" text-anchor="start" direction="rtl" font-weight="500" font-size="20" fill="#CBD5E1">{_esc(_trim_words(plan['selections']['imagery_and_viz']['selected']['desc_fa'], 62))}</text>
  </g>
</svg>'''

    tmp_svg = "/var/tmp/_director_specimen.svg"
    tmp_png = "/var/tmp/_director_specimen.png"
    with open(tmp_svg, "w", encoding="utf-8") as fh:
        fh.write(svg)
    subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), tmp_svg, "-o", tmp_png], check=True)
    bgr = cv2.imread(tmp_png, cv2.IMREAD_COLOR)
    bgr = sva.apply_procedural_vfx(bgr, "aces_filmic", 0.5)
    os.makedirs(os.path.dirname(os.path.abspath(out_jpg)), exist_ok=True)
    cv2.imwrite(out_jpg, bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    Path(tmp_svg).unlink(missing_ok=True)
    Path(tmp_png).unlink(missing_ok=True)
    return out_jpg


# ==============================================================================
# MASTER ORCHESTRATION PIPELINE (`direct_scenario`)
# ==============================================================================
def direct_scenario(
    scenario_text: str,
    platform: str | None = None,
    top_k: int = 10,
    temperature: float = 0.65,
    seed: int | None = None,
    use_anti_repeat: bool = True,
    materialize_dir: str | None = None,
) -> dict:
    t0 = time.time()
    resolved_platform = detect_platform_from_text(scenario_text, platform)
    plat_spec = apools.PLATFORM_SPECS[resolved_platform]
    thumb_platform = plat_spec["thumb_platform"]

    rng = random.Random(seed if seed is not None else int(time.time() * 1000) ^ os.getpid())
    hist = load_history() if use_anti_repeat else {"recent_picks": {}}
    recent_map = hist.get("recent_picks", {})

    # Stage 2: Analyze scenario mood & beats
    analysis = analyze_scenario(scenario_text, resolved_platform)
    mvec = analysis["mood_vector"]

    # Load all 12 real workspace pools (Platform-First for typography!)
    pool_grammar = apools.build_editorial_grammar_pool()
    pool_styles = apools.build_visual_styles_pool()
    pool_plat_typo = apools.load_typography_pool(resolved_platform)      # 100 platform-native presets
    pool_thumb_typo = apools.load_typography_pool(thumb_platform)        # 100 thumbnail/cover presets
    pool_fonts = apools.build_font_and_caption_pool()                    # 105 font+caption stacks
    pool_motion = apools.build_motion_choreography_pool()                # 315 motion & camera templates
    pool_imagery = apools.build_imagery_and_viz_pool()                   # 108 photo/map/chart/thumb recipes
    pool_gl = apools.build_gl_transitions_pool()                         # 265 GLSL transitions
    pool_vfx = apools.build_vfx_and_shaders_pool()                       # 570 VFX / LYGIA / Frei0r
    pool_voice = apools.build_voice_dsp_pool()                           # 108 voice-05 + LADSPA/Pedalboard
    pool_sfx = apools.build_sfx_arsenal_pool()                           # 108 stereo 48kHz SFX synths
    pool_music = apools.build_music_score_pool()                         # 108 FluidR3_GM + Pedalboard scores

    selections = {}

    # 1. Editorial & Pacing Grammar (100 -> Top 10 -> 1)
    selections["editorial_grammar"] = score_and_select_top_k(
        "editorial_grammar", pool_grammar, resolved_platform, mvec, rng, top_k, temperature,
        recent_ids=recent_map.get("editorial_grammar", []),
        dedupe_key="structure",
    )

    # 2. Master Visual & Creator Style (152 -> Top 10 -> Primary + Secondary B-Style)
    selections["visual_style_pack"] = score_and_select_top_k(
        "visual_style_pack", pool_styles, resolved_platform, mvec, rng, top_k, temperature,
        recent_ids=recent_map.get("visual_style_pack", []), pick_count=2,
    )
    win_style = selections["visual_style_pack"]["selected"]
    coherence_ctx = {
        "tone": win_style.get("tone", "dark"),
        "paired_gl": win_style.get("paired_gl", []),
        "paired_vfx": win_style.get("paired_vfx", []),
        "fa_font": win_style.get("fa_font"),
    }

    # 3. Platform Hook Typography (100 platform presets -> Top 10 distinct layouts -> 1)
    selections["hook_typography"] = score_and_select_top_k(
        "hook_typography", pool_plat_typo, resolved_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("hook_typography", []),
        dedupe_key="layout",
        custom_bonus_fn=lambda it: 10.0 if it.get("layout") in ("stacked_center", "giant_bleed_word", "strip_highlight", "versus_duel_card", "karaoke_word_box", "badge_burst") else 0.0,
    )

    # 4. Platform Body, Subtitle & Big-Stat Typography (100 platform presets -> Top 10 distinct layouts -> 3)
    selections["body_and_data_typography"] = score_and_select_top_k(
        "body_and_data_typography", pool_plat_typo, resolved_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("body_and_data_typography", []) + [selections["hook_typography"]["selected"]["id"]],
        pick_count=3,
        dedupe_key="layout",
        custom_bonus_fn=lambda it: 11.0 if it.get("layout") in ("big_number_hero", "hud_telemetry_box", "photo_witness_split", "kinetic_list", "lower_third", "caption_bar", "scoreboard_flap") else 0.0,
    )

    # 5. Thumbnail / Cover Typography (100 cover presets -> Top 10 distinct layouts -> 1)
    selections["thumbnail_typography"] = score_and_select_top_k(
        "thumbnail_typography", pool_thumb_typo, thumb_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("thumbnail_typography", []),
        dedupe_key="layout",
        custom_bonus_fn=lambda it: 11.0 if it.get("layout") in ("versus_duel_card", "big_number_hero", "stacked_center", "strip_highlight", "photo_witness_split") else 0.0,
    )

    # 6. Verified Font Trio + LangChain Embedded Caption Identity (120 -> Top 10 -> 1)
    selections["font_and_caption_stack"] = score_and_select_top_k(
        "font_and_caption_stack", pool_fonts, resolved_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("font_and_caption_stack", []),
        dedupe_key="caption_dna",
    )

    # 7. Motion & Camera Choreography (315 -> Top 10 -> 4 varied curves for beats)
    selections["motion_choreography"] = score_and_select_top_k(
        "motion_choreography", pool_motion, resolved_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("motion_choreography", []),
        pick_count=4,
        dedupe_key="motion_curve",
    )

    # 8. Real Photography, AI B-Roll, GeoJSON Maps, 4K Charts & Thumbnail Strategy (108 -> Top 10 distinct archetypes -> 5)
    def _img_bonus(it: dict) -> float:
        b = 8.0 if it.get("uses_real_photography") else 0.0
        if it["archetype"].startswith("thumb_"):
            b -= 8.0  # Keep scene pool focused on in-video scenes; thumbnail has dedicated spec
        if analysis["has_percentage"] and ("candlestick" in it["archetype"] or "trend" in it["archetype"] or "treemap" in it["archetype"]):
            b += 9.0
        if "geopolitics_map" in analysis["dominant_moods"][:2] and "geojson" in it["archetype"]:
            b += 10.0
        return b

    selections["imagery_and_viz"] = score_and_select_top_k(
        "imagery_and_viz", pool_imagery, resolved_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("imagery_and_viz", []),
        pick_count=5,
        dedupe_key="archetype",
        custom_bonus_fn=_img_bonus,
    )

    # 9. GPU OpenGL Transitions (265 -> Top 10 -> 3: Primary, Shock, Chapter)
    selections["gl_transitions"] = score_and_select_top_k(
        "gl_transitions", pool_gl, resolved_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("gl_transitions", []),
        pick_count=3,
    )

    # 10. Post-VFX, LYGIA Shaders & Frei0r C++ Plugins (570 -> Top 10 -> 3: Master Grade, Beat Impact, Atmosphere)
    selections["vfx_and_shaders"] = score_and_select_top_k(
        "vfx_and_shaders", pool_vfx, resolved_platform, mvec, rng, top_k, temperature,
        coherence_ctx=coherence_ctx,
        recent_ids=recent_map.get("vfx_and_shaders", []),
        pick_count=3,
        custom_bonus_fn=lambda it: 6.5 if it.get("engine") == "studio_procedural_gpu" else 0.0,
    )

    # 11. Permanent `voice-05` + LADSPA/Pedalboard Vocal Mastering Rack (108 -> Top 10 -> 1)
    selections["voice_and_dsp"] = score_and_select_top_k(
        "voice_and_dsp", pool_voice, resolved_platform, mvec, rng, top_k, temperature,
        recent_ids=recent_map.get("voice_and_dsp", []),
        dedupe_key="archetype",
    )

    # 12A. Stereo 48kHz Foley & Cinema SFX Kit (108 -> Top 10 distinct families -> 6 distinct SFX!)
    selections["sfx_arsenal"] = score_and_select_top_k(
        "sfx_arsenal", pool_sfx, resolved_platform, mvec, rng, top_k, temperature,
        recent_ids=recent_map.get("sfx_arsenal", []),
        pick_count=6,
        dedupe_key="family",
    )

    # 12B. Symphonic / Electronic / Modal Background Music Score (108 -> Top 10 distinct compositions -> 1)
    selections["music_score"] = score_and_select_top_k(
        "music_score", pool_music, resolved_platform, mvec, rng, top_k, temperature,
        recent_ids=recent_map.get("music_score", []),
        dedupe_key="composition",
    )

    # Update Anti-Repeat History Ledger (keep last 8 IDs + family/composition groups per domain)
    if use_anti_repeat:
        dedupe_map = {
            "editorial_grammar": "structure",
            "hook_typography": "layout",
            "body_and_data_typography": "layout",
            "thumbnail_typography": "layout",
            "font_and_caption_stack": "caption_dna",
            "motion_choreography": "motion_curve",
            "imagery_and_viz": "archetype",
            "voice_and_dsp": "archetype",
            "sfx_arsenal": "family",
            "music_score": "composition",
        }
        for dom, res in selections.items():
            prev = recent_map.get(dom, [])
            win_it = res["selected"]
            new_tokens = [win_it["id"]]
            dk = dedupe_map.get(dom)
            if dk and win_it.get(dk):
                new_tokens.append(f"grp::{win_it[dk]}")
            prev = (new_tokens + [x for x in prev if x not in new_tokens])[:12]
            recent_map[dom] = prev
        hist["recent_picks"] = recent_map
        save_history(hist)

    # Build Beat-by-Beat Choreography Plan using the shortlisted multi-picks!
    motions_multi = selections["motion_choreography"]["selected_multi"]
    imgs_multi = selections["imagery_and_viz"]["selected_multi"]
    typos_body = selections["body_and_data_typography"]["selected_multi"]
    gls_multi = selections["gl_transitions"]["selected_multi"]
    vfxs_multi = selections["vfx_and_shaders"]["selected_multi"]
    sfxs_multi = selections["sfx_arsenal"]["selected_multi"]
    avg_beat_s = selections["editorial_grammar"]["selected"]["avg_beat_sec"]

    beat_choreography = []
    t_cursor = 0.0
    for idx_b, b in enumerate(analysis["beats"]):
        dur_b = round(max(2.2, min(8.5, max(avg_beat_s, len(b["excerpt"].split()) / 2.4))), 2)
        typo_pick = (
            selections["hook_typography"]["selected"]
            if b["role"] == "hook"
            else typos_body[idx_b % len(typos_body)]
        )
        # Smart trigger-aware visual pick from Top-10 imagery pool
        img_pick = imgs_multi[idx_b % len(imgs_multi)]
        if b["triggers"]["geo"]:
            for cand in pool_imagery:
                if "geojson" in cand["archetype"]:
                    img_pick = cand
                    break
        elif b["triggers"]["history"]:
            for cand in pool_imagery:
                if "archival" in cand["archetype"]:
                    img_pick = cand
                    break

        beat_choreography.append({
            "beat_index": b["beat_index"],
            "role": b["role"],
            "time_window_sec": [round(t_cursor, 2), round(t_cursor + dur_b, 2)],
            "duration_sec": dur_b,
            "excerpt": b["excerpt"],
            "voice_05_tts_text": b["tts_vocalized_fa"],
            "typography_preset_id": typo_pick["id"],
            "motion_choreography_id": motions_multi[idx_b % len(motions_multi)]["id"],
            "imagery_recipe_id": img_pick["id"],
            "gl_transition_out": gls_multi[idx_b % len(gls_multi)]["shader_name"],
            "vfx_pass": vfxs_multi[idx_b % len(vfxs_multi)]["id"],
            "sfx_cue": sfxs_multi[idx_b % len(sfxs_multi)]["id"],
        })
        t_cursor += dur_b

    total_scanned = sum(v["total_pool_scanned"] for v in selections.values())

    plan = {
        "version": "1.0.0",
        "elapsed_ms": round((time.time() - t0) * 1000, 1),
        "director_config": {
            "platform": resolved_platform,
            "thumbnail_platform": thumb_platform,
            "top_k": top_k,
            "temperature": temperature,
            "seed": seed,
            "anti_repeat_enabled": use_anti_repeat,
            "total_workspace_candidates_scanned": total_scanned,
            "permanent_voice_id": "voice-05",
            "local_tts_banned": True,
        },
        "platform_spec": plat_spec,
        "scenario_analysis": analysis,
        "selections": selections,
        "beat_choreography": beat_choreography,
        "materialized_assets": {},
    }

    # Optional Stage 4 Materialization: render real WAV music, WAV SFX kit & Moodboard JPG!
    if materialize_dir:
        os.makedirs(materialize_dir, exist_ok=True)
        music_wav = os.path.join(materialize_dir, "music_score_preview.wav")
        apools.synthesize_music_score_wav(selections["music_score"]["selected"], music_wav, duration_sec=10.0)

        sfx_files = []
        for si, sfx_it in enumerate(sfxs_multi, start=1):
            sp = os.path.join(materialize_dir, f"sfx_{si:02d}_{sfx_it['family']}.wav")
            apools.synthesize_sfx_wav(sfx_it, sp)
            sfx_files.append(sp)

        specimen_jpg = os.path.join(materialize_dir, "moodboard_specimen.jpg")
        render_moodboard_specimen_jpg(plan, specimen_jpg)

        plan["materialized_assets"] = {
            "kit_dir": materialize_dir,
            "music_score_wav": music_wav,
            "sfx_kit_wavs": sfx_files,
            "moodboard_specimen_jpg": specimen_jpg,
        }
        with open(os.path.join(materialize_dir, "director_plan.json"), "w", encoding="utf-8") as fh:
            json.dump(plan, fh, ensure_ascii=False, indent=2)
        with open(os.path.join(materialize_dir, "DIRECTOR_SHEET.md"), "w", encoding="utf-8") as fh:
            fh.write(format_markdown_report(plan))

    return plan


def format_markdown_report(plan: dict) -> str:
    ps = plan["platform_spec"]
    sa = plan["scenario_analysis"]
    dc = plan["director_config"]
    lines = [
        f"# برگه کارگردانی هوشمند سناریو (`scenario_director.py`)",
        "",
        f"- **پلتفرم هدف (اولویت اول پایش):** `{ps['id']}` — {ps['label_fa']} (`{ps['resolution'][0]}×{ps['resolution'][1]}`)",
        f"- **محدوده امن تصویر (Safe Zone):** `Top:{ps['safe_zone_px']['top']} Right:{ps['safe_zone_px']['right']} Bottom:{ps['safe_zone_px']['bottom']} Left:{ps['safe_zone_px']['left']}`",
        f"- **تعداد کل گزینه‌های پایش‌شده در ۱۲ بخش ورک‌اسپیس:** **`{dc['total_workspace_candidates_scanned']}` گزینه واقعی**",
        f"- **قیف انتخاب هر عنصر:** پایش کل مخزن پلتفرم ⬅ استخراج **`Top-{dc['top_k']}`** مناسب‌ترین‌ها ⬅ انتخاب تصادفیِ وزن‌دار و هماهنگ",
        f"- **حال‌وهوای تشخیص‌داده‌شده سناریو:** `{', '.join(sa['dominant_moods'])}`",
        f"- **گوینده الزامی:** `Arena generate_speech(voice_id='voice-05')` (ممنوعیت مطلق TTS محلی)",
        "",
        "## ۱. جدول انتخاب‌های کارگردان در ۱۲ حوزه ورک‌اسپیس",
        "",
        "| بخش (Domain) | کل مخزن | کاندید پلتفرم | فیلتر `Top-K` | برنده نهایی (Selected Winner) | امتیاز تناسب |",
        "|---|---:|---:|---:|---|---:|",
    ]
    domain_labels = {
        "editorial_grammar": "۱. ساختار روایت و ضرب‌آهنگ تدوین",
        "visual_style_pack": "۲. سبک بصری و هویت کارگردانی",
        "hook_typography": "۳. تایپوگرافی کینتیک هوک شروع",
        "body_and_data_typography": "۴. تایپوگرافی بدنه، زیرنویس و آمار",
        "thumbnail_typography": "۵. تایپوگرافی تامبنیل / کاور",
        "font_and_caption_stack": "۶. خانواده فونت فارسی + تم کپشن",
        "motion_choreography": "۷. انیمیشن، حرکت دوربین و OpenMotion",
        "imagery_and_viz": "۸. عکاسی واقعی، تصویرسازی، نقشه و نمودار",
        "gl_transitions": "۹. ترنزیشن‌های سه‌بعدی OpenGL",
        "vfx_and_shaders": "۱۰. جلوه‌های ویژه GPU / LYGIA / Frei0r",
        "voice_and_dsp": "۱۱. صداپیشگی `voice-05` و رک LADSPA/Pedalboard",
        "sfx_arsenal": "۱۲الف. پک ۶تایی افکت‌های صوتی و فولی",
        "music_score": "۱۲ب. موسیقی متن ارکسترال / الکترونیک",
    }
    for k, lbl in domain_labels.items():
        s = plan["selections"][k]
        win = s["selected"]
        lines.append(
            f"| {lbl} | `{s['total_pool_scanned']}` | `{s['platform_matched_pool']}` | "
            f"`Top {s['top_k_size']}` | **{win.get('title', win['id'])}** | `{s['selected_score']}` |"
        )

    lines += ["", "## ۲. جزئیات ۱۰ کاندید برتر (`Top-10`) و دلیل انتخاب هر بخش", ""]
    for k, lbl in domain_labels.items():
        s = plan["selections"][k]
        win = s["selected"]
        lines.append(f"### {lbl}")
        lines.append(f"- **انتخاب نهایی:** `{win['id']}` — {win.get('desc_fa', '')}")
        top_str = " ، ".join(f"`#{c['rank']} {c['id'].split('__')[0]}` ({c['score']})" for c in s["top_k_candidates"][:10])
        lines.append(f"- **۱۰ کاندید برتر پایش‌شده:** {top_str}")
        lines.append("")

    lines += [
        "## ۳. جدول کارگردانی صحنه‌به‌صحنه (Beat-by-Beat Execution Sheet)",
        "",
        "| صحنه | نقش دراماتیک | بازه زمانی | تصویر و داده | تایپوگرافی | موشن و دوربین | ترنزیشن + VFX | افکت صوتی (SFX) |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for b in plan["beat_choreography"]:
        t0_s, t1_s = b["time_window_sec"]
        lines.append(
            f"| `{b['beat_index']}` | `{b['role']}` | `{t0_s}s–{t1_s}s` | "
            f"`{b['imagery_recipe_id'].split('__')[1]}` | `{b['typography_preset_id'][:32]}…` | "
            f"`{b['motion_choreography_id'][:26]}` | `{b['gl_transition_out']}` + `{b['vfx_pass'][:20]}` | `{b['sfx_cue'].split('__')[1]}` |"
        )

    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    print("==========================================================================")
    print("  SCENARIO DIRECTOR SELF-TEST — Auditing All 12 Workspace Asset Pools")
    print("==========================================================================")
    p1 = direct_scenario(
        "۵ سیگنال خیابانی ابرتورم: چرا حقوق ۳۵ درصد زیاد شد ولی قیمت‌ها ۸۸ درصد جهش کرد؟ بررسی بودجه و بازار تهران و مقایسه با آلمان ۱۹۲۳",
        platform="yt_16x9", top_k=10, seed=101, use_anti_repeat=False,
    )
    p2 = direct_scenario(
        "چرا قراردادهای اجاره یک‌دفعه ۶ ماهه شد؟ شوک هزینه جایگزینی در مغازه‌های شهر!",
        platform="ig_reels", top_k=10, seed=202, use_anti_repeat=False,
    )
    for tag, pl in [("YouTube 16:9", p1), ("Instagram Reels 9:16", p2)]:
        tot = pl["director_config"]["total_workspace_candidates_scanned"]
        print(f"\n[{tag}] Scanned={tot} items | Moods={pl['scenario_analysis']['dominant_moods'][:3]}")
        for dom, s in pl["selections"].items():
            assert s["total_pool_scanned"] >= 100, f"Pool {dom} has <100 items ({s['total_pool_scanned']})!"
            assert s["top_k_size"] == 10, f"Pool {dom} top_k_size={s['top_k_size']} != 10!"
            print(f"  - {dom:26s}: pool={s['total_pool_scanned']:3d} -> plat={s['platform_matched_pool']:3d} -> Top-{s['top_k_size']} -> WINNER: {s['selected']['id'][:52]} ({s['selected_score']})")
    assert p1["selections"]["hook_typography"]["selected"]["platform"] == "yt_16x9"
    assert p1["selections"]["thumbnail_typography"]["selected"]["platform"] == "yt_thumb"
    assert p2["selections"]["hook_typography"]["selected"]["platform"] == "ig_reels"
    assert p1["selections"]["voice_and_dsp"]["selected"]["voice_id"] == "voice-05"
    print("\n[SCENARIO DIRECTOR SELF-TEST PASSED ✅] All 13 selections (>=100 pool each, Top-10 funnel, Platform-First routing, voice-05 lock) verified!")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Smart Platform-First Top-K Mood & Workspace Arsenal Director")
    ap.add_argument("--scenario", help="Scenario prompt or summary text in Persian/English")
    ap.add_argument("--script", help="Path to a full scenario/script Markdown or text file")
    ap.add_argument("--platform", choices=list(apools.PLATFORM_SPECS.keys()), default=None,
                    help="Target platform (yt_16x9, yt_shorts, ig_reels, ig_story, ig_carousel, tiktok). Auto-detected if omitted.")
    ap.add_argument("--top-k", type=int, default=10, help="Shortlist K best candidates per element before weighted-random roll (default: 10)")
    ap.add_argument("--temperature", type=float, default=0.65, help="Randomness temperature inside Top-K (0.1=greedy, 0.65=smart variety, 1.5=wild)")
    ap.add_argument("--seed", type=int, default=None, help="Optional RNG seed for reproducible rolls")
    ap.add_argument("--no-anti-repeat", action="store_true", help="Disable anti-repeat history penalty")
    ap.add_argument("--out-json", help="Save full JSON production blueprint to this path")
    ap.add_argument("--out-md", help="Save readable Persian Markdown director sheet to this path")
    ap.add_argument("--materialize-kit", help="Directory to synthesize real WAV music score, 6 WAV SFX & visual moodboard JPG")
    ap.add_argument("--self-test", action="store_true", help="Run full verification across YouTube 16:9 and Instagram Reels 9:16")
    args = ap.parse_args()

    if args.self_test:
        raise SystemExit(run_self_test())

    if args.script:
        with open(args.script, encoding="utf-8") as fh:
            text = fh.read()
    elif args.scenario:
        text = args.scenario
    else:
        ap.error("Provide --scenario '...' or --script FILE.md (or run --self-test)")
        return

    plan = direct_scenario(
        scenario_text=text,
        platform=args.platform,
        top_k=args.top_k,
        temperature=args.temperature,
        seed=args.seed,
        use_anti_repeat=not args.no_anti_repeat,
        materialize_dir=args.materialize_kit,
    )

    if args.out_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_json)), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, ensure_ascii=False, indent=2)
    if args.out_md:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_md)), exist_ok=True)
        with open(args.out_md, "w", encoding="utf-8") as fh:
            fh.write(format_markdown_report(plan))

    print(format_markdown_report(plan))
    if plan["materialized_assets"]:
        print("\n[MATERIALIZED KIT READY ✅]:", json.dumps(plan["materialized_assets"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
