# ReelForge API

```python
import os, sys
sys.path.insert(0, "<skill dir>")          # templates do this for you (see their header)
from reelforge import *                     # Project, Scene, PRESETS, PALETTES, easing, colour helpers, audio
```

## Project

```python
proj = Project(name, preset="16:9", size=None, fps=60, duration=10.0, bpm=120,
               subframes=8, shutter=0.6, post=None, out_dir=None, loop=False)
```
| arg | meaning |
|---|---|
| `preset` | `16:9` `1080p` `4k` `720p` `9:16` `shorts` `reels` `tiktok` `1:1` `square` `4:5` `portrait` |
| `size` | explicit `(W, H)` instead of a preset |
| `subframes` | motion-blur samples per frame (8 = smooth; 1 = off) |
| `shutter` | fraction of a frame the shutter is open (0.5 = 180 degrees film look) |
| `post` | global post defaults, e.g. `dict(bloom=0.8, grain=0.04)` |
| `loop` | seamless loop: no fade in/out on picture or music |

Methods:
- `proj.add(scene, start, end, transition=None, offset=0.0)`. `transition=(kind, seconds)` is centred on
  `start`; kinds are `fade` `iris` `push` `glitch` `zoom` `wipe`. For `push`, the third element is a
  direction: `("push", 0.5, (1, 0))`. `offset` reuses a scene starting at a later local time, which is
  how you build montages from earlier shots.
- `proj.flash(t, amount)` adds an additive white flash that decays over about 0.1 s. Use it for impacts.
- `proj.music_score(key="F minor", sections=None, impacts=(), whooshes=None, blips=(), seed=7)`
  - `sections`: `[(energy, first_bar, end_bar), ...]`, where energy is one of `intro` `build` `groove` `drop` `break` `outro`.
  - `whooshes` defaults to every transition time.
  - `blips` are UI ticks, e.g. for counters and pop-ins.
- `proj.music_file(path, bpm_hint=None)` uses your own track: tempo, beats and downbeat are detected.
- `proj.beat(n)` and `proj.bar(n)` return the time of beat or bar n, from the score or the detected grid.
  `proj.track.quantize(t, div=2)` snaps a time to the nearest half-beat.
- `proj.cli()` provides the commands below.

## CLI (the project file is the CLI)

```
python my_video.py stills 0.5 2 4.25 [--full]     # PNGs -> out/<name>/stills/   (half-res by default)
python my_video.py contact --every 0.5 [--range a b]
python my_video.py check                          # black / blown-out / frozen + audio levels
python my_video.py preview [--range a b]          # half-res 30 fps draft with audio
python my_video.py render [--quality draft|high|master] [--chunked] [--range a b] [--out f.mp4]
python my_video.py gif [--range a b] [--width 640] [--fps 15]
python my_video.py audio                          # loudness report + spectrogram with shot marks
```
On Windows Optimus laptops the CLI re-launches itself with `SHIM_MCCOMPAT=0x800000001`, so OpenGL
runs on the NVIDIA GPU instead of the iGPU.

## Scene

```python
class MyScene(Scene):
    post = dict(bloom=0.8, threshold=0.9, ca=0.003, vignette=0.6, grain=0.03, exposure=1.0, sat=1.0)
    cuts = [2.0]                         # internal hard cuts (local s), so motion blur never straddles them
    def setup(self, eng): ...            # optional, called once: build textures/programs here
    def shake(self, t): return 0.0       # camera shake in pixels at local time t
    def render(self, eng, t, fb): ...    # draw the frame for local time t into framebuffer fb
```
`self.project` is available inside scenes (`self.project.track.spb` = seconds per beat).

## Engine (`eng`)

- `eng.fs(frag_src, fb, uniforms={}, textures={}, blend=None|"add"|"over", clear=(r,g,b,a))`
  runs a fullscreen GLSL fragment shader. Write only the body: declare `out vec4 o;` and `void main(){...}`.
  The header and the library below are prepended for you.
- `eng.common["uKick"]`, `["uSnare"]`, `["uBeat"]` and `["uTime"]` are the current values, also available in Python.
- `eng.W`, `eng.H`, `eng.aspect`, `eng.ctx` (raw moderngl context, for custom programs).
- `eng.fbA`, `fbB` and `fbC` are HDR scratch framebuffers. Don't use the one you were handed as `fb`.

### Uniforms that every fullscreen shader gets
`uRes` (px), `uTime` (global s), `uKick`, `uSnare` (0..1 decaying envelopes), `uBeat` (beats since start),
`uJitter`. Pass your own uniforms via `uniforms={"uFoo": 1.0, "uCol": (1, .5, 0)}`.

### GLSL library (always available)
`P()` gives centred coordinates (height 1, y up); `FC()` gives the jittered fragment coordinate.
- **Constants and utilities:** `PI`, `TAU`, `sat(x)`, `rot(a)` (a mat2), `hex(0xRRGGBB)` (linear colour), `srgb2lin`, `pal(t,a,b,c,d)` (cosine palette)
- **Noise:** `hash11` `hash21` `hash22` `hash33` `vnoise(vec2)` `vnoise3` `fbm(vec2)` `fbm3`
- **Easing:** `easeOutCubic` `easeInOutCubic` `easeOutExpo` `easeInOutExpo` `easeOutBack` `easeOutElastic`
- **2D SDFs:** `sdCircle` `sdBox` `sdRBox(p,b,r)` `sdSeg(p,a,b)` `sdRing(p,r,w)` `smin(a,b,k)` `smax`
- **Anti-aliased rendering:** `fill(d)` gives AA coverage, `stroke(d,w)`, `glow(d,k)` gives exp falloff

## Text (`eng.text`)

Built-in fonts, all SIL OFL:
- `display`: Archivo Black, heavy headlines
- `sans`: Space Grotesk Bold
- `sans-light`: Space Grotesk Light
- `mono`: JetBrains Mono Bold
- `serif`: Instrument Serif Italic

Add your own with `eng.text.add_font("brand", "Brand.ttf", variation="Bold")`. Atlases are cached in `~/.cache/reelforge`.

```python
eng.text.put(s, font, size, fb, x=0, y=0, color=(1,1,1,1), align="center", tracking=0.0, anim=None,
             outline=0.0, glow=0.0, dilate=0.0, skew=0.0)
size = eng.text.fit(s, font, max_size, max_width)          # shrink to fit
gl = eng.text.layout(s, font, size, tracking, align, x, y)  # list of Glyph; eng.text.draw(gl, font, fb, ...)
w = eng.text.width(s, font, size, tracking)
```
`anim(g)` is called per glyph. The glyph exposes `g.i`, `g.n`, `g.cx`, `g.cy`, `g.gw` and `g.gh`.
Return `None` to hide the glyph, or a dict with any of these keys:
- position and transform: `dx`, `dy`, `s`, `sx`, `sy`, `rot`, `skew`
- pivot: `ax`, `ay` (offset from the glyph centre)
- look: `alpha`, `color`, `outline` (px, 0 = fill), `glow` (px), `dilate` (px, bolder)

## Shapes (`eng.shapes`), queued and instanced; call `flush(fb)`
```python
S.box(x, y, half_w, half_h, color, corner=0, rot=0, stroke=0, glow=0, glowk=40)
S.circle(x, y, r, color, stroke=0, glow=0, glowk=40)
S.line(x0, y0, x1, y1, width, color, glow=0)
S.polyline(pts, width, color)
S.flush(fb, blend="over"|"add")
```
Colours are RGBA with linear RGB. `rgba(c, a)`, `mul(c, k)` and `mix3(a, b, t)` help build them.

## Easing & helpers (Python)
- **Easing:** `ease_out_cubic` `ease_in_cubic` `ease_in_out_cubic` `ease_out_expo` `ease_in_expo` `ease_in_out_expo`
  `ease_out_back(x, c=1.70158)` `ease_in_back` `ease_out_elastic` `ease_in_out_sine` `spring(t, freq, damp)`
- **Helpers:** `clamp01` `remap(t,a,b)` `lerp` `smooth` `stagger(i,n,total)` `pingpong` `h11(x)` (deterministic hash)
- **Colour:** `lin(0xRRGGBB)`
- **Palettes:** `PALETTES[name]` gives `bg`, `fg`, `a`, `b`, `c`. Names: `ember` `neon` `paper` `mint` `mono` `sunset`.

## Audio module (`reelforge.audio`)
- `score(path, duration, bpm, key, sections, impacts, whooshes, blips, seed, fade=True)` returns a `Track`.
- `from_file(path, bpm_hint=None, out_wav=None, duration=None)` returns a `Track`, with beats detected by dynamic-programming beat tracking.
- `Track` fields and methods: `.bpm`, `.beats`, `.kicks`, `.beat(n)`, `.bar(n)`, `.quantize(t, div)`, `.kick_env(t)`,
  and `.onset(t)` (the loudness envelope of your own song, for audio-reactive visuals).
- `report(path, spectrogram_png=None, marks=())` returns peak, clipping, loudness per second and silence.
- The instruments are usable directly: `kick()` `snare()` `clap()` `hat()` `crash()` `impact()` `riser(d)` `whoosh()`
  `blip()` `pluck(midi)` `bell(midi)` `supersaw(midi, dur)` `bass_note(midi, dur)`.
