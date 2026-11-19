"""Animated data story - headline stat counter, elastic bar chart, self-drawing line chart (16:9, 10 s)."""
import os, sys, math
SKILL_DIR = None  # set by `rf.py new`; otherwise auto-detected below
for _d in (SKILL_DIR, os.environ.get("REELFORGE_HOME"), os.path.join(os.path.expanduser("~"), ".claude", "skills", "reelforge"),
           os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
    if _d and os.path.isdir(os.path.join(_d, "reelforge")):
        sys.path.insert(0, _d); break
from reelforge import *

# ---------------------------------------------------------------- edit me  (replace with real data)
TITLE = "MONTHLY ACTIVE USERS"
UNIT = "k"
LABELS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG"]
VALUES = [12, 18, 17, 29, 35, 41, 56, 73]
SOURCE = "source: example data"
PAL = PALETTES["mint"]
# ------------------------------------------------------------------------------------------------

BG = r"""
uniform vec3 uBg; uniform vec3 uA;
out vec4 o;
void main(){
  vec2 p = P();
  vec3 c = uBg * (1.15 - 0.35*length(p));
  vec2 g = abs(fract(p*10.)-.5)/fwidth(p*10.);
  c += vec3(0.02)*(1.-min(min(g.x,g.y),1.));
  c += uA*0.06*exp(-length(p-vec2(0.4,0.3))*2.);
  o = vec4(c,1);
}
"""


class Story(Scene):
    post = dict(bloom=0.6, threshold=0.9, grain=0.025, vignette=0.5)

    def render(self, eng, t, fb):
        T, S = eng.text, eng.shapes
        eng.fs(BG, fb, {"uBg": PAL["bg"], "uA": PAL["a"]}, clear=(0, 0, 0, 1))
        fg, a, b = PAL["fg"], PAL["a"], PAL["b"]
        vmax = max(VALUES)
        e0 = ease_out_expo(t / 0.6)
        T.put(TITLE, "sans", 0.026, fb, x=-0.78, y=0.40, align="left", tracking=0.25, color=rgba(fg, 0.7 * e0))
        # headline number counts up with the chart
        grow = ease_out_expo((t - 0.4) / 2.6)
        val = VALUES[-1] * grow
        T.put(f"{val:,.0f}{UNIT}", "display", 0.11, fb, x=-0.78, y=0.27, align="left", color=rgba(mul(a, 1.4)),
              anim=lambda g: dict(alpha=e0))
        growth = (VALUES[-1] / max(1e-9, VALUES[0]) - 1) * 100
        T.put(f"+{growth * grow:.0f}% since {LABELS[0]}", "mono", 0.02, fb, x=-0.78, y=0.17, align="left",
              color=rgba(mul(b, 1.3), ease_out_cubic((t - 1.0) / 0.5)))
        # bar chart
        x0, x1, y0, h = -0.78, 0.2, -0.36, 0.42
        n = len(VALUES)
        bw = (x1 - x0) / n
        S.line(x0, y0, x1, y0, 0.001, rgba(fg, 0.3))
        for i, v in enumerate(VALUES):
            gi = ease_out_elastic(clamp01((t - 0.8 - i * 0.09) / 1.0))
            hh = v / vmax * h * gi
            last = i == n - 1
            col = mix3(mul(b, 0.8), a, i / max(1, n - 1))
            S.box(x0 + bw * (i + 0.5), y0 + hh / 2, bw * 0.3, max(hh / 2, 1e-4), rgba(mul(col, 1.6 if last else 1.0)),
                  corner=0.006, glow=0.5 if last else 0.0, glowk=60)
        S.flush(fb)
        for i, (lab, v) in enumerate(zip(LABELS, VALUES)):
            gi = ease_out_cubic((t - 1.2 - i * 0.09) / 0.4)
            T.put(lab, "mono", 0.014, fb, x=x0 + bw * (i + 0.5), y=y0 - 0.03, color=rgba(fg, 0.55 * gi))
            T.put(f"{v}", "sans", 0.016, fb, x=x0 + bw * (i + 0.5), y=y0 + v / vmax * h + 0.025,
                  color=rgba(fg, 0.9 * clamp01((t - 1.6 - i * 0.09) / 0.3)))
        # line chart card (right) draws itself
        cx0, cx1, cy0, cy1 = 0.32, 0.8, -0.36, 0.06
        ca = ease_out_back(clamp01((t - 2.4) / 0.5), 1.4)
        if ca > 0:
            S.box((cx0 + cx1) / 2, (cy0 + cy1) / 2, (cx1 - cx0) / 2 * ca, (cy1 - cy0) / 2 * ca, (0.03, 0.05, 0.05, 0.85), corner=0.02)
            S.box((cx0 + cx1) / 2, (cy0 + cy1) / 2, (cx1 - cx0) / 2 * ca, (cy1 - cy0) / 2 * ca, rgba(fg, 0.12), corner=0.02, stroke=0.001)
            S.flush(fb)
            pr = ease_in_out_cubic((t - 2.9) / 2.2)
            m = 60
            pts = []
            for j in range(m):
                u = j / (m - 1)
                if u > pr: break
                f = u * (n - 1); i = int(min(n - 2, f)); fr = f - i
                v = lerp(VALUES[i], VALUES[i + 1], smooth(fr))
                pts.append((lerp(cx0 + 0.03, cx1 - 0.03, u), lerp(cy0 + 0.04, cy1 - 0.07, v / vmax)))
            for (px, py) in pts:
                S.box(px, (py + cy0 + 0.04) / 2, (cx1 - cx0 - 0.06) / m / 2 + 0.0005, (py - cy0 - 0.04) / 2, rgba(a, 0.12))
            if len(pts) > 1:
                S.polyline(pts, 0.0025, rgba(mul(a, 1.8)))
                S.circle(*pts[-1], 0.007 * (1 + 0.5 * eng.common["uKick"]), rgba(mul(a, 3)), glow=0.8, glowk=90)
            S.flush(fb)
            T.put("TREND", "sans", 0.014, fb, x=cx0 + 0.03, y=cy1 - 0.03, align="left", tracking=0.3, color=rgba(fg, 0.6 * ca))
        T.put(SOURCE, "mono", 0.012, fb, x=0.8, y=-0.44, align="right", color=rgba(fg, 0.35 * e0))


proj = Project("data_story", preset="16:9", duration=10.0, bpm=110)
proj.add(Story(), 0, 10.0)
proj.music_score(key="C major", blips=[0.8 + i * 0.09 for i in range(len(VALUES))])

if __name__ == "__main__":
    proj.cli()
