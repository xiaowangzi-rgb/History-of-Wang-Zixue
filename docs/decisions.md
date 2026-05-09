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
