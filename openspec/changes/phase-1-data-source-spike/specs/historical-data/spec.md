## ADDED Requirements

### Requirement: 数据契约版本标识

所有 `data_source/*.json` 和 `assets/data/*.json` 的顶层 MUST 包含
`_schemaVersion` 字段,Phase 1 使用 `"v0.6"`。运行期 app 启动时 SHALL 检查
版本兼容性,不匹配则提示用户升级。

#### Scenario: 数据文件含有 schema 版本

- **WHEN** 任何 `data_source/dynasties.json`、`data_source/regimes.json`、
  `data_source/events/*.json` 或 `data_source/persons/*.json` 文件被写入
- **THEN** 顶层 JSON 对象包含 `"_schemaVersion": "v0.6"` 字段

#### Scenario: build 产物保留 schema 版本

- **WHEN** `tools/build.py` 从 `data_source/` 产出 `assets/data/*.json`
- **THEN** 顶层 JSON 对象包含 `"_schemaVersion": "v0.6"` 字段

### Requirement: 朝代实体字段

每个 dynasty 记录 MUST 包含: `id`、`name`、`startYear`、`endYear`、`color`、
`historicity`、`_yearAuthority`。Phase 1 默认 `_yearAuthority: "夏商周断代工程"`。
`id` 形如 `dynasty_<拼音下划线>`,全局唯一,一旦使用不可修改。

#### Scenario: 必填字段齐全

- **WHEN** `data_source/dynasties.json` 中加入一条朝代记录
- **THEN** 该记录至少含 `id`、`name`、`startYear`、`endYear`、`color`、
  `historicity`、`_yearAuthority` 七个字段

#### Scenario: 朝代年份采纳断代工程权威

- **WHEN** 录入西周朝代起始年份
- **THEN** `startYear` 值为 `-1046`(夏商周断代工程结论)
- **AND** `_yearAuthority` 字段值为 `"夏商周断代工程"`

### Requirement: 政权(Regime)实体字段含树拓扑

每个 regime 记录 MUST 包含: `id`、`name`、`dynastyId`、`startYear`、
`endYear`、`color`、`historicity`。**v0.6 新增树拓扑字段**:
- `parentRegimeId` (可空,表示从哪个 regime 分裂)
- `mergedIntoRegimeId` (可空,表示被哪个 regime 取代/并入)
- `siblingRegimeIds` (数组,同期并立的兄弟)

#### Scenario: 三国 regime 含树拓扑

- **WHEN** 录入"曹魏"政权
- **THEN** `parentRegimeId` 为 `"regime_eastern_han"`
- **AND** `mergedIntoRegimeId` 为 `"regime_western_jin"`
- **AND** `siblingRegimeIds` 包含 `"regime_shu"` 和 `"regime_wu"`

#### Scenario: 树拓扑双向引用一致性

- **WHEN** regime A 的 `siblingRegimeIds` 含 B
- **THEN** regime B 的 `siblingRegimeIds` 必须含 A
- **AND** `tools/validate.py` 检查双向一致性,不一致则报错

### Requirement: 事件实体字段(v0.6)

每个 event 记录 MUST 包含: `id`、`name`、`year`、`dynastyId`、`category`、
`summary`、`historicity`。Phase 1 深耕时段(legendary / 夏 / 商 / 西周)
**额外**必须含 `body`(markdown)和 `participants`(数组,可为空)。

可选字段: `month` / `day` / `era` / `regimeIds` / `tags` / `locationName`/
`outcome` / `relatedEvents` / `yearUncertainty` / `source`。

`category` 取自枚举: `war` | `politics` | `culture` | `science` |
`diplomacy` | `economy` | `person`。

`year` 公元前用负整数(如 `-1046`)。

#### Scenario: β 深耕事件含完整 body

- **WHEN** 录入"武王伐纣"(属深耕时段)
- **THEN** event 含 `body` 字段,内容为 markdown
- **AND** `body` 含至少一个 `## 起因` / `## 经过` / `## 后果` 段

#### Scenario: 骨架事件可省 body

- **WHEN** 录入"文景之治"(西汉,Phase 1 非深耕时段)
- **THEN** event **可** 省略 `body` 字段(占位状态)
- **AND** 仅含 `id` / `name` / `year` / `dynastyId` / `category` /
  `summary` / `historicity` 等最小字段

### Requirement: 字数硬约束

`tools/validate.py` MUST 强制以下字数限制:

| 字段 | 下限 | 常态目标 | 上限 | 行为 |
|---|---|---|---|---|
| `summary` | 150 字 | 200-300 字 | 500 字 | 超出 → 错误,阻塞 build |
| `body` | 800 字 | **1000-2000 字** | **5000 字** | 超过上限 → 错误,阻塞;不足下限 → warning |

字数计算: 字符数(中文一字一计,英文/数字一字符一计,**含 markdown 标记**,
不计空白)。

### Requirement: 内容双层风格(summary A / body C)

`summary` 字段 MUST 用 **A 风格**(教科书味,精准,可背诵)。
`body` 字段 MUST 用 **C 风格**(历史叙事,起因/经过/后果,后果段含现代史学视角)。
详见 `docs/content-style-guide.md`。

#### Scenario: summary 风格符合 A 标准

- **WHEN** 撰写 event.summary
- **THEN** 内容是中性陈述,1-2 段,无 markdown 标题
- **AND** 不带情感色彩 / 主观最高级评价 / 口语化措辞

#### Scenario: body 必含起因经过后果三段

- **WHEN** 撰写 β 时段 event.body
- **THEN** 含 `## 起因` / `## 经过` / `## 后果` 三段
- **AND** 后果段含"现代史学家认为..."或类似的当代视角句

### Requirement: 内容比例(LLM prompt 与人工 review 标准)

每朝代 100 件事件按以下比例分布(±5% 容差):
- 政治 25% / 军事 15% / 文化 25% / 科技 15% / 外交 5% / 经济 5% / 人物大事 10%

LLM 起草 prompt MUST 含明确比例约束。人工 review 事件清单时按比例砍/补。

#### Scenario: 事件清单比例失衡

- **WHEN** 某朝代 100 件事件中政治军事合计 > 50%(超过 40+5 的容差)
- **THEN** 视为不合格,需重新分布

#### Scenario: body 超过 5K 字阻塞 build

- **WHEN** 一条事件的 `body` 字段 6000 字
- **THEN** `tools/validate.py` 报错并指出该事件 id
- **AND** 退出码非零,`tools/build.py` abort

#### Scenario: summary 不足 150 字阻塞 build

- **WHEN** 一条事件的 `summary` 字段仅 80 字
- **THEN** `tools/validate.py` 报错
- **AND** 退出码非零

### Requirement: body 结构推荐

事件 `body` 字段 SHOULD 含 `## 起因` / `## 经过` / `## 后果` 三段。
可扩 `## 影响` / `## 评价` / `## 争议`。validate 不强制结构,但 warning
未含三段的事件。

#### Scenario: body 缺起因经过后果三段

- **WHEN** 事件 body 仅含一段散文,无 `##` 标题
- **THEN** `validate.py` 输出 warning(不阻塞)指出该事件

### Requirement: participants 字段语义

事件 `participants` 字段 MUST 仅含**主角/参与者**,不含"被影响者"。每个元素
形如 `{"personId": "...", "role": "...", "side": "..."}`。所有 `personId`
必须能在 `data_source/persons/*.json` 中找到,否则 validate 报错。

#### Scenario: participants 引用未知 personId

- **WHEN** 事件 participants 含 `personId: "person_unknown"`,但 persons
  文件中无此 id
- **THEN** `validate.py` 报错并阻塞 build

### Requirement: 不确定年份与传说时代

对年份不确定的事件(尤其传说时代),记录 SHALL 含 `yearUncertainty` 字段,
取值 `year` | `decade` | `century` | `era`。`historicity` 字段取值
`historical` | `semi-historical` | `legendary`,默认 `historical`。

#### Scenario: 传说时代事件标注

- **WHEN** 录入"大禹治水"等传说时代事件
- **THEN** 该事件含 `historicity: "legendary"` 和 `yearUncertainty: "century"`(或 "era")

### Requirement: 文件组织 — 按朝代拆分

`data_source/events/` 和 `data_source/persons/` 下文件 MUST 按朝代/时段拆分。
每个文件顶层格式:
```json
{
  "_schemaVersion": "v0.6",
  "events": [...]   // 或 "persons": [...]
}
```

Phase 1 至少含: `legendary.json` / `xia.json` / `shang.json` /
`western_zhou.json`(深耕),以及其他 21 个时段的占位文件。

#### Scenario: 事件按时段拆分到独立文件

- **WHEN** Phase 1 数据落地完成
- **THEN** `data_source/events/` 下含 25 个 JSON 文件,事件按所在时段分布

### Requirement: ID 全局唯一

所有 `dynasty_*` / `regime_*` / `event_*` / `person_*` ID MUST 跨所有数据
文件全局唯一。跨实体引用(如 `event.dynastyId`、`participants.personId`、
`regime.parentRegimeId` 等)的目标 ID 必须存在。

#### Scenario: 重复 ID 校验失败

- **WHEN** 两个事件文件中出现相同的 event id
- **THEN** `tools/validate.py` 报错并指出两处冲突位置

#### Scenario: 引用不存在的 ID 校验失败

- **WHEN** 一个 event 的 `dynastyId` 指向 `dynasties.json` 中不存在的 ID
- **THEN** `tools/validate.py` 报错并指出该 event 的 id

### Requirement: Phase 1 数据完整度

Phase 1 数据 SHALL 同时满足:

1. **全朝代骨架**: 25 个朝代节点全部录入,树拓扑(并立期政权的 parent /
   merged / siblings)完整
2. **β 深耕**: **夏 + 商 + 西周 + 东周春秋 + 东周战国** 5 时段含完整 body 和关键人物
3. **β 时段事件量**: 合并后 ≥ 100 件且 ≤ 180 件
4. **β 时段人物量**: 合并后 ≥ 40 人且 ≤ 80 人
5. **其他时段占位**: 每时段 5-10 件事件标题 + 5-10 个人物名
6. **尧舜禹**: 仅作为 dynasty_legendary 骨架渲染,事件占位 5-10 件,无 body

#### Scenario: 全朝代骨架完整度

- **WHEN** Phase 1 数据完成
- **THEN** `data_source/dynasties.json` 至少含 25 个朝代记录,从
  `dynasty_legendary` 起,到改革开放前(1976/1978)止

#### Scenario: β 深耕完整度

- **WHEN** Phase 1 数据完成
- **THEN** `data_source/events/xia.json` + `shang.json` + `western_zhou.json`
  + `eastern_zhou_spring_autumn.json` + `eastern_zhou_warring_states.json`
  合并后含 100-180 件事件
- **AND** 每件含 `summary` (A 风格) + `body` (C 风格) 字段
- **AND** body 字数 800-5000

#### Scenario: 三国并立期树拓扑完整

- **WHEN** Phase 1 数据完成
- **THEN** `data_source/regimes.json` 含 `regime_wei` / `regime_shu` /
  `regime_wu` 三个 regime
- **AND** 三者的 `siblingRegimeIds` 互相引用
- **AND** 三者的 `parentRegimeId` 都指向 `regime_eastern_han`(或类似前序)

### Requirement: 图片字段(v0.6)

`dynasty` 实体 MUST 含: `heroImage` / `heroImageSource` / `heroImageLicense`。
`person` 实体可选含: `portrait` / `portraitSource` / `portraitLicense`。
`event` 实体 Phase 1 不要求图片字段。

`heroImageLicense` / `portraitLicense` 取自枚举:
`CC-BY-SA-4.0` | `CC-BY-SA-3.0` | `CC-BY-4.0` | `CC0` | `public-domain`。

#### Scenario: dynasty 必填 hero 图

- **WHEN** 创建 dynasty 记录
- **THEN** 含 `heroImage`(相对 `assets/images/` 路径)
- **AND** 含 `heroImageSource`(URL)
- **AND** 含 `heroImageLicense`(枚举值)

#### Scenario: 图片来源限 Wikimedia

- **WHEN** Phase 1 录入图片字段
- **THEN** `heroImageSource` / `portraitSource` 必须以
  `https://commons.wikimedia.org/` 或 `https://*.wikipedia.org/` 开头

#### Scenario: β 时段人物 portrait 完整度

- **WHEN** Phase 1 数据完成
- **THEN** β 时段 ≥ 80% 的关键人物含 `portrait` 字段(允许部分缺失)

### Requirement: 政治敏感边界

事件内容 MUST 按 `docs/content-style-guide.md` 三档处理:
- **安全话题**: 大胆挖现代史学视角
- **敏感话题**: 中立陈述,不带价值判断
- **红线话题**: 简短陈述,不做"为什么"解释

**1949-1976 内容 Phase 1 整体推迟**(占位事件可以有,无 body)。

#### Scenario: 红线话题不写 body

- **WHEN** 录入"文革"或类似红线话题事件
- **THEN** 仅写 summary(精简事实),不写 body
- **AND** 标 `source: "manual"` 不进 LLM 起草流程
