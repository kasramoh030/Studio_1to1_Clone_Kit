"""Project / Scene / CLI - the part Claude (and you) actually drive.

    proj = Project("promo", preset="9:16", duration=12, bpm=120)
    proj.add(MyScene(), 0, 6, transition=None)
    proj.add(Other(),   6, 12, transition=("iris", 0.6))
    proj.music_score(key="A minor")          # or proj.music_file("song.mp3")
    proj.cli()                               # stills | contact | check | preview | render | gif | audio

Every scene must be a PURE FUNCTION OF TIME: render(eng, t, fb) may not keep state between calls.
That is what makes motion blur, scrubbing, stills, chunked/resumable renders and montages possible.
"""
import os, re, io, sys, math, time, shutil, argparse, subprocess
import numpy as np
from PIL import Image, ImageDraw

from .ease import clamp01, lerp, smooth
from . import audio as _audio

PRESETS = {
    "16:9": (1920, 1080), "1080p": (1920, 1080), "4k": (3840, 2160), "720p": (1280, 720),
    "9:16": (1080, 1920), "shorts": (1080, 1920), "reels": (1080, 1920), "tiktok": (1080, 1920),
    "1:1": (1080, 1080), "square": (1080, 1080), "4:5": (1080, 1350), "portrait": (1080, 1350),
}
DEFAULT_POST = dict(bloom=0.6, threshold=0.9, exposure=1.0, ca=0.003, vignette=0.5, grain=0.025,
                    sat=1.0, contrast=1.0, tint=(1, 1, 1), radius=1.0)


class Scene:
    """Subclass and implement render(eng, t, fb).  t = seconds since the shot started (can be slightly
    negative / beyond the end during transitions - clamp inside if you care)."""
    post = {}          # per-scene post overrides, e.g. dict(bloom=1.0, grain=0.04)
    cuts = []          # internal hard cuts (local seconds): motion blur will not smear across them
    project = None     # set by Project.add - gives access to project.track (beats), project.W/H...

    def shake(self, t):
        """pixels of camera shake at local time t (0 = none)"""
        return 0.0

    def render(self, eng, t, fb):
        raise NotImplementedError


class Shot:
    def __init__(self, scene, t0, t1, transition=None, offset=0.0):
        self.scene, self.t0, self.t1, self.transition, self.offset = scene, t0, t1, transition, offset

    def local(self, T):
        return T - self.t0 + self.offset


class Project:
    def __init__(self, name, preset="16:9", size=None, fps=60, duration=10.0, bpm=120.0,
                 subframes=8, shutter=0.6, post=None, out_dir=None, loop=False):
        self.loop = loop                      # True = seamless loop: no fade in/out (video + music)
        self.name = name
        self.W, self.H = size or PRESETS[preset]
        self.fps, self.duration, self.bpm = fps, float(duration), float(bpm)
        self.subframes, self.shutter = subframes, shutter
        self.post = dict(DEFAULT_POST, **(post or {}))
        self.shots = []
        self.flashes = []                     # (time, amount)
        self.track = _audio.Track(None, bpm, duration)
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv and sys.argv[0] else os.getcwd()
        self.out = out_dir or os.path.join(script_dir, "out", name)
        os.makedirs(self.out, exist_ok=True)
        self.audio_path = None

    # ------------------------------------------------------------------ building
    @property
    def aspect(self):
        return self.W / self.H

    def beat(self, n):
        return self.track.beat(n)

    def bar(self, n):
        return self.track.bar(n)

    def add(self, scene, start, end, transition=None, offset=0.0):
        """transition = (kind, seconds) centred on `start`; kind in fade|iris|push|glitch|zoom|wipe"""
        scene.project = self
        if hasattr(scene, "setup") and not getattr(scene, "_setup_done", False):
            scene._needs_setup = True
        self.shots.append(Shot(scene, float(start), float(end), transition, offset))
        self.shots.sort(key=lambda s: s.t0)
        return scene

    def flash(self, t, amount=1.0):
        self.flashes.append((float(t), float(amount)))

    def music_score(self, key="F minor", sections=None, impacts=(), whooshes=None, blips=(), seed=7):
        """Generate an original track that fits this edit (transition whooshes added automatically)."""
        path = os.path.join(self.out, "score.wav")
        if whooshes is None:
            whooshes = [s.t0 for s in self.shots if s.transition]
        sig = repr((self.duration, self.bpm, key, sections, list(impacts), list(whooshes), list(blips), seed, self.loop))
        stamp = path + ".sig"
        hits = path + ".hits.json"
        import json
        if os.path.exists(path) and os.path.exists(stamp) and os.path.exists(hits) and open(stamp).read() == sig:
            h = json.load(open(hits))                     # cached: synthesis takes a few seconds, skip it
            self.track = _audio.Track(path, self.bpm, self.duration, kicks=h["kicks"], snares=h["snares"])
        else:
            self.track = _audio.score(path, self.duration, self.bpm, key, sections, impacts, whooshes, blips, seed,
                                      fade=not self.loop)
            json.dump({"kicks": [float(k) for k in self.track.kicks], "snares": [float(s) for s in self.track.snares]},
                      open(hits, "w"))
            open(stamp, "w").write(sig)
        self.audio_path = path
        return self.track

    def music_file(self, path, bpm_hint=None):
        """Use your own song: tempo/beats/downbeat are detected so you can cut on the beat."""
        wav = os.path.join(self.out, "music.wav")
        self.track = _audio.from_file(path, bpm_hint=bpm_hint, out_wav=wav, duration=self.duration)
        self.bpm = self.track.bpm
        self.audio_path = wav
        print(f"[reelforge] detected {self.track.bpm:.1f} BPM, {len(self.track.beats)} beats, downbeat index {self.track.downbeat}")
        return self.track

    # ------------------------------------------------------------------ evaluation
    def _bounds(self):
        b = [0.0, self.duration]
        for s in self.shots:
            if not s.transition:
                b.append(s.t0)
            for c in s.scene.cuts:
                g = s.t0 + c - s.offset
                if s.t0 < g < s.t1:
                    b.append(g)
        return sorted(set(b))

    def _shot_index(self, T):
        for i, s in enumerate(self.shots):
            if s.t0 <= T < s.t1:
                return i
        return len(self.shots) - 1

    def _blend(self, T):
        i = self._shot_index(T)
        s = self.shots[i]
        if s.transition and i > 0 and T < s.t0 + s.transition[1] / 2:
            d = s.transition[1]
            return self.shots[i - 1], s, clamp01((T - (s.t0 - d / 2)) / d), s.transition
        if i + 1 < len(self.shots):
            n = self.shots[i + 1]
            if n.transition and T >= n.t0 - n.transition[1] / 2:
                d = n.transition[1]
                return s, n, clamp01((T - (n.t0 - d / 2)) / d), n.transition
        return s, None, 0.0, None

    def _render_sub(self, eng, T):
        A, B, p, tr = self._blend(T)
        if B is None:
            A.scene.render(eng, A.local(T), eng.fbA)
            return eng.fbA
        A.scene.render(eng, A.local(T), eng.fbA)
        B.scene.render(eng, B.local(T), eng.fbB)
        eng.transition(eng.fbA, eng.fbB, eng.fbC, p, tr[0], tr[2] if len(tr) > 2 else (1.0, 0.0))
        return eng.fbC

    def _post(self, T):
        A, B, p, tr = self._blend(T)
        pa = dict(self.post, **A.scene.post)
        if B is not None:
            pb = dict(self.post, **B.scene.post)
            for k in pa:
                if isinstance(pa[k], (int, float)):
                    pa[k] = lerp(pa[k], pb[k], smooth(p))
        pa["flash"] = sum(a * math.exp(-(T - t) * 12) for t, a in self.flashes if T >= t)
        pa["fade"] = 1.0 if self.loop else clamp01(T / 0.2) * (1 - smooth((T - (self.duration - 0.6)) / 0.6))
        return pa

    def _shake(self, T):
        A, B, p, tr = self._blend(T)
        s = A.scene.shake(A.local(T))
        return s if B is None else lerp(s, B.scene.shake(B.local(T)), p)

    def _setup(self, eng):
        for s in self.shots:
            if getattr(s.scene, "_needs_setup", False):
                s.scene.setup(eng)
                s.scene._needs_setup = False

    def frame(self, eng, T, fidx, sub, fps):
        bounds = self._bounds()
        lo = max(x for x in bounds if x <= T + 1e-9)
        hi = min([x for x in bounds if x > T + 1e-9] + [self.duration]) - 1e-4
        from .core import halton
        eng.accum_clear()
        for k in range(sub):
            tk = min(max(T + (k + 0.5) / sub * self.shutter / fps, lo), hi)
            jx, jy = halton(k + 1, 2) - 0.5, halton(k + 1, 3) - 0.5
            sa = self._shake(tk) * (eng.H / 1080)
            if sa > 0.01:
                jx += sa * (math.sin(tk * 83.1) * 0.6 + math.sin(tk * 211.7) * 0.4)
                jy += sa * (math.cos(tk * 71.3) * 0.6 + math.sin(tk * 167.9) * 0.4)
            eng.jitter = (jx, jy)
            tr = self.track
            eng.common.update(uTime=tk, uKick=tr.kick_env(tk), uSnare=tr.snare_env(tk), uBeat=tr.beat_float(tk), uGlobal=tk)
            eng.accum_add(self._render_sub(eng, tk), 1.0 / sub)
        eng.post(fidx, **self._post(T))
        return eng.read()

    # ------------------------------------------------------------------ CLI
    def cli(self, argv=None):
        _ensure_gpu_env()
        ap = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), description=f"ReelForge project '{self.name}'")
        sp = ap.add_subparsers(dest="cmd")
        a = sp.add_parser("stills", help="PNG stills at given times (look at them!)"); a.add_argument("times", nargs="+", type=float)
        a.add_argument("--full", action="store_true", help="full resolution (default: half)")
        a = sp.add_parser("contact", help="contact sheet(s): a thumbnail every N seconds")
        a.add_argument("--every", type=float, default=0.5); a.add_argument("--range", nargs=2, type=float)
        a = sp.add_parser("check", help="automatic QA: black / blown-out / frozen stretches, audio levels")
        a.add_argument("--every", type=float, default=0.25)
        a = sp.add_parser("preview", help="fast half-res draft MP4 with audio")
        a.add_argument("--range", nargs=2, type=float)
        a = sp.add_parser("render", help="final MP4")
        a.add_argument("--quality", default="high", choices=["draft", "high", "master"])
        a.add_argument("--chunked", action="store_true", help="crash-proof/resumable (auto for > 20s)")
        a.add_argument("--range", nargs=2, type=float); a.add_argument("--out")
        a = sp.add_parser("gif", help="share-ready GIF (README / X / Slack)")
        a.add_argument("--range", nargs=2, type=float); a.add_argument("--width", type=int, default=640)
        a.add_argument("--fps", type=int, default=15)
        sp.add_parser("audio", help="audio report + spectrogram with cut marks")
        a = sp.add_parser("verify", help="inspect a rendered MP4: frames, audio, decoded frame strip")
        a.add_argument("file", nargs="?")
        a = sp.add_parser("_chunk"); a.add_argument("a", type=float); a.add_argument("b", type=float); a.add_argument("out")
        a.add_argument("--quality", default="high")
        args = ap.parse_args(argv)
        if not args.cmd:
            ap.print_help(); return
        getattr(self, "cmd_" + args.cmd.lstrip("_"))(args)

    def _engine(self, scale=1.0):
        from .core import Engine
        W = int(round(self.W * scale / 2) * 2); H = int(round(self.H * scale / 2) * 2)
        eng = Engine(W, H)
        self._setup(eng)
        return eng

    def cmd_stills(self, args):
        eng = self._engine(1.0 if args.full else 0.5)
        d = os.path.join(self.out, "stills"); os.makedirs(d, exist_ok=True)
        for t in args.times:
            b = self.frame(eng, t, int(t * self.fps), self.subframes, self.fps)
            p = os.path.join(d, f"t{t:07.3f}.png")
            Image.frombytes("RGB", (eng.W, eng.H), b).save(p)
            print(p)

    def _thumbs(self, eng, times):
        for t in times:
            b = self.frame(eng, float(t), int(t * self.fps), 2, self.fps)
            yield float(t), Image.frombytes("RGB", (eng.W, eng.H), b)

    def cmd_contact(self, args):
        t0, t1 = args.range or (0.0, self.duration)
        times = list(np.arange(t0, t1, args.every))
        eng = self._engine(0.25 if self.W >= 1280 else 0.4)
        tw = 240 if self.aspect >= 1 else 135
        th = int(round(tw / self.aspect))
        cols = 8 if self.aspect >= 1 else 12
        per = cols * (8 if self.aspect >= 1 else 4)
        sheets = []
        for si in range(0, len(times), per):
            chunk = times[si:si + per]
            rows = math.ceil(len(chunk) / cols)
            sheet = Image.new("RGB", (cols * tw, rows * th), (30, 30, 30))
            for i, (t, im) in enumerate(self._thumbs(eng, chunk)):
                im = im.resize((tw, th), Image.LANCZOS)
                ImageDraw.Draw(im).text((4, 3), f"{t:.2f}", fill=(255, 0, 255))
                sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
            p = os.path.join(self.out, f"contact_{chunk[0]:06.2f}-{chunk[-1]:06.2f}.png")
            sheet.save(p); sheets.append(p); print(p)
        return sheets

    def cmd_check(self, args):
        eng = self._engine(0.25 if self.W >= 1280 else 0.4)
        times = np.arange(0, self.duration, args.every)
        prev, still_run, issues = None, 0.0, []
        for t, im in self._thumbs(eng, times):
            a = np.asarray(im, "f4") / 255.0
            L = a.mean()
            clipped = (a.min(2) > 0.97).mean()
            in_fade = (not self.loop) and (t < 0.25 or t > self.duration - 0.7)
            if L < 0.015 and not in_fade:
                issues.append(f"{t:6.2f}s  BLACK frame (mean luma {L:.3f})")
            if clipped > 0.45:
                issues.append(f"{t:6.2f}s  BLOWN OUT ({clipped*100:.0f}% of pixels clipped) - fine only if it's an intended flash")
            if prev is not None:
                diff = np.abs(a - prev).mean()
                still_run = still_run + args.every if diff < 0.002 else 0.0
                if abs(still_run - 1.5) < 1e-6:
                    issues.append(f"{t-1.5:6.2f}s  FROZEN for 1.5s+ (nothing moves) - add secondary motion")
            prev = a
        print(f"[check] {len(times)} samples, {len(issues)} warnings")
        for s in issues:
            print("  " + s)
        if self.audio_path and os.path.exists(self.audio_path):
            r = _audio.report(self.audio_path)
            print(f"[audio] {r['duration']}s  peak {r['peak_dbfs']} dBFS  clipped={r['clipped_samples']}  silent seconds={r['silent_seconds']}")
            if abs(r["duration"] - self.duration) > 0.1:
                print(f"  AUDIO LENGTH {r['duration']}s != video {self.duration}s")
        return issues

    def cmd_verify(self, args):
        self.verify(args.file or os.path.join(self.out, f"{self.name}.mp4"))

    def cmd_audio(self, args):
        if not self.audio_path:
            print("no music set: call proj.music_score() or proj.music_file(path)"); return
        png = os.path.join(self.out, "spectrogram.png")
        r = _audio.report(self.audio_path, png, marks=[s.t0 for s in self.shots])
        for k, v in r.items():
            print(f"{k}: {v}")
        print(png, "(orange lines = shot starts; energy changes should line up with them)")

    def _encode(self, path, t0, t1, scale, fps, sub, quality, audio=True):
        from .core import Encoder
        eng = self._engine(scale)
        enc = Encoder(path, eng.W, eng.H, fps, audio=self.audio_path if (audio and self.audio_path) else None,
                      quality=quality, audio_offset=t0)
        f0, f1 = int(round(t0 * fps)), int(round(t1 * fps))
        st = time.time()
        for f in range(f0, f1):
            enc.write(self.frame(eng, f / fps, f, sub, fps))
            if (f - f0) % fps == 0 and f > f0:
                r = (f - f0) / (time.time() - st)
                print(f"  {f/fps:6.2f}s / {t1:.2f}s   {r:5.1f} fps   eta {(f1-f)/r:4.0f}s", flush=True)
        rc = enc.close()
        if rc != 0:
            raise RuntimeError(f"ffmpeg exited with {rc}")
        return path

    def cmd_preview(self, args):
        t0, t1 = args.range or (0.0, self.duration)
        p = os.path.join(self.out, f"{self.name}_preview.mp4")
        self._encode(p, t0, t1, 0.5, 30, 2, "draft")
        print(p)

    def cmd_chunk(self, args):
        self._encode(args.out, args.a, args.b, 1.0, self.fps, self.subframes, args.quality, audio=False)

    def cmd_render(self, args):
        t0, t1 = args.range or (0.0, self.duration)
        out = args.out or os.path.join(self.out, f"{self.name}.mp4")
        if not args.chunked and (t1 - t0) <= 20:
            self._encode(out, t0, t1, 1.0, self.fps, self.subframes, args.quality)
            self.verify(out, t1 - t0)
            return out
        from .core import FFMPEG
        root = os.path.join(self.out, "chunks")
        cdir = os.path.join(root, self._render_key(args.quality))      # new code/settings -> fresh chunks
        os.makedirs(cdir, exist_ok=True)
        for old in os.listdir(root):                                   # drop chunks of previous versions
            if old != os.path.basename(cdir):
                shutil.rmtree(os.path.join(root, old), ignore_errors=True)
        size = 5.0
        parts = []
        n = max(1, math.ceil((t1 - t0) / size - 1e-9))
        for i in range(n):
            a, b = t0 + i * size, min(t1, t0 + (i + 1) * size)
            p = os.path.join(cdir, f"{args.quality}_{a:07.2f}_{b:07.2f}.mp4")
            want = int(round(b * self.fps)) - int(round(a * self.fps))
            for attempt in range(4):
                if os.path.exists(p) and _count_frames(p) == want:
                    break
                print(f"[chunk {i+1}/{n}] {a:.2f}-{b:.2f}s" + (f" (retry {attempt})" if attempt else ""), flush=True)
                try:
                    subprocess.run([sys.executable, os.path.abspath(sys.argv[0]), "_chunk", str(a), str(b), p,
                                    "--quality", args.quality], timeout=1800, env=os.environ.copy())
                except subprocess.TimeoutExpired:
                    print("  chunk timed out, retrying")
            if not (os.path.exists(p) and _count_frames(p) == want):
                sys.exit(f"chunk {a}-{b} failed 4 times - run `stills {a}` to see the error")
            parts.append(p)
        lst = os.path.join(cdir, "list.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{p}'\n" for p in parts)
        cmd = [FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst]
        if self.audio_path:
            cmd += ["-ss", f"{t0:.4f}", "-i", self.audio_path, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "256k", "-shortest"]
        subprocess.run(cmd + ["-c:v", "copy", "-movflags", "+faststart", out], check=True)
        self.verify(out, t1 - t0)
        return out

    def _render_key(self, quality):
        """hash of everything that changes the picture: the project script, the engine source, settings"""
        import hashlib
        h = hashlib.sha1()
        pkg = os.path.dirname(os.path.abspath(__file__))
        files = [os.path.abspath(sys.argv[0])] + sorted(os.path.join(pkg, f) for f in os.listdir(pkg) if f.endswith(".py"))
        for f in files:
            try:
                h.update(open(f, "rb").read())
            except OSError:
                pass
        if self.audio_path and os.path.exists(self.audio_path):
            h.update(str(os.path.getmtime(self.audio_path)).encode())
        h.update(repr((self.W, self.H, self.fps, self.subframes, self.shutter, quality, sorted(self.post.items()))).encode())
        return h.hexdigest()[:12]

    def verify(self, path, expect_dur=None):
        """Inspect the DELIVERED file: frame count, audio, and a strip of frames decoded from the MP4 itself."""
        from .core import FFMPEG
        expect_dur = expect_dur or self.duration
        n = _count_frames(path)
        want = int(round(expect_dur * self.fps))
        info = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
        m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else -1.0
        has_audio = "Audio:" in info
        strip = os.path.splitext(path)[0] + "_verify.png"
        ts = [expect_dur * f for f in (0.1, 0.35, 0.6, 0.9)]
        ims = []
        for t in ts:
            r = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf", "scale=480:-2",
                                "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
            if r.stdout:
                ims.append(Image.open(io.BytesIO(r.stdout)).convert("RGB"))
        if ims:
            w, h = ims[0].size
            sheet = Image.new("RGB", (w * len(ims), h))
            for i, im in enumerate(ims):
                ImageDraw.Draw(im).text((4, 3), f"{ts[i]:.2f}s", fill=(255, 0, 255))
                sheet.paste(im, (i * w, 0))
            sheet.save(strip)
        ok = n == want and abs(dur - expect_dur) < 0.1 and (has_audio or not self.audio_path)
        print(f"[verify] {path}")
        print(f"  frames {n}/{want}  duration {dur:.2f}s  audio={'yes' if has_audio else 'NO'}  -> {'OK' if ok else 'PROBLEM'}")
        print(f"  frames decoded from the file: {strip}   <- Read this image")
        return ok

    def cmd_gif(self, args):
        from .core import FFMPEG
        t0, t1 = args.range or (0.0, min(self.duration, 8.0))
        src = os.path.join(self.out, f"{self.name}.mp4")
        if not os.path.exists(src):
            src = os.path.join(self.out, f"{self.name}_preview.mp4")
            self._encode(src, 0.0, self.duration, 0.5, 30, 2, "draft")
        out = os.path.join(self.out, f"{self.name}.gif")
        flt = f"fps={args.fps},scale={args.width}:-2:flags=lanczos"
        subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", src, "-vf",
                        f"{flt},split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a",
                        out], check=True)
        print(out, f"{os.path.getsize(out)/1e6:.1f} MB")


def _count_frames(path):
    from .core import FFMPEG
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path, "-map", "0:v", "-c", "copy", "-f", "null", "-"],
                       capture_output=True, text=True)
    for line in r.stderr.splitlines()[::-1]:
        if "frame=" in line:
            try:
                return int(line.split("frame=")[1].split()[0])
            except Exception:
                return 0
    return 0


def _ensure_gpu_env():
    """Windows Optimus laptops give OpenGL the *integrated* GPU unless SHIM_MCCOMPAT is set before the
    process starts - so re-launch ourselves once with it.  Also avoid OpenBLAS thread-buffer OOMs."""
    if os.environ.get("RF_CHILD"):
        return
    env = os.environ.copy()
    changed = False
    if os.name == "nt" and "SHIM_MCCOMPAT" not in env and shutil.which("nvidia-smi"):
        env["SHIM_MCCOMPAT"] = "0x800000001"; changed = True
    if "OPENBLAS_NUM_THREADS" not in env:
        env["OPENBLAS_NUM_THREADS"] = "1"; changed = True
    if changed:
        env["RF_CHILD"] = "1"
        sys.exit(subprocess.run([sys.executable] + sys.argv, env=env).returncode)
