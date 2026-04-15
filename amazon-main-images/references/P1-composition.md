# P1-composition.md 构图规范

> 构图先于道具。骨骼定了画面秩序,道具只是往骨骼上挂肉。
> 本文件定义所有图片的构图规则,由 G1 在写 prompt 时调用。

---

## 一、核心原则

**没有构图骨架,道具摆得再对也乱。**

构图的作用是建立画面秩序,让 9 张图(或 N 张图)作为一组有统一的视觉语言,而不是各画各的。
构图不是摄影师的风格偏好,是工程约束——每张中景图都必须按同一套规则组织画面。

---

## 二、5 条硬约束

### 2.1 主体锚点

- 产品统一放在画面**左 1/3 或右 1/3 的纵向黄金分割线**上
- 全片锁定**一个方向**,9 张图不切换(全部左 1/3 或全部右 1/3)
- 居中构图仅用于尺寸图、特写、俯拍,其他图禁止居中
- **prompt 写法**:`positioned on the right third of the frame`

**为什么**:居中构图视觉死板,且不给道具留呼吸空间。黄金分割线是编辑风静物的默认锚点。

---

### 2.2 几何骨架(每张中景图必选一种)

| 骨架类型 | 特征 | 适用场景 | prompt 写法 |
|---|---|---|---|
| **三角构图** | 高点+产品+低点形成三角 | 最稳,主场景默认 | `triangular composition` |
| **L 形构图** | 一件高物做竖,一件低物做横,产品在交点 | 紧凑空间(玄关/梳妆台) | `L-shaped composition` |
| **对角线构图** | 画面元素沿对角线排布 | 有方向感(阅读角/客厅) | `diagonal composition running from upper-left to lower-right` |
| **放射构图** | 俯拍专用,元素从产品向外散 | 俯拍静物 | `radial composition from top-down view` |

**prompt 写法必须做到**:
1. 显式声明几何类型
2. 指明每个顶点/节点是什么道具

示例:`triangular composition, a tall round mirror forming the high point, a small stack of letters forming the low point`

---

### 2.3 高度层次

每张中景图必须同时包含:

- **高层**:一件明显**高于**产品的物
- **中层**:产品本身
- **低层**:至少一件明显**低于**产品的物

**高点候选**:墙上镜子 / 立着的书 / 高花瓶 / 台灯 / 椅背 / 窗帘上沿 / 床头板
**低点候选**:平放的书 / 托盘 / 折叠布 / 低浅碗 / 散落的小物 / 台面边缘

**反例**:9 张图全是"产品+几件同高度的台面物",画面成一条平线,视觉死。

---

### 2.4 负空间

- 产品**斜对角方向**必须保留一块完整空白(空墙/空台面/空光区)
- 负空间不允许被道具侵占,哪怕是边缘
- **prompt 写法**:`clean negative space in the [upper-left / upper-right / lower-left / lower-right] corner`

**判断标准**:产品在右 1/3 → 负空间在左上;产品在左 1/3 → 负空间在右上。

**为什么**:负空间是"编辑风"和"杂货铺感"的最大分野。道具填满画面 = 廉价感。

---

### 2.5 视线引导

每张图必须有一条**隐性引导线**把观众视线带向产品。引导线来源:

- 台面边缘线
- 光的方向
- 道具的朝向(书本翻开的方向、花枝指向、布料褶皱走向)
- 墙角线 / 家具边缘

**不用在 prompt 里显式写"leading line"**,但选道具时必须想到这条线,让道具的摆放方向自然引向产品。

---

## 三、整片节律

- N 张图**至少覆盖 3 种不同几何骨架**,不允许全片同构图
- 主图默认分布建议:三角 ×3–4 + L 形 ×2–3 + 对角线 ×1–2 + 放射/特写 ×1
- 节律靠**构图类型变化**建立,不靠道具种类变化

---

## 四、豁免规则

| 图类型 | 豁免项 |
|---|---|
| 尺寸图 | 1–5 全豁免,正中心布置 |
| 俯拍图 | 必须用放射或对角线构图 + 负空间 |
| 交互图(手部) | 可豁免第 1 条锚点,其他 4 条仍需遵守 |
| 全景 / 远景图 | 1–5 全豁免,按 G1 §3.7 全景图写法专章执行,只保留"产品在右 1/3 + 大块负空间" |

---

## 五、prompt 组装模板

中景图构图部分的标准写法:

```
[产品锚定句],
positioned on the [left/right] third of the frame,
[triangular / L-shaped / diagonal] composition,
[具体高点物] forming the high point,
[具体低点物] as the low point,
[边缘/虚化物] partially out of frame at the [位置],
clean negative space in the [对角方位] corner,
...
```

**完整示例**:
```
The exact same statue from the reference image,
sitting on a bleached oak entryway console table
positioned on the right third of the frame,
triangular composition,
a tall round mirror on the wall behind forming the high point of the triangle,
a small stack of unopened letters lying flat at the front-left forming the low point,
a folded pair of leather gloves partially out of frame at the lower-right edge,
clean negative space in the upper-left corner,
soft natural window light from the left at 5300K,
...
```

---

## 六、正反例对照

### 正例
三角构图,镜子做高点,折叠信件做低点,手套一半出框,左上留空,台面边缘线从右下指向产品。
→ 画面有骨架、有层次、有呼吸。

### 反例
5 件道具全部完整摆在台面上同一高度,均匀分布在产品周围,每件都清晰可见。
→ 没有高点,没有负空间,没有引导线,视觉平铺,挤且乱。

---

## 七、构图审核(每张中景图必过)

| 审核项 | 通过条件 |
|---|---|
| 主体锚点 | 产品在左 1/3 或右 1/3,全片方向一致 |
| 几何骨架 | 显式声明且每个节点有具体道具 |
| 高度层次 | 高/中/低三层齐全 |
| 负空间 | 斜对角有完整空白 |
| 整片节律 | 9 张覆盖 ≥3 种几何 |

任意一项不通过 → 该图重写。

---

## 八、与 G1 的接口

- G1 写 prompt 时,构图部分**必须调用本文件**的 2.1–2.5 和第五节模板
- G1 的"写法后置审核"追加构图审核(第七节)
- 本文件只管构图,不管道具具体是什么(道具由 G1 第七节决定)、不管风格(由 D2 决定)
