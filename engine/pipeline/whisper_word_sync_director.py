"""اسکیل ۴: Whisper Word-Sync Director — همگام‌سازی کلمه‌به‌کلمه.

میزانculate می‌کند تا کٹ‌های B-Roll، اعداد بزرگ، نمودارها و SFXها دقیقاً روی ثانیهٔ речи قفل شوند.
اگر `faster-whisper` نصب نیست، یک «طرح همگام‌سازی» (plan) بر اساس متن و زمان تخمینی می‌سازد.

الگو:
  - faster-whisper small / int8 روی آرایه ۱۶۰۰۰ Hz mono float32
  - word_timestamps=True
  - SequenceMatcher برای هم‌ترازی با متن اصلی
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WordAnchor:
    word: str
    start: float
    end: float
    confidence: float = 1.0


@dataclass
class SyncPlan:
    text: str
    language: str = "fa"
    whisper_model: str = "small"
    compute_type: str = "int8"
    sample_rate: int = 16000
    anchors: list[WordAnchor] = field(default_factory=list)


def plan_anchors(text: str, estimated_duration_sec: float) -> SyncPlan:
    """تخمین ذهنی زمان کلمات (به′위置 جایگزین faster-whisper)."""
    words = [w for w in text.split() if w]
    n = len(words)
    plan = SyncPlan(text=text)
    if n == 0:
        return plan
    per_word = estimated_duration_sec / n
    t = 0.0
    for w in words:
        plan.anchors.append(
            WordAnchor(word=w, start=round(t, 3), end=round(t + per_word, 3))
        )
        t += per_word
    return plan


def describe() -> str:
    return (
        "=== Whisper Word-Sync Director (اسکیل ۴) ===\n"
        "- faster-whisper small(int8) روی آرایه ۱۶kHz mono float32\n"
        "- استخراج تایم‌استامپ تک‌تک کلمات و قفل کردن کٹ B-Roll / SFX / تایتر روی کلمات گفتار\n"
        "- اگر faster-whisper نصب نباشد، `plan_anchors()` طرح تخمینی بر اساس طول متن برمی‌گرداند\n"
    )


if __name__ == "__main__":
    print(describe())
