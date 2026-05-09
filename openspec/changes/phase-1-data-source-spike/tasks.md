## 1. 准备

- [ ] 1.1 确认 `.gitignore` 含 `raw/` 和 `staged/`
- [ ] 1.2 安装 Python 依赖: `pip install jsonschema`
- [ ] 1.3 准备 `DEEPSEEK_API_KEY` 环境变量(β 深耕用)
- [ ] 1.4 简化 `docs/data-schema.md` 已完成 ✓ (Step 1)

## 2. 数据源候选实地验证

- [ ] 2.1 `git clone https://github.com/Hellohistory/HistoryChronology raw/historychronology`
      → 看 README + LICENSE + 数据格式
- [ ] 2.2 `git clone https://github.com/wushixong/ChineseHistoryTimeline raw/chinesehistorytimeline`
- [ ] 2.3 `git clone https://github.com/ScottYuan09/History-Chronology raw/history-chronology-scott`
- [ ] 2.4 浏览维基百科"中国历史大事年表"页面,确认是否有结构化导出
- [ ] 2.5 维基数据 SPARQL endpoint 测试 — 查"中国历代帝王"
- [ ] 2.6 在 `docs/data-source-survey.md` 底部新增"实地验证结论"段
- [ ] 2.7 选定每类数据的源,写 ADR-018 入 `docs/decisions.md`

## 3. JSON Schema 工件

- [ ] 3.1 写 `tools/schema/dynasty.schema.json`(含 `_yearAuthority` 字段)
- [ ] 3.2 写 `tools/schema/regime.schema.json`(含 `parentRegimeId` /
      `mergedIntoRegimeId` / `siblingRegimeIds`)
- [ ] 3.3 写 `tools/schema/event.schema.json`(含 `body` 字段、字数限制)
- [ ] 3.4 写 `tools/schema/person.schema.json`(简化版,无 persona 字段)
- [ ] 3.5 写 `tools/schema/__init__.py` 聚合入口

## 4. 全 25 朝代骨架数据

### 4.1 朝代列表

- [ ] 4.1.1 整理完整朝代列表(尧舜禹起,改革开放前止),包括:
      - 传说时代(尧/舜/禹) → `dynasty_legendary` 或拆分
      - 夏 / 商 / 西周 / 东周(春秋/战国可作为 dynasty 也可作为 regime,定一下)
      - 秦 / 汉(西/新莽/东) / 三国 / 晋(西/东)/ 十六国 / 南北朝 / 隋 / 唐 /
        五代十国 / 宋(辽夏金)/ 元 / 明 / 清 / 民国 / 新中国(1949-1978)
- [ ] 4.1.2 每个朝代填: id / name / startYear / endYear / color /
      historicity / `_yearAuthority`(默认"夏商周断代工程")
- [ ] 4.1.3 输出到 `data_source/dynasties.json`

### 4.2 政权(regime)与树拓扑

- [ ] 4.2.1 列出所有 regime: 春秋诸侯(主要 5-10 国)/ 战国七雄 / 三国 /
      十六国 / 南北朝(南朝/北朝)/ 五代十国 / 辽夏金
- [ ] 4.2.2 每个 regime 填: id / name / dynastyId / startYear / endYear /
      color / `parentRegimeId` / `mergedIntoRegimeId` / `siblingRegimeIds`
- [ ] 4.2.3 双向一致性手工 review(`A.siblings ↔ B.siblings`)
- [ ] 4.2.4 输出到 `data_source/regimes.json`

### 4.3 各朝代占位事件 + 人物

- [ ] 4.3.1 25 个时段每个 5-10 个事件标题 + year + dynastyId(占位)
- [ ] 4.3.2 25 个时段每个 5-10 个关键人物 name + role + birth/death(占位)
- [ ] 4.3.3 占位文件 _schemaVersion 和顶层结构正确

## 5. β 深耕(尧舜禹 / 夏 / 商 / 西周)

> 这是 Phase 1 的"创造性工作量",约 1-2 个月业余时间。

### 5.1 尧舜禹时期(传说时代)

- [ ] 5.1.1 列出 5-10 件关键事件: 大禹治水 / 禅让 / 三皇五帝传说 / ...
- [ ] 5.1.2 列出 5-10 个关键人物: 尧 / 舜 / 禹 / 黄帝 / 炎帝 / ...
- [ ] 5.1.3 每件事 LLM 起草 body → `staged/llm-drafts/legendary/`
- [ ] 5.1.4 人工校对 → `data_source/events/legendary.json`,所有 historicity
      = "legendary"

### 5.2 夏

- [ ] 5.2.1 列出 5-10 件关键事件: 启杀伯益 / 太康失国 / 少康中兴 / 夏桀亡 / ...
- [ ] 5.2.2 列出 5-10 个关键人物: 启 / 少康 / 桀 / ...
- [ ] 5.2.3 LLM 起草 → 校对 → `data_source/events/xia.json`(部分 historicity
      = "semi-historical")

### 5.3 商

- [ ] 5.3.1 列出 10-20 件关键事件: 商汤灭夏 / 盘庚迁殷 / 武丁中兴 / 牧野之
      战(商方视角)/ ...
- [ ] 5.3.2 列出 10-15 个关键人物: 商汤 / 伊尹 / 盘庚 / 武丁 / 妇好 / 纣王 /
      ...
- [ ] 5.3.3 LLM 起草 → 校对 → `data_source/events/shang.json`

### 5.4 西周

- [ ] 5.4.1 列出 15-30 件关键事件: 武王伐纣 / 周公东征 / 成康之治 / 国人暴动 /
      宣王中兴 / 平王东迁 / ...
- [ ] 5.4.2 列出 10-15 个关键人物: 文王 / 武王 / 周公 / 姜尚 / 召公 / 厉王 /
      宣王 / 幽王 / ...
- [ ] 5.4.3 LLM 起草 → 校对 → `data_source/events/western_zhou.json`

### 5.5 β 深耕字数检查

- [ ] 5.5.1 跑 `tools/validate.py` 字数检查,确保所有 body 在 800-5000 字间
- [ ] 5.5.2 修订 < 800 字的(扩写)和 > 5000 字的(拆分事件)

## 6. 校验工具

- [ ] 6.1 写 `tools/validate.py`(载入 schema + 跑自定义规则)
- [ ] 6.2 实现规则: ID 唯一、跨实体引用存在
- [ ] 6.3 实现规则: `_schemaVersion` 检查
- [ ] 6.4 实现规则: 字数硬约束(summary / body)
- [ ] 6.5 实现规则: 树拓扑双向一致性 + 闭环检测
- [ ] 6.6 实现规则: β 深耕时段事件必须含 body
- [ ] 6.7 实现规则: `source: "llm-draft"` 不允许在 `data_source/`
- [ ] 6.8 实现规则: event.year 落在 dynasty 范围(soft warning)
- [ ] 6.9 跑 `python tools/validate.py`,直到 `data_source/` 全 pass
- [ ] 6.10 故意破坏数据测各条规则能 catch

## 7. import + merge 工具(若用)

- [ ] 7.1 写 `tools/import_hellohistory.py`(若 ADR-018 选用)
- [ ] 7.2 写 `tools/import_wikidata.py`(SPARQL 拉人物)
- [ ] 7.3 写 `tools/import_wiki_zh.py`(维基百科年表抓取,若用)
- [ ] 7.4 写 `tools/merge_dynasties.py`(多源朝代年份冲突解决)
- [ ] 7.5 写 `tools/merge_events.py`(事件去重 + 命名归一)

## 8. β 深耕辅助工具

- [ ] 8.1 写 `tools/seed_phase1.py`(读取 YAML 输入 → JSON 输出 + LLM 起草调用)
- [ ] 8.2 实现 LLM 起草调用(DeepSeek-V3,环境变量 key)
- [ ] 8.3 实现"草稿落 staged + source: llm-draft"
- [ ] 8.4 实现"校对后导出到 data_source + source 改为 llm-reviewed"

## 9. build 工具

- [ ] 9.1 写 `tools/build.py`(读 `data_source/` → 合并/复制 → `assets/data/`)
- [ ] 9.2 实现 build 前调 validate,失败则 abort
- [ ] 9.3 events 按 year 升序合并到 `assets/data/events.json`
- [ ] 9.4 顶层加 `_schemaVersion: "v0.6"` + `_buildTime`
- [ ] 9.5 跑 `python tools/build.py`,验证 `assets/data/*.json` 内容
- [ ] 9.6 验证文件总大小(预计 8-15 MB)

## 10. 文档收尾

- [ ] 10.1 在 `docs/data-source-survey.md` 底部"实地验证结论"段补全
- [ ] 10.2 在 `docs/decisions.md` 写 ADR-018(选定的数据源)
- [ ] 10.3 在 `tools/README.md` 简短记录脚本用法
- [ ] 10.4 更新 `docs/data-pipeline.md`(若需)反映多源策略

## 11. 提交 + 归档

- [ ] 11.1 跑 `tools/validate.py` 最终全 pass
- [ ] 11.2 跑 `tools/build.py` 产出 `assets/data/*.json`
- [ ] 11.3 git add → commit
- [ ] 11.4 跑 `openspec validate phase-1-data-source-spike` 通过
- [ ] 11.5 准备 archive: `/opsx:archive phase-1-data-source-spike` 关闭本次 change

## 12. 接力下一个 change

- [ ] 12.1 启动 `/opsx:propose phase-1-tree-renderer`(Flutter 树图实现)
- [ ] 12.2 在新 change proposal 中引用本 change 产出的 `assets/data/`
