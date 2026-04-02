> **调用方**：Phase A Step A2（Claude深度分析）
> **读取时机**：执行Step A2前必须读取本文档

# 买家表达提取规则

## 提取目标

从竞品评论中提取**买家对产品的自然称呼和描述方式**，作为Listing撰写的语言风格参考。

**V2.0变更**：本文件替代原`keyword-extraction.md`。不再输出L1-L4锚点词配置和推荐级别（TITLE_PRIORITY等），因为锚点配置由P0真值+人工设定，CRD不参与。

---

## buyer_vocabulary 四类提取

### 类别1：买家怎么称呼这类产品（how_buyers_call_product）

**定义**：买家在评论中自然使用的品类/产品称呼。

**提取规则（Claude执行）**：
- 从评论中识别买家对产品的自然称呼
- 区分正式称呼（如"planter"）和口语化称呼（如"pot"、"face pot"）
- 统计每种称呼的出现频次

**提取示例**：

| 评论原文 | 提取结果 |
|----------|----------|
| "Very cute planter" | planter |
| "Aztec looking pots" | pot |
| "fun abstract flower pot" | flower pot |
| "Picasso like pot" | pot |
| "This flowerpot is so cool" | flowerpot |
| "Abstract Face Planter was nice" | face planter |

**用途**：Phase B可参考买家最常用的称呼，在Description中使用更贴近买家习惯的表达。

---

### 类别2：买家常用的正面描述词（positive_descriptors）

**定义**：买家在正面评论中描述产品的高频形容词/表达。

**提取规则（Claude执行）**：
- 仅从4-5星评论中提取
- 提取的是买家自发使用的描述词，不是产品规格词
- 排除通用词（good, nice, great等太泛的词）

**提取示例**：

| 评论原文 | 提取结果 |
|----------|----------|
| "Very cute! Love the colors!" | cute |
| "Great unique pot" | unique |
| "Fun abstract planter" | fun |
| "This is EVEN cooler in person" | cool |
| "Its colorful, quirky and adds fun" | quirky, colorful |
| "Very nice conversation piece" | conversation piece |
| "Cute and artsy" | artsy |

**用途**：Phase B在撰写Description的情感钩子时，可参考买家自然使用的形容方式。

**⚠️ 限制**：这些词是买家的主观感受，不可当作产品属性写入五点（例如不能写"Our CUTE planter..."，但可以在Description中营造类似氛围）。

---

### 类别3：买家提及的使用场景（scene_mentions）

**定义**：买家在评论中提到的产品摆放位置或使用空间。

**提取规则（Claude执行）**：
- 从全部评论中提取（正面和负面都可能提及场景）
- 包括明确场景词（kitchen, patio）和隐含场景描述（"in front of my window"）

**提取示例**：

| 评论原文 | 提取结果 |
|----------|----------|
| "Will be on display in new plant shelves" | shelf |
| "I can't wait to use it on my patio" | patio |
| "Looks nice in my window" | window |
| "It's on my kitchen counter" | kitchen |
| "Brings a smile in my garden" | garden |

**用途**：listing-writer在Description的场景描绘中，可参考买家真实提及的场景。

---

### 类别4：买家提及的使用方式/用途（use_case_mentions）

**定义**：买家实际如何使用该产品。

**提取规则（Claude执行）**：
- 从全部评论中提取
- 特别注意**非预期用途**（如花盆被用来放厨房用品）

**提取示例**：

| 评论原文 | 提取结果 |
|----------|----------|
| "Put 3 small succulents in it" | succulent |
| "I use it to hold soup spoons and other larger kitchen utensils" | utensil holder |
| "matching aloe plants for us both" | plant (aloe) |
| "choose which plant will go in it" | plant |
| "Gave as a gift" | gift |

**用途**：帮助Phase B了解买家的真实使用场景，可在Description中覆盖。

---

## 底层文本处理工具（脚本辅助）

以下工具函数由crd_preprocessor.py提供，Claude在分析时可参考其预处理结果。

### 文本预处理

```python
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\-\']', ' ', text)
    text = ' '.join(text.split())
    return text
```

### 停用词过滤

```python
STOP_WORDS = {
    "a", "an", "the", "i", "you", "he", "she", "it", "we", "they",
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did",
    "in", "on", "at", "to", "for", "with", "by", "from", "of",
    "and", "but", "or", "so", "very", "really", "just"
}

REVIEW_STOP_WORDS = {
    "bought", "ordered", "received", "arrived",
    "product", "item", "purchase", "amazon", "seller"
}
```

### 同义词合并

Claude在提取buyer_vocabulary时应自动合并同义表达：

```python
SYNONYM_MAP = {
    "planter": ["planter", "plant pot"],
    "pot": ["pot", "pots"],
    "flower pot": ["flower pot", "flowerpot", "flower planter"],
    "hand painted": ["hand painted", "handpainted", "hand-painted"],
    "living room": ["living room", "livingroom", "lounge"],
}
```

---

## 输出格式

```json
{
  "buyer_vocabulary": {
    "how_buyers_call_product": [
      {"expression": "planter", "frequency": 30},
      {"expression": "pot", "frequency": 25}
    ],
    "positive_descriptors": [
      {"expression": "cute", "frequency": 35},
      {"expression": "unique", "frequency": 15}
    ],
    "scene_mentions": [
      {"expression": "kitchen", "frequency": 5},
      {"expression": "patio", "frequency": 3}
    ],
    "use_case_mentions": [
      {"expression": "plant", "frequency": 40},
      {"expression": "succulent", "frequency": 8}
    ],
    "note": "⚠️ 以上词汇仅供表达方式参考，不可作为产品事实来源。"
  }
}
```

---

## 质量要求

| 检查项 | 规则 |
|--------|------|
| 每类别至少输出3个表达 | 不足时标注`"low_data": true` |
| 频次按当前置信度档位的门槛过滤 | HIGH档≥3次，LOW档≥1次 |
| 同义词已合并 | 不出现"pot"和"pots"同时存在 |
| 通用泛词已排除 | 不出现"good", "nice", "great"等 |
| 标注了使用限制 | note字段必须存在 |
