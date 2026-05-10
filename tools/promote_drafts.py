"""Promote LLM/manual drafts from _local/llm-drafts/ into event records.

For each *.md file in _local/llm-drafts/, parse the event_id from the leading
HTML comment, find the matching event in data_source/events/*.json, and write
the markdown body (after stripping the comment header) into event.body.

Usage:
    python tools/promote_drafts.py            # promote all
    python tools/promote_drafts.py --only event_xia_dayu_treat_water
    python tools/promote_drafts.py --dry-run
"""
import argparse, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "_local" / "llm-drafts"
EV_DIR = ROOT / "data_source" / "events"

# Comment header lines (event_id / name / year+dynasty) — strip from body.
HEADER_RE = re.compile(r"^<!--.*?-->\s*$", re.MULTILINE)


def parse_draft(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<!--\s*event_id:\s*(\S+)\s*-->", text)
    if not m:
        return None
    event_id = m.group(1).strip()
    body = HEADER_RE.sub("", text).strip() + "\n"
    return event_id, body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="single event id to promote")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Collect drafts.
    drafts: dict[str, str] = {}
    for p in sorted(DRAFTS_DIR.glob("*.md")):
        parsed = parse_draft(p)
        if parsed is None:
            print(f"  SKIP {p.name} (no event_id header)")
            continue
        eid, body = parsed
        if args.only and eid != args.only:
            continue
        drafts[eid] = body
    print(f"loaded {len(drafts)} drafts")

    # Walk events and inject body.
    total_updated = 0
    for ev_file in sorted(EV_DIR.glob("*.json")):
        with ev_file.open("r", encoding="utf-8") as f:
            records = json.load(f)
        changed = 0
        for rec in records:
            body = drafts.get(rec.get("id"))
            if body is None:
                continue
            rec["body"] = body
            changed += 1
        if changed == 0:
            continue
        if not args.dry_run:
            with ev_file.open("w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"  {ev_file.name}: promoted {changed} bodies"
              f"{' (dry-run)' if args.dry_run else ''}")
        total_updated += changed

    print(f"\nTotal events updated: {total_updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
