## Context

数据骨架完成(23 朝代 / 47 政权 / 139 事件 / 532 人物 / 294 KB)。本 change 把 Flutter 端从零启动,把数据画成 git 风格的从下到上的历史树。

约束:
- 用户已装 Flutter SDK + Android Studio,本机开发,真机/模拟器调试
- 设计 tokens / 树拓扑约束已在 `docs/design-tokens.md` / `docs/timeline-design.md` / `docs/dynasty-palette.md` 定稿
- schema v0.6 数据由 build.py 产物驱动,本 change 只读消费

## Goals / Non-Goals

**Goals:**
- 一个能在 Android 手机上跑起来的 Flutter app
- 完整渲染 23 朝代 + 47 政权,含三国 / 十六国 / 南北朝 / 五代十国 / 春秋战国并立分支
- 支持上下滚动浏览整条历史(下 = 远古,上 = 现代)
- 朝代节点 tap → 看到该朝代的事件列表(summary)+ 君主列表
- 事件 tap → 看到 markdown body(若有,无则 placeholder)
- Light / Dark 双主题
- 60fps 滚动 + 启动 < 500ms

**Non-Goals:**
- iOS 支持(后期)
- 热更新模块(下一个 change)
- 搜索 / 全局索引(Phase 2)
- 人物对话 / 做题(Phase 3+)
- 朝代 hero 图 / 君主 portrait 显示(图片资产未 ingest;占位色块即可)
- 事件 body 深耕内容(数据层负责,本 change 只渲染)

## Decisions

### D1. 数据加载策略 = 启动时全量 + 内存索引

**决策**:app 启动时一次性加载全部 4 个 JSON 到内存,构建 `Map<id, T>` 索引,不分页、不流式。

**理由**:总量 ~300 KB,Dart 解析 + 索引 < 100ms,单次启动成本极低。换来代码简单 + 任意跳转无延迟。

**替代**:lazy 按需加载、SQLite 缓存 — 都过度工程化,省下的内存(<10 MB)不值得复杂度。

### D2. 树布局算法 = 多列瀑布流 + 时间轴 y = -year

**决策**:y 轴 = `-year * pxPerYear`(年份越早,y 越小,显示越靠下),x 轴按"分支列"分配。主朝代占中间列(x=0),并立期 regime 按 siblingRegimeIds 数量平分两侧。北魏分裂为东西魏:东魏占左、西魏占右,各自向上延伸,在 mergedIntoRegimeId 处汇入下一代(北齐 / 北周)。

**理由**:跟 git log --graph 视觉同构;parentRegimeId / mergedIntoRegimeId 字段已经为这种布局准备。pxPerYear 用 0.4-1.0 之间,scrollable 范围约 4500 年 × 0.5 = 2250 px(可滚动)。

**替代**:Sankey 桑基图(美但不直观)、平铺时间轴(不能表达并立)、d3-tree 风格分形(信息密度低)。

### D3. 渲染 = CustomPainter,不用 SVG / WebView

**决策**:用 Flutter 原生 `CustomPainter` 画 Canvas,节点 / 连线 / 文字全部 Path + drawText。

**理由**:60fps 性能保证;无外部 webview 包袱;像素级精度可控;朝代色 / 印章风 / 雾化效果都用 Paint 直出。

**替代**:flutter_svg(插入 SVG 资源,缩放好但绘制慢);WebView 跑 d3.js(包大、启动慢、原生感差)。

### D4. 节点点击交互 = ModalBottomSheet 而非新页

**决策**:tap 朝代节点弹 ModalBottomSheet(顶部把手 + 该朝代 summary + 事件列表 + 君主列表 + 关闭手势)。tap 事件标题 → push 全屏 MarkdownView 路由。

**理由**:朝代 detail 信息密度中等(~10 事件 + ~10 君主),BottomSheet 50-70% 屏高足够,不打断浏览上下文。事件 body 才需要全屏阅读体验。

**替代**:全部用全屏页 — 增加返回键操作,丢失"我在哪条朝代"的视觉记忆。

### D5. 字体加载 = google_fonts package

**决策**:运行时 fetch Noto Serif SC + Noto Sans SC,本地缓存。不打包 ttf。

**理由**:Noto SC 全字符集 ttf 单个 ~10 MB,打包占空间。google_fonts 首次启动需联网下载一次,以后从 cache 走,体验可接受(自用,有网)。

**替代**:打包子集(运维麻烦);系统字体(各 ROM 不一致);打包完整 ttf(包变 30+ MB)。

### D6. 状态管理 = Provider + 简单 InheritedWidget

**决策**:启动加载 → AppDataStore(Provider) → 各页面 Consumer/Selector 取数据。不引入 Bloc / Riverpod / GetX。

**理由**:数据是只读、单源、不变的(直到下次启动重读)。Provider 一行解决,新人 onboarding 成本最低。

**替代**:Riverpod(强,但本项目用不到大半特性)、setState(够用但 prop drilling 烦)。

### D7. 雾化效果 = 灰阶填充 + ImageFilter.blur(radius=2-3)

**决策**:`historicity == "legendary"` 的朝代/事件/人物节点,用灰阶色板 + 高斯模糊 σ=2 + 透明度 0.7 渲染,文字依旧清晰但视觉退后。

**理由**:呼应"传说时代不应抢眼"的设计意图(`docs/timeline-design.md`);视觉系统统一,不用单独画法。

## Risks / Trade-offs

[**树布局算法可能在并立期太挤**] → 第一遍优先正确性,渲染出来再看视觉。若太挤,引入"展开/折叠政权列"交互(默认主朝代,长按展开 regime)

[**google_fonts 首次启动需联网**] → 自用 app 这个约束可接受;若朋友首次离线启动会回落到系统字体,功能不丢

[**Android Studio + Flutter 配置耗时不可控**] → 用户已装好 Android Studio,但 Flutter SDK 还需独立装。开干前先 `flutter doctor` 确认环境

[**CustomPainter 复杂度高,新手容易写出全重绘**] → 严格用 `RepaintBoundary` + `shouldRepaint` 控制;每帧只重绘可见 viewport(off-screen culling)

[**schema v0.6 在实际渲染中可能暴露不足**] → 跑出来若发现需要调整(例如新加 `displayPriority` 字段),回到 phase-1-data-source-spike change 修 schema + 重 build

## Migration Plan

不涉及生产环境迁移。本地开发流程:

1. 用户跑 `flutter doctor`,装 Flutter SDK + Android emulator(或连真机)
2. `flutter create .`(在项目根用现有目录初始化 Flutter 骨架)
3. 按 tasks.md 实现 → `flutter run`
4. 在真机上确认能跑后,本 change 完结归档

回滚策略:Flutter 是新增代码,无破坏性。任意时刻 git revert 即可。

## Open Questions

- **pxPerYear 取多少**?需要在真机上试 0.4 / 0.6 / 0.8 / 1.0,看哪个密度最舒服。Tasks 4.x 单独验。
- **朝代节点形状**:印章风(矩形 + 中文字)vs 圆角矩形?`docs/timeline-design.md` 说印章,先按这个做,出来不好看再调
- **暗黑模式触发**:跟系统(MediaQuery.platformBrightness)还是手动开关?Phase 1 跟系统,设置页 Phase 2 加切换
- **十国 / 辽 / 金 / 西夏未补全 regime**:数据层 4.2.5 还有 pending,届时若发现,临时把这些政权当作 dynasty_song / dynasty_five_dynasties_ten_kingdoms 子标签渲染(不画分支),等数据补上再升级布局
