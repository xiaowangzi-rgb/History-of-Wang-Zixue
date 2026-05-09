"""Import dynasties + regimes from raw/dynasties/dynasties-wxh06.json.

wxh06 covers 西周→现代。This script:
  - groups its 57 rows into 25 top-level dynasties (4.1)
  - emits the regimes (4.2): 三国 / 十六国 / 南北朝 / 五代 from wxh06
  - manually adds 传说时代 / 夏 / 商 / 民国 / 新中国 (wxh06 missing)
  - manually adds 战国七雄 + 春秋诸侯 (wxh06 missing)
  - injects v0.6 fields: color/colorDark (from docs/dynasty-palette.md),
    historicity, _yearAuthority, parentDynastyId, parentRegimeId, ...

Outputs:
  data_source/dynasties.json   (~25 records)
  data_source/regimes.json     (~40+ records)

Re-runnable: overwrites the output files.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
WXH06 = ROOT / "raw" / "dynasties" / "dynasties-wxh06.json"
OUT_DYNASTIES = ROOT / "data_source" / "dynasties.json"
OUT_REGIMES = ROOT / "data_source" / "regimes.json"

SCHEMA_VERSION = "v0.6"
SOURCE = "wxh06+manual"
YEAR_AUTHORITY = "夏商周断代工程"


# ---------- color palette (mirror of docs/dynasty-palette.md) ----------

DYNASTY_COLORS = {
    "dynasty_legendary": ("#A8A29C", "#7A6A6A"),
    "dynasty_xia": ("#B97A56", "#D49678"),
    "dynasty_shang": ("#8B6F47", "#A88B5F"),
    "dynasty_western_zhou": ("#C04848", "#D86060"),
    "dynasty_eastern_zhou": ("#A89858", "#C2B070"),
    "dynasty_qin": ("#2D2A26", "#4A4540"),
    "dynasty_western_han": ("#B8473C", "#D45C50"),
    "dynasty_xin": ("#997A5C", "#B59070"),
    "dynasty_eastern_han": ("#A04E45", "#BC665D"),
    "dynasty_three_kingdoms": ("#5C6F94", "#7589AB"),
    "dynasty_western_jin": ("#6B4F75", "#85688E"),
    "dynasty_eastern_jin": ("#806F94", "#9888AC"),
    "dynasty_sixteen_kingdoms": ("#8C6B4B", "#A8856A"),
    "dynasty_southern_northern": ("#A89858", "#C2B070"),
    "dynasty_sui": ("#3F5B7C", "#5C7898"),
    "dynasty_tang": ("#C84E4E", "#E07070"),
    "dynasty_five_dynasties_ten_kingdoms": ("#806147", "#997D62"),
    "dynasty_song": ("#5E8970", "#7AA38B"),
    "dynasty_yuan": ("#3F4F7C", "#5C6E98"),
    "dynasty_ming": ("#B85D6E", "#D27689"),
    "dynasty_qing": ("#4A6E8C", "#688AAB"),
    "dynasty_republic": ("#6E7B82", "#8A969D"),
    "dynasty_prc_pre_reform": ("#4A4A4A", "#6A6A6A"),
}

# Three-kingdoms / Northern-Southern / Sixteen-kingdoms / Five-dynasties regime colors
REGIME_COLORS = {
    "regime_wei": ("#5C6F94", "#7589AB"),
    "regime_shu": ("#4A7858", "#6A9477"),
    "regime_wu": ("#6189A6", "#7CA4C0"),
    "regime_northern_wei": ("#A89858", "#C2B070"),
    "regime_eastern_wei": ("#928550", "#AE9F68"),
    "regime_western_wei": ("#9E8F58", "#B8A875"),
    "regime_northern_qi": ("#7B8A52", "#97A66E"),
    "regime_northern_zhou": ("#8C7C50", "#A8966A"),
    "regime_song_liu": ("#5E7B6E", "#7A9788"),
    "regime_qi_southern": ("#6E8A7A", "#8AA697"),
    "regime_liang_southern": ("#7A9582", "#94B09D"),
    "regime_chen": ("#6E8E7E", "#8AAA9A"),
    "regime_later_liang": ("#806147", "#997D62"),
    "regime_later_tang": ("#A05B47", "#B87862"),
    "regime_later_jin": ("#7A6B5C", "#94867A"),
    "regime_later_han": ("#8B5C4F", "#A47A6C"),
    "regime_later_zhou": ("#5C7B6F", "#7A9888"),
    # Warring states 7 (Phase 1 manual)
    "regime_qin_state": ("#3D3A36", "#5A5550"),
    "regime_chu": ("#5C7A4F", "#7A9870"),
    "regime_qi": ("#A88E5F", "#C2A878"),
    "regime_yan": ("#5A6B85", "#7889A0"),
    "regime_zhao": ("#8A6B7A", "#A88898"),
    "regime_wei_state": ("#9D6B5C", "#B68674"),
    "regime_han_state": ("#6F8C8E", "#8AA8AA"),
    # Spring-autumn (Phase 1 manual)
    "regime_lu": ("#A88E5F", "#C2A878"),
    "regime_qi_state_sa": ("#5A6B85", "#7889A0"),
    "regime_jin_state_sa": ("#6F8C8E", "#8AA8AA"),
    "regime_chu_state_sa": ("#5C7A4F", "#7A9870"),
    "regime_qin_state_sa": ("#3D3A36", "#5A5550"),
    "regime_song_state": ("#7A8B6F", "#94A589"),
    "regime_wu_state": ("#6189A6", "#7CA4C0"),
    # Sixteen kingdoms (uniform light brown family, distinguishable)
    "regime_han_zhao": ("#8C6B4B", "#A8856A"),
    "regime_cheng_han": ("#9A7858", "#B69077"),
    "regime_former_liang": ("#A89072", "#C2A88C"),
    "regime_later_zhao": ("#7A5A40", "#94765C"),
    "regime_former_yan": ("#8E7A5C", "#A89478"),
    "regime_former_qin": ("#8C6F50", "#A8896E"),
    "regime_later_yan": ("#7E6A50", "#9A866E"),
    "regime_later_qin": ("#85684C", "#A0846A"),
    "regime_western_qin": ("#94785C", "#AE9078"),
    "regime_later_liang_16": ("#705840", "#8C7560"),
    "regime_southern_liang": ("#7C6850", "#988570"),
    "regime_northern_liang": ("#82704F", "#9C8A6E"),
    "regime_southern_yan": ("#86684A", "#A0846A"),
    "regime_western_liang": ("#90785A", "#AC9276"),
    "regime_hu_xia": ("#754F38", "#906A55"),
    "regime_northern_yan": ("#7E6850", "#9A866E"),
}


# ---------- helpers ----------

def _year(v: Any) -> int:
    """wxh06 uses int year OR [year, month, day?]. Return int year only."""
    if isinstance(v, list):
        return int(v[0])
    return int(v)


def load_wxh06() -> list:
    with WXH06.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def dyn(id_: str, name: str, sy: int, ey: int, **kw) -> dict:
    color, color_dark = DYNASTY_COLORS[id_]
    rec = {
        "id": id_,
        "name": name,
        "startYear": sy,
        "endYear": ey,
        "color": color,
        "colorDark": color_dark,
        "yearUncertainty": kw.pop("yearUncertainty", "year"),
        "_yearAuthority": kw.pop("_yearAuthority", YEAR_AUTHORITY),
        "historicity": kw.pop("historicity", "historical"),
        "_schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
    }
    rec.update(kw)
    return rec


def reg(id_: str, name: str, sy: int, ey: int, parent_dynasty: str, **kw) -> dict:
    color, color_dark = REGIME_COLORS[id_]
    rec = {
        "id": id_,
        "name": name,
        "startYear": sy,
        "endYear": ey,
        "color": color,
        "colorDark": color_dark,
        "parentDynastyId": parent_dynasty,
        "yearUncertainty": kw.pop("yearUncertainty", "year"),
        "_schemaVersion": SCHEMA_VERSION,
        "source": SOURCE,
    }
    rec.update(kw)
    return rec


# ---------- build dynasties ----------

def _index(rows: list) -> dict:
    """Index by (group, name) -> (sy, ey), keeping the FIRST occurrence.

    Some keys repeat in wxh06 (e.g. 汉/西汉 has two segments around 新莽);
    we want the first segment for top-level dynasty bounds.
    """
    by: dict = {}
    for r in rows:
        k = (r[0], r[1])
        if k not in by:
            by[k] = (_year(r[2]), _year(r[3]))
    return by


def build_dynasties(rows: list) -> list:
    by = _index(rows)

    out: list[dict] = []

    # 1. Legendary (manual, fuzzy era)
    out.append(dyn(
        "dynasty_legendary", "传说时代", -2500, -2070,
        yearUncertainty="era", historicity="legendary",
        _yearAuthority="传说,无定论",
    ))

    # 2. Xia / Shang (manual, 夏商周断代工程)
    out.append(dyn("dynasty_xia", "夏", -2070, -1600, historicity="semi-historical", yearUncertainty="century"))
    out.append(dyn("dynasty_shang", "商", -1600, -1046, historicity="semi-historical", yearUncertainty="century"))

    # 3. Western/Eastern Zhou (wxh06 has 周/西周, 周/东周)
    sy, ey = by[("周", "西周")]
    out.append(dyn("dynasty_western_zhou", "西周", sy, ey, historicity="historical"))
    sy, ey = by[("周", "东周")]
    out.append(dyn("dynasty_eastern_zhou", "东周", sy, ey, historicity="historical",
                   summary="春秋(前770-前476)+ 战国(前475-前221)合并为东周。"))

    # 4. Qin (秦/秦; 西楚 是 regime, 不是 top dynasty)
    sy, ey = by[("秦", "秦")]
    out.append(dyn("dynasty_qin", "秦", sy, ey))

    # 5. Western Han / Xin / Eastern Han (wxh06 splits 西汉 into two ranges + 新)
    sy, _ = by[("汉", "西汉")]
    # endYear of western han = end of second 西汉 segment (24,25 reign of 更始帝); use 9 (start of 新) as end
    out.append(dyn("dynasty_western_han", "西汉", sy, 9))
    sy, ey = by[("汉", "新")]
    out.append(dyn("dynasty_xin", "新莽", sy, ey))
    sy, ey = by[("汉", "东汉")]
    out.append(dyn("dynasty_eastern_han", "东汉", sy, ey))

    # 6. Three Kingdoms (overall envelope 220-280 = max of 魏蜀吴 ranges)
    out.append(dyn("dynasty_three_kingdoms", "三国", 220, 280,
                   summary="魏/蜀/吴并立,详见 regimes。"))

    # 7. Jin (Western + Eastern as two top dynasties — both clearly distinct)
    sy, ey = by[("晋", "西晋")]
    out.append(dyn("dynasty_western_jin", "西晋", sy, ey))
    sy, ey = by[("晋", "东晋")]
    out.append(dyn("dynasty_eastern_jin", "东晋", sy, ey))

    # 8. Sixteen Kingdoms (envelope 304-439)
    out.append(dyn("dynasty_sixteen_kingdoms", "十六国", 304, 439,
                   summary="北方 16 国并立,详见 regimes。"))

    # 9. Southern-Northern (envelope 420-589 = 南朝 start to 陈 end)
    out.append(dyn("dynasty_southern_northern", "南北朝", 420, 589,
                   summary="南朝(宋齐梁陈)+ 北朝(北魏分裂为东西魏 → 北齐北周),详见 regimes。"))

    # 10. Sui
    sy, ey = by[("隋", "隋")]
    out.append(dyn("dynasty_sui", "隋", sy, ey))

    # 11. Tang
    sy, ey = by[("唐", "唐")]
    out.append(dyn("dynasty_tang", "唐", sy, ey))

    # 12. Five Dynasties Ten Kingdoms (envelope 907-960; ten kingdoms partly overlap)
    out.append(dyn("dynasty_five_dynasties_ten_kingdoms", "五代十国", 907, 979,
                   summary="北方五代相继 + 南方十国并立,详见 regimes。"))

    # 13. Song (北宋+南宋 合并)
    sy_n, _ = by[("宋", "北宋")]
    _, ey_s = by[("宋", "南宋")]
    out.append(dyn("dynasty_song", "宋", sy_n, ey_s,
                   summary="北宋(960-1127)+ 南宋(1127-1279)合并显示,与辽/西夏/金并立。"))

    # 14. Yuan (蒙古 → 元 → 北元)
    sy, _ = by[("元", "蒙古")]
    _, ey = by[("元", "北元")]
    out.append(dyn("dynasty_yuan", "元", sy, ey,
                   summary="蒙古(1206-1271)→ 元(1271-1368)→ 北元(1368-1388)。"))

    # 15. Ming (明 + 南明)
    sy, _ = by[("明", "明")]
    _, ey = by[("明", "南明")]
    out.append(dyn("dynasty_ming", "明", sy, ey))

    # 16. Qing (后金 → 清)
    sy, _ = by[("清", "后金")]
    _, ey = by[("清", "清")]
    out.append(dyn("dynasty_qing", "清", sy, ey))

    # 17. Republic + 18. PRC pre-reform (manual)
    out.append(dyn("dynasty_republic", "中华民国", 1912, 1949, yearUncertainty="exact"))
    out.append(dyn("dynasty_prc_pre_reform", "新中国(1949-1978)", 1949, 1978, yearUncertainty="exact"))

    return out


# ---------- build regimes ----------

def build_regimes(rows: list) -> list:
    by = _index(rows)
    out: list[dict] = []

    # Three Kingdoms
    sy, ey = by[("三国", "魏")]; out.append(reg("regime_wei", "曹魏", sy, ey, "dynasty_three_kingdoms", siblingRegimeIds=["regime_shu","regime_wu"]))
    sy, ey = by[("三国", "蜀")]; out.append(reg("regime_shu", "蜀汉", sy, ey, "dynasty_three_kingdoms", siblingRegimeIds=["regime_wei","regime_wu"]))
    sy, ey = by[("三国", "吴")]; out.append(reg("regime_wu", "东吴", sy, ey, "dynasty_three_kingdoms", siblingRegimeIds=["regime_wei","regime_shu"]))

    # Northern dynasties (Northern Wei → split into Eastern + Western Wei → Northern Qi/Zhou)
    sy, ey = by[("北朝", "北魏")]; out.append(reg("regime_northern_wei", "北魏", sy, ey, "dynasty_southern_northern"))
    sy, ey = by[("北朝", "东魏")]; out.append(reg("regime_eastern_wei", "东魏", sy, ey, "dynasty_southern_northern", parentRegimeId="regime_northern_wei", mergedIntoRegimeId="regime_northern_qi"))
    sy, ey = by[("北朝", "西魏")]; out.append(reg("regime_western_wei", "西魏", sy, ey, "dynasty_southern_northern", parentRegimeId="regime_northern_wei", mergedIntoRegimeId="regime_northern_zhou"))
    sy, ey = by[("北朝", "北齐")]; out.append(reg("regime_northern_qi", "北齐", sy, ey, "dynasty_southern_northern", parentRegimeId="regime_eastern_wei"))
    sy, ey = by[("北朝", "北周")]; out.append(reg("regime_northern_zhou", "北周", sy, ey, "dynasty_southern_northern", parentRegimeId="regime_western_wei"))

    # Southern dynasties
    sy, ey = by[("南朝", "宋")]; out.append(reg("regime_song_liu", "刘宋", sy, ey, "dynasty_southern_northern"))
    sy, ey = by[("南朝", "齐")]; out.append(reg("regime_qi_southern", "南齐", sy, ey, "dynasty_southern_northern", parentRegimeId="regime_song_liu"))
    sy, ey = by[("南朝", "梁")]; out.append(reg("regime_liang_southern", "南梁", sy, ey, "dynasty_southern_northern", parentRegimeId="regime_qi_southern"))
    sy, ey = by[("南朝", "陈")]; out.append(reg("regime_chen", "陈", sy, ey, "dynasty_southern_northern", parentRegimeId="regime_liang_southern"))

    # Sixteen Kingdoms (16, after merging the two 西秦 segments)
    sk_map = [
        ("regime_han_zhao", "汉赵", "汉赵"),
        ("regime_cheng_han", "成汉", "成汉"),
        ("regime_former_liang", "前凉", "前凉"),
        ("regime_later_zhao", "后赵", "后赵"),
        ("regime_former_yan", "前燕", "前燕"),
        ("regime_former_qin", "前秦", "前秦"),
        ("regime_later_yan", "后燕", "后燕"),
        ("regime_later_qin", "后秦", "后秦"),
        # 西秦 has two ranges in wxh06 (385-400, 409-431); union them
        ("regime_western_qin", "西秦", "西秦"),
        ("regime_later_liang_16", "后凉", "后凉"),
        ("regime_southern_liang", "南凉", "南凉"),
        ("regime_northern_liang", "北凉", "北凉"),
        ("regime_southern_yan", "南燕", "南燕"),
        ("regime_western_liang", "西凉", "西凉"),
        ("regime_hu_xia", "胡夏", "胡夏"),
        ("regime_northern_yan", "北燕", "北燕"),
    ]
    for rid, name, src_name in sk_map:
        if src_name == "西秦":
            # union the two segments
            sy = 385; ey = 431
        else:
            sy, ey = by[("十六国", src_name)]
        out.append(reg(rid, name, sy, ey, "dynasty_sixteen_kingdoms"))

    # Five Dynasties (the five northern, sequential — parentRegimeId chain)
    five = [
        ("regime_later_liang", "后梁", None),
        ("regime_later_tang", "后唐", "regime_later_liang"),
        ("regime_later_jin", "后晋", "regime_later_tang"),
        ("regime_later_han", "后汉", "regime_later_jin"),
        ("regime_later_zhou", "后周", "regime_later_han"),
    ]
    for rid, name, parent in five:
        sy, ey = by[("五代十国", name)]
        kw = {"parentRegimeId": parent} if parent else {}
        out.append(reg(rid, name, sy, ey, "dynasty_five_dynasties_ten_kingdoms", **kw))

    # Warring States 7 (manual; wxh06 missing)
    ws7 = [
        ("regime_qin_state", "秦"),
        ("regime_chu", "楚"),
        ("regime_qi", "齐"),
        ("regime_yan", "燕"),
        ("regime_zhao", "赵"),
        ("regime_wei_state", "魏"),
        ("regime_han_state", "韩"),
    ]
    ws7_ids = [r[0] for r in ws7]
    for rid, name in ws7:
        siblings = [x for x in ws7_ids if x != rid]
        out.append(reg(rid, name, -475, -221, "dynasty_eastern_zhou", siblingRegimeIds=siblings))

    # Spring-Autumn major 7 (manual)
    sa7 = [
        ("regime_lu", "鲁"),
        ("regime_qi_state_sa", "齐"),
        ("regime_jin_state_sa", "晋"),
        ("regime_chu_state_sa", "楚"),
        ("regime_qin_state_sa", "秦"),
        ("regime_song_state", "宋"),
        ("regime_wu_state", "吴"),
    ]
    sa7_ids = [r[0] for r in sa7]
    for rid, name in sa7:
        siblings = [x for x in sa7_ids if x != rid]
        out.append(reg(rid, name, -770, -476, "dynasty_eastern_zhou", siblingRegimeIds=siblings))

    return out


# ---------- main ----------

def main() -> int:
    rows = load_wxh06()
    dynasties = build_dynasties(rows)
    regimes = build_regimes(rows)

    # back-fill regimeIds onto dynasties
    by_dyn: dict[str, list[str]] = {}
    for r in regimes:
        by_dyn.setdefault(r["parentDynastyId"], []).append(r["id"])
    for d in dynasties:
        if d["id"] in by_dyn:
            d["regimeIds"] = sorted(by_dyn[d["id"]])

    write_json(OUT_DYNASTIES, dynasties)
    write_json(OUT_REGIMES, regimes)
    print(f"Wrote {OUT_DYNASTIES.relative_to(ROOT)}: {len(dynasties)} dynasties")
    print(f"Wrote {OUT_REGIMES.relative_to(ROOT)}: {len(regimes)} regimes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
