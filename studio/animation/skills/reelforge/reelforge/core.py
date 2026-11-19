"""GPU core: context, HDR buffers, sub-frame accumulation, bloom/tonemap post, transitions, ffmpeg writer."""
import os, sys, math, queue, threading, subprocess, platform
import numpy as np
import moderngl
import imageio_ffmpeg
from . import glsl

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
TRANSITIONS = {"fade": 0, "iris": 1, "push": 2, "glitch": 3, "zoom": 4, "wipe": 5}


def create_context():
    """Try the platform default first, then EGL (headless Linux / servers). Returns (ctx, backend)."""
    errors = []
    attempts = [dict()]
    if platform.system() == "Linux":
        attempts.append(dict(backend="egl"))
    for kw in attempts:
        try:
            return moderngl.create_standalone_context(require=330, **kw), kw.get("backend", "default")
        except Exception as e:  # noqa
            errors.append(f"{kw or 'default'}: {e}")
    raise RuntimeError("Could not create an OpenGL 3.3 context:\n  " + "\n  ".join(errors) +
                       "\nRun:  python <skill>/scripts/rf.py doctor")


def halton(i, b):
    f, r = 1.0, 0.0
    while i > 0:
        f /= b; r += f * (i % b); i //= b
    return r


class Engine:
    """Owns the GL context and every render target.  Scene code draws into `eng.fbA`-style framebuffers."""

    def __init__(self, W, H, quiet=False):
        self.ctx, self.backend = create_context()
        self.renderer = self.ctx.info["GL_RENDERER"]
        if not quiet:
            print(f"[reelforge] GL: {self.renderer} ({self.backend})", flush=True)
        self.W, self.H = W, H
        self.jitter = (0.0, 0.0)
        self.common = dict(uTime=0.0, uKick=0.0, uSnare=0.0, uBeat=0.0, uGlobal=0.0)
        self._progs, self._vaos = {}, {}
        mk = self.hdr_fbo
        self.fbA, self.fbB, self.fbC = mk(W, H), mk(W, H), mk(W, H)
        self.accum = mk(W, H, "f4")
        self.mips = []
        w, h = W, H
        for _ in range(6):
            w, h = max(1, w // 2), max(1, h // 2)
            self.mips.append(mk(w, h))
        self.out = self.ctx.framebuffer(color_attachments=[self.ctx.texture((W, H), 3, dtype="f1")])
        from .draw import TextRenderer, ShapeRenderer
        self.text = TextRenderer(self)
        self.shapes = ShapeRenderer(self)

    @property
    def aspect(self):
        return self.W / self.H

    def hdr_fbo(self, w, h, dtype="f2"):
        t = self.ctx.texture((w, h), 4, dtype=dtype)
        t.filter = (moderngl.LINEAR, moderngl.LINEAR)
        t.repeat_x = t.repeat_y = False
        return self.ctx.framebuffer(color_attachments=[t])

    def program(self, frag, vert=glsl.VS_FULLSCREEN):
        key = (vert, frag)
        if key not in self._progs:
            src = frag if frag.lstrip().startswith("#version") else glsl.GLSL_HEADER.replace("430", "330") + glsl.GLSL_LIB + frag
            try:
                p = self.ctx.program(vertex_shader=vert, fragment_shader=src)
            except Exception:
                print("\n".join(f"{i+1:4d} {l}" for i, l in enumerate(src.split("\n"))), file=sys.stderr)
                raise
            self._progs[key] = p
            self._vaos[key] = self.ctx.vertex_array(p, [])
        return self._progs[key], self._vaos[key]

    @staticmethod
    def set_uniforms(prog, u):
        for k, v in u.items():
            if k in prog:
                try:
                    prog[k].value = v
                except Exception:
                    prog[k].write(np.asarray(v, "f4").tobytes())

    def fs(self, frag, target, uniforms=None, textures=None, blend=None, clear=None):
        """Run a fullscreen fragment shader into `target`.  Common uniforms (uTime, uKick, uRes...) are set for you."""
        prog, vao = self.program(frag)
        u = dict(self.common)
        u["uRes"] = (float(target.width), float(target.height))
        u["uJitter"] = self.jitter
        if uniforms:
            u.update(uniforms)
        for unit, (name, tex) in enumerate((textures or {}).items()):
            tex.use(unit)
            if name in prog:
                prog[name].value = unit
        self.set_uniforms(prog, u)
        target.use()
        if clear is not None:
            target.clear(*clear)
        ctx = self.ctx
        if blend:
            ctx.enable(moderngl.BLEND)
            ctx.blend_func = (moderngl.ONE, moderngl.ONE) if blend == "add" else (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)
        vao.render(moderngl.TRIANGLES, vertices=3)
        if blend:
            ctx.disable(moderngl.BLEND)

    def accum_clear(self):
        self.accum.use(); self.accum.clear(0, 0, 0, 0)

    def accum_add(self, src, weight):
        self.fs(glsl.FS_BLIT, self.accum, {"uWeight": weight}, {"uSrc": src.color_attachments[0]}, blend="add")

    def transition(self, a, b, target, p, kind="fade", direction=(1.0, 0.0)):
        k = TRANSITIONS.get(kind, kind) if isinstance(kind, str) else kind
        self.fs(glsl.FS_TRANSITION, target, {"uP": p, "uType": k, "uDir": direction},
                {"uA": a.color_attachments[0], "uB": b.color_attachments[0]})

    def post(self, frame, bloom=0.6, threshold=0.9, exposure=1.0, ca=0.003, vignette=0.6, grain=0.03,
             flash=0.0, sat=1.0, contrast=1.0, tint=(1, 1, 1), fade=1.0, radius=1.0):
        src = self.accum
        for i, m in enumerate(self.mips):
            st = src.color_attachments[0]
            self.fs(glsl.FS_DOWN, m, {"uSrcTexel": (1 / st.width, 1 / st.height), "uDstSize": (m.width, m.height),
                                      "uFirst": 1 if i == 0 else 0, "uThreshold": threshold}, {"uSrc": st})
            src = m
        for i in range(len(self.mips) - 1, 0, -1):
            s, d = self.mips[i], self.mips[i - 1]
            st = s.color_attachments[0]
            self.fs(glsl.FS_UP, d, {"uSrcTexel": (1 / st.width, 1 / st.height), "uDstSize": (d.width, d.height),
                                    "uRadius": radius}, {"uSrc": st}, blend="add")
        self.fs(glsl.FS_FINAL, self.out, {"uBloomAmt": bloom, "uExposure": exposure, "uCA": ca, "uVignette": vignette,
                                          "uGrain": grain, "uFrame": float(frame), "uFlash": flash, "uSat": sat,
                                          "uContrast": contrast, "uTint": tuple(tint), "uFade": fade},
                {"uHDR": self.accum.color_attachments[0], "uBloom": self.mips[0].color_attachments[0]})

    def read(self):
        """8-bit RGB, top row first (the final pass flips, so no numpy flip is needed)."""
        return self.out.read(components=3, alignment=1)


class Encoder:
    """rgb24 -> libx264 yuv420p, BT.709 tagged.  Fails fast (instead of hanging) if ffmpeg dies."""

    def __init__(self, path, W, H, fps, audio=None, quality="high", audio_offset=0.0):
        vf = ("scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
              "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
        crf, preset = {"draft": ("23", "veryfast"), "high": ("17", "medium"), "master": ("14", "slow")}[quality]
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(fps), "-i", "-"]
        if audio:
            if audio_offset:
                cmd += ["-ss", f"{audio_offset:.4f}"]
            cmd += ["-i", audio]
        cmd += ["-map", "0:v"] + (["-map", "1:a", "-c:a", "aac", "-b:a", "256k"] if audio else [])
        cmd += ["-c:v", "libx264", "-preset", preset, "-crf", crf, "-profile:v", "high", "-rc-lookahead", "20",
                "-threads", "6", "-g", str(fps * 2), "-vf", vf, "-colorspace", "bt709", "-color_primaries", "bt709",
                "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart"]
        if audio:
            cmd += ["-shortest"]
        self.p = subprocess.Popen(cmd + [path], stdin=subprocess.PIPE)
        self.q = queue.Queue(maxsize=8)
        self.err = None
        self.th = threading.Thread(target=self._run, daemon=True)
        self.th.start()

    def _run(self):
        try:
            while True:
                b = self.q.get()
                if b is None:
                    break
                self.p.stdin.write(b)
            self.p.stdin.close()
        except Exception as ex:
            self.err = ex

    def write(self, b):
        while True:
            if not self.th.is_alive():
                raise RuntimeError(f"ffmpeg died ({self.err}); often out-of-memory - use `render --chunked`")
            try:
                self.q.put(b, timeout=1.0)
                return
            except queue.Full:
                pass

    def close(self):
        if self.th.is_alive():
            self.q.put(None)
        self.th.join()
        return self.p.wait()
