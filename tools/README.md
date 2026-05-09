# tools/

开发期 Python 脚本。运行期 app 不依赖这里的任何东西。

## 依赖

```bash
pip install jsonschema Pillow requests
# β 深耕阶段需要:
pip install scrapling
```

环境变量(LLM 起草用):
- `DEEPSEEK_API_KEY` — 主力批量
- `ANTHROPIC_API_KEY` — 精修

## 脚本一览

| 脚本 | 作用 |
|---|---|
| `schema/` | JSON Schema(dynasty / regime / event / person)+ Python 入口 |
| `validate.py` | 校验 `data_source/`(schema + 跨引用 + 字数 + 树拓扑 + β 深耕 body 必填等) |
| `process_images.py` | `raw/images/` 下原图 → `data_source/images/persons/` 的 800×600 WebP + 缩略图 |
| `build_image_manifest.py` | 扫 `data_source/images/` 写 `assets/images/_manifest.json`(SHA-256 + size) |
| `build.py` | 跑 validate → 合并 `data_source/` → 写 `assets/data/`(含 manifest.json,SHA-256 + minAppVersion) |

## 典型流程

```bash
# 1. 校验源数据
python tools/validate.py

# 2. 处理图片(可选,首次跑或新增图后)
python tools/process_images.py
python tools/build_image_manifest.py

# 3. 构建 app 资产
python tools/build.py
```

`build.py` 默认会先调 `validate.py`,失败则中止。加 `--skip-validate` 可跳过(不推荐)。

## 校验规则速查

`validate.py` 实现的规则(详见脚本顶部 docstring):

- R1 ID 唯一
- R2 跨实体引用都要解析得到
- R3 `_schemaVersion` 必须等于当前版本(v0.6)
- R4 `summary` 50-1000 / `body` 800-5000 字符
- R5 树拓扑: sibling 双向、parent 链不闭环
- R6 β 深耕(夏 / 商 / 西周 / 东周)事件必须有 body
- R7 `source: "llm-draft"` 不允许进 `data_source/`
- R8 event.year 应在 dynasty 范围内(soft warning)
