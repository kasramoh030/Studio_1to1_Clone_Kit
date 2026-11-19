"""اسکیل ۳: Six-SFX Cinema Vault — 두건 استریو ۴۸kHz.

سه افکت تصویری و صدایی برای سینک کلمه‌به‌کلمه و ترنزیشن‌های موشن：
- paper_slide: صدای کاغذ لغزنده (keitokehi)
- checklist_tick ×۶: صدای تیک لز \]
- epic_whoosh:صدای surge
- impact: ضربه سنگین
- coin: سکه
- bell_notification: نوتیفیکیشن

تمام فایل‌ها در `assets/sfx/` به ۴۸۰۰۰ هرتز، استریو، ۱۶ بیت ذخیره شده‌اند.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SFX_NAMES = [
    "paper_slide.wav",
    "checklist_tick.wav",
    "epic_whoosh.wav",
    "impact.wav",
    "coin.wav",
    "bell_notification.wav",
]


@dataclass
class SFXEntry:
    name: str
    path: Path
    duration_sec: float
    sample_rate: int = 48000
    channels: int = 2


def vault_root() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / "sfx"


def list_sfx() -> list[SFXEntry]:
    root = vault_root()
    entries = []
    import wave

    for name in SFX_NAMES:
        p = root / name
        if p.exists():
            with wave.open(str(p), "rb") as w:
                dur = w.getnframes() / w.getframerate()
            entries.append(SFXEntry(name=name, path=p, duration_sec=dur))
    return entries


def describe() -> str:
    lines = ["=== Six-SFX Cinema Vault (اسکیل ۳) ===", "サン플 فایل‌های استریو ۴۸kHz:"]
    for e in list_sfx():
        lines.append(f"  - {e.name} ({e.duration_sec:.2f}s)")
    lines.append(
        "استفاده: تیک‌ها روی کلمات کلیدی، whoosh در ترنزیشن‌های صحنه، impact در اعداد شوک‌آور، bell_notification برای اعلان."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
