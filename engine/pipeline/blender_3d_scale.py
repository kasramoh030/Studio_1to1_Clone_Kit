"""اسکیل ۳ بعدی: بلندر + اناتومی — رندر سه‌بعدی حرفه‌ای (Headless Blender).

این اسکایل برای ساخت صحنه‌های ۳ بعدی، اناتومی Figural (ساختار بدن/م yüz/nochen_structure)
و 모شن گروییک ۳ بعدی در اینستاگرام و یوتیوب طراحی شده است.

نیازها:
  - Blender 4.x ( Headless /pytest-free CLI ) نصب شده در سیستم
  - ماژول bpy در Pythoon Blender در دسترس باشد
  - برای رندر بدون مانیتور: EGL / Offscreen / ソフトwar_render

اگر Blender نصب نباشد، اسکایل یک "طرح رندر ۳ بعدی" (render plan) خروجی می‌دهد
و کاربر را هدایت می‌کند تا Blender را نصب کند.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from shutil import which


BLENDER_BIN = "blender"


@dataclass
class BlenderPreset:
    name: str
    description: str
    engine: str = "CYCLES"  # CYCLES or EEVEE
    resolution: tuple[int, int] = (1920, 1080)
    samples: int = 128
    fps: int = 60


@dataclass
class AnatomyScale:
    """اناتومی برای Моشن گرافیک‌های علمی و پزشکی."""
    body_part: str  # مثلا 'skeleton', 'muscle', 'heart', 'brain', 'eye'
    style: str = "medical_illustration"  # medical_illustration, wireframe, x_ray, translucent
    camera_orbit: bool = True
    label_fa: bool = True  # برچسب فارسی


BLENDER_PRESETS = {
    "cinema_4k": BlenderPreset("cinema_4k", "سنما ۴K", engine="CYCLES", resolution=(3840, 2160), samples=256),
    "yt_1080p": BlenderPreset("yt_1080p", "یوتیوب ۱۰۸۰p", engine="EEVEE", resolution=(1920, 1080), samples=64),
    "ig_reels": BlenderPreset("ig_reels", "اینستاگرام ریلز ۱۰۸۰×۱۹۲۰", engine="EEVEE", resolution=(1080, 1920), samples=64, fps=60),
}

ANATOMY_PRESETS = [
    AnatomyScale("skeleton", "x_ray", True, True),
    AnatomyScale("muscle_system", "medical_illustration", True, True),
    AnatomyScale("heart_cardiac", "translucent", True, True),
    AnatomyScale("brain_neural", "wireframe", True, True),
    AnatomyScale("eye_retina", "medical_illustration", False, True),
]


def blender_available() -> bool:
    return which(BLENDER_BIN) is not None


def blender_version() -> str | None:
    if not blender_available():
        return None
    import subprocess

    try:
        out = subprocess.run([BLENDER_BIN, "--version"], capture_output=True, text=True, timeout=15)
        return out.stdout.strip().splitlines()[0] if out.stdout else None
    except Exception:
        return None


def render_script(preset_name: str, anatomy: AnatomyScale | None = None, output: str = "/tmp/render_3d.mp4") -> str:
    """اسکریپت پایتون برای بلندر (헤ڈلِس) را تولید می‌کند."""
    preset = BLENDER_PRESETS.get(preset_name, BLENDER_PRESETS["yt_1080p"])
    anatomy_note = ""
    if anatomy:
        anatomy_note = f"""
# اناتومی: {anatomy.body_part} ({anatomy.style})
# برچسب فارسی: {anatomy.label_fa}, دوربین مدار: {anatomy.camera_orbit}
"""
    script = f'''import bpy
import math

# —— تنظیمات رندر ——
scene = bpy.context.scene
scene.render.engine = "{preset.engine}"
scene.render.resolution_x = {preset.resolution[0]}
scene.render.resolution_y = {preset.resolution[1]}
scene.render.fps = {preset.fps}
scene.cycles.samples = {preset.samples}
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = "{output}"

# —— ان Objekte ——
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

{anatomy_note}
# اینجا می‌تواند مدل اناتومی (skeleton, muscle, heart, brain) لود شود
# bpy.ops.import_scene.obj(filepath="anatomy/{anatomy.body_part}.obj")

# دوربین و نور
bpy.ops.object.camera_add(location=(0, -3, 2))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(75), 0, 0)
scene.camera = cam

bpy.ops.object.light_add(type='SUN', location=(2, 2, 5))

# انیمیشن مداری ساده
if {str(anatomy.camera_orbit).lower() if anatomy else 'True'}:
    def frame_change(scene):
        frame = scene.frame_current
        cam.location.x = 3 * math.cos(math.radians(frame * 2))
        cam.location.y = 3 * math.sin(math.radians(frame * 2))
    bpy.app.handlers.frame_change_pre.append(frame_change)

scene.frame_start = 1
scene.frame_end = 120

print("Render script ready for Blender CLI.")
'''
    return script


def describe() -> str:
    lines = [
        "=== اسکیل ۳ بعدی: بلندر + اناتومی ===",
        f"بلندر در دسترس: {'بله (' + blender_version() + ')' if blender_available() else 'خیر — نصب کنید (blender.org)'}",
        "پ्रيست‌ها:",
    ]
    for name, p in BLENDER_PRESETS.items():
        lines.append(f"  - {name}: {p.description}, {p.engine}, {p.resolution[0]}x{p.resolution[1]}, {p.samples}samples")
    lines.append("پรيست‌های اناتومی:")
    for a in ANATOMY_PRESETS:
        lines.append(f"  - {a.body_part}: {a.style}, برچسب={'دار' if a.label_fa else 'ندارد'}, مدار={'بله' if a.camera_orbit else 'خیر'}")
    lines.append(
        "اجرای رندر: blender --background --python render_script.py  (فایل تولیدی توسط render_script() )"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
