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

## 阶段 1: 树形脉络图 + β 深耕 + 数据热更(全职 2-3 周 / 业余 1-2 月)

> ⚠️ 2026-05 多次重定位:
> - v1: "孔子单人物对话跑通" → 已废弃
> - v2: "时间线 MVP,先秦+春秋战国" → 已废弃(范围太小)
> - v3 (current): "全 25 朝代树图骨架 + β 深耕(尧舜禹+夏+商+西周)+ 数据热更"
> 设计动机见 `docs/decisions.md` 的 ADR-013 ~ ADR-020。

**起点为什么是这样**:
- 树形脉络图是项目最强差异化(任何通用 LLM/wiki 给不了),做出来朋友看一眼就懂
- β 深耕保证 Phase 1 完成时有"实质内容",不是空骨架 demo
- 数据热更让你 push 一次 GitHub commit 就能给朋友推送新内容,**Phase 1 只发一次 APK**
- 数据策略 = 多源 git 仓库 merge + LLM 起草 β 深耕 body + 你校对

**任务清单**:

### 1.0 doc 重定位 ✅ (本次完成)

- 修订 `CLAUDE.md`、`roadmap.md`、`persona-design.md`
- 新增 `docs/timeline-design.md`(时间线模块详细设计)
- 新增 `docs/data-source-survey.md`(现成 git 仓库调研)

### 1.1 数据源 spike(0.5-1 天)

- 详细评估 `data-source-survey.md` 列出的候选仓库
- 真去 clone 看格式 + 验证许可证
- 产出: 选定 1-2 个仓库作 import 起点 + 留 fallback

### 1.2 Schema 简化 v0.5(0.5 天)

- 砍掉 person 的 `personality / selfReference / speechStyle / systemPrompt*`
  字段(留到 Phase 后期再加)
- 留下 event / dynasty / regime 的核心字段
- 不走 OpenSpec 冻结流程,**仅 v0.5 草案**(等数据进来再 v1)

### 1.3 数据起点(1 天)

**路径根据 1.1 结果分支**:
- 路径 A: 选中仓库导入 → 写 `tools/import_*.py` 适配
- 路径 B: 没找到合适仓库 → 自己列 30-50 条事件(用 LLM 协助起草后人工校对)
- 路径 C: 混合(朝代用仓库,事件自己写)

**产出**: `data_source/dynasties.json` + `data_source/events/pre_qin.json` +
`data_source/events/spring_autumn.json` + `data_source/events/warring_states.json`

### 1.4 Flutter 项目骨架 + 时间线页(2-3 天)

- `flutter create .`
- 最简依赖: `flutter_riverpod` / `freezed` / `path_provider`
- `assets/data/events.json + dynasties.json` 加载到内存
- 时间线 v0:
  - 纵向 ListView(顺序由旧到新)
  - 朝代色块背景(分隔)
  - 事件卡片: 年份 + 名称 + 1 行简介
  - 缩放交互**不在 v0 范围**(可选,1.5 / Phase 2 再加)

### 1.5 数据热更模块(0.5-1 天)

详见 `docs/data-update-strategy.md`。简版:

- 写 `tools/build_manifest.py`,产出 `assets/data/manifest.json`(每个 JSON 文件的 hash + version)
- Flutter 端 `RemoteDataSyncService`:
  - 启动时后台拉 GitHub Raw 的 manifest
  - 比较 hash → 不同则下载新文件到 `path_provider.applicationDocumentsDirectory`
  - 下次启动优先读本地 cache,fallback 用 assets 内置版本
- schema 版本不兼容时显示"请升级 APK"提示
- 部署: 你 push GitHub commit → 朋友 app 启动检测到 manifest 变化 → 自动更新

### 1.6 在自己手机上能看的版本 + 给朋友的 APK(0.5 天)

- Android: `flutter build apk` + adb install + 直接微信发 APK 给朋友
- iOS: Xcode 个人开发者证书 → 真机(最多给 3 个朋友,免 99 美元)
- 朋友首次安装后,以后**只需开 app 就有新内容**(数据热更生效)

**阶段 1 结束态**: 你和朋友打开 app 能看到完整中国史树形脉络图,
β 4 时段(尧舜禹/夏/商/西周)有完整事件 body 和关键人物,
其他朝代骨架显示"待补充"。每次你 push GitHub 朋友自动看到新内容。

---

## 阶段 2: 朝代脉络图 + 人物卡 + 数据扩段(2-3 个周末)

> 2026-05 重定位后: 阶段 2 焦点从"对话 app 雏形"改为"补齐另外 3 个核心模块
> 的 v0 形态"。Flutter 骨架已经在 Phase 1.4 立起来了,这里是模块扩展。

**目标**: 在 Phase 1 时间线基础上,把朝代脉络图和人物卡片立起来,数据从先
秦+春秋战国扩到秦汉。

### 2.1 朝代脉络图 v0(1-2 周末)

- `CustomPainter` 自绘 Swimlane
- 数据驱动:从 `dynasties.json` + `regimes.json` 渲染
- 第一版**不要求**三国 / 南北朝并立分叉(Phase 3 再做)
- 横向时间轴 + 朝代色块,点朝代 → 跳到时间线对应段

### 2.2 人物卡片 v0(1 周末)

- 人物列表页(按朝代分组)
- 详情卡: 基础信息 / 关键事件 / 关系(简单列表,不画网图)
- 数据来源: 还是手填 + git 仓库 import,不调 LLM

### 2.3 数据扩段: 加秦汉

- 沿用 Phase 1.1 选定的数据源,扩到秦汉
- 事件量预计扩到 100-150 条
- 校对周期会变长,这是真实工作量

### 2.4 做题模块 v0(1 周末,可后置)

- 第一版: 时间排序题 + 单选题(2 种题型够用)
- SRS 调度暂用最简版本(每天复习昨天答错的)
- 题目可由事件自动生成:"以下事件按时间顺序排列"

**阶段 2 结束态**: 4 个核心模块都有 v0 形态,数据覆盖到秦汉。能给最铁的 1-2
个朋友看(还不公开 release)。

---

## 阶段 3: 全朝代铺开 + 对话能力恢复(持续推进,~2-3 个月)

> 2026-05 重定位: 对话模块在 Phase 3 才恢复(原 Phase 1)。届时 4 个核心模
> 块已稳,可以放心做加分项,且 schema/数据已经被压力测试过。

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

### 4.3 做题 + SRS(1-2 周末) — **2026-05 降级,可能砍**

> 原计划做题作为 4 大核心之一,2026-05 用户决定 Phase 1-3 都不做。
> Phase 4 视使用反馈再决定是否值得做。

- 若做: SuperMemo-2 简化版调度 + 单选 + 时间排序两种题型
- 若不做: Phase 4 资源用于其他模块

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
