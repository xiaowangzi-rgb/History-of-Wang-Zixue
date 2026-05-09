## 1. 环境准备

- [ ] 1.1 用户跑 `flutter --version` 确认 Flutter SDK 已装(若没装 → 装 stable)
- [ ] 1.2 用户跑 `flutter doctor`,把所有 ✗ 修绿(Android toolchain / Android Studio / 真机或模拟器至少一个)
- [ ] 1.3 用户连真机或启动 Android 模拟器
- [ ] 1.4 在项目根 `flutter create . --project-name wzxhistory --org com.wangzixue --platforms android`(用现有目录初始化,只生成 android/iOS 骨架,不覆盖既有 docs/data_source 等)
- [ ] 1.5 review 生成的 `pubspec.yaml`,加入依赖: `google_fonts`、`flutter_markdown`、`provider`、`path_provider`(后用)
- [ ] 1.6 跑 `flutter pub get` 确认依赖安装成功
- [ ] 1.7 跑 `flutter run` 看到默认 counter app 能在真机/模拟器跑起来 → 环境绿灯

## 2. assets/data 接入 + 数据模型

- [ ] 2.1 在 `pubspec.yaml` 的 `flutter:` 下加入 `assets:`,路径为 `assets/data/`
- [ ] 2.2 写 `lib/models/dynasty.dart`、`regime.dart`、`event.dart`、`person.dart`(POJO + fromJson)
- [ ] 2.3 写 `lib/data/asset_data_loader.dart`(rootBundle.loadString → jsonDecode → 模型)
- [ ] 2.4 写 `lib/data/app_data_store.dart`(Provider 入口,持有 4 个 Map<id, T> + getDynastiesSorted / getEventsByDynasty 等查询方法)
- [ ] 2.5 在 main.dart 启动时 await loader.loadAll() 后再 runApp(成功 → 主页;失败 → ErrorScreen)
- [ ] 2.6 单测: 加载 assets 后 dynasty 数 == 23 / regime == 47 / event == 139 / person == 532

## 3. Theme + 设计 token 落地

- [ ] 3.1 写 `lib/theme/colors.dart`(从 docs/design-tokens.md 抄出 light / dark 完整 ColorScheme)
- [ ] 3.2 写 `lib/theme/typography.dart`(google_fonts: Noto Serif SC + Noto Sans SC,字号阶梯)
- [ ] 3.3 写 `lib/theme/app_theme.dart`(ThemeData light + dark)
- [ ] 3.4 main.dart MaterialApp themeMode: ThemeMode.system + theme + darkTheme
- [ ] 3.5 在真机上切系统外观,验证 light/dark 切换无遗漏色

## 4. TreeLayoutEngine

- [ ] 4.1 写 `lib/tree/layout_engine.dart`(纯函数: List<Dynasty> + List<Regime> → List<NodeLayout>)
- [ ] 4.2 实现"主朝代占中间列(x=0),按 endYear 倒序铺(y = -year * pxPerYear)"
- [ ] 4.3 实现"并立 regime 按 siblingRegimeIds 数量在主朝代两侧分列"
- [ ] 4.4 实现"parentRegimeId 链 + mergedIntoRegimeId 决定分裂 / 汇合的连线 path"
- [ ] 4.5 实现 viewport culling: 给定可见 y 区间,只输出该区间的节点
- [ ] 4.6 单测: 三国 / 北朝东西魏分合 / 战国七雄 / 春秋七国 各跑一遍,验证布局合理

## 5. TreeCanvas (CustomPainter)

- [ ] 5.1 写 `lib/tree/tree_canvas.dart`(CustomPainter,paint() 接 List<NodeLayout>)
- [ ] 5.2 实现年份轴左侧 24 px 区(每 100 年一格 + 标签)
- [ ] 5.3 实现朝代色背景带(每个 dynasty [startYear, endYear] 半透明色块,延伸到屏宽)
- [ ] 5.4 实现朝代节点(印章风矩形 80×40 + 名 + 年份)
- [ ] 5.5 实现政权节点(60×32,小一号)
- [ ] 5.6 实现连线: 主朝代之间直线、并立期分支曲线
- [ ] 5.7 实现雾化效果(historicity != "historical" → 灰阶 + blur σ=2 + alpha 0.7)
- [ ] 5.8 用 RepaintBoundary 包住,验证 frame timing 60fps

## 6. 主页面 (TreeTimelinePage)

- [ ] 6.1 写 `lib/pages/tree_timeline_page.dart`(Scaffold + SingleChildScrollView + CustomPaint)
- [ ] 6.2 实现 GestureDetector / hit testing: tap 落在节点矩形内 → 触发 onNodeTap
- [ ] 6.3 onNodeTap → showModalBottomSheet 弹出 DynastyDetailSheet
- [ ] 6.4 实现 SafeArea + 顶部 AppBar("中国历史" + 主题切换按钮 placeholder)

## 7. DynastyDetailSheet

- [ ] 7.1 写 `lib/sheets/dynasty_detail_sheet.dart`(StatelessWidget,接 Dynasty 参数)
- [ ] 7.2 顶部:朝代名 + 起讫年份 + summary
- [ ] 7.3 中部:Events 区(从 store.getEventsByDynasty(dynasty.id),按 year 升序,ListTile)
- [ ] 7.4 底部:Persons 区(从 store.getPersonsByDynasty,按 birthYear 升序,横向滑动 chip 列表 — 因为可达 100+ 君主)
- [ ] 7.5 tap 事件 ListTile → Navigator.pushNamed('/event/:id')

## 8. 事件详情页

- [ ] 8.1 写 `lib/pages/event_detail_page.dart`(Scaffold + AppBar + body)
- [ ] 8.2 顶部:事件名 + year + summary
- [ ] 8.3 主体:flutter_markdown 渲染 event.body(若有)
- [ ] 8.4 placeholder: body 为空时显示"本事件暂无详细叙述"
- [ ] 8.5 底部:participants 列表(person link)、locationName(若有)

## 9. 真机测试 + 调优

- [ ] 9.1 在自己 Android 真机跑 `flutter run --release`(release 模式才有真实 perf)
- [ ] 9.2 滚动整条历史,确认无掉帧、无错位、无溢出
- [ ] 9.3 各朝代点 → BottomSheet 数据正确
- [ ] 9.4 三国 / 北朝东西魏 / 战国 / 春秋 视觉验证(分支正确)
- [ ] 9.5 light/dark 切换试 5 次
- [ ] 9.6 调 pxPerYear: 试 0.4 / 0.6 / 0.8 / 1.0,选最舒服的
- [ ] 9.7 截屏存 `docs/screenshots/`(后续 README 用)

## 10. 收尾

- [ ] 10.1 跑 `flutter analyze` 0 warnings
- [ ] 10.2 跑 `flutter test` 全 pass(主要是 4.6 / 2.6 单测)
- [ ] 10.3 git add lib/ android/ pubspec.yaml + 截图,commit
- [ ] 10.4 `openspec validate phase-1-tree-renderer` 通过
- [ ] 10.5 archive: `/opsx:archive phase-1-tree-renderer`
