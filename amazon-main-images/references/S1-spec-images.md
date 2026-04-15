# S1-spec-images.md 规格型图片专项规范

> 规格型图片 = 不承载场景叙事、以传递客观信息为目的的图。
> 本文件独立于 G1。G1 负责场景/置景/交互类叙事图。
> M2 Step 8 写图时按职责类型路由:叙事类 → G1,规格类(尺寸图)→ S1。

---

## 一、适用范围

| 职责 | 类型 |
|---|---|
| 尺寸图(Image_2 硬锁) | 尺寸规格 |

---

## 二、共同原则

1. 无场景叙事、无生活道具(尺寸图的参照物除外)
2. 背景统一为中性素底(pale chalk / off-white / light neutral gray)
   - **复合尺寸图豁免本条**:可沿用风格包定义的落点与光线方案,与其他 8 张图视觉统一;但需通过 §3.3a 抢戏自检,未通过则降级为中性素底
3. 光线统一为平均漫射光,避免强方向性阴影
   - 复合尺寸图采用风格包落点时,光线改为风格包对应的自然光方案
4. 产品本体描述仍遵守第一铁律,极简 + `exact same` 前缀 + `no color change to the product`
5. 负面词必须追加 `no lifestyle elements, no environmental props`
6. 规格图**不参与 P1 构图规范**(不走右 1/3,不走几何骨架)
7. 规格图**不执行 G1 §9 视觉哲学审核**(本身就不是摄影叙事)
8. 规格图仍执行第一铁律审核

---

## 三、尺寸图规范

### 3.1 两种形态(二选一)

| 形态 | 适用 |
|---|---|
| **纯净尺寸图** | 默认。小件产品 / 尺寸是核心顾虑 / 参考图仅 1-2 张 |
| **复合尺寸图** | 工艺是核心卖点 / 参考图 ≥3 张 / 副图位置紧张时考虑 |

### 3.2 纯净尺寸图

**强制要求**
- Image_2 硬锁,不可移位
- 产品正侧面视图(最能体现长宽)
- 必须 1 个真实尺度参照物
- 双单位文字标注:英寸 + 厘米
- 测量线描述:`thin clean horizontal/vertical measurement line`
- 字体描述:`crisp sans-serif labels in solid charcoal gray`
- 负面词追加:`no distorted letters, no extra text, no lifestyle elements`

**模板**
```
The exact same [产品类别] from the reference images, shown in clean [side/front] profile view centered on a neutral pale chalk flat background, a [参照物] placed beside it as a real-world scale reference, thin clean horizontal and vertical measurement lines marking the outer dimensions, crisp sans-serif labels reading '[X.X] in / [XX] cm' along the width and '[X.X] in / [XX] cm' along the height in solid charcoal gray, flat even diffused daylight at 5400K, preserving true material colors, product technical reference photography, aspect ratio 1:1, no watermark, no duplicate subject, no color change to the product, no extra text, no distorted letters, no lifestyle elements, no environmental props, [按材质追加的负面词]
```

### 3.3 复合尺寸图(主图 + 细节条)

**前置条件**
- 参考图 ≥3 张(否则退回纯净尺寸图)
- 产品有 ≥3 个真正不同的细节维度
- 细节数量固定为 3 个,排布方式为右侧竖排或上侧横排

**强制要求**
- 主图区占 60-65%,细节区占 35-40%
- 主图区包含完整尺寸标注(双单位 + 测量线)
- 3 个细节 panel 之间用 `thin clean white gutter` 分隔
- 3 个细节必须对应 3 个**真正不同的工艺维度**,禁止同一处不同远近
- 细节 panel 内产品呼吸空间 ≥20%,禁止填满
- 主图区与细节区共用同一落点与同一光线方案(按 §3.3a 决定走风格包落点还是中性素底)
- 负面词追加 `no product color drift between sections, no misaligned grid, no cropped product`

**模板(主图在左,细节在右竖排)**
```
The exact same [产品类别] from the reference images, presented as a composite specification layout on a clean pale chalk off-white background, aspect ratio 1:1,

left section occupies approximately 60% of the frame width: the [类别] shown in clean [side/front] profile view centered vertically with generous breathing space, a thin clean horizontal measurement line below it reading '[X.X] in / [XX] cm' and a thin clean vertical measurement line on its left reading '[X.X] in / [XX] cm', crisp sans-serif labels in solid charcoal gray, small arrow ticks at the line endpoints,

right section occupies approximately 40% of the frame width, divided into three equal square detail panels stacked vertically with thin clean white gutters between them:
top panel: [维度1,描述意图而非外观],
middle panel: [维度2],
bottom panel: [维度3],

all sections sharing identical flat even diffused daylight at 5400K, identical pale chalk background, consistent product color across left section and all three right panels, preserving true material colors, product technical reference photography, shallow depth of field within each detail panel,

no text other than the dimension labels, no watermark, no duplicate subject, no color change to the product, no distorted letters, no extra text, no product color drift between sections, no misaligned grid, no cropped product, no stretched product, no lifestyle elements, no environmental props, [按材质追加的负面词]
```

细节放在上方时把 "right section / stacked vertically" 改为 "top section / arranged horizontally",主图区相应放在 bottom section。

### 3.3a 复合尺寸图落点选择(条件判断)

复合尺寸图的落点需要根据**抢戏自检**决定走哪种方案,不是无条件场景化。

#### 判断顺序(强制)

```
Step 1:默认尝试沿用风格包"全片核心落点"
Step 2:执行抢戏自检(下方三条)
Step 3:三条全部通过 → 使用风格包落点,与其他 8 张图视觉统一
       任意一条触发 → 降级为中性素底(pale chalk / off-white / light neutral gray)
```

#### 抢戏自检三条

| 判断项 | 触发条件 | 触发后果 |
|---|---|---|
| 颜色接近 | 落点主色与产品主色在色相或明度上距离过小,产品会糊在背景里 | 降级 |
| 纹理明显 | 落点有可见纹理(粗木纹、强石纹、布料织纹等),会和产品细节争夺视觉 | 降级 |
| 明度极端 | 落点过亮(纯白易过曝)或过暗(深色边缘丢失) | 降级 |

#### 两种方案的写法差异

**方案 A — 风格包落点(通过自检时)**
- 主图区和细节区共用**风格包定义的落点材质**(如 "pale bleached oak plank with fine tight grain"、"white marble slab with subtle veining")
- 光线采用**风格包的自然光方案**(如 "soft natural window light from the left at 5300K")
- 允许有自然方向性阴影

**方案 B — 中性素底(降级时)**
- 主图区和细节区共用 **pale chalk / off-white / light neutral gray** 中性素底
- 光线采用 **flat even diffused daylight**,无明显方向性阴影
- 沿用 §3.2 纯净尺寸图的背景与光线规范

#### 铁律

- 降级判断必须在写 prompt **之前**完成,禁止"先写了风格包落点再返工"
- 主图区与细节区**必须使用同一方案**,禁止主图区用风格包落点、细节 panel 用素底这种混搭
- 降级到中性素底时,风格包的色温参数仍然生效(保护产品色相)

### 3.4 参照物选择

| 产品尺寸 | 推荐参照物 |
|---|---|
| XS(<10cm) | 硬币 / 钥匙 / 鸡蛋 |
| S(10-20cm) | 咖啡杯 / 苹果 / 手机 |
| M(20-30cm) | 硬封书本 / 纸杯 / 红酒瓶 |
| L(30-50cm) | A4 纸 / 台灯 / 抱枕 |
| XL(>50cm) | 椅子 / 标准门框 |

参照物必须全球公认(禁用地域性物品),且与产品风格兼容。

---

## 四、(已删除)

细节宫格图职责已从 SKILL 中移除,本文件不再承担宫格图规范。

---

## 五、规格图专属审核

| 审核项 | 通过条件 |
|---|---|
| 第一铁律 | 产品描述极简 + exact same 前缀 + no color change |
| 无叙事元素 | 负面词含 no lifestyle elements, no environmental props |
| 背景中性 | 使用 pale chalk / neutral gray 等素底 |
| 光线均匀 | 使用 flat diffused daylight |
| 尺寸图双单位 | 含 in 和 cm |
| 复合尺寸图区块比例 | 主图区 60-65%,细节区 35-40% |
| 复合尺寸图落点判断 | 已执行 §3.3a 抢戏自检,主图区与细节区使用同一方案 |

任意一项不通过 → 该图重写。

---

## 六、与主干文件的接口

- **M1 Step 2**:输出参考图盘点表,决定复合尺寸图是否允许启用(≥3 张参考图)
- **M2 Step 8**:职责路由:规格类(尺寸图)→ S1,叙事类 → G1
- **G1 §3.5 尺寸图段落已删除**,改为引用 S1 §3
- **G1 §9 视觉哲学审核**对规格图豁免
- **P1 构图规范**对规格图豁免
