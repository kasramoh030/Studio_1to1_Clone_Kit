"""SDF glyph atlases + instanced text, and instanced SDF vector shapes.

Coordinate system everywhere: origin at frame centre, y up, frame height = 1.0,
so x spans [-aspect/2, +aspect/2]  (16:9 -> +-0.889,  9:16 -> +-0.281).
"""
import os, math
import numpy as np
import moderngl
from PIL import Image, ImageFont, ImageDraw
from scipy.ndimage import distance_transform_edt
from . import glsl

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "reelforge")
BUILTIN_FONTS = {                     # name: (file, atlas px, variation)   all SIL OFL 1.1
    "display":    ("ArchivoBlack-Regular.ttf", 176, None),
    "sans":       ("SpaceGrotesk[wght].ttf", 160, "Bold"),
    "sans-light": ("SpaceGrotesk[wght].ttf", 128, "Light"),
    "mono":       ("JetBrainsMono[wght].ttf", 128, "Bold"),
    "serif":      ("InstrumentSerif-Italic.ttf", 160, None),
}

CHARSET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
           " .,:;!?'\"-_/\\()[]{}<>+=*&%#@$|~^×·•—–→←↑↓°")


class GlyphAtlas:
    def __init__(self, ctx, name, path, px=160, spread=18, variation=None):
        self.name, self.px, self.spread = name, px, spread
        os.makedirs(CACHE, exist_ok=True)
        import hashlib
        st = os.stat(path)
        key = hashlib.sha1(repr((os.path.abspath(path), st.st_size, int(st.st_mtime), variation, px, spread, CHARSET)).encode()).hexdigest()[:10]
        cache = os.path.join(CACHE, f"atlas_{name}_{key}.npz")
        if os.path.exists(cache):
            z = np.load(cache, allow_pickle=True)
            img, meta = z["img"], z["meta"].item()
        else:
            img, meta = self._build(path, px, spread, variation)
            np.savez_compressed(cache, img=img, meta=np.array(meta, dtype=object))
        self.meta = meta
        self.ascent = meta["_ascent"]; self.capH = meta["_cap"]
        h, w = img.shape
        self.tex = ctx.texture((w, h), 1, img.astype("f4").tobytes(), dtype="f4")
        self.tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.tex.repeat_x = self.tex.repeat_y = False
        self.W, self.H = w, h

    def _build(self, path, px, spread, variation):
        font = ImageFont.truetype(path, px)
        if variation:
            font.set_variation_by_name(variation)
        pad = spread + 2
        glyphs = []
        for ch in CHARSET:
            adv = font.getlength(ch)
            if ch == " ":
                glyphs.append((ch, None, 0, 0, adv)); continue
            l, t, r, b = font.getbbox(ch, anchor="ls")
            gw, gh = r - l + 2 * pad, b - t + 2 * pad
            im = Image.new("L", (gw, gh), 0)
            ImageDraw.Draw(im).text((pad - l, pad - t), ch, font=font, fill=255, anchor="ls")
            m = np.asarray(im) > 127
            din = distance_transform_edt(m)
            dout = distance_transform_edt(~m)
            sd = np.clip(din - dout, -spread, spread).astype("f4")
            glyphs.append((ch, sd, l - pad, t - pad, adv))
        # shelf pack
        AW = 2048; x = y = rowh = 0; placed = {}
        for ch, sd, ox, oy, adv in glyphs:
            if sd is None:
                placed[ch] = dict(adv=adv, uv=None); continue
            gh, gw = sd.shape
            if x + gw > AW:
                x = 0; y += rowh + 1; rowh = 0
            placed[ch] = dict(adv=adv, x=x, y=y, w=gw, h=gh, ox=ox, oy=oy, sd=sd)
            x += gw + 1; rowh = max(rowh, gh)
        AH = y + rowh + 1
        img = np.full((AH, AW), -spread, "f4")
        meta = {}
        for ch, g in placed.items():
            if g.get("uv", 1) is None:
                meta[ch] = dict(adv=g["adv"], space=True); continue
            img[g["y"]:g["y"] + g["h"], g["x"]:g["x"] + g["w"]] = g["sd"]
            meta[ch] = dict(adv=g["adv"], w=g["w"], h=g["h"], ox=g["ox"], oy=g["oy"],
                            uv=(g["x"] / AW, g["y"] / AH, (g["x"] + g["w"]) / AW, (g["y"] + g["h"]) / AH))
        l, t, r, b = font.getbbox("H", anchor="ls")
        meta["_cap"] = -t
        meta["_ascent"] = font.getmetrics()[0]
        return img, meta


class Glyph:
    __slots__ = ("ch", "x", "y", "size", "i", "n", "w", "cx", "cy", "gw", "gh", "uv")


class TextRenderer:
    """Instanced SDF glyph quads.  Coordinates: scene units (height = 1, y up, origin centre)."""
    FMT = "2f 2f 4f 1f 4f 4f 2f 2f/i"
    ATTRS = ["iPos", "iSize", "iUV", "iRot", "iColor", "iStyle", "iScale", "iAnchor"]
    NF = 2 + 2 + 4 + 1 + 4 + 4 + 2 + 2

    def __init__(self, eng):
        self.eng = eng
        ctx = eng.ctx
        self.prog = ctx.program(vertex_shader=glsl.VS_GLYPH, fragment_shader=glsl.FS_GLYPH)
        self.maxn = 8192
        self.buf = ctx.buffer(reserve=self.maxn * self.NF * 4)
        self.vao = ctx.vertex_array(self.prog, [(self.buf, self.FMT, *self.ATTRS)])
        self.atlases = {}
        self._pending = {n: (os.path.join(FONT_DIR, f), px, v) for n, (f, px, v) in BUILTIN_FONTS.items()}

    def add_font(self, name, path, px=160, variation=None):
        """Register any .ttf/.otf (e.g. a brand font).  Built-ins: display, sans, sans-light, mono, serif."""
        self._pending[name] = (path, px, variation)
        self.atlases.pop(name, None)

    def atlas(self, name):
        if name not in self.atlases:
            if name not in self._pending:
                raise KeyError(f"unknown font '{name}'. Built-ins: {sorted(self._pending)}")
            path, px, var = self._pending[name]
            self.atlases[name] = GlyphAtlas(self.eng.ctx, name, path, px=px, variation=var)
        return self.atlases[name]

    def layout(self, s, font, size, tracking=0.0, align="center", x=0.0, y=0.0, valign="cap"):
        """Return list of Glyph with positions of glyph quad centres.  size = cap height in scene units."""
        A = self.atlas(font)
        k = size / A.capH
        pen = 0.0
        items = []
        for ch in s:
            g = A.meta.get(ch) or A.meta["?"]
            if not g.get("space"):
                items.append((ch, pen, g))
            pen += g["adv"] * k + tracking * size
        total = pen - tracking * size
        x0 = x - (total * 0.5 if align == "center" else (total if align == "right" else 0.0))
        base = y - (size * 0.5 if valign == "cap" else 0.0)       # baseline so caps are v-centred on y
        out = []
        n = len(items)
        for i, (ch, pen, g) in enumerate(items):
            gl = Glyph()
            gl.ch, gl.i, gl.n, gl.size = ch, i, n, size
            gw, gh = g["w"] * k, g["h"] * k
            gl.gw, gl.gh = gw, gh
            gl.cx = x0 + pen + (g["ox"] + g["w"] / 2) * k
            gl.cy = base - (g["oy"] + g["h"] / 2) * k
            gl.x, gl.y = gl.cx, gl.cy
            gl.uv = g["uv"]; gl.w = total
            out.append(gl)
        return out

    def put(self, s, font, size, target, x=0.0, y=0.0, color=(1, 1, 1, 1), align="center", tracking=0.0,
            anim=None, **style):
        """layout + draw in one call.  anim(g) gets a Glyph (g.i, g.n, g.cx, g.cy...) and returns
        dict(dx, dy, s, sx, sy, rot, alpha, color, outline, glow, dilate, skew) or None to hide it."""
        gl = self.layout(s, font, size, tracking=tracking, align=align, x=x, y=y)
        self.draw(gl, font, target, color=color, anim=anim, **style)
        return gl

    def fit(self, s, font, max_size, max_width, tracking=0.0):
        """largest size <= max_size whose rendered width fits max_width (use for long/dynamic text)"""
        w = self.width(s, font, max_size, tracking)
        return max_size if w <= max_width else max_size * max_width / w

    def width(self, s, font, size, tracking=0.0):
        A = self.atlas(font); k = size / A.capH
        return sum((A.meta.get(c) or A.meta["?"])["adv"] * k + tracking * size for c in s) - tracking * size

    def draw(self, glyphs, font, target, color=(1, 1, 1, 1), outline=0.0, glow=0.0, dilate=0.0, skew=0.0,
             anim=None, blend="over"):
        """anim(g) -> dict(dx,dy,rot,sx,sy,alpha,color,outline,glow,dilate,skew,ax,ay) or None (skip)."""
        if not glyphs:
            return
        rows = []
        for g in glyphs:
            p = {} if anim is None else anim(g)
            if p is None:
                continue
            a = p.get("alpha", 1.0)
            if a <= 0.001:
                continue
            col = p.get("color", color)
            s = p.get("s", 1.0)
            rows.append((g.cx + p.get("dx", 0.0), g.cy + p.get("dy", 0.0), g.gw, g.gh,
                         *g.uv, p.get("rot", 0.0),
                         col[0], col[1], col[2], (col[3] if len(col) > 3 else 1.0) * a,
                         p.get("outline", outline), p.get("glow", glow), p.get("dilate", dilate), p.get("skew", skew),
                         p.get("sx", s), p.get("sy", s), p.get("ax", 0.0), p.get("ay", 0.0)))
        if not rows:
            return
        arr = np.asarray(rows, "f4")
        self.buf.orphan(self.maxn * self.NF * 4)
        self.buf.write(arr.tobytes())
        A = self.atlas(font)
        A.tex.use(0)
        self.prog["uAtlas"] = 0
        self.prog["uRes"] = (target.width, target.height)
        self.prog["uJitter"] = self.eng.jitter
        target.use()
        ctx = self.eng.ctx
        ctx.enable(moderngl.BLEND)
        if blend == "add":
            ctx.blend_func = moderngl.ONE, moderngl.ONE
        else:
            ctx.blend_func = moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA
        self.vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=len(rows))
        ctx.disable(moderngl.BLEND)


# --------------------------------------------------------------------------------------
# instanced 2D vector shapes (rounded boxes / circles / capsules / rings, with glow)
# --------------------------------------------------------------------------------------
class ShapeRenderer:
    FMT = "2f 2f 1f 4f 4f/i"
    ATTRS = ["iPos", "iHalf", "iRot", "iColor", "iParam"]

    def __init__(self, eng):
        self.eng = eng
        self.prog = eng.ctx.program(vertex_shader=glsl.VS_SHAPE, fragment_shader=glsl.FS_SHAPE)
        self.buf = eng.ctx.buffer(reserve=65536 * 13 * 4)
        self.vao = eng.ctx.vertex_array(self.prog, [(self.buf, self.FMT, *self.ATTRS)])
        self.items = []

    # queue helpers --------------------------------------------------------------
    def box(self, x, y, hw, hh, color, corner=0.0, rot=0.0, stroke=0.0, glow=0.0, glowk=40.0):
        c = tuple(color) + ((1.0,) if len(color) == 3 else ())
        self.items.append((x, y, hw, hh, rot, *c, corner, stroke, glowk, glow))

    def circle(self, x, y, r, color, stroke=0.0, glow=0.0, glowk=40.0):
        self.box(x, y, r, r, color, corner=r, stroke=stroke, glow=glow, glowk=glowk)

    def line(self, x0, y0, x1, y1, w, color, glow=0.0, glowk=40.0):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        self.box((x0 + x1) / 2, (y0 + y1) / 2, L / 2 + w, w, color, corner=w, rot=math.atan2(dy, dx),
                 glow=glow, glowk=glowk)

    def polyline(self, pts, w, color, glow=0.0, glowk=40.0):
        for (a, b) in zip(pts[:-1], pts[1:]):
            self.line(a[0], a[1], b[0], b[1], w, color, glow, glowk)

    def flush(self, target, blend="over"):
        if not self.items:
            return
        arr = np.asarray(self.items, "f4")
        self.items = []
        self.buf.orphan(max(arr.nbytes, 1024))
        self.buf.write(arr.tobytes())
        self.prog["uRes"] = (target.width, target.height)
        self.prog["uJitter"] = self.eng.jitter
        target.use()
        ctx = self.eng.ctx
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE) if blend == "add" else (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)
        self.vao.render(moderngl.TRIANGLE_STRIP, vertices=4, instances=len(arr))
        ctx.disable(moderngl.BLEND)


