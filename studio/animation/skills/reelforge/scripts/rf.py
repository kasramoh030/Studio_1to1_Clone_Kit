#!/usr/bin/env python3
"""ReelForge helper CLI.

  python rf.py doctor              check GPU / OpenGL / ffmpeg / fonts / memory before you start
  python rf.py templates           list starter templates
  python rf.py new <template> [dest.py]   copy a template into the current folder, ready to run
"""
import os, sys, shutil, platform, subprocess

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL)
TEMPLATES = os.path.join(SKILL, "templates")
DEPS = ["moderngl", "numpy", "PIL", "scipy", "imageio_ffmpeg"]
PIP = "moderngl numpy pillow scipy imageio-ffmpeg"


def ok(m): print(f"  [ok]   {m}")
def warn(m): print(f"  [warn] {m}")
def bad(m): print(f"  [FAIL] {m}")


def doctor():
    print(f"ReelForge doctor  -  Python {platform.python_version()} on {platform.system()} {platform.machine()}")
    fails = 0
    missing = []
    for d in DEPS:
        try:
            __import__(d)
        except Exception:
            missing.append(d)
    if missing:
        bad(f"missing python packages: {missing}\n         fix:  {sys.executable} -m pip install {PIP}")
        return 1
    ok("python packages: " + ", ".join(DEPS))
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    ok(f"ffmpeg: {ff}")
    r = subprocess.run([ff, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    ok("libx264 available") if "libx264" in r else (bad("ffmpeg has no libx264"), )
    # GPU
    env = os.environ.copy()
    nvidia = shutil.which("nvidia-smi") is not None
    if os.name == "nt" and nvidia:
        env["SHIM_MCCOMPAT"] = "0x800000001"
    probe = ("import moderngl,sys\nsys.path.insert(0, r'%s')\nfrom reelforge.core import create_context\n"
             "c,b=create_context(); print(c.info['GL_RENDERER'],'|',c.info['GL_VERSION'],'|',b)" % SKILL)
    p = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        bad("could not create an OpenGL 3.3 context:\n         " + p.stderr.strip().splitlines()[-1])
        if platform.system() == "Linux":
            print("         headless Linux: install EGL/Mesa (apt install libegl1 libgl1-mesa-dri) or use a GPU host.")
        fails += 1
    else:
        rend = p.stdout.strip()
        ok(f"OpenGL: {rend}")
        low = rend.lower()
        if any(k in low for k in ("llvmpipe", "softpipe", "swiftshader", "microsoft basic")):
            warn("software renderer - works, but 10-50x slower. Use --preview and short ranges.")
        elif nvidia and "nvidia" not in low:
            warn("an NVIDIA GPU exists but OpenGL got another adapter. ReelForge re-launches with "
                 "SHIM_MCCOMPAT=0x800000001 automatically; if this persists set the NVIDIA Control Panel "
                 "'Preferred graphics processor' for python.exe.")
    # fonts
    fd = os.path.join(SKILL, "reelforge", "fonts")
    fonts = [f for f in os.listdir(fd) if f.endswith(".ttf")] if os.path.isdir(fd) else []
    ok(f"bundled fonts: {len(fonts)} (OFL)") if len(fonts) >= 4 else (bad("bundled fonts missing"),)
    # memory
    try:
        if os.name == "nt":
            import ctypes
            class MS(ctypes.Structure):
                _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("tp", ctypes.c_ulonglong),
                            ("ap", ctypes.c_ulonglong), ("tpf", ctypes.c_ulonglong), ("apf", ctypes.c_ulonglong),
                            ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ae", ctypes.c_ulonglong)]
            m = MS(); m.l = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            free = m.apf / 2 ** 30
            label = "free commit (RAM+pagefile)"
        else:
            free = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") / 2 ** 30
            label = "free RAM"
        if free < 1.5:
            warn(f"{label}: {free:.1f} GB - renders may crash. Close browsers/tabs; `render --chunked` resumes after crashes.")
        else:
            ok(f"{label}: {free:.1f} GB")
    except Exception:
        pass
    # store python sandbox
    if "WindowsApps" in sys.executable:
        warn("Microsoft Store Python: writes under AppData may be redirected. Keep projects/outputs in a normal folder.")
    print("\nReady." if fails == 0 else "\nFix the FAIL items above first.")
    return fails


def templates():
    for f in sorted(os.listdir(TEMPLATES)):
        if f.endswith(".py"):
            first = open(os.path.join(TEMPLATES, f), encoding="utf8").read().split('"""')[1].strip().splitlines()[0]
            print(f"  {f[:-3]:16s} {first}")


def new(name, dest=None):
    src = os.path.join(TEMPLATES, name if name.endswith(".py") else name + ".py")
    if not os.path.exists(src):
        print(f"no template '{name}'. Available:"); templates(); return 1
    dest = dest or os.path.basename(src)
    if os.path.exists(dest):
        print(f"{dest} already exists - not overwriting"); return 1
    code = open(src, encoding="utf8").read()
    code = code.replace("SKILL_DIR = None", f"SKILL_DIR = r\"{SKILL}\"", 1)
    open(dest, "w", encoding="utf8").write(code)
    print(f"created {dest}\n  python {dest} stills 1 3 5     # look before you render\n  python {dest} render")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    sys.exit({"doctor": lambda: doctor(), "templates": lambda: templates() or 0,
              "new": lambda: new(*a[1:3]) if len(a) > 1 else (print("usage: rf.py new <template> [dest.py]") or 1)}
             .get(a[0], lambda: print(__doc__) or 1)() or 0)
