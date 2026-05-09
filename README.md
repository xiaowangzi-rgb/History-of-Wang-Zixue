# 王子学历史 / Wang Zixue's History App

> 一个把中国史从「线性教科书」变成「可触摸、可对话、可记忆」的手机 app。
>
> A mobile app that turns Chinese history from a linear textbook into something
> you can touch, talk to, and actually remember.

**状态**: 🌱 alpha / pre-development(规划阶段,尚未发布)

---

## 这是什么

一款 Flutter 写的中国史学习 app(自用为主),四大模块:

- **📅 历史事件时间线** — 纵向滚动 + 多级缩放,从通史到十年级
- **🌳 朝代脉络图** — 多车道 / Swimlane 渲染,正确呈现三国 / 南北朝 / 五代
  十国等并立时期
- **🎴 历史人物卡 + 做题** — 人物卡片 + 间隔重复(SRS)做题
- **💬 与历史人物对话** ⭐ — 点击任一历史人物,LLM 基于该人物生平、性格、
  知识边界扮演对话。支持「严肃模式」(基于正史)和「演义模式」(允许民间形象)

---

## 技术栈

- **App**: Flutter(跨端 Android + iOS)
- **数据**: 本地 SQLite + JSON 资源 + 预生成 system prompt
- **LLM**: OpenAI 兼容 baseUrl(用户填中转或官方 API key)
  - 推荐主力: DeepSeek-V3
  - 推荐精修: Claude Sonnet / GPT-4o

---

## 数据来源 / 致谢

本项目数据为多源 ETL 产物,以下上游来源不可或缺,谨致谢意:

| 上游 | 主页 | 协议 | 用途 |
|---|---|---|---|
| **CBDB** (China Biographical Database) | [cbdb.hsites.harvard.edu](https://cbdb.hsites.harvard.edu/) | 学术开放 | 7-19 世纪人物数据(主体) |
| **chinese-poetry** | [github.com/chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) | MIT | 唐宋诗人 + 作品 |
| **Wikipedia / Wikidata** | [wikipedia.org](https://www.wikipedia.org/) / [wikidata.org](https://www.wikidata.org/) | CC BY-SA | 先秦 / 秦汉 / 通用补充 |

CBDB 数据维护方为哈佛大学、北京大学、中央研究院,本仓库不直接分发 CBDB 原数据
库,仅分发提取与转换后的精简字段。

事件描述与人物人设字段中,部分草稿由大语言模型生成,**全部经人工校对**后方进入
本仓库。

---

## 协议

本仓库采用**双协议**:

- **代码部分**(Flutter app 源码、`tools/` 下 Python 脚本、配置文件等)— MIT,
  详见 [LICENSE](LICENSE)
- **数据部分**(`data_source/` 目录下所有 JSON 内容)— CC BY-SA 4.0,详见
  [data_source/LICENSE](data_source/LICENSE)

如果你基于本仓库的**数据**做衍生作品,需:
1. 署名本仓库 + 上游来源(CBDB / chinese-poetry / Wikipedia)
2. 以同等协议(CC BY-SA 4.0)分发你的衍生数据

---

## 仓库结构

```
.
├── CLAUDE.md                # 项目记忆(给 Claude Code 用)
├── README.md                # 你正在看的文件
├── LICENSE                  # 代码 MIT
├── docs/                    # 详细设计文档
├── data_source/             # 校对后的源数据(进 git)
│   └── LICENSE              # 数据 CC BY-SA 4.0
├── tools/                   # 开发期 Python 脚本
├── personas/                # LLM prompt 模板
├── assets/data/             # build 产物
└── (Flutter 项目根)         # 待 flutter create 后生成
```

---

## 设计文档

详细设计在 [`docs/`](docs/):

- [architecture.md](docs/architecture.md) — 整体架构(三层)
- [data-sources.md](docs/data-sources.md) — 数据源调研
- [data-schema.md](docs/data-schema.md) — 数据 schema 草案
- [persona-design.md](docs/persona-design.md) — LLM 扮演设计
- [ui-design.md](docs/ui-design.md) — UI 设计要点
- [data-pipeline.md](docs/data-pipeline.md) — ETL 流程
- [roadmap.md](docs/roadmap.md) — 阶段路线
- [decisions.md](docs/decisions.md) — 关键决策记录

---

## 开发

🚧 阶段 0 完成,Flutter 项目骨架尚未初始化。

阶段 1 起点: **春秋战国诸子百家**(孔子作为首个完整人物试点)。

变更管理使用 [OpenSpec](https://github.com/Fission-AI/OpenSpec):
```
/opsx:propose <想做的功能>
```

---

## 反馈

仓库: https://github.com/xiaowangzi-rgb/History-of-Wang-Zixue
