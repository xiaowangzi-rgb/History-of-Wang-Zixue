"""Process portrait PNGs and link them into person records.

Walks raw/images/people-portraits/index.json for has_portrait records,
processes each image to data_source/images/persons/<slug>.webp + thumb,
then updates data_source/persons/<dyn_short>.json by setting the matching
person's `portrait` field.

Usage:
    python tools/link_portraits.py
    python tools/link_portraits.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "raw" / "images" / "people-portraits" / "index.json"
PORTRAIT_ROOT = ROOT / "raw" / "images" / "people-portraits"
DST_IMG = ROOT / "data_source" / "images" / "persons"
PERSONS_DIR = ROOT / "data_source" / "persons"

# Mirror import_persons_index.py mapping (subset where portraits actually exist)
DYNASTY_MAP: dict[str, str] = {
    # exact direct map (raw → file_short)
    "夏": "xia",
    "商": "shang",
    "西周": "western_zhou",
    "东周": "eastern_zhou",
    "秦": "qin",
    "西汉": "western_han",
    "新": "xin",
    "玄汉": "xin",
    "东汉": "eastern_han",
    "晋": "western_jin",  # ambiguous default
    "隋": "sui",
    "唐": "tang",
    "周（唐）": "tang",
    "北宋": "song",
    "南宋": "song",
    "大元": "yuan",
    "明": "ming",
    "后金": "qing",
    "清": "qing",
    "大清": "qing",
    "中国民国": "republic",
    "魏（三国）": "three_kingdoms",
    "蜀汉": "three_kingdoms",
    "吴（三国）": "three_kingdoms",
    "魏（南北朝）": "southern_northern",
    "宋（南北朝）": "southern_northern",
    "梁": "southern_northern",
    "陈": "southern_northern",
    "周（南北朝）": "southern_northern",
}


def slugify(s: str) -> str:
    s = s.strip()
    return re.sub(r"[^\w一-鿿\-]+", "", s) or "unknown"


def process(src: Path, main_dst: Path, thumb_dst: Path) -> None:
    with Image.open(src) as im:
        im = im.convert("RGB")
        # main: max 800x600 keeping aspect
        main = im.copy()
        main.thumbnail((800, 600), Image.LANCZOS)
        main_dst.parent.mkdir(parents=True, exist_ok=True)
        main.save(main_dst, "WEBP", quality=85, method=6)
        # thumb: max 200x200
        thumb = im.copy()
        thumb.thumbnail((200, 200), Image.LANCZOS)
        thumb.save(thumb_dst, "WEBP", quality=78, method=6)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with INDEX.open("r", encoding="utf-8") as f:
        records = json.load(f)

    # Group target updates by file_short for batch JSON writes.
    updates_by_file: dict[str, dict[str, dict]] = {}
    processed = 0
    skipped_no_map = 0
    skipped_missing = 0

    for rec in records:
        if not rec.get("has_portrait"):
            continue
        dyn_raw = rec.get("dynasty")
        name = rec.get("name", "").strip()
        images = rec.get("images") or []
        if not images:
            continue
        file_short = DYNASTY_MAP.get(dyn_raw)
        if file_short is None:
            skipped_no_map += 1
            continue

        src = PORTRAIT_ROOT / rec["path"] / images[0]
        if not src.exists():
            skipped_missing += 1
            continue

        slug = f"{file_short}_{slugify(name)}"
        main_rel = f"persons/{slug}.webp"
        thumb_rel = f"persons/{slug}_thumb.webp"
        main_dst = DST_IMG / f"{slug}.webp"
        thumb_dst = DST_IMG / f"{slug}_thumb.webp"

        if args.dry_run:
            print(f"DRY {src.relative_to(ROOT)} → {main_rel}")
        else:
            try:
                process(src, main_dst, thumb_dst)
            except Exception as e:
                print(f"FAIL {src}: {e}", file=sys.stderr)
                continue

        person_id = f"person_{file_short}_{slugify(name)}"
        updates_by_file.setdefault(file_short, {})[person_id] = {
            "portrait": main_rel,
            "_portraitThumb": thumb_rel,
            "portraitSource": "AI 生成",
            "portraitLicense": "CC0",
        }
        processed += 1

    # Apply updates to persons JSON files.
    files_changed = 0
    for file_short, person_updates in updates_by_file.items():
        target = PERSONS_DIR / f"{file_short}.json"
        if not target.exists():
            print(f"WARN: {target} missing, skipping {len(person_updates)} updates")
            continue
        with target.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"WARN: {target} not a list, skipping")
            continue
        applied = 0
        for rec in data:
            upd = person_updates.get(rec.get("id"))
            if upd:
                rec.update(upd)
                applied += 1
        if applied and not args.dry_run:
            with target.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            files_changed += 1
        print(f"  {target.name}: applied {applied}/{len(person_updates)} updates")

    print(f"\nProcessed {processed} portraits, "
          f"{skipped_missing} missing, {skipped_no_map} unmapped. "
          f"Changed {files_changed} JSON files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
