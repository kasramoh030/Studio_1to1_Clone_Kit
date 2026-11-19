"""Audio for ReelForge: a tiny synth studio (royalty-free generated scores), beat tracking for your own
music, and measurable audio QA.  Pure numpy/scipy + the ffmpeg bundled by imageio-ffmpeg."""
import os, math, wave
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(7)

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

def tt(dur): return np.arange(int(dur * SR)) / SR

def polyblep(ph, dt):
    y = np.zeros_like(ph)
    m = ph < dt
    x = ph[m] / dt[m]
    y[m] = x + x - x * x - 1.0
    m2 = ph > 1 - dt
    x = (ph[m2] - 1.0) / dt[m2]
    y[m2] = x * x + x + x + 1.0
    return y

def saw(freq, n, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, "f8"), (n,)).astype("f8")
    dt = f / SR
    ph = (phase0 + np.cumsum(dt)) % 1.0
    return 2.0 * ph - 1.0 - polyblep(ph, dt)

def lp(x, fc, order=2):
    fc = min(fc, SR * 0.45)
    return signal.sosfilt(signal.butter(order, fc, "low", fs=SR, output="sos"), x, axis=0)

def hp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, "high", fs=SR, output="sos"), x, axis=0)

def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos"), x, axis=0)

def sweep_lp(x, f0, f1, block=256):
    """time-varying 2-pole lowpass (exponential cutoff sweep)"""
    out = np.zeros_like(x)
    n = len(x); zi = None
    for s in range(0, n, block):
        e = min(n, s + block)
        fc = f0 * (f1 / f0) ** (s / max(1, n - 1))
        sos = signal.butter(2, min(fc, SR * 0.45), "low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[s:e], zi = signal.sosfilt(sos, x[s:e], zi=zi)
    return out

def adsr(n, a=0.005, d=0.1, s=0.7, r=0.05):
    t = np.arange(n) / SR
    dur = n / SR
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    rel = np.clip((dur - t) / max(r, 1e-6), 0, 1)
    return e * rel

class Bus:
    def __init__(self, dur): self.x = np.zeros((int(dur * SR) + SR * 4, 2))
    def add(self, t0, sig, gain=1.0, pan=0.0):
        s = int(round(t0 * SR))
        if s < 0:
            sig = sig[-s:]; s = 0
        if sig.ndim == 1:
            l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
            sig = np.stack([sig * l, sig * r], 1) * math.sqrt(2)
        e = min(len(self.x), s + len(sig))
        self.x[s:e] += sig[:e - s] * gain

# ---- instruments
def kick(punch=1.0):
    t = tt(0.55)
    f = 44 + 120 * np.exp(-t * 30) + 40 * np.exp(-t * 200)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 5.5) * (1 - np.exp(-t * 3000))
    click = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 400) * 0.25
    return np.tanh((body * 1.3 + click) * 1.6 * punch) * 0.9

def snare():
    t = tt(0.35)
    tone = (np.sin(2 * np.pi * 190 * t) * 0.6 + np.sin(2 * np.pi * 330 * t) * 0.3) * np.exp(-t * 22)
    nz = bp(rng.standard_normal(len(t)), 1200, 9000) * np.exp(-t * 13)
    return np.tanh((tone + nz * 0.9) * 1.4) * 0.7

def clap():
    t = tt(0.4)
    nz = bp(rng.standard_normal(len(t)), 900, 4000)
    e = np.exp(-t * 16)
    for d in (0.0, 0.011, 0.022):
        e = e + np.where(t >= d, np.exp(-(t - d) * 180), 0) * 0.8
    return nz * e * 0.5

def hat(open_=False):
    t = tt(0.3 if open_ else 0.08)
    nz = hp(rng.standard_normal(len(t)), 7500, 4)
    return nz * np.exp(-t * (11 if open_ else 70)) * 0.35

def crash():
    t = tt(2.8)
    nz = hp(rng.standard_normal(len(t)), 3500, 2)
    metal = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (3120, 4470, 5530, 6710)) * 0.08
    return (nz * 0.5 + metal) * np.exp(-t * 1.6) * 0.55

def impact():
    t = tt(3.0)
    f = 28 + 70 * np.exp(-t * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)
    nz = lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 5) * 0.8
    return np.tanh((boom * 1.4 + nz) * 1.3) * 0.9

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = sweep_lp(rng.standard_normal(n), 200, 14000) * (t / dur) ** 2
    f = 180 * (12 ** (t / dur))
    tone = saw(f, n) * 0.08 * (t / dur) ** 3
    return (nz * 0.45 + lp(tone, 6000))

def whoosh(dur=0.6, up=True):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.sin(np.pi * t / dur) ** 2
    x = sweep_lp(rng.standard_normal(n), 400 if up else 8000, 8000 if up else 400)
    return x * env * 0.5

def blip(f=1400, dur=0.09):
    t = tt(dur)
    return np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 40)) * np.exp(-t * 45) * 0.35

def bloop():
    t = tt(0.22)
    f = 180 + 520 * np.exp(-t * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.45

def tick():
    t = tt(0.03)
    return hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 220) * 0.3

def pluck(m, dur=0.6, bright=1.0):
    f = mtof(m); t = tt(dur)
    y = np.zeros_like(t)
    for k in range(1, 16):
        if f * k > SR * 0.4: break
        y += (1 / k) * np.sin(2 * np.pi * f * k * t + k * 0.3) * np.exp(-t * (3 + k * 2.2 / bright))
    return y * (1 - np.exp(-t * 800)) * 0.3

def bell(m, dur=2.5):
    f = mtof(m); t = tt(dur)
    I = 3.5 * np.exp(-t * 2.5)
    y = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * 3.5 * t))
    y += 0.3 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 3)
    return y * np.exp(-t * 1.5) * (1 - np.exp(-t * 600)) * 0.22

def supersaw(m, dur, voices=7, detune=0.18, cutoff=2500, a=0.3, r=0.6, bright_env=None):
    n = int(dur * SR); f = mtof(m)
    y = np.zeros((n, 2))
    for v in range(voices):
        d = (v / (voices - 1) - 0.5) * 2 * detune if voices > 1 else 0
        s = saw(f * 2 ** (d / 12), n, rng.uniform())
        p = (v / (voices - 1) - 0.5) * 1.4 if voices > 1 else 0
        y[:, 0] += s * math.cos((p + 1) * math.pi / 4); y[:, 1] += s * math.sin((p + 1) * math.pi / 4)
    y = lp(y, cutoff, 2) / voices * 1.6
    return y * adsr(n, a, 0.4, 0.85, r)[:, None]

def bass_note(m, dur, cutoff=900, drive=1.5):
    n = int(dur * SR); f = mtof(m)
    s = saw(f, n) * 0.6 + saw(f * 1.005, n, 0.3) * 0.4 + np.sin(2 * np.pi * f / 2 * np.arange(n) / SR) * 0.7
    t = np.arange(n) / SR
    y = lp(s, cutoff) * 0.7 + lp(s, cutoff * 4) * 0.3 * np.exp(-t * 18)
    return np.tanh(y * drive) * adsr(n, 0.004, 0.2, 0.9, 0.03) * 0.5

def wobble(m, dur, rate):
    n = int(dur * SR); f = mtof(m); t = np.arange(n) / SR
    s = saw(f, n) + saw(f * 1.01, n, .5) * .6 + np.sin(2 * np.pi * f / 2 * t)
    lfo = 0.5 - 0.5 * np.cos(2 * np.pi * rate * t)
    out = np.zeros(n); zi = None; B = 128
    for i in range(0, n, B):
        fc = 150 + 2400 * lfo[i] ** 2
        sos = signal.butter(2, fc, "low", fs=SR, output="sos")
        if zi is None: zi = np.zeros((sos.shape[0], 2))
        out[i:i + B], zi = signal.sosfilt(sos, s[i:i + B], zi=zi)
    return np.tanh(out * 2.0) * adsr(n, 0.01, 0.3, 0.9, 0.05) * 0.45

def reverb_ir(dur=2.6, seed=3):
    r = np.random.default_rng(seed)
    t = tt(dur)
    ir = r.standard_normal((len(t), 2)) * np.exp(-t * 6.9 / dur)[:, None]
    ir = lp(ir, 7000) * 0.5 + lp(ir, 2000) * 0.5 * np.exp(-t * 2)[:, None]
    ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0))

def delay(x, d, fb=0.4, taps=5, pingpong=True):
    y = x.copy(); s = int(d * SR)
    g = 1.0
    for k in range(1, taps + 1):
        g *= fb
        sh = np.zeros_like(x)
        sh[s * k:] = x[:-s * k] if s * k < len(x) else 0
        if pingpong and k % 2 == 1:
            sh = sh[:, ::-1]
        y += lp(sh, 5000 - k * 600) * g
    return y

def sidechain_curve(n, kicks, depth=0.75, rel=0.12):
    t = np.arange(n) / SR
    g = np.ones(n)
    for k in kicks:
        s = int(k * SR)
        if s >= n: continue
        e = min(n, s + int(0.6 * SR))
        tau = t[s:e] - k
        g[s:e] = np.minimum(g[s:e], 1 - depth * np.exp(-tau / rel) * np.minimum(1, tau / 0.004 + 0.2))
    return g



# =====================================================================================
# Track: the single source of timing truth shared by picture and sound
# =====================================================================================
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7,
        "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


class Track:
    """Beat grid + hit lists + the wav on disk.  Visuals read kick_env(t) / beat(n) / bar(n) from here."""

    def __init__(self, path, bpm, duration, beats=None, kicks=None, snares=None, downbeat=0, onset=None, onset_rate=None):
        self.path, self.bpm, self.duration = path, float(bpm), float(duration)
        self.spb = 60.0 / self.bpm
        self.beats = np.asarray(beats if beats is not None else np.arange(0, duration + 1e-6, self.spb), "f8")
        self.kicks = np.asarray(sorted(kicks) if kicks is not None else self.beats, "f8")
        self.snares = np.asarray(sorted(snares) if snares is not None else [], "f8")
        self.downbeat = downbeat
        self._onset, self._onset_rate = onset, onset_rate

    def beat(self, n):
        """time of beat n (float n allowed; extrapolates past the grid)"""
        b = self.beats
        if len(b) < 2:
            return n * self.spb
        i = int(math.floor(n))
        if 0 <= i < len(b) - 1:
            return float(b[i] + (b[i + 1] - b[i]) * (n - i))
        return float(b[0] + n * self.spb) if i < 0 else float(b[-1] + (n - (len(b) - 1)) * self.spb)

    def bar(self, n, beats_per_bar=4):
        return self.beat(self.downbeat + n * beats_per_bar)

    def quantize(self, t, div=1):
        """snap a time to the nearest beat subdivision"""
        k = round((t - self.beats[0]) / (self.spb / div))
        return float(self.beats[0] + k * self.spb / div)

    @staticmethod
    def _env(t, hits, rate):
        if len(hits) == 0:
            return 0.0
        i = np.searchsorted(hits, t, side="right") - 1
        return 0.0 if i < 0 else float(math.exp(-(t - hits[i]) * rate))

    def kick_env(self, t): return self._env(t, self.kicks, 7.0)
    def snare_env(self, t): return self._env(t, self.snares, 9.0)
    def beat_float(self, t): return (t - self.beats[0]) / self.spb

    def onset(self, t):
        """loudness-onset envelope (0..1) of a user-supplied song - for audio-reactive visuals"""
        if self._onset is None:
            return self.kick_env(t)
        i = int(t * self._onset_rate)
        return float(self._onset[i]) if 0 <= i < len(self._onset) else 0.0


# =====================================================================================
# generated score
# =====================================================================================
ENERGIES = ("intro", "build", "groove", "drop", "break", "outro")


def auto_sections(bars):
    """sensible default arrangement for `bars` bars"""
    if bars <= 4:
        return [("groove", 0, bars)]
    intro = 1 if bars < 10 else 2
    outro = 1 if bars < 10 else 2
    mid = bars - intro - outro
    build = 1 if mid >= 4 else 0
    groove = (mid - build) // 2
    drop = mid - build - groove
    secs, b = [], 0
    for name, n in (("intro", intro), ("groove", groove), ("build", build), ("drop", drop), ("outro", outro)):
        if n > 0:
            secs.append((name, b, b + n)); b += n
    return secs


def score(path, duration, bpm=120, key="F minor", sections=None, impacts=(), whooshes=(), blips=(), seed=7, fade=True):
    """Synthesize an original, royalty-free track that fits the edit.

    sections : list of (energy, first_bar, end_bar)   energy in intro|build|groove|drop|break|outro
               (default: auto arrangement).  Put your big visual moment on the first "drop" bar.
    impacts / whooshes / blips : times (s) for hit / transition / UI sound effects.
    """
    global rng
    rng = np.random.default_rng(seed)
    spb = 60.0 / bpm
    BARL = spb * 4
    bars = int(math.ceil(duration / BARL - 1e-6))
    sections = sections or auto_sections(bars)
    root_name, _, mode = key.partition(" ")
    r = NOTE[root_name] + 48
    if mode.lower().startswith("maj"):
        prog = [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]          # I V vi IV
        roots = [0, 7, 9, 5]
    else:
        prog = [[0, 3, 7], [-4, 0, 3], [3, 7, 10], [-2, 2, 5]]             # i VI III VII
        roots = [0, -4, 3, -2]
    chord = lambda bar: [r + n for n in prog[bar % 4]]
    rootn = lambda bar: r - 12 + roots[bar % 4]
    energy = {}
    for name, b0, b1 in sections:
        for b in range(b0, b1):
            energy[b] = name
    first_outro = min([b for b, v in energy.items() if v == "outro"] or [10 ** 9])
    T = lambda bar, beat=0.0: bar * BARL + beat * spb
    drums, bass, music, lead, sfx, send = (Bus(duration) for _ in range(6))
    K, SN, CL, CR, IMP = kick(), snare(), clap(), crash(), impact()
    kicks, snares = [], []
    order = {"intro": 0, "outro": 0, "break": 1, "build": 2, "groove": 2, "drop": 3}
    for bar in range(bars):
        e = energy.get(bar, "groove")
        nxt = energy.get(bar + 1, "outro")
        c = chord(bar)
        cut = {"intro": 700, "break": 1200, "outro": 1400, "build": 1800, "groove": 1800, "drop": 3200}[e]
        g = 0.2 if e == "intro" else 0.13
        for m in c:
            music.add(T(bar), supersaw(m, BARL + 0.5, cutoff=cut, a=1.0 if e == "intro" else 0.08, r=0.5), g)
            send.add(T(bar), supersaw(m + 12, BARL + 0.5, voices=3, cutoff=cut, a=0.3), g * 0.25)
        pattern = {"groove": [0, 1, 2, 3], "drop": [0, 1, 2, 3], "build": [0, 2]}.get(e, [])
        if e == "outro" and bar == first_outro:
            pattern = [0]
        for bt in pattern:
            kicks.append(T(bar, bt)); drums.add(T(bar, bt), K, 1.0)
        if e in ("groove", "drop", "build"):
            for bt in (1, 3):
                snares.append(T(bar, bt)); drums.add(T(bar, bt), SN, 0.5); drums.add(T(bar, bt), CL, 0.45)
                send.add(T(bar, bt), CL, 0.3)
            steps = 16 if e == "drop" else 8
            for i in range(steps):
                if steps == 8 and i % 2 == 0:
                    continue
                drums.add(T(bar, i * 4 / steps), hat(), 0.5 if i % 2 else 0.28, pan=0.25 * math.sin(i))
        if e in ("groove", "build"):
            for i in range(4):
                bass.add(T(bar, i + 0.5), bass_note(rootn(bar), 0.45, cutoff=700), 0.9)
        elif e == "drop":
            for i in range(8):
                bass.add(T(bar, i * 0.5), bass_note(rootn(bar) + (12 if i % 2 else 0), 0.48, cutoff=1200, drive=2.2), 0.9)
        if e in ("groove", "build", "break"):
            pat = [0, 1, 2, 1, 0, 2, 1, 2]
            for i in range(16):
                m = c[pat[i % 8]] + 12 + (12 if i % 4 == 3 else 0)
                lead.add(T(bar, i * 0.25), pluck(m, 0.5), 0.38 if i % 4 == 0 else 0.26, pan=math.sin(i * 1.3) * 0.5)
        if e == "drop":
            tones = sorted(set(c + [x + 12 for x in c] + [x + 24 for x in c]))
            for (b, idx, d) in [(0, 2, 1), (1, 1, .5), (1.5, 2, .5), (2, 3, 1), (3, 4, 1)]:
                m = tones[min(len(tones) - 1, 3 + idx + (bar % 2))]
                lead.add(T(bar, b), supersaw(m, d * spb + 0.05, voices=3, detune=0.08, cutoff=4500, a=0.01, r=0.08), 0.26)
        if e in ("break", "outro", "intro") and bar % 2 == 0:
            for j, m in enumerate([c[2] + 24, c[1] + 24, c[0] + 24]):
                lead.add(T(bar, j * 1.0), bell(m, 2.5), 0.45, pan=(j - 1) * 0.4)
        if order.get(nxt, 0) > order.get(e, 0) or (e == "build" and nxt == "drop"):
            sfx.add(T(bar), riser(BARL), 0.5)
            if nxt == "drop":
                for i in range(16):
                    drums.add(T(bar, i * 0.25 * 0.94), SN, 0.1 + 0.45 * (i / 16) ** 2)
        if e == "drop" and energy.get(bar - 1) != "drop":
            sfx.add(T(bar), IMP, 0.9); drums.add(T(bar), CR, 0.7); send.add(T(bar), IMP, 0.4)
    for t0 in impacts:
        sfx.add(t0, IMP, 0.9); drums.add(t0, CR, 0.6); send.add(t0, IMP, 0.4)
    for t0 in whooshes:
        sfx.add(t0 - 0.25, whoosh(0.5), 0.45)
    for i, t0 in enumerate(blips):
        sfx.add(t0, blip(1300 + 180 * (i % 4)), 0.5, pan=(i % 3 - 1) * 0.4)
    kicks = sorted(set(round(k, 5) for k in kicks))
    n = len(drums.x)
    sc = sidechain_curve(n, kicks)[:, None]
    lead_fx = delay(lead.x, spb * 0.75, fb=0.35)
    wet_in = send.x + music.x * 0.35 + lead_fx * 0.3 + sfx.x * 0.15
    ir = reverb_ir()
    wet = np.stack([signal.fftconvolve(wet_in[:, ch], ir[:, ch])[:n] for ch in range(2)], 1)
    mix = drums.x * 0.85 + bass.x * sc * 0.8 + music.x * sc * 0.75 + lead_fx * 0.6 + sfx.x * 0.7 + wet * 0.28 * sc
    mix = hp(mix, 25)[:int(duration * SR)]
    t = np.arange(len(mix)) / SR
    if fade:
        mix *= np.clip((duration - t) / min(2.5, duration * 0.2), 0, 1)[:, None] * np.clip(t / 0.05, 0, 1)[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / max(1e-9, np.abs(mix).max()) * 10 ** (-1.0 / 20)
    write_wav(path, mix)
    return Track(path, bpm, duration, kicks=kicks, snares=snares)


def write_wav(path, stereo):
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


# =====================================================================================
# user-supplied music: decode + beat tracking (no librosa needed)
# =====================================================================================
def decode(path, sr=22050, mono=True):
    import imageio_ffmpeg, subprocess
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", path, "-f", "s16le", "-ac", "1" if mono else "2",
           "-ar", str(sr), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    x = np.frombuffer(raw, "<i2").astype("f4") / 32768.0
    return x if mono else x.reshape(-1, 2)


def onset_envelope(x, sr=22050, hop=256, n_fft=1024):
    f, t, Z = signal.stft(x, sr, nperseg=n_fft, noverlap=n_fft - hop, boundary=None, padded=False)
    S = np.log1p(100 * np.abs(Z[f < 8000]))
    flux = np.concatenate([[0], np.maximum(0, np.diff(S, axis=1)).sum(0)])
    flux = np.maximum(flux - signal.medfilt(flux, 31) * 0.8, 0)
    flux /= flux.max() + 1e-9
    lowS = S[: max(2, int(len(S) * 150 / 8000))]
    low = np.concatenate([[0], np.maximum(0, np.diff(lowS, axis=1)).sum(0)])
    low /= low.max() + 1e-9
    return flux, low, sr / hop


def track_beats(env, rate, bpm_hint=None, tightness=100.0):
    """Ellis-style dynamic-programming beat tracker.  Returns (bpm, beat_times)."""
    e = env - env.mean()
    ac = signal.fftconvolve(e, e[::-1], "full")[len(e) - 1:]
    lags = np.arange(len(ac)) / rate
    bpms = 60.0 / np.maximum(lags, 1e-9)
    ok = (bpms > 60) & (bpms < 200)
    center = bpm_hint or 120.0
    w = np.exp(-0.5 * (np.log2(np.maximum(bpms, 1e-9) / center) / 0.9) ** 2)
    cand = np.where(ok, ac * w, -np.inf)
    L = int(np.argmax(cand))
    Lf = float(L)
    if 1 <= L < len(ac) - 1:
        y0, y1, y2 = ac[L - 1], ac[L], ac[L + 1]
        Lf = L + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
    period = Lf
    bpm = 60.0 * rate / period
    n = len(env)
    score_ = env.astype("f8").copy()
    back = -np.ones(n, int)
    lo, hi = int(round(period * 0.5)), int(round(period * 2))
    offs = np.arange(lo, hi + 1)
    pen = -tightness * np.log(offs / period) ** 2
    for i in range(hi, n):
        prev = score_[i - offs] + pen
        k = int(np.argmax(prev))
        score_[i] = env[i] + prev[k]
        back[i] = i - offs[k]
    P = int(period)
    i = int(np.argmax(score_[-P:])) + n - P
    beats = []
    while i >= 0:
        beats.append(i)
        i = back[i]
    beats = np.array(beats[::-1], "f8") / rate
    return bpm, beats


def from_file(path, bpm_hint=None, out_wav=None, duration=None):
    """Load YOUR song, detect tempo + beats + downbeat, and return a Track you can cut to."""
    sr = 22050
    x = decode(path, sr)
    env, low, rate = onset_envelope(x, sr)
    bpm, beats = track_beats(env, rate, bpm_hint)
    idx = np.clip((beats * rate).astype(int), 0, len(low) - 1)
    beats = beats + 512.0 / sr                     # STFT frame -> window-centre time
    downbeat = int(np.argmax([low[idx[p::4]].sum() for p in range(4)]))
    dur = duration or len(x) / sr
    if out_wav:
        import imageio_ffmpeg, subprocess
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error", "-i", path, "-t", f"{dur:.3f}",
                        "-ar", str(SR), "-ac", "2", out_wav], check=True)
    sm = signal.lfilter([1.0], [1.0, -0.6], env)
    sm /= sm.max() + 1e-9
    return Track(out_wav or path, bpm, dur, beats=beats, kicks=beats, downbeat=downbeat, onset=sm, onset_rate=rate)


# =====================================================================================
# audio QA (Claude can't listen - so measure)
# =====================================================================================
def report(path, spectrogram_png=None, marks=()):
    x = decode(path, sr=SR, mono=False)
    m = x.mean(1)
    peak = float(np.abs(x).max())
    sec = [float(20 * np.log10(np.sqrt((m[i * SR:(i + 1) * SR] ** 2).mean()) + 1e-9)) for i in range(int(len(m) / SR))]
    out = dict(duration=round(len(m) / SR, 3), peak_dbfs=round(20 * math.log10(peak + 1e-12), 2),
               clipped_samples=int((np.abs(x) > 0.999).sum()),
               rms_db_per_second=[round(v, 1) for v in sec], silent_seconds=[i for i, v in enumerate(sec) if v < -45])
    if spectrogram_png:
        from PIL import Image, ImageDraw
        f, t, S = signal.spectrogram(m, SR, nperseg=2048, noverlap=1024)
        S = np.clip((10 * np.log10(S[f < 10000] + 1e-12) + 100) / 80, 0, 1)[::-1]
        im = Image.fromarray((S * 255).astype("u1")).resize((1600, 360)).convert("RGB")
        d = ImageDraw.Draw(im)
        for tm in marks:
            X = int(tm / max(out["duration"], 1e-6) * 1600)
            d.line([(X, 0), (X, 360)], fill=(255, 90, 31))
        im.save(spectrogram_png)
    return out
