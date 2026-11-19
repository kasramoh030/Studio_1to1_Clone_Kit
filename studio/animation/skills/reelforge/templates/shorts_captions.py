"""Vertical 9:16 Short / Reel / TikTok - hook title + word-by-word animated captions (SRT or auto-timed)."""
import os, sys, math, re
SKILL_DIR = None  # set by `rf.py new`; otherwise auto-detected below
for _d in (SKILL_DIR, os.environ.get("REELFORGE_HOME"), os.path.join(os.path.expanduser("~"), ".claude", "skills", "reelforge"),
           os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
    if _d and os.path.isdir(os.path.join(_d, "reelforge")):
        sys.path.insert(0, _d); break
from reelforge import *

# ---------------------------------------------------------------- edit me
HOOK = "3 RULES OF\nGREAT MOTION"
SCRIPT = ("Rule one. Nothing moves at constant speed. Ease in, ease out. "
          "Rule two. Overlap your animation so things feel alive. "
          "Rule three. Cut on the beat and your edit will feel twice as fast.")
SRT_FILE = None          # e.g. "captions.srt" - overrides SCRIPT timing
VOICE_FILE = None        # e.g. "voiceover.wav" - used as the soundtrack instead of the generated score
HANDLE = "@yourchannel"
WORDS_PER_SEC = 2.6
PAL = PALETTES["neon"]
# -------------------------------------------------------------------------

HOOK_END = 2.2


def parse_srt(path):
    txt = open(path, encoding="utf8").read()
    out = []
    for m in re.finditer(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.+?)(?:\n\n|\Z)", txt, re.S):
        g = [int(x) for x in m.groups()[:8]]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        words = m.group(9).replace("\n", " ").split()
        for i, w in enumerate(words):
            out.append((w, a + (b - a) * i / len(words), a + (b - a) * (i + 1) / len(words)))
    return out


def auto_time(text, t0, wps):
    out, t = [], t0
    for w in text.split():
        d = 1.0 / wps * (1.6 if w[-1] in ".!?" else 1.0) * (0.8 + 0.05 * len(w))
        out.append((w, t, t + d)); t += d
    return out


WORDS = parse_srt(SRT_FILE) if SRT_FILE else auto_time(SCRIPT, HOOK_END + 0.2, WORDS_PER_SEC)
END_CARD = WORDS[-1][2] + 0.4
DURATION = END_CARD + 2.5

# group words into caption "pages" of <= 3 words, breaking at sentence ends
PAGES, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 3 or w[0][-1] in ".!?,":
        PAGES.append(cur); cur = []
if cur:
    PAGES.append(cur)

BG = r"""
uniform vec3 uA; uniform vec3 uB; uniform vec3 uBg;
out vec4 o;
void main(){
  vec2 p = P(); float t = uTime;
  vec3 c = uBg;
  c += uA * 0.55 * exp(-length(p - vec2(0.18*sin(t*.5), 0.30 + 0.05*cos(t*.7))) * 3.2);
  c += uB * 0.50 * exp(-length(p - vec2(-0.2*cos(t*.4), -0.28 + 0.06*sin(t*.6))) * 3.0);
  c *= 0.9 + 0.1*fbm(p*3. + t*0.1);
  c *= 1.0 + 0.08*uKick;
  o = vec4(c, 1);
}
"""


class Short(Scene):
    post = dict(bloom=0.7, threshold=0.9, grain=0.03, vignette=0.4)

    def render(self, eng, t, fb):
        T, S = eng.text, eng.shapes
        XR = eng.aspect / 2
        eng.fs(BG, fb, {"uA": PAL["a"], "uB": PAL["b"], "uBg": PAL["bg"]}, clear=(0, 0, 0, 1))
        # progress bar (top) - viewers love knowing how long is left
        pr = clamp01(t / DURATION)
        S.box(-XR + XR * pr, 0.47, XR * pr, 0.004, rgba(mul(PAL["a"], 2.0)), corner=0.004)
        # hook title
        if t < HOOK_END + 0.5:
            out = ease_in_cubic((t - HOOK_END) / 0.35)
            for li, line in enumerate(HOOK.split("\n")):
                y = 0.08 - li * 0.1
                T.put(line, "display", T.fit(line, "display", 0.075, eng.aspect * 0.86), fb, y=y, color=rgba(mul(PAL["fg"], 1.1)), anim=lambda g, li=li: dict(
                    dy=(1 - ease_out_back(clamp01((t - 0.1 - li * 0.15 - g.i * 0.02) / 0.4))) * -0.08 + out * 0.3,
                    alpha=clamp01((t - 0.1 - li * 0.15 - g.i * 0.02) / 0.1) * (1 - out)))
        # captions
        page = next((pg for pg in PAGES if pg[0][1] - 0.05 <= t < pg[-1][2] + 0.15), None)
        if page and t < END_CARD:
            line = " ".join(w for w, a, b in page)
            size = T.fit(line.upper(), "display", 0.07, eng.aspect * 0.86, tracking=0.02)
            gl = T.layout(line.upper(), "display", size, tracking=0.02, y=-0.12)
            # map glyphs -> word index
            widx, k = [], 0
            letters = [c for c in line.upper() if c != " "]
            counts = [len(w) for w, a, b in page]
            for i in range(len(letters)):
                while i >= sum(counts[:k + 1]):
                    k += 1
                widx.append(k)
            active = max([i for i, (w, a, b) in enumerate(page) if t >= a] or [0])
            # highlight pill behind the active word
            gs = [g for g, wi in zip(gl, widx) if wi == active]
            if gs:
                x0, x1 = gs[0].cx - gs[0].gw * 0.45, gs[-1].cx + gs[-1].gw * 0.45
                pop = ease_out_back(clamp01((t - page[active][1]) / 0.18), 3)
                S.box((x0 + x1) / 2, -0.12, (x1 - x0) / 2 * pop + 0.004, size * 0.85 * pop, rgba(mul(PAL["a"], 1.3)), corner=0.012)
                S.flush(fb)
            T.draw(gl, "display", fb, anim=lambda g: (lambda wi: None if t < page[wi][1] - 0.05 else dict(
                color=rgba(mul(PAL["bg"], 1.0)) if wi == active else rgba(mul(PAL["fg"], 1.1)),
                s=1 + 0.12 * math.exp(-(t - page[wi][1]) * 14) if wi == active else 1.0,
                dy=(1 - ease_out_back(clamp01((t - page[wi][1] + 0.05) / 0.15))) * -0.02)
            )(widx[g.i]), dilate=1.0)
        # end card
        if t > END_CARD - 0.2:
            e = ease_out_back(clamp01((t - END_CARD) / 0.5), 1.6)
            S.box(0, -0.02, 0.24 * e, 0.05 * e, rgba(mul(PAL["a"], 1.4)), corner=0.05)
            S.flush(fb)
            T.put("FOLLOW", "display", 0.04, fb, y=-0.02, color=rgba(PAL["bg"]), anim=lambda g: dict(alpha=e))
            T.put(HANDLE, "mono", 0.028, fb, y=0.09, color=rgba(mul(PAL["fg"], 1.1)),
                  anim=lambda g: dict(alpha=ease_out_cubic((t - END_CARD - 0.2) / 0.4)))
        S.flush(fb)


proj = Project("shorts_captions", preset="9:16", duration=DURATION, bpm=110)
proj.add(Short(), 0, DURATION)
if VOICE_FILE:
    proj.music_file(VOICE_FILE)
else:
    proj.music_score(key="A minor", blips=[w[1] for w in WORDS if w[0][-1] in ".!?"])

if __name__ == "__main__":
    proj.cli()
