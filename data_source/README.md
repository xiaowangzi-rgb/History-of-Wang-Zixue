# data_source/

校对后的源数据目录,**进 git**,采用 CC-BY-SA-4.0(见同目录 LICENSE)。

## 边界

- ✅ 进入此目录的所有 JSON **必须经人工校对**
- ❌ LLM 直接生成的草稿**不**进此目录(放 `staged/`,gitignore 中)
- ❌ CBDB 原始 SQLite 不放此目录(放 `raw/`,gitignore 中)

## 结构(待阶段 1 起开始填充)

```
data_source/
├── LICENSE                     # CC-BY-SA-4.0
├── README.md                   # 本文件
├── dynasties.json              # 全部朝代
├── regimes.json                # 全部政权(三国 / 南北朝 / 五代十国等并立期)
├── persons/                    # 按朝代拆分
│   ├── pre_qin.json
│   ├── spring_autumn.json      # 阶段 1 起点(孔子等)
│   ├── ...
└── events/                     # 按朝代拆分
    └── spring_autumn.json
```

详见 `docs/data-schema.md`。
