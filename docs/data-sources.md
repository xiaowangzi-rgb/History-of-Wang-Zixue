# 数据来源 (Data Sources)

> 调研结论:GitHub 上**没有一个**完美的开箱即用中国史数据集。需要做"多源 ETL
> + LLM 富化",以 CBDB 为人物底座,Wikidata 补先秦 / 秦汉,chinese-poetry 补
> 文学家,LLM 生成事件。

---

## ⭐⭐⭐ CBDB (China Biographical Database) — 人物主数据源

哈佛大学 + 北京大学 + 中央研究院联合维护的**学术金标准**。

| 项 | 详情 |
|---|---|
| 规模 | **649,533 人物**(2025 年 5 月数据) |
| 覆盖 | **7-19 世纪为主**(唐宋元明清强,先秦/秦汉/魏晋/隋弱) |
| 字段 | 生卒年、籍贯、亲属关系、社会关系、官职、著作、事件等 |
| 主表 | `BIOG_MAIN`(人物主表)+ 几十张关联表 |
| 格式 | SQLite / MySQL / MS Access / SQL Server |
| 更新 | 持续维护,**最新 2026-02-08** |
| 许可 | 学术开放,**自用绝对没问题**,商用需联系 |
| SQLite 下载 | https://github.com/cbdb-project/cbdb_sqlite (`latest.7z`) |
| 官网 | https://cbdb.hsites.harvard.edu/ |

### 关键价值

不只是名字 + 简介,**关系网完整**(谁是谁的师生 / 父子 / 同僚 / 政敌)。这是
本项目"对话 + 知识边界 + 关系图"的核心数据来源。

### 已知坑

- 字段为学术研究设计,**不是为 app 设计**。需写脚本提炼"app 友好"的精简字段
- 7 世纪(唐)之前覆盖弱,需别的源补充
- SQLite 数据库不小(预计几百 MB),不适合直接打包进 app,要 ETL 后只取你需
  要的人物
- CBDB 的人物简介字段较短,深度内容需要其他源补充或 LLM 富化

### 抽取策略

1. 下载 `latest.7z` 解压到 `raw/cbdb_latest.sqlite`
2. `tools/etl/extract_cbdb.py` 按朝代过滤人物 → 候选 JSON
3. 取核心字段:`c_personid`, `c_name`, `c_birthyear`, `c_deathyear`,
   `c_dy`(朝代),`c_index_addr`(籍贯),`c_notes`(简介)
4. 关联表查关系:`KIN_DATA`(亲属)、`ASSOC_DATA`(社会关系)
5. 输出到 `staged/persons_cbdb.json`,等待 merge

---

## ⭐⭐ chinese-poetry — 文学家 + 诗词补充

| 项 | 详情 |
|---|---|
| 规模 | ~14,000 唐宋诗人 + 5.5 万唐诗 + 26 万宋诗 + 21,050 首宋词 + 论语 / 诗经等经典 |
| 仓库 | https://github.com/chinese-poetry/chinese-poetry |
| 格式 | **JSON,直接可用** |
| 许可 | **MIT** ✅ |

### 实测 schema(`authors.tang.json` 第一条)

```json
{
  "name": "太宗皇帝",
  "id": "uuid",
  "desc": "帝姓李氏,諱世民,神堯次子,聰明英武。貞觀之治,庶幾成康..."
}
```

### 已知坑

- 字段简陋,**没有 dynasty/birthYear/deathYear 等结构化字段**(诗集按朝代分目
  录隐式表达)
- `desc` 是**文言文**(古籍引文),要 LLM 转译成现代汉语 summary
- 但**作品数据**极有价值——每个文学家的代表作直接就有

### 抽取策略

1. `git clone https://github.com/chinese-poetry/chinese-poetry raw/chinese-poetry`
2. `tools/etl/extract_poetry.py` 把作者条目 + 其作品列表合并
3. 朝代信息从目录路径推断(`全唐诗/authors.tang.json` → dynasty=tang)
4. `desc` 字段先存原文,后续在 enrich 阶段 LLM 转译

---

## ⭐⭐ Wikipedia / Wikidata — 不可或缺的补充

不在 GitHub 上,但**这才是先秦/秦汉/魏晋人物的最佳来源**(CBDB 不覆盖)。

| 子源 | 用途 |
|---|---|
| Wikidata SPARQL | 查"中国历代帝王"、"先秦诸子"、"汉朝丞相"等列表,获 Q-ID + 生卒年 + 朝代 |
| 中文维基百科 dump / API | 每篇人物条目第一段就是结构化简介,LLM 摘要后用 |

### 协议

CC-BY-SA(署名 + 同等共享),**自用没问题,公开发布需署名**。本项目仓库 Public,
所以衍生数据也必须 CC-BY-SA(已在 `data_source/LICENSE` 中声明)。

### 抽取策略

1. `tools/etl/fetch_wikidata.py` 用 SPARQL 查目标人物列表
   ```sparql
   SELECT ?person ?personLabel ?birth ?death ?dynastyLabel WHERE {
     ?person wdt:P31 wd:Q5 ;
             wdt:P27 wd:Q29520 ;  # 中国国籍
             wdt:P509 / wdt:P509 ?something .  # 限定时段
     # ...
   }
   ```
2. 拿到 Q-ID 后,用维基百科 API 拿对应条目第一段做 summary 起点
3. 缓存到 `raw/wikidata-cache/`,避免重复拉

---

## ⭐ grand-timeline — 备选时间线数据(暂不接入)

| 项 | 详情 |
|---|---|
| 规模 | 30,800 古人,公元前 1000 - 公元 2000 |
| 仓库 | https://github.com/LingDong-/grand-timeline |
| 字段 | 名字 / 简介 / 朝代 / 维基链接 |
| 许可 | **未明示**,需进仓库看 LICENSE |

**价值**: 覆盖时段比 CBDB 广得多(含先秦)。
**风险**: 许可不明,自用问题不大但要存疑。**暂不接入**,留作后续选项。

---

## ❌ 调研后排除的项目

| 项目 | 排除原因 |
|---|---|
| `chinatimeline/data` | 主要是当代政治事件(2000+),不适合古代史 |
| `anzhihe/encyclopedia` | 全是 .doc/.xls/.pdf,**非结构化**,工程不友好 |
| `JNingWei/Chinese_History` | 是电子书集合,文本而非结构化数据 |
| `HarborLibrary/Chinese-History` | 同上,资料汇编非数据集 |
| `MescoCoder/AncientChineseProject` | 资治通鉴 NER 标注语料,是 NLP 研究素材,要从中抽事件不如直接 LLM 生成 |
| `fucora/CBDB` | 只是 CBDB 可视化项目,**不分发数据**,数据要从官方拿 |

---

## 事件数据 — 没有合适的现成数据集

中文社区**没有结构化、覆盖广的"中国史事件数据库"**开源项目。CBDB 有事件表
但聚焦于人物相关事件(任职、流放、考中科举之类),不是"赤壁之战"这种宏观事件。

**结论**: 事件数据必须 **LLM 按朝代批次生成 + 人工校对**,这部分工作量绕不
过去。但好消息是:朝代清晰、事件总量可控(秦汉到民国,核心事件 300-500 个就
够支撑一个用得爽的产品)。

校对重点:**年份**(LLM 在年份上最容易幻觉,差几年是常见错误)。

---

## 总结:多源融合矩阵

|       | 先秦 | 秦汉 | 魏晋南北朝 | 隋 | 唐 | 宋 | 元 | 明 | 清 | 民国 |
|-------|------|------|-----------|-----|----|----|----|----|----|------|
| CBDB  | ❌   | ❌   | ⚠️         | ⚠️  | ✅ | ✅ | ✅ | ✅ | ✅ | ❌   |
| chinese-poetry | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ |
| Wikidata | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| LLM 生成 | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |

(✅ = 主力,⚠️ = 部分,❌ = 不覆盖)

LLM 生成在「先秦」和「民国」打 ⚠️ 的原因:先秦史实需要谨慎,民国近现代敏感
内容多。
