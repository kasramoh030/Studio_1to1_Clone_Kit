#!/usr/bin/env python3
# scripts/make_assets.py — Studio_1to1_Clone_Kit アセット生成スクリプト
# FFmpeg 不要：純粋 NumPy + wave で 48kHz / ステレオ / 16bit WAV を生成。
# 実行: python3 scripts/make_assets.py
import math
import wave
import numpy as np

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if False else None
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)  # リポジトリ ルート
SFX_DIR = os.path.join(ROOT, "assets", "sfx")
MUSIC_DIR = os.path.join(ROOT, "assets", "music")
os.makedirs(SFX_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)


def write_wav(dest_dir, fname, samples):
    """mono (n,) or stereo (n,2) in -1..1 -> 16bit WAV."""
    arr = np.asarray(samples, dtype=np.float64)
    if arr.ndim == 1:
        arr = np.column_stack([arr, arr])
    arr = np.clip(arr, -1.0, 1.0)
    pcm = (arr * 32767).astype(np.int16)
    path = os.path.join(dest_dir, fname)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {path} ({len(pcm)/SR:.2f}s)", flush=True)


def env_adsr(n, attack, decay, sustain, release, sr=SR):
    e = np.full(n, sustain, dtype=np.float64)
    a_n = int(attack * sr); d_n = int(decay * sr); r_n = int(release * sr)
    if a_n > 0: e[:a_n] = np.linspace(0, 1, a_n)
    if d_n > 0 and a_n + d_n <= n: e[a_n:a_n + d_n] = np.linspace(1, sustain, d_n)
    if r_n > 0: e[n - r_n:] = np.linspace(sustain, 0, r_n)
    return e


def apply_reverb(sig, rt=0.6, mix=0.35):
    out = sig.copy()
    for delay_ms, gain in [(29.7, 0.772), (37.1, 0.633), (41.1, 0.541), (43.7, 0.493)]:
        d = int(SR * delay_ms / 1000)
        buf = np.zeros_like(sig)
        buf[d:] = sig[:-d] * gain
        out = out + buf
    return (1 - mix) * sig + mix * out


def bp_noise(n, low, high, seed):
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(n)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    spec = np.fft.rfft(noise)
    spec *= (freqs >= low) & (freqs <= high)
    return np.fft.irfft(spec, n=n)


# ============================ 6 つのシネマティック SFX (48kHz ステレオ) ============================
def paper_slide(dur=0.7):
    n = int(dur * SR); t = np.arange(n) / SR
    sig = bp_noise(n, 700, 4500, 42) * 0.35 + np.sin(2 * np.pi * (800 + 2500 * t / dur)) * 0.15
    sig *= env_adsr(n, 0.05, 0.25, 0.5, 0.35) * np.sin(np.pi * t / dur)
    return sig


def checklist_tick(dur=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    sig = np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 28) + 0.6 * np.sin(2 * np.pi * 4400 * t) * np.exp(-t * 40)
    sig *= env_adsr(n, 0.005, 0.04, 0.3, 0.13)
    return sig


def epic_whoosh(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    banded = bp_noise(n, 300, 9000, 7) * 0.5
    env = np.sin(np.pi * t / dur) ** 2
    sig = banded * env
    sig *= env_adsr(n, 0.15, 0.5, 0.6, 0.4)
    return sig


def impact(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 6)
    body = np.sin(2 * np.pi * 110 * t) * np.exp(-t * 10) * 0.5
    click = bp_noise(n, 2500, 7000, 3) * np.exp(-t * 40) * 0.3
    sig = thump + body + click
    sig = apply_reverb(sig, rt=0.9, mix=0.45)
    sig *= env_adsr(n, 0.02, 0.15, 0.5, 0.6)
    return sig / np.max(np.abs(sig)) * 0.9


def coin(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * 1100 * t) + 0.7 * np.sin(2 * np.pi * 1650 * t)) * np.exp(-t * 14)
    sig += 0.4 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 30)
    sig *= env_adsr(n, 0.002, 0.05, 0.4, 0.2)
    return sig


def bell_notification(dur=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.06 * np.sin(2 * np.pi * 5.5 * t)
    sig = (np.sin(2 * np.pi * 980 * t * vib) + 0.55 * np.sin(2 * np.pi * 1470 * t * vib)) * np.exp(-t * 2.2)
    sig += 0.3 * np.sin(2 * np.pi * 2460 * t * vib) * np.exp(-t * 3.0)
    sig *= env_adsr(n, 0.01, 0.05, 0.85, 0.9)
    return sig


SFX = {
    "paper_slide.wav": paper_slide,
    "checklist_tick.wav": checklist_tick,
    "epic_whoosh.wav": epic_whoosh,
    "impact.wav": impact,
    "coin.wav": coin,
    "bell_notification.wav": bell_notification,
}
for fname, gen in SFX.items():
    write_wav(SFX_DIR, fname, gen())


# ============================ BGM：Italo-Funk 120 BPM (ループ可能) ============================
def italo_funk_bgm(dur_sec=32.0):
    bpm = 120.0
    beat = 60.0 / bpm
    n = int(dur_sec * SR)
    t = np.arange(n) / SR
    mix = np.zeros(n)

    def place(seg_len_beats, start_beat, gen_fn, gain=1.0):
        nonlocal mix
        s = int(start_beat * beat * SR)
        L = int(seg_len_beats * beat * SR)
        e = min(n, s + L)
        if s >= e:
            return
        mix[s:e] += gen_fn(e - s) * gain

    def kick(L):
        tt = np.arange(L) / SR
        f = 60 * np.exp(-tt * 12) + 35
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 22) * 1.1

    def snare(L):
        tt = np.arange(L) / SR
        rng = np.random.default_rng(11)
        return rng.standard_normal(L) * np.exp(-tt * 35) * 0.75 + np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 15) * 0.35

    def hat(L, open_=False, seed=13):
        tt = np.arange(L) / SR
        rng = np.random.default_rng(seed)
        return rng.standard_normal(L) * np.exp(-tt * (8 if open_ else 60)) * (0.45 if open_ else 0.25)

    def bass(L, root):
        tt = np.arange(L) / SR
        f = root * (1 + 0.15 * np.exp(-tt * 10))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3) * 0.5

    def stab(L):
        tt = np.arange(L) / SR
        sig = (np.sin(2 * np.pi * 220 * tt) + np.sin(2 * np.pi * 277.18 * tt) + np.sin(2 * np.pi * 329.63 * tt)) / 3
        return sig * np.exp(-tt * 16) * 0.35

    total_beats = int(dur_sec / beat)
    for b in range(total_beats):
        t0 = b * beat
        pos = b % 4
        if pos == 0 or pos == 2:
            place(0.24, t0, kick, 1.0)
        if pos == 1 or pos == 3:
            place(0.28, t0, snare, 0.8)
        place(0.12, t0, lambda L: hat(L, False, 100 + b), 0.5)
        place(0.12, t0 + beat / 2, lambda L: hat(L, False, 200 + b), 0.4)
        if pos == 3:
            place(0.12, t0 + beat / 2, lambda L: hat(L, True, 300 + b), 0.3)
        root = 55.0 if b % 2 == 0 else 41.20
        place(0.7, t0, lambda L: bass(L, root), 0.7)
        if pos == 0 or pos == 2:
            place(0.36, t0 + 0.06, stab, 0.5)

    fade = int(1.0 * SR)
    mix[:fade] *= np.linspace(0, 1, fade)
    mix[-fade:] *= np.linspace(1, 0, fade)
    return np.clip(mix, -1, 1)


write_wav(MUSIC_DIR, "bgm_italo_funk_120bpm.wav", italo_funk_bgm(32.0))
write_wav(MUSIC_DIR, "bgm_italo_funk_120bpm_short15.wav", italo_funk_bgm(15.0))

print("すべてのアセットを生成しました。")
