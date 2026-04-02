# image-prompt-guide.md（统一修订版）

## 一、核心原则

**image_prompt 的分工：**

| Skill管 | 模型自己知道 |
|---|---|
| 风格气质（色调/材质/光线） | 场景里有什么道具 |
| 色系边界（禁止出现什么颜色/材质） | 道具怎么摆放 |
| 镜头参数（机位/景别/构图） | 空间背景长什么样 |
| 道具存不存在（必须明确写） | 道具具体是哪几件 |

> 你告诉模型 `kitchen coffee corner`，它自己知道有咖啡机、木勺、咖啡豆、橱柜背景。但道具存不存在，必须明确写，不能省。

---

## 二、语言规范（强制）

- **image_prompt 必须全部使用英文输出**
- 禁止中文、禁止中英混写
- 禁止使用标签前缀（"镜头语言："、"场景："、"道具："等冒号结构）
- 写成**自然语言连续描述句**，像摄影师在描述一张照片

---

## 三、image_prompt 推荐结构

按以下顺序写成连续英文句，不加任何标签：

```
[产品描述] placed on [台面材质+家具完整结构],
[场景名称] + [背景关键结构],
[道具：至少1件，全景/中景强制2-3件],
[镜头参数：机位+景别+构图],
[光线规范],
[色系边界约束],
[摄影风格触发词], aspect ratio [比例].
no [负面1], no [负面2], no [负面3].
```

### 示例（A类·厨房咖啡角·中景）
```
A black and white checkerboard ceramic canister with bamboo lid, small canister no taller than a standard drinking glass appearing compact on the marble surface, placed on a white Carrara marble countertop, kitchen coffee corner, light oak cabinetry and warm white walls in background, a wooden scoop and scattered coffee beans on the same surface, shot from slightly above eye level, front-center angle, medium shot, soft diffused natural side window light, preserving true material colors, subtle shadow detail only, no color cast, lived-in cozy feel, no bright colors, no wicker, photorealistic, editorial food photography style, 8K, aspect ratio 16:9. no text, no watermark, no duplicate subject.
```

### 示例（C类·玄关摆件·宽景）
```
A matte black French bulldog sculpture holding a gold tray, small figurine roughly the size of a coffee mug appearing petite on the wide console table, placed on a white marble console table with gold metal legs fully visible, full entryway scene, complete round gold-framed mirror on wall, cream white wall with fine linear molding panels, a small white ceramic vase with dried stem, a thin gold pillar candle, and a folded linen cloth on the same surface, shot from slightly above eye level, front-center angle, wide medium shot, soft diffused natural side window light approximately 5000K, preserving true material colors, subtle shadow detail only, no color cast, no warm amber tone, no bright colors, no rustic elements, photorealistic, luxury interior editorial, 8K, aspect ratio 16:9. no text, no watermark, no duplicate subject.
```

---

## 四、道具规范（强制）

**道具不是可选项，是场景成立的必要条件。**

| 景别 | 道具数量要求 |
|---|---|
| 全景 / 中景 | 强制 2–3 件，必须在提示词中明确点名 |
| 近景 | 1 件即可，可只写产品本身 |
| 特写 / 微距 | 可为 0 件 |

**写法规范：**
- 必须点名道具是什么，例如：`a wooden scoop and scattered coffee beans`
- 只说道具是什么，颜色/材质由风格约束，位置交给模型
- 禁止写模糊描述：`styled with accessories` / `a few decorative items`（模型会忽略）

---

## 四A、花材体量描述规范（B类）

B类花瓶产品的花材体量描述规范见 `R05-vase-flower-guide.md` 第十三节。

---

## 五、镜头参数写法

镜头参数直接写进英文句中，必须包含以下3项：

**① 相机方位**
- `front-center angle` / `left 25-degree angle` / `right 30-degree angle`

**② 机位高度**
- `slightly above eye level` / `at eye level` / `low angle looking up` / `top-down 25-degree`

**③ 景别**
- `close-up shot` / `medium shot` / `wide shot` / `full scene`

---

## 六、光线规范（强制）

**核心原则：产品固有色优先，光影只做轻微层次，不改变产品本身的色彩感知。**

**标准写法：**
```
soft diffused natural side window light, preserving true material colors, 
subtle shadow detail only, no color cast
```

**色温选择（全场景统一规则：最低5000K）：**
- 所有室内家居场景 → 最低 `5000K`，推荐 `5000K–5500K`
- 海岸/自然光场景 → `5500K–6000K`
- 含金色/暖金属道具场景 → 必须 `5500K`，防止金属反光污染环境色
- 黑色产品额外追加：`the subject remains deep matte black with no color contamination`

**防偏黄标准写法（含金色道具场景必加）：**
```
soft diffused neutral-white natural side window light approximately 5500K,
cool neutral daylight, clean white light with no warm bias,
no golden color spill onto surroundings,
no warm tint, no yellow cast, no color cast
```

**严格禁止：**
- 禁止 `dramatic lighting` / `moody light` / `golden hour`
- 产品含金色时，禁止同时叠加 `warm white light` + `3500K` + `warm gold accents`（三者叠加导致整体过黄）
- 禁止光影强度超过产品固有色饱和度的20%

---

## 七、风格触发词规范（强制）

**禁止把风格名称直译为英文写入提示词。**
- 错误：`cold minimal luxury` / `coastal vacation style` / `real home style`
- 正确：使用摄影行业标准触发词

**按产品类型选1组，写在提示词末尾：**

| 产品类型 | 标准摄影触发词 |
|---|---|
| 食品/厨房/储物类 | `photorealistic, editorial food photography style, 8K` |
| 家居摆件/装饰类 | `photorealistic, editorial lifestyle photography, 8K` |
| 轻奢/高端家居类 | `photorealistic, luxury interior editorial, 8K` |
| 花瓶/花艺类 | `photorealistic, editorial interior photography, 8K` |
| 真实居家类 | `photorealistic, editorial home decor photography, 8K` |
| 海岸/度假类 | `photorealistic, coastal lifestyle photography, 8K` |

---

## 八、家具完整结构规范（强制）

场景名称不够，必须写出家具的完整结构，禁止只写台面名称。

| 场景 | 错误写法 | 正确写法 |
|---|---|---|
| 玄关 | `marble console table` | `marble console table with gold metal legs fully visible` |
| 电视柜 | `TV cabinet` | `white TV cabinet with full cabinet body and legs visible` |
| 床头柜 | `nightstand` | `white nightstand with drawer and legs fully visible beside the bed` |
| 茶几 | `coffee table` | `round marble coffee table with metal frame legs fully visible` |

> 只写台面名称，模型会生成悬浮台面，柜体消失。

---

## 九、色系边界约束

Skill 只需规定禁止出现的颜色和材质，具体道具颜色由模型根据场景判断：

**通用禁止（所有风格）：**
`no text, no watermark, no wicker, no bright saturated colors, no patterned tablecloth, no children's toys, no cluttered wires`

**按风格追加：**
- 真实居家风：`no all-white cabinetry, no cold blue light, no showroom feel`
- 轻奢风：`no rough wood grain, no rustic ironwork, no heavy ornamentation`
- 海岸风：`no high saturation, no tourist souvenir style`

---

## 十、产品尺寸说明

产品尺寸感知规则见 `R04-size-profile-guide.md`。

- 模型无法精确执行厘米数字，禁止在提示词中写具体尺寸数值
- M / L 档：写 `true to life scale` 即可
- S 档（≤20cm）：全景/中景必须加相对体量描述，规则见 `R04-size-profile-guide.md` S档专属章节

---

## 十一、比例规则

- 默认固定为 `aspect ratio 16:9`，写在触发词之后
- 用户明确指定其他比例时才覆盖

---

## 十二、后置校验

生成提示词后自查：
1. 是否全英文、无标签前缀
2. 场景名称是否清晰 + 家具结构是否完整
3. 全景/中景是否有 2–3 件道具明确点名
4. 光线是否符合产品固有色优先原则
5. 末尾是否有标准摄影触发词 + 比例声明
6. 产品含金色时是否加了 `no warm amber tone`
7. B类花瓶产品：执行 `R05-vase-flower-guide.md` 第十三节花材体量描述校验
