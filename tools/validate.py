"""Validate data_source/ contents against schemas + project rules.

Usage:
    python tools/validate.py            # validate all
    python tools/validate.py --strict   # warnings become errors

Rules enforced (beyond JSON schema):
  R1  ID uniqueness within each entity type
  R2  Cross-references resolve (event.dynastyId, event.participants, regime.parentDynastyId, ...)
  R3  _schemaVersion present and matches CURRENT_SCHEMA_VERSION
  R4  Word/char counts (summary 50-1000, body 800-5000 when present)
  R5  Tree topology bidirectional consistency:
        - regime.siblingRegimeIds must be reciprocal
        - parentRegimeId chain must not loop
        - mergedIntoRegimeId must point at an existing regime
  R6  beta deep-dive eras (xia/shang/western_zhou/eastern_zhou_*) require event.body
  R7  source: "llm-draft" forbidden in data_source/ (must be llm-reviewed or human)
  R8  event.year falls inside dynasty [startYear, endYear] (soft warning)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

try:
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

from schema import CURRENT_SCHEMA_VERSION, load_all

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data_source"

BETA_DYNASTY_IDS = {
    "dynasty_xia",
    "dynasty_shang",
    "dynasty_western_zhou",
    "dynasty_eastern_zhou",
}

BODY_MIN = 800
BODY_MAX = 5000
SUMMARY_MIN = 30
SUMMARY_MAX = 1000


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self) -> bool:
        return not self.errors

    def print(self, strict: bool) -> int:
        for w in self.warnings:
            print(f"WARN  {w}")
        for e in self.errors:
            print(f"ERROR {e}")
        bad = len(self.errors) + (len(self.warnings) if strict else 0)
        total = len(self.errors) + len(self.warnings)
        if bad == 0:
            print(f"OK    validate passed ({total} warnings)")
            return 0
        print(f"FAIL  {len(self.errors)} errors, {len(self.warnings)} warnings")
        return 1


# ---------- file loading ----------

def _iter_records(path: Path) -> Iterable[dict]:
    """Each data_source JSON is either a list of records or {records: [...]}."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        yield from data
    elif isinstance(data, dict) and isinstance(data.get("records"), list):
        yield from data["records"]
    else:
        # treat top-level dict as a single record (e.g. a manifest-style file)
        yield data


def load_entity(kind: str) -> List[Tuple[Path, dict]]:
    """Return [(file_path, record), ...] for entity kind under data_source/."""
    out: List[Tuple[Path, dict]] = []
    if kind == "dynasty":
        f = DATA_DIR / "dynasties.json"
        if f.exists():
            for r in _iter_records(f):
                out.append((f, r))
    elif kind == "regime":
        f = DATA_DIR / "regimes.json"
        if f.exists():
            for r in _iter_records(f):
                out.append((f, r))
    elif kind == "event":
        events_dir = DATA_DIR / "events"
        if events_dir.exists():
            for f in sorted(events_dir.glob("*.json")):
                for r in _iter_records(f):
                    out.append((f, r))
    elif kind == "person":
        persons_dir = DATA_DIR / "persons"
        if persons_dir.exists():
            for f in sorted(persons_dir.glob("*.json")):
                for r in _iter_records(f):
                    out.append((f, r))
    return out


# ---------- validators ----------

def validate_schema(schemas: Dict[str, dict], records: Dict[str, list], rep: Report) -> None:
    for kind, items in records.items():
        validator = Draft7Validator(schemas[kind])
        for path, rec in items:
            for err in validator.iter_errors(rec):
                loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
                rid = rec.get("id", "<no-id>")
                rep.err(f"[schema:{kind}] {path.name} {rid} @ {loc}: {err.message}")


def validate_unique_ids(records: Dict[str, list], rep: Report) -> None:
    for kind, items in records.items():
        seen: Dict[str, Path] = {}
        for path, rec in items:
            rid = rec.get("id")
            if not rid:
                continue
            if rid in seen:
                rep.err(f"[unique:{kind}] duplicate id {rid} in {path.name} (also in {seen[rid].name})")
            else:
                seen[rid] = path


def validate_schema_version(records: Dict[str, list], rep: Report) -> None:
    for kind, items in records.items():
        for path, rec in items:
            v = rec.get("_schemaVersion")
            if v is None:
                rep.warn(f"[version:{kind}] {path.name} {rec.get('id','?')} missing _schemaVersion")
            elif v != CURRENT_SCHEMA_VERSION:
                rep.warn(f"[version:{kind}] {path.name} {rec.get('id','?')} _schemaVersion={v} (expected {CURRENT_SCHEMA_VERSION})")


def validate_word_counts(records: Dict[str, list], rep: Report) -> None:
    for kind in ("event", "person"):
        for path, rec in records.get(kind, []):
            rid = rec.get("id", "?")
            s = rec.get("summary")
            if isinstance(s, str):
                if len(s) < SUMMARY_MIN:
                    rep.warn(f"[length:{kind}] {rid} summary {len(s)}<{SUMMARY_MIN}")
                if len(s) > SUMMARY_MAX:
                    rep.err(f"[length:{kind}] {rid} summary {len(s)}>{SUMMARY_MAX}")
            b = rec.get("body")
            if isinstance(b, str) and b.strip():
                if len(b) < BODY_MIN:
                    rep.warn(f"[length:{kind}] {rid} body {len(b)}<{BODY_MIN}")
                if len(b) > BODY_MAX:
                    rep.err(f"[length:{kind}] {rid} body {len(b)}>{BODY_MAX}")


def validate_cross_refs(records: Dict[str, list], rep: Report) -> None:
    dynasty_ids = {r.get("id") for _, r in records.get("dynasty", [])}
    regime_ids = {r.get("id") for _, r in records.get("regime", [])}
    person_ids = {r.get("id") for _, r in records.get("person", [])}

    for path, rec in records.get("regime", []):
        rid = rec.get("id", "?")
        pd = rec.get("parentDynastyId")
        if pd and pd not in dynasty_ids:
            rep.err(f"[xref:regime] {rid} parentDynastyId {pd} not found")
        for fld in ("parentRegimeId", "mergedIntoRegimeId"):
            target = rec.get(fld)
            if target and target not in regime_ids:
                rep.err(f"[xref:regime] {rid} {fld}={target} not found")
        for sib in rec.get("siblingRegimeIds") or []:
            if sib not in regime_ids:
                rep.err(f"[xref:regime] {rid} sibling {sib} not found")

    for path, rec in records.get("event", []):
        rid = rec.get("id", "?")
        d = rec.get("dynastyId")
        if d and d not in dynasty_ids:
            rep.err(f"[xref:event] {rid} dynastyId {d} not found")
        r = rec.get("regimeId")
        if r and r not in regime_ids:
            rep.err(f"[xref:event] {rid} regimeId {r} not found")
        for pid in rec.get("participants") or []:
            if pid not in person_ids:
                rep.warn(f"[xref:event] {rid} participant {pid} not found")

    for path, rec in records.get("person", []):
        rid = rec.get("id", "?")
        d = rec.get("dynastyId")
        if d and d not in dynasty_ids:
            rep.err(f"[xref:person] {rid} dynastyId {d} not found")
        r = rec.get("regimeId")
        if r and r not in regime_ids:
            rep.err(f"[xref:person] {rid} regimeId {r} not found")


def validate_tree_topology(records: Dict[str, list], rep: Report) -> None:
    by_id: Dict[str, dict] = {r.get("id"): r for _, r in records.get("regime", []) if r.get("id")}

    # bidirectional sibling check
    for rid, rec in by_id.items():
        for sib in rec.get("siblingRegimeIds") or []:
            other = by_id.get(sib)
            if other is None:
                continue
            if rid not in (other.get("siblingRegimeIds") or []):
                rep.err(f"[tree] sibling not reciprocal: {rid} -> {sib} but {sib} does not list {rid}")

    # parent chain loop detection
    for rid in by_id:
        seen = set()
        cur = rid
        while cur:
            if cur in seen:
                rep.err(f"[tree] parentRegimeId loop involving {rid}")
                break
            seen.add(cur)
            cur = (by_id.get(cur) or {}).get("parentRegimeId")


def validate_beta_body(records: Dict[str, list], rep: Report) -> None:
    for path, rec in records.get("event", []):
        if rec.get("dynastyId") in BETA_DYNASTY_IDS:
            body = rec.get("body")
            if not body or not str(body).strip():
                rep.err(f"[beta] {rec.get('id','?')} in beta era requires body (file {path.name})")


def validate_no_llm_draft(records: Dict[str, list], rep: Report) -> None:
    for kind, items in records.items():
        for path, rec in items:
            if rec.get("source") == "llm-draft":
                rep.err(f"[source] {kind} {rec.get('id','?')} has source=llm-draft (forbidden in data_source/, file {path.name})")


def validate_event_year_in_dynasty(records: Dict[str, list], rep: Report) -> None:
    by_id: Dict[str, dict] = {r.get("id"): r for _, r in records.get("dynasty", []) if r.get("id")}
    for path, rec in records.get("event", []):
        d = by_id.get(rec.get("dynastyId"))
        if not d:
            continue
        y = rec.get("year")
        if y is None:
            continue
        s, e = d.get("startYear"), d.get("endYear")
        if isinstance(s, int) and isinstance(e, int):
            if y < s or y > e:
                rep.warn(f"[range] event {rec.get('id','?')} year={y} outside dynasty {d.get('id')} [{s},{e}]")


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()

    if not DATA_DIR.exists():
        print(f"ERROR: data_source/ not found at {DATA_DIR}", file=sys.stderr)
        return 2

    schemas = load_all()
    records: Dict[str, list] = {
        kind: load_entity(kind) for kind in ("dynasty", "regime", "event", "person")
    }

    counts = {k: len(v) for k, v in records.items()}
    print(f"Loaded: {counts}")

    rep = Report()
    validate_schema(schemas, records, rep)
    validate_unique_ids(records, rep)
    validate_schema_version(records, rep)
    validate_word_counts(records, rep)
    validate_cross_refs(records, rep)
    validate_tree_topology(records, rep)
    validate_beta_body(records, rep)
    validate_no_llm_draft(records, rep)
    validate_event_year_in_dynasty(records, rep)

    return rep.print(args.strict)


if __name__ == "__main__":
    sys.exit(main())
