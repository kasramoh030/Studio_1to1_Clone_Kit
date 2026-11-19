#!/usr/bin/env python3
"""studio-engine — Studio_1to1_Clone_Kit 統合コマンドライン.

使い方:
    python3 -m engine cli check-engines
    python3 -m engine cli list-sfx
    python3 -m engine cli list-transitions
    python3 -m engine cli list-effects
    python3 -m engine cli render-sample --out /tmp/demo.mp4
    python3 -m engine cli chat-reminder --check state.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lazy imports so the CLI works even if optional deps are missing.


def cmd_check_engines(args):
    """システム・モーターと Python 依存の生存確認."""
    checks = []
    for exe in ["ffmpeg", "blender", "fluidsynth", "rsvg-convert"]:
        from shutil import which

        checks.append((exe, bool(which(exe))))
    for mod in ["numpy", "scipy", "cv2", "soundfile", "moderngl", "faster_whisper", "pedalboard"]:
        try:
            __import__(mod)
            checks.append((mod, True))
        except ImportError:
            checks.append((mod, False))
    ok = True
    for name, healthy in checks:
        flag = "OK " if healthy else "MISS"
        print(f"[{flag}] {name}")
        ok = ok and healthy
    print()
    print("エンジン検証:", "全健全" if ok else "一部未導入（install.sh を参照してインストールしてください）")
    return 0 if ok else 1


def _list_dir(desc, directory, ext):
    print(f"## {desc} ({directory})")
    if not os.path.isdir(directory):
        print("  (ディレクトリ未作成)")
        return 1
    files = sorted(f for f in os.listdir(directory) if f.endswith(ext))
    for f in files:
        print(f"  - {f}")
    print(f"合計: {len(files)} 件")
    return 0


def cmd_list_sfx(args):
    return _list_dir("Six-SFX Cinema Vault サンプル (48kHz ステレオ WAV)",
                     os.path.join(REPO_ROOT, "assets", "sfx"), ".wav")


def cmd_list_music(args):
    return _list_dir("BGM サンプル (Italo-Funk 120 BPM)",
                     os.path.join(REPO_ROOT, "assets", "music"), ".wav")


def cmd_list_transitions(args):
    d = os.path.join(REPO_ROOT, "studio", "animation", "vfx-repos", "gl-transitions")
    return _list_dir("gl-transitions GPU シェーダー (265)", d, ".glsl")


def cmd_list_effects(args):
    d = os.path.join(REPO_ROOT, "studio", "animation", "vfx-repos", "lygia")
    count = 0
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith(".glsl"):
                print(f"  - {os.path.relpath(os.path.join(root, f), os.path.join(REPO_ROOT, 'studio', 'animation', 'vfx-repos'))}")
                count += 1
    print(f"## LYGIA シェーダーモジュール (378) 合計: {count} 件")
    return 0


def cmd_render_sample(args):
    """デモ・クリップをレンダリング (ffmpeg があれば MP4 出力, なければプランのみ表示)."""
    from shutil import which

    out = args.out or "/tmp/studio_demo.mp4"
    sfx = os.path.join(REPO_ROOT, "assets", "sfx", "epic_whoosh.wav")
    music = os.path.join(REPO_ROOT, "assets", "music", "bgm_italo_funk_120bpm_short15.wav")
    print(f"SFX サンプル: {sfx} (存在: {os.path.exists(sfx)})")
    print(f"BGM サンプル: {music} (存在: {os.path.exists(music)})")
    if which("ffmpeg"):
        import subprocess

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=0x1a1a2e:size=1920x1080:rate=30:duration=5",
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
            "-i", sfx,
            "-filter_complex", "[1:a][2:a]amerge=inputs=2[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-shortest", out,
        ]
        print("ffmpeg でデモをレンダリング中...")
        subprocess.run(cmd, check=True)
        print(f"出力: {out}")
    else:
        print("ffmpeg が未導入のため実際のエンコードはスキップしました（install.sh で ffmpeg を導入してください）.")
    return 0


def cmd_chat_reminder(args):
    """チャット・ページ制限リマインダー."""
    script = os.path.join(REPO_ROOT, "scripts", "chat_reminder", "chat_reminder.py")
    if os.path.exists(script):
        import runpy

        sys.argv = [script] + (args.reminder_args or [])
        runpy.run_path(script, run_name="__main__")
    else:
        print("scripts/chat_reminder/chat_reminder.py が見つかりません。")
        return 1
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="studio-engine", description="Studio_1to1_Clone_Kit 統合エンジン CLI")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("check-engines", help="モーター/依存関係の生存確認").set_defaults(func=cmd_check_engines)
    sub.add_parser("list-sfx", help="SFX サンプル一覧").set_defaults(func=cmd_list_sfx)
    sub.add_parser("list-music", help="BGM サンプル一覧").set_defaults(func=cmd_list_music)
    sub.add_parser("list-transitions", help="gl-transitions 一覧").set_defaults(func=cmd_list_transitions)
    sub.add_parser("list-effects", help="LYGIA シェーダー一覧").set_defaults(func=cmd_list_effects)

    p_render = sub.add_parser("render-sample", help="デモ・クリップをレンダリング")
    p_render.add_argument("--out", default="/tmp/studio_demo.mp4")
    p_render.set_defaults(func=cmd_render_sample)

    p_chat = sub.add_parser("chat-reminder", help="チャット・ページ制限リマインダー")
    p_chat.add_argument("reminder_args", nargs="*")
    p_chat.set_defaults(func=cmd_chat_reminder)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
