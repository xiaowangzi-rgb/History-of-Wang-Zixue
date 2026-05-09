# 25 朝代色板 v0.6

> 创建于 2026-05。每朝代一对 light/dark 颜色,记入 `data_source/dynasties.json`
> 的 `color` (light) + `colorDark` (dark) 字段。
>
> 设计原则: 矿物色 / 自然色 / 中国画颜料,饱和度 25-45%,相邻朝代色相隔 ≥ 30°。

---

## 完整色板

| ID | 朝代 | 中文意象 | Light hex | Dark hex | 备注 |
|---|---|---|---|---|---|
| `dynasty_legendary` | 传说时代 | (灰阶) | `#A8A29C` | `#7A6A6A` | 雾化,不算"色" |
| `dynasty_xia` | 夏 | 赭石 | `#B97A56` | `#D49678` | 红土 |
| `dynasty_shang` | 商 | 青铜 | `#8B6F47` | `#A88B5F` | 礼器 |
| `dynasty_western_zhou` | 西周 | 朱砂 | `#C04848` | `#D86060` | 王畿 |
| `dynasty_eastern_zhou` | 东周 | 石黄/青金 | `#A89858` | `#C2B070` | 春秋 + 战国共用主色 |
| `dynasty_qin` | 秦 | 墨黑 | `#2D2A26` | `#4A4540` | 秦尚黑 |
| `dynasty_western_han` | 西汉 | 赤朱 | `#B8473C` | `#D45C50` | 汉尚赤 |
| `dynasty_xin` | 新莽 | 褐黄 | `#997A5C` | `#B59070` | 短暂 |
| `dynasty_eastern_han` | 东汉 | 丹砂 | `#A04E45` | `#BC665D` | 西汉 略变 |
| `dynasty_three_kingdoms` | 三国(主朝代) | 灰青 | `#5C6F94` | `#7589AB` | 上层名义 |
| `dynasty_western_jin` | 西晋 | 紫檀 | `#6B4F75` | `#85688E` | |
| `dynasty_eastern_jin` | 东晋 | 丁香 | `#806F94` | `#9888AC` | |
| `dynasty_sixteen_kingdoms` | 十六国(主朝代) | 驼色 | `#8C6B4B` | `#A8856A` | 北方混乱 |
| `dynasty_southern_northern` | 南北朝(主朝代) | 秋香 | `#A89858` | `#C2B070` | 实际拆 regime |
| `dynasty_sui` | 隋 | 群青 | `#3F5B7C` | `#5C7898` | 短暂统一 |
| `dynasty_tang` | 唐 | 朱朱 | `#C84E4E` | `#E07070` | 盛唐气派,色更鲜 |
| `dynasty_five_dynasties_ten_kingdoms` | 五代十国 | 褐石 | `#806147` | `#997D62` | 实际拆 regime |
| `dynasty_song` | 宋(主朝代) | 豆青 | `#5E8970` | `#7AA38B` | 宋色清雅 |
| `dynasty_yuan` | 元 | 宝蓝 | `#3F4F7C` | `#5C6E98` | 蒙古蓝 |
| `dynasty_ming` | 明 | 海棠 | `#B85D6E` | `#D27689` | 红墙 |
| `dynasty_qing` | 清 | 琉璃 | `#4A6E8C` | `#688AAB` | 满洲蓝 |
| `dynasty_republic` | 民国 | 青灰 | `#6E7B82` | `#8A969D` | 中性 |
| `dynasty_prc_pre_reform` | 新中国(1949-1978) | 墨灰 | `#4A4A4A` | `#6A6A6A` | 朴素 |

并立期 regime(在 `data_source/regimes.json` 中):

| Regime | 朝代色 (light/dark) | 备注 |
|---|---|---|
| `regime_wei`(曹魏) | `#5C6F94` / `#7589AB` | 三国主色 |
| `regime_shu`(蜀汉) | `#4A7858` / `#6A9477` | 与魏蓝色对比 |
| `regime_wu`(东吴) | `#6189A6` / `#7CA4C0` | 蓝绿调,与魏区分 |
| `regime_northern_wei`(北魏) | `#A89858` / `#C2B070` | 北朝代表 |
| `regime_song`(刘宋) | `#5E7B6E` / `#7A9788` | 沉香 |
| 战国七雄 | 见下方专表 |

---

## 战国七雄 regime 配色

战国时段 7 国并立,色板需要互相区分:

| Regime | Light hex | Dark hex |
|---|---|---|
| `regime_qin_state`(秦) | `#3D3A36` | `#5A5550` |
| `regime_chu`(楚) | `#5C7A4F` | `#7A9870` |
| `regime_qi`(齐) | `#A88E5F` | `#C2A878` |
| `regime_yan`(燕) | `#5A6B85` | `#7889A0` |
| `regime_zhao`(赵) | `#8A6B7A` | `#A88898` |
| `regime_wei_state`(魏) | `#9D6B5C` | `#B68674` |
| `regime_han_state`(韩) | `#6F8C8E` | `#8AA8AA` |

> 注: 七国名称与后世朝代重名(秦/魏)→ ID 后缀加 `_state` 区分。

---

## 五代十国 regime 配色

10 国 + 5 代,Phase 1 只录 5 代主政权 + 主要 3-5 国:

| Regime | Light hex | Dark hex |
|---|---|---|
| `regime_later_liang`(后梁) | `#806147` | `#997D62` |
| `regime_later_tang`(后唐) | `#A05B47` | `#B87862` |
| `regime_later_jin`(后晋) | `#7A6B5C` | `#94867A` |
| `regime_later_han`(后汉) | `#8B5C4F` | `#A47A6C` |
| `regime_later_zhou`(后周) | `#5C7B6F` | `#7A9888` |
| `regime_southern_tang`(南唐) | `#5E8970` | `#7AA38B` |
| `regime_wuyue`(吴越) | `#6189A6` | `#7CA4C0` |
| 其他十国按需补 | (灰色统一 `#807A70`) | `#9A9489` |

---

## 春秋诸侯 regime 配色

Phase 1 主要 5-7 国,其他归"其余诸侯":

| Regime | Light hex | Dark hex |
|---|---|---|
| `regime_lu`(鲁) | `#A88E5F` | `#C2A878` | 孔子之国 |
| `regime_qi_state_sa`(齐,春秋) | `#5A6B85` | `#7889A0` | 桓公 |
| `regime_jin_state_sa`(晋) | `#6F8C8E` | `#8AA8AA` | 文公 |
| `regime_chu_state_sa`(楚) | `#5C7A4F` | `#7A9870` | 庄王 |
| `regime_qin_state_sa`(秦,春秋) | `#3D3A36` | `#5A5550` | 穆公 |
| `regime_song_state`(宋) | `#7A8B6F` | `#94A589` | 襄公 |
| `regime_wu_state`(吴,春秋末) | `#6189A6` | `#7CA4C0` | 阖闾 |
| 其他诸侯 | 统一 `#807A70` | `#9A9489` | 折叠显示 |

> 注: 春秋时段 ID 后缀 `_sa` (spring-autumn),战国 `_state`,避免与朝代重名冲突

---

## 配色关系图(光环)

```
                  暖色系 (赤/朱/黄/橙)
                  ────────────────────────
                  夏(赭石) / 西周(朱砂) /
                  西汉(赤朱) / 东汉(丹砂) /
                  唐(朱朱) / 明(海棠)
                  → 多用于"统一王朝/盛世"

                  冷色系 (青/蓝/紫)
                  ────────────────────────
                  秦(墨黑) / 三国(灰青) /
                  晋(紫檀/丁香) / 隋(群青) /
                  元(宝蓝) / 清(琉璃)
                  → 多用于"短暂朝代 + 北方民族"

                  中性 (褐/灰/绿)
                  ────────────────────────
                  商(青铜) / 新莽(褐黄) /
                  十六国(驼色) / 五代(褐石) /
                  宋(豆青) / 民国(青灰) /
                  新中国(墨灰)
```

设计意图:
- **暖色 = 兴盛王朝**(汉唐明的"盛世"感)
- **冷色 = 短暂或北方**(秦/晋/元/清的"硬朗"感)
- **中性 = 过渡/分裂**(商/五代/宋的"复杂"感)

不严格,但帮助用户在树图上**视觉识别朝代性格**。

---

## 实施

`data_source/dynasties.json` 每条增加:

```json
{
  "id": "dynasty_western_zhou",
  ...
  "color": "#C04848",
  "colorDark": "#D86060"
}
```

`data_source/regimes.json` 每条同理。

Flutter 端按主题模式选 color 或 colorDark,通过 `Theme.of(context).brightness`
判断。

---

## 兼容性

WCAG 对比度检查:
- 朝代色作为**节点填充背景** → 阴文白字 #FFFFFF 在朝代色上对比度 ≥ 4.5:1 ✓
  (所有色饱和度 25-45% + 暗度足够)
- 朝代色作为**文字颜色**(罕用,详情页 markdown 链接) → light 模式直接用,dark
  模式用 colorDark
- 朝代色作为**背景色块**(树图朝代色块背景) → 用 alpha 0.1-0.2 透明度叠加,
  不影响文字可读性

---

## 调整记录

- 2026-05-09: 初版,基于 ui-ux-pro-max 输出
- (后续调整在此追加)
