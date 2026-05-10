"""Fetch portraits for non-monarch persons via Wikipedia REST API.

Strategy: for each person whose Wiki page has a `pageimages` original, download
that image (commons-hosted), process to WebP, and link into the person record.

Targets: persons listed in TARGETS below — primarily 诸子百家 / 文豪 / 重臣 /
近代人物 — that we manually curated in data_source/persons/_non_monarchs.json
plus a few extras we can plausibly find images for.

Usage:
    python tools/fetch_wikipedia_portraits.py
    python tools/fetch_wikipedia_portraits.py --skip-download   (use cache)
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
    print("ERROR: pip install requests", file=sys.stderr)
    sys.exit(2)

try:
    from PIL import Image
except ImportError:
    print("ERROR: pip install Pillow", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "_local" / "crawl-cache" / "wikipedia"
DST_IMG = ROOT / "data_source" / "images" / "persons"
PERSONS_DIR = ROOT / "data_source" / "persons"

# Map: person_id → wikipedia search title (zh)
TARGETS: dict[str, str] = {
    # 诸子百家 / 春秋
    "person_kongzi": "孔子",
    "person_laozi": "老子",
    "person_sunwu": "孙武",
    "person_guanzhong": "管仲",
    # 战国
    "person_mengzi": "孟子",
    "person_zhuangzi": "莊子",
    "person_hanfeizi": "韩非",
    "person_shangyang": "商鞅",
    "person_quyuan": "屈原",
    "person_baiqi": "白起",
    # 秦
    "person_lisi": "李斯",
    # 三国
    "person_zhugeliang": "诸葛亮",
    "person_guanyu": "关羽",
    "person_simayi": "司马懿",
    # 唐
    "person_xuanzang": "玄奘",
    "person_libai": "李白",
    "person_dufu": "杜甫",
    # 宋
    "person_sushi": "苏轼",
    "person_wanganshi": "王安石",
    "person_zhuxi": "朱熹",
    "person_yuefei": "岳飞",
    # 明
    "person_wangyangming": "王阳明",
    "person_zhangjuzheng": "张居正",
    "person_lishizhen": "李时珍",
    # 清
    "person_caoxueqin": "曹雪芹",
    "person_linzexu": "林则徐",
    # 近代
    "person_sunzhongshan": "孙中山",
    "person_luxun": "鲁迅",
    "person_maozedong": "毛泽东",
    "person_zhouenlai": "周恩来",
}


def slugify(s: str) -> str:
    s = s.strip()
    return re.sub(r"[^\w一-鿿\-]+", "", s) or "unknown"


def fetch_pageimage(title: str) -> str | None:
    """Return the original image URL for a zh.wikipedia article, or None."""
    api = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "pageimages",
        "piprop": "original",
        "titles": title,
        "format": "json",
        "redirects": 1,
    }
    try:
        r = requests.get(
            api,
            params=params,
            headers={"User-Agent": "wzxhistory-app/0.1"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"FAIL  api {title}: {e}", file=sys.stderr)
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        original = page.get("original")
        if original and original.get("source"):
            return original["source"]
    return None


def download(url: str, dst: Path) -> bool:
    if dst.exists() and dst.stat().st_size > 1024:
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "wzxhistory-app/0.1"},
            timeout=30,
        )
        r.raise_for_status()
        dst.write_bytes(r.content)
        return True
    except Exception as e:
        print(f"FAIL  dl {url}: {e}", file=sys.stderr)
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

    DST_IMG.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)

    # Build person_id → file_short by scanning existing person files.
    person_to_file: dict[str, str] = {}
    person_records: dict[str, dict] = {}
    for f in sorted(PERSONS_DIR.glob("*.json")):
        with f.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            person_to_file[rec["id"]] = f.stem
            person_records[rec["id"]] = rec

    updates_by_file: dict[str, dict[str, dict]] = {}
    found = 0
    not_found_url = []
    not_found_person = []

    for person_id, title in TARGETS.items():
        if person_id not in person_records:
            not_found_person.append(person_id)
            continue
        rec = person_records[person_id]
        if rec.get("portrait"):
            # Already has a portrait — skip.
            continue

        cache_path = CACHE / f"{slugify(title)}.bin"
        url = None
        if not args.skip_download:
            url = fetch_pageimage(title)
            time.sleep(1.5)
            if url:
                if download(url, cache_path):
                    pass
                else:
                    not_found_url.append(title)
                    continue
            else:
                not_found_url.append(title)
                continue

        if not cache_path.exists() or cache_path.stat().st_size < 1024:
            not_found_url.append(title)
            continue

        # Slug for output: use person_id without "person_" prefix.
        slug = person_id.replace("person_", "")
        main_rel = f"persons/{slug}.webp"
        thumb_rel = f"persons/{slug}_thumb.webp"
        main_dst = DST_IMG / f"{slug}.webp"
        thumb_dst = DST_IMG / f"{slug}_thumb.webp"

        try:
            process(cache_path, main_dst, thumb_dst)
        except Exception as e:
            print(f"FAIL  process {title}: {e}", file=sys.stderr)
            continue

        file_short = person_to_file[person_id]
        updates_by_file.setdefault(file_short, {})[person_id] = {
            "portrait": main_rel,
            "_portraitThumb": thumb_rel,
            "portraitSource": f"Wikipedia: {title}",
            "portraitLicense": "see Wikipedia file page",
        }
        found += 1
        print(f"  ✓ {title} → {main_rel}")

    # Apply updates.
    files_changed = 0
    for file_short, updates in updates_by_file.items():
        target = PERSONS_DIR / f"{file_short}.json"
        with target.open("r", encoding="utf-8") as f:
            data = json.load(f)
        applied = 0
        for rec in data:
            upd = updates.get(rec.get("id"))
            if upd:
                rec.update(upd)
                applied += 1
        if applied:
            with target.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            files_changed += 1
            print(f"  {target.name}: applied {applied}")

    print(f"\nFound {found} portraits, {files_changed} files changed.")
    if not_found_url:
        print(f"\nNo Wikipedia image ({len(not_found_url)}):")
        for t in not_found_url:
            print(f"  - {t}")
    if not_found_person:
        print(f"\nPerson id missing in data_source ({len(not_found_person)}):")
        for p in not_found_person:
            print(f"  - {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
