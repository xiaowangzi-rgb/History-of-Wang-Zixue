"""Build assets/images/_manifest.json with SHA-256 + size for every image.

Walks data_source/images/ and writes the manifest into assets/images/.
The Flutter client uses this for diff-based hot updates of binary assets.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "data_source" / "images"
DST_DIR = ROOT / "assets" / "images"
MANIFEST = DST_DIR / "_manifest.json"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not SRC_DIR.exists():
        print(f"ERROR: {SRC_DIR} not found", file=sys.stderr)
        return 1
    DST_DIR.mkdir(parents=True, exist_ok=True)

    files = []
    total_bytes = 0
    for f in sorted(SRC_DIR.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(SRC_DIR).as_posix()
        size = f.stat().st_size
        files.append({
            "path": rel,
            "sha256": sha256_of(f),
            "size": size,
        })
        total_bytes += size

    manifest = {
        "_version": "v0.6",
        "count": len(files),
        "totalBytes": total_bytes,
        "files": files,
    }
    with MANIFEST.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    mb = total_bytes / 1024 / 1024
    print(f"Wrote {MANIFEST.relative_to(ROOT)}: {len(files)} files, {mb:.2f} MB")
    if mb > 80:
        print(f"WARN  image bundle {mb:.1f} MB > 80 MB target")
    return 0


if __name__ == "__main__":
    sys.exit(main())
