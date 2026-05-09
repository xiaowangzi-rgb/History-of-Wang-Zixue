## 1. 准备

- [x] 1.1 确认 `.gitignore` 含 `_local/` + `raw/cbdb/` 等大库 (ADR-028,raw/ 已**进 git**)
- [x] 1.2 安装 Python 依赖: `pip install jsonschema Pillow` 已装 (scrapling/requests 用到再装)
- [ ] 1.3 准备 `DEEPSEEK_API_KEY` 环境变量(β 深耕 LLM 起草用)
- [x] 1.4 schema 已升 v0.6 ✓ (`docs/data-schema.md`)
- [x] 1.5 创建 `_local/llm-drafts/` 和 `_local/crawl-cache/` 目录(gitignored 工作区)

## 2. 数据源 review(agent 已提供 raw/,本节大部分已经做完)

> 2026-05 更新: agent 已经把 5 个源的数据 push 到 `raw/`(commit be6937e),
> 本节从"调研 + clone"变为"review 现有数据 + 决定怎么用"。

- [x] 2.1 review `raw/dynasties/` 内容
      - dynasties-wxh06.json: 朝代 + 政权完整清单(从西周到现代)
      - history-rtkarcher.json: 英文 timeline 风格事件
      - grand-timeline-era.tsv: 年号表
      - emperors-timeline-wanxb.js: 7259 行 JS 数据
- [x] 2.2 review `raw/images/`
      - emperor-portraits.json: 70 张 Wikimedia 帝王画像 URL
      - people-portraits/index.json: 532 位君主完整索引(含 reign 年份)
      - people-portraits/_batch_list.json: 25 位 AI 生成画像参数
      - 25 张 PNG 已在 `raw/images/people-portraits/<朝代>/<君主>/*.png`
- [x] 2.3 review `raw/wikipedia/` 4 篇英文 wiki 摘录(可作 LLM 起草素材库)
- [x] 2.4 review `raw/people/` (注: grand-timeline-TC2SC 是繁简字典,毛轨迹超 Phase 1 scope)
- [x] 2.5 review `raw/geography/` (Phase 1 暂用 location-history 作 locationName 标注)
- [x] 2.6 在 `docs/data-source-survey.md` 底部新增"实地验证结论"段,记录每个源的: 用法、覆盖度、是否选用
- [x] 2.7 写 ADR-030(选定数据源 + 拒用源原因)入 `docs/decisions.md`(注: 编号改为 ADR-030,ADR-027 已被设计语言占用)

## 3. JSON Schema 工件

- [x] 3.1 写 `tools/schema/dynasty.schema.json`(含 `_yearAuthority` 字段)
- [x] 3.2 写 `tools/schema/regime.schema.json`(含 `parentRegimeId` /
      `mergedIntoRegimeId` / `siblingRegimeIds`)
- [x] 3.3 写 `tools/schema/event.schema.json`(含 `body` 字段、字数限制)
- [x] 3.4 写 `tools/schema/person.schema.json`(简化版,无 persona 字段)
- [x] 3.5 写 `tools/schema/__init__.py` 聚合入口

## 4. 全 25 朝代骨架数据

> **起点**: `raw/dynasties/dynasties-wxh06.json` 已含从西周到现代的完整
> 朝代 + 政权清单(JSON 数组,带月日精度)。本节主要工作是 import + 校对 +
> 加 v0.6 字段(树拓扑 / 颜色 / hero 图)。

### 4.1 朝代列表

- [x] 4.1.1 写 `tools/import_dynasties_wxh.py`,从 `raw/dynasties/dynasties-wxh06.json`
      抽取顶层朝代(夏 / 商 / 西周 / 东周 / 秦 / 西汉 / 东汉 / 三国 / 西晋 / ...)
- [x] 4.1.2 补充传说时代条目: `dynasty_legendary`(historicity=legendary,
      yearUncertainty=era,雾化处理)
- [x] 4.1.3 补充 1949-1978 条目: `dynasty_prc_pre_reform`
- [x] 4.1.4 每个朝代加 v0.6 字段: color / colorDark (从 `docs/dynasty-palette.md`) /
      historicity / `_yearAuthority` ("夏商周断代工程")
- [x] 4.1.5 输出到 `data_source/dynasties.json`(实际 23 条 — 与 dynasty-palette.md 一致;
      docs 标题写 "25" 但表格只有 23 行,Sprint 2 尾段建议改 docs 标题)

### 4.2 政权(regime)与树拓扑

- [x] 4.2.1 从 `raw/dynasties/dynasties-wxh06.json` 抽取并立期: 十六国 16 条 /
      南北朝(南朝 4 + 北朝 5)/ 三国 3 / 五代 5 / 战国七雄(手填)
- [x] 4.2.2 春秋诸侯主要 7 国手填(鲁/齐/晋/楚/秦/宋/吴)
- [x] 4.2.3 每个 regime 加 v0.6 字段: color / colorDark (从 dynasty-palette.md) /
      `parentRegimeId` / `mergedIntoRegimeId` / `siblingRegimeIds`
- [x] 4.2.4 双向一致性: validate.py R5 自动校验通过
- [x] 4.2.5 输出到 `data_source/regimes.json`(47 条)
      pending: 五代十国的"十国"和辽/西夏/金 留 Sprint 3 / 后续 manual 补

### 4.3 各朝代占位事件 + 人物(非 β 时段)

- [x] 4.3.1 19 个非 β 时段每个 4-10 个事件标题 (139 条手工写入,只 summary 不写 body)
      → 文件: legendary, qin, western_han, xin, eastern_han, three_kingdoms,
        western_jin, eastern_jin, sixteen_kingdoms, southern_northern, sui,
        tang, five_dynasties, song, yuan, ming, qing, republic, prc_pre_reform
- [x] 4.3.2 全 21 个朝代共 **532 个君主人物**从 `raw/images/people-portraits/index.json` import
      → `tools/import_persons_index.py [--include-beta]` 自动映射 dynasty 名 → dynasty_id (+regime_id)
      → β 朝代 (xia 19 / shang 30 / western_zhou 14 / eastern_zhou 108) Sprint 4-lite 已 import
      → β 朝代人物的 body / portrait 留 Sprint 4 真正 curate 时填
      → 诸子百家 / 重臣 (诸葛亮 / 李白 等)Sprint 4 手工补
- [x] 4.3.3 占位文件 _schemaVersion + 顶层结构正确 (validate.py 全 pass)

### 4.4 朝代 hero 图(从 raw/ 引用)

- [ ] 4.4.1 25 朝代 hero 图: 优先从 `raw/images/people-portraits/<朝代>/<开国君主>/`
      引用,例如:
      - dynasty_qin → 秦始皇.png
      - dynasty_ming → 朱元璋.png
      - dynasty_qing → 皇太极.png
- [ ] 4.4.2 没现成画像的朝代(夏/商/西周/春秋战国)用 dynasty.color 色块占位
- [ ] 4.4.3 在 dynasties.json 填 heroImage / heroImageSource / heroImageLicense

## 5. β 深耕(尧舜禹 / 夏 / 商 / 西周)

> 这是 Phase 1 的"创造性工作量",约 1-2 个月业余时间。

### 5.1 尧舜禹(雾化骨架,**不深耕**)

- [ ] 5.1.1 录入 5-10 个传说事件占位(name + year approx),historicity = legendary
- [ ] 5.1.2 录入 5-10 个传说人物占位(name + role)
- [ ] 5.1.3 不写 body / portrait,UI 雾化呈现

### 5.2 夏(深耕)

- [ ] 5.2.1 列出 15-25 件关键事件: 大禹治水(historical 视角)/ 启杀伯益 /
      太康失国 / 少康中兴 / 夏桀亡 / ...
- [ ] 5.2.2 列出 8-12 个关键人物: 启 / 少康 / 桀 / 伊尹(夏末)/ ...
- [ ] 5.2.3 LLM 双 pass 起草 (summary A 风格 + body C 风格)
- [ ] 5.2.4 人工校对 → `data_source/events/xia.json`(部分 historicity = "semi-historical")

### 5.3 商(深耕)

- [ ] 5.3.1 列出 20-30 件关键事件: 商汤灭夏 / 盘庚迁殷 / 武丁中兴 / 妇好祭祀 /
      纣王亡 / ...
- [ ] 5.3.2 列出 10-15 个关键人物: 商汤 / 伊尹 / 盘庚 / 武丁 / 妇好 / 纣王 / ...
- [ ] 5.3.3 LLM 双 pass 起草 → 校对 → `data_source/events/shang.json`

### 5.4 西周(深耕)

- [ ] 5.4.1 列出 20-30 件关键事件: 武王伐纣 / 周公东征 / 成康之治 / 国人暴动 /
      宣王中兴 / 平王东迁 / ...
- [ ] 5.4.2 列出 10-15 个关键人物: 文王 / 武王 / 周公 / 姜尚 / 召公 / 厉王 /
      宣王 / 幽王 / ...
- [ ] 5.4.3 LLM 双 pass 起草 → 校对 → `data_source/events/western_zhou.json`

### 5.5 东周春秋(深耕)

- [ ] 5.5.1 列出 25-40 件关键事件: 平王东迁 / 春秋五霸(齐桓晋文宋襄秦穆楚庄)/
      孔子周游 / 老子出关 / 子产改革 / 弭兵之会 / ...
- [ ] 5.5.2 列出 15-20 个关键人物: 周平王 / 齐桓公 / 管仲 / 晋文公 / 楚庄王 /
      孔子 / 老子 / 孙武 / 子产 / ...
- [ ] 5.5.3 LLM 双 pass 起草 → 校对 → `data_source/events/eastern_zhou_spring_autumn.json`

### 5.6 东周战国(深耕)

- [ ] 5.6.1 列出 25-40 件关键事件: 三家分晋 / 田氏代齐 / 商鞅变法 / 围魏救赵 /
      合纵连横 / 田单复国 / 秦灭六国 / 长平之战 / 屈原投江 / 荆轲刺秦 / ...
- [ ] 5.6.2 列出 15-20 个关键人物: 商鞅 / 苏秦 / 张仪 / 孟子 / 庄子 / 荀子 /
      韩非子 / 屈原 / 白起 / 廉颇 / 李斯 / 嬴政 / ...
- [ ] 5.6.3 LLM 双 pass 起草 → 校对 → `data_source/events/eastern_zhou_warring_states.json`

### 5.7 β 深耕字数 + 比例检查

- [ ] 5.7.1 跑 `tools/validate.py` 字数检查(summary 150-500, body 800-5000)
- [ ] 5.7.2 跑内容比例检查(政治军事合计 ≤ 40%,文化+科技+人物 ≥ 50%)
- [ ] 5.7.3 修订 < 800 字的(扩写)和 > 5000 字的(拆分事件)

## 6. 校验工具

- [x] 6.1 写 `tools/validate.py`(载入 schema + 跑自定义规则)
- [x] 6.2 实现规则: ID 唯一、跨实体引用存在
- [x] 6.3 实现规则: `_schemaVersion` 检查
- [x] 6.4 实现规则: 字数硬约束(summary / body)
- [x] 6.5 实现规则: 树拓扑双向一致性 + 闭环检测
- [x] 6.6 实现规则: β 深耕时段事件必须含 body
- [x] 6.7 实现规则: `source: "llm-draft"` 不允许在 `data_source/`
- [x] 6.8 实现规则: event.year 落在 dynasty 范围(soft warning)
- [x] 6.9 跑 `python tools/validate.py`,空 data_source/ pass(0 errors / 0 warnings)
- [ ] 6.10 故意破坏数据测各条规则能 catch(等 Sprint 2 有数据后再做)

## 7. import + merge 工具(若用)

- [ ] 7.1 写 `tools/import_hellohistory.py`(若 ADR-018 选用)
- [ ] 7.2 写 `tools/import_wikidata.py`(SPARQL 拉人物)
- [ ] 7.3 写 `tools/import_wiki_zh.py`(维基百科年表抓取,若用)
- [ ] 7.4 写 `tools/merge_dynasties.py`(多源朝代年份冲突解决)
- [ ] 7.5 写 `tools/merge_events.py`(事件去重 + 命名归一)

## 8. β 深耕辅助工具

- [ ] 8.1 写 `tools/seed_phase1.py`(读取 YAML 输入 → JSON 输出 + LLM 起草调用)
- [ ] 8.2 实现 LLM 起草调用(DeepSeek-V3,环境变量 key)
- [ ] 8.3 实现"草稿落 staged + source: llm-draft"
- [ ] 8.4 实现"校对后导出到 data_source + source 改为 llm-reviewed"

## 8.5 图片处理(Phase 1 — agent 已提供大部分)

> 2026-05 更新: agent 已 push 25 张 AI 生成 PNG + 70 张 Wikimedia 帝王画像
> URL + 532 君主索引。本节主要是**处理 + 关联**,而非"爬取"。
> 缺失的图(春秋战国诸子百家)走 Scrapling 爬。

- [x] 8.5.1 写 `tools/process_images.py`(Pillow 压缩到 800x600 WebP + 缩略图)
- [ ] 8.5.2 处理 raw/images/people-portraits/*.png (25 张) → data_source/images/persons/*.webp
- [ ] 8.5.3 emperor-portraits.json 70 张 Wikimedia URL: 写 `tools/download_wikimedia_images.py`
      下载到 `_local/crawl-cache/` → process → data_source/images/persons/
- [ ] 8.5.4 春秋战国关键人物画像缺失部分: 写 `tools/crawl_images.py`(Scrapling)
      限定 commons.wikimedia.org 域,人工 review (~2-3 小时筛选)
- [x] 8.5.5 写 `tools/build_image_manifest.py`(SHA-256 hash + size)
      生成 `assets/images/_manifest.json`(独立于主数据 manifest)
- [ ] 8.5.6 在 dynasty / person JSON 中填入 heroImage / portrait + source + license 字段
- [ ] 8.5.7 验证图片总体积(预计 30-50 MB,β 时段为主)

## 9. build 工具

- [x] 9.1 写 `tools/build.py`(读 `data_source/` → 合并/复制 → `assets/data/`)
- [x] 9.2 实现 build 前调 validate,失败则 abort
- [x] 9.3 events 按 year 升序合并到 `assets/data/events.json`
- [x] 9.4 主数据 manifest: 直接在 `tools/build.py` 内写 `assets/data/manifest.json`
      (含 `_schemaVersion: "v0.6"` / `_minAppVersion: "1.0.0"` / per-file SHA-256 + size,ADR-029)
- [x] 9.5 图片 manifest: 由 8.5.5 生成的 `assets/images/_manifest.json` 独立管理
- [x] 9.6 跑 `python tools/build.py`,空 data_source/ 流程通过,manifest 写入成功
- [ ] 9.7 验证文件总大小(等 Sprint 2/3 数据 import 完再 check)

## 10. 文档收尾

- [ ] 10.1 在 `docs/data-source-survey.md` 底部"实地验证结论"段补全
- [ ] 10.2 在 `docs/decisions.md` 写 ADR-018(选定的数据源)
- [x] 10.3 在 `tools/README.md` 简短记录脚本用法
- [ ] 10.4 更新 `docs/data-pipeline.md`(若需)反映多源策略

## 11. 提交 + 归档

- [ ] 11.1 跑 `tools/validate.py` 最终全 pass
- [ ] 11.2 跑 `tools/build.py` 产出 `assets/data/*.json`
- [ ] 11.3 git add → commit
- [ ] 11.4 跑 `openspec validate phase-1-data-source-spike` 通过
- [ ] 11.5 准备 archive: `/opsx:archive phase-1-data-source-spike` 关闭本次 change

## 12. 接力下一个 change

- [ ] 12.1 启动 `/opsx:propose phase-1-tree-renderer`(Flutter 树图实现)
- [ ] 12.2 在新 change proposal 中引用本 change 产出的 `assets/data/`
