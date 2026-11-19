---
name: video-editing-kit
description: Local-first editorial kit — 15 skills (story-editor, cut-audit, render-review, motion-overlay, platform-package, format-repurposer, style-memory, video-semantic-search, broll-curator, color-match, audio-finisher, asset-plan, vlog-editor, video-editor, watch) plus 10 production templates and verified FFmpeg/Python helpers.
---

# Video Editing Kit (۱۵ مهارت + ۱۰ قالب + اسکریپت‌های اعتبارسنجی‌شده)

منبع: `https://github.com/prathameshp107/video-editing`

## مهارت‌ها
`story-editor` · `cut-audit` · `render-review` · `motion-overlay` · `platform-package` · `format-repurposer` · `style-memory` · `video-semantic-search` · `broll-curator` · `color-match` · `audio-finisher` · `asset-plan` · `vlog-editor` · `video-editor` · `watch`

> `voiceover-generator` (Chatterbox محلی) **حذف شد** — نقض قانون `voice-05`.

## قالب‌های تولید (در `templates/`)
`BRIEF.md` · `STORYBOARD.md` · `MOTION_PLAN.md` · `ASSET_PLAN.md` · `SHOT_LOG.csv` · `EDIT_DECISIONS.csv` · `CUT_AUDIT.md` · `REVIEW.md` · `PLATFORM_PACKAGE.md` · `STYLE.md`

## اسکریپت‌های QA (در `scripts/`)
`check_edit_plan.py` · `audit_visual_beats.py` · `verify_export.py` · `review_contact_sheet.py` · `color_compare.py` · `audio_finish.py` · `make_thumbnail.py` · `make_short.py` · `make_format.py` · `match_timeline.py` · `check_chapters.py` · `curate_broll.py` · `scan_media.py` · `index_media.py`

## استفاده
- **قبل از رندر**: `STORYBOARD.md` + `MOTION_PLAN.md` + `EDIT_DECISIONS.csv` را پر کن.
- **بعد از رندر**: `audit_visual_beats.py` و `review_contact_sheet.py` برای بازرسی، `verify_export.py` برای صحت کدک/مدت/لودنس.
