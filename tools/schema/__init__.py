"""JSON schema loader for data_source/ validation.

Schemas live as plain JSON files alongside this module so they can be
consumed by both Python (jsonschema) and external tooling.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

SCHEMA_DIR = Path(__file__).parent

SCHEMA_FILES = {
    "dynasty": "dynasty.schema.json",
    "regime": "regime.schema.json",
    "event": "event.schema.json",
    "person": "person.schema.json",
}

CURRENT_SCHEMA_VERSION = "v0.6"


def load_schema(name: str) -> dict:
    path = SCHEMA_DIR / SCHEMA_FILES[name]
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_all() -> Dict[str, dict]:
    return {name: load_schema(name) for name in SCHEMA_FILES}
