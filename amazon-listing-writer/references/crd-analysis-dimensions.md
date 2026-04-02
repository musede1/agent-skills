> **调用方**：Phase A Step A2（Claude深度分析）
> **读取时机**：执行Step A2前必须读取本文档

# 5大分析维度详解

本文档详细说明每个分析维度的提取规则和输出要求。

V2.0变更：从8大维度精简为5大维度，删除了关键词库（原维度1）、场景词库（原维度4）、差异化机会（原维度7），相关有用内容已并入buyer_vocabulary和痛点分析。

---

## 通用性过滤规则（所有维度共用）

**此规则适用于下述所有5个维度的输出。**

所有变体的评论合并为单一池分析。每个洞察（卖点主题/痛点主题/问答主题）纳入输出的条件：

**满足任一即可纳入：**
- **条件A**：该洞察出现在 **≥2个变体** 中（通过`cross_variant_count`字段判定）
- **条件B**：该洞察的总提及数 **≥3条**（绝对数兜底）

**两条件都不满足 → 自动丢弃，不纳入输出。**

`型号`字段的作用：统计每个洞察在哪些变体中出现过，计算`cross_variant_count`。

---

## 小样本动态阈值（所有维度共用）

| 评论总数 | 置信度 | 频次门槛 | 痛点严重判定 | 礼品HIGH触发 |
|---------|--------|---------|-------------|-------------|
| ≥100条 | HIGH | ≥3次 | 百分比驱动（evidence_rate≥5%=HIGH） | gift_rate ≥ 20% |
| 50-99条 | MEDIUM | ≥2次 | 双重验证（evidence_rate≥3% 且 ≥5条=HIGH） | gift_rate≥15% 或 绝对数≥10条 |
| 20-49条 | LOW | ≥2次 | 绝对数驱动（≥3条=存在信号，≥5条=较强信号） | 绝对数≥5条 |
| 10-19条 | VERY_LOW | ≥1次 | 仅定性描述，不做定量结论 | 绝对数≥2条，标LOW_CONFIDENCE |
| <10条 | INSUFFICIENT | ≥1次 | 仅列原文摘要，不做分析结论 | 不判定 |

**尺寸/材质痛点特例**：涉及误购风险的痛点（尺寸误解、材质误解、数量误解）在任何样本量下都标注为HIGH。

---

## 维度1：正面卖点提炼

### 辅助角色

角色3：表达方式参考库

### 目的

从正面评论中提炼买家认可的方向，作为五点和Description的**语言参考**，而非产品事实来源。

### 提取规则（Claude执行）

#### Step 1: 筛选正面评论

```
筛选条件: 星级 >= 4
```

#### Step 2: 主题聚类

Claude语义理解驱动，识别以下常见卖点主题方向：

| 主题方向 | 示例买家表达 |
|----------|-------------|
| 外观/设计 | "so cute", "unique", "cool looking", "conversation piece" |
| 尺寸满意 | "perfect size", "good size" |
| 材质/质感 | "solid", "well made", "quality" |
| 包装/开箱 | "well packaged", "gift ready" |
| 礼品反馈 | "great gift", "she loved it" |
| 性价比 | "worth the price", "great value" |
| 实用性 | "great drainage", "holds utensils" |
| 装饰效果 | "gets compliments", "adds personality" |

注意：Claude不限于上述主题，应根据评论内容灵活识别。

#### Step 3: 通用性过滤

每个卖点主题必须通过通用性过滤（≥2变体 OR ≥3条）才能纳入输出。

#### Step 4: 提取代表性引用

- 每主题最多3条引用
- 优先选择`赞同数`高的评论
- 引用长度20-100字符

### 输出格式

```json
{
  "id": "SP001",
  "theme": "外观/设计吸引力",
  "theme_en": "Visual Appeal",
  "summary": "买家普遍认为设计独特、有个性",
  "evidence_count": 45,
  "cross_variant_count": 4,
  "representative_quotes": [
    {
      "text": "This is EVEN cooler in person",
      "rating": 5,
      "helpful_votes": 0
    }
  ],
  "buyer_expressions": ["cute", "unique", "cool", "fun", "quirky"],
  "listing_suggestion": {
    "role": "表达参考",
    "suggested_angle": "可参考买家常用的描述方式：cute, unique, fun",
    "note": "仅供语言风格参考，产品事实必须来自P0真值"
  }
}
```

### ⚠️ 注意事项

**代表性引用和buyer_expressions仅作为表达参考，不可作为产品事实来源。**

Listing中的所有事实性描述必须来自用户提供的P0真值，而非竞品评论。

---

## 维度2：负面痛点警示

### 辅助角色

角色1：预期管理顾问

### 目的

1. 合规风控：避免虚假承诺
2. 预防差评：在Listing中主动管理预期
3. 确定P0真值中哪些字段需要优先、醒目地展示

### 提取规则（Claude执行）

#### Step 1: 筛选含负面信号的评论

```
主要来源: 星级 <= 2
辅助来源: 星级 = 3 且内容含明确不满表达
辅助来源: 星级 = 4-5 但内容含"but"/"wish"/"only"等转折不满
```

注意：Claude应识别高星评论中的隐含不满，例如：
- "5★: Very cute! **Wish they had more sizes**" → 尺寸痛点信号
- "4★: Love it, **but smaller than expected**" → 尺寸痛点信号

#### Step 2: 主题聚类

Claude语义理解驱动，识别以下常见痛点主题方向：

| 痛点方向 | 典型表达（关键词无法完全覆盖的隐含表达） |
|----------|----------------------------------------|
| 尺寸误解 | "I had it pictured larger in my mind", "no measurements" |
| 材质失望 | "looks a little bit too plastic", "feels cheap" |
| 颜色偏差 | "darker and muddier than in all the pictures" |
| 做工/质量 | "the black paint came off", "very poorly made" |
| 气味问题 | "had a foul odor" |
| 价格不值 | "super small for the price", "way to small for $30" |
| 图片误导 | "pictures are misleading", "does not look like photograph" |

#### Step 3: 通用性过滤

每个痛点主题必须通过通用性过滤（≥2变体 OR ≥3条）才能纳入输出。

#### Step 4: 严重程度判定（动态阈值）

**误购风险痛点（尺寸误解/材质误解/数量误解）：任何样本量下都标注HIGH。**

其他痛点按评论基数动态判定：

| 评论基数 | HIGH | MEDIUM | LOW |
|---------|------|--------|-----|
| ≥100条 | evidence_rate≥5% | 2-5% | <2% |
| 50-99条 | evidence_rate≥3% 且 ≥5条 | ≥3条 | <3条 |
| 20-49条 | ≥5条 | ≥3条 | <3条 |
| 10-19条 | — | — | — |
| <10条 | 不判定severity | | |

### 输出格式

```json
{
  "id": "NP001",
  "theme": "尺寸误解",
  "theme_en": "Size Misunderstanding",
  "summary": "大量买家反映产品比预期小，图片缺乏尺寸参照",
  "evidence_count": 15,
  "cross_variant_count": 3,
  "severity": "HIGH",
  "severity_reason": "涉及误购风险，且跨3个变体出现",
  "representative_quotes": [
    {
      "text": "Much smaller than I thought",
      "rating": 2,
      "helpful_votes": 1
    }
  ],
  "root_causes": ["图片缺乏参照物", "尺寸信息不醒目", "产品本身偏小"],
  "compliance_warning": "必须在五点明确标注尺寸，提供参照物描述",
  "listing_action": {
    "required": true,
    "priority": "P0真值中的尺寸字段必须优先、醒目展示",
    "suggested_approach": "Bullet中用参照物对比写清尺寸"
  }
}
```

### HIGH级别痛点的Listing处理

所有`severity: HIGH`的痛点，Phase B Step B3在撰写五点时必须有对应的预期管理措辞。这不是"要不要写"的问题，而是"怎么写得既诚实又不劝退买家"的问题。

---

## 维度3：礼品意图信号

### 辅助角色

角色2：S2触发信号

### 目的

检测竞品买家的礼品意图强度，作为S2模式触发的**辅助依据之一**。

⚠️ 本维度输出为`suggest_s2_mode`（建议），而非`trigger_s2_mode`（触发）。S2模式的最终决定需结合P0和P1数据综合判定。

### 检测规则（Claude执行）

#### Step 1: 礼品意图识别

Claude从全部评论中识别礼品相关信号，包括但不限于：

| 信号类型 | 示例表达 |
|---------|---------|
| 直接提及gift/present | "bought as a gift", "best Christmas present" |
| 赠送行为描述 | "bought more for a friend", "gave to friends" |
| 收礼反馈 | "she loved it", "my friend loves it" |
| 礼品场合 | "birthday", "Christmas", "housewarming" |
| 礼品对象 | "for my mom", "for a plant lover friend" |

注意：Claude应识别隐含赠送意图，不仅限于包含"gift"关键词的评论。

#### Step 2: 统计与分类

- `gift_mention_count`：包含礼品信号的评论总数
- `gift_mention_rate`：gift_mention_count / 有效评论总数
- `gift_recipients`：礼品接收对象频次统计
- `gift_occasions`：礼品场合频次统计

#### Step 3: 置信度判定（动态阈值）

| 评论基数 | HIGH置信度条件 | MEDIUM条件 | LOW条件 |
|---------|---------------|-----------|---------|
| ≥100条 | gift_rate ≥ 20% | 10-20% | <10% |
| 50-99条 | gift_rate≥15% 或 绝对数≥10条 | gift_rate≥8% 或 ≥5条 | 其他 |
| 20-49条 | 绝对数≥5条 | 绝对数≥3条 | <3条 |
| 10-19条 | 绝对数≥2条（标LOW_CONFIDENCE） | ≥1条 | 0条 |
| <10条 | 不判定 | | |

### 输出格式

```json
{
  "gift_intent_signal": {
    "detected": true,
    "confidence": "MEDIUM",
    "gift_mention_count": 15,
    "gift_mention_rate": 0.103,
    "gift_keywords": {
      "gift": 8,
      "friend": 5,
      "christmas": 2,
      "birthday": 1
    },
    "gift_recipients": {
      "friend": 8,
      "mom/mother": 3,
      "daughter": 2
    },
    "gift_occasions": {
      "christmas": 2,
      "birthday": 1,
      "general gifting": 12
    },
    "recommendation": {
      "suggest_s2_mode": true,
      "confidence_reason": "gift_mention_rate=10.3%，在MEDIUM档评论基数下达到辅助建议阈值",
      "note": "此为辅助信号，S2模式最终决定需结合P0产品真值和P1关键词库综合判定"
    }
  }
}
```

---

## 维度4：尺寸/材质关注点

### 辅助角色

角色1：预期管理顾问

### 目的

分析买家对尺寸和材质的敏感程度，确定P0真值中哪些字段需要优先、醒目地展示。

### 分析内容（Claude执行）

#### 尺寸敏感度

Claude从全部评论中统计尺寸相关提及，包括显性表达（"too small"）和隐性表达（"I had it pictured larger"）。

输出：
- `size_total`：尺寸相关提及总数
- `size_positive` / `size_negative` / `size_neutral`：按情感分类
- `size_sensitivity_score`：敏感度评分（0-10）

**敏感度评分规则**：

| 评分 | 条件 | Listing处理建议 |
|------|------|----------------|
| 8-10 | 负面尺寸提及占总评论≥10% | 尺寸信息必须在Bullet 1-2最醒目位置 |
| 5-7 | 负面尺寸提及占总评论5-10% | 尺寸信息必须在Bullet中清晰展示 |
| 3-4 | 负面尺寸提及占总评论2-5% | 尺寸信息在Bullet中正常展示 |
| 0-2 | 负面尺寸提及<2% | 尺寸可在Description中提及 |

#### 材质期望差距

识别买家对材质的误解：

```json
{
  "expectation_gaps": [
    {
      "buyer_expectation": "看起来像陶瓷/石材",
      "actual_common_material": "树脂(resin)",
      "trigger_expressions": ["looks plastic", "feels cheap", "thought it was ceramic"],
      "frequency": 5,
      "suggestion": "Listing中说明resin特性，设置正确预期"
    }
  ]
}
```

### 输出格式

```json
{
  "size_material_concerns": {
    "size_mentions": {
      "total": 35,
      "positive": 10,
      "negative": 20,
      "neutral": 5,
      "size_sensitivity_score": 8,
      "common_positive_expressions": ["perfect size", "good size"],
      "common_negative_expressions": ["smaller than expected", "too small for the price"],
      "recommendation": "尺寸敏感度极高，P0真值中的尺寸字段必须优先展示"
    },
    "material_mentions": {
      "total": 12,
      "positive": 5,
      "negative": 6,
      "neutral": 1,
      "expectation_gaps": [...],
      "recommendation": "材质期望管理：说明resin特性，强调优点（轻便、不易碎）"
    }
  }
}
```

---

## 维度5：Rufus问答题库

### 辅助角色

角色1+3：预期管理 + 表达方式参考

### 目的

从评论中推断买家最想问的问题，作为五点Q&A结构优化的参考。

### 提取规则（Claude执行）

#### Step 1: 识别隐性问题

从评论中提取暗示的问题（Claude语义推断）：

| 评论内容 | 推断的隐性问题 |
|----------|---------------|
| "smaller than expected" | "How big is this exactly?" |
| "feels cheap" | "What material is it made of?" |
| "had a foul odor" | "Does it have any smell?" |
| "bought as a gift, she loved it" | "Is this good as a gift?" |
| "great drainage holes" | "Does it have drainage holes?" |
| "I use it to hold kitchen utensils" | "What can I use it for besides plants?" |

#### Step 2: 问题主题聚类

| 主题 | 优先级判定依据 |
|------|---------------|
| 尺寸/规格 | 与痛点维度的size_sensitivity联动 |
| 材质/耐久 | 与痛点维度的material_mentions联动 |
| 礼品适合度 | 与礼品维度的gift_intent联动 |
| 使用场景 | 从正面评论的使用描述中提取 |
| 包装/运输 | 从负面评论的包装投诉中提取 |
| 功能细节 | 如drainage holes, indoor/outdoor等 |

#### Step 3: 通用性过滤

每个问答主题必须通过通用性过滤（≥2变体 OR ≥3条相关评论）。

### 输出格式

```json
{
  "id": "QA001",
  "question_theme": "尺寸相关",
  "question_theme_en": "Size Related",
  "priority": "HIGH",
  "typical_questions": [
    "How big is this?",
    "What are the exact dimensions?",
    "Is it bigger or smaller than it looks in photos?"
  ],
  "evidence_count": 20,
  "cross_variant_count": 3,
  "suggested_bullet_coverage": {
    "position": "Bullet 2（建议）",
    "must_include": ["精确尺寸", "参照物对比描述"],
    "note": "此为结构建议，具体内容由P0真值驱动"
  }
}
```

### 五点覆盖矩阵建议

以下为默认建议，Phase B可根据P0真值和P1关键词数据调整：

| Bullet | 建议覆盖主题 | Rufus问答对应 |
|--------|--------------|---------------|
| Bullet 1 | 核心卖点/题材 | What is this? |
| Bullet 2 | 尺寸规格 | How big is it? |
| Bullet 3 | 材质工艺 | What material? |
| Bullet 4 | 场景用途 | Where to use? |
| Bullet 5 | 礼品/包装（如S2触发） | Good gift? |

---

## 跨维度关联分析

### 维度间的数据流向

```
维度1（正面卖点）──→ 角色3：表达参考 ──→ 五点语言风格
                                       
维度2（负面痛点）──→ 角色1：预期管理 ──→ 五点措辞优先级
                                       
维度3（礼品信号）──→ 角色2：S2辅助 ──→ S2模式建议（需综合判定）

维度4（尺寸材质）──→ 角色1：预期管理 ──→ P0真值展示优先级

维度5（Rufus QA）──→ 角色1+3 ──→ 五点Q&A结构参考
         ↑
    与维度2/3/4联动
```

### 冲突处理规则

| 冲突场景 | 处理规则 |
|----------|----------|
| 正面卖点 vs 负面痛点同一主题 | 痛点优先（合规风控），卖点标注"需平衡表达" |
| 礼品信号 vs 数据不足 | 数据不足时降低置信度，标注LOW_CONFIDENCE |
| 跨维度数据不一致 | 以evidence_count较高的维度结论为准 |

### buyer_vocabulary的跨维度汇集

`buyer_vocabulary`不是独立维度，而是从所有维度的分析过程中同步提取的买家表达习惯汇总。详见 references/buyer-vocabulary-extraction.md。
