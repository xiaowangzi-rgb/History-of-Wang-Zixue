# 数据流水线 (Data Pipeline)

> 从原始第三方数据到 app 可吃的 JSON 的完整 ETL 链路。

---

## 阶段总览

```
raw/                  staged/             data_source/         assets/data/
(原始)                (中间)              (校对后,进 git)      (build 产物)
 ↓                     ↓                   ↓                    ↓
extract → merge → enrich → review → validate → build_personas → assets

第三方数据   多源融合    LLM 富化   人工校对   一致性校验   渲染 prompt
(只读)                              ★关键      ★必跑                  
```

每一步对应 `tools/` 下的一个或多个 Python 脚本。

---

## Stage 1: extract — 抽取

每个数据源一个抽取脚本,输出格式统一为「候选 person/event JSON」。

### `tools/etl/extract_cbdb.py`

输入: `raw/cbdb_latest.sqlite`
输出: `staged/persons_cbdb.json`

```python
# 伪代码
import sqlite3
db = sqlite3.connect('raw/cbdb_latest.sqlite')
for row in db.execute("""
    SELECT c_personid, c_name_chn, c_birthyear, c_deathyear, c_dy
    FROM BIOG_MAIN
    WHERE c_dy IN (?, ?, ?)  -- 过滤朝代
"""):
    write({...})
```

关键表:
- `BIOG_MAIN`(人物主)
- `KIN_DATA`(亲属关系)
- `ASSOC_DATA`(社会关系,师生 / 同僚等)
- `POSTED_TO_OFFICE_DATA`(任职)
- `ENTRY_DATA`(科举入仕)

### `tools/etl/extract_poetry.py`

输入: `raw/chinese-poetry/`(git clone)
输出: `staged/persons_poetry.json` + `staged/works.json`

按目录推断朝代:
- `全唐诗/authors.tang.json` → dynasty=tang
- `宋诗/authors.song.json` → dynasty=song

### `tools/etl/fetch_wikidata.py`

SPARQL 查询目标人物列表,缓存到 `raw/wikidata-cache/<qid>.json`,然后产出
`staged/persons_wikidata.json`。

例如查"先秦诸子":
```sparql
SELECT ?p ?pLabel ?birth ?death WHERE {
  ?p wdt:P106/wdt:P279* wd:Q2306091 .  # 哲学家
  ?p wdt:P27 wd:Q29520 .              # 中国国籍
  ?p wdt:P569 ?birth .
  FILTER(?birth < "0000-01-01"^^xsd:dateTime)
  ...
}
```

API 限流: 加 `time.sleep(1)`,有礼貌。

---

## Stage 2: merge — 多源去重

### `tools/etl/merge_persons.py`

输入: `staged/persons_*.json`
输出: `staged/persons_merged.json`

去重策略:
1. 按 `name + dynasty` 匹配(姓名相同 + 朝代相同 → 同一人)
2. 别名字段(`altNames`)也参与匹配
3. **冲突时优先级**: CBDB > Wikidata > chinese-poetry
4. 字段合并: 取并集,缺字段从其他源补
5. 每条记录加 `mergedFrom: ["cbdb", "wikidata"]` 溯源

### 输出示例

```json
{
  "id": "person_su_shi",
  "name": "苏轼",
  "altNames": ["东坡居士", "苏东坡", "子瞻"],
  "dynasty": "northern_song",
  "birthYear": 1037,
  "deathYear": 1101,
  "summary": "...(从 CBDB c_notes 取)",
  "works": [...],  // 从 chinese-poetry 取
  "mergedFrom": ["cbdb", "chinese-poetry"]
}
```

---

## Stage 3: enrich — LLM 富化

### `tools/enrich/translate_desc.py`

文言文 desc → 现代汉语 summary。
对 chinese-poetry 来源数据用得多。

```bash
python tools/enrich/translate_desc.py \
    --input staged/persons_merged.json \
    --output staged/persons_translated.json \
    --model deepseek-chat \
    --batch-size 20
```

### `tools/enrich/generate_persona.py`

为核心人物生成:
- `personality`(150 字内性格描述)
- `selfReference`(自称)
- `speechStyle`(2-3 个示例对话)
- 严肃版 + 演义版 各一套

```bash
python tools/enrich/generate_persona.py \
    --input staged/persons_translated.json \
    --output staged/persons_with_persona.json \
    --core-only \                # 只为 core 人物做(非 core 留空)
    --model deepseek-chat
```

`core` 人物 = `tags` 里有 `core` 或者手工标记的重点人物。其他人物 LLM 对话
不强求高质量,可以略过 personality 字段(运行期 fallback 到一个泛用 prompt)。

### `tools/enrich/generate_events.py`

按朝代生成事件草稿:

```bash
python tools/enrich/generate_events.py \
    --dynasty spring_autumn \
    --count 30 \                 # 目标事件数
    --output staged/events_spring_autumn_draft.json \
    --model deepseek-chat
```

### LLM 调用约定

所有 enrich 脚本共用 `tools/enrich/_llm.py`(底层 OpenAI 兼容客户端):
- 从 `os.environ` 读 key,**不接受** CLI 参数 / 配置文件
- 失败重试 3 次,指数退避
- 全部输出 strict JSON(用 `response_format={"type": "json_object"}` 或解析时
  容错)
- 缓存到 `staged/.llm-cache/<hash>.json`,避免重复调用

---

## Stage 4: review — 人工校对(★ 不可省略)

`staged/*.json` 里所有 `source: "llm-draft"` 的字段必须经人工校对。

### 工作流

1. 打开 `staged/persons_with_persona.json` 或 `staged/events_*.json`
2. **重点校对**:
   - **年份**(LLM 最容易在这里幻觉,差几年是常见错误)
   - **关系**(尤其老师/学生方向、君臣关系)
   - **关键事件描述**(史实细节)
3. 修改后,把 `source` 改为 `"llm-reviewed"` 或 `"manual"`
4. 移到 `data_source/` 对应文件

可写一个 `tools/review.py` 命令行交互工具(后续做):
- 显示一条记录
- 旁边显示 Wikipedia / 史料链接做参考
- 交互式 accept / edit / reject

### 不校对的代价

LLM 错的史实进了 data_source → 再经 build_personas 进 prompt → 用户和 LLM
扮演的"孔子"对话,孔子说错了史实 → 用户记错了 → 你做的 app 在传播错误信
息。这对一个**学习类**产品是不可接受的。

---

## Stage 5: validate — 一致性校验

### `tools/validate.py`

```bash
python tools/validate.py data_source/
```

检查项见 `data-schema.md` 校验规则章节。**任何一项失败,build 阻断。**

---

## Stage 6: build_personas — 渲染 system prompt

### `tools/build_personas.py`

```python
from jinja2 import Template

template_serious = Template(open('personas/template_serious.j2').read())
template_romance = Template(open('personas/template_romance.j2').read())

for person in load_persons('data_source/persons/'):
    if person.has_persona_fields():
        person.systemPromptSerious = template_serious.render(person=person)
        person.systemPromptRomance = template_romance.render(person=person)

save('assets/data/persons.json', all_persons)
```

`personas/template_serious.j2` 的内容结构见 `persona-design.md`。

---

## Stage 7: build — 主控

### `tools/build.py`

一键跑全流程:

```bash
python tools/build.py [--from-stage extract] [--dynasties qin,han]
```

```python
def build(from_stage='extract', dynasties=None):
    if from_stage <= 'extract':
        extract_cbdb()
        extract_poetry()
        fetch_wikidata()
    if from_stage <= 'merge':
        merge_persons()
    if from_stage <= 'enrich':
        translate_desc()
        generate_persona(core_only=True)
        generate_events(dynasties=dynasties)
    if from_stage <= 'validate':
        validate()
    if from_stage <= 'build_personas':
        build_personas()
        copy_to_assets()
    print("✅ Build complete")
```

支持从中间阶段开始,避免 LLM 调用浪费。

---

## 文件去向矩阵

| 文件位置 | 进 git? | 大小级别 | 来源 |
|---|---|---|---|
| `raw/` | ❌ | 几百 MB | 第三方原始下载 |
| `staged/` | ❌(默认) | 几十 MB | 中间产物,可重跑 |
| `staged/.llm-cache/` | ❌ | 不定 | LLM 调用缓存,可删 |
| `data_source/` | ✅ | 几 MB | 校对后的精简数据,**项目核心资产** |
| `personas/` | ✅ | KB | prompt 模板 |
| `tools/` | ✅ | KB | 全部 Python 脚本 |
| `assets/data/` | ✅ | 几 MB - 几十 MB | build 产物,Flutter 打包用 |

---

## 重跑性 (Idempotency)

所有脚本必须**可重入**:跑两遍结果一致,不会越跑越乱。

具体做法:
- 抽取脚本: 总是覆盖输出
- merge: 按 ID 去重,以最新一次为准
- enrich(LLM 调用): 用缓存,key = hash(input + prompt + model)
- build_personas: 总是从 data_source 读,完整覆盖 assets/

---

## 性能预估(自用规模)

- CBDB 抽取(过滤后保留几千核心): ~1 分钟
- chinese-poetry: 秒级
- Wikidata SPARQL(几百次,1 秒/次):~5-10 分钟
- LLM enrich(几千人物 × 2 prompt 模式):**几小时,主要成本**
- build_personas: 秒级
- validate: 秒级

LLM 调用是大头,所以缓存和增量更新非常重要。新增一个朝代时,**只跑该朝代**的
enrich,不要全跑。
