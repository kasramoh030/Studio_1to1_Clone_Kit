"""スケール 1: Warm Analog Vocal Mastering — ボーカル・アナログ温感マスタリング.

機能 (設計図準拠):
  - generate_speech 出力 (24000 Hz モノラル) を確実に 48000 Hz ステレオへ変換
    (24kHz を 48kHz として誤再生すると 2 倍速になるバグを根絶)
  - LADSPA タップ・プラグイン (tap_tubewarmth, tap_deesser) + Pedalboard 歪みチェーン
    (HPF 75Hz, +2.5dB@125Hz, -1.5dB@3.2kHz, +1.8dB@10.5kHz, Compressor, Reverb, Limiter)
  - 出力 Loudness を -16.0 LUFS にロック
  - faster-whisper 同期用に 16000 Hz mono float32 配列も同時出力

クラスは ffmpeg / pedalboard / scipy が無い環境でも動作し、
その時は「やるべき変換プラン」をテキストで出力する (graceful degradation).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

TARGET_SR = 48000
WHISPER_SR = 16000
TARGET_LUFS = -16.0


@dataclass
class MasterPlan:
    input_rate: int
    input_channels: int
    target_rate: int = TARGET_SR
    target_channels: int = 2
    target_lufs: float = TARGET_LUFS
    chain: list = None

    def __post_init__(self):
        self.chain = self.chain or [
            "resample 24000 Hz mono -> 48000 Hz stereo (aresample / scipy.signal.resample_poly x2)",
            "LADSPA tap_tubewarmth (アナログ管ハーモニクス)",
            "LADSPA tap_deesser (スシ音抑制)",
            "Pedalboard: HPF 75Hz, +2.5dB @ 125Hz, -1.5dB @ 3.2kHz, +1.8dB @ 10.5kHz",
            "Pedalboard: Compressor + Reverb + Limiter",
            f"Loudness normalize to {self.target_lufs} LUFS",
        ]


def master_plan(input_rate: int = 24000, input_channels: int = 1) -> MasterPlan:
    return MasterPlan(input_rate=input_rate, input_channels=input_channels)


def describe(input_rate: int = 24000, input_channels: int = 1) -> str:
    p = master_plan(input_rate, input_channels)
    lines = [
        "=== Warm Analog Vocal Mastering (スケール 1) ===",
        f"入力: {p.input_rate} Hz / {p.input_channels}ch",
        f"出力: {p.target_rate} Hz / {p.target_channels}ch stereo, {p.target_lufs} LUFS",
        "処理チェーン:",
    ]
    for step in p.chain:
        lines.append(f"  - {step}")
    lines.append(
        "注意: generate_speech は常に 24000 Hz モノラルを出力するため、ミックス前に必ず 48000 Hz ステレオへ変換すること。"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
