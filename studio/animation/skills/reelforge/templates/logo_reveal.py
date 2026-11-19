"""Logo / name reveal - ring draw-on, particle dust, staggered type, tagline (16:9, 6 s). Great intro/outro sting."""
import os, sys, math
SKILL_DIR = None  # set by `rf.py new`; otherwise auto-detected below
for _d in (SKILL_DIR, os.environ.get("REELFORGE_HOME"), os.path.join(os.path.expanduser("~"), ".claude", "skills", "reelforge"),
           os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
    if _d and os.path.isdir(os.path.join(_d, "reelforge")):
        sys.path.insert(0, _d); break
from reelforge import *

# ---------------------------------------------------------------- edit me
NAME = "NORTHWIND"
TAGLINE = "STUDIO  ·  MOTION  ·  SOUND"
PAL = PALETTES["ember"]
# -------------------------------------------------------------------------

BG = r"""
uniform float uRing; uniform float uDot; uniform vec3 uA; uniform vec3 uFg; uniform vec3 uBg;
out vec4 o;
void main(){
  vec2 p = P(); float t = uTime;
  vec3 c = uBg * (1.2 - 0.4*length(p));
  c += uA * 0.25 * exp(-length(p - vec2(0., .05)) * 2.2) * sat(t);
  for(int i=0;i<3;i++){                                    // drifting dust, 3 parallax layers
    float s = 30. + float(i)*25.;
    vec2 q = p*s + vec2(0., t*(0.5+float(i)*0.4)) + float(i)*13.;
    vec2 id = floor(q); vec2 f = fract(q)-.5; vec2 r = hash22(id)-.5;
    c += vec3(1.,.8,.6)*0.4*smoothstep(0.06,0.,length(f-r*.7))*step(.86,hash21(id+3.))*(.5+.5*sin(t*3.+hash21(id)*6.));
  }
  vec2 m = p - vec2(0., 0.19);
  float a01 = fract(-atan(m.x, m.y)/TAU + 1.0);
  float ring = abs(length(m) - 0.06) - 0.006;
  c = mix(c, uFg*1.4, fill(a01 < uRing ? ring : 1e3));
  float d = length(m) - 0.024*uDot;
  c = mix(c, uA*2.5, fill(d)); c += uA*uDot*0.5*exp(-max(d,0.)*60.);
  float oa = t*2.2; float od = length(m - vec2(sin(oa), cos(oa))*0.09) - 0.006*uDot;
  c = mix(c, uA*3.0, fill(od)*sat(uRing*1.5-.5));
  o = vec4(c, 1);
}
"""


class Reveal(Scene):
    post = dict(bloom=0.8, threshold=0.8, grain=0.03, vignette=0.7)

    def render(self, eng, t, fb):
        eng.fs(BG, fb, {"uRing": ease_in_out_cubic((t - 0.2) / 1.0), "uDot": ease_out_back(clamp01((t - 1.0) / 0.4), 3.0),
                        "uA": PAL["a"], "uFg": PAL["fg"], "uBg": PAL["bg"]}, clear=(0, 0, 0, 1))
        size = eng.text.fit(NAME, "display", 0.13, eng.aspect * 0.8, tracking=0.06)
        eng.text.put(NAME, "display", size, fb, y=0.0, tracking=0.06, color=rgba(mul(PAL["fg"], 1.15)), anim=lambda g: dict(
            alpha=ease_out_cubic((t - 0.6 - g.i * 0.06) / 0.5),
            dy=(1 - ease_out_expo((t - 0.6 - g.i * 0.06) / 0.8)) * -0.07,
            s=lerp(1.12, 1.0, ease_out_expo((t - 0.6 - g.i * 0.06) / 0.8)) * (1 + 0.01 * t)))
        e = ease_out_expo((t - 1.4) / 0.9)
        n = len(TAGLINE)
        eng.text.put(TAGLINE, "sans", 0.022, fb, y=-0.12, tracking=0.45, color=rgba(mul(PAL["a"], 1.6)),
                     anim=lambda g: dict(alpha=clamp01(e * 2 - abs(g.i - n / 2) * 0.04), dx=g.cx * 0.2 * (1 - e)))
        L = 0.28 * ease_out_expo((t - 1.2) / 0.8)
        eng.shapes.line(-L, -0.075, L, -0.075, 0.001, rgba(mul(PAL["fg"], 0.7)))
        eng.shapes.flush(fb)


proj = Project("logo_reveal", preset="16:9", duration=6.0, bpm=100)
proj.add(Reveal(), 0, 6.0)
proj.music_score(key="D minor", sections=[("intro", 0, 1), ("break", 1, 3)], impacts=[1.0])
proj.flash(1.0, 0.5)

if __name__ == "__main__":
    proj.cli()
