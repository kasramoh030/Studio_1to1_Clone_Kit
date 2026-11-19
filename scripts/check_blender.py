#!/usr/bin/env python3
# scripts/check_blender.py — بررسی نصب بلندر و راهنمای نصب دستی
# اجرا: python3 scripts/check_blender.py
from __future__ import annotations

import shutil
import subprocess
import sys


def check_blender() -> tuple[bool, str | None]:
    """True برمی‌گرداند اگر blender در PATH باشد، همراه با نسخه."""
    path = shutil.which("blender")
    if not path:
        return False, None
    try:
        out = subprocess.run(
            ["blender", "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        version = out.stdout.strip().splitlines()[0] if out.stdout else "ناشناخته"
        return True, version
    except Exception:
        return True, path


def main() -> int:
    ok, version = check_blender()
    print("=" * 60)
    print("🔍 بررسی نصب بلندر (Blender 3D)")
    print("=" * 60)
    if ok:
        print(f"✅ بلندر در دسترس است: {version}")
        print("   مسیر:", shutil.which("blender"))
        print("   برای رندر بدون مانیتور: blender --background --python script.py")
        return 0
    print("❌ بلندر نصب نشده است.")
    print()
    print("📥 راهنمای نصب دستی (خارج از ورک اسپیس):")
    print("   ۱. https://www.blender.org/download/  →  Blender LTS (مثل 4.3) را دانلود کنید.")
    print("   ۲. mkdir -p ~/apps && cd ~/apps")
    print("   ۳. tar -xjf blender-*.tar.xz")
    print("   ۴. echo 'export PATH=$PATH:~/apps/blender-*/' >> ~/.bashrc")
    print("   ۵. source ~/.bashrc")
    print()
    print("⚠️  در این Sandbox شبکه به blender.org و مخازن دبیان مسدود است،")
    print("   بنابراین نصب خودکارBlender امکان‌پذیر نیست.")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
