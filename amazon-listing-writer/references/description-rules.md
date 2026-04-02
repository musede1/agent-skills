> **调用方**：Phase B Step B3（生成Listing初稿）
> **读取时机**：执行Step B3前必须读取本文档

# 长描述规则（Product Description）

## 基本规范

| 指标 | 要求 |
|------|------|
| 最低长度 | 1200字符（含空格） |
| 最高长度 | 1900字符（含空格） |
| 格式 | 纯文本段落，无HTML |
| 段落数 | 5-6段 |
| 段落间隔 | 空行分隔 |

---

## 6段式结构

### 第1段：开篇（情感钩子 + 产品定位）

**占比**：约15%（180-285字符）

**内容要素**：
- 情感共鸣开场（爱情/家庭/美学价值）
- 产品核心定位（品类词 + 题材形状词）
- 设计理念/情绪价值

**写法示例**：
```
Celebrate the beauty of love with this elegant couple statue. This touching resin figurine captures an intimate embrace between two figures, symbolizing deep connection, commitment, and the timeless bond shared between partners. A meaningful decorative piece that brings warmth and romance to any space.
```

**禁止**：
- 夸大词（best/amazing/stunning）
- 未确认的功能宣称
- 竞品比较

---

### 第2段：核心价值（题材/设计/工艺亮点）

**占比**：约25%（300-475字符）

**内容要素**：
- 题材详细描述（姿态/表情/动作）
- 设计特点（线条/造型/艺术风格）
- 核心差异点（来自P0核心特征锚点）

**写法示例**：
```
The sculpture features two figures in a tender embrace, their flowing forms merging harmoniously to create a sense of unity and devotion. The abstract artistic style emphasizes emotion over detail, allowing viewers to project their own stories onto the piece. Smooth curved lines and balanced proportions create visual harmony that draws the eye and invites contemplation.
```

**关键词嵌入**：
- 题材形状词（couple/embrace/figurine）
- 风格词（abstract/modern/minimalist）—仅P1强证据或P0提供

---

### 第3段：规格信息（尺寸/材质/表面工艺）

**占比**：约20%（240-380字符）

**内容要素**：
- 精确尺寸（必须含单位 + approx换算）
- 材质说明（来自P0，不编造）
- 表面工艺（来自P0，不编造）
- 重量（如有）

**写法示例**：
```
This figurine measures approximately 8.5 inches tall, 4 inches wide, and 3 inches deep (21.5 x 10 x 7.5 cm), making it perfectly sized for display without overwhelming your space. Crafted from durable resin material with a smooth matte white finish, the sculpture offers a clean contemporary look that complements various interior styles. Lightweight yet sturdy construction ensures lasting display.
```

**必须遵守**：
- 尺寸数据只能来自P0
- 材质/工艺只写已确认项
- 单位换算标注"approx."或"approximately"

---

### 第4段：场景描绘（摆放场景/空间适配）

**占比**：约20%（240-380字符）

**内容要素**：
- 适合的摆放位置（摆放位置词）
- 适合的空间场景（空间场景词）
- 搭配建议（基于P0真值的低风险建议）

**写法示例**：
```
Display this sculpture on your mantel, bookshelf, nightstand, entryway console, or office desk to add a touch of romance to your environment. The neutral white color palette blends seamlessly with living room, bedroom, or office decor, whether your style is modern, minimalist, or transitional. Its compact footprint allows flexible placement in various settings throughout your home.
```

**空间场景词使用规则**：
- 通用场景可自动生成：living room/bedroom/office/entryway
- 强绑定场景需P0确认：bathroom/outdoor/kitchen
- 优先使用P1强证据场景词

---

### 第5段：礼品价值（适合场合/受众）

**占比**：约15%（180-285字符）

**内容要素**：
- 适合的节日场合（节日场合词）
- 适合的受众人群（受众词）
- 礼品场景词
- 包含物说明（正向表述：有什么写什么）

**S1模式（自用为主）写法**：
```
Whether treating yourself or gifting to someone special, this sculpture makes a thoughtful addition to any home. Its timeless design appeals to art lovers and couples alike, serving as a daily reminder of love and connection.
```

**S2模式（礼品意图）写法**：
```
This couple statue makes an ideal gift for anniversaries, weddings, Valentine's Day, housewarmings, or any occasion celebrating love. Perfect for husbands, wives, newlyweds, engaged couples, or anyone who appreciates meaningful home decor. Comes in protective packaging ready for gifting.
```

**礼盒/包装规则**：
- 有礼盒：写明"Comes in elegant gift box"
- 无礼盒：不提，不写"不含礼盒"
- 有配件：写明包含什么
- 无配件：不提

---

### 第6段：收尾（行动号召/品牌信任）

**占比**：约5%（60-95字符）

**内容要素**（可选，非必须）：
- 简短收尾语
- 品牌承诺（仅在用户提供品牌调性时）

**写法示例**：
```
Add this beautiful piece to your collection and let it tell your story of love.
```

**禁止**：
- 过度营销语言
- 虚假承诺（终身保修/100%满意等）
- 催促购买的压力词

---

## 与五点差异化原则

| 维度 | 五点（Bullets） | 长描述（Description） |
|------|----------------|----------------------|
| 语言风格 | 功能导向、简洁直接 | 叙事性、情感共鸣 |
| 结构 | 分点罗列、大写开头 | 段落流畅、自然过渡 |
| 信息密度 | 高密度、关键词集中 | 适度展开、阅读舒适 |
| 侧重点 | 规格/功能/卖点 | 场景/情感/价值 |

**禁止**：
- 直接复制五点内容
- 简单罗列五点信息
- 重复相同句式

---

## 关键词覆盖策略

长描述中应自然覆盖以下关键词类型：

| 优先级 | 词类型 | 覆盖方式 |
|--------|--------|----------|
| 必须 | 品类词 | 第1段定位 + 第5段呼应 |
| 必须 | 题材形状词 | 第2段详细描述 |
| 必须 | 尺寸规格词 | 第3段精确数据 |
| 必须 | 材质词 | 第3段材质说明 |
| 高 | 摆放位置词 | 第4段场景描绘 |
| 高 | 空间场景词 | 第4段空间适配 |
| 中 | 风格词 | 第2段或第4段自然嵌入 |
| 中 | 受众词 | 第5段礼品价值 |
| 条件 | 礼品场景词 | 第5段（S2模式强化） |
| 条件 | 节日场合词 | 第5段（S2模式强化） |

---

## 合规检查

长描述必须遵守与五点相同的合规规则：

- [ ] 所有尺寸/材质/工艺来自P0
- [ ] 无未经证实的功能宣称
- [ ] 无他人品牌/IP词
- [ ] 无夸大营销词（stunning/exquisite/gorgeous/magnificent/amazing/elegant/premium/luxury/beautiful）
- [ ] 包含物正向表述（有什么写什么）
- [ ] 长度在1200-1900字符区间

---

## 完整示例

```
Celebrate the beauty of love with this elegant couple statue. This touching resin figurine captures an intimate embrace between two figures, symbolizing deep connection, commitment, and the timeless bond shared between partners. A meaningful decorative piece that brings warmth and romance to any space.

The sculpture features two figures in a tender embrace, their flowing forms merging harmoniously to create a sense of unity and devotion. The abstract artistic style emphasizes emotion over detail, allowing viewers to project their own stories onto the piece. Smooth curved lines and balanced proportions create visual harmony that draws the eye and invites contemplation.

This figurine measures approximately 8.5 inches tall, 4 inches wide, and 3 inches deep (21.5 x 10 x 7.5 cm), making it perfectly sized for display without overwhelming your space. Crafted from durable resin material with a smooth matte white finish, the sculpture offers a clean contemporary look that complements various interior styles. Lightweight yet sturdy construction ensures lasting display.

Display this sculpture on your mantel, bookshelf, nightstand, entryway console, or office desk to add a touch of romance to your environment. The neutral white color palette blends seamlessly with living room, bedroom, or office decor, whether your style is modern, minimalist, or transitional. Its compact footprint allows flexible placement in various settings throughout your home.

This couple statue makes an ideal gift for anniversaries, weddings, Valentine's Day, housewarmings, or any occasion celebrating love. Perfect for husbands, wives, newlyweds, engaged couples, or anyone who appreciates meaningful home decor. Comes in protective packaging ready for gifting.

Add this beautiful piece to your collection and let it tell your story of love.
```

**字符统计**：约1750字符（符合1200-1900区间）
