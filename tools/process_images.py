"""Compress images to WebP (800x600 max + thumbnail) for app distribution.

Reads:  raw/images/people-portraits/<dynasty>/<person>/*.png|*.jpg
Writes: data_source/images/persons/<slug>.webp        (800x600 max)
        data_source/images/persons/<slug>_thumb.webp  (200x200 max)

Usage:
    python tools/process_images.py
    python tools/process_images.py --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
SRC_DIRS = [
    ROOT / "raw" / "images" / "people-portraits",
    ROOT / "_local" / "crawl-cache",
]
DST_DIR = ROOT / "data_source" / "images" / "persons"

MAIN_MAX = (800, 600)
THUMB_MAX = (200, 200)
WEBP_QUALITY = 85
THUMB_QUALITY = 75


def slugify(name: str) -> str:
    """Map '秦始皇' or 'Confucius (Kong Qiu)' to a safe ASCII-ish slug."""
    s = name.strip().lower()
    s = re.sub(r"[^\w一-鿿]+", "_", s, flags=re.UNICODE)
    return s.strip("_")


def process_one(src: Path, dst: Path, max_size: tuple, quality: int) -> None:
    with Image.open(src) as im:
        im = im.convert("RGBA") if im.mode in ("P", "LA") else im.convert("RGB")
        im.thumbnail(max_size, Image.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "WEBP", quality=quality, method=6)


def find_sources() -> list[Path]:
    out: list[Path] = []
    for root in SRC_DIRS:
        if not root.exists():
            continue
        for ext in ("*.png", "*.jpg", "*.jpeg"):
            out.extend(root.rglob(ext))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sources = find_sources()
    if not sources:
        print("No source images found.")
        return 0

    DST_DIR.mkdir(parents=True, exist_ok=True)

    done = 0
    for src in sources:
        # slug from immediate parent dir name (person folder), fallback to filename stem
        person_name = src.parent.name if src.parent.parent.name else src.stem
        slug = slugify(person_name) or slugify(src.stem)
        main_dst = DST_DIR / f"{slug}.webp"
        thumb_dst = DST_DIR / f"{slug}_thumb.webp"

        if args.dry_run:
            print(f"DRY  {src.relative_to(ROOT)} -> {main_dst.relative_to(ROOT)}")
            continue

        try:
            process_one(src, main_dst, MAIN_MAX, WEBP_QUALITY)
            process_one(src, thumb_dst, THUMB_MAX, THUMB_QUALITY)
            done += 1
        except Exception as e:
            print(f"FAIL {src}: {e}", file=sys.stderr)

    print(f"Processed {done}/{len(sources)} images -> {DST_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
