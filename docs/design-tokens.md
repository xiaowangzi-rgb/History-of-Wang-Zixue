# Design Tokens v0.6

> 创建于 2026-05。app **完整设计系统的事实来源**。Flutter 实施直接对照本表。
>
> 设计语言: 水墨电子纸 (Ink-Paper),详见 ADR-027。

---

## 颜色 — 全局基础

### 背景与表面

| Token | Light | Dark | 用途 |
|---|---|---|---|
| `bg-primary` | `#FDFBF7` | `#000000` | App 主背景(整屏底色) |
| `bg-surface` | `#FFFFFF` | `#121212` | Material 3 surface(卡片底层) |
| `bg-card` | `#FAF7F0` | `#1E1E1E` | 事件 / 朝代卡片背景 |
| `bg-bottomSheet` | `#FFFFFF` | `#1A1A1A` | 抽屉式弹层背景 |
| `bg-legendary` | `#F0EBE0` | `#2A1F1F` | 传说时代雾化区 |

### 文字

| Token | Light | Dark | 对比度 vs bg-primary | 用途 |
|---|---|---|---|---|
| `text-primary` | `#1A1A1A` | `#FAFAFA` | 17:1 / 19:1 | 主标题 / body 主要文字 |
| `text-secondary` | `#5A5751` | `#B0B0B0` | 7:1 / 8:1 | 副标题 / 元数据 |
| `text-muted` | `#8A8580` | `#6A6A6A` | 4.5:1 / 4.8:1 | 提示 / 弱化文字 |
| `text-legendary` | `#888888` | `#7A6A6A` | 3:1 (允许低,雾化) | 传说时代文字 |
| `text-link` | (用朝代色) | (用朝代色 dark) | — | body 内 markdown 链接 |

### 边框 / 分隔

| Token | Light | Dark | 用途 |
|---|---|---|---|
| `border-default` | `#E8E0D5` | `#2C2C2C` | 卡片 / 列表分隔 |
| `border-emphasis` | `#B0A89D` | `#4A4A4A` | 重点边框(选中态) |
| `border-legendary` | `#C0B5A0` (虚线) | `#5A4A4A` (虚线) | 传说节点边框 |

### 阴影

| Token | Light | Dark |
|---|---|---|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.06)` | `0 1px 2px rgba(0,0,0,0.4)` |
| `shadow-md` | `0 4px 8px rgba(0,0,0,0.10)` | `0 4px 8px rgba(0,0,0,0.6)` |
| `shadow-lg` | `0 8px 24px rgba(0,0,0,0.14)` | `0 8px 24px rgba(0,0,0,0.7)` |

阴影**克制使用**,主要在卡片悬浮 / BottomSheet 边缘,不在 hero 元素堆砌。

### Accent / 朝代色

朝代色 = 25 套独立 light/dark 配对,见 `docs/dynasty-palette.md`。

事件 category 配色(Phase 2):
- `cat-war`: 朱砂 `#C04848`
- `cat-politics`: 墨黑 `#2D2A26`
- `cat-culture`: 石青 `#5C7A8C`
- `cat-science`: 豆青 `#5E8970`
- `cat-diplomacy`: 群青 `#3F5B7C`
- `cat-economy`: 金土 `#9D7C4E`
- `cat-person`: 朱红 `#A04E45`

---

## 排版

### 字体家族

| Family | Light + Dark 都用 | 用途 |
|---|---|---|
| `font-serif` | Noto Serif SC | 标题 / hero / 引用 |
| `font-sans` | Noto Sans SC | body / UI 控件 |
| `font-kai` | 系统楷体 (Flutter `serif` 回退) | 传说时代 |

加载方式: `google_fonts: ^6.x` 包,首次启动下载后缓存到本地。

### Type scale(Mobile-first,iPhone 13/14 标准)

| Token | Family | Size | Weight | Line height | 用途 |
|---|---|---|---|---|---|
| `text-display` | serif | 28 sp | Bold (700) | 1.3 | 详情页大标题 |
| `text-h1` | serif | 22 sp | SemiBold (600) | 1.35 | AppBar 标题 |
| `text-h2` | serif | 20 sp | Bold (700) | 1.4 | body `## 起因` 标题 |
| `text-h3` | serif | 17 sp | SemiBold (600) | 1.4 | 朝代节点 / 卡片标题 |
| `text-body` | sans | 16 sp | Regular (400) | 1.7 | body 正文 / summary |
| `text-meta` | sans | 14 sp | Regular (400) | 1.5 | 元数据 / 时间 / 副标题 |
| `text-caption` | sans | 12 sp | Regular (400) | 1.4 | 标签 / 注释 / chip 文字 |
| `text-tiny` | sans | 11 sp | Regular (400) | 1.3 | 节点上的年份小字 |
| `text-quote` | serif italic | 15 sp | Regular (400) | 1.6 | markdown blockquote |
| `text-legendary` | kai | 14 sp | Regular (400) italic | 1.5 | 传说时代文字 |

**Dynamic Type**: Flutter `MediaQuery.textScaleFactor` 缩放,**上限 1.3x**
(防布局崩),通过 `MaterialApp.builder` 限制。

---

## Spacing

8-base scale:

| Token | Value | 用途 |
|---|---|---|
| `space-1` | 4 dp | 极小间距(图标内 padding) |
| `space-2` | 8 dp | 控件内距 |
| `space-3` | 12 dp | 卡片内距 / 控件间 |
| `space-4` | 16 dp | 段落间距 / 标准 padding |
| `space-5` | 20 dp | 卡片间距 / 区块间 |
| `space-6` | 24 dp | 大段间距 |
| `space-8` | 32 dp | 章节分隔 |
| `space-12` | 48 dp | 视觉呼吸区 |

页面级:
- AppBar 高: 56 dp(Material 默认)
- 整屏左右 padding: 16 dp
- 卡片内 padding: 16 上下 / 20 左右
- BottomSheet 顶部 drag handle: 高 4dp,左右居中

---

## Radius / 圆角

| Token | Value | 用途 |
|---|---|---|
| `radius-xs` | 2 dp | chip / tag |
| `radius-sm` | 4 dp | 节点 / 小卡片 |
| `radius-md` | 6 dp | 事件卡片 / 按钮 |
| `radius-lg` | 12 dp | 大容器 / 抽屉顶 |
| `radius-xl` | 20 dp | 全屏对话框(罕用) |
| `radius-full` | 9999 | 圆形头像 / chip |

**原则**: 微圆(2-6dp 主导),避免过软("Claymorphism" 风);也避免直角
(Brutalism 不应景)。

---

## 触摸目标 / Touch Target

**最小 48 dp**(Material 标准,iOS 44pt 也满足)。

| 控件 | 最小尺寸 | 实际推荐 |
|---|---|---|
| 朝代节点(level 1) | 48 × 48 | 80 × 60 |
| 政权节点(level 2) | 48 × 48 | 60 × 45 |
| 人物 chip | 44 × 44 | 圆 48 + label 下方 |
| 链接(markdown 内) | 44 × 44 | 文字 + 8dp 上下 padding |
| 卡片 | 任意 | 整卡可点击,内部不嵌互斥点击区 |

**间距**: 触摸目标之间 ≥ 8 dp 防误点。

---

## 转场 / 动画

| Token | Duration | Easing | 用途 |
|---|---|---|---|
| `transition-fast` | 150 ms | ease-out | 状态变化(按下态) |
| `transition-default` | 200 ms | ease-out | 颜色过渡 / 透明度 |
| `transition-page` | 280 ms | cubic-bezier(.4,0,.2,1) | 页面跳转 |
| `transition-sheet` | 320 ms | ease-in-out | BottomSheet 弹起 |

**禁用项**:
- 无 motion blur(违背 Ink-Paper 风)
- 无 bounce / spring 弹效(显得轻浮)
- 无 parallax 滚动(电池/晕动)
- 无 page turn 翻书(过度)

**尊重 reduce-motion**: `MediaQuery.disableAnimations`,触发时所有 duration → 0。

---

## 触觉反馈 (Haptic Feedback)

Flutter `HapticFeedback`,关键交互点:

| 触发 | 反馈 | 备注 |
|---|---|---|
| 点击朝代节点(展开) | `lightImpact` | 轻微 |
| 切换政权节点(level 2) | `selectionClick` | 选择感 |
| 跳转事件详情 | `selectionClick` | 同上 |
| 触发数据热更完成 | `mediumImpact` | 较明显 |
| 错误提示(罕用) | `heavyImpact` | 不要滥用 |

**关闭开关**: 设置页提供"关闭触觉反馈"选项(老人 / 怕震动用户)。

---

## SafeArea + Status Bar

```
   每个页面包裹层级:
   ────────────────────────────────────────
   MaterialApp
     └── Scaffold
           ├── AppBar (自动处理 SafeArea.top)
           └── body
                 └── SafeArea (主动包裹,处理 home indicator)
                       └── 真实内容
```

**Status Bar**:
- light 模式: 透明背景,深色图标(`SystemUiOverlayStyle.dark`)
- dark 模式: 透明背景,浅色图标(`SystemUiOverlayStyle.light`)

设置在 `MaterialApp` 的 `theme.appBarTheme.systemOverlayStyle`。

---

## 主题切换

```
   MaterialApp(
     theme: lightTheme,           // 上面所有 light token
     darkTheme: darkTheme,        // 上面所有 dark token
     themeMode: ThemeMode.system, // 默认跟随系统
   )

   设置页可强制:
   • 跟随系统 (system,默认)
   • 始终亮色 (light)
   • 始终深色 (dark)

   状态存 SharedPreferences,启动时读取
```

---

## 屏幕方向 (Phase 1)

```dart
WidgetsFlutterBinding.ensureInitialized();
SystemChrome.setPreferredOrientations([
  DeviceOrientation.portraitUp,
]);
runApp(MyApp());
```

Phase 2 视体验决定是否解锁横屏 / iPad。

---

## 性能预算 (Phase 1 移动端)

- 启动到首屏可交互: < 1.5s (冷启动) / < 0.5s (热启动)
- 树图首次渲染: < 200ms (节点数 ~30)
- 滚动 60 fps (无掉帧)
- 详情页打开 < 250ms
- APK 体积 < 30 MB(含字体 + 25 朝代 hero 图)
- 数据 JSON 内存占用 < 20 MB

---

## 不允许的设计选择(防漂移)

| 错误 | 原因 |
|---|---|
| ✗ 用 emoji 当 UI 图标 | 用 SVG / Material Icons / 自绘 |
| ✗ Claymorphism / 黏土 | 违背"严肃学习"调性 |
| ✗ Cyberpunk / Neon | 违背"水墨电子纸"基调 |
| ✗ Glassmorphism / 毛玻璃 | 违背"纸感"基调 |
| ✗ Light 模式纯白 #FFFFFF | 用米白 #FDFBF7,避免刺眼 |
| ✗ Dark 模式深灰 #1E1E1E 主背景 | 用 #000000(OLED 续航) |
| ✗ 浮动 navbar | 用 Material AppBar(自动 SafeArea) |
| ✗ Modal / Dialog 弹窗(主交互) | 用 BottomSheet |
| ✗ Hover 状态相关代码 | mobile 没 hover,用按下态 |
| ✗ 字体内联(`Inter Tight` etc) | 用 Noto Serif SC + Noto Sans SC |
