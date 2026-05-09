## Why

Phase 1 数据骨架已就位(23 朝代 + 47 政权 + 139 事件 + 532 人物),但用户**看不见**任何东西。数据 schema 是否合理(parentRegimeId / siblingRegimeIds 在 layout 算法里能否驱动出正确的 git 风格树图)只有跑出渲染器才能验证。先做一个能在手机上跑起来、能上下滚动浏览整棵历史树、能点节点看详情的 MVP,比继续打磨数据更有 leverage。

这是 Phase 1 的"核心可视化"部分,完成后 app 已经"能用",哪怕事件 body 还没深耕、图片还没全。

## What Changes

- 新建 Flutter 项目骨架(`lib/`、`pubspec.yaml`、Android 部分),不上 iOS
- 实现 **AssetDataLoader**:启动时从 `assets/data/{dynasties,regimes,events,persons,manifest}.json` 加载 + 简单内存索引
- 实现 **TreeLayoutEngine**:输入 dynasty + regime 列表,输出每个节点的 (x, y) 坐标 + 边连线;按 git 风格"从下到上、按时间从下到上"展开,正确处理三国 / 十六国 / 南北朝 / 五代十国 / 春秋战国并立(用 parentRegimeId / mergedIntoRegimeId / siblingRegimeIds 驱动多列布局)
- 实现 **TreeCanvas**(CustomPainter):画朝代节点(印章风)+ 政权分支 + 朝代色背景带 + 年份轴
- 实现 **节点交互**:tap → BottomSheet 显示朝代/政权 summary + 该时段事件列表 + 君主列表;tap event → 全屏 markdown body 视图(目前大多数 event 没 body 显示 placeholder)
- 实现 **设计 token 应用**:`docs/design-tokens.md` 的 light/dark 双套色 / 排版 / spacing 全部落到 ThemeData
- 实现 **传说时代雾化**:dynasty_legendary + 夏 historicity != "historical" 时节点画法不同(灰阶 + 模糊)
- **不做**(Phase 1 不在此 change 内):热更新模块、人物对话、做题、事件 body 深耕、图片资产 ingest

## Capabilities

### New Capabilities
- `tree-timeline-render`: 树形时间线渲染 — 数据加载、布局算法、Canvas 绘制、节点点击、详情面板
- `app-shell`: Flutter app 主体 — main.dart / 路由 / 主题 / 启动流程

### Modified Capabilities

(无 — 本 change 是首次引入 Flutter 端,没有已有 spec 修改)

## Impact

- **新增**:`lib/`(Flutter Dart 代码)、`android/`(Gradle / manifest)、`pubspec.yaml`、`pubspec.lock`
- **依赖**:`flutter`、`google_fonts`(Noto Serif/Sans SC)、`flutter_markdown`(事件 body)、`path_provider`(后续热更要)
- **不影响**:`tools/`、`data_source/`、`assets/data/`(只读消费,不改 schema)
- **平台**:仅 Android 首发,iOS 后期支持
- **性能预算**:启动加载 < 500ms(JSON 总量 ~300 KB),tree 首帧 < 100ms,滚动 60fps
