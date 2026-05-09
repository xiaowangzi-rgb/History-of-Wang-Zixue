# 数据 Schema v0.6(草案)

> ⚠️ **2026-05 升级**: 本草案从 v0.5 升至 **v0.6**,主要变化:
> - event 加 `body` 字段(markdown,1-2K 常态,**5K 字硬上限**)
> - event 字段确认: `summary` (150-500 字一行版) + `body` (详细) + `participants`
> - regime 加树拓扑字段: `parentRegimeId` / `mergedIntoRegimeId` / `siblingRegimeIds`
>   (用于树形时间线渲染)
> - dynasty 加 `_yearAuthority` 标注采用的纪年权威(默认: 夏商周断代工程)
> - person 字段维持简化版(persona 字段推迟到 Phase 3 复活)
>
> 顶层 JSON 含 `"_schemaVersion": "v0.6"` 字段。最终 schema 在 Phase 1 完成
> β 深耕后,通过 OpenSpec 流程冻结为 v1.0。

---

## 设计约定

### 时间表示

- **年份用整数**,公元前用负数(`-1046` = 公元前 1046 年)
- 月日是可选字段(`month?`, `day?`),古代大多数事件只到年
- **年号、纪年**(如"贞观元年")作为**显示层字段**(`era`),不参与计算
- 不确定年份用 `historicity` + `yearUncertainty` 表达,见下

### ID 命名

- 全部下划线小写英文,前缀表类型:
  - `person_kongzi` / `person_li_si`
  - `event_chibi_zhanyi` / `event_qin_unify_china`
  - `dynasty_zhou` / `dynasty_western_han`
  - `regime_wei` / `regime_shu` / `regime_wu`
- ID 一旦使用**不可修改**,改名只改 `name`

### 溯源

每条记录加 `source` 字段,枚举值:
`cbdb` | `wikidata` | `chinese-poetry` | `manual` | `llm-draft` |
`llm-reviewed`

`llm-draft` 状态的记录**不进 `data_source/`**,只在 `staged/` 阶段存在。
经人工校对后改为 `llm-reviewed` 才允许进入正式数据。

---

## Entity: Person

历史人物。

```json
{
  "id": "person_kongzi",
  "name": "孔子",
  "altNames": ["孔丘", "仲尼", "孔夫子"],

  "dynasty": "spring_autumn",
  "regimeIds": ["regime_lu"],

  "birthYear": -551,
  "deathYear": -479,
  "birthMonth": null,
  "deathMonth": null,

  "historicity": "historical",
  "yearUncertainty": "year",

  "role": "教育家、思想家",
  "tags": ["儒家", "诸子百家", "教育"],
  "summary": "春秋末期鲁国人,儒家学派创始人...(150-300 字现代汉语)",

  "personality": "温而厉,威而不猛,恭而安。重礼乐,厌武力,...(用于 LLM 扮演的性格描写,150 字内)",
  "selfReference": "丘",
  "speechStyle": "用 2-3 个示例对话片段说明语言风格",

  "works": ["《论语》(由弟子辑录)", "整理《诗》《书》《礼》《乐》《易》《春秋》"],

  "events": ["event_kongzi_birth", "event_kongzi_zhouyou", "event_kongzi_death"],

  "relations": [
    {"type": "student", "personId": "person_yanhui", "note": "最得意弟子"},
    {"type": "student", "personId": "person_zilu"},
    {"type": "contemporary_rival", "personId": "person_laozi", "note": "曾问礼于老子"}
  ],

  "source": "manual",
  "sources": ["《论语》", "《史记·孔子世家》"],
  "wikidataId": "Q4604",

  "portrait": "images/persons/person_kongzi.webp",
  "portraitSource": "https://commons.wikimedia.org/wiki/File:Confucius_Tang_Dynasty.jpg",
  "portraitLicense": "public-domain",

  "systemPromptSerious": "(Phase 3 复活,Phase 1 不填)",
  "systemPromptRomance": "(Phase 3 复活,Phase 1 不填)",
  "promptTemplateVersion": "v1"
}
```

**v0.6 注**: `portrait` / `portraitSource` / `portraitLicense` 三字段为 v0.6 新增。
`systemPrompt*` 字段定义保留但 Phase 1 不填(Phase 3 恢复时填,详见 ADR-011)。

### 字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | 唯一标识,见命名规范 |
| `name` | ✅ | 主名(显示用) |
| `altNames` | | 别名/字/号,用于搜索匹配 |
| `dynasty` | ✅ | 主朝代 ID,跨朝者填生平主要朝代 |
| `regimeIds` | | 所属政权(并立期需填,如三国人物的 wei/shu/wu) |
| `birthYear` / `deathYear` | | 公元前用负数 |
| `historicity` | ✅ | `historical` \| `semi-historical` \| `legendary` |
| `yearUncertainty` | | `year` \| `decade` \| `century` \| `era`,用于 UI 渲染 |
| `role` | | 简短身份("丞相"、"将军"、"诗人") |
| `tags` | | 用于筛选和聚合 |
| `summary` | ✅ | 现代汉语简介 |
| `personality` | ⚠️ | LLM 扮演用,核心人物必填 |
| `selfReference` | ⚠️ | 自称("我"/"在下"/"丘"/"朕"),核心人物必填 |
| `speechStyle` | ⚠️ | 语言风格示例对话(few-shot),核心人物必填 |
| `works` | | 代表著作 / 言论 |
| `events` | | 关联事件 ID 列表 |
| `relations` | | 见下 |
| `source` | ✅ | 数据来源 |
| `wikidataId` | | 维基数据 Q-ID,用于反查 |
| `systemPromptSerious/Romance` | ⚠️ | **build 时自动生成**,不要手填 |

### `historicity` 字段意义

| 值 | 含义 | 示例 | UI 处理 |
|---|---|---|---|
| `historical` | 正史人物,有可靠生卒 | 孔子、李白 | 正常渲染 |
| `semi-historical` | 历史可能存在但细节不可考 | 老子(部分学者) | 正常渲染 + 微小标注 |
| `legendary` | 传说人物,无可考史实 | 黄帝、尧、舜、禹 | **雾化 / 淡色 / "传说时代"标签** |

`legendary` 人物可以填 `approximateYear`(模糊年份),`yearUncertainty:
"century"` 或 `"era"`。

---

## Entity: Dynasty(v0.6 加纪年权威标注)

朝代,主朝代体系。

```json
{
  "id": "dynasty_western_han",
  "name": "西汉",
  "altNames": ["前汉"],
  "startYear": -202,
  "endYear": 8,
  "capital": ["长安"],
  "founderId": "person_liu_bang",
  "lastRulerId": "person_liu_ying",
  "parentId": null,
  "color": "#C04848",
  "summary": "...",
  "tags": ["大一统"],
  "historicity": "historical",
  "_yearAuthority": "夏商周断代工程",
  "source": "manual"
}
```

### v0.6 新增图片字段

```json
{
  ...,
  "heroImage": "images/dynasties/dynasty_western_zhou.webp",
  "heroImageSource": "https://commons.wikimedia.org/wiki/File:He_Zun.jpg",
  "heroImageLicense": "CC-BY-SA-4.0"
}
```

- `heroImage`: 相对 `assets/images/` 的路径,build 时从 `data_source/images/` 拷贝
- `heroImageSource`: 溯源 URL(合规需要,显示"图源:维基共享")
- `heroImageLicense`: 许可证(`CC-BY-SA-4.0` / `CC-BY-4.0` / `CC0` / `public-domain`)
- Phase 1 仅 dynasty 必须有,event / person 选填(详见 content-style-guide)

### `_yearAuthority` 字段

记录该朝代起讫年份所采纳的权威。Phase 1 默认 `"夏商周断代工程"`,争议年份
用 `yearUncertainty: "century"` 标注。其他权威值候选:
- `"史记"` (传统纪年)
- `"夏商周断代工程"` (主流采纳,默认)
- `"考古修订"` (针对夏 - 商早期等仍在演进的)
- `"通行历史教科书"` (无争议时段)

`parentId` 用于"继承关系"表达(如东汉.parent = 西汉),不强制单继承,可以为
null。

---

## Entity: Regime(政权,v0.6 加树拓扑字段)

朝代下面一级,处理三国 / 南北朝 / 五代十国 / 辽宋夏金等并立期。**v0.6 关键:
加入树形时间线渲染所需的拓扑字段**。

```json
{
  "id": "regime_wei",
  "name": "曹魏",
  "dynastyId": "dynasty_three_kingdoms",
  "startYear": 220,
  "endYear": 265,
  "capital": ["洛阳"],
  "founderId": "person_cao_pi",
  "color": "#4B5D8C",

  "parentRegimeId": "regime_eastern_han",       // ★ 从哪个政权 fork(可空)
  "mergedIntoRegimeId": "regime_western_jin",   // ★ merge 到哪个(可空)
  "siblingRegimeIds": ["regime_shu", "regime_wu"],  // ★ 同时期并立兄弟

  "summary": "...",
  "historicity": "historical",
  "source": "manual"
}
```

### 拓扑字段语义

| 字段 | 含义 | 示例 |
|---|---|---|
| `parentRegimeId` | 该 regime 从谁分裂出来 | 曹魏 ← 东汉 |
| `mergedIntoRegimeId` | 该 regime 被谁取代 / 并入(可空,如朝代延续到改革开放前) | 曹魏 → 西晋 |
| `siblingRegimeIds` | 同期并立的兄弟 regime | 曹魏 ↔ 蜀 / 吴 |

**用于**: 树图 UI 计算节点位置(分叉/合并)。validate.py 检查双向引用一致性。

非并立期的朝代不需要 regime,直接用 dynasty 即可(西汉就是一个 dynasty,无
regime)。

---

## Entity: Event(v0.6)

```json
{
  "id": "event_chibi_zhanyi",
  "name": "赤壁之战",
  "year": 208,
  "month": null,
  "day": null,
  "era": "建安十三年",
  "yearUncertainty": "year",
  "historicity": "historical",
  "dynastyId": "dynasty_eastern_han",
  "regimeIds": ["regime_eastern_han"],
  "category": "war",
  "tags": ["三国", "决定性战役"],

  "summary": "(150-500 字一行卡片用)",

  "body": "## 起因\n建安十三年...\n\n## 经过\n...\n\n## 后果\n...",

  "participants": [
    {"personId": "person_cao_cao", "role": "主将", "side": "曹军"},
    {"personId": "person_zhou_yu", "role": "主将", "side": "孙刘联军"},
    {"personId": "person_zhuge_liang", "role": "谋士", "side": "孙刘联军"}
  ],
  "locationName": "赤壁(今湖北)",
  "outcome": "孙刘联军胜,奠定三国鼎立格局",
  "relatedEvents": ["event_san_guo_lifa"],
  "source": "manual"
}
```

### 字数硬约束(`tools/validate.py` 强制)

| 字段 | 下限 | 常态目标 | 上限 | 行为 |
|---|---|---|---|---|
| `summary` | 150 字 | 200-300 字 | 500 字 | 超出 → 报错 |
| `body` | 800 字 | **1000-2000 字** | **5000 字** | 超过上限 → 报错并阻塞 build;不足 → warning |

字数计算: markdown 全文(含 `## 起因` 等标题 + 内容)的中文/英文字符数(不计空白)。

### 内容风格(参见 `docs/content-style-guide.md`)

- **`summary` 风格 = A (教科书风)**: 精准、可背诵、5 句话框架完整
- **`body` 风格 = C (历史叙事风)**: 故事性 + 起因/经过/后果 + 现代史学视角
- 此组合让"快速浏览(树图卡片读 summary)"和"深度阅读(详情页读 body)"
  共用一份数据,职责清晰

### `body` 推荐结构

至少含 `## 起因` / `## 经过` / `## 后果` 三段,可扩展:
- `## 影响`(对后世/制度的深远效应)
- `## 评价`(史家或后人评价)
- `## 争议`(史实有分歧时)

### `participants` 字段语义

**仅含主角/参与者**,不含"被影响者"。一个人物在一次事件中"被影响"但未参与
(如赤壁之战影响了汉献帝),不进入 participants。

### `category` 枚举(5-7 类够用)

`war`(战争) | `politics`(政治) | `culture`(文化) | `science`(科技) |
`diplomacy`(外交) | `economy`(经济) | `person`(人物大事)

---

## Entity: PersonRelation

人物关系,独立 entity 而不是嵌进 person,因为关系是双向的(避免维护两遍)。

```json
{
  "id": "rel_kongzi_yanhui",
  "fromPersonId": "person_kongzi",
  "toPersonId": "person_yanhui",
  "type": "teacher_student",
  "directional": true,
  "note": "颜回是孔子最得意弟子",
  "source": "manual"
}
```

### `type` 枚举

`teacher_student` | `father_son` | `mother_son` | `husband_wife` |
`siblings` | `colleague` | `ruler_minister` | `friend` | `rival` |
`enemy` | `mentor` | `same_school`

`directional: true` 表示需要区分方向(老师→学生);
`directional: false` 用于平等关系(朋友、同僚、兄弟)。

---

## 文件组织

```
data_source/
├── LICENSE
├── dynasties.json              # 全部朝代,一文件
├── regimes.json                # 全部政权,一文件
├── persons/                    # 按朝代拆分,git diff 可读
│   ├── pre_qin.json            # 先秦(传说时代)
│   ├── spring_autumn.json      # 春秋
│   ├── warring_states.json     # 战国
│   ├── qin.json
│   ├── western_han.json
│   ├── eastern_han.json
│   ├── three_kingdoms.json
│   ├── ...
│   └── modern.json
├── events/
│   ├── pre_qin.json
│   ├── spring_autumn.json
│   ├── ...
└── relations/
    └── all.json                # 单文件即可,通常不会太大
```

---

## 校验规则(`tools/validate.py` 应实现)

1. ✅ 所有 ID 全局唯一
2. ✅ 所有 `*Id` 引用都能在对应集合里找到
3. ✅ `birthYear < deathYear`(若都填)
4. ✅ event.year 在 dynasty.startYear / endYear 之间
5. ✅ person.dynasty 在 dynasties.json 中存在
6. ✅ relation 的 from/to 都存在
7. ✅ 关系不冲突(同两人不能同时是 父子 + 兄弟)
8. ✅ `historicity: legendary` 的人物可以缺 birthYear/deathYear
9. ✅ `historicity: historical` 的人物**必须**有至少一个时间字段
10. ✅ `systemPromptSerious` 末尾包含 `cutoff year` 约束语,且年份与 deathYear
    一致

---

## 演化策略

- 字段加 — 兼容(老数据缺字段视为 null)
- 字段改 — 必须 bump `schemaVersion`(在每个 JSON 顶层加 `"_schemaVersion":
  "v1"`)
- 字段删 — 严格禁止,改用 deprecated 注释

`schemaVersion` 同时进 `assets/data/persons.json` 顶层,运行期 app 启动时检
查,版本不匹配则提示"升级 app"。
