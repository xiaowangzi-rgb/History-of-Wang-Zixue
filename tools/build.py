"""Build assets/data/ from data_source/.

Pipeline:
  1. Run validate.py first; abort on failure (unless --skip-validate).
  2. Copy dynasties.json / regimes.json verbatim.
  3. Merge data_source/events/*.json -> assets/data/events.json (sorted by year).
  4. Merge data_source/persons/*.json -> assets/data/persons.json.
  5. Generate assets/data/manifest.json (SHA-256 + size + schemaVersion).

Usage:
    python tools/build.py
    python tools/build.py --skip-validate
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data_source"
DST = ROOT / "assets" / "data"
SCHEMA_VERSION = "v0.6"
MIN_APP_VERSION = "1.0.0"


def _read_records(path: Path) -> list:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("records"), list):
        return data["records"]
    return [data]


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_validate() -> int:
    print(">> validate")
    return subprocess.call([sys.executable, str(Path(__file__).parent / "validate.py")])


def copy_top(name: str) -> Path | None:
    src = SRC / name
    if not src.exists():
        print(f"-- skip {name} (not present)")
        return None
    dst = DST / name
    shutil.copyfile(src, dst)
    print(f"copy {name}")
    return dst


def merge_dir(name: str, sort_key: str | None) -> Path | None:
    src_dir = SRC / name
    if not src_dir.exists():
        print(f"-- skip {name}/ (not present)")
        return None
    merged: List[dict] = []
    for f in sorted(src_dir.glob("*.json")):
        merged.extend(_read_records(f))
    if sort_key:
        merged.sort(key=lambda r: (r.get(sort_key) is None, r.get(sort_key)))
    dst = DST / f"{name}.json"
    _write_json(dst, merged)
    print(f"merge {name}/ ({len(merged)} records) -> {dst.name}")
    return dst


def write_manifest(files: List[Path]) -> None:
    entries = []
    total = 0
    for f in files:
        if f is None or not f.exists():
            continue
        size = f.stat().st_size
        entries.append({
            "path": f.relative_to(DST).as_posix(),
            "sha256": _sha256(f),
            "size": size,
        })
        total += size
    manifest = {
        "_schemaVersion": SCHEMA_VERSION,
        "_minAppVersion": MIN_APP_VERSION,
        "count": len(entries),
        "totalBytes": total,
        "files": entries,
    }
    _write_json(DST / "manifest.json", manifest)
    print(f"manifest: {len(entries)} files, {total/1024:.1f} KB")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-validate", action="store_true")
    args = ap.parse_args()

    if not SRC.exists():
        print(f"ERROR: {SRC} not found", file=sys.stderr)
        return 2
    DST.mkdir(parents=True, exist_ok=True)

    if not args.skip_validate:
        rc = run_validate()
        if rc != 0:
            print("ABORT  validate failed; rerun with --skip-validate to bypass.", file=sys.stderr)
            return rc

    outputs = [
        copy_top("dynasties.json"),
        copy_top("regimes.json"),
        merge_dir("events", sort_key="year"),
        merge_dir("persons", sort_key="birthYear"),
    ]
    write_manifest([p for p in outputs if p])
    print("BUILD OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
