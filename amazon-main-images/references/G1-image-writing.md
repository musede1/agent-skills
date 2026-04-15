# G1-image-writing.md Image_N 描述写法规范

> 本文件定义 Image_1 ~ Image_9 英文描述的写法规则。
> 所有规则服务于 Nano Banana 图生图模式。
> 第一铁律和视觉哲学高于本文件所有其他规则。
> **XS/S 档位产品必须同时叠加 `R1-scale-discipline.md` 的尺度纪律约束。**

---

## 【第一铁律 · 不可豁免】

```
Image_1 ~ Image_9 的英文描述中,产品本体描述必须极简:

· 只允许出现产品类别名(the sculpture / the vase / the figurine 等)
· 禁止任何颜色词、纹理词、造型形容词、工艺形容词
· 禁止任何尺寸词或厘米数字
· 细节/材质类图只能描述"镜头要拍什么属性",不能描述"产品长什么样"
· 尺寸图允许出现尺寸数字与测量线描述

强制锁定:每张图描述的开头必须用
"The exact same [产品类别] from the reference image"
来锁定参考图,防止模型自由创作产品本体。

负面词必须包含 "no color change to the product"。

违反铁律 → 该图强制重写,不可豁免。
```

---

## 【视觉哲学 · 第二最高原则】

```
描述应该让模型像真实摄影师那样工作,不是像修图师那样工作。

主角和配角的关系靠焦点、构图、光线、站位建立,
不靠把配角模糊或缩小来"伪装"主角的重要性。

道具按真实生活大小自然存在,产品按真实尺寸自然存在,
两者在同一画面里以真实的比例共处。

构图上产品始终是视觉中心,道具围绕产品但不越过产品的视觉领地。
```

这是方向,不是死规则。具体怎么落地凭对真实摄影的理解判断。

---

## 一、语言规范

- 必须全英文,禁止中英混写
- 禁止标签前缀(`Product:` / `Scene:` / `Lighting:` 等)
- 写成自然语言连续描述句,像摄影师在描述一张照片
- 用逗号自然连接,避免符号拼接

---

## 二、核心结构

每张图描述大致按以下顺序展开,具体取舍由图类型决定:

```
[1 强制锁定前缀:The exact same [产品类别] from the reference image]
[1b XS/S 档位追加:画面占比声明(详见 6.2b)]
[2 落点 / 环境]
[3 道具陪衬](道具按真实大小自然存在,XS/S 档位含倍数声明)
[4 镜头参数](机位+方位+景别,XS/S 档位景别受 R1 基线约束)
[5 光线](方向+色温+质感)
[5b 镜头语言](浅景深+焦点锁定+前后景分离+背景 bokeh,详见 §六)
[6 摄影触发词](从风格包取)
[7 比例](aspect ratio 1:1)
[8 负面词](通用三项 + 锁定参考图 + 风格专属 + XS/S 档位专属负面词包)
```

各层的具体写法不强制模板,凭真实摄影理解组织语言。

---

## 三、按图类型的写法差异

### 3.1 场景陈列图
完整结构展开,环境层交代真实居家空间,道具按空间识别物自然出现。

**两条加成铁律**(本次场景图必须叠加):
1. **强方向光必写**(详见 §5.2 场景图光线铁律)
2. **产品质感词必写**(详见 §5.4 产品质感词清单)

这两条加成是为了避免场景图陷入"产品扁平 + 整图均匀光"的常见塌陷,**任何场景图缺一即重写**。

**不要做的事**(踩过的坑,留作警示):
- ❌ 不要硬锁景别(wide / medium 由产品和房间真实拍摄逻辑自由判断)
- ❌ 不要规定"房间元素 ≥N 件"(数量不是关键,真实感才是)
- ❌ 不要"先建房间再放产品"的反向 prompt 结构(产品锚定句仍然放在最前)
- ❌ 不要 focus locked + 全背景 blur(会让产品孤立,空间感塌掉)
- ❌ 不要为了 60-30-10 硬塞"呼应色锚点"(产品色彩强时禁止凑呼应物,详见 D2 §三 60-30-10 隐式判断)

### 3.2 借景型置景
借窗帘/门框/桌面等元素,不交代具体房间,道具极简或无。

### 3.3 材质背景置景 / 自然元素置景
只写背景材质或自然物,不写空间。

### 3.4 (已删除)
近景工艺图职责已从 SKILL 中移除,G1 不再承担工艺类叙事图的写法规范。

### 3.5 尺寸图(已迁移)

尺寸图规范已迁移至 `S1-spec-images.md` §3。M2 Step 8 按职责路由,此处不再重复。

### 3.6 交互图
人物描述限于必要部位(a hand / two hands),禁止全身/面部描述。
负面词追加 `no full body, no face details`。

**XS/S 档位交互图**:手部和前臂必须占画面主导地位,产品占比 ≤22%,详见 6.2b。

---

## 四、镜头参数

每张图必须包含:
- 机位高度(slightly above eye level / at eye level / low angle / top-down 等)
- 相机方位(front-center / left 25-degree / three-quarter rear 等,**仅正面型产品禁止后角**)
- 景别(extreme close-up / close-up / medium shot / wide shot 等)

**景别按图类型自由判断**,根据产品大小、房间空间、拍摄目的灵活选择,不预设硬绑定。

**XS/S 档位景别约束**:必须在 R1 §四的基线范围内,禁用景别关键词不得出现。详见 6.2b。

---

## 五、光线写法

### 5.1 必写参数
- 光源类型(natural window light / diffused daylight)
- 方向(from the left / right / behind)
- 色温(从风格包取,K值与风格包一致)
- 质感(soft diffused / directional)
- 自然色保护(preserving true material colors / no color cast)

### 5.2 场景图光线铁律(强方向光)

**场景陈列图必须使用强单侧方向光,不允许"均匀漫射光填满房间"**。这是立体空间感的物理基础,**没有方向光的场景图就是贴纸**。

prompt 中必须**显式声明三件事**:

1. **主光从哪一侧进入**:`strong directional sunlight from the [left / right / behind-left] window`
2. **明确的投影描述**:`casting defined diagonal shadows across the [家具] and the floor`
3. **暗部描述**:`the [opposite side of the room / far corner] remaining in soft natural shade`

**完整模板**:
```
strong directional sunlight pouring through the [window位置] from the [left/right] at [色温]K, 
casting defined diagonal shadows across the [家具] and the floor, 
the [opposite side] remaining in soft natural shade, 
creating clear contrast between the brightly lit [产品所在区域] and 
the gently shaded [背景区域]
```

**禁用的均匀光描述**(写了即重写):
- `filling the room with light`
- `crisp clean light filling the space`
- `evenly lit`
- `bathing the entire space in soft glow`
- `bright soft light throughout the room`

**适用范围**:本铁律仅适用于**场景陈列图**(主场景 / 次场景 / 礼品场景 / 节庆场景 / 场景内交互图)。
**不适用于**:
- 借景型置景(光线服从置景目的,可逆光可侧光)
- 尺寸图(必须均匀漫射光)
- 双手捧持类纯交互特写(光线服从产品质感呈现)

### 5.3 禁用
- dramatic lighting / moody light / golden hour
- warm yellow tone / amber glow
- studio strobe / harsh shadow

### 5.4 产品质感词清单(场景图必写)

**仅有方向光不够**,还必须显式描述"光在产品身上做了什么",否则产品仍然会扁平。
场景图的产品锚定句和光线描述里,必须包含**至少 3 项**以下质感词,组合使用:

**A 组 · 光对产品的雕刻**(至少选 1 项)
- `wrapping around the [产品] and creating bright crisp highlights along the [表面特征]`
- `the light catching the [表面纹理 / 边缘 / 曲面]`
- `directional light grazing the [表面] revealing its [texture/contour/depth]`

**B 组 · 光穿透产品**(透明 / 半透产品必选)
- `the light passing through the [产品颜色部位] making it glow luminously from within`
- `backlighting the entire [产品] making the [颜色] glow like translucent gemstone`
- `light passing through revealing internal depth and layered character`

**C 组 · 产品在台面上的投影**(必选 1 项)
- `a soft defined cast shadow falling from the [产品] across the [台面] to the [方向]`
- `casting a clear directional shadow on the [台面]`

**D 组 · 锐利质感词**(必选,放在 `preserving true colors` 之后)
- `with sharp surface detail`
- `visible reflections`
- `clear internal depth`
- `crisp highlights`

**E 组 · 防扁平负面词**(必加)
- `no flat product surface`
- `no flat lighting`
- `no overexposure`
- `no evenly lit room`

**完整组合示例**(场景图产品段落):
```
the exact same [产品] from the reference image, [位置]..., 
[A 组] strong directional sunlight pouring through the window from the left at 5500K wrapping around the vase and creating bright crisp highlights along the swirled surface,
[B 组] the light passing through the lower mint green portion making the glass glow luminously from within,
[C 组] a soft defined cast shadow falling from the vase across the oak table to the right,
[D 组] preserving the true [colors] with sharp surface detail visible reflections and clear internal depth,
...
[E 组负面词]: no flat product surface, no flat lighting, no overexposure, no evenly lit room
```

**适用范围**:
- 场景图(主场景 / 次场景 / 礼品场景 / 节庆场景 / 场景内交互图)→ **必写**
- 借景型置景 → 必写(光是置景的核心)
- 尺寸图 → **豁免**(规格图用均匀漫射光)
- 双手捧持类纯交互特写 → 必写(本来就是质感证明图)

---

## 六、镜头语言(浅景深 · 主体隔离)

> 本节执行 SKILL §二 H13 / H14 / H15 三条硬约束,违反任意一条 → 该图重写。
> 本节与 §五 光线写法并列,共同构成"视觉捕捉层"规范。

### 6.1 默认镜头配置(全品类硬锁)

除 Image_2 尺寸图外,所有 Image_N 必须**逐字**包含以下四件事,任意一项缺失或降级即重写:

```
shot with an 85mm telephoto lens at a wide open aperture of f/2.0,
shallow depth of field with crisp tack-sharp focus locked on the [产品类别],
strong foreground-background separation,
the background dissolving into soft creamy bokeh of [色调/光线] shapes
without revealing specific details
```

四件事的强度说明:

1. **镜头焦段 + 光圈(H13 硬锁)**:85mm + f/2.0 是全品类唯一合法基线。**不允许**以"画面需要"、"空间狭窄"、"产品特写"、"近景演示"等理由偏离。类型 2 手部交互允许 50mm,这是唯一的例外。详见 §6.3。
2. **焦点锁定(H14)**:`crisp tack-sharp focus locked on the [产品类别]`,类别名仍受第一铁律约束,只写 `the sculpture / the figurine / the vase` 等,不写颜色/纹理/造型。
3. **前后景分离(H14)**:`strong foreground-background separation`,逐字写。
4. **背景 bokeh 描述(H15)**:把原本想写的背景道具**全部**改写成"化作 bokeh 形状",**不写具体物件名**。违反这一条是上一版 9 图降级的主要原因。详见 §6.2 和 §6.4。

### 6.2 背景 bokeh 句式(H15 详解)

**违反 H15 的典型写法**(每一件道具都给出了具体名字+材质+形态+位置):

❌ `a tall floor lamp with a linen shade visible behind forming the upper-left anchor`
❌ `a folded chunky cream wool throw draped over the arm of the sofa partially out of frame at the left edge`
❌ `a small dark olive potted fiddle leaf in the far background-left corner`

这种写法会让模型把每一件道具都拍清晰,然后在结尾 `rendered as soft bokeh shapes` 是无效对冲,前面写得越具体,模型越不相信"bokeh"。

**符合 H15 的正确写法**(背景只交代色调 + 形状类型 + 光线倾向,不给具体物件名):

✓ `the entire background of the living room dissolving into soft creamy bokeh of warm cream wall tones and pale oak furniture shapes without revealing specific details`
✓ `the background rendered as a soft warm bokeh wash of out-of-focus interior tones without any identifiable props or architectural features`
✓ `the far wall and furniture reduced entirely to atmospheric bokeh of cream and muted oak tones`

**核心判断标准**:读一遍你写的背景句,如果能在脑海里具体画出几件道具(灯、毯子、植物、书),就是违反 H15;如果脑海里只浮现出"一片奶油色暖调的模糊影子",就是合规。

### 6.3 按图类型的硬锁镜头配置(执行 SKILL H13)

**硬锁不是建议,不允许以"画面需要"为由微调。** 以下是全品类唯一合法配置:

| 图类型 | 硬锁焦段 | 硬锁光圈 | 执行规则 |
|---|---|---|---|
| 场景陈列图(主/次/礼品/节庆) | **85mm** | **f/2.0** | 不可偏离 |
| 类型 1 人物场景交互 | **85mm** | **f/2.0** | 追加 `no sharp face details` |
| 类型 2 手部场景交互 | **50mm 或 85mm 二选一** | **f/2.0** | 50mm 用于手部+产品近距离同框 |
| 类型 3 手部特写交互 | **85mm** | **f/2.0** | 不可偏离 |
| 借景型置景 | **85mm** | **f/2.0** | 不可偏离 |
| 尺寸图(Image_2) | **豁免** | **豁免** | S1 §3 强制 flat even diffused daylight |

### 6.4 禁止事项(执行 SKILL H13)

- **禁止写 f/2.5 / f/2.8 / f/4**(光圈每小一档,虚化强度减半;f/4 = 上一版视觉效果的 1/4)
- **禁止写 35mm / 50mm(类型 2 除外)/ 70mm / 100mm / 135mm**(焦段偏离基线 = 空间压缩感不一致,9 张图拍起来不像一套)
- **禁止写 macro / extreme close-up + 50mm 以下焦段组合**(近距离+短焦 = 背景清晰,浅景深归零)
- **禁止以"工艺近景需要微距"为由突破基线**(工艺组已从 SKILL 移除,不存在这类豁免)

### 6.5 与场景图光线铁律的关系

- §5.2 场景图强方向光铁律**仍然生效**,两条规则叠加而非互斥
- 浅景深处理的是"空间如何虚化",强方向光处理的是"产品身上的光"
- 两条一起写的效果:产品在强方向光下清脆锐利 + 背景化成暖色 bokeh = 商业编辑风的标准视觉

### 6.6 XS/S 档位的镜头语言叠加

XS/S 档位的尺度纪律(R1)和本节镜头语言不冲突,两者叠加执行:
- R1 要求产品占画面小(≤20% / ≤30%)
- 本节要求前景产品清晰,背景化成 bokeh
- 叠加结果:产品占画面小但在前景清晰,背景大面积化成 bokeh,观感是"小主体 + 浅景深强制聚焦"
- R1 要求的景别基线(wide shot pulled back)与本节默认 85mm 长焦兼容,长焦拉远即可同时满足

---

## 七、构图规范

**构图规则已独立成文件,见 `P1-composition.md`。**

G1 写 prompt 时,构图部分必须调用 P1 的 5 条硬约束和 prompt 组装模板。
G1 的写法后置审核(第十节)同时追加 P1 的构图审核。

---

## 八、道具规范

**核心原则:道具不是装饰,是替这张图干活的。**
道具的存在是为了完成转化任务,缺哪个补哪个,不是为了"看起来不空"。

### 7.1 道具的 6 项转化任务

| 这张图要干的活 | 必须有的道具类型 |
|---|---|
| 证明大小(尺度锚点) | 1 件公认尺度物(咖啡杯/书/手) |
| 证明能融入家(空间归属) | 该空间的定义性识别物 + 1–2 件辅助物(详见第八节) |
| 证明怎么用(用法演示) | 使用状态道具(钥匙/糖果/花/水) |
| 证明价位档次(品质同盟) | 同档次材质陪衬(大理石/亚麻/黄铜/真花) |
| 证明是真人拍的(真实感) | 任意 1–2 件失焦环境物 |

### 7.2 按景别的填法逻辑(强制)

不同景别画面里"非产品区域"的占比不同,填法逻辑完全不同,**不能混用**。

| 景别 | 画面构成 | 道具填法 |
|---|---|---|
| **近景** | 产品占大半 + 一小块边缘环境 | **1 件低存在感陪衬**,或背景边缘暗示物 |
| **中景** | 产品占 1/3 ~ 1/2 + 一小块环境切片 | **3–5 件精选道具**,每件必须承担 7.1 中至少一项任务,少而精 |
| **中景偏广 / 全景** | 产品 + 一整个真实空间 | **还原真实空间**,该有什么放什么,堆得越像真实生活越好,少了反而假 |

### 7.2b XS/S 档位的景别豁免与道具规模硬约束(R1 镜像)

**XS 产品(<10cm)**:
- **禁用"中景"档位的填法逻辑**(3-5件精选道具),即便职责写"中景"也必须按 wide shot 档位填
- 每张图画面内必须至少有 1 件道具在 prompt 里显式写明"clearly N times taller/wider/larger than the [类别]",**N ≥ 3**
- 基线景别关键词:`wide shot pulled back` / `medium wide shot`
- 产品锚定句后必须追加画面占比声明:
  `the tiny [类别] occupying only about X percent of the frame height`(X ≤ 20)
- 禁止搭配"迷你道具"(详见 R1 §五)

**S 产品(10-20cm)**:
- 同上,但 **N ≥ 1.5**,占比 ≤ 30%

**M/L/XL 产品豁免本条**,按 7.2 正常填法。

### 7.3 中景图铁律(事故高发区,M/L/XL 档位适用)

中景是 9 张图里**唯一会出错的景别**,因为它夹在"特写零道具"和"全景堆满"中间,容易被当成"半个特写"处理,一不留神就空场。

> **中景图严禁零道具。**
> **中景图必须至少承担 7.1 中"空间归属""价位档次""真实感"中的一项,并配置对应道具。**
> **借景型置景、交互图、次场景陈列即使采用中景,同样适用本条。**
> **XS/S 档位已在 7.2b 中禁用中景填法,本条对其不适用。**

### 7.4 道具具体内容来源

- 道具材质类别 → 由风格包"材质白名单 + 道具方向"约束
- 道具具体物件 → 场景图按空间识别物清单(第八节);置景/交互图按 7.1 任务倒推
- 道具档次 → 必须与产品价位锚定一致(轻奢品类配大理石黄铜,自然品类配亚麻干枝)

---

## 九、空间识别物清单(场景图必查)

每个空间都有"定义性识别物"和"辅助识别物"。
场景图必须让定义性识别物占据画面足够的视觉权重,不能只放角落。

### 常见空间的识别物方向

| 空间 | 定义性识别物 | 辅助识别物 |
|---|---|---|
| 梳妆台 | 大镜子(主导背景) | 香水瓶 / 化妆刷罐 / 口红 / 戒指碟 |
| 床头柜 | 床头灯 + 床头板边缘(暗示床) | 闹钟 / 折角的书 / 水杯 |
| 玄关控台 | 大镜子或挂架 + 钥匙托盘 | 折叠围巾 / 单只手套 / 信件 |
| 餐边柜 | 玻璃醒酒器 + 红酒杯 | 银烛台 / 折叠餐巾 |
| 书桌 | 笔记本电脑/大叠书 | 笔筒 / 台灯 / 笔记本 |
| 客厅边几 | 沙发边角(暗示客厅) | 杂志 / 蜡烛 / 茶杯 |
| 纪念控台 | 大相框(黑白家庭照) + 台灯 | 硬封书/亚麻叠布/干枝 |

### 道具与材质白名单的两层关系

```
风格包的"材质白名单" = 允许出现的材质类别(陶瓷/木/亚麻/...)
空间识别物清单 = 该空间应该出现的具体物件(梳妆台必须有香水)

两层是 AND 关系:具体物件必须既符合材质白名单,又是该空间的识别物。

万能道具(陶瓶/书/亚麻布等)不属于任何具体空间的识别物。
万能道具只能出现在置景图里,禁止出现在场景图里冒充空间识别物。

判断标准:这个道具是否"只能"出现在这个空间?
  · 香水瓶 → 只能出现在梳妆台/卫浴 → 是梳妆台识别物
  · 闹钟 → 只能出现在床头柜/书桌 → 是床头柜/书桌识别物
  · 陶瓶 → 任何空间都可以 → 不是任何空间的识别物 → 场景图禁用
```

---

## 十、负面词

### 9.1 通用必加(每张图)
```
no text, no watermark, no duplicate subject, no color change to the product
```

### 9.2 按图类型追加
- 尺寸图:`no extra text, no distorted letters`
- 含金元素产品:`no warm yellow cast, no amber tone, no gold light pollution`
- 人物交互图:`no full body, no face details`
- 镜面材质产品:`no overexposed highlights`
- 仅正面型产品:`no rear view, no side back angle`
- **XS/S 档位产品(所有非规格图)**:
  ```
  no oversized product, no product filling the frame,
  no miniature props, no shrunken surroundings,
  no scaled-down accessories
  ```

---

## 十一、视觉哲学审核(每张图必过)

**写完一张 Image_N 后,执行者必须对自己提一遍以下三个问题:**

```
1. 这张图里的产品和道具,是不是按真实生活大小自然共处?
   还是我用了什么手段把道具弱化/缩小/模糊?

2. 产品的主角地位,是不是靠焦点、构图、光线、站位建立的?
   还是靠把其他东西藏起来才显得重要?

3. 真实的摄影师在拍这张图时,会这样描述吗?
   还是只有修图师才会这样写?
```

任意一个问题答案是"不是真实摄影做法" → 该图必须重写。

这不是死规则,是判断方向。执行者凭对真实摄影的理解判断,
不是逐字检查描述里有没有特定单词。

---

## 十二、写法后置审核(每张图必过)

| 审核项 | 通过条件 |
|---|---|
| 第一铁律 | 产品本体描述极简,有"exact same"前缀,有"no color change"负面词 |
| 视觉哲学(三问) | 三个问题全部答"是真实摄影做法" |
| 全英文 | 无中英混写 |
| 无标签前缀 | 无 Product: / Scene: 等 |
| 镜头参数完整 | 含机位+方位+景别 |
| **场景图-强方向光** | **场景图 prompt 含主光方向 + 投影描述 + 暗部描述(详见 §5.2)** |
| **场景图-产品质感词** | **场景图 prompt 含光对产品的雕刻描述(高光/透射/投影)+ 锐利质感词(详见 §5.4)** |
| 光线参数完整 | 含光源+方向+色温+质感+自然色保护 |
| **镜头语言-焦段光圈(H13)** | **prompt 含逐字 `85mm` 或类型2允许的 `50mm` + 逐字 `f/2.0`,不允许 f/2.5/2.8/4(规格图豁免)** |
| **镜头语言-焦点锁定(H14)** | **prompt 含 `focus locked on the [类别]` 结构(规格图豁免)** |
| **镜头语言-前后景分离(H14)** | **prompt 含 `strong foreground-background separation`(规格图豁免)** |
| **镜头语言-背景 bokeh(H15)** | **背景句只写色调+形状+光线倾向,不含任何具体道具名+材质+位置(规格图豁免)** |
| **镜头语言-规格图豁免** | **Image_2 尺寸图不含上述任意一项(含即违规)** |
| 摄影触发词 | 与风格包一致 |
| 比例声明 | 含 `aspect ratio 1:1` |
| 负面词 | 含通用四项 + 必要追加项 |
| 空间识别物 | 场景图含定义性识别物 |
| 叙事面合规 | 仅正面型无后角 |
| **尺度纪律-占比声明(XS/S)** | **prompt 中含明确占比声明,X ≤ 档位上限** |
| **尺度纪律-倍数声明(XS/S)** | **prompt 中至少 1 件道具含显式倍数或 dominating 结构** |
| **尺度纪律-景别基线(XS/S)** | **景别在 R1 §四基线内,禁用景别未出现** |
| **尺度纪律-专属负面词(XS/S)** | **含 R1 §七五连负面词** |

任意一项不通过 → 重写。
