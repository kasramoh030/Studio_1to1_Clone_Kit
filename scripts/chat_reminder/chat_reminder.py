#!/usr/bin/env python3
# scripts/chat_reminder/chat_reminder.py
# اسکریپت یادآور محدودیت صفحه (چت) — برای وقتی که صفحه چت به لیمیت توکن می‌رسد
# اجرا: python3 scripts/chat_reminder/chat_reminder.py --check state.json
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

REMINDER_TEMPLATE = """
⏰ یادآور محدودیت صفحه چت

ページ{(page)}: اگر صفحه چت به لیمیت توکن/message_limit برسد و پاسخ قطع شود:

۱. فایل `studio/_handoff/STUDIO_ARCHITECTURE_AND_TRAINING_GUIDE.md` را در چت جدید آپلود کنید
   (یا محتواش را کپی کنید) و پرامپت بخش «پرامپت آمادهٔ کپی برای آموزش به ورک‌اسپیس جدید»
   را به عنوان اولین پیام بفرستید.

۲. اگر فایل `studio/_handoff/MIGRATION_MANIFEST.json` و `studio/_handoff/recover_chat.py`
   وجود دارند، ابتدا `python3 studio/_handoff/recover_chat.py --full-auto` را اجرا کنید
   تا کل ساختار استودیو، فونت‌ها، شیدرها و حافظهٔ ضدتکرار بازیابی شود.

۳. سپس از آخرین نقطه-lasting (Session State Ledger) ادامه دهید:
   `studio/_handoff/SESSION_STATE_LEDGER.json`

تایم یادآور: {timestamp}
وضعیت فعلی: {status}
"""


def load_state(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_reminder(state_path: str | None) -> int:
    state = load_state(state_path) if state_path else {}
    status = state.get("status", "active")
    page = state.get("page", "1")
    print(
        REMINDER_TEMPLATE.format(
            page=page,
            timestamp=datetime.utcnow().isoformat() + "Z",
            status=status,
        )
    )
    if status in ("limit_reached", "limit", "cutoff"):
        print("⚠️  هشدار: وضعیت چت 'limite شده' علامت‌گذاری شده است. از recover_chat.py استفاده کنید.")
        return 1
    print("✅ وضعیت چت salivاری است (active).")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="یادآور محدودیت صفحه چت برای استودیو کپ-producing کلِپ"
    )
    parser.add_argument("--check", metavar="STATE_JSON", help="فایل وضعیت چت برای بررسی")
    args = parser.parse_args(argv)
    return check_reminder(args.check)


if __name__ == "__main__":
    sys.exit(main())
