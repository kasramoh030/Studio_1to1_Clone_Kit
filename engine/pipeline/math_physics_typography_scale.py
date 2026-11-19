"""اسکیل تایپوگرافی ریاضیات و فیزیک حرفه‌ای.

ساخت تایترها، فرمول‌ها، نمودارها و کارت‌های داده برای محتوای آموزشی
ریاضیات، فیزیک و علوم در یوتیوب و اینستاگرام.

ویژگی‌ها:
  - رندر فرمول LaTeX → SVG (از طریق matplotlib / fallback اليدي SVG)
  - تایپوگرافی RTL فارسی برای توضیحات کنار فرمول لاتین
  - Safe-zone برای ریلز/شورتس
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MathStyle:
    name: str
    font_latex: str = "Computer Modern"
    font_fa: str = "Vazirmatn"
    text_color: str = "#FFFFFF"
    bg_color: str = "#0B0F19"
    accent: str = "#FFD700"  # طلایی برای اعداد مهم


MATH_STYLES = {
    "blackboard": MathStyle("blackboard", accent="#00FF88", bg_color="#1A1A2E"),
    "white_clean": MathStyle("white_clean", text_color="#111827", bg_color="#FFFFFF", accent="#2563EB"),
    "neon_physics": MathStyle("neon_physics", text_color="#00F2FF", bg_color="#050505", accent="#FF0055"),
    "gold_math": MathStyle("gold_math", text_color="#FFFFFF", bg_color="#0B0F19", accent="#FFD700"),
}


@dataclass
class PhysicsPreset:
    topic: str
    formula_latex: str
    explanation_fa: str
    style: str = "blackboard"


PHYSICS_PRESETS = [
    PhysicsPreset("نور و النسبیت خاصة", "E = mc^2", "معادله آینشتین: انرژی = bulk × سرعت نوری^2", "neon_physics"),
    PhysicsPreset("مکانک کوانتم", "\\hat{H} \\Psi = E \\Psi", "مکوان Schrödinger — تحول حالت کوانتیک", "blackboard"),
    PhysicsPreset("ترمودینامیک", "\\Delta S \\ge 0", "دومین قانون ترمودینامیک: انتراپی هرگز کاهش نمی‌یابد", "white_clean"),
    PhysicsPreset("الکترومغناطیس", "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}", "قانون فارادی", "gold_math"),
]


def render_latex_svg(latex: str, out_path: str) -> str:
    """پردازش LaTeX به SVG اگر matplotlib موجود باشد، در غیر این صورت fallback hand-made."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(6, 2))
        fig.text(0.5, 0.5, f"${latex}$", fontsize=24, ha="center", va="center")
        fig.patch.set_alpha(0.0)
        plt.axis("off")
        plt.savefig(out_path, transparent=True, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        return out_path
    except Exception:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="120"><text x="20" y="60" font-family="Vazirmatn" font-size="24" fill="#fff">{latex}</text></svg>'
        Path(out_path).write_text(svg, encoding="utf-8")
        return out_path


def describe() -> str:
    lines = ["=== اسکیل تایپوگرافی ریاضیات و فیزیک ===", "سبک‌ها:"]
    for name, s in MATH_STYLES.items():
        lines.append(f"  - {name}: فونت لاتین {s.font_latex} + فارسی {s.font_fa}, accents {s.accent}")
    lines.append("پریست‌های فیزیک:")
    for p in PHYSICS_PRESETS:
        lines.append(f"  - {p.topic}: {p.formula_latex}  →  {p.explanation_fa}")
    lines.append("Require: matplotlib (fallback SVG hand-made در صورت عدم وجود)")
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
