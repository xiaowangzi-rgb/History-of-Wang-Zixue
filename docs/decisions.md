# 关键决策记录(Decisions / ADR)

> ADR 风格的简短决策记录。每条:**决策 → 理由 → 替代方案 → 后果**。
> 决策可被推翻,但推翻时**改文档 + 写新一条 ADR 解释为什么**,不要静默改。

---

## ADR-001: 自用为主,不上架

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 项目定位为自用 + 给家人朋友用,不规划上架 App Store / Play Store。

**理由**:
- 上架要处理 iOS / Android 审核,中国大陆要 ICP 备案
- 历史类 app 内容审查风险大(尤其近现代史)
- 数据版权要严苛梳理
- 自用阶段做出来如果体验不爆,根本不用考虑上架问题

**替代**: 直接公开发布 → 工作量翻 5 倍且分散注意力。

**后果**:
- 技术选型自由(选什么数据源、模型都行)
- 安装方式: Flutter build APK + sideload(Android)/ TestFlight(iOS)
- 未来想上架不阻塞,但不预设这个目标

---

## ADR-002: Flutter 跨端,不做原生

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 用 Flutter 一份代码出 Android + iOS,不做 Swift / Kotlin 原生开发。

**理由**:
- 自用 + 家人朋友 → 必然 Android + iOS 都要
- Flutter `CustomPainter` 做"朝代脉络图"这种自定义可视化比 React Native 强
- 单人开发,跨端节省工作量
- Flutter 中文社区和资料够用

**替代**:
- React Native: 自定义可视化弱
- 原生: 一个平台一套代码,工作量翻倍
- PWA: 离线 + 流式 LLM 体验在浏览器有限制

**后果**: Dart 学习成本(中等)。可视化模块用 Flutter 是优势,后续做朝代图
不会卡。

---

## ADR-003: 仓库 Public 开源

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: GitHub 仓库 `History-of-Wang-Zixue` 设为 Public。

**理由**:
- 个人项目自带宣传效果(有兴趣的人可以看 / star / fork)
- 倒逼"第一天就把合规做对"(.gitignore 严格、双协议、上游署名)
- LLM 生成的人设 prompt 公开反而是 feature(别人能学)

**替代**: Private → 失去公开收益,但合规压力小一些。

**后果**:
- API key 绝不能进 git,养成肌肉记忆
- 双协议(代码 MIT + 数据 CC-BY-SA-4.0)
- README 必须署名上游(CBDB / chinese-poetry / Wikipedia)
- CBDB 原数据不直接打包仓库

---

## ADR-004: 数据双协议(代码 MIT + 数据 CC-BY-SA-4.0)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 项目根 `LICENSE` 用 MIT(覆盖代码),`data_source/LICENSE` 用
CC-BY-SA-4.0(覆盖数据)。

**理由**:
- 数据来自 Wikipedia / Wikidata(CC-BY-SA),衍生数据**必须**同协议
- 代码 MIT 让别人复用流水线工具更方便(不强传染)
- 这是 OpenStreetMap 等"代码 / 数据双协议"开源项目的标准做法

**替代**:
- 全 MIT: 违反 Wikipedia/Wikidata 上游条款
- 全 CC-BY-SA: 代码也变传染性,劝退贡献者

**后果**: 别人 fork 数据需署名 + 同等协议;fork 代码只需 MIT 署名。

---

## ADR-005: Phase 1 起点 = 春秋战国诸子百家(不是尧舜禹,不是秦)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 第一个跑通完整数据流水线的朝代是**春秋战国**,首个完整人物是
**孔子**。

### 为什么不是尧舜禹

- 三皇五帝 / 尧舜禹是**传说时代**,史实极不可靠
- 没有可靠年份(只能"约公元前 23 世纪")
- CBDB 不覆盖,Wikidata 多归类"中国神话"
- LLM 扮演大禹聊"治水"只能纯虚构,**严肃模式和演义模式无法区分**(都是创
  作)
- 趣味性最高,但**工程难度也最高,没有任何"真实数据"做约束**

**保留尧舜禹 in 数据**(否则脉络图断头),用 `historicity: legendary` 字段
标记,UI 雾化处理。**但不做试点**。

### 为什么不是秦朝(原始建议被推翻)

- 秦朝核心人物只有 ~30 人
- LLM 扮演时**引用文献有限**(主要《史记》转述)
- 战国紧接秦,数据其实是连续的

### 为什么是春秋战国

- 30-50 个核心人物(孔子、老子、孟子、庄子、墨子、韩非子、孙武…)
- **都有大量传世文献**(论语、道德经、孟子、庄子、韩非子、孙子兵法)
  → LLM 扮演时有真实文本约束,严肃模式可引用原文
- 思想流派对比强烈(儒/道/法/墨/兵)→ 同一问题不同人物答得有戏剧张力
- 时间跨度合适(BC 770 - BC 221)
- 验证 schema 覆盖度比秦朝高

---

## ADR-006: LLM 双轨制(主力 DeepSeek-V3 + 精修 Claude/GPT)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- 批量生产(~80% 调用): **DeepSeek-V3**
- 困难校对 / 一致性 review(~20% 调用): **Claude Sonnet 4.6** 或 GPT-4o

**理由**:
- DeepSeek-V3 中文古文质量第一梯队,价格 1/10 - 1/20 GPT-4o,几千次调用不
  心疼
- 全 Claude / GPT-4o 钱包受不了
- 全 DeepSeek 在最复杂的角色一致性 review 上偶有不足
- ETL 脚本支持 `--model` 参数,环节级别选模型

**替代**:
- 单一模型: 要么贵要么质量妥协
- 本地小模型(Qwen2.5-7B): 自用阶段质量差距太大,不考虑

**后果**:
- 注册 DeepSeek 账号(国内手机号即可),拿 key
- 现有的 Claude / OpenAI key(走中转)用于精修
- API key 通过环境变量(`DEEPSEEK_API_KEY` 等)传入,不进文件

---

## ADR-007: system prompt 预生成,不临时拼装

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: system prompt 在**开发期**(`tools/build_personas.py`)一次性渲染
为字符串,写回 `assets/data/persons.json` 的 `systemPromptSerious /
systemPromptRomance` 字段。运行期 app 直接读取该字符串,**不做模板渲染**。

**理由**:
- 冷启动快,无运行时拼接
- 可审阅(能直接 cat 看每个人物的 prompt 是什么)
- 可缓存(中转网关 prefix cache 命中率 100%)
- 可版本化(prompt 进 git,改模板能 diff 全部人物 prompt 变化)
- Flutter 端零业务逻辑,纯字符串拼接

**替代**: 运行时拼装 → 慢、不可审、cache miss、Flutter 端引入模板引擎(Dart
没好用的 Jinja 等价物)。

**后果**:
- 改 prompt 模板必须 bump `promptTemplateVersion`,重跑 build
- 用户 session 绑定 prompt 版本(避免对话风格中途突变)

---

## ADR-008: 群聊功能延期到 v2

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: v1 不实现"多人物群聊"功能。

**理由**:
- 调度复杂(谁说话?顺序?互相打断?)
- 单人物体验先打磨好
- 用户分散注意力,难以判断"哪个人物的人设有问题"

**保留扩展空间**:
- system prompt 不写死"你只对一个人说话"
- 对话历史 schema 已支持多 speaker

**替代**: v1 就做群聊 → 工作量翻倍且单人物质量难评估。

**后果**: v2 才考虑;阶段 1-4 都是单人物对话。

---

## ADR-009: 不在阶段 0 写 Python 脚本和 Flutter 骨架

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 阶段 0(项目骨架种入)**只写文档 + 合规文件 + 占位空目录**,不写
任何真实代码或运行时配置。

**理由**:
- 没跑通孔子单人物试点之前,任何实现细节都是猜的
- 写空 `flutter create` 项目会让 git 历史变脏
- 写半成品 `tools/*.py` 会成形式主义代码债

**替代**: 阶段 0 就把所有脚手架搭起来 → 后续大量返工。

**后果**:
- 阶段 1 第一步是用 OpenSpec `/opsx:propose` 提议代码骨架,写 schema 和模板
- `flutter create` 在阶段 2 才执行

---

## ADR-011: 核心特色重定位 — 对话从"核心"降为"加分项"(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted(推翻 ADR-005 + 部分推翻 CLAUDE.md 原始定位)

**决策**:
- 项目核心 = 时间线 / 朝代脉络 / 人物 / 关键事件 / 做题 (5 项,前 4 个是 4 大模块)
- 人物对话(LLM 扮演)从"核心特色"**降级为加分项**,Phase 3+ 再做
- Phase 1 起点从"孔子单人物对话跑通"改为"**时间线先行,先秦+春秋战国 MVP**"

**理由**:
- 对话价值天花板 = LLM 通用能力,差异化弱(用户为啥不直接用 Claude/ChatGPT?)
- 对话**强依赖** API key,设置门槛劝退非技术朋友
- 离线可用性 = 0
- 真正的差异化在**策展品味 + 中国史可视化结构**(时间线 / 朝代图),
  这是任何通用 LLM 给不了的
- 时间线做出来后视觉冲击 + 反馈循环短(开发期 3-5 天就能在手机上滚)

**替代**: 继续按对话核心走 → 5-7 个月才能把 4 大模块全做完,中间反馈周期长,
新鲜感衰减风险大。

**后果**:
- `CLAUDE.md` 4 大模块顺序重排,对话进"加分项"段落
- `roadmap.md` Phase 1 + Phase 2 全重写
- `persona-design.md` 顶部加降级标注(内容保留供 Phase 3 恢复时用)
- 新增 `docs/timeline-design.md`(Phase 1 主战场)
- 新增 `docs/data-source-survey.md`(数据源调研)
- ADR-005 关于"Phase 1 = 春秋战国诸子百家"的决定**部分推翻**: 春秋战国仍然
  是首个时段,但**只取事件不取人物 persona**
- ADR-008(群聊)从"v2"延期到"对话恢复后",时间无所谓

---

## ADR-012: 数据策略 — 优先现成 git 仓库,LLM 富化降级(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- 事件 / 朝代数据**优先从现成 GitHub 仓库 import + 适配 schema**
- LLM 富化(原 ADR-006 主力角色之一)**降级**: 只在"仓库找不到"或"现代汉
  语转译"等场景使用
- CBDB 接入推迟到 Phase 3(人物模块恢复时)

**理由**:
- LLM 生成的事件草稿**校对成本** ≈ 自己重写,不省时
- 现成仓库有可信度优势(能溯源)
- 避免"LLM hallucination 进入 data_source"的污染风险(ADR-007 阻断了这条但
  仍是 LLM 生成内容,审计成本仍在)

**用户意向澄清(2026-05)**: 自用项目,版权不卡;但**公开 git 仓库**仍然只放
结构化数据,不入图书 PDF / 整本电子书(那是格式问题,不是版权问题)。

**替代**:
- 全 LLM 生成: ADR-006 原方案,审计工作量太大
- 全手填: 30-50 条事件可行,但扩到全朝代不现实

**后果**:
- Phase 1.1 spike: 真去 clone 候选仓库验证
- 选定的源记到本文件(ADR-013 待写)
- LLM 仍然有用(转译 / 补缺草稿),但不是数据来源主力
- `CLAUDE.md` 的"数据来源"表已更新

---

## ADR-013: 时间线 UI = git 风格树形朝代脉络图(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted(进一步细化 ADR-011 的"时间线先行")

**决策**:
- 时间线模块和原"朝代脉络图"模块**合并**为单一 UI: **git 风格树形脉络图**
- 视觉方向: **从下到上**(树根 = 远古,树梢 = 现代)
- 节点层级: 朝代节点(主) → 政权节点(并立期) → 事件 + 人物(展开后)
- 实现: Flutter `CustomPainter` 自绘 + `Stack` 叠 GestureDetector

**理由**:
- 中国史天然适合 git 分支隐喻: 三国 / 南北朝 / 五代十国 / 春秋战国诸侯并立
  = 多 branch;王朝继承 = fast-forward;统一 = merge commit
- 普通纵向 ListView 时间线**画不对并立期**(swimlane 也勉强)
- 树形结构在 25 朝代 + 上千事件的规模下仍可读(分层 + 折叠)
- 这是 app 最强的差异化视觉,任何通用 LLM 不能给

**替代**:
- 纯纵向 ListView: 无法表达并立,失去差异化
- 横向 swimlane: 屏幕窄 + 用户不习惯横向滑
- 网状关系图: 失去时间感,不适合"时间线"语义

**后果**:
- `docs/timeline-design.md` 重写为 v2(已完成)
- `docs/data-schema.md` regime 加 `parentRegimeId` / `mergedIntoRegimeId` /
  `siblingRegimeIds` 字段(已完成)
- 实现复杂度: Phase 1.4 从"2-3 天纵向 ListView"扩到"6-10 天 CustomPainter 树渲染"
- "从下到上"反直觉,Phase 1.4 实施时观察反馈,留"反转"开关空间

---

## ADR-014: 数据范围扩到 尧舜禹 → 改革开放前(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted(推翻 ADR-011 的"先秦+春秋战国"窄范围)

**决策**:
- 项目最终覆盖范围: **尧舜禹 → 改革开放前(约 1976/1978)**
- 每朝代上限: **100 件最关键事件**(总量预计 1000-1500 件)
- 关键人物: 每朝代 30-50 人(总量 750-1250 人)
- 朝代起讫年份: **夏商周断代工程**为权威,争议年份 `yearUncertainty: "century"`
- "近代"边界明确: **改革开放前止步**(规避 1978+ 政治敏感)

**理由**:
- 用户明确意图: "颗粒度越细越好",且核心要"完整中国史脉络"
- 单一时段(春秋战国)做完是 demo,不是产品 — 朋友看了会"然后呢"
- 尧舜禹有传说时代史实争议,但 schema 的 `historicity: "legendary"` 字段就是
  为它设计的,正好压力测试

**替代**:
- 限定先秦+春秋战国: 工作量小但产品形态弱(ADR-011 原方案)
- 扩到 1949+: 政治敏感 + Github 公开仓库审查风险

**后果**:
- 校对工作量大幅增加(预计全朝代 125-250 业余小时,4-8 个月)
- Phase 1 不可能一次做完,改用"全骨架 + 单深耕"模式(见 ADR-016)
- 数据策略需多源 merge(单一 git 仓库覆盖不全 — Hellohistory 限 BC841~1911)

---

## ADR-015: Schema v0.6 — markdown body + 字数硬约束(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- event 字段加 `body`: markdown,**1-2K 字常态,5K 字硬上限**
- body 推荐结构: `## 起因` / `## 经过` / `## 后果`(可扩 `## 影响` / `## 评价`)
- `summary` 字段: 150-500 字(树图卡片用)
- 字数硬约束在 `tools/validate.py` 强制(超过 5K → 报错并阻塞 build)
- `participants` 仅含主角/参与者,**不含**"被影响者"(简化语义)
- `_schemaVersion` 顶层字段升至 `"v0.6"`

**理由**:
- 用户明确: "起因 + 经过 + 后果 + 影响人物 = 1-2K 字,不超过 5K 字"
- 结构化 4 字段切死了某些事件(如"郑和下西洋"经过巨长但起因短)
- markdown 灵活 + 树图卡片用 summary,详情页用 body,职责清晰
- 字数上限阻止"越写越多"导致 JSON 包爆炸(2000 事件 × 5K = 10M 字 → 30MB)

**替代**:
- 4 个结构化字段 (cause/process/consequence/impactedPersons): 不灵活
- 无字数约束: 风险数据无序膨胀
- 无 summary 字段: 树图卡片每条要渲染整段 body,卡片渲染慢

**后果**:
- `tools/validate.py` 加字数校验规则
- Flutter 端引入 `flutter_markdown` 包(详情页用)
- assets/data/events.json 体积上限可控:1500 事件 × 5K 字 × 3 字节 = 22 MB
  (实际平均 1.5K 字,~7 MB,APK 内部可接受)

---

## ADR-016: Phase 1 形态 = 全朝代骨架 + β 深耕(尧舜禹+夏+商+西周)

**日期**: 2026-05-09
**状态**: ✅ accepted(进一步细化 ADR-011 / ADR-014)

**决策**:
- Phase 1 同时做两件事:
  - **全 25 朝代骨架**(树图渲染需要的所有 dynasty / regime / 拓扑)
  - **β 深耕**: 尧舜禹 + 夏 + 商 + 西周(40-70 件事件,完整 body + 人物)
- 其他朝代占位: 每朝代 5-10 个事件标题 + 5-10 个人物名,无 body
- Phase 后续按时间顺序逐个朝代深耕(Phase 2 = 春秋战国深耕,...)

**理由**:
- 全骨架 → 树图视觉立刻完整,demo 给朋友看就有"全中国史"感
- 单深耕 → 内容详细度有保证,不至于"什么都没"
- 选 β(尧舜禹起步)而非热门朝代(三国/唐): 用户明确希望"按朝代时间线",
  按时间顺序首站就是上古
- 上古事件量小,Phase 1 工作量可控(~6 周末业余)

**替代**:
- 选三国/唐先深耕: git 树图能秀肌肉,但跳过上古导致后续跨度别扭
- 全部 25 朝代都深耕: 工作量爆炸,Phase 1 永远不结束
- 只做骨架不深耕: demo 像个空壳,朋友点开"待补充"会觉得是 demo 早期版本

**后果**:
- Phase 1 范围(尧舜禹/夏/商/西周)成为 schema 压力测试的最佳样本(传说时代 +
  半信史 + 完整信史)
- 历经 Phase 1 后 schema 应可基本冻结到 v1.0
- Phase 2+ 滚动深耕,每个朝代发一次更新

---

## ADR-017: 朝代年份采纳"夏商周断代工程"为权威(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- 全项目朝代起讫年份**默认采用夏商周断代工程结论**
- 争议年份(如 -1046 vs -1027 武王伐纣)在 dynasty 里用断代工程值,
  `yearUncertainty: "century"` 标注
- dynasty 加 `_yearAuthority` 字段记录采纳来源
- 不接受单一考古学者新说覆盖断代工程主流(避免 schema 反复变动)

**理由**:
- 必须有一个**统一权威**,否则各 dynasty 起讫不一致
- 断代工程是国家级课题,主流学界采纳,公众教科书使用
- 用户明确选了"断代工程"

**替代**:
- 《史记·三代世表》传统纪年: 部分时段精确度低
- Wikipedia 中文当前共识: 不稳定,版本化困难
- 个别考古修订: 学界仍在演进,不适合作权威基准

**后果**:
- Phase 1 数据生产时 `dynasties.json` 起讫直接采纳断代工程
- 与其他来源(如 Hellohistory)冲突时以断代工程为准
- 未来主流学界更新时,通过 ADR 推翻本决策 + bump schema 版本

---

## ADR-018: 数据热更(GitHub Raw,Phase 1.5)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- Phase 1 内置**数据热更**模块: app 二进制不变,数据从 GitHub Raw 拉取
- 触发: app 启动时后台拉 `manifest.json`,hash 变则下载新文件到本地 cache
- 加载顺序: cache → assets 内置 → 远程后台同步
- 你 push GitHub commit → 朋友打开 app 自动看到新内容
- 详见 `docs/data-update-strategy.md`

**理由**:
- 数据校对是滚动持续过程,1500+ 事件不可能一次性完成
- 没有热更,每次填一个朝代都要重新打包 + 让朋友重装 → 摩擦大
- GitHub Raw 0 配置,公开仓库已经满足
- Flutter 代码热更几乎不可行(iOS 禁止,Android 复杂),只做数据热更最务实

**替代**:
- 静态 release: 每次发新 APK,朋友重装 → 不可持续
- Cloudflare R2: 速度更好但需要配置 → 推迟到大陆朋友抱怨慢时再切
- 国内 OSS: 月成本几块钱 → Phase 后期视需要

**后果**:
- assets/data/ 加 manifest.json
- Flutter 端加 RemoteDataSyncService
- Phase 1.5 任务(集成在 phase-1 系列 change 中)
- 大陆朋友可能受墙影响,Phase 后期视情切到 R2

---

## ADR-019: 做题模块降级 + 反馈通道砍掉(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted(进一步推翻 ADR-005 / ADR-011)

**决策**:
- 做题模块从"4 大核心"降至"加分项",Phase 1-3 不做,Phase 4 视使用反馈再决定
- app **不内置**反馈入口(意见箱 / Issue 链接 / 邮件 都不要)
- 朋友吐槽走微信,你看见了就改

**理由**:
- 做题工作量大(题型设计 + SRS 调度 + 题目编写),边际价值不确定
- 自用项目朋友圈不到 50 人,反馈走微信完全够用
- 内置反馈入口需要后端或邮件服务,引入复杂度
- 砍掉 = 项目更简单,跑得更快

**替代**:
- 做题保留: 增加几周末工作量,Phase 4 才能产出
- 反馈保留: 引入反馈表单 / 邮件链接,需要后端
- 都做: 项目膨胀,核心做不好

**后果**:
- 4 大模块 → 3 大模块(时间线 / 人物卡 / 数据热更)
- CLAUDE.md / roadmap.md 已更新
- app 设置页只保留: 主题切换 + about + 数据更新检查
- Phase 4 决策待重审(届时已运行 ~6 个月,有真实使用感觉)

---

## ADR-020: 工期估算重置(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- 项目工期估算从"业余周末 5-7 个月"重置为:
  - **全职 + AI 协助**: 10-15 天(2-3 周冲刺)
  - **业余 + AI 协助**: 1-2 个月(每周末 + 部分工作晚上)
- 不再以"个周末"作为估算单位

**理由**:
- 用户挑战: "AI + 现成数据 应该 1 周搞定"
- 重新核算后承认: AI 加持下,纯**生产**速度可以比业余周末快 5-10 倍
- 但**不能被 AI 加速**的瓶颈仍存在: 校对速度 / Flutter 树图调试 / 真机测试
- 1 周冲刺版可达"能玩",但 UI 粗糙、校对仓促,需明确取舍

**Phase 1 范围紧缩选项**(若选 1 周冲刺):
- β 深耕从 40-70 件砍到 20-30 件
- 25 朝代占位事件减到 3-5/朝代(原 5-10)
- Flutter 树图 v0 不做缩放、不做暗色模式
- 数据热更可推迟到 Phase 1.5

**Phase 1 范围扎实版**(2-3 周):
- 维持当前 spec 范围
- 数据热更 Phase 1.5 完整实现
- 至少跑过 2 个朋友的真机测试

**替代**: 业余周末模式仍可选,但更长(1-2 个月)。

**后果**:
- `roadmap.md` 工期改写
- `phase-1-data-source-spike` 的 spec 不变(可吃紧缩或扎实两种节奏)
- 实施时由你选具体节奏

---

## ADR-022: β scope 调整为夏商西周春秋战国(广义夏商周)

**日期**: 2026-05-09
**状态**: ✅ accepted(替代 ADR-016 中的 β = 尧舜禹+夏+商+西周)

**决策**: β 深耕范围调整:
- 砍掉: **尧舜禹**(传说时代,深耕史实风险大)
- 加入: **东周(春秋战国)**(数据丰富 + 趣味性高)
- 最终 β scope: **夏 + 商 + 西周 + 东周(春秋战国)**

**理由**:
- 尧舜禹是 legendary,LLM 起草误差最大、校对压力最重 → 不深耕
- 但 UI 上保留(雾化处理),骨架渲染,等 Phase 2 心情好了再补
- 春秋战国是周朝故事高潮: 诸子百家 / 商鞅变法 / 合纵连横 → 趣味性高
- "夏商周"是常识中的成套概念,做完有完整章节感
- 事件量从 40-70 → 100-180,工作量从 1-2 周扩到 3-5 周(可接受)

**替代**: 维持 ADR-016 原 scope → 砍 LLM 难起草部分,但失去"先秦完整章节"

**后果**:
- `phase-1-data-source-spike` 的 spec / tasks 更新
- LLM 起草工作量增加 ~2-3 倍,但**史实可靠**(校对省力)

---

## ADR-023: 内容比例 — 文化 / 科技偏多,政治偏少(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 每朝代 100 事件按以下比例分布:
- 政治 25% / 军事 15% / 文化 25% / 科技 15% / 外交 5% / 经济 5% / 人物大事 10%
- 文化 + 科技 + 人物大事 ≥ 50%(差异化于传统教科书)

**理由**:
- 传统教科书约 65% 政治军事,枯燥,这是用户痛点("死记硬背太难")
- 文化 / 科技 / 人物事件**趣味性更高**,适合"每天打开"的使用场景
- 对抗"皇帝叙事",建立**多元历史观**

**替代**: 按教科书 65% 政治军事 → 项目失去差异化

**后果**:
- LLM 起草 prompt 含明确比例约束
- 你 review 事件清单时按比例砍政治军事 / 加文化科技

---

## ADR-024: 政治敏感边界 — 安全 / 中立 / 红线 三档处理

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- **安全话题**: 大胆挖现代史学视角(商纣"暴君"修正 / 隋炀帝平反 / 宋朝"积弱"修正等)
- **敏感话题**: 中立陈述,不带价值判断(元清民族政策 / 鸦片战争至民国)
- **红线话题**: 简短陈述事件 + 时间,不做"为什么"解释(国共/边疆/文革)
- **1949-1976 范围**: Phase 1 整体推迟,Phase 后期重新评估是否覆盖

**理由**:
- 公开 GitHub 仓库,内容触线可能 takedown / 账号被封
- 用户做这个 app 的核心价值是**理解历史**,不是政治表态
- 安全话题足够丰富,够支撑 80%+ 内容

**替代**: 全话题大胆挖 → 风险高;全话题中立陈述 → 失去"现代视角"差异化

**后果**:
- `docs/content-style-guide.md` 详细列出三档话题清单
- LLM 起草 prompt 区分话题档次
- Phase 1 数据**不覆盖** 1949-1976(改革开放前)

---

## ADR-025: 内容风格 = summary(A 教科书) + body(C 叙事)双层组合

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 每个 event 用 summary + body 双字段组合:
- `summary` (150-500 字) = **A 风格**: 教科书味,精准,可背诵 — 树图卡片显示
- `body` (800-2000 字常态 / 5000 字上限) = **C 风格**: 历史叙事 + 起因/经过/后果
  + **现代史学视角** — 详情页显示

**理由**:
- 用户喜欢 A 风格的精准(易记忆),也认可 C 风格的合理(易理解)
- schema 已有这两字段,只需明确风格分工
- 用户场景: 树图浏览(读 summary 建认知节点) + 睡前阅读(读 body 深入)
- LLM 起草分两道,prompt 各自聚焦,质量更高
- 校对工作量降低 ~30%(summary 精度高,粗校;body 重点校"故事顺序")

**替代**:
- 只有 summary: 信息深度不足,失去"理解历史"价值
- 只有 body: 树图卡片显示长文本,UX 差
- A 和 C 选一: 两种用户需求都不满足

**后果**:
- `docs/content-style-guide.md` 详细写作规范 + 武王伐纣示例
- LLM 起草分两 pass: summary pass + body pass
- 字数硬约束 body 调整: 800-2000 (常态) / 5000 (硬上限)

---

## ADR-026: 图片策略 — Phase 1 朝代 hero + β 人物画像,Wikimedia 优先,Scrapling 爬取

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- Phase 1 必做: 25 朝代 hero 图(每朝代 1 张,~5 MB 总量)
- Phase 1 可做: β 时段 ~50 关键人物 portrait(夏商西周春秋战国)
- Phase 1 **不做**: 事件场景图(推 Phase 2 视体验决定)
- 来源**仅限 Wikimedia Commons + Wikipedia**(CC-BY-SA / CC0 / Public Domain)
- 故宫官网 / 百度百科图**仅本地 review 用**,不进 public 仓库
- AI 生成图 Phase 1 不用(历史准确性争议)
- 工具: `tools/crawl_images.py` 用 [Scrapling](https://github.com/D4Vinci/Scrapling)

**理由**:
- 图片**显著提升 app 视觉冲击和趣味度**
- Wikimedia 图协议清晰,不踩公开仓库版权雷
- Scrapling 反检测能力强,爬维基类站点足够 + 可应对未来站点改版
- 25 朝代 hero 工作量小(~2 小时筛选),性价比极高
- 事件图 ~150 张工作量大(~12 小时筛选),Phase 2 评估

**替代**:
- 完全无图: Phase 1 简,但视觉乏味
- 全 AI 生成: 历史人物像不可信
- 维基 + 百度 + 故宫多源: 公开仓库版权风险

**后果**:
- schema 加 `dynasty.heroImage` / `heroImageSource` / `heroImageLicense`
- schema 加 `person.portrait` / `portraitSource` / `portraitLicense`
- 工具链加 `crawl_images.py` / `process_images.py` / `build_image_manifest.py`
- 数据热更架构: 图片**单独 manifest**,懒加载(进树图节点才下载该朝代图)
- `docs/data-source-survey.md` 加图片源调研段
- `docs/content-style-guide.md` 写图片处理工作流

---

## ADR-027: 设计语言 = 水墨电子纸 (Ink-Paper) + 中国传统排版

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**:
- app 整体设计语言: **"水墨电子纸"(Ink-Paper)** — 现代极简 + 中国传统排版的克制融合
- 字体: Noto Serif SC (思源宋体) 标题 + Noto Sans SC (思源黑体) 正文,通过
  `google_fonts` 包加载
- 25 朝代色板: 矿物色 / 自然色,饱和度 25-45%,相邻色相隔 ≥ 30°(详见
  `docs/dynasty-palette.md`)
- 树节点造型: 印章风(Seal Stamp Style)
- 传说时代雾化: 沙色 + 灰阶 + 虚线 + 楷书 + opacity 0.6
- 暗色模式: OLED 真黑 #000000(深夜阅读 + 电池友好)
- 移动端规范: SafeArea / 触摸 ≥ 48dp / InkWell ripple / Haptic / BottomSheet 替代 modal
- 完整 token 表: `docs/design-tokens.md`

**理由**:
- ui-ux-pro-max 数据库匹配 **E-Ink / Paper 风格**(reading apps 最佳)+
  **Chinese Traditional 字体配对**(Noto Serif/Sans SC)
- 项目使命是"每天打开学历史" → 阅读型工具 → "电子纸"基调最合身
- 不选 "教育 app 默认" Claymorphism + Vibrant: 黏土风幼龄化,违背"严肃学习"
- 不选纯极简: 失去文化感
- 不选古风装饰过度: 长期看疲劳,违背"每天打开"
- 印章风格树节点: 中国文化标志性视觉,区别于通用圆点
- 朝代矿物色板: 取自中国画颜料,有"翻古书"的统一气质

**替代**:
- 教育 app 默认 (Claymorphism + Vibrant): 不合适
- Glassmorphism: 违背"纸感"基调
- Cyberpunk / Neon: 违背"古"的语境
- Brutalism: 不应景

**后果**:
- `docs/timeline-design.md` 加 UI Visual Design 段
- 新增 `docs/design-tokens.md`(完整 token 表)
- 新增 `docs/dynasty-palette.md`(25 朝代色板 + light/dark)
- Flutter 实施时(Phase 1.4)直接对照 token 表,不再"看心情写颜色"
- 引入 `google_fonts: ^6.x` 包(首次启动下载缓存)
- iOS / Android 字体首次启动加载延迟 ~500ms(可接受,有 splash screen)

---

## ADR-028: 仓库结构 — raw/ 进 git + _local/ 作 gitignored 工作区(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted(部分推翻 ADR-003 / ADR-004 中"raw/ 不进 git"的设定)

**决策**:
- `raw/` 目录改为**进 git**,存放外部采集的小型参考数据集(~78 MB 在限内)
- `raw/cbdb/` / `raw/chinese-poetry/` / `raw/wikidata-dump/` 等**大库子目录**仍单独 gitignore
- 新增概念 `_local/`(gitignored): 本地工作区,放 LLM 草稿 / 爬虫缓存 / 大文件
- 数据流向四层: `raw/ (外部)` → `data_source/ (校对)` → `assets/ (build)` → app

**理由**:
- 原 ADR 设"raw/ 不进 git"是为了防 CBDB 几百 MB 大库
- 实际 agent 采集的数据是结构化小文件(JSON/TSV/Wikipedia 摘录),~78 MB 完全在 GitHub repo 限内
- 数据进 git 有可追溯性 + reproducibility,他人 fork 也能跑通
- 大库通过 `raw/<source>/` 子目录 gitignore 单独控制,粒度更准
- agent 自动采集流程也需要"raw/ 是 git 一部分"才能 push 上来

**目录结构(本次确立)**:
```
/                              项目根
├── docs/ openspec/ tools/      ┐
├── personas/ data_source/      │  我们的开发(进 git)
├── assets/ lib/ pubspec.yaml   │
│
├── raw/                        ★ 外部采集数据(进 git,本次新政策)
│   ├── dynasties/              │
│   ├── geography/              │  agent / Scrapling 抓取产物
│   ├── images/                 │  含 AI 生成画像
│   ├── people/                 │
│   ├── wikipedia/              │
│   ├── cbdb/                   ✗ 大库子目录单独 gitignore
│   └── chinese-poetry/         ✗ 同上
│
└── _local/                     ✗ 本地工作区(gitignored)
    ├── llm-drafts/             ✗ LLM 起草中间产物
    ├── crawl-cache/            ✗ 爬虫下载原始(待 process)
    └── cbdb-cache/             ✗ CBDB 解压后大库
```

**替代**:
- 维持原 "raw/ 全 ignore": 数据无法进 git,agent push 不到远程,reproducibility 失
- 把 raw/ 改名 data-imports/: 改名工作量大,与 agent 现有路径冲突,推迟到稳定后再考虑

**后果**:
- `.gitignore` 修订: `raw/` 删,加 `_local/` + `raw/cbdb/` 等子目录
- 仓库体积: ~80 MB(GitHub 推荐 < 1 GB,完全 OK)
- CLAUDE.md 仓库结构段已更新
- 后续 agent 采集的新数据继续 push 到 raw/,Phase 1 ETL 工具读这里
- LLM 起草(`tools/seed_phase1.py`)输出到 `_local/llm-drafts/`,校对后才进 `data_source/`

**未决**: 是否改名 `raw/` → `data-imports/`(语义更准)?
推迟到 agent 采集流程稳定后再考虑(避免改名引入路径混乱)。

---

## ADR-029: 热更范围 — file-level 全量 + 砍 UX 复杂度(2026-05)

**日期**: 2026-05-09
**状态**: ✅ accepted(细化 ADR-018)

**决策**:
- 热更新粒度 = **file-level 全量替换**(events.json / dynasties.json / 等独立)
- 主数据 manifest 启动主动拉,有变化立刻下载
- 图片**单独 manifest + 懒加载**(展开朝代节点才下载该朝代图)
- 砍掉 UX 复杂度:
  - 不做更新 toast / 通知
  - 不区分蜂窝 vs WiFi
  - 不做积累提示("本周新增 N 条")
  - 用户感知 = 0(下次启动直接看到新数据)
- 错误处理 = `tools/validate.py` 严格 + git revert 作回滚
- Schema 迁移 = manifest 含 `_minAppVersion` 字段
- 测试机制 = 设置页"立即检查更新"按钮 + debug 模式拉取详情

**理由**:
- 用户核心需求是"我方便推数据",不是"用户感知到更新"
- 自用 + 朋友量 < 50,UX 投入 ROI 低
- file-level 全量 = 简单可靠,事件级 patch 复杂度太高
- 图片单独 manifest 因为 78 MB 不能每次启动全拉
- 砍 UX → Phase 1.5 实施量从"可能 1 周"降到"~2 天"

**替代**:
- 整个 raw/ 全量替换: 78 MB 每次更新,流量灾难
- 事件级 patch: 引入 diff/merge 复杂度,自用不值
- UX 全套(toast/积累提示/选项): Phase 1.5 工作量翻倍,边际价值低

**后果**:
- `docs/data-update-strategy.md` 新增 5 段 ★ 详细规范
- `assets/images/_manifest.json` 独立维护(图片 manifest)
- Flutter 端 RemoteDataSyncService 实现简化
- 设置页加"立即检查更新"按钮(Phase 1.5 唯一 UX 触点)
- 后续: 用户量真涨大(>100 朋友)再考虑增量更新 / WiFi 区分

---

## ADR-010: 用 OpenSpec 管理变更

**日期**: 2026-05-09
**状态**: ✅ accepted

**决策**: 使用 OpenSpec(`/opsx:propose` 流程)管理所有非琐碎的变更。

**理由**:
- AI 编程容易"chat 里聊一通就开始改",缺少结构化记录
- OpenSpec 把"提案 → 设计 → 任务 → 实施 → 归档"流程沉淀为 markdown 文件
  进 git
- 配合 Claude Code 直接出 spec,你只需 review

**替代**: 不用 OpenSpec → 设计决策容易随 chat 丢失,只剩 commit message。

**后果**:
- `.claude/` 和 `openspec/` 目录已 init
- 任何超过"加个按钮"规模的变更先走 `/opsx:propose`
- 琐碎修复(typo / 字体微调)不用走流程
