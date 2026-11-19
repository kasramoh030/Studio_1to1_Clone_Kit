#!/usr/bin/env bash
# scripts/install.sh — نصب وابستگی‌های موتور تولید کلیپ Studio_1to1_Clone_Kit
# اجرا: bash scripts/install.sh
set -euo pipefail

echo "🔧 شروع نصب وابستگی‌های استودیو..."

# ۱. پایتون core (PyPI —肖ها از اینجا می‌آیند)
python3 -m pip install --break-system-packages --quiet --upgrade pip
python3 -m pip install --break-system-packages --quiet numpy scipy wave

# ۲. تلاش برای نصب ابزار سیستمی (اگر sudo/apt در دسترس باشد)
if command -v apt-get >/dev/null 2>&1; then
    echo "⬇️  تلاش برای apt-get (ffmpeg, fluidsynth, frei0r, ladspa, librsvg)..."
    sudo apt-get update -qq 2>/dev/null || true
    sudo apt-get install -y -qq \
        ffmpeg fluidsynth fluid-soundfont-gm ladspa-sdk tap-plugins frei0r-plugins librsvg2-bin \
        2>/dev/null || echo "⚠️  apt_get محدود است (بدون اینترنت سیستمی). ادامه بدون ابزار سیستمی."
else
    echo "ℹ️  apt-get یافت نشد — ابزار سیستمی نادیده گرفته شد."
fi

# ۳. بلندر ۳ بعدی (نصب دستی خارج از ورک اسپیس — شبکه Sandbox به blender.org دسترسی ندارد)
echo ""
echo "🧊 نصب بلندر (.headless رندر ۳ بعدی و اناتومی) — خارج از ورک اسپیس:"
if command -v blender >/dev/null 2>&1; then
    echo "  ✅ blender هم‌اکنون در دسترس است: $(blender --version | head -1)"
else
    echo "  ❌ blender یافت نشد (نصب دستی لازمه)."
    echo ""
    echo "   ✏️  مراحل نصب دستی بلندر (خارج از /home/user/Studio_1to1_Clone_Kit):"
    echo "   ۱. به https://www.blender.org/download/ بروید و Blender LTS (مثلاً 4.3) را دانلود کنید."
    echo "   ۲. فایل tar.xz را در دایرکتوری خارج از ورک اسپیس استخراج کنید:"
    echo "        mkdir -p ~/apps && cd ~/apps"
    echo "        tar -xjf blender-*.tar.xz"
    echo "   ۳. بلندر را به PATH اضافه کنید:"
    echo "        echo 'export PATH=\$PATH:~/apps/blender-*/' >> ~/.bashrc"
    echo "        source ~/.bashrc"
    echo "   ۴. برای رندر بدون مانیتور (headless):"
    echo "        blender --background --python render_script.py"
    echo ""
    echo "   ⚠️  توجه: در این Sandbox دسترسی به blender.org و مخازن دبیان مسدود است،"
    echo "      بنابراین نصب خودکار Blender ممکن نیست."
fi

# ۳. بررسیmotorها
echo ""
echo "📋 گزارش وضعیت موتورها:"
for exe in ffmpeg blender fluidsynth rsvg-convert python3; do
    if command -v "$exe" >/dev/null 2>&1; then
        echo "  ✅ $exe"
    else
        echo "  ❌ $exe (نصب نشده)"
    fi
done

for mod in numpy scipy; do
    if python3 -c "import $mod" 2>/dev/null; then
        echo "  ✅ python:$mod"
    else
        echo "  ❌ python:$mod"
    fi
done

echo ""
echo "✅ نصب پایان یافت."
echo "   اجرای begleggender: python3 -m engine cli check-engines"
echo "   لیست SFX: python3 -m engine cli list-sfx"
echo "   لیست ترنزیشن‌ها: python3 -m engine cli list-transitions"
