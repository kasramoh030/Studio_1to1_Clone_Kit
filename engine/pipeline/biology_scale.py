"""اسکیل زیست‌شناسی — انیمیشن و تایپوگرافی برای محتوای بیولوژیک و پزشکی.

ساخت صحنه‌های سلول، DNA، پروتئین، گذر گerusellen (mitosis)، سیستم‌های بدن و
توضیحات ریلی لاین (callout) با فونت فارسی و لاتین.

بسته‌ها: opensimplex (نویز ارگانیک برای حرکت سلولی), shapely (هندسه سلولی/دامیتر)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CellPreset:
    name: str
    organelle_focus: list[str]
    style: str = "medical_illustration"
    duration_sec: float = 8.0


CELL_PRESETS = [
    CellPreset("جانوسیتوز (Mitosis)", ["کROMوسوم", "میتوکندری", "زامپラー گوئ"]),
    CellPreset("ترسیل پروتئین", ["ریبوزوم", "ارگانه گوئ", "vesicle"]),
    CellPreset("zynapse عصبی", ["نوروترانسмитور", "ماترسن"]),
    CellPreset("DNA رپلیکشن", ["هایلکس دو گانه", "انزیم هلیکاز"]),
]

DNA_SEQUENCES = ["ATGCGTAC", "CGTAACGT", "TTAGGGTT", "GCCAACTG"]


def dna_animation_plan(seq: str, duration: float = 6.0) -> dict:
    """طرح انیمیشن DNA برای ریلز/شورتس."""
    return {
        "sequence": seq,
        "duration_sec": duration,
        "frames": int(duration * 60),
        "rotation_deg": 360,
        "color_palette": ["#00F2FF", "#FF0055", "#FFD700", "#00FF88"],
        "rtl_label_fa": "رکیت DNA — 애니메이션 زیستی",
    }


def describe() -> str:
    lines = ["=== اسکیل زیست‌شناسی ===", "پรيست‌های سلولی:"]
    for c in CELL_PRESETS:
        organs = "، ".join(c.organelle_focus)
        lines.append(f"  - {c.name}: fokus بر روی [{organs}] ({c.duration_sec} ثانیه)")
    lines.append("رکیت‌های DNA نمونه:")
    for s in DNA_SEQUENCES:
        lines.append(f"  - {s}")
    lines.append("Require: opensimplex, shapely (نصب شد) + بلندر برای مدل ۳ بعدی سلول")
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
