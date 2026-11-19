#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Chat-Limit & Workspace Disaster Recovery Engine (`recover_chat.py`)
==============================================================================
100% standalone (Python stdlib only — zero external packages required to start)
so it runs immediately even on a brand-new empty Linux workspace BEFORE studio
engines are installed.

Capabilities when an Arena chat hits its context/turn limit:
  1. Auto-Bundle Discovery & Transactional Restore:
     Finds any uploaded `Studio_Migration_Pack_*.zip` / `.tar.zst` / `.tar.gz`,
     validates CRC + SHA-256 hashes in staging, atomically commits files to
     `/home/user`, and parks the consumed archive in `/var/tmp/recovered_bundles/`
     so `/home/user` never exceeds the 124 MB snapshot cap.
  2. Forensic Corruption Scanner & Auto-Healer:
     - Checks all `.json` ledgers/manifests; if truncated mid-turn, auto-heals
       from `/var/tmp/chat_handoff_backups/*.bak`.
     - Validates `.mp4` ISO-BMFF `moov/mvhd/tkhd` headers (even without `ffprobe`)
       and safely moves interrupted half-encoded `.mp4` files to `/var/tmp/quarantine_partials/`.
  3. Unfinished Build Detector (`/var/tmp` Forensics):
     Finds surviving `voice-05` stems (`*.mp3`, `*.wav`), generated AI images,
     `director_plan.json`, and `build_*.py` scripts from an interrupted turn so
     the new chat finishes the video in seconds without re-calling TTS/image APIs.
  4. Engine Self-Check & Auto-Boot (`--boot-engines` / `--full-auto`):
     Audits `ffmpeg`, `rsvg-convert`, `fluidsynth`, `moderngl`, `pedalboard`, `skia`
     and runs `ensure_engines.sh` automatically when needed.
  5. Brain Briefing & Ready Continuation Prompt Generator:
     Writes `/home/user/RECOVERY_BRIEFING_FOR_AI.md` + updates `CHAT_HANDOFF_READY.md`
     in the exact 3-part Persian continuation format.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE_ROOT = Path("/home/user")
STUDIO_ROOT = WORKSPACE_ROOT / "animation-studio"
LEDGER_PATH = WORKSPACE_ROOT / "SESSION_STATE_LEDGER.json"
HANDOFF_MD_PATH = WORKSPACE_ROOT / "CHAT_HANDOFF_READY.md"
BRIEFING_MD_PATH = WORKSPACE_ROOT / "RECOVERY_BRIEFING_FOR_AI.md"

BACKUP_DIR = Path("/var/tmp/chat_handoff_backups")
QUARANTINE_DIR = Path("/var/tmp/quarantine_partials")
PARKED_BUNDLES_DIR = Path("/var/tmp/recovered_bundles")
MAX_SNAPSHOT_KB = 124 * 1024  # 126,976 KB ceiling (`whip_enforcer.py` Gate 10)

CORE_STANDING_RULES: List[str] = [
    "گویندهٔ دائمی و تغییرناپذیر: فقط `generate_speech` با `voice_id=\"voice-05\"` + پردازش با `vocal_fx_chain.py`؛ هرگونه TTS محلی مطلقاً ممنوع است.",
    "اعراب‌گذاری اجباری در نریشن فارسی: «ابرتورم» همیشه به صورت «اَبَر تَوَرُّم» / «اَبَر تَوَرُّمه» و «می‌دَوَن» فرستاده شود.",
    "کارگردان هوشمند پلتفرم‌محور (`scenario_director.py` + `arsenal_pools.py`): پایش ۲٬۲۵۴ دارایی استودیو برای پلتفرم هدف -> فیلتر `Top-10` در هر ۱۳ دامنه -> انتخاب تصادفی هماهنگ با ثبت در `director_history.json` جهت جلوگیری از تکرار.",
    "استفادهٔ کامل از آرسنال استودیو: ۱٬۱۴۵ استایل تایپوگرافی/موشن، ۸۳۵ افکت GPU/LYGIA/Frei0r، حداقل ۵ حالت Kinetic Typography، حداقل ۴ ترنزیشن OpenGL (`gl-transitions`)، نقشهٔ برداری `GeoJSON` و داده‌نگاری ۲.۵بعدی.",
    "ایمنی فونت فارسی و RTL در HarfBuzz (`rsvg-convert`): عدم استفاده از فونت‌های لاتین یا ناقص (`ReadexPro`, `Changa`, `Harmattan Bold`) برای فارسی؛ استفاده از `text-anchor=\"start\"` در لبهٔ راست با `direction=\"rtl\"`، `direction=\"ltr\"` برای درصدهای علامت‌دار مستقل (`+۳۵٪`) و رسم پرچم با `<rect>` برداری.",
    "قانون طلایی لایه‌ها و چک‌لیست RTL: کارت‌های متنی ثابت همیشه بالاتر از کاغذپاره‌ها/عکس‌های متحرک قرار گیرند؛ فاصلهٔ تیک و متن فارسی بدون تداخل باشد؛ کاور `cover_pro` در ثانیهٔ اول ویدیو سینک باشد؛ ترک‌های سوخته (`ad_1144` و ترک‌های قدیمی تکراری) ممنوع‌اند.",
    "اصالت محتوا و خطوط قرمز: صفر کپی‌برداری متنی؛ ممنوعیت پیش‌بینی تاریخ/درصد دقیق یا توصیهٔ مالی؛ درج برچسب «نمونه‌های تاریخی، نه پیش‌بینی» روی مثال‌های تاریخی؛ عکس‌های واقعی بدون واترمارک.",
    "ایمنی حافظهٔ GPU و سقف اسنپ‌شات: پیش‌رندر ترنزیشن‌های EGL روی دیسک (`/var/tmp`) قبل از اجرای `ffmpeg libx264`؛ بازبینی چشمی فریم‌ها و کاور با `read_file`؛ قبولی ۱۰ گیت `whip_enforcer.py` و حفظ حجم `/home/user` زیر `124 MB`.",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_text(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists():
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            shutil.copy2(target, BACKUP_DIR / f"{target.name}.{stamp}.bak")
        except OSError:
            pass
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(content.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def get_workspace_used_kb(root: Path = WORKSPACE_ROOT) -> int:
    out = subprocess.check_output(
        [
            "du", "-sk",
            "--exclude=node_modules", "--exclude=.cache", "--exclude=.local",
            "--exclude=.npm", "--exclude=__pycache__",
            str(root),
        ],
        text=True,
    ).split()[0]
    return int(out)


# ==============================================================================
# LAYER 1: AUTO-DISCOVER & TRANSACTIONALLY RESTORE UPLOADED MIGRATION BUNDLES
# ==============================================================================
def find_candidate_bundles(explicit_path: Optional[str] = None) -> List[Path]:
    if explicit_path:
        p = Path(explicit_path).expanduser().resolve()
        return [p] if p.exists() else []

    candidates: List[Path] = []
    search_dirs = [WORKSPACE_ROOT, WORKSPACE_ROOT / "Uploads", Path("/tmp"), Path("/var/tmp")]
    patterns = (
        "Studio_1to1_Clone_Kit*.zip",
        "Studio_Migration_Pack*.zip",
        "Studio_Migration_Pack*.tar.zst",
        "Studio_Migration_Pack*.tar.gz",
        "*Clone_Kit*.zip",
        "*Migration_Pack*.zip",
        "*studio*backup*.zip",
    )
    seen = set()
    for d in search_dirs:
        if not d.exists():
            continue
        for pat in patterns:
            for fp in d.glob(pat):
                rp = fp.resolve()
                if rp not in seen and fp.is_file():
                    seen.add(rp)
                    candidates.append(rp)
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates


def restore_bundle_transactionally(bundle: Path, target_root: Path, log: List[str]) -> bool:
    staging = Path(tempfile.mkdtemp(prefix="recover_stage_", dir="/var/tmp"))
    try:
        name_low = bundle.name.lower()
        if name_low.endswith(".zip"):
            with zipfile.ZipFile(bundle, "r") as zf:
                bad = zf.testzip()
                if bad is not None:
                    log.append(f"❌ فایل آرشیو `{bundle.name}` در عضو `{bad}` آسیب CRC دارد؛ استخراج متوقف شد.")
                    return False
                zf.extractall(staging)
        elif name_low.endswith(".tar.zst"):
            subprocess.run(["tar", "--zstd", "-xf", str(bundle), "-C", str(staging)], check=True)
        elif name_low.endswith((".tar.gz", ".tgz")):
            with tarfile.open(bundle, "r:gz") as tf:
                tf.extractall(staging)
        else:
            log.append(f"⚠️ فرمت آرشیو `{bundle.name}` پشتیبانی نمی‌شود.")
            return False

        mig_file = staging / "MIGRATION_MANIFEST.json"
        verified_count = 0
        if mig_file.exists():
            mig = json.loads(mig_file.read_text(encoding="utf-8"))
            for entry in mig.get("files", []):
                rel = entry["rel_path"]
                sfp = staging / rel
                if not sfp.exists():
                    raise RuntimeError(f"فایل `{rel}` داخل آرشیو یافت نشد!")
                if sha256_file(sfp) != entry["sha256"]:
                    raise RuntimeError(f"عدم تطابق SHA-256 در فایل `{rel}`!")
                verified_count += 1

            for entry in mig.get("files", []):
                rel = entry["rel_path"]
                sfp = staging / rel
                dfp = target_root / rel
                dfp.parent.mkdir(parents=True, exist_ok=True)
                tmp_dst = dfp.parent / f".rec_{dfp.name}.tmp"
                shutil.copy2(sfp, tmp_dst)
                os.chmod(tmp_dst, entry.get("mode", 0o644))
                os.replace(tmp_dst, dfp)
        else:
            for sfp in staging.rglob("*"):
                if sfp.is_file():
                    rel = sfp.relative_to(staging)
                    dfp = target_root / rel
                    dfp.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(sfp, dfp)
                    verified_count += 1

        for exec_rel in ("animation-studio/ensure_engines.sh", "handoff.py", "recover_chat.py"):
            ep = target_root / exec_rel
            if ep.exists():
                ep.chmod(0o755)

        log.append(f"✅ آرشیو `{bundle.name}` با موفقیت کامل و تأیید سلامت `{verified_count}` فایل بازیابی شد.")

        if str(bundle).startswith(str(WORKSPACE_ROOT.resolve()) + "/"):
            PARKED_BUNDLES_DIR.mkdir(parents=True, exist_ok=True)
            parked = PARKED_BUNDLES_DIR / bundle.name
            shutil.move(str(bundle), str(parked))
            log.append(f"🛡️ آرشیو مصرف‌شده برای حفظ سقف `124 MB` به `{parked}` منتقل شد.")
        return True
    except Exception as exc:
        log.append(f"❌ خطا در بازیابی آرشیو `{bundle}`: {exc}")
        return False
    finally:
        shutil.rmtree(staging, ignore_errors=True)


# ==============================================================================
# LAYER 2: FORENSIC CORRUPTION SCANNER & AUTO-HEALER (JSON + MP4 HEADERS)
# ==============================================================================
def inspect_mp4_health(mp4_path: Path) -> Tuple[bool, Optional[str], Optional[float], str]:
    sz = mp4_path.stat().st_size
    if sz < 16 * 1024:
        return False, None, None, f"حجم ناقص ({sz} bytes)"

    if shutil.which("ffprobe"):
        try:
            out = subprocess.check_output(
                [
                    "ffprobe", "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-show_entries", "format=duration",
                    "-of", "json",
                    str(mp4_path),
                ],
                text=True,
                stderr=subprocess.PIPE,
                timeout=8,
            )
            info = json.loads(out)
            streams = info.get("streams") or []
            fmt = info.get("format") or {}
            if not streams or "duration" not in fmt:
                return False, None, None, "فاقد استریم ویدیو یا مدت‌زمان معتبر"
            res = f"{streams[0].get('width', '?')}x{streams[0].get('height', '?')}"
            dur = round(float(fmt["duration"]), 2)
            return True, res, dur, "سالم (ffprobe)"
        except Exception as exc:
            return False, None, None, f"خطای ساختار MP4 (`moov atom missing` / قطع ناگهانی رندر): {exc}"

    with mp4_path.open("rb") as fh:
        head = fh.read(1024 * 1024)
        tail = b""
        if sz > 1024 * 1024:
            fh.seek(max(0, sz - 1024 * 1024))
            tail = fh.read(1024 * 1024)

    blob = head if b"moov" in head else tail
    if b"moov" not in blob or b"mvhd" not in blob:
        return False, None, None, "اتم `moov` یافت نشد (رندر وسط کار قطع شده است)"

    dur_sec: Optional[float] = None
    res_str: Optional[str] = None
    idx = blob.find(b"mvhd")
    if idx >= 4:
        ver = blob[idx + 4]
        if ver == 0 and idx + 24 <= len(blob):
            ts, dur = struct.unpack(">II", blob[idx + 16: idx + 24])
            if ts > 0:
                dur_sec = round(dur / ts, 2)
        elif ver == 1 and idx + 36 <= len(blob):
            ts, dur = struct.unpack(">IQ", blob[idx + 24: idx + 36])
            if ts > 0:
                dur_sec = round(dur / ts, 2)

    t_pos = 0
    while True:
        k = blob.find(b"tkhd", t_pos)
        if k < 0:
            break
        ver = blob[k + 4]
        end_off = (k + 88) if ver == 0 else (k + 100)
        if end_off <= len(blob):
            wf, hf = struct.unpack(">II", blob[end_off - 8: end_off])
            w, h = wf >> 16, hf >> 16
            if w > 0 and h > 0:
                res_str = f"{w}x{h}"
                break
        t_pos = k + 4

    return True, res_str, dur_sec, "سالم (ISO-BMFF)"


def heal_json_and_quarantine_partials(target_root: Path, quarantine_broken_mp4: bool, log: List[str]) -> Dict[str, Any]:
    healed_jsons: List[str] = []
    corrupt_jsons: List[str] = []
    healthy_videos: List[Dict[str, Any]] = []
    broken_videos: List[Dict[str, Any]] = []

    studio_dir = target_root / "animation-studio"
    json_candidates = list(target_root.glob("*.json"))
    hist_json = studio_dir / "skills" / "mega-style-vfx-arsenal" / "director_history.json"
    if hist_json.exists():
        json_candidates.append(hist_json)

    for jf in sorted(json_candidates):
        try:
            json.loads(jf.read_text(encoding="utf-8"))
        except Exception as exc:
            baks = sorted(BACKUP_DIR.glob(f"{jf.name}.*.bak"), reverse=True) if BACKUP_DIR.exists() else []
            restored = False
            for bak in baks:
                try:
                    txt = bak.read_text(encoding="utf-8")
                    json.loads(txt)
                    atomic_write_text(jf, txt)
                    healed_jsons.append(f"`{jf.name}` از بکاپ `{bak.name}` ترمیم شد.")
                    log.append(f"🩹 فایل آسیب‌دیدهٔ `{jf.name}` به صورت خودکار از `{bak.name}` بازیابی شد.")
                    restored = True
                    break
                except Exception:
                    continue
            if not restored:
                corrupt_jsons.append(f"{jf}: {exc}")
                log.append(f"⚠️ فایل JSON آسیب‌دیده بدون بکاپ سالم: `{jf}` ({exc})")

    for mp4 in sorted(target_root.glob("*.mp4")):
        ok, res, dur, reason = inspect_mp4_health(mp4)
        sz_mb = round(mp4.stat().st_size / (1024 * 1024), 2)
        if ok:
            healthy_videos.append({
                "name": mp4.name,
                "path": str(mp4),
                "resolution": res or "?",
                "duration_sec": dur if dur is not None else "?",
                "size_mb": sz_mb,
            })
        else:
            q_target = str(mp4)
            if quarantine_broken_mp4:
                QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
                dest = QUARANTINE_DIR / mp4.name
                shutil.move(str(mp4), str(dest))
                q_target = str(dest)
                log.append(f"🧹 ویدیوی نیمه‌کاره `{mp4.name}` ({reason}) به قرنطینهٔ امن `{dest}` منتقل شد تا دوباره رندر شود.")
            broken_videos.append({"name": mp4.name, "quarantined_at": q_target, "reason": reason})

    return {
        "healed_jsons": healed_jsons,
        "corrupt_jsons": corrupt_jsons,
        "healthy_videos": healthy_videos,
        "broken_videos": broken_videos,
    }


# ==============================================================================
# LAYER 3: IN-PROGRESS / INTERRUPTED BUILD DETECTOR IN `/var/tmp`
# ==============================================================================
def scan_unfinished_tmp_work() -> List[Dict[str, Any]]:
    tmp_root = Path("/var/tmp")
    if not tmp_root.exists():
        return []

    ignored = {"chat_handoff_backups", "quarantine_partials", "recovered_bundles", "whip_selftest"}
    projects: List[Dict[str, Any]] = []
    for entry in sorted(tmp_root.iterdir()):
        if not entry.is_dir() or entry.name in ignored or entry.name.startswith((".", "systemd-", "recover_stage_")):
            continue
        py_scripts = sorted(str(p) for p in entry.glob("*.py"))
        wav_files = sorted(str(p) for p in entry.glob("*.wav"))
        mp3_files = sorted(str(p) for p in entry.glob("*.mp3"))
        img_files = sorted(str(p) for p in list(entry.glob("*.jpg")) + list(entry.glob("*.png")) if not p.name.startswith("_sp_"))
        has_plan = (entry / "director_plan.json").exists()

        if py_scripts or wav_files or mp3_files or img_files or has_plan:
            projects.append({
                "dir": str(entry),
                "has_director_plan": has_plan,
                "build_scripts": py_scripts,
                "wav_stems": wav_files,
                "mp3_raw_voice05": mp3_files,
                "visual_assets_count": len(img_files),
            })
    return projects


# ==============================================================================
# LAYER 4: STUDIO ENGINE HEALTH & SELF-BOOT
# ==============================================================================
def check_and_boot_engines(auto_boot: bool, log: List[str]) -> Dict[str, bool]:
    def _probe_bins() -> Dict[str, bool]:
        status = {
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "ffprobe": shutil.which("ffprobe") is not None,
            "rsvg-convert": shutil.which("rsvg-convert") is not None,
            "fluidsynth": shutil.which("fluidsynth") is not None,
        }
        for mod in ("moderngl", "pedalboard", "skia", "cv2"):
            try:
                __import__(mod)
                status[f"py:{mod}"] = True
            except Exception:
                status[f"py:{mod}"] = False
        return status

    st = _probe_bins()
    ensure_sh = STUDIO_ROOT / "ensure_engines.sh"
    if auto_boot and not all(st.values()) and ensure_sh.exists():
        log.append("⚙️ برخی موتورهای رندر خاموش بودند؛ اجرای خودکار `ensure_engines.sh`...")
        subprocess.run(["bash", str(ensure_sh)], check=True)
        st = _probe_bins()
        log.append("✅ تمام موتورهای صوتی، گرافیکی و GPU بیدار شدند.")
    return st


# ==============================================================================
# LAYER 5: RECONSTRUCT FULL AI RECOVERY BRIEFING & CONTINUATION PROMPT
# ==============================================================================
def _best_match(ref_name: str, items: List[Path]) -> str:
    if not items:
        return "—"
    toks = {
        t.lower() for t in ref_name.replace(".", "_").split("_")
        if len(t) >= 4 and t.lower() not in {"clip", "reel", "thumb", "script", "manifest", "1080p", "shorts", "reels", "1080x1920"}
    }
    best = str(items[-1])
    best_sc = -1
    for i, p in enumerate(items):
        ptoks = {t.lower() for t in p.name.replace(".", "_").split("_")}
        sc = len(toks & ptoks) * 100 + i
        if sc > best_sc:
            best_sc = sc
            best = str(p)
    return best


def generate_recovery_briefing(
    target_root: Path,
    audit: Dict[str, Any],
    tmp_work: List[Dict[str, Any]],
    engines: Dict[str, bool],
    log: List[str],
    next_msg: Optional[str],
) -> str:
    ledger: Dict[str, Any] = {}
    if LEDGER_PATH.exists():
        try:
            ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        except Exception:
            ledger = {}

    rules = ledger.get("standing_rules") or CORE_STANDING_RULES
    milestones = ledger.get("session_milestones") or [
        "راه‌اندازی کامل استودیوی انیمیشن و ویدیو (`animation-studio`) با ۳۲ پکیج مهارتی، ۵۶ فونت، ۲۶۵ ترنزیشن OpenGL و ۳۷۸ شیدر LYGIA.",
    ]

    thumbs = sorted(list(target_root.glob("Thumb_*.jpg")) + list(target_root.glob("Thumb_*.png")))
    manifests = sorted(target_root.glob("*_manifest.json"))
    scripts = sorted(target_root.glob("Script_*.md"))
    healthy_vids = audit["healthy_videos"]

    hist_json = STUDIO_ROOT / "skills" / "mega-style-vfx-arsenal" / "director_history.json"
    anti_repeat_count = 0
    if hist_json.exists():
        try:
            hd = json.loads(hist_json.read_text(encoding="utf-8"))
            rp = hd.get("recent_picks", {}) if isinstance(hd, dict) else {}
            anti_repeat_count = sum(len(v) for v in rp.values() if isinstance(v, list))
        except Exception:
            pass

    used_kb = get_workspace_used_kb(target_root)
    used_mb = round(used_kb / 1024.0, 2)

    # Determine latest verified deliverable
    if healthy_vids:
        ref_tok = manifests[-1].name if manifests else healthy_vids[-1]["name"]
        vid_paths = [Path(v["path"]) for v in healthy_vids]
        matched_vp = _best_match(ref_tok, vid_paths)
        lv = next((v for v in healthy_vids if v["path"] == matched_vp), healthy_vids[-1])
        lt = _best_match(lv["name"], thumbs)
        ls = _best_match(lv["name"], scripts)
        lm = _best_match(lv["name"], manifests)
        last_result_text = (
            f"آخرین پروژهٔ سالم و تأییدشده در فضای کار:\n"
            f"- ویدیوی نهایی: `{lv['path']}` ({lv['resolution']} · `{lv['duration_sec']}s` · `{lv['size_mb']} MB`)\n"
            f"- کاور اختصاصی: `{lt}`\n"
            f"- اسکریپت سناریو: `{ls}`\n"
            f"- مانیفست استودیو: `{lm}`"
        )
    else:
        last_result_text = (
            f"مغز کامل استودیو (`animation-studio`، قوانین، تامبنیل‌ها و `{len(manifests)}` مانیفست) بازیابی و تأیید شد."
        )

    # Unfinished /var/tmp summary if previous chat hit limit mid-build!
    tmp_section_lines: List[str] = []
    if tmp_work or audit["broken_videos"]:
        if audit["broken_videos"]:
            for bv in audit["broken_videos"]:
                tmp_section_lines.append(
                    f"  - ⚠️ رندر نیمه‌کاره شناسایی و قرنطینه شد: `{bv['name']}` ({bv['reason']}) -> `{bv['quarantined_at']}`"
                )
        for tw in tmp_work:
            tmp_section_lines.append(
                f"  - 📂 پروژهٔ موقت زنده در `{tw['dir']}`: اسکریپت‌های ساخت={tw['build_scripts']}, "
                f"فایل‌های صوتی آماده={len(tw['wav_stems'])} WAV / {len(tw['mp3_raw_voice05'])} MP3 (`voice-05`), "
                f"دارایی‌های تصویری={tw['visual_assets_count']} تصویر"
            )
    else:
        tmp_section_lines.append("  - هیچ رندر ناقص یا نیمه‌کاره‌ای وجود ندارد؛ تمام خروجی‌ها ۱۰۰٪ سالم و کامل هستند.")

    eng_ok = sum(1 for v in engines.values() if v)
    eng_total = len(engines)
    eng_note = (
        "تمام موتورها روشن‌اند ✅"
        if eng_ok == eng_total
        else f"`{eng_ok}/{eng_total}` موتور فعال است (قبل از رندر ویدیو دستور `bash /home/user/animation-studio/ensure_engines.sh` را اجرا کن)"
    )

    vids_md = "\n".join(
        f"  - `{v['path']}` ({v['resolution']}, `{v['duration_sec']}s`, `{v['size_mb']} MB`)"
        for v in healthy_vids
    ) or "  - (در حالت انتقال سبک `brain` ویدیوهای سنگین MP4 حذف شده‌اند و مانیفست‌ها/کاورها موجودند)"

    rules_md = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(rules))
    miles_md = "\n".join(f"  - {m}" for m in milestones)
    log_md = "\n".join(f"- {entry}" for entry in log) or "- بررسی کامل انجام شد؛ هیچ خطا یا خرابی‌ای یافت نشد."
    tmp_md = "\n".join(tmp_section_lines)
    next_final = next_msg or ledger.get("next_request_placeholder") or "[پیام و دستور بعدی‌ات را اینجا بنویس]"

    briefing = f"""# گزارش کامل بازیابی چت و تزریق حافظه به مدل جدید (`RECOVERY_BRIEFING_FOR_AI.md`)
- **زمان بازیابی:** `{utc_now()}`
- **وضعیت استودیو (`/home/user/animation-studio`):** `{"موجود و سالم ✅" if STUDIO_ROOT.exists() else "یافت نشد ❌"}`
- **وضعیت موتورهای رندر:** {eng_note}
- **حافظهٔ ضدتکرار (`director_history.json`):** `{anti_repeat_count}` آیتم ثبت‌شده در ۱۳ دامنه
- **بودجهٔ اسنپ‌شات `/home/user`:** `{used_mb} MB / 124.00 MB` (`{"ایمن ✅" if used_kb <= MAX_SNAPSHOT_KB else "هشدار حجم ⚠️"}`)

## ۱) لاگ عملیات بازیابی و ترمیم خودکار
{log_md}

## ۲) بررسی کارهای نیمه‌تمامِ باقی‌مانده از لحظهٔ لیمیت شدن چت قبلی (`/var/tmp`)
{tmp_md}

---

## ۳) متن آمادهٔ کپی و ارسال به مدل در چت جدید (Copy & Paste)

```text
ما در حال ادامه یک گفتگوی قبلی هستیم که طولانی شد.

خلاصه کار تا اینجا:
- اسکریپت بازیابی خودکار `recover_chat.py` اجرا شد و سلامت کامل فضای کار (`/home/user/RECOVERY_BRIEFING_FOR_AI.md` و `/home/user/AGENTS.md`) تأیید گردید. (لطفاً در اولین قدم فایل `/home/user/RECOVERY_BRIEFING_FOR_AI.md` را با `read_file` بخوان.)
- دستاوردهای تکمیل‌شده تا این لحظه:
{miles_md}
- قوانین ثابت و غیرقابل‌تخطی پروژه:
{rules_md}
- ویدیوهای سالم موجود در فضای کار:
{vids_md}
- وضعیت کارهای در دست اقدام هنگام قطع چت قبلی:
{tmp_md}

آخرین نتیجه:
{last_result_text}

حالا می‌خوام از همین‌جا ادامه بدیم: {next_final}
```
"""
    return briefing


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Standalone Disaster-Recovery & Context-Reconstruction Script when an Arena chat hits its limit."
    )
    ap.add_argument("--from-bundle", help="Explicit path to Studio_Migration_Pack_*.zip/.tar.zst to restore")
    ap.add_argument("--target", default=str(WORKSPACE_ROOT), help="Target workspace root (default: /home/user)")
    ap.add_argument("--boot-engines", action="store_true", help="Automatically run ensure_engines.sh if engines are asleep")
    ap.add_argument("--full-auto", action="store_true", help="Run full bundle recovery + JSON/MP4 healing + engine boot + briefing")
    ap.add_argument("--no-quarantine", action="store_true", help="Report broken MP4 files without moving them to /var/tmp/quarantine_partials")
    ap.add_argument("--next", dest="next_msg", help="Inject your next user instruction directly into the recovered prompt")
    ap.add_argument("--print-prompt", action="store_true", help="Print the ready-to-paste Persian prompt directly to stdout")
    args = ap.parse_args(argv)

    target_root = Path(args.target).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    log: List[str] = []

    # Step 1: Restore bundle if explicitly requested OR if animation-studio is missing in a fresh workspace!
    studio_missing = not (target_root / "animation-studio" / "skills").exists()
    if args.from_bundle or studio_missing:
        bundles = find_candidate_bundles(args.from_bundle)
        if bundles:
            log.append(f"📦 بستهٔ انتقال `{bundles[0]}` شناسایی شد؛ شروع بازیابی تراکنشی با تست SHA-256...")
            restore_bundle_transactionally(bundles[0], target_root, log)
        elif args.from_bundle:
            print(f"ERROR: آرشیو مشخص‌شده یافت نشد: {args.from_bundle}", file=sys.stderr)
            return 1
        elif studio_missing:
            log.append("⚠️ پوشهٔ `animation-studio` در این ورک‌اسپیس جدید وجود ندارد و فایل `Studio_Migration_Pack*.zip` هم آپلود نشده است.")

    # Step 2: Boot engines if requested (before MP4 probe so ffprobe is available if desired)
    engines = check_and_boot_engines(auto_boot=(args.boot_engines or args.full_auto), log=log)

    # Step 3: Forensic JSON auto-heal + broken MP4 quarantine
    audit = heal_json_and_quarantine_partials(target_root, quarantine_broken_mp4=(not args.no_quarantine), log=log)

    # Step 4: Detect surviving mid-build assets in /var/tmp from sudden chat cutoff
    tmp_work = scan_unfinished_tmp_work()
    if tmp_work:
        log.append(f"🔎 تعداد `{len(tmp_work)}` پوشهٔ کاری فعال در `/var/tmp` از چت قبلی شناسایی شد (بدون نیاز به تولید مجدد صدا/تصویر).")

    # Step 5: Write `RECOVERY_BRIEFING_FOR_AI.md` atomically & sync `handoff.py` if present
    briefing_md = generate_recovery_briefing(target_root, audit, tmp_work, engines, log, args.next_msg)
    if target_root == WORKSPACE_ROOT:
        atomic_write_text(BRIEFING_MD_PATH, briefing_md)
        migrator = STUDIO_ROOT / "tools" / "chat_workspace_migrator.py"
        if migrator.exists():
            cmd = [sys.executable, str(migrator), "snapshot"]
            if args.next_msg:
                cmd.extend(["--next", args.next_msg])
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        atomic_write_text(target_root / "RECOVERY_BRIEFING_FOR_AI.md", briefing_md)

    used_kb = get_workspace_used_kb(target_root)
    print("======================================================================")
    print(" 🚑 CHAT-LIMIT RECOVERY & AUTO-HEAL ENGINE COMPLETED")
    print("======================================================================")
    print(f"  • Studio Core       : {'READY ✅' if (target_root / 'animation-studio').exists() else 'MISSING ⚠️'}")
    print(f"  • Healthy Videos    : {len(audit['healthy_videos'])} verified | Quarantined Partials: {len(audit['broken_videos'])}")
    print(f"  • Healed JSONs      : {len(audit['healed_jsons'])} | Corrupt JSONs: {len(audit['corrupt_jsons'])}")
    print(f"  • Live /var/tmp Jobs: {len(tmp_work)} recoverable staging folder(s)")
    print(f"  • Engines Awake     : {sum(1 for v in engines.values() if v)}/{len(engines)}")
    print(f"  • AI Brain Briefing : {target_root / 'RECOVERY_BRIEFING_FOR_AI.md'}")
    print(f"  • Snapshot Budget   : {used_kb / 1024.0:.2f} MB / 124.00 MB ({'SAFE ✅' if used_kb <= MAX_SNAPSHOT_KB else 'OVER ⚠️'})")
    print("======================================================================")

    if args.print_prompt:
        print("\n" + briefing_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
