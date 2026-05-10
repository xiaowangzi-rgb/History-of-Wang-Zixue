"""Download Wikimedia portraits from raw/images/emperor-portraits.json,
process to WebP, and link into person records via an alias table.

Usage:
    python tools/download_wikimedia_portraits.py
    python tools/download_wikimedia_portraits.py --skip-download   (use cache)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(2)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "raw" / "images" / "emperor-portraits.json"
CACHE = ROOT / "_local" / "crawl-cache" / "wikimedia"
DST_IMG = ROOT / "data_source" / "images" / "persons"
PERSONS_DIR = ROOT / "data_source" / "persons"

# Map "common name" (in emperor-portraits.json) → (file_short, person_name from index.json)
# We curated this by inspecting raw/images/people-portraits/index.json names.
# Where ambiguous or absent in our person list, the entry is omitted.
ALIASES: dict[str, tuple[str, str]] = {
    # 秦
    "秦始皇": ("qin", "始皇帝"),
    # 西汉
    "汉高祖": ("western_han", "汉太祖"),  # 庙号 vs 谥号
    "汉武帝": ("western_han", "汉世宗"),
    "汉文帝": ("western_han", "汉太宗"),
    "汉景帝": ("western_han", "汉孝景皇帝"),
    "汉宣帝": ("western_han", "汉中宗"),
    "汉光武帝": ("eastern_han", "汉世祖"),
    "汉明帝": ("eastern_han", "汉显宗"),
    "汉章帝": ("eastern_han", "汉肃宗"),
    "汉献帝": ("eastern_han", "汉献帝"),
    # 三国
    "魏武帝": ("three_kingdoms", "魏太祖"),  # 曹操,追尊魏武帝
    "魏文帝": ("three_kingdoms", "魏高祖"),  # 曹丕
    "蜀汉昭烈帝": ("three_kingdoms", "蜀汉烈祖"),
    "刘备": ("three_kingdoms", "蜀汉烈祖"),
    "孙权": ("three_kingdoms", "吴大帝"),
    # 西/东晋
    "晋武帝": ("western_jin", "晋世祖"),
    "晋元帝": ("eastern_jin", "晋中宗"),
    # 隋
    "隋文帝": ("sui", "隋高祖"),
    "隋炀帝": ("sui", "隋世祖"),
    # 唐
    "唐高祖": ("tang", "唐高祖"),
    "唐太宗": ("tang", "唐太宗"),
    "唐高宗": ("tang", "唐高宗"),
    "唐玄宗": ("tang", "唐玄宗"),
    "唐宪宗": ("tang", "唐宪宗"),
    "唐德宗": ("tang", "唐德宗"),
    "唐宣宗": ("tang", "唐宣宗"),
    "武则天": ("tang", "武瞾"),  # raw 庙号 武瞾 (从 周（唐） map 到 tang)
    # 五代
    # 北宋
    "宋太祖": ("song", "宋太祖"),
    "宋太宗": ("song", "宋太宗"),
    "宋真宗": ("song", "宋真宗"),
    "宋仁宗": ("song", "宋仁宗"),
    "宋神宗": ("song", "宋神宗"),
    "宋哲宗": ("song", "宋哲宗"),
    "宋徽宗": ("song", "宋徽宗"),
    "宋钦宗": ("song", "宋钦宗"),
    # 南宋
    "宋高宗": ("song", "宋高宗"),
    "宋孝宗": ("song", "宋孝宗"),
    "宋光宗": ("song", "宋光宗"),
    "宋宁宗": ("song", "宋宁宗"),
    "宋理宗": ("song", "宋理宗"),
    "宋度宗": ("song", "宋度宗"),
    # 元
    "元世祖": ("yuan", "元世祖"),
    "元成宗": ("yuan", "元成宗"),
    "元仁宗": ("yuan", "元仁宗"),
    "成吉思汗": ("yuan", "蒙古太祖"),  # 追尊 元太祖
    "忽必烈": ("yuan", "元世祖"),
    # 明
    "明太祖": ("ming", "明太祖"),
    "明成祖": ("ming", "明成祖"),
    "明仁宗": ("ming", "明仁宗"),
    "明宣宗": ("ming", "明宣宗"),
    "明英宗": ("ming", "明英宗"),
    "明代宗": ("ming", "明代宗"),
    "明宪宗": ("ming", "明宪宗"),
    "明孝宗": ("ming", "明孝宗"),
    "明武宗": ("ming", "明武宗"),
    "明世宗": ("ming", "明世宗"),
    "明穆宗": ("ming", "明穆宗"),
    "明神宗": ("ming", "明神宗"),
    "明光宗": ("ming", "明光宗"),
    "明熹宗": ("ming", "明熹宗"),
    "明思宗": ("ming", "明思宗"),
    # 清
    "努尔哈赤": ("qing", "清太祖"),
    "皇太极": ("qing", "清太宗"),
    "顺治": ("qing", "清世祖"),
    "康熙": ("qing", "清圣祖"),
    "雍正": ("qing", "清世宗"),
    "乾隆": ("qing", "清高宗"),
    "嘉庆": ("qing", "清仁宗"),
    "道光": ("qing", "清宣宗"),
    "咸丰": ("qing", "清文宗"),
    "同治": ("qing", "清穆宗"),
    "光绪": ("qing", "清德宗"),
    "宣统": ("qing", "溥仪"),
    # Variants where common name has 庙号 + 谥号 / 名 — second-pass aliases
    "清世祖顺治": ("qing", "清世祖"),
    "清圣祖康熙": ("qing", "清圣祖"),
    "清世宗雍正": ("qing", "清世宗"),
    "清高宗乾隆": ("qing", "清高宗"),
    "清仁宗嘉庆": ("qing", "清仁宗"),
    "清文宗咸丰": ("qing", "清文宗"),
    "清穆宗同治": ("qing", "清穆宗"),
    "清宣统溥仪": ("qing", "溥仪"),
    "明穆宗朱载坖": ("ming", "明穆宗"),
    "元明宗和世㻋": ("yuan", "元明宗"),
    # 唐 missing emperors
    "唐中宗": ("tang", "唐中宗"),
    "唐睿宗": ("tang", "唐睿宗"),
    "唐肃宗": ("tang", "唐肃宗"),
    "唐代宗": ("tang", "唐代宗"),
    "唐穆宗": ("tang", "唐穆宗"),
    "唐敬宗": ("tang", "唐敬宗"),
    "唐文宗": ("tang", "唐文宗"),
    "唐武宗": ("tang", "唐武宗"),
    "唐懿宗": ("tang", "唐懿宗"),
    "唐僖宗": ("tang", "唐僖宗"),
    "唐昭宗": ("tang", "唐昭宗"),
    # 民国
    "袁世凯": ("republic", "袁世凯"),
}


def slugify(s: str) -> str:
    s = s.strip()
    return re.sub(r"[^\w一-鿿\-]+", "", s) or "unknown"


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


def download(url: str, dst: Path) -> bool:
    if dst.exists() and dst.stat().st_size > 1024:
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "wzxhistory-app/0.1 (educational)"},
            timeout=30,
            allow_redirects=True,
        )
        r.raise_for_status()
        if len(r.content) < 1024:
            return False
        dst.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"FAIL  download {url}: {e}", file=sys.stderr)
        return False


def process(src: Path, main_dst: Path, thumb_dst: Path) -> None:
    with Image.open(src) as im:
        im = im.convert("RGB")
        main = im.copy()
        main.thumbnail((800, 600), Image.LANCZOS)
        main_dst.parent.mkdir(parents=True, exist_ok=True)
        main.save(main_dst, "WEBP", quality=85, method=6)
        thumb = im.copy()
        thumb.thumbnail((200, 200), Image.LANCZOS)
        thumb.save(thumb_dst, "WEBP", quality=78, method=6)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-download", action="store_true")
    args = ap.parse_args()

    with SRC.open("r", encoding="utf-8") as f:
        records = json.load(f)

    DST_IMG.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    updates_by_file: dict[str, dict[str, dict]] = {}
    downloaded = 0
    processed = 0
    matched = 0
    unmatched: list[str] = []

    for rec in records:
        common = rec["name"]
        url = rec["commons_url"]
        cache_path = CACHE / safe_name(rec["image"])

        if not args.skip_download:
            if download(url, cache_path):
                downloaded += 1
                time.sleep(0.3)  # be polite

        if not cache_path.exists() or cache_path.stat().st_size < 1024:
            continue

        alias = ALIASES.get(common)
        if alias is None:
            unmatched.append(common)
            continue

        file_short, person_name = alias
        slug = f"{file_short}_{slugify(person_name)}"
        main_rel = f"persons/{slug}.webp"
        thumb_rel = f"persons/{slug}_thumb.webp"
        main_dst = DST_IMG / f"{slug}.webp"
        thumb_dst = DST_IMG / f"{slug}_thumb.webp"

        # Don't overwrite existing AI-generated portraits unless they are missing.
        # AI ones are higher quality / consistent style.
        if main_dst.exists() and main_dst.stat().st_size > 0:
            # Skip — keep existing AI portrait.
            continue

        try:
            process(cache_path, main_dst, thumb_dst)
            processed += 1
        except Exception as e:
            print(f"FAIL  process {cache_path}: {e}", file=sys.stderr)
            continue

        person_id = f"person_{file_short}_{slugify(person_name)}"
        updates_by_file.setdefault(file_short, {})[person_id] = {
            "portrait": main_rel,
            "_portraitThumb": thumb_rel,
            "portraitSource": "Wikimedia Commons",
            "portraitLicense": "CC-BY-SA / public-domain (per Wikimedia file)",
        }
        matched += 1

    # Apply updates.
    files_changed = 0
    for file_short, person_updates in updates_by_file.items():
        target = PERSONS_DIR / f"{file_short}.json"
        if not target.exists():
            print(f"WARN: {target.name} missing, skipping {len(person_updates)} updates")
            continue
        with target.open("r", encoding="utf-8") as f:
            data = json.load(f)
        applied = 0
        for rec in data:
            upd = person_updates.get(rec.get("id"))
            if upd:
                rec.update(upd)
                applied += 1
        if applied:
            with target.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            files_changed += 1
        unapplied = len(person_updates) - applied
        print(f"  {target.name}: applied {applied}/{len(person_updates)}"
              f"{' (' + str(unapplied) + ' person id mismatch)' if unapplied else ''}")

    print(f"\nDownloaded {downloaded} images, processed {processed}, "
          f"matched {matched} aliases, {files_changed} files changed.")
    if unmatched:
        print(f"\nUnmatched aliases ({len(unmatched)}):")
        for n in unmatched:
            print(f"  - {n}")
        print("Add to ALIASES table and re-run with --skip-download.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
