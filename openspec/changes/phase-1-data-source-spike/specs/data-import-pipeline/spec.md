## ADDED Requirements

### Requirement: 多源数据策略

Phase 1 数据来源 SHALL 是多源融合(单一仓库不覆盖尧舜禹 → 改革开放前)。
默认优先级:

1. **朝代骨架**: Hellohistory/HistoryChronology(BC841~1911)+ 夏商周断代工程
   补 -841 之前
2. **事件骨架**: 维基百科中文"中国历史大事年表"页 / Hellohistory
3. **β 深耕事件 body**: 人工撰写,LLM 协助起草(DeepSeek-V3),人工校对
4. **关键人物**: 维基数据 SPARQL + 人工挑选

候选仓库实地验证(`docs/data-source-survey.md` 中 ★★★ 必查项)的结果 MUST
记录在 `docs/decisions.md`(新 ADR-018)。

#### Scenario: 选定数据源记 ADR

- **WHEN** 完成候选仓库的实地验证
- **THEN** `docs/decisions.md` 新增 ADR-018,记录每个候选的: 评分、是否选用、
  pass 原因

### Requirement: 朝代年份冲突解决 — 断代工程优先

当多源数据对同一朝代起讫年份不一致时,merge 工具 MUST 优先采用夏商周断代工
程结论。冲突年份 SHALL 在 dynasty 记录上标 `yearUncertainty: "century"`,
`_yearAuthority: "夏商周断代工程"`。

#### Scenario: 武王伐纣年份冲突

- **WHEN** 多源对武王伐纣给出 -1046 / -1027 / -1075 等不同结论
- **THEN** merge 工具最终输出 `-1046` (断代工程结论)
- **AND** dynasty / event 标 `yearUncertainty: "century"` / 类似

### Requirement: import 脚本契约

每个数据源 MUST 有对应的 `tools/import_<source>.py`,从 `raw/<source>/` 读
取原始数据,转换为符合 historical-data spec 的 JSON,写到 `data_source/`。
脚本 MUST 可重入(运行多次结果一致)。

#### Scenario: import 脚本可重入

- **WHEN** `python tools/import_<source>.py` 连续运行两次
- **THEN** `data_source/` 中的 JSON 文件内容字节相同

#### Scenario: import 不污染 git

- **WHEN** import 脚本运行
- **THEN** 它不在 `raw/` 之外创建任何中间文件
- **AND** `raw/` 已在 `.gitignore` 中

### Requirement: merge 工具

`tools/merge_dynasties.py`(以及 `merge_events.py` 等)MUST 把多源 import
后的中间产物(在 `staged/` 目录)合并为最终 `data_source/` 数据。冲突解决:
- 朝代年份: 夏商周断代工程优先
- 朝代命名: 归一化到项目命名(`西汉` 而非 `前汉`)
- 同一事件: 优先 source 优先级 > 后者覆盖前者(在 ADR-018 决定具体顺序)

#### Scenario: 多源命名归一

- **WHEN** 一个源用"前汉",另一个用"西汉",另一个用"漢"
- **THEN** merge 工具输出统一为 `dynasty_western_han` (id) + `西汉` (name)

### Requirement: β 深耕的 LLM 起草工作流

Phase 1 β 深耕(尧舜禹+夏+商+西周)允许 LLM 协助起草事件 `body`。流程:

1. 人工列出待写事件(`tools/seed_phase1.py` 输入 YAML)
2. LLM 生成 body 草稿(DeepSeek-V3,通过 `DEEPSEEK_API_KEY`)
3. 草稿落到 `staged/` 目录,标 `source: "llm-draft"`
4. **人工校对**(必须),改对后 `source` 改为 `manual` 或 `llm-reviewed`
5. 仅 `source` 为 `manual` / `llm-reviewed` 的记录可进 `data_source/`

#### Scenario: LLM 草稿不进 data_source

- **WHEN** 一条事件 `source: "llm-draft"`
- **THEN** `tools/validate.py` 在检查 `data_source/` 时报错
- **AND** 仅 `staged/` 目录下允许此状态

### Requirement: 校验工具(v0.6 升级)

`tools/validate.py` MUST 检查:

1. JSON 解析失败
2. `_schemaVersion` 字段缺失或不为 `"v0.6"`
3. 必填字段缺失(参见 historical-data spec)
4. ID 全局重复
5. 跨实体 ID 引用找不到目标
6. **字数硬约束**(summary / body)
7. **树拓扑双向一致性**(siblingRegimeIds / parentRegimeId)
8. `historicity: historical` 的事件缺所有时间字段
9. event.year 落在 dynasty 起止范围之外(soft warning)
10. β 深耕时段事件必须含 `body` 字段

校验失败 MUST 以非零退出码返回。

#### Scenario: 校验通过

- **WHEN** `data_source/` 数据无错误,运行 `python tools/validate.py`
- **THEN** 输出 "OK" 类信息,退出码 0

#### Scenario: 校验捕获树拓扑不一致

- **WHEN** regime A 含 B 在 siblings,但 B 不含 A
- **THEN** `validate.py` 输出错误位置,退出码非 0

#### Scenario: 校验捕获 body 超长

- **WHEN** 一条 β 深耕事件 body 字数 6000
- **THEN** `validate.py` 报错并阻塞 build

### Requirement: build 工具

`tools/build.py` MUST 从 `data_source/` 读取数据,产出
`assets/data/{events,dynasties,regimes,persons}.json`。Build 前 MUST 调用
`validate.py`;校验失败则 build abort。Build 产物保留 `_schemaVersion`
字段,events 顶层数组按 year 升序。

#### Scenario: build 成功

- **WHEN** `data_source/` 校验通过,运行 `python tools/build.py`
- **THEN** `assets/data/events.json` 含所有事件按 year 升序
- **AND** `assets/data/dynasties.json` / `regimes.json` / `persons.json` 同步更新

#### Scenario: build 拒绝校验失败的数据

- **WHEN** `data_source/` 数据有错误,运行 `python tools/build.py`
- **THEN** build 中止,退出码非 0,不更新 `assets/data/`

### Requirement: raw 数据目录 gitignore

任何从外部仓库 clone 的原始数据 MUST 落在 `raw/` 目录下,该目录已在根
`.gitignore` 中。`data_source/` 中只存校对后的精简数据。

#### Scenario: raw 不进 git

- **WHEN** 在 `raw/` 下 clone 任意仓库
- **THEN** `git status` 不显示 `raw/` 下的内容

### Requirement: 图片爬取与处理工具

`tools/crawl_images.py` MUST 基于 [Scrapling](https://github.com/D4Vinci/Scrapling)
库,从 Wikimedia Commons + 中文维基百科 拉取候选图片到 `raw/images/<entity_type>/<id>/`。
其他来源(故宫 / 百度 / AI)Phase 1 不爬取。

`tools/process_images.py` MUST 用 Pillow 把人工筛选后的图压缩到:
- 主图: 800x600 WebP, ~150 KB
- 缩略图: 320x240 WebP, ~30 KB
输出到 `data_source/images/<entity_type>/<id>.{webp,thumb.webp}`。

`tools/build_image_manifest.py` MUST 生成 `assets/images/_manifest.json`,
含每张图的 SHA-256 hash + size,用于运行期热更检测。

#### Scenario: 仅从 Wikimedia 爬

- **WHEN** `tools/crawl_images.py` 运行
- **THEN** 仅访问 `commons.wikimedia.org` 和 `*.wikipedia.org` 域名
- **AND** 不访问百度 / 故宫 / 国博等其他源(Phase 2 评估)

#### Scenario: 自动评分排序

- **WHEN** 多张候选图被爬到
- **THEN** 按规则打分(分辨率 / 来源 / 标签 / 文件名匹配),top1 为默认采用

### Requirement: 图片热更模块

`assets/images/_manifest.json` MUST 是独立 manifest(不与数据 manifest 混在一起),
让运行期可以**懒加载**(按朝代展开时才下载该朝代图)。

#### Scenario: 图片 manifest 独立

- **WHEN** `tools/build.py` 完成
- **THEN** `assets/images/_manifest.json` 存在,与
  `assets/data/manifest.json` 分开
- **AND** 图片 manifest 含 `entity_id` → `{hash, size, type}` 映射

### Requirement: Phase 1 流水线最小性

Phase 1 流水线 SHALL 仅含: import → merge → validate → build →
crawl_images → process_images → build_image_manifest。**不含**:
- CBDB 抽取(Phase 3)
- LLM 富化产生骨架数据(本期 LLM 仅作 β 深耕的起草助手)
- chinese-poetry 文学家抽取(Phase 3)
- 事件场景图爬取(Phase 2 评估)
- AI 图生成(Phase 1 不用)

#### Scenario: Phase 1 不依赖 CBDB

- **WHEN** Phase 1 数据生产流程运行
- **THEN** 流程不读取 CBDB SQLite 文件

#### Scenario: Phase 1 LLM 仅用于 β 深耕

- **WHEN** 25 朝代骨架数据生产
- **THEN** 流程不调用任何 LLM API

#### Scenario: β 深耕允许 LLM 起草

- **WHEN** 撰写 β 时段事件 body
- **THEN** 允许调用 DeepSeek-V3 起草,但产物 `source: "llm-draft"`,
  人工校对后才能进 `data_source/`
