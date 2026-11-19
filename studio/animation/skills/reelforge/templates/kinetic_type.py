"""Kinetic typography - one word per beat, each with its own motion style (16:9, 9 s)."""
import os, sys, math
SKILL_DIR = None  # set by `rf.py new`; otherwise auto-detected below
for _d in (SKILL_DIR, os.environ.get("REELFORGE_HOME"), os.path.join(os.path.expanduser("~"), ".claude", "skills", "reelforge"),
           os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
    if _d and os.path.isdir(os.path.join(_d, "reelforge")):
        sys.path.insert(0, _d); break
from reelforge import *

# ---------------------------------------------------------------- edit me
WORDS = ["MAKE", "IT", "MOVE", "WITH", "TIMING", "SPACING", "WEIGHT", "AND", "RHYTHM", "EVERY", "FRAME", "COUNTS"]
TAGLINE = "motion graphics, rendered in code"
OUTRO = "REELFORGE"          # your name / brand on the end card
PAL = PALETTES["ember"]
BPM = 120
# -------------------------------------------------------------------------

BG = r"""
uniform vec3 uA; uniform vec3 uB; uniform float uWipe; uniform vec3 uFg;
out vec4 o;
void main(){
  vec2 p = P();
  vec3 c = p.y < mix(-0.6, 0.6, uWipe) ? uB : uA;
  float s = fract((p.x + p.y) * 12. - uTime * 1.5);          // drifting diagonal stripes
  c = mix(c, uFg, fill(abs(s - .5) - .1) * 0.025);
  c *= 1.0 - 0.2 * dot(p, p) + 0.06 * uKick;                 // vignette + kick pulse
  o = vec4(c, 1);
}
"""


class Words(Scene):
    post = dict(bloom=0.5, threshold=1.1, grain=0.03)

    def shake(self, t):
        beat = self.project.track.spb
        return 5 * math.exp(-(t % beat) * 14)

    def render(self, eng, t, fb):
        spb = self.project.track.spb
        k = max(0, min(len(WORDS) - 1, int(max(t, 0) // spb)))
        lt = t - k * spb                                          # time inside this beat
        cols = [PAL["bg"], PAL["a"], PAL["bg"], PAL["b"]]
        bg, prev = cols[k % 4], cols[(k - 1) % 4]
        fg = PAL["fg"] if bg == PAL["bg"] else PAL["bg"]
        eng.fs(BG, fb, {"uA": prev, "uB": bg, "uWipe": ease_out_expo(lt / 0.15) if k else 1.0, "uFg": fg},
               clear=(0, 0, 0, 1))
        word, style = WORDS[k], k % 4
        size = eng.text.fit(word, "display", 0.28, eng.aspect * 0.85, tracking=0.03)   # keep long words inside the frame
        c = rgba(fg)
        if style == 0:      # drop in with overshoot, staggered
            anim = lambda g: dict(dy=(1 - ease_out_back(clamp01((lt - g.i * 0.03) / 0.25), 2.2)) * 0.7,
                                  alpha=clamp01((lt - g.i * 0.03) / 0.05))
        elif style == 1:    # tracking expands
            e = ease_out_expo(lt / 0.45)
            anim = lambda g: dict(dx=g.cx * lerp(-0.5, 0.2, e))
        elif style == 2:    # slam + squash
            s = lerp(1.6, 1.0, ease_out_expo(lt / 0.07))
            sq = 1 - 0.2 * math.exp(-lt * 22) * (lt > 0.06)
            anim = lambda g: dict(s=s, sy=s * sq, sx=s / sq ** 0.5, ay=-g.gh * 0.3)
        else:               # bouncing letters, alternating outline
            anim = lambda g: dict(dy=0.04 * abs(math.sin(math.pi * lt * 4 - g.i * 0.9)) * clamp01(lt * 6),
                                  outline=(3.0 if g.i % 2 else 0.0))
        eng.text.put(word, "display", size, fb, color=c, tracking=0.03, anim=anim)
        eng.text.put(TAGLINE.upper(), "mono", 0.016, fb, y=-0.4, tracking=0.25, color=rgba(fg, 0.6))


class Outro(Scene):
    def render(self, eng, t, fb):
        eng.fs(BG, fb, {"uA": PAL["bg"], "uB": PAL["bg"], "uWipe": 1.0, "uFg": PAL["fg"]}, clear=(0, 0, 0, 1))
        eng.text.put(OUTRO, "display", eng.text.fit(OUTRO, "display", 0.14, eng.aspect * 0.8, 0.05), fb, color=rgba(mul(PAL["fg"], 1.2)), tracking=0.05,
                     anim=lambda g: dict(alpha=ease_out_cubic((t - g.i * 0.05) / 0.4),
                                         dy=(1 - ease_out_expo((t - g.i * 0.05) / 0.6)) * -0.06))
        L = 0.3 * ease_out_expo((t - 0.4) / 0.6)
        eng.shapes.line(-L, -0.11, L, -0.11, 0.002, rgba(mul(PAL["a"], 2.5)), glow=0.5, glowk=200)
        eng.shapes.flush(fb)
        eng.text.put(TAGLINE, "serif", 0.045, fb, y=-0.19, color=rgba(PAL["fg"], ease_out_cubic((t - 0.6) / 0.5)))


spb = 60 / BPM
words_end = len(WORDS) * spb                       # 12 words * 0.5 s = 6 s ... then a held outro
proj = Project("kinetic_type", preset="16:9", duration=words_end + 4 * spb * 1.5, bpm=BPM)
proj.add(Words(), 0, words_end)
proj.add(Outro(), words_end, proj.duration, transition=("iris", 0.6))
proj.music_score(key="F minor", sections=[("build", 0, 1), ("drop", 1, 3), ("outro", 3, 5)])
proj.flash(words_end, 0.6)

if __name__ == "__main__":
    proj.cli()
