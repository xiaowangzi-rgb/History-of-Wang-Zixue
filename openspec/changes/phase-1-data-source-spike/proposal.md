## Why

Phase 1 已重定位为"**全 25 朝代树图骨架 + β 深耕(夏+商+西周+东周春秋战国)
+ Wikimedia 图片**"(详见 ADR-022 / ADR-026)。这要求项目第一次有完整的中国
史结构化数据 — 所有朝代/政权/树拓扑齐备,加 100-180 件事件含完整 markdown body
+ 关键人物 + 图片(朝代 hero + β 人物画像)。

当前 `data_source/` 是空的。本变更负责把数据基础打好,让 Phase 1 的 Flutter
树图(独立的下一个 change)能直接吃。

数据策略已在 ADR-012 / ADR-014 调整为"**多源 git 仓库 merge + 人工校对**",
LLM 仅作起草助手。本变更也包含 spec 升级(historical-data 升至 v0.6 schema:
markdown body / 字数硬约束 / 树拓扑字段)和工具链(import / merge / validate /
build)。

## What Changes

### 数据
- **新增** `data_source/dynasties.json`(全 25 朝代骨架,夏商周断代工程为权威,
  含 heroImage / heroImageSource / heroImageLicense 字段)
- **新增** `data_source/regimes.json`(全部并立期政权,含 `parentRegimeId` /
  `mergedIntoRegimeId` / `siblingRegimeIds` 树拓扑字段)
- **新增** `data_source/events/*.json` 共 25 个文件(按朝代拆分):
  - β 4 时段(`xia.json` / `shang.json` / `western_zhou.json` /
    `eastern_zhou_spring_autumn.json` / `eastern_zhou_warring_states.json`)
    每条事件含完整 `summary` (A 风格 150-500 字) + `body` (C 风格 800-2000 字
    常态,5K 硬上限)
  - 其他 20 时段每个 5-10 条占位事件
- **新增** `data_source/persons/*.json` 共 25 个文件:
  - β 时段每个填 10-15 个关键人物完整 summary + portrait
  - 其他时段每个 5-10 个人物名占位
- **新增** `data_source/images/`(WebP 格式)
  - `dynasties/` 25 张朝代 hero 图
  - `persons/` β 时段 ~50 张关键人物画像
  - 来源仅 Wikimedia Commons + Wikipedia(详见 ADR-026)

### 工具链
- **新增** `tools/schema/*.json`(JSON Schema for dynasty / regime / event / person v0.6)
- **新增** `tools/import_*.py`(多源 import: Hellohistory / Wikidata / 维基百科年表)
- **新增** `tools/merge_dynasties.py`(多源 merge,断代工程优先)
- **新增** `tools/validate.py`(schema 校验 + 字数硬约束 + 树拓扑一致性 + 图片字段)
- **新增** `tools/build.py`(`data_source/` → `assets/data/`)
- **新增** `tools/seed_phase1.py`(β 深耕的人工编辑工作流 + LLM 双 pass 起草)
- **新增** `tools/crawl_images.py`(基于 Scrapling,Wikimedia 主力)
- **新增** `tools/process_images.py`(Pillow 压缩 + WebP 转换)
- **新增** `tools/build_image_manifest.py`(图片单独 manifest 用于热更)

### 文档
- **更新** `docs/data-schema.md`(v0.6 + 图片字段)
- **更新** `docs/data-source-survey.md`(底部加"实地验证结论"段 + 图片源已加)
- **更新** `docs/decisions.md`(ADR-013 ~ ADR-026 已写)
- **新增** `docs/content-style-guide.md`(写作风格 + 比例 + 标准 + 敏感 + 图片)
- **新增** ADR-027 入 `docs/decisions.md`(选定的数据源,实施 2.x 后写)

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
- 全 25 朝代骨架(树图能完整渲染)+ 25 朝代 hero 图
- **β 5 时段(夏 / 商 / 西周 / 春秋 / 战国)** 事件含 summary + body(100-180 件)
- 关键人物列表(β 时段每个 10-15 人含 portrait,其他时段占位)
- 工具链可重入,validate 全 pass,build 产物字节稳定
- 图片单独 manifest,支持后续热更

**非目标**(推迟到后续 change):
- Flutter 树图实现(下一个 change: `phase-1-tree-renderer`)
- 秦 / 汉 / 唐 / ... 等其他 20 时段深耕(Phase 2+)
- person 字段恢复 persona / systemPrompt(Phase 3)
- CBDB 抽取(Phase 3)
- 事件场景图(Phase 2 视体验决定)
- 1949-1976 内容(Phase 后期重新评估)
- 尧舜禹深耕(Phase 2,只在 Phase 1 做雾化骨架)
