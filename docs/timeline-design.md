# 时间线模块设计 v2 — 树形朝代脉络图

> **重大重定位 (2026-05)**: 本模块从"纵向 ListView 时间线"重定向为
> **"git 风格树形朝代脉络图"**。这同时也合并了原"朝代脉络图"模块 — 时间线
> 和朝代图变成同一件事。
>
> 当前事实来源 = 本文件。`docs/ui-design.md` 早期内容**全部废弃**。

---

## 角色定位

打开 app 第一眼看到的就是**全朝代树形脉络图**:从树根(传说时代/上古)生长
到树梢(改革开放前)。整个中国史的形状一眼可见,这是 app 的差异化门面。

```
                  app 启动 → 默认进树形时间线
   ════════════════════════════════════════════════════

         ┌──────────────────────────────┐
         │   树形时间线(主入口)         │  ← 用户大部分时间在这里
         │   = 时间线 + 朝代图          │
         └──────────┬───────────────────┘
                    │ (点击朝代节点 / 事件 / 人物)
       ┌────────────┼────────────┬────────────┐
       ▼            ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │事件详情 │  │人物详情 │  │ 做题   │  │ 设置   │
   │(markdown)│ │(卡片)  │  │       │  │        │
   └────────┘  └────────┘  └────────┘  └────────┘
```

---

## 树形结构概念

### 隐喻: git 提交图

中国史天然适合 git 分支的隐喻:
- 三国并立 = 主干分裂为三条 branch,最终晋统一时 merge
- 南北朝 = 两条平行 branch
- 五代十国 = 短命多 branch
- 春秋战国诸侯并立 = 多 branch
- 王朝继承 = fast-forward commit
- 王朝末年农民起义 → 新王朝建立 = fork from "王朝末年" commit

```
                        现代 ↑(树梢)
                         │
                       (清)
                       ╱│
                  (太平天国 短分支)
                       │
                       ↑ (改革开放前 = Phase 1 终点)
                       │
                       │
                       ⋮
                       │
                       ●  晋统一 (merge commit)
                      ╱│╲
                   (魏)│(蜀)(吴)        ← 三国并立
                      ╲│╱
                       ●  东汉
                       │
                       ⋮
                       │
                       ●  秦统一 (merge commit)
                       │
                ╱╱╱╱─┼─╲╲╲╲             ← 战国七雄
                秦楚齐燕赵魏韩
                       │
                ╱╱╱──┼──╲╲╲              ← 春秋诸侯
                       │
                       ●  西周
                       │
                       ●  商
                       │
                       ●  夏
                       │
                  ╞═══════╡ (虚线区)        ← 传说时代:雾化
                  尧─舜─禹
                       ↓
                       根
```

### 方向: 从下到上(growing tree)

- 树根 = 传说时代(底部),树梢 = 现代(顶部)
- 用户**滚动方向**: 默认初始视图在中间(秦汉?),向下滚 = 看更早,向上滚 = 看更晚
- 这反直觉于"老在上、新在下",但符合"树生长"隐喻
- **TBD**: Phase 1 实施时观察是否反人类,大多数史实 app 仍是 top-down

### 节点层级

```
   层级 1: 朝代节点(主节点)
   ────────────────────────
   ●  夏 / 商 / 西周 / 秦 / 唐 / ...
   总计 ~25 个朝代节点

   层级 2: 政权节点(并立期)
   ────────────────────────
   ○  魏 / 蜀 / 吴(三国)
   ○  魏(北魏/东魏/西魏)/ 宋齐梁陈(南朝)
   ○  战国七雄 / 春秋诸侯
   作为朝代下属的"分支提交"

   层级 3: 事件 + 人物(展开后)
   ────────────────────────
   点击朝代/政权节点 → 抽屉式展开
     • 事件列表(年份 + 名称 + summary)
     • 人物列表(横向滚动 chip)
   再点击事件 → 详情页(markdown body)
   再点击人物 → 人物卡
```

---

## 数据契约(完整版)

时间线读 5 个 JSON 文件,加载策略 = **先 cache 后远程**(详见
`docs/data-update-strategy.md`):

```
   assets/data/                 # 内置(打包时)
   ├── manifest.json            # 各文件 hash + schema version
   ├── dynasties.json
   ├── regimes.json
   ├── events.json
   └── persons.json

   ApplicationDocumentsDir/data/  # 运行时 cache(热更产物)
   └── 同上 5 个文件,优先读取
```

**加载顺序**(`DataRepository`):
1. 检查 `ApplicationDocumentsDir/data/` 是否有 cache
2. 有 → 加载 cache
3. 无 → 加载 `assets/data/`(打包时内置版)
4. 后台异步拉 GitHub Raw 的 manifest,比较 hash → 有新就下载到 cache
5. 不打断当前会话,**下次启动**用新数据

### dynasty 字段

```json
{
  "id": "dynasty_western_zhou",
  "name": "西周",
  "altNames": [],
  "startYear": -1046,
  "endYear": -771,
  "color": "#A0826D",
  "summary": "...",
  "historicity": "historical",
  "_yearAuthority": "夏商周断代工程"
}
```

### regime 字段(关键: 含树拓扑)

```json
{
  "id": "regime_wei",
  "name": "曹魏",
  "dynastyId": "dynasty_three_kingdoms",
  "startYear": 220,
  "endYear": 265,
  "color": "#4B5D8C",

  "parentRegimeId": "regime_eastern_han",     // ← 从哪 fork
  "mergedIntoRegimeId": "regime_western_jin", // ← merge 到哪(可空)
  "siblingRegimeIds": ["regime_shu", "regime_wu"],  // ← 同期并立的兄弟

  "summary": "..."
}
```

`parentRegimeId` / `mergedIntoRegimeId` 是树渲染的拓扑信息。一个 regime 没
有 parent 时,接到 dynasty 主干上;有 parent 时,从该 regime 分叉出来。

### event 字段(schema v0.6)

```json
{
  "id": "event_wuwang_fa_zhou",
  "name": "武王伐纣",
  "year": -1046,
  "yearUncertainty": "year",
  "historicity": "historical",
  "dynastyId": "dynasty_western_zhou",
  "regimeIds": [],
  "category": "war",
  "tags": ["建国"],

  "summary": "周武王率诸侯联军于牧野击败商纣王,商朝灭亡,西周建立。(150-300 字)",

  "body": "## 起因\n商纣王...\n\n## 经过\n公元前 1046 年正月...\n\n## 后果\n...",

  "participants": [
    {"personId": "person_zhou_wuwang", "role": "主帅", "side": "周"},
    {"personId": "person_jiang_ziya",  "role": "军师", "side": "周"},
    {"personId": "person_shang_zhou",  "role": "君主", "side": "商"}
  ],

  "locationName": "牧野(今河南淇县)",
  "outcome": "商灭周立",
  "relatedEvents": ["event_zhougong_dongzheng"],
  "source": "manual"
}
```

**字数硬约束**:
- `summary`: 150 ~ 500 字
- `body`: 800 ~ 5000 字(markdown 全文,含标题字符)
- 超过 5K → `tools/validate.py` 报错并阻塞 build

### person 字段(Phase 1 简版,Phase 3 复活 persona)

```json
{
  "id": "person_zhou_wuwang",
  "name": "周武王",
  "altNames": ["姬发"],
  "dynasty": "western_zhou",
  "regimeIds": [],
  "birthYear": -1087,
  "deathYear": -1043,
  "yearUncertainty": "decade",
  "historicity": "historical",
  "role": "西周开国君主",
  "tags": ["王", "开国"],
  "summary": "(150-300 字现代汉语)",
  "events": ["event_wuwang_fa_zhou"],
  "source": "manual"
}
```

Phase 3 才恢复 `personality / selfReference / speechStyle / systemPrompt*`。

---

## UI 形态

### 主视图

```
   ┌──────────────────────────────────────┐
   │  ☰  中国史脉络        🔍  🌙  ⚙️       │  AppBar
   ├──────────────────────────────────────┤
   │                                      │
   │   ↑ 现代                             │
   │                                      │
   │   ●  清                              │
   │   │  (-1644 ~ -1912)                 │
   │   │                                  │
   │   ●  明                              │
   │   │                                  │
   │   ⋮                                  │
   │                                      │
   │       ●  魏  ●  蜀  ●  吴             │ ← 三国并立期
   │        ╲   │   ╱                     │
   │         ╲  │  ╱                      │
   │          ╲ │ ╱                       │
   │   ●  东汉                            │
   │   │                                  │
   │   ⋮                                  │
   │                                      │
   │ ╳╳╳ 传说时代 ╳╳╳                     │ ← 雾化区
   │   ╞┄┄┄┄ 尧 ┄┄┄┄┄ 舜 ┄┄┄┄┄ 禹 ┄┄┄┄╡  │
   │                                      │
   │   ↓ 远古                             │
   └──────────────────────────────────────┘
```

### 朝代节点展开(抽屉式)

```
   ┌──────────────────────────────────────┐
   │  ●  西周                             │
   │  │  -1046 ~ -771 (275 年)            │
   │  │                                   │
   │  ▼ 已展开                            │
   │  ┃                                   │
   │  ┃ 关键事件 (12)                     │
   │  ┃   • -1046  武王伐纣               │
   │  ┃   • -1043  周公东征               │
   │  ┃   • -841   国人暴动               │
   │  ┃   • ...                           │
   │  ┃                                   │
   │  ┃ 关键人物 (8)                      │
   │  ┃   ◯ 武王 ◯ 周公 ◯ 成王 ◯ 厉王    │ ← 横向滚动 chip
   │  ┃   ◯ 宣王 ◯ 幽王 ◯ 姜尚 ◯ 召公    │
   │  ┃                                   │
   │  ●                                   │
   └──────────────────────────────────────┘
```

### 事件详情页

```
   ┌──────────────────────────────────────┐
   │ ←                                    │
   │                                      │
   │  武王伐纣                             │
   │  (前 1046 年 · 牧野)                 │
   │  category: 战争 · 建国                │
   │                                      │
   │  ──────────────────────────────      │
   │                                      │
   │  ## 起因                              │
   │  商纣王无道...                        │
   │                                      │
   │  ## 经过                              │
   │  公元前 1046 年正月...                │
   │                                      │
   │  ## 后果                              │
   │  商朝灭亡,周武王建立周朝...           │
   │                                      │
   │  ──────────────────────────────      │
   │  参与者:                              │
   │   ◯ 周武王 (主帅)                     │
   │   ◯ 姜子牙 (军师)                     │
   │   ◯ 商纣王 (敌方)                     │
   │                                      │
   │  相关事件:                            │
   │   → 周公东征                          │
   └──────────────────────────────────────┘
```

---

## 传说时代视觉处理

```
   特征:
   • 背景沙色或浅灰
   • 卡片虚线边框(不是实线)
   • 字体: 楷书(信史用现代黑体作对比)
   • 年份带 "?" 标记 ("约 -2400?")
   • 节点间用 ┄┄ 虚线连接

   实现要点:
   • UI 通过 historicity == "legendary" 判断
   • dynasty.historicity = "legendary" → 该朝代下的所有事件默认雾化
   • 单个事件可独立标注 historicity("禅让"是 legendary)
```

---

## Phase 1 范围 (β)

### 全朝代骨架(都要建)

25 个朝代节点 + 树拓扑完整(三国分叉、南北朝并立、五代十国分支),但内容是
**占位级**(每朝代 5-10 个事件标题 + 5-10 个人物名字)。

### β 深耕(完整内容)

仅限 **尧舜禹 + 夏 + 商 + 西周** 4 个时段:
- 事件 40-70 件,每件**完整 body**(1-2K 字)
- 关键人物 ~20-30 人,每人 summary 完整
- 校对到位

### Phase 1 不做

- 缩放手势(Phase 2)
- 关系网图(Phase 2)
- 暗色模式色板(Phase 2,但暗色框架要在 v0 留口)
- 事件 category 配色(Phase 2)
- 人物详情页深度内容(Phase 3,只显示 summary)
- 横屏 / iPad / Web(Phase 4+)

---

## 实现技术(Flutter)

```
   树渲染层:
   ────────────────────────────────────
   • CustomPainter 自绘
   • 输入: 节点列表 + 拓扑边
   • 输出: 计算每个节点 (x, y) + 绘制连接线
   • Bezier 曲线 / 折线: TBD,Phase 1.4 实施时决定

   节点交互层:
   ────────────────────────────────────
   • Stack 在 CustomPainter 上叠 GestureDetector
   • 节点 = Positioned widget,位置由 painter 计算后传给 builder
   • 点击 → AnimatedContainer 抽屉式展开

   状态管理:
   ────────────────────────────────────
   • flutter_riverpod
   • TimelineState (展开的节点 id 集合)
   • DataRepository (一次加载所有 JSON 进内存)

   markdown 渲染:
   ────────────────────────────────────
   • flutter_markdown 包
   • 自定义样式(标题/正文字号/中文行间距)
```

---

## 布局算法草图(待 Phase 1.4 详化)

输入: 朝代列表 + 政权列表 + 树拓扑边

```
   Step 1: 沿"年份"作 y 轴
            年份越大 → y 越小(顶端 = 现代,底端 = 远古)
            按比例还是按节点等距,Phase 1.4 决定

   Step 2: 给每个节点分配 x(列号)
            主干 x = 0
            分叉时分裂(parentRegimeId 父节点 x = 0,
              子节点 x ∈ {-1, +1, -2, +2, ...} 按数量分配)
            合并时收回主干

   Step 3: 绘制连接线
            (parent.x, parent.y_end) ─→ (child.x, child.y_start)
            分叉/合并处用贝塞尔曲线避免直角

   Step 4: 处理特殊期
            春秋诸侯/战国七雄: 不全画 7 个并行,只画"主要 3-5 个"
              其余折叠为"+其余 X 国"小标签
            五代十国: 同上
            南北朝: 主干分左右两条
```

---

## UI Visual Design v0.6(2026-05 ui-ux-pro-max 产出)

### 设计语言: 水墨电子纸 (Ink-Paper)

```
   定位:   "现代极简" + "中国传统排版"的克制融合
            ── 不古风(避免装饰过度),不极简到失去文化感
            ── 像一本"用 iPhone 显示的高质量纸质历史书"
```

参考: ui-ux-pro-max 数据库的 **E-Ink / Paper** style + **Chinese Traditional**
typography pairing。详细见 ADR-027。

### 设计 token 总表

详见 `docs/design-tokens.md`(完整 light/dark 双套 token + 排版 + spacing)。

要点:
- 主背景: light = `#FDFBF7` (米白纸感) / dark = `#000000` (OLED 真黑)
- 文字: light = `#1A1A1A` (Ink Black) / dark = `#FAFAFA`
- 圆角: 主 6px,大 12px,卡片 4-6px(微圆,不过软)
- spacing: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 48
- 转场: 200ms ease-out,无 motion blur

### 字体配对

```
   标题:  Noto Serif SC (思源宋体)  — 翻书感 / 中国味
   正文:  Noto Sans SC  (思源黑体)  — 现代清晰 / 长读不累
   引用:  Noto Serif SC italic       — 史料块
   传说:  楷体 (Flutter 内置回退)    — 区分信史
```

通过 `google_fonts: ^6.x` 包加载 + 缓存。

### 25 朝代色板

详见 `docs/dynasty-palette.md`。设计原则:
- 全部走**矿物色 / 自然色**(传统中国画颜料)
- 相邻朝代色相隔 ≥ 30°
- 饱和度 25-45%(不抢戏)
- 每色含 light + dark 配对

### 树节点造型: 印章风 (Seal Stamp)

```
   主朝代节点(level 1)    政权节点(level 2)    传说节点
   ┌─────────────────────┐ ┌─────────────────┐ ┌──────────┐
   │ ╔═══════════╗       │ │ ╔═══════════╗   │ │ ┄┄ 尧 ┄┄ │
   │ ║   西周    ║       │ │ ║   曹魏    ║   │ │  灰阶虚线 │
   │ ║  -1046    ║       │ │ ║  220-265  ║   │ │  楷书     │
   │ ╚═══════════╝       │ │ ╚═══════════╝   │ │           │
   │  80 × 60 dp          │ │  60 × 45 dp     │ │  楷书 italic │
   │  双线边框(深+浅)    │ │  单线边框        │ │  浅灰 #888  │
   │  阴文白字            │ │  缩小版主节点    │ │  虚线 4 4   │
   └─────────────────────┘ └─────────────────┘ └──────────┘
```

### 事件卡片 + 详情页

事件卡片(树图朝代节点展开后,BottomSheet 内显示):
- 朝代色横条 4px(顶部,与树节点呼应)
- Noto Serif SC 16pt 事件名 + 14pt summary
- 边框 0.5px 朝代浅色 + 圆角 6px
- 点击 → push 详情页(Navigator,转场 280ms)

详情页(全屏 markdown body):
- 单栏布局,内容宽度 = SafeArea 内屏宽 - 32dp 左右 padding
- 段落间距 16pt,行高 1.7,行长目标 26-32 中文字符
- 引用块 楷体或宋体斜体
- 底部参与人物 chip + 相关事件链接

### 移动端实施细节(必须遵守)

**SafeArea**: 所有页面顶部/底部内容包在 SafeArea widget。AppBar 自动处理,但
自绘 CustomPainter 区域要主动 padding。

**触摸目标**: ≥ 48 dp(Material 标准)。树节点 60×45 / 80×60 已达标;chip 至
少 44×44。卡片间距 ≥ 12dp 防误点。

**按下态(无 hover)**: 所有可点击控件用 InkWell + Material ripple,或自定义
按下态(透明度 0.7,松开 200ms 回原)。

**触觉反馈**: 关键交互点用 `HapticFeedback`:
- 点击朝代节点 → `lightImpact`
- 跳转事件详情 → `selectionClick`
- 数据热更完成 → `mediumImpact`

**抽屉而不是 modal**: 朝代节点展开 → `showModalBottomSheet`(半屏 + 全屏两
档)。事件详情 → `Navigator.push`(整页 push,iOS/Android 平台默认转场)。
不用 `showDialog`。

**滚动 physics**: 用 Flutter 默认(`AlwaysScrollableScrollPhysics`),平台自
适应(iOS 弹性 / Android 硬停)。**别覆盖**。

**下拉刷新**: 主树图包 `RefreshIndicator`,下拉触发数据热更检查
(详见 `docs/data-update-strategy.md`)。

**屏幕方向**: Phase 1 锁竖屏(`SystemChrome.setPreferredOrientations`)。
Phase 2 再考虑横屏 + iPad。

**Dynamic Type**: 尊重系统字号设置,用 `MediaQuery.textScaleFactor` 缩放。
最大限制 1.3x(避免布局炸)。

**主题切换**: `MaterialApp` 设 `theme` + `darkTheme` + `themeMode:
ThemeMode.system`。设置页可强制 light / dark / system。

### 传说时代雾化(详细)

4 层叠加:
1. 背景渐变: 沙色 `#F0EBE0` → 主背景(透出年代久远感)
2. 节点本身: 灰阶 + opacity 0.6
3. 节点边框: 虚线(`dashed: [4, 4]`)
4. 文字: 楷书 + `#888` + italic

### 暗色模式策略

- 触发: 跟随系统(`MediaQuery.platformBrightness`)+ 设置页可强制
- light 模式 = 米白纸感(不是纯白,避免刺眼)
- dark 模式 = OLED 真黑(深夜阅读 + 续航)
- 朝代色 dark 变体: 饱和度 +15%,亮度 +20%
- 雾化区 dark = 深褐紫 `#2A1F1F`

详见 `docs/design-tokens.md`。

---

## 开放问题(Phase 1.4 实施时再决定)

- 滚动方向是真"从下到上"还是允许配置(可能引入"反转"开关)
- 春秋战国诸侯如何选"主要 3-5 个"(秦楚齐晋 vs 七雄全画)
- 详情页 hero 图加载占位(灰阶 placeholder?)
- 树图节点深度展开后的视觉层次(超过 2 层是否合并)
