"""
studio_harness.py — Heavy-Duty Multi-Asset Execution Harness for «چی میشه؟» Studio
==================================================================================
Forces ALL persisted workspace assets into active production for every new clip:
  - Assets/Geo: iran_provinces.min.geojson (31 provinces) & world_countries.geo.json
  - Assets/Fonts: Lalezar-Regular.ttf + Vazirmatn-Black/Bold.ttf + FiraCode-Bold.ttf
    rendered via native HarfBuzz/Pango SVG (`rsvg-convert`) for 100% flawless OpenType RTL!
  - VFX Repos: 265 gl-transitions shaders + 378 LYGIA GLSL modules (via vfx_studio.py)
  - Skills: 2.5D Isometric Comparisons, Geopolitical Province & World Maps, and GPU Shaders.
"""

import os
import sys
import json
import base64
import subprocess
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter

STUDIO_ROOT = "/home/user/animation-studio"
if STUDIO_ROOT not in sys.path:
    sys.path.insert(0, STUDIO_ROOT)

from vfx_studio import GPUVFXEngine, list_gl_transitions, resolve_lygia_includes

GEO_IRAN  = os.path.join(STUDIO_ROOT, "assets", "geo", "iran_provinces.min.geojson")
GEO_WORLD = os.path.join(STUDIO_ROOT, "assets", "geo", "world_countries.geo.json")

FONT_DIR       = os.path.join(STUDIO_ROOT, "assets", "fonts")
FONT_LALEZAR   = os.path.join(FONT_DIR, "Lalezar-Regular.ttf")
FONT_VAZIR_BLK = os.path.join(FONT_DIR, "Vazirmatn-Black.ttf")
FONT_VAZIR_BLD = os.path.join(FONT_DIR, "Vazirmatn-Bold.ttf")
FONT_FIRACODE  = os.path.join(FONT_DIR, "FiraCode-Bold.ttf")

SIGNATURE_TRANSITIONS = [
    "BurnThrough",
    "CameraShake",
    "BloomDissolve",
    "BokehDissolve",
    "CrossZoom",
    "GlitchMemories",
    "DirectionalWarp",
]


def get_lygia_aces_glsl() -> str:
    """Expand LYGIA's authentic ACES Filmic Tonemapping GLSL function from vfx-repos/lygia."""
    return resolve_lygia_includes('#include "lygia/color/tonemap/aces.glsl"')


def _render_svg_text_overlay(svg_elements: str, width=1920, height=1080) -> Image.Image:
    """
    Render Persian + English OpenType text (Lalezar + Vazirmatn + FiraCode) with 100% native
    HarfBuzz GSUB shaping & RTL BiDi via headless Chromium + Puppeteer-Core (zero fontconfig dep!).
    """
    if not os.path.isdir(f"{STUDIO_ROOT}/node_modules/puppeteer-core") or not os.path.isfile("/usr/bin/chromium"):
        subprocess.run(["bash", f"{STUDIO_ROOT}/ensure_engines.sh"], check=True)
    with open(FONT_LALEZAR, "rb") as f:
        b64_lal = base64.b64encode(f.read()).decode("ascii")
    with open(FONT_VAZIR_BLK, "rb") as f:
        b64_vbk = base64.b64encode(f.read()).decode("ascii")
    with open(FONT_VAZIR_BLD, "rb") as f:
        b64_vbd = base64.b64encode(f.read()).decode("ascii")
    with open(FONT_FIRACODE, "rb") as f:
        b64_fir = base64.b64encode(f.read()).decode("ascii")

    html = f"""<!DOCTYPE html><html lang="fa"><head><meta charset="utf-8"><style>
      @font-face {{ font-family:'Lalezar'; src:url(data:font/ttf;base64,{b64_lal}) format('truetype'); }}
      @font-face {{ font-family:'Vazirmatn'; src:url(data:font/ttf;base64,{b64_vbd}) format('truetype'); font-weight:700; }}
      @font-face {{ font-family:'Vazirmatn'; src:url(data:font/ttf;base64,{b64_vbk}) format('truetype'); font-weight:900; }}
      @font-face {{ font-family:'Fira Code'; src:url(data:font/ttf;base64,{b64_fir}) format('truetype'); font-weight:700; }}
      * {{ margin:0; padding:0; }}
      body {{ width:{width}px; height:{height}px; background:transparent; overflow:hidden; }}
    </style></head><body>
      <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        {svg_elements}
      </svg>
    </body></html>"""

    tmp_html = "/var/tmp/_harness_svg.html"
    tmp_png  = "/var/tmp/_harness_svg.png"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html)

    js = f"""
    const puppeteer = require('{STUDIO_ROOT}/node_modules/puppeteer-core');
    (async () => {{
      const b = await puppeteer.launch({{executablePath:'/usr/bin/chromium', args:['--no-sandbox','--disable-setuid-sandbox','--disable-gpu']}});
      const p = await b.newPage();
      await p.setViewport({{width:{width}, height:{height}, deviceScaleFactor:1}});
      await p.goto('file://{tmp_html}', {{waitUntil:'load'}});
      await p.evaluate(() => document.fonts.ready);
      await p.screenshot({{path:'{tmp_png}', omitBackground:true}});
      await b.close();
    }})();
    """
    subprocess.run(["node", "-e", js], check=True)
    im = Image.open(tmp_png).convert("RGBA")
    im.load()
    return im


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _iter_lonlat_rings(geometry: dict):
    gtype = geometry.get("type", "")
    coords = geometry.get("coordinates", [])
    if gtype == "Polygon":
        for ring in coords:
            yield ring
    elif gtype == "MultiPolygon":
        for poly in coords:
            for ring in poly:
                yield ring


def render_iran_provinces_map_overlay(
    out_png: str,
    highlight_provinces: dict = None,
    title_fa: str = "کانون فشار تورم و مسکن در استان‌های ایران",
    subtitle_en: str = "GEOPOLITICAL & PROVINCIAL HEATMAP • IRAN 31 PROVINCES",
    box=(80, 110, 880, 950),
) -> str:
    """
    Render a glowing Vox / Johnny-Harris-style vector map of all 31 provinces of Iran
    directly from assets/geo/iran_provinces.min.geojson using Lalezar + Vazirmatn + FiraCode!
    """
    if highlight_provinces is None:
        highlight_provinces = {
            "تهران": (255, 59, 48),
            "هرمزگان": (250, 204, 21),
            "خوزستان": (249, 115, 22),
            "بوشهر": (56, 189, 248),
            "اصفهان": (251, 113, 133),
        }

    with open(GEO_IRAN, "r", encoding="utf-8") as f:
        geo = json.load(f)

    W, H = 1920, 1080
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    draw_base = ImageDraw.Draw(base)
    draw_glow = ImageDraw.Draw(glow_layer)

    x0, y0, x1, y1 = box
    pad = 55
    mx0, my0, mx1, my1 = x0 + pad, y0 + 145, x1 - pad, y1 - 50

    lon_min, lon_max = 44.0, 63.4
    lat_min, lat_max = 24.8, 39.9

    def proj(lon, lat):
        nx = (lon - lon_min) / (lon_max - lon_min)
        ny = 1.0 - (lat - lat_min) / (lat_max - lat_min)
        return (mx0 + nx * (mx1 - mx0), my0 + ny * (my1 - my0))

    draw_base.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=26,
        fill=(6, 11, 22, 216),
        outline=(56, 189, 248, 130),
        width=2,
    )

    centroids = []
    for feat in geo.get("features", []):
        props = feat.get("properties", {})
        name_fa = str(props.get("name:fa") or props.get("name") or "")
        name_en = str(props.get("name:en") or "")

        matched_col = None
        for k, col in highlight_provinces.items():
            if k in name_fa or k.lower() in name_en.lower():
                matched_col = col
                break

        pts_all = []
        for ring in _iter_lonlat_rings(feat.get("geometry", {})):
            if len(ring) < 3:
                continue
            pts = [proj(pt[0], pt[1]) for pt in ring]
            pts_all.extend(pts)
            if matched_col:
                r, g, b = matched_col
                draw_glow.polygon(pts, fill=(r, g, b, 165), outline=(255, 255, 255, 230))
                draw_base.polygon(pts, fill=(r, g, b, 185), outline=(255, 245, 210, 235))
            else:
                draw_base.polygon(pts, fill=(18, 32, 56, 185), outline=(71, 120, 170, 155))

        if matched_col and pts_all:
            cx = sum(p[0] for p in pts_all) / len(pts_all)
            cy = sum(p[1] for p in pts_all) / len(pts_all)
            centroids.append((cx, cy, name_fa, matched_col))

    comp = Image.alpha_composite(glow_layer.filter(ImageFilter.GaussianBlur(radius=16)), base)
    dc = ImageDraw.Draw(comp)

    svg_parts = [
        f'<text x="{x0 + 30}" y="{y0 + 42}" font-family="Fira Code" font-weight="700" font-size="16" fill="#38BDF8">{_esc(subtitle_en)}</text>',
        f'<text x="{x1 - 30}" y="{y0 + 96}" direction="rtl" text-anchor="start" font-family="Lalezar" font-size="40" fill="#FEF08A">{_esc(title_fa)}</text>',
    ]

    for cx, cy, n_fa, col in centroids:
        r, g, b = col
        dc.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255, 255), outline=(r, g, b, 255), width=3)
        bw = max(84, len(n_fa) * 13 + 26)
        svg_parts.append(
            f'<rect x="{cx - bw/2:.1f}" y="{cy - 44:.1f}" width="{bw:.1f}" height="32" rx="8" '
            f'fill="#070B16" fill-opacity="0.90" stroke="rgb({r},{g},{b})" stroke-width="2"/>'
        )
        svg_parts.append(
            f'<text x="{cx:.1f}" y="{cy - 21:.1f}" direction="rtl" text-anchor="middle" '
            f'font-family="Vazirmatn" font-weight="900" font-size="20" fill="#FFFFFF">{_esc(n_fa)}</text>'
        )

    txt_layer = _render_svg_text_overlay("\n".join(svg_parts), W, H)
    final = Image.alpha_composite(comp, txt_layer)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    final.save(out_png)
    return out_png


def render_world_corridor_map_overlay(
    out_png: str,
    focus_countries=("Iran", "United States of America", "China", "Russia", "Saudi Arabia", "United Arab Emirates"),
    corridors=(((-74.0, 40.7), (8.5, 47.4)), ((8.5, 47.4), (51.4, 35.7)), ((116.4, 39.9), (56.2, 27.1))),
    title_fa: str = "کریدور جهانی انتقال طلا، نفت و شوک ارزی",
    subtitle_en: str = "GLOBAL MACRO CORRIDORS • 180 COUNTRIES GEOJSON",
    box=(80, 110, 960, 940),
) -> str:
    """Render a global geopolitical corridor map from assets/geo/world_countries.geo.json."""
    with open(GEO_WORLD, "r", encoding="utf-8") as f:
        world = json.load(f)

    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dg = ImageDraw.Draw(glow)

    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=(5, 10, 20, 216), outline=(250, 204, 21, 130), width=2)

    mx0, my0, mx1, my1 = x0 + 36, y0 + 138, x1 - 36, y1 - 40
    lon0, lon1, lat0, lat1 = -125.0, 145.0, -35.0, 68.0

    def proj(lon, lat):
        nx = (lon - lon0) / (lon1 - lon0)
        ny = 1.0 - (lat - lat0) / (lat1 - lat0)
        return (mx0 + nx * (mx1 - mx0), my0 + ny * (my1 - my0))

    focus_lower = {c.lower() for c in focus_countries}
    for feat in world.get("features", []):
        nm = str(feat.get("properties", {}).get("name", ""))
        is_hit = nm.lower() in focus_lower or ("iran" in nm.lower())
        for ring in _iter_lonlat_rings(feat.get("geometry", {})):
            pts = [proj(p[0], p[1]) for p in ring if lon0 <= p[0] <= lon1 and lat0 <= p[1] <= lat1]
            if len(pts) < 3:
                continue
            if "iran" in nm.lower():
                dg.polygon(pts, fill=(255, 59, 48, 175), outline=(255, 220, 180, 240))
                d.polygon(pts, fill=(239, 68, 68, 190), outline=(255, 240, 200, 245))
            elif is_hit:
                dg.polygon(pts, fill=(250, 204, 21, 120))
                d.polygon(pts, fill=(234, 179, 8, 145), outline=(254, 240, 138, 210))
            else:
                d.polygon(pts, fill=(20, 34, 58, 165), outline=(56, 89, 130, 110))

    for (la0, ph0), (la1, ph1) in corridors:
        p_start = proj(la0, ph0)
        p_end   = proj(la1, ph1)
        mid = ((p_start[0] + p_end[0]) * 0.5, min(p_start[1], p_end[1]) - 58)
        curve = [
            ((1 - s) ** 2 * p_start[0] + 2 * (1 - s) * s * mid[0] + s ** 2 * p_end[0],
             (1 - s) ** 2 * p_start[1] + 2 * (1 - s) * s * mid[1] + s ** 2 * p_end[1])
            for s in np.linspace(0, 1, 36)
        ]
        dg.line(curve, fill=(250, 204, 21, 210), width=7)
        d.line(curve, fill=(255, 250, 210, 255), width=3)
        for px, py in (p_start, p_end):
            d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(255, 255, 255, 255), outline=(250, 204, 21, 255), width=2)

    comp = Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)), img)
    svg_parts = [
        f'<text x="{x0 + 28}" y="{y0 + 42}" font-family="Fira Code" font-weight="700" font-size="16" fill="#FACC15">{_esc(subtitle_en)}</text>',
        f'<text x="{x1 - 28}" y="{y0 + 96}" direction="rtl" text-anchor="start" font-family="Lalezar" font-size="40" fill="#FFFFFF">{_esc(title_fa)}</text>',
    ]
    final = Image.alpha_composite(comp, _render_svg_text_overlay("\n".join(svg_parts), W, H))
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    final.save(out_png)
    return out_png


def render_isometric_comparison_overlay(
    out_png: str,
    bars=(
        ("حداقل حقوق", "۶۴ دلار", 0.22, (56, 189, 248)),
        ("سبد معیشت", "۲۲۵ دلار", 0.68, (251, 146, 60)),
        ("سقف تورمی ۲۰۲۷", "۳۸۰ دلار", 1.00, (239, 68, 68)),
    ),
    title_fa: str = "مقایسه حجمی قدرت خرید و هزینه بقا",
    subtitle_en: str = "2.5D ISOMETRIC DATA STORY • PURCHASING POWER GAP",
    box=(980, 120, 1840, 940),
) -> str:
    """
    Render extruded 2.5D Isometric 3D Towers using Lalezar + Vazirmatn-Black + FiraCode-Bold!
    """
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dg = ImageDraw.Draw(glow)

    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=(7, 11, 22, 218), outline=(255, 255, 255, 55), width=2)

    svg_parts = [
        f'<text x="{x0 + 28}" y="{y0 + 42}" font-family="Fira Code" font-weight="700" font-size="16" fill="#34D399">{_esc(subtitle_en)}</text>',
        f'<text x="{x1 - 28}" y="{y0 + 96}" direction="rtl" text-anchor="start" font-family="Lalezar" font-size="40" fill="#FEF08A">{_esc(title_fa)}</text>',
    ]

    n = len(bars)
    span_w = (x1 - x0 - 140)
    step_x = span_w / max(1, n)
    base_y = y1 - 125
    max_h  = (y1 - y0) - 340
    iso_dx, iso_dy = 52, 28

    for i, (lbl_fa, val_fa, ratio, rgb) in enumerate(bars):
        cx = x0 + 95 + step_x * (i + 0.5)
        bh = max(36, ratio * max_h)
        top_y = base_y - bh
        r, g, b = rgb

        p_top   = [(cx, top_y - iso_dy), (cx + iso_dx, top_y), (cx, top_y + iso_dy), (cx - iso_dx, top_y)]
        p_left  = [(cx - iso_dx, top_y), (cx, top_y + iso_dy), (cx, base_y + iso_dy), (cx - iso_dx, base_y)]
        p_right = [(cx, top_y + iso_dy), (cx + iso_dx, top_y), (cx + iso_dx, base_y), (cx, base_y + iso_dy)]

        dg.polygon(p_top, fill=(r, g, b, 185))
        d.polygon(p_left,  fill=(int(r * 0.88), int(g * 0.88), int(b * 0.88), 245), outline=(255, 255, 255, 90))
        d.polygon(p_right, fill=(int(r * 0.56), int(g * 0.56), int(b * 0.56), 245), outline=(255, 255, 255, 70))
        d.polygon(p_top,   fill=(min(255, int(r * 1.15)), min(255, int(g * 1.15)), min(255, int(b * 1.15)), 255), outline=(255, 255, 255, 200))

        svg_parts.append(
            f'<text x="{cx:.1f}" y="{top_y - iso_dy - 18:.1f}" direction="rtl" text-anchor="middle" '
            f'font-family="Vazirmatn" font-weight="900" font-size="30" fill="#FFFFFF">{_esc(val_fa)}</text>'
        )
        svg_parts.append(
            f'<text x="{cx:.1f}" y="{base_y + iso_dy + 42:.1f}" direction="rtl" text-anchor="middle" '
            f'font-family="Vazirmatn" font-weight="700" font-size="23" fill="#CBD5E1">{_esc(lbl_fa)}</text>'
        )

    comp = Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)), img)
    final = Image.alpha_composite(comp, _render_svg_text_overlay("\n".join(svg_parts), W, H))
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    final.save(out_png)
    return out_png
