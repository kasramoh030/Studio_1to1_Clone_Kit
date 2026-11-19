"""اسکیل ۵: Morph B-Roll Shader Engine — ترنزیشن و مورف تصویر.

این اسکیل ۵ لایه را مدیریت می‌کند：
1. frei0r فیلترهای تصویر (contrast0r, saturat0r)
2. ۲۶۵ ترنزیشن gl-transitions (CrossZoom, CrossWarp, DirectionalWarp, FilmBurn, GooeyWipe, CardSwipe, Mosaic, Swirl, ZoomInCircles, RadialWipe)
3. ۳۷۸ ماژول LYGIA PostFX (نور، بلوم، کromatic aberration, ACES tonemap)
4. compositing لایه‌های uint16 (سریع و ضد کرش)

 motore به `/home/user/studio/animation/vfx_studio.py` و پوشه‌های
`vfx-repos/gl-transitions` و `vfx-repos/lygia` دسترسی دارد.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RENDER_ROOT = Path(__file__).resolve().parents[2] / "studio" / "animation"


@dataclass
class MorphConfig:
    transition: str = "CrossZoom"
    progress: float = 0.5  # 0.0 -> 1.0
    filters: list[str] = None  # frei0r filter names
    lygia_fx: list[str] = None  # postfx module names
    width: int = 1920
    height: int = 1080

    def __post_init__(self):
        self.filters = self.filters or ["contrast0r", "saturat0r"]
        self.lygia_fx = self.lygia_fx or ["filter/bloom", "color/tonemap/aces"]


def transition_list() -> list[str]:
    gl_dir = RENDER_ROOT / "vfx-repos" / "gl-transitions"
    if not gl_dir.exists():
        return []
    return sorted(p.stem for p in gl_dir.glob("*.glsl"))


def lygia_list() -> list[str]:
    lygia_dir = RENDER_ROOT / "vfx-repos" / "lygia"
    out = []
    if lygia_dir.exists():
        for p in lygia_dir.rglob("*.glsl"):
            out.append(str(p.relative_to(RENDER_ROOT / "vfx-repos")))
    return sorted(out)


def describe() -> str:
    lines = [
        "=== Morph B-Roll Shader Engine (اسکیل ۵) ===",
        f"tranzیشن‌های gl-transitions: {len(transition_list())} عدد",
        f"ماژول‌های LYGIA: {len(lygia_list())} عدد",
        "필ترهای frei0r: contrast0r, saturat0r",
        "لایه‌بندی: uint16 SIMD (پیش‌پخت EGL در /var/tmp -> ffmpeg)",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
