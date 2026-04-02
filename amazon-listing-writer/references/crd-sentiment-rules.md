> **调用方**：Phase A Step A2（Claude深度分析）
> **读取时机**：执行Step A2前必须读取本文档

# 情感分析规则

## 情感分析概述

本技能的情感分析主要服务于：
1. 卖点/痛点主题分类（正面/负面/中性）
2. 痛点严重程度判定
3. 置信度计算

V2.0变更：删除了"关键词情感标注"用途（不再输出L1-L4关键词库）。新增跨变体验证和缺失字段容错。

---

## 情感计算方法

### 主要方法：基于星级的情感推断

最简单可靠的方法：利用评论星级推断情感。

```python
def calculate_sentiment_by_rating(theme_reviews):
    """
    基于包含该主题的评论星级计算情感分数
    
    Args:
        theme_reviews: 包含该主题的评论列表
    
    Returns: sentiment score in [-1, 1]
    """
    if not theme_reviews:
        return 0  # 无数据，中性
    
    total_weight = 0
    weighted_sum = 0
    
    for review in theme_reviews:
        weight = get_review_weight(review)
        weighted_sum += review.rating * weight
        total_weight += weight
    
    avg_rating = weighted_sum / total_weight  # 1-5 scale
    
    # 转换为 [-1, 1] 区间
    # 1星 → -1, 3星 → 0, 5星 → 1
    sentiment = (avg_rating - 3) / 2
    
    return round(sentiment, 2)
```

### 辅助方法：情感词典

用于Claude在语义分析中辅助判断情感倾向。

#### 正面情感词（家居工艺品常见）

```python
POSITIVE_WORDS = {
    # 外观相关
    "beautiful", "gorgeous", "stunning", "lovely", "pretty",
    "detailed", "intricate", "elegant", "exquisite",
    "cute", "unique", "fun", "cool", "quirky", "artsy",
    
    # 质量相关
    "quality", "solid", "durable", "sturdy", "well-made",
    "craftsmanship", "crafted",
    
    # 尺寸相关（满意）
    "perfect size", "good size", "right size",
    
    # 价值相关
    "worth", "value", "affordable",
    "exceeded expectations", "better than expected",
    
    # 情感相关
    "love", "loved", "amazing", "wonderful", "fantastic",
    "happy", "pleased", "satisfied", "impressed",
    
    # 推荐相关
    "recommend", "highly recommend", "must have"
}
```

#### 负面情感词

```python
NEGATIVE_WORDS = {
    # 外观相关
    "ugly", "cheap-looking", "tacky", "disappointing",
    
    # 质量相关
    "cheap", "flimsy", "fragile", "broke", "broken",
    "defective", "damaged", "poor quality", "poorly made",
    
    # 尺寸相关（不满）
    "smaller than expected", "too small", "tiny",
    
    # 价值相关
    "overpriced", "not worth", "waste of money",
    "regret", "return", "refund",
    
    # 情感相关
    "disappointed", "frustrating", "terrible",
    "awful", "horrible",
    
    # 警告相关
    "don't buy", "avoid", "stay away",
    
    # 感官问题
    "smell", "odor", "stink", "chemical smell"
}
```

### 情感标签映射

```python
def get_sentiment_label(sentiment_score):
    if sentiment_score >= 0.3:
        return "positive"
    elif sentiment_score <= -0.3:
        return "negative"
    else:
        return "neutral"
```

---

## 评论分组规则

### 按星级分组

| 分组 | 星级范围 | 用途 |
|------|----------|------|
| 正面 | 4-5星 | 提炼卖点（维度1） |
| 中性 | 3星 | 提炼期望/隐含不满 |
| 负面 | 1-2星 | 提炼痛点（维度2） |

**注意**：Claude在分析痛点时还应关注高星评论中的转折不满（如"Love it but smaller than expected"）。

### 评论权重计算（含缺失字段容错）

```python
def get_review_weight(review):
    """
    计算评论权重
    
    V2.0: 增加缺失字段容错
    """
    weight = 1.0
    
    # VP评论加权
    # 容错：VP评论字段缺失时，默认视为VP，weight不变
    vp_value = getattr(review, 'vp', None)
    if vp_value is not None:
        if str(vp_value).upper() == 'Y':
            weight *= 1.5
        # 非Y（包括N、空值）保持weight=1.0
    else:
        # VP列不存在，默认全部视为VP
        weight *= 1.5
    
    # 赞同数加权（对数缩放）
    # 容错：赞同数字段缺失时，默认0，不加权
    helpful = getattr(review, 'helpful_votes', 0) or 0
    if helpful > 0:
        weight *= 1 + math.log(1 + helpful) * 0.2
    
    # 评论长度加权（长评论通常更有价值）
    text_len = len(getattr(review, 'text', '') or '')
    if text_len > 200:
        weight *= 1.2
    elif text_len < 50:
        weight *= 0.8
    
    return weight
```

---

## 主题聚类规则

### 卖点主题（Claude语义驱动，以下为参考方向）

| 主题方向 | 参考触发信号 | 对接角色 |
|----------|-------------|---------|
| 外观/设计 | cute, unique, cool, fun, conversation piece | 角色3：表达参考 |
| 尺寸满意 | perfect size, good size | 角色3：表达参考 |
| 材质质感 | solid, quality, well made | 角色3：表达参考 |
| 包装/开箱 | well packaged, gift ready | 角色3：表达参考 |
| 礼品反馈 | gift, present, she loved it | 角色2：S2信号 |
| 性价比 | worth, value, great price | 角色3：表达参考 |
| 实用性 | drainage, holds utensils | 角色3：表达参考 |
| 装饰效果 | compliments, personality, statement | 角色3：表达参考 |

### 痛点主题（Claude语义驱动，以下为参考方向）

| 主题方向 | 参考触发信号 | 严重程度规则 |
|----------|-------------|-------------|
| 尺寸误解 | smaller, tiny, expected bigger, pictured larger | 必定HIGH（误购风险） |
| 材质失望 | cheap, plastic, flimsy | 动态阈值判定 |
| 颜色偏差 | darker, different color, not like picture | 动态阈值判定 |
| 做工/质量 | paint came off, poorly made, defect | 动态阈值判定 |
| 气味问题 | smell, odor, chemical | 动态阈值判定 |
| 价格不值 | overpriced, not worth | 动态阈值判定 |
| 图片误导 | misleading, not as shown | 动态阈值判定 |

### 跨变体验证（V2.0新增）

每个聚类主题必须计算`cross_variant_count`：

```python
def calculate_cross_variant_count(theme_reviews, variant_column='型号'):
    """
    计算该主题在多少个不同变体中出现
    """
    variants = set()
    for review in theme_reviews:
        variant = getattr(review, variant_column, None)
        if variant:
            variants.add(variant)
    return len(variants)
```

---

## 代表性引用选择规则

### 选择标准

1. **相关性**：必须与主题核心观点相关
2. **代表性**：表达主题核心态度
3. **质量**：优先选择`赞同数`高的评论
4. **长度**：20-100字符为宜
5. **上限**：每主题最多3条

### 选择逻辑

```python
def select_representative_quotes(theme_reviews, max_quotes=3):
    # 按赞同数排序（容错：缺失赞同数默认0）
    sorted_reviews = sorted(
        theme_reviews, 
        key=lambda r: getattr(r, 'helpful_votes', 0) or 0, 
        reverse=True
    )
    
    quotes = []
    used_patterns = set()
    
    for review in sorted_reviews:
        if len(quotes) >= max_quotes:
            break
        
        text = review.text.strip()
        
        # 去重：避免太相似的引用
        pattern = text[:30].lower()
        if pattern not in used_patterns:
            # 截断过长文本
            if len(text) > 100:
                text = text[:97] + "..."
            
            quotes.append({
                "text": text,
                "rating": review.rating,
                "helpful_votes": getattr(review, 'helpful_votes', 0) or 0
            })
            used_patterns.add(pattern)
    
    return quotes
```

---

## 情感分析质量保证

### 异常值处理

```python
def handle_sentiment_outliers(sentiment_scores):
    # 极端值修正
    scores = [max(-1, min(1, s)) for s in sentiment_scores]
    
    # 样本量不足时降低置信度
    if len(scores) < 5:
        return {
            "sentiment": sum(scores) / len(scores) if scores else 0,
            "confidence": "LOW",
            "note": "insufficient_samples"
        }
    
    return {
        "sentiment": sum(scores) / len(scores),
        "confidence": "HIGH"
    }
```

### 冲突检测

当同一主题同时出现在正面和负面评论中：

```python
def detect_sentiment_conflict(theme, positive_count, negative_count):
    total = positive_count + negative_count
    
    if total == 0:
        return None
    
    conflict_ratio = min(positive_count, negative_count) / total
    
    if conflict_ratio > 0.3:
        return {
            "theme": theme,
            "conflict": True,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "recommendation": "该主题正负评价并存，需在Listing中平衡表达"
        }
    
    return None
```
