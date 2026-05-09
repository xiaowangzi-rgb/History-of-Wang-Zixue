## ADDED Requirements

### Requirement: Flutter 应用骨架

系统 SHALL 提供一个可在 Android 真机或模拟器上启动的 Flutter app,启动时加载 `assets/data/` 下的全部 JSON 数据并构建内存索引。

#### Scenario: 冷启动加载数据
- **WHEN** 用户首次启动 app(或冷启动)
- **THEN** app 从 `assets/data/{dynasties,regimes,events,persons,manifest}.json` 同步读取并解析
- **AND** 构建 `Map<String, Dynasty>`、`Map<String, Regime>`、`Map<String, HistoricalEvent>`、`Map<String, Person>` 四个内存索引
- **AND** 总加载时间 SHALL ≤ 500ms(真机 mid-range Android)
- **AND** 加载失败时 SHALL 显示错误页 + retry 按钮(不静默崩溃)

#### Scenario: 数据 schemaVersion 检查
- **WHEN** manifest.json 的 `_schemaVersion` 与 app 内置版本不匹配
- **THEN** app 显示"数据版本不兼容,请更新 app"提示
- **AND** 不进入主界面

### Requirement: 主题与设计 token 落地

系统 SHALL 应用 `docs/design-tokens.md` 定义的 light / dark 双套主题,并跟随系统外观自动切换。

#### Scenario: Light/Dark 跟随系统
- **WHEN** 系统外观切换(`MediaQuery.platformBrightness` 改变)
- **THEN** app 主题立即切换到对应的 light 或 dark 配色
- **AND** 朝代色用 `color`(light)或 `colorDark`(dark)字段

#### Scenario: 字体加载
- **WHEN** app 启动
- **THEN** 用 `google_fonts` package 加载 Noto Serif SC(标题)+ Noto Sans SC(正文)
- **AND** 无网络时回落到系统字体,功能不受阻

### Requirement: 路由结构

系统 SHALL 用 Flutter Navigator 2.0 或 1.0 提供至少 2 条路由:树图主页(`/`)、事件详情页(`/event/:id`)。

#### Scenario: 主页路由
- **WHEN** app 启动且数据加载成功
- **THEN** 默认显示树图主页

#### Scenario: 事件详情页
- **WHEN** 用户在 BottomSheet 点击事件标题
- **THEN** push 全屏路由 `/event/:id` 显示事件 markdown body
- **AND** 返回手势 / 系统返回键 SHALL 弹出回主页或上一层
