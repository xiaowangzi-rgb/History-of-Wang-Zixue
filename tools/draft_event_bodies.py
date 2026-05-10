"""LLM-draft markdown body for β-era events (xia/shang/western_zhou/eastern_zhou).

Reads existing summary + name from data_source/events/<beta>.json, prompts the
LLM to write a 800-2000 char markdown body in C-style (historical narrative,
modern historiography). Writes drafts to _local/llm-drafts/<event_id>.md and
also updates a per-event JSON status file. Manual review then promotes drafts
into the actual event records.

Design intent:
  - LLM produces a DRAFT only — never auto-merged into data_source/
  - Each event gets one .md file in _local/llm-drafts/ for human review
  - source field stays "manual" until reviewed; promotion is a separate step

Usage:
    set LLM_API_KEY=...   (PowerShell: $env:LLM_API_KEY=...)
    set LLM_BASE_URL=https://api.apilink.cc
    python tools/draft_event_bodies.py                    # all β events
    python tools/draft_event_bodies.py --only event_xia_dayu_treat_water
    python tools/draft_event_bodies.py --only-file xia.json
    python tools/draft_event_bodies.py --skip-existing    # skip already-drafted
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: pip install openai", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
EV_DIR = ROOT / "data_source" / "events"
DRAFTS_DIR = ROOT / "_local" / "llm-drafts"
PERSONS_DIR = ROOT / "data_source" / "persons"
DYNASTY_FILE = ROOT / "data_source" / "dynasties.json"

BETA_FILES = ["xia.json", "shang.json", "western_zhou.json", "eastern_zhou.json"]

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.apilink.cc")


SYSTEM_PROMPT = """你是中国史学者,擅长把历史事件写成既严谨又生动可读的中文叙事。

风格规则(C 风格 = 历史叙事 + 现代史学视角,严格遵守):

1. 长度: 800-1800 字符(中文计字符)。短了内容不够,长了读者疲劳。
2. 结构: 用 markdown 二级标题分段,推荐结构:
   ## 背景 / 时代脉络
   ## 经过 / 关键节点
   ## 后果与影响
   ## 史学评价(用现代视角看)
   你可灵活调整二级标题名称,但**至少 3 段**。
3. 文风: 沉稳、不煽情、不空洞。具体年份、人名、地名要准确。引用《史记》《左传》等史料但只精选一两处关键引文。
4. 视角: 中立,呈现而非评判。不忌讳争议(如夏朝信史性、长平坑卒数字),坦白当代史学认知。
5. 禁忌:
   - 不要写"我们应该向 X 学习"这类 didactic 总结
   - 不要把传说当确凿史实(夏商以前必须标注"传说"或"半信史")
   - 不要堆砌成语(成语适度,叙事为主)
   - 不要过分美化或批判某一方
6. 可读性: 假定读者是有基础常识但非专业的成年人。

请直接输出 markdown,不要前言"以下是..."、不要后记"以上为...希望..."。
"""


USER_TEMPLATE = """请为以下中国历史事件撰写详细 markdown body:

**事件**: {name}
**年份**: {year_str}
**朝代**: {dynasty_name}
**简介(已有,作为提示,不要重复其措辞)**: {summary}
**历史性等级**: {historicity_label}

要求:
- 800-1800 字符
- 至少 3 个二级标题段(## ...)
- C 风格:历史叙事 + 起因经过结果 + 现代视角
- 不要用"以下是""希望对您有帮助"等 LLM 客套话
- 直接输出 markdown,不要包代码块"""


def fmt_year(y: int) -> str:
    return f"前 {-y} 年" if y < 0 else f"{y} 年"


def historicity_label(s: str | None) -> str:
    return {
        "legendary": "传说(无考古实证)",
        "semi-historical": "半信史(传说与考古夹杂)",
    }.get(s or "", "信史(有可靠史料)")


def load_dynasty_names() -> dict[str, str]:
    with DYNASTY_FILE.open(encoding="utf-8") as f:
        return {d["id"]: d["name"] for d in json.load(f)}


def collect_events(only_files: list[str], only_id: str | None) -> list[dict]:
    out = []
    files = only_files if only_files else BETA_FILES
    for fn in files:
        path = EV_DIR / fn
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as f:
            for ev in json.load(f):
                if only_id and ev["id"] != only_id:
                    continue
                out.append(ev)
    return out


def draft_one(client: OpenAI, model: str, ev: dict, dyn_names: dict, retries: int = 2) -> str | None:
    user = USER_TEMPLATE.format(
        name=ev["name"],
        year_str=fmt_year(ev["year"]),
        dynasty_name=dyn_names.get(ev["dynastyId"], ev["dynastyId"]),
        summary=ev.get("summary", ""),
        historicity_label=historicity_label(ev.get("historicity")),
    )
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user},
                ],
                temperature=0.6,
                max_tokens=3200,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            last_err = e
            print(f"    retry {attempt+1} due to: {e}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    print(f"  FAIL after {retries+1} tries: {last_err}", file=sys.stderr)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="single event id")
    ap.add_argument("--only-file", action="append", default=[],
                    help="restrict to specific file (e.g. xia.json), repeatable")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip events that already have a draft file")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--limit", type=int, default=0,
                    help="cap number of events drafted in this run (0=all)")
    args = ap.parse_args()

    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        print("ERROR: set LLM_API_KEY env var", file=sys.stderr)
        return 2

    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=api_key, base_url=f"{BASE_URL}/v1")
    dyn_names = load_dynasty_names()

    events = collect_events(args.only_file, args.only)
    if not events:
        print("no events match filters")
        return 1

    print(f"model={args.model}  candidates={len(events)}")
    written = 0
    for i, ev in enumerate(events, 1):
        if args.limit and written >= args.limit:
            print(f"hit --limit {args.limit}, stopping")
            break
        out = DRAFTS_DIR / f"{ev['id']}.md"
        if args.skip_existing and out.exists() and out.stat().st_size > 200:
            print(f"  [{i}/{len(events)}] SKIP {ev['id']} (already drafted)")
            continue
        print(f"  [{i}/{len(events)}] {ev['id']} ({ev['name']})")
        body = draft_one(client, args.model, ev, dyn_names)
        if not body:
            continue
        with out.open("w", encoding="utf-8") as f:
            f.write(f"<!-- event_id: {ev['id']} -->\n")
            f.write(f"<!-- name: {ev['name']} -->\n")
            f.write(f"<!-- year: {ev['year']}  dynasty: {ev['dynastyId']} -->\n\n")
            f.write(body)
            f.write("\n")
        chars = len(body)
        marker = "✓" if 800 <= chars <= 2000 else "!"
        print(f"      {marker} {chars} chars → {out.relative_to(ROOT)}")
        written += 1

    print(f"\nWrote {written} drafts to {DRAFTS_DIR.relative_to(ROOT)}")
    print("Review them, then promote into data_source/events/*.json with"
          ' `tools/promote_drafts.py` (next step).')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
