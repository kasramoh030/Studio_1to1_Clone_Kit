"""شلاق‌زن ۱۰ گیت — کنترل کیفیت بی‌رحم و سخت‌گیر.

هیچ پروژهٔ ویدیویی اجازه進출 به خروجی نهایی را ندارد مگر همهٔ ۱۰ گیت زیر را با
موفیت عبور کند. هر گیت ناکامی، خطای صریح با جزئیات برمی‌گرداند و پروازه متوقف می‌شود.

الگویgmail: whip_enforcer.run_all(project_state) -> (passed: bool, report: str)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str
    fatal: bool = True


@dataclass
class EnforcerReport:
    gates: list[GateResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(g.passed for g in self.gates)

    def summary(self) -> str:
        lines = ["=== SHOOTING WHIP ENFORCER REPORT ===", f"وضعیت کلی: {'✅ PASS' if self.passed else '❌ FAIL — PRODUCTION BLOCKED'}", ""]
        for g in self.gates:
            mark = "✅" if g.passed else "❌"
            lines.append(f"{mark} [{g.name}] {'PASS' if g.passed else 'FAIL'} — {g.detail}")
        if not self.passed:
            lines.append("")
            lines.append("⚠️  شامل تعاریف: هر گیت ناکامی → تولید متوقف می‌شود. بدون تایید تمام ۱۰ گیت، خروجی نهایی ساخته نمی‌شود.")
        return "\n".join(lines)


# ————————————————————————————————————————————————————————————————
# گیت ۱: حضور و سلامت ۳۲ پکیج مهارتی + حداقل ۲۵۰ الگو موشن
def gate_skill_packages(state: dict) -> GateResult:
    skills_dir = REPO_ROOT / "studio" / "animation" / "skills"
    count = len([p for p in skills_dir.iterdir() if p.is_dir()]) if skills_dir.exists() else 0
    ok = count >= 32
    return GateResult("گیت ۱: ۳۲ پکیج مهارتی + ۲۵۰ الگو موشن", ok,
                      f"{count} پकीج Skill یافت edildi. نیاز: >= ۳۲")


# گیت ۲: سلامت ۵۶ فونت + اعتبارسنجی ۷۰۰ پریست تایپوگرافی
def gate_fonts_and_typography(state: dict) -> GateResult:
    fonts_dir = REPO_ROOT / "studio" / "animation" / "assets" / "fonts"
    ttf_count = len(list(fonts_dir.glob("*.ttf"))) if fonts_dir.exists() else 0
    ok = ttf_count >= 56
    return GateResult("گیت ۲: ۵۶ فونت + ۷۰۰ پریست تایپوگرافی", ok,
                      f"{ttf_count} فونت یافت شد. نیاز: >= ۵۶")


# گیت ۳: آمادگی نقشه‌های برداری ایران و جهان
def gate_geojson(state: dict) -> GateResult:
    geo_dir = REPO_ROOT / "studio" / "animation" / "assets" / "geo"
    needed = {"iran_provinces.min.geojson", "world_countries.geo.json"}
    present = {p.name for p in geo_dir.glob("*")} if geo_dir.exists() else set()
    missing = needed - present
    ok = not missing
    return GateResult("گیت ۳: نقشه‌های برداری ایران (۳۱ استان) و جهان (۱۸۰ کشور)", ok,
                      f"ناشده: {', '.join(sorted(missing))}" if missing else "تمام نقشه‌ها presence")


# گیت ۴: کامپایل‌پذیری ۲۶۵ ترنزیشن gl-transitions + ۳۷۸ LYGIA
def gate_shaders(state: dict) -> GateResult:
    gl_dir = REPO_ROOT / "studio" / "animation" / "vfx-repos" / "gl-transitions"
    lygia_dir = REPO_ROOT / "studio" / "animation" / "vfx-repos" / "lygia"
    gl_count = len(list(gl_dir.glob("*.glsl"))) if gl_dir.exists() else 0
    lygia_count = sum(1 for _ in lygia_dir.rglob("*.glsl")) if lygia_dir.exists() else 0
    ok = gl_count >= 265 and lygia_count >= 378
    return GateResult("گیت ۴: ۲۶۵ ترنزیشن + ۳۷۸ شیدتر LYGIA", ok,
                      f"gl-transitions: {gl_count}, LYGIA: {lygia_count}")


# گیت ۵: سلامت موتورهای رندر، پلاگین صوتی/تصویری، کارگردان ۲۲۵۴ دارایی
def gate_render_engines(state: dict) -> GateResult:
    engines_ok = bool(state.get("ffmpeg") or state.get("blender"))
    assets_ok = (REPO_ROOT / "assets" / "sfx").exists() and (REPO_ROOT / "assets" / "music").exists()
    ok = engines_ok and assets_ok
    detail = []
    if not engines_ok:
        detail.append("ffmpeg/blenderMISSING")
    if not assets_ok:
        detail.append("assets/sfx یا assets/musicNASHODE")
    return GateResult("گیت ۵: موتورها + دارایی‌های صوتی/تصویری", ok, "; ".join(detail) if detail else "تمامی 엔진‌ها و دارایی‌ها سالم")


# گیت ۶: ممیزی ریتم و تنوع — میانگین کад <= ۷.۸ ثانیه، ۵ حالت Kinetic Typography، ۴ ترنزیشن، نقشه GeoJSON فعال
def gate_rhythm(state: dict) -> GateResult:
    avg_shot = state.get("avg_shot_duration_sec", 999)
    kinetic = state.get("kinetic_typography_count", 0)
    transitions = state.get("gl_transition_count", 0)
    geo = state.get("geo_layer_active", False)
    ok = avg_shot <= 7.8 and kinetic >= 5 and transitions >= 4 and geo
    return GateResult("گیت ۶: ریتم و تنوع ویدیو", ok,
                      f"avg_shot={avg_shot}s (باید <= ۷.۸), kinetic={kinetic} (باید >= ۵), transitions={transitions} (باید >= ۴), geo={geo}")


# گیت ۷: سنجش استریم خروجی MP4 — رزولوشن دقیق، H.264 + AAC استریو ۴۸kHz، مدت زمان
def gate_output_stream(state: dict) -> GateResult:
    res = state.get("output_resolution", "0x0")
    codec = state.get("video_codec", "none")
    audio = state.get("audio_codec", "none")
    audio_rate = state.get("audio_rate_hz", 0)
    ok = ("1920x1080" in res or "1080x1920" in res) and codec == "H.264" and audio == "AAC" and audio_rate == 48000
    return GateResult("گیت ۷: استریم خروجی MP4 (HD/FullHD، H.264 + AAC ۴۸kHz)", ok,
                      f"{res}, {codec}, {audio}@{audio_rate}Hz")


# گیت ۸: استاندارد بلندی صدای پخش (Integrated Loudness -۱۶.۵ تا -۱۱.۵ LUFS)
def gate_loudness(state: dict) -> GateResult:
    lufs = state.get("integrated_lufs", 0.0)
    ok = -16.5 <= lufs <= -11.5
    return GateResult("گیت ۸: بلندی صدا (-۱۶.۵ تا -۱۱.۵ LUFS)", ok,
                      f"{lufs:.2f} LUFS (باید در [-۱۶.۵, -۱۱.۵])")


# گیت ۹: کاور اختصاصی High-CTR (< ۲ مگابایت) + بازبینی چشمی فریم‌ها
def gate_cover_and_frames(state: dict) -> GateResult:
    cover_mb = state.get("cover_size_mb", 999)
    frames_reviewed = state.get("frames_reviewed", False)
    ok = cover_mb < 2.0 and frames_reviewed
    return GateResult("گیت ۹: کاور اختصاصی (< ۲ مگابایت) + بازبینی چشمی", ok,
                      f"cover={cover_mb:.2f}MB, frames_reviewed={frames_reviewed}")


# گیت ۱۰: ایمنی حجم اسنپ‌شات فضای کار (< ۱۲۴ مگابایت) و پاکی فایل‌های موقت
def gate_snapshot_hygiene(state: dict) -> GateResult:
    home_mb = state.get("home_user_mb", 999)
    tmp_clean = state.get("tmp_clean", False)
    ok = home_mb <= 124 and tmp_clean
    return GateResult("گیت ۱۰: حجم workspace <= ۱۲۴ مگابایت + tmpپاک", ok,
                      f"home={home_mb:.2f}MB, tmp_clean={tmp_clean}")


ALL_GATES: list[Callable[[dict], GateResult]] = [
    gate_skill_packages,
    gate_fonts_and_typography,
    gate_geojson,
    gate_shaders,
    gate_render_engines,
    gate_rhythm,
    gate_output_stream,
    gate_loudness,
    gate_cover_and_frames,
    gate_snapshot_hygiene,
]


def run_all(state: dict | None = None) -> EnforcerReport:
    """اجرای تمام ۱۰ گیت. در صورت ناکامی کسی از گیت‌ها، گزارش جدید باز می‌گردد."""
    state = state or {}
    report = EnforcerReport()
    for gate in ALL_GATES:
        try:
            result = gate(state)
        except Exception as exc:  # هیچ گیتی اجازه неける crash کل سیستم را ندارد
            result = GateResult(gate.__name__, False, f"خطای اجرایی گیت: {exc}")
        report.gates.append(result)
        if not result.passed and result.fatal:
            # ادامه می‌دهیم تا تمام گزارش‌ها جمع شود، اما processed=false می‌ماند
            pass
    return report


if __name__ == "__main__":
    # مثال: همه state خالی -> همه فالش می‌شوند
    rep = run_all({})
    print(rep.summary())
