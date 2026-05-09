# 数据源调研 — 现成 GitHub 仓库

> 创建于 2026-05,Phase 1.1 spike 的产出。
> 本文档记录"WebSearch 浅层调研"结果,**未真去 clone 验证**。
> 实际选定哪个仓库需要 Phase 1.1 任务里实地验证(clone + 看格式 + 查许可)。

---

## 调研背景

2026-05 重定位后,数据策略改为"**优先用现成 git 仓库 + 适配 schema**"。
本文档列出候选仓库,标注**适配工作量**和**许可证风险**,作为 Phase 1.1 验
证清单。

---

## 候选仓库一览

> ⚠️ 许可证一栏标注 `?` 的需要实地验证。**没有声明许可的仓库 = 不能用**。

| # | 仓库 | 内容类型 | 时段覆盖 | 适配工作量 | 许可 |
|---|---|---|---|---|---|
| 1 | [Hellohistory/HistoryChronology](https://github.com/Hellohistory/HistoryChronology) | 朝代/帝王/年号/干支 | -841 → 1911 | 中(查工具) | ? |
| 2 | [chinatimeline/data](https://github.com/chinatimeline/data) | 政治/社会事件 | **现代为主**(20-21 世纪) | — | CC-BY?* |
| 3 | [wushixong/ChineseHistoryTimeline](https://github.com/wushixong/ChineseHistoryTimeline) | 中国历史时间轴 | 待查 | 待查 | ? |
| 4 | [ScottYuan09/History-Chronology](https://github.com/ScottYuan09/History-Chronology) | 中外历史年代对照表 | 待查 | 待查 | ? |
| 5 | [quzhi1/ChineseHistoricalSource](https://github.com/quzhi1/ChineseHistoricalSource) | 史料解析 → JSON | 待查 | 中-大 | ? |
| 6 | [MagisterKnecht/Chinese-Dynasties](https://github.com/MagisterKnecht/Chinese-Dynasties) | 朝代分析 jupyter + Excel | 全朝代 | 中(Excel 转 JSON) | ? |
| 7 | [lcclab-blcu/CHED](https://github.com/lcclab-blcu/CHED) | 二十四史事件检测数据集 | 全朝代 | **大**(NLP 数据集格式) | 学术? |
| 8 | [cadicex/history_map](https://github.com/cadicex/history_map) | 中国历史地图集 | 全朝代 | — (是 app 不是数据) | — |

\* chinatimeline 内容偏现代 + 政治敏感,**不适合本项目**。

---

## ⚠️ 排除项(重要)

### `HarborLibrary/Chinese-History` — 不能用

调研中出现频率高,但实际是**钱穆 / 当年明月 / 龙应台 / 史景迁等的整本图书**
(PDF/epub),全部受版权保护。即便 fork 几行也是侵权,**完全 pass**。

### `JNingWei/Chinese_History` — 同上

"完整全套电子书"项目,版权状况同 HarborLibrary。

---

## 关键候选深入分析(待 Phase 1.1 验证)

### 候选 1: Hellohistory/HistoryChronology

**特征**:
- 覆盖 **公元前 841 → 公元 1911**(共和元年到清末)
- 包含: 干支纪年 / 朝代更迭 / 帝王年号
- 是个**查询工具软件**,数据应该是结构化的

**适合本项目的用途**:
- ✅ `dynasties.json` 主力(朝代起止 + 帝王)
- ✅ 帝王年号转换(可能在做题里有用)
- ❌ **没有"事件"字段**(只是纪年表)

**风险**:
- 许可证未知,Phase 1.1 必须查
- 可能数据嵌在 SQLite / 二进制里,不是 JSON

**Phase 1.1 行动**: clone 仓库,检查 LICENSE,查数据格式。

---

### 候选 3: wushixong/ChineseHistoryTimeline

**特征**: 名字就叫"中国历史时间轴",最 on-topic。

**风险**:
- 仓库可能很小 / 不维护
- 许可证未知
- 数据粒度未知

**Phase 1.1 行动**: clone 看 README 和数据文件。

---

### 候选 4: ScottYuan09/History-Chronology

**特征**: 中外历史年代对照表 — 比单纯中国史多了"中外对照"维度,**对本项目
是 bonus**(我们暂不需要世界史,但未来可能扩展)。

**Phase 1.1 行动**: 优先级低于候选 1 和 3,先看那两个。

---

## 推荐路径(Phase 1.1 实施)

```
   优先级           动作
   ════════════════════════════════════════════════════

   ★★★ 必查        candidate 1 (Hellohistory) — clone + 查格式/许可
   ★★★ 必查        candidate 3 (wushixong)    — clone + 看 README
   ★★  bonus       candidate 4 (ScottYuan09)  — 简看
   ★★  备选        candidate 5 (quzhi1)       — 史料粒度可能太细
   ★   仅了解      candidate 7 (CHED)         — 学术 NLP 格式,转换成本高
```

---

## 决策树

```
   先查 candidate 1 + 3 + 4 的 LICENSE
            │
            ▼
   ┌────────────────────────────────┐
   │ 至少一个有兼容许可(CC-BY-SA   │
   │  / MIT / CC0 / 公有领域)?     │
   └────────────────────────────────┘
            │            │
          YES           NO
            │            │
            ▼            ▼
   ┌────────────┐  ┌────────────────────┐
   │ 路径 A:     │  │ 路径 B:             │
   │ import 该仓 │  │ 自己列 30-50 条     │
   │ 库 + 适配   │  │ 事件 (用 LLM 协助    │
   │ schema      │  │  起草 + 人工校对)   │
   └────────────┘  └────────────────────┘
            │
            ▼
   ┌────────────────────────────────┐
   │ 数据**完整度足够 Phase 1**?    │
   │ (30-50 条先秦+春秋战国事件)   │
   └────────────────────────────────┘
            │            │
          YES           NO(只有朝代,无事件)
            │            │
            ▼            ▼
   ┌────────────┐  ┌────────────────────┐
   │ 单源足够    │  │ 路径 C: 混合        │
   │ 直接用     │  │ 朝代 = 仓库,        │
   │            │  │ 事件 = 自己列       │
   └────────────┘  └────────────────────┘
```

---

## 兜底方案

如果三个候选都没有合适许可,或数据完全不可用,**不卡住 Phase 1**。
直接走"自己列 30-50 条事件"路线 — 一个下午配合 LLM 起草 + 自己校对就完事,
比纠结仓库快多了。Phase 1 真正的产出是**手机上能滚的 UI**,不是"完美的数据
来源"。

---

## 后续

- Phase 1.1 完成后,在本文档底部附"实地验证结论"段落
- 选定的源记到 `docs/decisions.md`(ADR)
- 不选的源在本文档备注一笔,免得后面忘了为什么 pass

---

## 图片源调研(2026-05 新增)

### 候选图片源

| # | 源 | 协议 | 内容 | 适合 Phase 1? |
|---|---|---|---|---|
| 1 | [Wikimedia Commons](https://commons.wikimedia.org) | CC-BY-SA / CC0 / Public Domain | 真实文物 / 传统画像 / 地图 | ★★★★★ 主力 |
| 2 | [中文维基百科](https://zh.wikipedia.org) | CC-BY-SA-3.0/4.0 | 主条目首图 | ★★★★ |
| 3 | 故宫博物院官网 | "未经许可不得使用" | 高清文物 | ⚠ 仅本地 review |
| 4 | 国家博物馆官网 | 部分 CC | 国家级文物 | ★★ 备选 |
| 5 | 百度百科 | 来源混乱 | 杂图 | ⚠ 仅本地 review |
| 6 | AI 生成 (MJ/SD) | 用户拥有 | 任意 | ✗ 历史准确性争议 |

### Phase 1 图片来源决策(ADR-026)

```
   仅限源 1 + 2(Wikimedia + Wikipedia 中文)
   ────────────────────────────────────────
   理由:
   ✓ 协议干净(公开仓库 OK)
   ✓ 内容覆盖度高(80%+ 朝代 + 人物有图)
   ✓ 高清(传统文物图分辨率足够)

   故宫 / 百度 / AI 推迟到 Phase 2 评估
```

### 爬取工具

[D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) — Python 反检测爬虫库:
- Cloudflare 绕过(以备未来 Wikimedia 加防护)
- Auto-relocate elements(网站改版后自动追)
- 异步支持,批量爬取效率高
- Phase 1 用法相对简单,主要用其 `Fetcher` 接口

### Wikimedia 图片获取建议

```python
# 伪代码,Phase 1.4 实施时具体写
from scrapling import Fetcher

def find_hero_image(entity_name: str) -> list[ImageCandidate]:
    """根据实体名找候选图(权重排序)"""
    # 1. 维基条目首图(权威)
    # 2. Commons 搜索 entity_name 标题/描述匹配
    # 3. 按 license / resolution / 来源权威打分
```

### 自动评分规则(降低人工筛选成本)

```
   分辨率 ≥ 800x600           +2
   来源 commons.wikimedia.org  +3
   文件名含实体名              +2
   标签含 "painting/statue/portrait/artifact"   +2
   非 thumbnail               +1
   尺寸 ≥ 200KB(非过小压缩)  +1

   按总分倒序排,top1 默认采用
   你点"备选"按钮可切换 top2/3
```

### Phase 1 图片任务量预估

```
   25 朝代 hero            ~2 小时(快速筛选)
   β 时段人物 ~50 张       ~3-5 小时
   ──────────────────────
   总计                    ~5-7 小时
```

事件场景图(~150-180 张) Phase 1 不做。

