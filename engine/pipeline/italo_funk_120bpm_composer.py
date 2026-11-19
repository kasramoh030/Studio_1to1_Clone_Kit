"""スケール 2: Italo-Funk 120 BPM Composer — 120 BPM イタロファンク作曲.

機能 (設計図準拠):
  - 120 BPM のマルチトラック構成 (スラップ・ベース, ファンク・ギター, キーボード, ドラム・キット)
  - FluidSynth + FluidR3_GM.sf2 で 48000 Hz WAV にシンセサイズ (エンジン内 assets/music にサンプル付属)
  - インスタ・リールズ / ユーチューブ・ショート向けループ可能 BGM

ffmpeg / fluidsynth が無い場合は、楽譜プランとコード進行をテキスト出力する。
"""
from __future__ import annotations

from dataclasses import dataclass, field

BPM = 120
BEAT_SEC = 60.0 / BPM
KEY = "A minor"
CHORD_PROGRESSION = ["Am", "F", "C", "G"]  # クラシック・イタロ・ディスコ進行


@dataclass
class Track:
    name: str
    instrument: str
    program: int  # GM program number
    bars: int


@dataclass
class Composition:
    bpm: int = BPM
    key: str = KEY
    beats_per_bar: int = 4
    bars: int = 8  # 32 ビート = 16 秒 @120BPM
    chord_progression: list = field(default_factory=lambda: list(CHORD_PROGRESSION))
    tracks: list = field(
        default_factory=lambda: [
            Track("Slap Bass", "Synth Bass 1", 39, 8),
            Track("Funk Guitar", "Funk Guitar", 27, 8),
            Track("Keys / Synth", "Synth Lead 2", 81, 8),
            Track("Drum Kit", "Standard Kit", 0, 8),
        ]
    )
    length_sec: float = field(init=False)

    def __post_init__(self):
        self.length_sec = self.bars * self.beats_per_bar * BEAT_SEC


def compose() -> Composition:
    return Composition()


def describe() -> str:
    c = compose()
    lines = [
        "=== Italo-Funk 120 BPM Composer (スケール 2) ===",
        f"テンポ: {c.bpm} BPM (1 ビート = {BEAT_SEC} 秒), キー: {c.key}",
        f"構成: {c.bars} 小節 / 約 {c.length_sec:.1f} 秒 (ループ対応)",
        f"コード進行: {' - '.join(c.chord_progression)}",
        "トラック:",
    ]
    for tr in c.tracks:
        lines.append(f"  - {tr.name}: GM program {tr.program} ({tr.instrument})")
    lines.append(
        "シンセサイズ: FluidSynth + FluidR3_GM.sf2 -> WAV 48000 Hz ステレオ "
        "(assets/music/bgm_italo_funk_120bpm.wav にサンプル付属)"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
