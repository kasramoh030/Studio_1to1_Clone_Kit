"""Easing, springs, colour helpers.  Colours are LINEAR RGB tuples (the pipeline encodes to sRGB once, at the end).
Values above 1.0 are HDR and will bloom."""
import math

def lin(h):
    return tuple((((h >> s) & 255) / 255.0) ** 2.2 for s in (16, 8, 0))

INK = lin(0x0b0b12)
INK2 = lin(0x161622)
CREAM = lin(0xf3ecdf)
ORANGE = lin(0xff5a1f)
BLUE = lin(0x2f6bff)
MINT = lin(0x3cf2c0)
PINK = lin(0xff3d8b)
YELLOW = lin(0xffd23f)
WHITE = (1.0, 1.0, 1.0)

def mul(c, k): return tuple(x * k for x in c[:3])
def rgba(c, a=1.0): return (c[0], c[1], c[2], a)
def mix3(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

def clamp01(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)
def remap(t, a, b): return clamp01((t - a) / (b - a)) if b != a else float(t >= a)
def lerp(a, b, t): return a + (b - a) * t
def smooth(x): x = clamp01(x); return x * x * (3 - 2 * x)
def ease_out_cubic(x): x = clamp01(x); return 1 - (1 - x) ** 3
def ease_in_cubic(x): x = clamp01(x); return x ** 3
def ease_in_out_cubic(x):
    x = clamp01(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def ease_out_expo(x):
    x = clamp01(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def ease_in_expo(x):
    x = clamp01(x); return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def ease_in_out_expo(x):
    x = clamp01(x)
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 2 ** (20 * x - 10) / 2 if x < .5 else (2 - 2 ** (-20 * x + 10)) / 2
def ease_out_back(x, c1=1.70158):
    x = clamp01(x); c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def ease_out_elastic(x):
    x = clamp01(x)
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 2 ** (-10 * x) * math.sin((x * 10 - .75) * (2 * math.pi) / 3) + 1
def ease_in_back(x, c1=1.70158):
    x = clamp01(x); return (c1 + 1) * x ** 3 - c1 * x ** 2

def h11(x):
    """deterministic hash -> [0,1)"""
    s = math.sin(x * 127.1 + 311.7) * 43758.5453123
    return s - math.floor(s)

def spring(t, freq=4.0, damp=5.0):
    """unit step response of a damped spring (0 -> 1 with overshoot)"""
    if t <= 0: return 0.0
    return 1 - math.exp(-damp * t) * math.cos(2 * math.pi * freq * t)


def ease_in_out_sine(x): x = clamp01(x); return -(math.cos(math.pi * x) - 1) / 2
def stagger(i, n, total, t0=0.0):
    """start time of item i of n when the whole stagger should take `total` seconds"""
    return t0 + (total * i / max(1, n - 1) if n > 1 else 0.0)
def pingpong(x): x = x % 2.0; return x if x < 1 else 2 - x

# Ready-made palettes (linear RGB).  Pick one per video and stay in it.
PALETTES = {
    "ember":   dict(bg=lin(0x0b0b12), fg=lin(0xf3ecdf), a=lin(0xff5a1f), b=lin(0x2f6bff), c=lin(0xffd23f)),
    "neon":    dict(bg=lin(0x07061a), fg=lin(0xf2f0ff), a=lin(0xff2bd6), b=lin(0x2bf0ff), c=lin(0xb6ff2b)),
    "paper":   dict(bg=lin(0xf3ecdf), fg=lin(0x14141d), a=lin(0xff5a1f), b=lin(0x2f6bff), c=lin(0x14141d)),
    "mint":    dict(bg=lin(0x061814), fg=lin(0xeafff8), a=lin(0x3cf2c0), b=lin(0xff3d8b), c=lin(0xffd23f)),
    "mono":    dict(bg=lin(0x0a0a0a), fg=lin(0xf5f5f5), a=lin(0xf5f5f5), b=lin(0x8a8a8a), c=lin(0xff3b30)),
    "sunset":  dict(bg=lin(0x1a0b1e), fg=lin(0xfff1e6), a=lin(0xff7a45), b=lin(0xc03cff), c=lin(0xffd166)),
}
