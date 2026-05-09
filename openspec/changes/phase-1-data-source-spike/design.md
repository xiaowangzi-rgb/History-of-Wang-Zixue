## Context

Phase 1 范围已扩到"全 25 朝代骨架 + β 深耕(尧舜禹+夏+商+西周)"(ADR-016)。
本变更产出全部 Phase 1 数据 + 工具链,**不含** Flutter 树图实现(独立的下一
个 change)。

**约束**:
- 时段: 尧舜禹 → 改革开放前(每朝代 ≤ 100 件)
- 字数: summary 150-500 字 / body 1-2K 常态 / 5K 字硬上限
- 朝代年份权威: 夏商周断代工程
- 树拓扑: regime 含 `parentRegimeId` / `mergedIntoRegimeId` /
  `siblingRegimeIds`,用于树形 UI 渲染
- LLM 仅作 β 深耕的起草助手,**不**生成骨架数据
- 公开仓库,数据放结构化 JSON(不放图书 PDF)

**已有基础**:
- `docs/data-schema.md` v0.6 已写
- `docs/timeline-design.md` v2 已写(树图设计)
- `docs/data-source-survey.md` 候选仓库清单(浅层 WebSearch)
- ADR-013 ~ ADR-017 已沉淀

## Goals / Non-Goals

**Goals**:
- 1-2 个月业余周末(累计 ~6-12 周末)走完整个 Phase 1 数据生产
- 全 25 朝代骨架 + β 4 时段深耕全部入 `data_source/`
- `tools/validate.py` 全 pass,`tools/build.py` 产出 `assets/data/*.json`
- 选定的数据源 + pass 掉的源都记进 ADR-018
- 阻塞解除 → 下一 change(`phase-1-tree-renderer`)可以接 Flutter 实现

**Non-Goals**:
- Flutter 代码 / UI 实现(下一 change)
- 春秋战国 / 秦 / 汉 / ... 深耕(Phase 2+,按时间顺序逐个)
- person 字段 persona / systemPrompt(Phase 3)
- CBDB 接入(Phase 3)
- LLM 生成骨架数据(只允许在 β 深耕用作起草)
- schema v1.0 冻结(等 Phase 1 验证后)

## Decisions

### D1: 候选仓库验证方法 = clone + 评分(同前 + 多源)

延续上版决策,但范围扩大: 不再只选"一个"仓库,而是为每类数据找最佳源:
- 朝代骨架: Hellohistory(主)+ 断代工程补缺(BC2070-BC841)
- 事件骨架: 维基百科年表 + Hellohistory + ScottYuan09 三源 merge
- 关键人物: 维基数据 SPARQL + 人工挑选

每个候选 5 分制评分,产物在 `docs/data-source-survey.md` 底部。

### D2: 树拓扑数据来源 = 人工梳理 + 验证

`parentRegimeId` / `mergedIntoRegimeId` / `siblingRegimeIds` 这些字段**没有
现成来源**(没仓库提供"中国朝代谱系图"的结构化数据)。所以:

- 由我(用户)+ Claude 协作整理一份**完整中国朝代谱系**
- 落到 `data_source/regimes.json` 的拓扑字段
- 关键节点: 三国 / 西晋东晋 / 十六国 / 南北朝 / 五代十国 / 宋辽夏金
- 这是 Phase 1 的"创造性工作量",约 1-2 天

### D3: β 深耕的 LLM 起草工作流

LLM(DeepSeek-V3)允许用作起草:
- 事件 body 草稿 (起因/经过/后果各段)
- 人物 summary 草稿

**严格流程**:
1. 我手列待写事件 + 关键提示给 LLM
2. LLM 出草稿到 `staged/llm-drafts/`
3. **我必须人工校对**,改对后 source 字段从 `llm-draft` 改为 `llm-reviewed`
4. validate.py 检查 `data_source/` 中**没有** `llm-draft` 状态记录

### D4: 字数硬约束怎么校验

`tools/validate.py` 字数计算:
```python
def char_count(s):
    # 含 markdown 标记,不计空白
    return sum(1 for c in s if not c.isspace())
```

- summary: 150 ≤ count ≤ 500
- body: 800 ≤ count ≤ 5000(深耕时段必填),其他时段 body 缺省允许

### D5: 文件组织 = 按朝代/时段拆分

```
   data_source/
   ├── _meta.json                # _schemaVersion + _yearAuthority + _generated
   ├── dynasties.json            # 全朝代骨架,一文件
   ├── regimes.json              # 全部政权,一文件(含树拓扑)
   ├── events/
   │   ├── legendary.json        # ★ β 深耕
   │   ├── xia.json              # ★ β 深耕
   │   ├── shang.json            # ★ β 深耕
   │   ├── western_zhou.json     # ★ β 深耕
   │   ├── spring_autumn.json    # 占位
   │   ├── warring_states.json
   │   ├── qin.json
   │   ├── ...
   │   └── prc_pre_reform.json   # 1949-1978
   └── persons/
       ├── legendary.json        # ★ β 深耕
       ├── xia.json
       ├── ...
       └── prc_pre_reform.json
```

按时段拆分让 git diff 可读,合并冲突也少。

### D6: 树拓扑校验是双向 + 闭环

`tools/validate.py` 的树拓扑检查:

1. **双向 sibling**: A.siblings 含 B → B.siblings 必须含 A
2. **parent 存在**: 所有 `parentRegimeId` 引用必须能找到
3. **mergedInto 存在**: 同上
4. **闭环检测**: 不允许 parentRegimeId 形成环(A.parent = B, B.parent = A)
5. **时间相容**: parent 的 endYear ≤ child 的 startYear(soft warning, 因为
   实际历史中分裂可能逐步发生)

## Risks / Trade-offs

**[R1] 树拓扑数据手工梳理出错** → Mitigation: D2 提到的人工梳理,Claude 可
以辅助 review。validate 的双向一致性检查是网,会 catch 大部分笔误。

**[R2] β 深耕字数 5K 上限频繁触发** → Mitigation: 上限其实很宽松(5K 字够
写一篇详细科普),触发说明事件本身需拆分(如"安史之乱"可拆为"起因/前期/平
息"三个事件)。validate 报错时可指导拆分。

**[R3] LLM 起草 hallucination 进入 data_source** → Mitigation: D3 严格流程 +
validate 阻断。校对时重点验"年份/人物/地点/数字"是否准确。

**[R4] 多源 merge 冲突难解** → Mitigation: D5 单一权威(断代工程),不强求
保留所有来源信息。冲突按 ADR-018 选定的优先级覆盖。

**[R5] β 深耕 40-70 件事件,每件 1-2K 字,工作量约 1-2 个月** → Mitigation:
不强求 Phase 1 一次完成全部。可以接受 Phase 1 close 时尧舜禹+夏完成,商西周
仍在校对(只要全朝代骨架完整 + 至少 30 件深耕事件即可)。

**[R6] 朝代年份的"夏商周断代工程"在学界仍有争议** → Mitigation: ADR-017
已说清是项目内部约定,不是学术声明。仍然在 dynasty 加 `yearUncertainty:
"century"` 让 UI 表达不确定性。

## Migration Plan

不适用(项目第一次有数据)。

但要注意: 现有 phase-1-data-source-spike change 的旧 specs / tasks(基于
v0.5 schema 和小范围)被本次大改**直接覆盖**,git history 留 trail。

## Open Questions

- 春秋战国诸侯具体录哪些?7 雄全画 还是 主要 5 国 + 折叠?(实施时决定)
- 五代十国 16 个政权全画还是只画"五代"?(实施时决定,不影响 Phase 1 因为
  五代十国不是深耕时段)
- 改革开放前的边界精确到哪年? 1976 (毛泽东逝世) / 1977 (恢复高考) /
  1978 (十一届三中全会)? → 倾向 1978,理由是"改革开放"标志事件就是
  十一届三中全会(实施时记 ADR)
