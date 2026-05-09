# 架构 (Architecture)

## 总览

整个系统分为**开发期**(我的电脑上的离线工具链)和**运行期**(用户手机上的
Flutter app)两部分,通过 `assets/data/*.json` 这个**数据契约**连接。

```
开发期(我的电脑,离线运行)              运行期(手机 app,联网调 LLM)
┌───────────────────────────────┐        ┌───────────────────────────────┐
│  data_source/  (源数据,校对后) │        │  Flutter app                  │
│      ↓                        │        │  ├─ UI(时间线/朝代图/卡片)    │
│  tools/build.py               │ build  │  ├─ SQLite(对话/做题/SRS)    │
│      ├─ ETL(多源融合)         │  ──→   │  ├─ OpenAI 兼容客户端         │
│      ├─ 富化(LLM)             │        │  └─ assets/data/*.json(只读) │
│      ├─ build_personas        │        │       ↑                       │
│      ├─ validate              │        │       预生成 systemPrompt 字段 │
│      └─ 输出 → assets/data/   │        │       (运行期不再拼装)        │
└───────────────────────────────┘        └───────────────────────────────┘
```

---

## 开发期 (`tools/`)

**职责**: 把"原始第三方数据 + 我的校对 + LLM 富化"变成 app 能直接吃的 JSON。

```
raw/                           # 原始数据,gitignore,只在本机
  cbdb_latest.sqlite
  chinese-poetry/
  wikidata-cache/
       ↓
tools/etl/                     # 多源抽取(每个源一个脚本)
  extract_cbdb.py              # SQLite → 候选 person JSON
  extract_poetry.py            # 文学家 + 作品
  fetch_wikidata.py            # SPARQL 查先秦/秦汉
  merge_persons.py             # 多源去重,冲突时优先 CBDB
       ↓
staged/                        # 中间产物,gitignore(也可以进 git 存档)
       ↓
tools/enrich/                  # LLM 富化层
  translate_desc.py            # 文言文 → 现代汉语 summary
  generate_persona.py          # 生成 personality / selfRef / 严肃 + 演义两套
  generate_events.py           # 按朝代生成事件(草稿)
       ↓
(人工校对环节)               # ★ 不可省略,这是数据质量底线
       ↓
data_source/                   # 校对后的源数据,进 git
  dynasties.json
  persons/qin.json
  events/qin.json
       ↓
tools/build_personas.py        # 渲染 system prompt(严肃 + 演义),写回字段
tools/validate.py              # 一致性校验(年份 / 关系 / cutoffYear)
       ↓
assets/data/                   # build 产物,进 git,Flutter 直接打包
  persons.json (含 systemPrompt_serious / systemPrompt_romance)
  events.json
  dynasties.json
```

### 关键设计决策

1. **`raw/` 不进 git**: CBDB 数据库几百 MB,且原数据许可不允许直接重新分发
2. **`data_source/` 进 git**: 校对后的精简数据是项目核心资产
3. **`staged/` 可选进 git**: 中间产物,看本地空间决定。建议**不进**,可重跑
4. **build 脚本必须可重入**: 跑两遍结果一致,而不是越跑越乱
5. **每个朝代独立 JSON**: `persons/qin.json` 而不是单文件 monolith,git diff 可读

---

## 运行期 (Flutter app)

**职责**: 加载预制资产、本地存储用户行为、转发 LLM 对话。

### 数据加载

启动时 `rootBundle.loadString('assets/data/persons.json')` 加载所有人物数据进
内存。对于"自用 + 中国史"这个规模(预计 200-3000 人物 + 300-500 事件),内存
完全够用,不需要数据库做查询。

**SQLite 只用于用户行为**:
- 对话历史(每个 person 多个 session)
- 做题进度 + SRS 状态(下次复习时间、记忆强度)
- 用户笔记 / 收藏

### LLM 客户端

OpenAI 兼容 baseUrl,运行期纯字符串拼接:

```dart
final sysPrompt = mode == 'serious'
    ? person.systemPromptSerious
    : person.systemPromptRomance;

final messages = [
  ChatMessage.system(sysPrompt),
  ...sessionHistory,
  ChatMessage.user(userInput),
];

final stream = openaiClient.streamChat(
  model: settings.modelName,
  messages: messages,
);
```

**关键**: `systemPrompt_*` 字段是开发期已经渲染好的成品文本,运行期**不做模板
渲染、不做字段拼接**。

### 凭据管理

- baseUrl / apiKey / modelName 用 `flutter_secure_storage`(Keychain /
  Keystore)
- 提供"设置"页让用户填入,**不内置任何默认 key**
- 切换模型不需要重启,每次调用读取最新设置

### 目录结构(运行期视角)

```
lib/
├── main.dart
├── data/                     # 数据加载
│   └── repository.dart       # 一次加载,内存缓存
├── models/                   # 数据模型(Freezed)
│   ├── person.dart
│   ├── event.dart
│   ├── dynasty.dart
│   └── regime.dart
├── ui/
│   ├── timeline/             # 时间线(纵向滚动 + 缩放)
│   ├── dynasty_map/          # 朝代脉络图(CustomPainter)
│   ├── person_card/          # 人物卡 + 关系网
│   ├── chat/                 # 对话界面(SSE 流式)
│   └── quiz/                 # 做题 + SRS
├── services/
│   ├── openai_client.dart    # OpenAI 兼容客户端
│   ├── srs_scheduler.dart    # 间隔重复算法
│   └── secure_config.dart    # 凭据存取
└── settings/
    └── settings_page.dart    # baseUrl / apiKey / modelName / 模式切换
```

---

## 数据契约 — `assets/data/*.json`

`assets/data/` 是开发期 build 脚本的最终产物,也是运行期 app 的唯一数据入口。
它的 schema 一旦固定,开发期和运行期就解耦了。

每条 person 记录在 build 后形如:

```json
{
  "id": "person_kongzi",
  "name": "孔子",
  "altNames": ["孔丘", "仲尼"],
  "dynasty": "spring_autumn",
  "birthYear": -551,
  "deathYear": -479,
  "historicity": "historical",
  "summary": "...",
  "personality": "...",
  "selfReference": "丘",
  "speechStyle": "...",
  "works": ["《论语》(由弟子辑录)", ...],
  "relations": [
    {"type": "student", "personId": "person_yanhui"},
    ...
  ],
  "events": ["event_kong_zhouyou", ...],
  "systemPromptSerious": "你是孔子(春秋鲁国人)... [完整 prompt 文本]",
  "systemPromptRomance": "..."
}
```

详见 `data-schema.md`。

---

## 边界与不变量

1. **运行期不修改 assets/**: app 是**只读消费方**,所有编辑发生在开发期
2. **运行期不调用 LLM 来生成内容**: LLM 只负责"扮演对话",不负责"产生数据"。
   想加新人物 / 新事件 → 走开发期流程
3. **不混用代码协议和数据协议**: `lib/` 下任何 .dart 文件 MIT,
   `data_source/` 下任何 .json 文件 CC-BY-SA-4.0
4. **system prompt 一旦上线只能换版本不能改写**: 用户的对话历史依赖某个具体
   prompt 版本。改 prompt 模板 → bump 版本号 → 用户可见"角色更新"通知
