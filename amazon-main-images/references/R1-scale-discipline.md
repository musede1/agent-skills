# R1-scale-discipline.md 尺度纪律

> 本文件定义"尺度优先决策链"。当产品尺寸档位为 XS 或 S 时强制激活,
> 覆盖并重排原 SKILL 的决策顺序,确保产品尺寸在决策链上游发言,
> 而不是最后一步才被动塞进画框。

---

## 一、核心原则:两条决策链

SKILL 从本次修订起,承认两条并列的决策链,按产品尺寸档位分流。

### 职责优先链路(M/L/XL 档位 / 原 SKILL 默认)

```
产品 → 风格 → 心智方案 → 职责分配(含自由景别)→ 道具填充 → 风格落点 → 逐图落地 → 校验
```

景别和道具规模是自由变量,由职责类型决定。适用于 20cm 以上的正常摆件。

### 尺度优先链路(XS/S 档位强制)

```
产品 → 尺寸档位 → 景别基线(被尺寸锁死)→ 职责/心智(在基线内选择)
     → 道具规模(按档位硬下限)→ 风格落点 → 逐图落地 → 校验
```

景别和道具规模是被尺寸约束的因变量,不能被职责或心智方案推翻。

### 路由规则

M1 Step 3 判定尺寸档位后,根据档位自动路由:
- 档位 = XS 或 S → 尺度优先链路,强制加载本文件所有约束
- 档位 = M / L / XL → 职责优先链路,本文件豁免

两条链路共用风格包、G1 写法、审核工具,差别只在 M2 Step 6 的景别和道具决策是否被尺寸约束。

---

## 二、为什么需要尺度优先链路

**商业原因**(核心):
- "比想象小"是亚马逊家居摆件类目 TOP3 差评原因之一
- 尺度误导 → 退货(扣物流+佣金)+ 差评(拉低星级)+ 平台下架风险
- 尺度问题不是审美问题,是合规+转化的双杀

**技术原因**:
- 原 SKILL 是按中型摆件(20-40cm)的构图习惯设计的
- 中景画面对中型摆件刚好,道具也刚好匹配
- 但 XS(<10cm)产品用同一套景别逻辑时,道具会"陪着产品一起缩",尺度对比关系归零
- 结果:7.5cm 的 urn 和 30cm 的雕像在画面里看起来差不多大

---

## 三、尺寸档位判定

| 档位 | 范围 | 典型产品 |
|---|---|---|
| **XS** | <10cm | 掌心纪念罐 / 迷你摆件 / 小型雕像 / 香薰吊坠 |
| **S** | 10–20cm | 小型花瓶 / 桌面摆件 / 小香薰蜡烛 |
| **M** | 20–30cm | 中型花瓶 / 台面雕塑 / 一般摆件 |
| **L** | 30–50cm | 大型花瓶 / 落地雕像 / 大摆件 |
| **XL** | >50cm | 落地雕塑 / 超大花器 |

判定以产品**最长边**为准。7.5×5cm → XS。

---

## 四、景别基线(XS/S 强制,M/L/XL 豁免)

| 档位 | 基线景别 | 禁用景别 | 产品画面高度占比上限 |
|---|---|---|---|
| **XS** | wide shot pulled back / medium wide 为主 | medium close-up 及更紧 | ≤20% |
| **S** | medium wide / medium 为主 | close-up(工艺图除外) | ≤30% |
| M | medium 为主 | — | ≤45%(软指标) |
| L | medium / medium wide | — | ≤55%(软指标) |
| XL | medium wide / wide | extreme close-up | ≤60%(软指标) |

**XS/S 铁律**:
- 景别基线为硬约束,不可因"节律需要"豁免
- 每张图的 prompt 必须显式声明产品占比:`the tiny [类别] occupying only about X percent of the frame height`(X ≤ 档位上限)
- "景别混搭 ≥3 种"规则降为 ≥2 种(因为可选景别窄)

**豁免图类型**(对 XS/S 也豁免):
- 尺寸图(S1 §3)

---

## 五、道具规模硬下限(XS/S 强制)

### 5.1 硬下限表

| 档位 | 硬下限 |
|---|---|
| **XS** | 每张中景/置景图至少 1 件道具视觉体积 ≥ 产品 3 倍,且 prompt 必须显式声明倍数 |
| **S** | 每张中景/置景图至少 1 件道具视觉体积 ≥ 产品 1.5 倍,且 prompt 必须显式声明倍数 |
| M/L/XL | 无下限(道具按真实比例自然存在即可) |

### 5.2 强制倍数声明语言

XS 产品 prompt 必须出现以下结构之一:
- `clearly three to four times taller than the [类别]`
- `clearly four to five times taller than the [类别]`
- `clearly much larger than the [类别]`
- `clearly wider than the [类别] base`
- `dominating the background/composition`

不允许只写"a lamp / a book / a frame"而不声明尺寸关系。

### 5.3 典型"达标道具"候选(按空间)

| 空间 | 达标高点物(≥3倍)| 达标低点物(≥1.5倍)|
|---|---|---|
| 纪念控台 | 大相框/大镜子/台灯 | 硬封书/亚麻叠布/大号托盘 |
| 床头柜 | 正常床头灯/床头板边缘 | 硬封书/杂志/水杯 |
| 窗台 | 整幅窗帘(ceiling to sill) | 硬封书/咖啡杯 |
| 梳妆台 | 大镜子/香水瓶簇 | 化妆盘/折叠布巾 |
| 书桌 | 台灯/书堆/显示器边缘 | 笔记本/马克杯 |

### 5.4 禁用"迷你道具"

XS/S 产品禁止搭配以下道具(会让产品显大):
- 迷你相框 / 迷你蜡烛 / 小镜子
- 小号花瓶 / 小陶罐
- 任何专为小摆件设计的"配件级"物品

---

## 六、尺度顾虑等级(直接挂钩差评风险)

M1 Step 3 判定档位时,同步判定尺度顾虑等级:

| 等级 | 触发条件 | 强制要求 |
|---|---|---|
| **高** | XS 档位 / 好评差评中出现 "small/tiny/bigger than expected" | 全片 ≥4 张尺度证明图(尺寸图 + 尺度参照 + 2 张交互图)|
| **中** | S 档位 / 数据无明确尺度信号 | 全片 ≥2 张尺度证明图(尺寸图 + 1 张交互图)|
| **低** | M/L/XL 档位 | 仅保留 Image_2 尺寸图即可 |

**尺度证明图定义**:画面中包含至少一件公认尺度锚点(手/书/咖啡杯/鸡蛋/台灯)并与产品产生直观对比的图。

---

## 七、XS/S 专属负面词包

所有 XS/S 档位产品的 9 张图(除规格图外)必须在 G1 通用负面词之外追加:

```
no oversized product, no product filling the frame, 
no miniature props, no shrunken surroundings, 
no scaled-down accessories
```

这个负面词包专门对抗 Nano Banana 的"道具陪缩"惯性。

---

## 八、Prompt 组装模板(XS 产品中景/置景图)

```
The exact same [类别] from the reference image, 
[落点] positioned on the [left/right] third of the frame, 
the tiny [类别] occupying only about [≤20] percent of the frame height 
and appearing visibly dwarfed by its surroundings,
[几何骨架],
a [full-size 大物] [站位] behind forming the high point 
and clearly [three to four / four to five] times taller than the [类别],
a [full-size 中物] [站位] forming the low point and clearly wider than the [类别] base,
[边缘虚化物] partially out of frame at the [位置],
clean negative space in the [对角方位] corner,
eye level [角度],
wide shot pulled back to emphasize the intimate keepsake scale,
soft natural window light from the left at 5400K,
soft diffused directional light,
preserving true material colors,
editorial still life photography, shallow depth of field, aspect ratio 1:1,
no text, no watermark, no duplicate subject, no color change to the product,
no oversized product, no product filling the frame, no miniature props, no shrunken surroundings, no scaled-down accessories,
[按叙事面追加的负面词], [按材质追加的负面词]
```

---

## 九、R1 专属审核(M2 Step 9 追加为 9.4 节)

仅对 XS/S 档位的非规格图执行:

| 审核项 | 通过条件 |
|---|---|
| 占比声明 | prompt 中出现 `occupying only about X percent of the frame height`,X ≤ 档位上限 |
| 倍数声明 | prompt 中至少出现 1 次 "times taller/larger/wider than" 或 "dominating" 结构 |
| 景别基线 | 景别在表四的基线范围内 |
| 禁用景别 | prompt 中不含表四禁用景别关键词 |
| 专属负面词包 | 含第七节五连负面词 |
| 尺度证明图数量 | 全片尺度证明图数量 ≥ 第六节等级要求 |

任意一项不通过 → 该图重写(尺度证明数量不足 → 整体重新分配职责)。

---

## 十、与主干文件的接口

| 主干步骤 | R1 介入 |
|---|---|
| **SKILL.md 总原则** | 第 4b 条声明两条决策链分流 |
| **SKILL.md 文件表** | R1 被列为必须调用的共享文件 |
| **M1 Step 3** | 判定尺寸档位后强制调用 R1,将景别基线 / 道具规模下限 / 尺度顾虑等级写入决策包 |
| **M2 Step 6** | XS/S 档位的景别和道具规模决策必须符合 R1 约束,违反即作废 |
| **M2 Step 7** | 预校验追加"景别基线合规 / 道具规模达标 / 尺度证明图数量达标"三项 |
| **M2 Step 9** | 逐图审核追加 9.4 节 R1 专属审核 |
| **G1 第六节** | XS/S 档位写图时强制叠加 R1 的占比声明、倍数声明、负面词包 |

---

## 十一、禁止事项

- 禁止 XS/S 档位绕过 R1 走职责优先链路
- 禁止 XS/S 档位用 medium close-up 或更紧的景别(工艺特写/尺寸图除外)
- 禁止 prompt 缺失占比声明或倍数声明
- 禁止搭配"迷你道具"试图让产品显大
- 禁止因"画面太空"为由把 wide shot 改回 medium shot
- 禁止尺度证明图数量低于尺度顾虑等级要求

---

## 十二、修订记录

v1.0 首版。动因:某 7.5×5cm 掌心纪念骨灰罐的 9 图生成中,执行者反复将产品拍得过大,经 3 轮人工反馈后才拉远。复盘发现根因是尺寸档位在原决策链中只是标签、不产生约束,本文件即为此问题的根治方案。
