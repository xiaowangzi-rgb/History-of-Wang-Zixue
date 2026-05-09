"""Import persons from raw/images/people-portraits/index.json (532 君主).

Maps each record's `dynasty` (Chinese name) to our dynasty_id + optional regime_id.
Outputs one file per dynasty bucket: data_source/persons/<dynasty_short>.json.

Phase 1 scope:
  - Skip β dynasties (xia/shang/western_zhou/eastern_zhou); those get hand-curated treatment.
  - For non-β dynasties, write all monarchs as Phase 1 placeholders (name + reign + dynastyId).
  - Reign string e.g. "-682~-677" parsed into birthYear/deathYear best-effort
    (we treat reign-start as birthYear placeholder; UI can show reign explicitly).
  - Unmapped dynasties dump to _unmapped.json for manual review.

ID strategy: `person_<dynasty_short>_<name>` with Chinese characters allowed.
Collisions within a dynasty get numeric suffix.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "raw" / "images" / "people-portraits" / "index.json"
OUT_DIR = ROOT / "data_source" / "persons"

SCHEMA_VERSION = "v0.6"
SOURCE = "people-portraits-index"

# β dynasties — skip; they get curated content in Sprint 4
BETA_DYNASTIES = {"dynasty_xia", "dynasty_shang", "dynasty_western_zhou", "dynasty_eastern_zhou"}

# raw dynasty-name → (dynasty_id, regime_id|None, file_short)
# Compound mappings disambiguate based on the parenthetical hint in raw data.
DYNASTY_MAP: dict[str, tuple[str, str | None, str]] = {
    # 朝代主朝
    "夏": ("dynasty_xia", None, "xia"),
    "商": ("dynasty_shang", None, "shang"),
    "西周": ("dynasty_western_zhou", None, "western_zhou"),
    "东周": ("dynasty_eastern_zhou", None, "eastern_zhou"),
    "秦": ("dynasty_qin", None, "qin"),
    "西汉": ("dynasty_western_han", None, "western_han"),
    "新": ("dynasty_xin", None, "xin"),
    "玄汉": ("dynasty_xin", None, "xin"),
    "东汉": ("dynasty_eastern_han", None, "eastern_han"),
    "晋": ("dynasty_western_jin", None, "western_jin"),  # default; reign-disambiguated
    "隋": ("dynasty_sui", None, "sui"),
    "唐": ("dynasty_tang", None, "tang"),
    "周（唐）": ("dynasty_tang", None, "tang"),  # 武周
    "北宋": ("dynasty_song", None, "song"),
    "南宋": ("dynasty_song", None, "song"),
    "大元": ("dynasty_yuan", None, "yuan"),
    "明": ("dynasty_ming", None, "ming"),
    "后金": ("dynasty_qing", None, "qing"),
    "清": ("dynasty_qing", None, "qing"),
    "大清": ("dynasty_qing", None, "qing"),
    "中国民国": ("dynasty_republic", None, "republic"),

    # 三国
    "魏（三国）": ("dynasty_three_kingdoms", "regime_wei", "three_kingdoms"),
    "蜀汉": ("dynasty_three_kingdoms", "regime_shu", "three_kingdoms"),
    "吴（三国）": ("dynasty_three_kingdoms", "regime_wu", "three_kingdoms"),

    # 南北朝
    "魏（南北朝）": ("dynasty_southern_northern", "regime_northern_wei", "southern_northern"),
    "宋（南北朝）": ("dynasty_southern_northern", "regime_song_liu", "southern_northern"),
    "梁": ("dynasty_southern_northern", "regime_liang_southern", "southern_northern"),
    "陈": ("dynasty_southern_northern", "regime_chen", "southern_northern"),
    "周（南北朝）": ("dynasty_southern_northern", "regime_northern_zhou", "southern_northern"),

    # 十六国
    "汉（五胡十六国）": ("dynasty_sixteen_kingdoms", "regime_han_zhao", "sixteen_kingdoms"),
    "夏（五胡十六国）": ("dynasty_sixteen_kingdoms", "regime_hu_xia", "sixteen_kingdoms"),
    "前凉": ("dynasty_sixteen_kingdoms", "regime_former_liang", "sixteen_kingdoms"),
    "前秦": ("dynasty_sixteen_kingdoms", "regime_former_qin", "sixteen_kingdoms"),
    "前燕": ("dynasty_sixteen_kingdoms", "regime_former_yan", "sixteen_kingdoms"),
    "后赵": ("dynasty_sixteen_kingdoms", "regime_later_zhao", "sixteen_kingdoms"),
    "后凉": ("dynasty_sixteen_kingdoms", "regime_later_liang_16", "sixteen_kingdoms"),
    "后秦": ("dynasty_sixteen_kingdoms", "regime_later_qin", "sixteen_kingdoms"),
    "后燕": ("dynasty_sixteen_kingdoms", "regime_later_yan", "sixteen_kingdoms"),
    "西秦": ("dynasty_sixteen_kingdoms", "regime_western_qin", "sixteen_kingdoms"),
    "西凉": ("dynasty_sixteen_kingdoms", "regime_western_liang", "sixteen_kingdoms"),
    "南凉": ("dynasty_sixteen_kingdoms", "regime_southern_liang", "sixteen_kingdoms"),
    "南燕": ("dynasty_sixteen_kingdoms", "regime_southern_yan", "sixteen_kingdoms"),
    "北凉": ("dynasty_sixteen_kingdoms", "regime_northern_liang", "sixteen_kingdoms"),
    "北燕": ("dynasty_sixteen_kingdoms", "regime_northern_yan", "sixteen_kingdoms"),
    "成": ("dynasty_sixteen_kingdoms", "regime_cheng_han", "sixteen_kingdoms"),

    # 五代
    "后梁": ("dynasty_five_dynasties_ten_kingdoms", "regime_later_liang", "five_dynasties"),
    "后唐": ("dynasty_five_dynasties_ten_kingdoms", "regime_later_tang", "five_dynasties"),
    "后晋": ("dynasty_five_dynasties_ten_kingdoms", "regime_later_jin", "five_dynasties"),
    "后汉": ("dynasty_five_dynasties_ten_kingdoms", "regime_later_han", "five_dynasties"),
    "后周": ("dynasty_five_dynasties_ten_kingdoms", "regime_later_zhou", "five_dynasties"),

    # 十国 (no regime defined yet — Phase 1 group under dynasty only)
    "南唐": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "南汉": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "南平": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "前蜀": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "后蜀": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "吴（五代十国）": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "吴越": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "闽": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),
    "楚": ("dynasty_five_dynasties_ten_kingdoms", None, "five_dynasties"),  # 五代十国 马楚

    # 战国 (东周)
    "秦（战国）": ("dynasty_eastern_zhou", "regime_qin_state", "eastern_zhou"),
    "楚（战国）": ("dynasty_eastern_zhou", "regime_chu", "eastern_zhou"),
    "齐（战国）": ("dynasty_eastern_zhou", "regime_qi", "eastern_zhou"),
    "燕（战国）": ("dynasty_eastern_zhou", "regime_yan", "eastern_zhou"),
    "赵（战国）": ("dynasty_eastern_zhou", "regime_zhao", "eastern_zhou"),
    "魏（战国）": ("dynasty_eastern_zhou", "regime_wei_state", "eastern_zhou"),
    "韩（战国）": ("dynasty_eastern_zhou", "regime_han_state", "eastern_zhou"),

    # 春秋诸侯 (东周 — bare names assumed spring-autumn for those with no warring-states variant)
    "齐": ("dynasty_eastern_zhou", "regime_qi_state_sa", "eastern_zhou"),
    "赵": ("dynasty_eastern_zhou", "regime_zhao", "eastern_zhou"),  # ambiguous — bucket warring 赵

    # 辽 / 西夏 / 金 / 西辽 — Phase 1 共置 dynasty_song 时段
    "大契丹国（大辽）": ("dynasty_song", None, "song"),
    "西夏": ("dynasty_song", None, "song"),
    "西辽": ("dynasty_song", None, "song"),
    "金": ("dynasty_song", None, "song"),
    "夏王国（大辽、宋册封）": ("dynasty_song", None, "song"),
    "海陵庶人（金世宗諡）": ("dynasty_song", None, "song"),
    "衛绍王（金宣宗諡）": ("dynasty_song", None, "song"),

    # 边缘条目
    "有穷氏": ("dynasty_xia", None, "xia"),  # 后羿 / 寒浞,夏代
}


REIGN_RE = re.compile(r"^(-?\d+)~(-?\d+)$")


def parse_reign(s: str | None) -> tuple[int | None, int | None]:
    if not s or not isinstance(s, str):
        return None, None
    m = REIGN_RE.match(s.strip())
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def disambiguate_jin(reign_start: int | None, default: tuple[str, str | None, str]) -> tuple[str, str | None, str]:
    """晋 alone: spring-autumn vs western-jin vs eastern-jin by reign year."""
    if reign_start is None:
        return default
    if reign_start < 0:
        return ("dynasty_eastern_zhou", "regime_jin_state_sa", "eastern_zhou")
    if reign_start <= 316:
        return ("dynasty_western_jin", None, "western_jin")
    return ("dynasty_eastern_jin", None, "eastern_jin")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-beta", action="store_true",
                    help="include β dynasties (xia/shang/western_zhou/eastern_zhou) instead of skipping")
    args = ap.parse_args()

    with SRC.open("r", encoding="utf-8") as f:
        records = json.load(f)

    by_file: dict[str, list[dict]] = defaultdict(list)
    unmapped: list[dict] = []
    skipped_beta: list[dict] = []
    seen_ids: dict[str, int] = defaultdict(int)

    for rec in records:
        raw_dyn = rec.get("dynasty")
        name = rec.get("name", "").strip()
        reign = rec.get("reign")
        reign_start, reign_end = parse_reign(reign)

        mapped = DYNASTY_MAP.get(raw_dyn)
        if mapped is None:
            unmapped.append({"raw_dynasty": raw_dyn, "name": name, "reign": reign})
            continue

        # disambiguate 晋 by reign
        if raw_dyn == "晋":
            mapped = disambiguate_jin(reign_start, mapped)

        dynasty_id, regime_id, file_short = mapped

        if dynasty_id in BETA_DYNASTIES and not args.include_beta:
            skipped_beta.append({"raw_dynasty": raw_dyn, "name": name, "reign": reign, "dynasty_id": dynasty_id})
            continue

        # build id; allow Chinese chars (schema relaxed). Strip stray punctuation.
        safe = re.sub(r"[^\w一-鿿\-]+", "", name) or "unknown"
        base_id = f"person_{file_short}_{safe}"
        seen_ids[base_id] += 1
        if seen_ids[base_id] > 1:
            person_id = f"{base_id}_{seen_ids[base_id]}"
        else:
            person_id = base_id

        person: dict = {
            "id": person_id,
            "name": name,
            "dynastyId": dynasty_id,
            "role": "君主",
            "historicity": "historical",
            "_schemaVersion": SCHEMA_VERSION,
            "source": SOURCE,
        }
        if regime_id:
            person["regimeId"] = regime_id
        if reign_start is not None:
            person["reignStart"] = reign_start
            # use reign-start as birthYear placeholder; UI displays reign explicitly
            person["birthYear"] = reign_start
            person["yearUncertainty"] = "year"
        if reign_end is not None:
            person["reignEnd"] = reign_end
            person["deathYear"] = reign_end
        if rec.get("has_portrait"):
            # portrait link will be filled by image-processing pass
            person["_rawPortraitPath"] = rec.get("path")

        by_file[file_short].append(person)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for file_short, items in sorted(by_file.items()):
        items.sort(key=lambda r: (r.get("birthYear") if r.get("birthYear") is not None else 0))
        out = OUT_DIR / f"{file_short}.json"
        with out.open("w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        total += len(items)
        print(f"  {file_short}.json: {len(items)} persons")

    if unmapped:
        with (OUT_DIR / "_unmapped.json").open("w", encoding="utf-8") as f:
            json.dump(unmapped, f, ensure_ascii=False, indent=2)
        print(f"  _unmapped.json: {len(unmapped)} entries (manual review)")

    print(f"Total mapped: {total} persons across {len(by_file)} files")
    print(f"Skipped β dynasties (will be hand-curated): {len(skipped_beta)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
