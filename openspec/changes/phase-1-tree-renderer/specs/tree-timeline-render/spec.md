## ADDED Requirements

### Requirement: 树形时间线布局算法

系统 SHALL 提供 `TreeLayoutEngine`,输入 dynasty + regime 列表,输出每个节点的屏幕坐标 (x, y) 和连线 path,支持并立期分支。

#### Scenario: 单一线性朝代
- **WHEN** 输入 5 个连续无并立的朝代(秦 → 西汉 → 新莽 → 东汉 → 三国 envelope)
- **THEN** 输出每个朝代节点 x = 0,y = -startYear * pxPerYear
- **AND** 相邻朝代用直线连接

#### Scenario: 三国并立
- **WHEN** 输入 dynasty_three_kingdoms + regime_wei / regime_shu / regime_wu
- **THEN** 主朝代节点 x = 0,三个 regime 按 siblingRegimeIds 顺序在 x = -120 / 0 / +120 三列展开
- **AND** 三 regime 在 y 轴跨 220-280 范围(各自 startYear / endYear)
- **AND** 280 年三 regime 汇合到 dynasty_western_jin

#### Scenario: 北朝分裂合并
- **WHEN** regime_northern_wei (386-534) 后裂为 regime_eastern_wei + regime_western_wei,各自 mergedIntoRegimeId 指向 regime_northern_qi / regime_northern_zhou
- **THEN** 北魏节点上方分两支,东魏左 / 西魏右
- **AND** 东魏支线 550 年汇入北齐,西魏支线 557 年汇入北周(用 mergedIntoRegimeId 字段驱动)

#### Scenario: 雾化时段渲染
- **WHEN** 节点的 dynasty 或 regime 的 `historicity` 不等于 "historical"
- **THEN** 该节点用灰阶填充 + 高斯模糊 σ=2 + 透明度 0.7 渲染
- **AND** 文字依旧清晰可读

### Requirement: 朝代节点视觉样式

系统 SHALL 把每个 dynasty 渲染为印章风格的矩形节点:朝代色背景、白色 / 朝代色相反色文字、圆角半径 4-8 px。

#### Scenario: 朝代节点显示朝代名
- **WHEN** 渲染 dynasty_tang
- **THEN** 节点矩形填充 #C84E4E (light) 或 #E07070 (dark)
- **AND** 居中显示"唐"字 + 下方小字 "618-907"
- **AND** 矩形宽高约 80 × 40 px

#### Scenario: 政权节点显示政权名
- **WHEN** 渲染 regime_wei (曹魏)
- **THEN** 节点矩形填充 #5C6F94,白色字"曹魏"
- **AND** 政权节点比朝代节点小一号(60 × 32 px)

### Requirement: 年份轴 + 朝代色背景带

系统 SHALL 在 Canvas 左侧画年份刻度(每 100 年一格),在每个 dynasty 区段画半透明的朝代色背景带,帮助视觉识别"现在在哪个朝代"。

#### Scenario: 年份刻度
- **WHEN** Canvas 渲染
- **THEN** 左侧 24 px 宽的年份轴,每 100 年画一条横线 + 数字标签
- **AND** 公元前年份用 "前 XXX" 或 "BC XXX" 显示

#### Scenario: 朝代色背景带
- **WHEN** Canvas 渲染
- **THEN** 每个 dynasty 的 [startYear, endYear] 区段画水平延伸到屏幕宽度的半透明色带 (alpha 0.1-0.15)
- **AND** 色带颜色 = dynasty.color / colorDark

### Requirement: 节点点击 → BottomSheet

系统 SHALL 响应朝代 / 政权节点的 tap 手势,弹出 ModalBottomSheet 显示该实体的详情。

#### Scenario: 点击朝代节点
- **WHEN** 用户 tap dynasty_tang 节点
- **THEN** 弹出 BottomSheet(占屏 50-70%),内容包含:
  - 顶部:朝代名 + 起讫年份 + summary 文本
  - 中部:该朝代的事件列表(按 year 升序),每条显示 name + year + 短 summary
  - 底部:该朝代的君主列表(按 birthYear 升序),每条显示 name + reign 范围
- **AND** 顶部有把手(grabber bar),下拉手势可关闭

#### Scenario: 点击事件 → 全屏 markdown 详情
- **WHEN** 用户在 BottomSheet 点击某事件标题
- **THEN** push 全屏路由 `/event/:id`
- **AND** 显示事件名 + year + summary + body(若有 body 字段则用 flutter_markdown 渲染)
- **AND** 若 body 字段为空,显示 "本事件暂无详细叙述,Phase 1 后期补全" placeholder

### Requirement: 滚动与性能

系统 SHALL 支持上下滚动浏览整棵历史树,在 mid-range Android 真机上保持 60fps。

#### Scenario: 滚动整条历史
- **WHEN** 用户上下 fling
- **THEN** 滚动平滑,无掉帧、无白屏
- **AND** 离屏的节点不重绘(viewport culling 或 RepaintBoundary)

#### Scenario: 树高范围
- **WHEN** 默认 pxPerYear = 0.5
- **THEN** 整棵树总高 ≈ (1978 - (-2500)) × 0.5 = 2239 px,可滚动
