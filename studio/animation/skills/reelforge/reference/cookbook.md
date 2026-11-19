# ReelForge cookbook: copy-paste recipes

The snippets below live inside a `Scene.render(self, eng, t, fb)` unless noted. `S = eng.shapes`, `T = eng.text`.

## Backgrounds
```glsl
// soft moving colour blobs (always looks expensive)
out vec4 o; uniform vec3 uA; uniform vec3 uB; uniform vec3 uBg;
void main(){ vec2 p = P(); float t = uTime;
  vec3 c = uBg;
  c += uA*0.5*exp(-length(p-vec2(-.5+.1*sin(t*.5), .25))*2.6);
  c += uB*0.5*exp(-length(p-vec2(.6, -.2+.1*cos(t*.4)))*2.4);
  c *= 0.9 + 0.1*fbm(p*3. + t*.1);
  o = vec4(c,1); }
```
```glsl
// retro perspective grid floor
float y = p.y + .22;
if(y < 0.){ float z = .25/(-y); vec2 fp = vec2(p.x*z, z + uTime*1.2);
  vec2 g = abs(fract(fp*2.)-.5)/fwidth(fp*2.); c += hex(0x2f6bff)*(1.-min(min(g.x,g.y),1.))*.35*exp(-z*.35); }
```
Other quick textures:
- **Paper:** `c *= .96 + .04*vnoise(FC()*.9);`
- **Dot grid:** `fill(length(fract(p*20.)-.5)-.05)`

## Glow / neon
Use HDR colours. `mul(PAL["a"], 3.0)` blooms, so no blur code is needed. For a glow line:
`S.line(x0,y,x1,y, 0.002, rgba(mul(c, 3)), glow=0.6, glowk=250)`. Glowing text:
`T.put(..., glow=6.0)`.

## Staggered text entrances (the classics)
```python
e = lambda g, d=0.5: ease_out_expo((t - 0.2 - g.i*0.04) / d)
T.put("HEADLINE", "display", 0.15, fb, anim=lambda g: dict(alpha=e(g), dy=(1-e(g))*-0.06))            # rise
T.put("SPACING",  "display", 0.15, fb, anim=lambda g: dict(dx=g.cx*lerp(-0.5, 0.2, e(g, .6))))         # track out
T.put("POP",      "display", 0.15, fb, anim=lambda g: dict(s=ease_out_back(clamp01((t-g.i*.05)/.3), 2.5)))
T.put("TYPE",     "mono", 0.03, fb, anim=lambda g: None if g.i > (t-0.3)/0.05 else {})                  # typewriter
T.put("OUTLINE",  "display", 0.15, fb, outline=2.5, color=rgba(mul(PAL["a"], 2)))
```
To exit, use `q = ease_in_cubic((t - t_out - g.i*0.03)/0.35)`, then `dy += q*1.2`, `alpha *= 1-q`.
To size long or variable strings, use `size = T.fit(s, "display", 0.2, eng.aspect*0.85)`.

## Counters & numbers
`T.put(f"{int(4320*ease_out_expo((t-1)/1.6)):,}", "mono", 0.07, fb)`. Mono digits don't jitter while counting.

## Charts
- **Bars:** grow each bar with `ease_out_elastic(clamp01((t - t0 - i*0.06)/0.9))`.
- **Lines:** draw progressively by taking only the points with `u <= progress`, then `S.polyline(pts, 0.0025, col)`.
- **Area fill:** a thin `S.box` per sample from the baseline up to the curve, alpha 0.12.
- **Donut:** 90 short `S.line` segments around a circle, coloured by whether `u <= progress`.

## SDF shape morphing (liquid / blobby)
```glsl
float d = mix(sdCircle(p,.2), sdRBox(p, vec2(.17), .06), uMorph);   // any two SDFs
d = smin(d, length(p - orbit) - .04, 0.08);                           // merging satellites
// 2.5D shading: height from the SDF, normal from its gradient
#define H(q) (1. - exp(-max(-scene(q),0.)/0.055))
```
Drive `uMorph` with `ease_out_elastic`. Avoid a pure `sqrt(-d)` dome, because it creases along the medial axis.

## Raymarching (3D in one shader)
Skeleton, taken from `templates/neon_loop.py`:
- `map(p)` returns `vec2(dist, material)`.
- Domain repetition: `q.z = mod(q.z, cell) - cell*.5`.
- Normals come from central differences, and fog is `mix(col, fogCol, 1-exp(-t*.035))`.
- Emissive glow accumulates while marching: `glow += exp(-dEmissive*9.)*0.016*color`.
- One reflection bounce for floors uses 48 steps.

Limits: at most about 110 primary steps. Use `uKick` to pulse the emissives. If the scene has
internal camera cuts, list them in `Scene.cuts`.

## GPU particles (hundreds of thousands, stateless)
```python
VS = """#version 330
uniform float uT; uniform vec2 uRes; uniform vec2 uJitter;
out vec3 vCol;
uint pcg(uint v){ uint s=v*747796405u+2891336453u; uint w=((s>>((s>>28u)+4u))^s)*277803737u; return (w>>22u)^w; }
float H(uint c){ return float(pcg(uint(gl_VertexID)*16u+c))/4294967295.0; }   // integer hash (sin-hash breaks at big ids)
void main(){
  vec3 p = vec3(H(0u), H(1u), H(2u)) - .5;                                     // start
  float a = uT*(0.3+H(3u)); p.xz = mat2(cos(a),-sin(a),sin(a),cos(a))*p.xz;    // any pure f(t)
  vec3 v = p - vec3(0,0,2.2); vec2 sp = v.xy/(-v.z)*2.2;                        // perspective
  gl_Position = vec4(sp/vec2(.5*uRes.x/uRes.y,.5) + uJitter*2./uRes, 0, 1);
  gl_PointSize = 2.5*uRes.y/1080.; vCol = mix(vec3(1,.4,.1), vec3(.3,.5,1), H(4u)); }"""
FS = """#version 330
in vec3 vCol; out vec4 o;
void main(){ vec2 c=gl_PointCoord*2.-1.; float a=exp(-dot(c,c)*3.)*.25; o=vec4(vCol*a,a); }"""

class Particles(Scene):
    def setup(self, eng):
        self.prog = eng.ctx.program(vertex_shader=VS, fragment_shader=FS)
        self.vao = eng.ctx.vertex_array(self.prog, [])
    def render(self, eng, t, fb):
        import moderngl
        eng.fs(BG, fb, clear=(0,0,0,1))
        self.prog["uT"] = t; self.prog["uRes"] = (fb.width, fb.height); self.prog["uJitter"] = eng.jitter
        fb.use(); eng.ctx.enable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
        eng.ctx.blend_func = moderngl.ONE, moderngl.ONE
        self.vao.render(moderngl.POINTS, vertices=262144)
        eng.ctx.disable(moderngl.BLEND | moderngl.PROGRAM_POINT_SIZE)
```
To make particles form a word, render it with PIL, sample 262k pixel positions into an RGBA32F texture
in `setup`, and `texelFetch` it by `gl_VertexID`. Then `mix(start, target, easeInOut(t))`.

## Transitions & montage
- Between shots: `proj.add(scene, 8, 16, transition=("iris", 0.8))`, centred on t=8.
- For a hard cut, set no transition, then optionally `proj.flash(8, 0.6)` and add `Scene.shake`.
- A beat-cut montage reuses earlier scenes at interesting local times:
  `for i,(sc,off) in enumerate(picks): proj.add(sc, T0+i*0.5, T0+(i+1)*0.5, offset=off)`.

## Camera shake & impacts
`def shake(self, t): return 12*math.exp(-(t-4.0)*6) if t >= 4.0 else 0`, plus `proj.flash(t0, 0.8)` and
`impacts=[t0]` in `music_score`.

## Lower third
```python
e = ease_out_expo((t-0.3)/0.6); q = ease_in_cubic((t-4)/0.4)
S.box(-0.55, -0.33, 0.28*e*(1-q), 0.045, rgba(PAL["a"]), corner=0.006); S.flush(fb)
T.put("JANE DOE", "display", 0.035, fb, x=-0.8, y=-0.325, align="left", color=rgba(PAL["bg"]), anim=lambda g: dict(alpha=e*(1-q)))
T.put("Motion Designer", "sans-light", 0.022, fb, x=-0.8, y=-0.4, align="left", color=rgba(PAL["fg"], e*(1-q)))
```

## Seamless loops
- Construct the project with `Project(..., loop=True)`.
- Make every motion periodic in the loop length L: use `sin(TAU*t/L)`, and translate by an exact
  multiple of the repetition cell per loop.
- Pick the BPM so that L is a whole number of bars.
- Verify by comparing `stills 0` with `stills <L-0.001>`.

## Audio-reactive visualizer (your own song)
`proj.music_file("song.mp3")`, then inside scenes read `self.project.track.onset(t)`, which is 0..1
loudness onsets, or `eng.common["uKick"]`, which follows the beats. Drive scale, bloom and camera speed from these.
