# 王子学历史 — 项目记忆 (CLAUDE.md)

> 这是一份给 Claude Code 在每次新会话开机时自动加载的项目背景。**保持精简**,
> 详细设计在 `docs/`,变更提案走 OpenSpec(`/opsx:propose`)。

---

## 项目目标

Flutter 写的中国史学习 app,**自用为主**(给我自己 + 家人朋友用,暂不上架)。

四大核心模块(优先级从高到低):
1. **历史事件时间线**(纵向滚动 + 缩放,从通史到十年级)— **Phase 1 起点**
2. **朝代脉络图**(Swimlane / 多车道,正确呈现三国 / 南北朝 / 五代十国并立)
3. **历史人物卡 + 关键事件**(关系网、卡片浏览)
4. **做题模块**(SRS 间隔重复,围绕事件 / 人物 / 朝代)

加分项(非核心,Phase 后期):
- **人物对话**(LLM 扮演历史人物)— 原本作为核心特色,现降级为加分项。理由:
  对话价值天花板 = LLM 通用能力,差异化弱;离线可用性 = 0;依赖 API key 设置
  门槛高。app 真正的差异化在"策展品味 + 可视化结构"。

> ⚠️ 2026-05 重定位: 详见 `docs/decisions.md`(若已记录)。原计划"对话作为核
> 心,从孔子单人物跑通"的 Phase 1 已废弃,改为"时间线先行,先秦+春秋战国"。

---

## 架构(三层)

```
开发期(我的电脑)                      运行期(手机 app)
┌──────────────────────┐               ┌──────────────────────┐
│ tools/ Python 脚本    │               │ Flutter app          │
│  - ETL(多源融合)      │  build →      │  - 本地 SQLite       │
│  - LLM 富化           │  打包 assets   │  - OpenAI 兼容客户端  │
│  - 校对 / 验证        │               │  (中转 baseUrl)      │
└──────────────────────┘               └──────────────────────┘
        ↑                                       ↑
┌──────────────────────┐               ┌──────────────────────┐
│ raw/ (gitignore)     │               │ assets/data/         │
│  - CBDB SQLite       │               │  含**预生成的**       │
│  - chinese-poetry    │               │  systemPrompt 字段    │
│  - Wikidata cache    │               │  (运行期不拼装)       │
└──────────────────────┘               └──────────────────────┘
```

详细见 `docs/architecture.md` 和 `docs/data-pipeline.md`。

---

## 关键约束(请严格遵守)

1. **仓库 Public 开源** → API key 绝不进 git,`raw/` 不进 git
2. **双协议**: 代码 MIT(根 LICENSE),数据 CC-BY-SA-4.0(`data_source/LICENSE`)
3. **LLM 产物未人工校对不得进 `data_source/`** — 这是质量底线,严守
4. **system prompt 预生成**: 开发期 build 脚本一次性生成 prompt 文本,写回
   JSON 字段,运行期**只字符串拼接 user message**,不再做模板渲染
5. **CBDB 原数据不直接分发** — 提取所需字段后写到 `data_source/persons/*.json`,
   原始 SQLite 留在本机 `raw/`
6. **每个朝代独立 JSON 文件**(`persons/qin.json`、`persons/han.json`),不做单
   文件 monolith,git diff 才有意义

---

## 数据来源(详见 `docs/data-sources.md` 和 `docs/data-source-survey.md`)

> ⚠️ 2026-05 重定位: 数据策略从"LLM 富化为主 + CBDB"改为
> "**优先用现成 GitHub 数据集 + 适配 schema + 人工校对**"。
> LLM 退居"补缺草稿 / 现代汉语转译"角色。

| 来源 | 角色 | 协议 | 覆盖 |
|---|---|---|---|
| 现成 GitHub 数据集 | **事件/朝代主力** | 因仓库而异 ⚠️ | 待调研验证 |
| CBDB | 人物补充(后期) | 学术开放,需署名 | 7-19 世纪(唐-清强)|
| chinese-poetry | 文学家 + 诗词 | MIT | 唐宋为主 |
| Wikidata / Wikipedia | 先秦/秦汉/魏晋补充 | CC-BY-SA | 全时段 |
| LLM 生成 | 草稿 / 文言转译(降级使用) | — | 必须校对 |

---

## LLM 双轨制

- **主力(批量,~80%)**: DeepSeek-V3,`base_url=https://api.deepseek.com/v1`
  - 中文古文质量好,价格 1/10 - 1/20 GPT-4o
- **精修(困难校对,~20%)**: Claude Sonnet 4.6 / GPT-4o
  - 多角色一致性 review、prompt 模板优化

ETL 脚本支持 `--model` 参数,环节级别选择模型。

**API key 通过环境变量传入**:`DEEPSEEK_API_KEY`、`ANTHROPIC_API_KEY` 等,
**不接受**配置文件方式,**不接受**硬编码。

---

## 工作流

- **变更管理**: OpenSpec 已 init,使用 `/opsx:propose <想做的事>` 提议变更
- **设计文档**: `docs/` 下分模块组织,**改动设计先改文档,再改代码**
- **提交规范**: 中文 commit message ok,类型前缀建议 `feat:` / `fix:` /
  `chore:` / `docs:`

---

## 当前阶段

- ✅ **Phase 0**: 项目骨架 + 文档种入
- ✅ **Phase 0.5**(2026-05): 重定位 — 核心从"对话"改为"时间线/朝代/人物/事件"
- → **Phase 1 起点**: **时间线先行,先秦 + 春秋战国**
  - 1.0 doc 重定位(本次完成)
  - 1.1 数据源 spike: 调研现成 git 仓库,产出 `data-source-survey.md`
  - 1.2 schema 简化 v0.5(砍 persona 字段,只留 event/dynasty/regime)
  - 1.3 数据起点: 从仓库 import 30-50 条先秦+春秋战国事件 + 朝代/政权
  - 1.4 Flutter 项目骨架 + 时间线页(纵向滚动)
  - 1.5 在你自己手机上能滚的版本

  **范围理由**: 起点限定先秦 + 春秋战国(到秦统一止)。事件量 30-50 条够先把
  时间线 UI 跑通,不需要全朝代铺开。诸子百家的人物 / 对话留到后期。

---

## 仓库结构

```
.
├── CLAUDE.md                    # 这个文件
├── README.md                    # 公开仓库门面
├── LICENSE                      # 代码 MIT
├── .gitignore
├── .claude/                     # OpenSpec 写入的 commands + skills
├── openspec/
│   ├── specs/                   # 由 /opsx:propose 流程产出
│   └── changes/                 # 同上
├── docs/                        # 详细设计文档(进 git)
├── data_source/                 # 校对后的源数据(进 git)
│   └── LICENSE                  # 数据 CC-BY-SA-4.0
├── tools/                       # 开发期 Python 脚本(占位)
├── personas/                    # prompt 模板(占位)
├── assets/                      # Flutter 资产
│   └── data/                    # build 产物(进 git)
└── raw/                         # gitignore!原始第三方数据
```

---

## 详细文档索引

| 文档 | 内容 |
|---|---|
| `docs/architecture.md` | 三层架构详细说明 |
| `docs/data-sources.md` | 数据源调研结论 + 各源详情 |
| `docs/data-schema.md` | person/event/dynasty/regime 字段定义(草案) |
| `docs/persona-design.md` | LLM 扮演历史人物的设计(⚠️ 已降级,Phase 后期) |
| `docs/ui-design.md` | 时间线 / 朝代图 / 卡片 / 对话 UI 设计 |
| `docs/timeline-design.md` | 时间线模块详细设计(Phase 1 主战场) |
| `docs/data-source-survey.md` | 现成 GitHub 数据集调研 |
| `docs/data-pipeline.md` | 多源 ETL 流程 |
| `docs/roadmap.md` | 阶段 0-4 路线图 |
| `docs/decisions.md` | 关键决策记录(ADR 风格) |

---

## 给 Claude Code 的提示

- 写代码前先看 `docs/` 中相关设计文档
- 涉及多文件改动或新功能,**优先**用 `/opsx:propose` 启动变更流程
- 遇到数据 schema 不确定 → `docs/data-schema.md` 是当前事实来源
- 遇到时间线 / Phase 1 不确定 → `docs/timeline-design.md` 是当前事实来源
- 遇到 prompt 设计不确定 → `docs/persona-design.md`(注意:已降级,Phase 后期)
- **永远不要**在任何文件里写明文 API key,即使是占位示例
