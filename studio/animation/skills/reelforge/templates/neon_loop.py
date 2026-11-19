"""Seamless 3D neon tunnel loop - raymarched SDF, reflections, beat pulses; first frame == last frame (16:9, 8 s)."""
import os, sys, math
SKILL_DIR = None  # set by `rf.py new`; otherwise auto-detected below
for _d in (SKILL_DIR, os.environ.get("REELFORGE_HOME"), os.path.join(os.path.expanduser("~"), ".claude", "skills", "reelforge"),
           os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
    if _d and os.path.isdir(os.path.join(_d, "reelforge")):
        sys.path.insert(0, _d); break
from reelforge import *

# ---------------------------------------------------------------- edit me
LOOP = 8.0            # seconds; everything below is periodic in LOOP -> perfect loop
TITLE = "INFINITE"
PAL = PALETTES["neon"]
# -------------------------------------------------------------------------

TUNNEL = r"""
uniform float uLoop; uniform vec3 uA; uniform vec3 uB;
out vec4 o;
float sdBox3(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
float gEm;
vec2 map(vec3 p){
  float w = TAU/uLoop;
  vec3 q = p; q.xy *= rot(0.35*sin(q.z*TAU/8.8) + sin(uTime*w)*0.15);   // twist periodic over the 4-cell travel
  float cell = 2.2;
  float id = floor(q.z/cell);
  q.z = mod(q.z, cell) - cell*.5;
  float arch = max(sdBox3(q, vec3(3.2,2.0,0.28)), -sdBox3(q, vec3(2.6,1.5,1.0))) - 0.02;
  vec2 res = vec2(arch, 1.);
  vec3 s = q; s.x = abs(s.x) - 2.62;
  float em = min(sdBox3(s, vec3(0.03,1.5,0.04)), sdBox3(q - vec3(0.,1.52,0.), vec3(2.6,0.03,0.04)));
  if(em < res.x) res = vec2(em, 2. + step(0.5, fract(id*0.5)));
  gEm = min(gEm, em);
  float fl = p.y + 1.5;
  if(fl < res.x) res = vec2(fl, 0.);
  return res;
}
vec3 nrm(vec3 p){ vec2 e=vec2(0.0015,0); return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x, map(p+e.yxy).x-map(p-e.yxy).x, map(p+e.yyx).x-map(p-e.yyx).x)); }
vec3 emc(float m){ return (m < 2.5 ? uA : uB) * 5.0 * (1.0 + 1.2*uKick); }
void main(){
  vec2 p = P();
  float w = TAU/uLoop;
  float speed = 2.2*4.0/uLoop;                           // travel exactly 4 cells (8.8 units) per loop
  vec3 ro = vec3(sin(uTime*w)*0.5, -0.2 + sin(uTime*w*2.)*0.15, uTime*speed);
  vec3 ta = ro + vec3(sin(uTime*w)*0.3, 0., 4.);
  float roll = sin(uTime*w)*0.15;
  vec3 fw = normalize(ta-ro), up = vec3(sin(roll), cos(roll), 0.);
  vec3 rt = normalize(cross(up, fw)); up = cross(fw, rt);
  vec3 rd = normalize(fw*1.6 + rt*p.x + up*p.y);
  float t = 0.02, mat = -1.; vec3 glowc = vec3(0);
  for(int i=0;i<110;i++){
    gEm = 1e9; vec3 q = ro + rd*t; vec2 h = map(q);
    glowc += exp(-gEm*9.)*0.016*mix(uA, uB, step(0.5, fract(floor(q.z/2.2)*0.5)))*3.;
    if(h.x < 0.001*t){ mat = h.y; break; }
    t += h.x; if(t > 60.) break;
  }
  vec3 col = vec3(0.01, 0.01, 0.02);
  if(mat >= 0.){
    vec3 hp = ro + rd*t, n = nrm(hp);
    if(mat >= 1.5) col = emc(mat);
    else if(mat < 0.5){
      vec2 g = abs(fract(hp.xz*0.5)-.5);
      col = vec3(0.012) + uB*smoothstep(0.02,0.,min(g.x,g.y))*0.3*exp(-t*0.08);
      vec3 rr = reflect(rd, n); float t2 = 0.02, m2 = -1.;
      for(int i=0;i<48;i++){ gEm=1e9; vec2 h = map(hp + n*0.01 + rr*t2); if(h.x < 0.002){ m2 = h.y; break; } t2 += h.x; if(t2>30.) break; }
      if(m2 >= 1.5) col += emc(m2)*0.4*exp(-t2*0.1);
    } else {
      float fr = pow(1.-sat(dot(n,-rd)), 5.);
      col = vec3(0.02)*(0.3 + sat(dot(n, normalize(vec3(.4,.8,-.3))))) + fr*0.3;
    }
    col = mix(col, vec3(0.01,0.01,0.02), 1.0 - exp(-t*0.035));
  }
  o = vec4(col + glowc, 1);
}
"""


class Tunnel(Scene):
    post = dict(bloom=0.9, threshold=1.0, grain=0.03, vignette=0.7, ca=0.004)

    def render(self, eng, t, fb):
        eng.fs(TUNNEL, fb, {"uLoop": LOOP, "uA": PAL["a"], "uB": PAL["b"], "uTime": t % LOOP}, clear=(0, 0, 0, 1))
        eng.text.put(TITLE, "display", 0.1, fb, tracking=0.35, color=rgba(mul(PAL["fg"], 1.2)), outline=2.0,
                     anim=lambda g: dict(dy=0.012 * math.sin(2 * math.pi * t / LOOP * 2 + g.i * 0.7)))


BPM = 120          # 8 s at 120 BPM = 4 bars, so the music loops too
proj = Project("neon_loop", preset="16:9", duration=LOOP, bpm=BPM, loop=True)
proj.add(Tunnel(), 0, LOOP)
proj.music_score(key="E minor", sections=[("drop", 0, 4)])

if __name__ == "__main__":
    proj.cli()
