# Roadmap — 阶段路线图

> "自用 + 长期项目"的现实节奏:**不试图一次拿到所有数据,按朝代逐步推进**。

---

## 阶段 0: 项目骨架 ✅(本次完成)

**产出**:
- ✅ git 仓库初始化
- ✅ OpenSpec init(`.claude/` + `openspec/`)
- ✅ `.gitignore` / `LICENSE` / `data_source/LICENSE`
- ✅ `CLAUDE.md` / `README.md`
- ✅ `docs/` 全套设计文档
- ✅ 占位空目录(`tools/` / `personas/` / `assets/data/` / `data_source/`)
- ✅ 第一次 commit + push

**结束态**: 任何人 clone 仓库 + 看 README → 理解项目意图 + 数据来源 + 协议;
你 cd 到目录用 Claude Code → 立刻接上下文。

---

## 阶段 1: 春秋战国诸子百家试点(1-2 个周末)

**起点为什么是这里**: 见 `decisions.md`。一句话:史实可靠 + 文献丰富 + 思想
对比强烈,完美验证 schema 和 persona 设计。

**任务清单**:

### 1.1 schema 冻结(0.5 天)

- 通过 OpenSpec 提案: `/opsx:propose data-schema-v1`
- 在 `openspec/specs/data-schema/spec.md` 沉淀冻结版本
- 写 `tools/schema/*.json`(JSON Schema 定义)

### 1.2 持久 prompt 模板(0.5 天)

- 写 `personas/template_serious.j2` 和 `personas/template_romance.j2`
- 写 `tools/build_personas.py`(最小可用版)

### 1.3 第一个完整人物:孔子(1-2 天)

**手工 + LLM 协作**填一份完整 `data_source/persons/spring_autumn.json`:
- 仅含一条:孔子(完整字段)
- 人工填:基础信息 / 主要关系
- LLM 草稿:summary / personality / speechStyle
- 你校对

跑通: `python tools/build_personas.py` → 输出 `assets/data/persons.json`,
含 `systemPromptSerious` 字段。

### 1.4 端到端对话验证(0.5-1 天)

**不需要 Flutter 项目还没建**:
- 写 `tools/test_chat.py`(命令行 LLM 客户端)
- 加载 `assets/data/persons.json` 中孔子的 systemPrompt
- 命令行和孔子聊几轮,人工评估:
  - ✅ 严肃模式聊"如何治国"引用《论语》原文,推礼乐
  - ✅ 切到演义模式有差异
  - ✅ 问"你怎么看苏轼" → "未之闻也"
  - ✅ 自称"丘",不用"我"
  - ✅ 不出现"OK"等现代词

### 1.5 推广到其他诸子(2-3 天)

孔子跑通后,加 5-10 个诸子:
- 老子 / 孟子 / 庄子 / 墨子 / 韩非子 / 孙武

每加一个,跑 build + 测试对话。这个阶段很愉快,因为每个人物都能独立验证。

**阶段 1 结束态**: 春秋战国 ~10 个核心人物,每人都能在命令行里聊得有模有样。
schema 和 persona 模板被 6-10 个不同人物压力测试过,大概率是正确的。

---

## 阶段 2: Flutter app 雏形(2-3 个周末)

**目标**: 把阶段 1 的对话能力包进 app,让你能在手机上玩。

### 2.1 Flutter 项目骨架

- `flutter create .`(在项目根)
- `pubspec.yaml` 加依赖:`flutter_secure_storage` / `riverpod` / `freezed` /
  `dio` / `http` / `path_provider` / `sqflite`
- 项目结构按 `architecture.md` 的 lib/ 子目录组织

### 2.2 数据加载层

- 启动时从 `assets/data/persons.json` 读全部 person 数据进内存
- 用 Freezed 生成 model
- Repository pattern 包装

### 2.3 设置页 + LLM 客户端

- 设置页让用户填 baseUrl / apiKey / modelName
- `OpenAIClient`:OpenAI 兼容,支持 SSE 流式
- "测试连接"按钮

### 2.4 最简陋的人物列表 + 对话页

- 列表:展示阶段 1 那 ~10 个诸子,卡片样式
- 详情页:summary + "💬 对话"按钮
- 对话页:消息列表 + 输入框 + 流式输出
- 模式切换 toggle

### 2.5 对话历史

- SQLite 存 session + messages
- 不同 person 独立 session 列表
- 后退能看历史 session

**阶段 2 结束态**: 你能在自己手机上点"孔子" → 进入对话 → 流畅聊几轮。
无时间线、无朝代图、无做题,但**核心特色**已经活了。

---

## 阶段 3: CBDB 接入 + 全朝代铺开(持续推进,~2-3 个月)

**目标**: 人物数据从 ~10 扩到几百,覆盖主要朝代。

### 3.1 CBDB 抽取(1 周末)

- 下载 CBDB SQLite
- 写 `tools/etl/extract_cbdb.py`
- 试点抽取**唐朝**(因为 CBDB 唐朝数据最全)
- 输出 `staged/persons_cbdb.json`

### 3.2 多源 merge(1 周末)

- 写 `tools/etl/merge_persons.py`
- 唐朝走通 CBDB + Wikidata 合并

### 3.3 LLM 富化批处理

- 完善 `tools/enrich/*.py`
- 启动批量 enrich(后台跑几小时)
- 校对 - 校对 - 校对(这是工作量大头)

### 3.4 朝代逐个铺开

按这个顺序:
1. 春秋战国(已做)
2. 秦汉(LLM 生成 + Wikidata,因为 CBDB 弱)
3. **唐**(CBDB 主力,数据最丰富)
4. 宋(同样 CBDB 主力)
5. 三国(用户最熟,做"演义模式"差异化最明显)
6. 明清

每个朝代铺开一个,提交一次,你和家人就能用一次。**渐进式有反馈,持续动力**。

---

## 阶段 4: 时间线 + 朝代脉络图 + 做题(并行,~2-3 个月)

数据铺开过程中,UI 模块同步开发:

### 4.1 时间线模块(1-2 周末)

- 纵向 ListView + 缩放手势
- `event.category` 配色
- 点事件 → 弹关联人物

### 4.2 朝代脉络图(2-3 周末)

- `CustomPainter` 自绘 Swimlane
- 数据驱动:从 `dynasties.json` + `regimes.json` 渲染
- 三国 / 南北朝 / 五代十国正确分叉
- 动画 / 缩放 / 点击

### 4.3 做题 + SRS(1-2 周末)

- SuperMemo-2 简化版调度
- 5 种题型(单选 / 多选 / 时间排序 / 连连看 / 填空)
- 每日推送

### 4.4 关系网图(1 周末)

- 人物详情页力导向图
- 点节点跳转

**阶段 4 结束态**: 四大模块全活,可以发给家人朋友试用。"自用 demo" 完成。

---

## 阶段 5+: 长期演化

视使用反馈决定:

- 群聊功能(多人物对话)
- 真实人物画像(版权处理 + 设计)
- 文物 / 古建筑数据
- 笔记 + 高亮
- 跨设备同步(可选,需要后端)
- 上架(要不要走 App Store / Play 见心情)
- 世界史扩展
- 移植 PWA / 桌面端

---

## 工作量预估(单人,业余)

| 阶段 | 周末数 | 备注 |
|---|---|---|
| 阶段 0 | ~1 | 已完成 |
| 阶段 1 | 1-2 | 关键验证期 |
| 阶段 2 | 2-3 | UI 起步 |
| 阶段 3 | ~10-15 | **数据校对是大头** |
| 阶段 4 | 5-7 | UI 模块 |
| 总计 | **~20-30 个周末** | 约 5-7 个月 |

**这是一个长期项目**。前 2-3 个周末跑通孔子 demo 体验非常关键,验证产品方向
是不是真的让你愉悦。如果不愉悦,及时调整或叫停 — 自用项目最大的浪费是"硬撑
做完一个自己已经不爱的东西"。

---

## 节奏建议

- **每周末投入半天-一天**,不强迫
- **每个朝代铺开后 commit + push 一次**,有里程碑感
- **遇到瓶颈优先调研而非硬干**,数据问题 80% 是"找对源" + "校对策略"
- **保留"原汁原味"的快乐**,看自己生成的孔子说话本身就是这个项目的奖励
