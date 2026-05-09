## Why

Phase 1 已重定位为"**全 25 朝代树图骨架 + β 深耕(尧舜禹+夏+商+西周)**"
(详见 ADR-016)。这要求项目第一次有完整的中国史结构化数据 — 所有朝代/政权/
树拓扑齐备,加 40-70 件事件含完整 markdown body + 关键人物。

当前 `data_source/` 是空的。本变更负责把数据基础打好,让 Phase 1 的 Flutter
树图(独立的下一个 change)能直接吃。

数据策略已在 ADR-012 / ADR-014 调整为"**多源 git 仓库 merge + 人工校对**",
LLM 仅作起草助手。本变更也包含 spec 升级(historical-data 升至 v0.6 schema:
markdown body / 字数硬约束 / 树拓扑字段)和工具链(import / merge / validate /
build)。

## What Changes

### 数据
- **新增** `data_source/dynasties.json`(全 25 朝代骨架,夏商周断代工程为权威)
- **新增** `data_source/regimes.json`(全部并立期政权,含 `parentRegimeId` /
  `mergedIntoRegimeId` / `siblingRegimeIds` 树拓扑字段)
- **新增** `data_source/events/*.json` 共 25 个文件(按朝代拆分):
  - β 4 时段(`legendary.json` / `xia.json` / `shang.json` / `western_zhou.json`)
    每条事件含完整 `summary` (150-500 字) + `body` (1-2K 字 markdown)
  - 其他 21 时段每个 5-10 条占位事件(只 `id` / `name` / `year` / `dynastyId`)
- **新增** `data_source/persons/*.json` 共 25 个文件(按朝代拆分):
  - β 4 时段每个填 5-15 个关键人物完整 summary
  - 其他时段每个 5-10 个人物名占位

### 工具链
- **新增** `tools/schema/*.json`(JSON Schema for dynasty / regime / event / person v0.6)
- **新增** `tools/import_*.py`(多源 import: Hellohistory / Wikidata / 维基百科年表)
- **新增** `tools/merge_dynasties.py`(多源 merge,断代工程优先)
- **新增** `tools/validate.py`(schema 校验 + 字数硬约束 + 树拓扑一致性)
- **新增** `tools/build.py`(`data_source/` → `assets/data/`)
- **新增** `tools/seed_phase1.py`(β 深耕的人工编辑工作流)

### 文档
- **简化** `docs/data-schema.md`(已在 Step 1 完成 v0.6)
- **更新** `docs/data-source-survey.md`(底部加"实地验证结论"段)
- **新增** ADR-013 ~ ADR-018 入 `docs/decisions.md`(ADR-013~017 已写,
  ADR-018 选定数据源待实施时写)

## Capabilities

### New Capabilities

- `historical-data`: 中国史结构化数据契约 — schema v0.6,含 markdown body /
  字数硬约束 / 树拓扑字段 / participants。覆盖 dynasty / regime / event /
  person 四类实体。
- `data-import-pipeline`: 开发期数据流水线 — 多源 import → merge → validate
  → build,断代工程为年份权威。LLM 仅作 β 深耕时的起草助手,不参与骨架数据。

### Modified Capabilities

无(本项目第一份 spec)。

## Impact

- **数据**: `data_source/` 从空 → 全 25 朝代骨架 + 4 时段完整深耕
- **工具**: `tools/` 从空 → 5 个 Python 脚本 + JSON Schema 定义
- **代码运行期**: 不直接影响(Flutter 还没建)。但 `assets/data/` 产出的文件
  即是 Phase 1.4 Flutter 树图加载的数据契约
- **文档**:
  - `docs/data-source-survey.md` 加实地验证结论
  - `docs/decisions.md` 加 ADR-018(选定数据源)
- **依赖**:
  - Python 3.10+
  - `pip install jsonschema`
  - `git clone` 候选数据源仓库到 `raw/`(已 gitignore)
  - LLM 起草: `DEEPSEEK_API_KEY` 环境变量(仅 β 深耕用)
- **不影响**: Flutter 项目(下一个 change)、CBDB 接入(Phase 3)、persona 设计(Phase 3)

## 范围与非目标

**Phase 1 完成态**:
- 全 25 朝代骨架(树图能完整渲染)
- 尧舜禹 + 夏 + 商 + 西周 4 时段事件含 body(40-70 件)
- 关键人物列表(每深耕时段 5-15 人,其他时段占位)
- 工具链可重入,validate 全 pass,build 产物字节稳定

**非目标**(推迟到后续 change):
- Flutter 树图实现(下一个 change: `phase-1-tree-renderer`)
- 春秋战国 / 秦 / 汉 / 唐 / ... 深耕(Phase 2+)
- person 字段恢复 persona / systemPrompt(Phase 3)
- CBDB 抽取(Phase 3)
- LLM 富化产生 body(本期允许 LLM 起草 β 深耕的 body 草稿,但要人工校对)
