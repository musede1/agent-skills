> **调用方**：Phase A Step A3（输出CRD分析结果）
> **读取时机**：执行Step A3前必须读取本文档

# 输出格式规范

## 输出文件清单

| 文件名 | 格式 | 用途 | 生成条件 |
|--------|------|------|----------|
| `review_analysis.json` | JSON | 结构化数据，对接Phase B作为P2辅助输入 | 必须输出 |
| `review_report.md` | Markdown | 可读报告，人工审阅 | 必须输出 |

---

## JSON输出结构详解

### 顶层结构（V2.0，6个字段）

```json
{
  "meta": {},                        // 元数据
  "positive_selling_points": [],     // 正面卖点（角色3：表达参考）
  "negative_pain_points": [],        // 负面痛点（角色1：预期管理）
  "gift_intent_signal": {},          // 礼品意图信号（角色2：S2辅助信号）
  "size_material_concerns": {},      // 尺寸/材质关注（角色1：预期管理）
  "rufus_qa_library": [],            // Rufus问答库（角色1+3）
  "buyer_vocabulary": {}             // 买家表达词库（角色3：表达参考）
}
```

**V2.0变更说明**：
- 删除：`keyword_library`（L1-L4锚点配置由P0+人工设定，CRD不参与）
- 删除：`intent_extractor_config`（同上理由）
- 删除：`differentiation_opportunities`（依赖主观判断，无法全自动化）
- 新增：`buyer_vocabulary`（买家表达词库，角色3的核心输出）

---

### meta 元数据

```json
{
  "meta": {
    "version": "2.0",
    "generated_at": "2025-02-09T12:00:00Z",
    "source_file": "CRD_B0D7V67BNX_US_145.xlsx",
    "total_reviews": 145,
    "valid_reviews": 140,
    "filtered_reviews": 5,
    "rating_distribution": {
      "5_star": 100,
      "4_star": 25,
      "3_star": 10,
      "2_star": 5,
      "1_star": 5
    },
    "variant_count": 5,
    "variant_distribution": {
      "Style: Classic": 84,
      "Style: Modern": 44,
      "Style: Eclectic": 7,
      "Style: Contemporary": 6,
      "Style: Retro": 4
    },
    "vp_rate": 0.986,
    "avg_review_length": 89,
    "date_range": {
      "earliest": "2024-11-24",
      "latest": "2026-01-27"
    },
    "confidence_level": "HIGH",
    "universality_filter": {
      "rule": "cross_variant_count>=2 OR evidence_count>=3",
      "description": "所有洞察必须通过通用性过滤才能纳入输出"
    },
    "warnings": [],
    "crd_positioning": "P2辅助验证层（Auxiliary Validation Layer）"
  }
}
```

**confidence_level判定规则（5档）**：

| 评论数 | 置信度 |
|--------|--------|
| ≥100 | `HIGH` |
| 50-99 | `MEDIUM` |
| 20-49 | `LOW` |
| 10-19 | `VERY_LOW` |
| <10 | `INSUFFICIENT` |

---

### positive_selling_points 正面卖点

```json
{
  "positive_selling_points": [
    {
      "id": "SP001",
      "theme": "外观/设计吸引力",
      "theme_en": "Visual Appeal",
      "summary": "买家普遍认为设计独特、有个性，常用cute/unique/fun等词描述",
      "evidence_count": 45,
      "cross_variant_count": 4,
      "representative_quotes": [
        {
          "text": "This is EVEN cooler in person. Already getting compliments on it.",
          "rating": 5,
          "helpful_votes": 0
        },
        {
          "text": "So cool. Guests always comment on how awesome it is.",
          "rating": 4,
          "helpful_votes": 2
        }
      ],
      "buyer_expressions": ["cute", "unique", "cool", "fun", "quirky", "conversation piece"],
      "listing_suggestion": {
        "role": "表达参考（角色3）",
        "suggested_angle": "买家常用cute/unique/fun形容此类产品",
        "note": "仅供语言风格参考，产品事实必须来自P0真值"
      }
    }
  ]
}
```

**字段说明**：

| 字段 | 说明 |
|------|------|
| `cross_variant_count` | 该卖点在多少个变体中出现（≥2或evidence_count≥3才纳入） |
| `buyer_expressions` | 买家描述该卖点时的高频自然语言词汇 |
| `listing_suggestion.role` | 固定标注"表达参考"，提醒不可当作事实 |

---

### negative_pain_points 负面痛点

```json
{
  "negative_pain_points": [
    {
      "id": "NP001",
      "theme": "尺寸误解",
      "theme_en": "Size Misunderstanding",
      "summary": "大量买家反映产品比预期小，图片缺乏尺寸参照",
      "evidence_count": 15,
      "cross_variant_count": 3,
      "severity": "HIGH",
      "severity_reason": "涉及误购风险（尺寸误解必定HIGH），且跨3个变体出现",
      "representative_quotes": [
        {
          "text": "Much smaller than I thought, I really expected a decent size",
          "rating": 2,
          "helpful_votes": 1
        },
        {
          "text": "I had it pictured larger in my mind",
          "rating": 3,
          "helpful_votes": 0
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
  ]
}
```

**severity动态判定规则**：

误购风险痛点（尺寸/材质/数量误解）：任何样本量下都标注HIGH。

其他痛点：

| 评论基数 | HIGH条件 | MEDIUM条件 | LOW条件 |
|---------|----------|-----------|---------|
| ≥100条 | evidence_rate≥5% | 2-5% | <2% |
| 50-99条 | rate≥3% 且 count≥5 | count≥3 | <3条 |
| 20-49条 | count≥5 | count≥3 | <3条 |
| 10-19条 | 不判定，仅定性描述 | | |
| <10条 | 不判定 | | |

---

### gift_intent_signal 礼品意图信号

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
      "note": "此为P2辅助信号，S2模式最终决定需结合P0产品真值和P1关键词库综合判定"
    }
  }
}
```

**关键区别（V2.0 vs V1.1）**：
- `trigger_s2_mode` → `suggest_s2_mode`（从"触发"降为"建议"）
- 新增`note`字段，提醒需综合判定

---

### size_material_concerns 尺寸/材质关注

```json
{
  "size_material_concerns": {
    "size_mentions": {
      "total": 35,
      "positive": 10,
      "negative": 20,
      "neutral": 5,
      "common_positive_expressions": ["perfect size", "good size"],
      "common_negative_expressions": ["smaller than expected", "too small for the price"],
      "size_sensitivity_score": 8,
      "recommendation": "尺寸敏感度极高（8/10），P0真值中的尺寸字段必须优先展示"
    },
    "material_mentions": {
      "total": 12,
      "positive": 5,
      "negative": 6,
      "neutral": 1,
      "common_positive_expressions": ["solid", "well made"],
      "common_negative_expressions": ["looks plastic", "feels cheap"],
      "expectation_gaps": [
        {
          "buyer_expectation": "看起来像陶瓷/石材",
          "actual_common_material": "树脂(resin)",
          "trigger_expressions": ["looks plastic", "feels cheap", "thought it was ceramic"],
          "frequency": 5,
          "suggestion": "Listing中说明resin特性，设置正确预期"
        }
      ],
      "recommendation": "材质期望管理：说明resin特性，强调优点（轻便、不易碎）"
    },
    "weight_mentions": {
      "total": 5,
      "positive": 3,
      "negative": 1,
      "neutral": 1,
      "recommendation": "重量为次要关注点，在尺寸Bullet中附带提及即可"
    }
  }
}
```

---

### rufus_qa_library Rufus问答库

```json
{
  "rufus_qa_library": [
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
  ]
}
```

---

### buyer_vocabulary 买家表达词库（V2.0新增）

```json
{
  "buyer_vocabulary": {
    "how_buyers_call_product": [
      {"expression": "planter", "frequency": 30},
      {"expression": "pot", "frequency": 25},
      {"expression": "flower pot", "frequency": 10},
      {"expression": "face pot", "frequency": 5},
      {"expression": "face planter", "frequency": 8}
    ],
    "positive_descriptors": [
      {"expression": "cute", "frequency": 35},
      {"expression": "unique", "frequency": 15},
      {"expression": "fun", "frequency": 12},
      {"expression": "cool", "frequency": 10},
      {"expression": "quirky", "frequency": 5},
      {"expression": "conversation piece", "frequency": 4}
    ],
    "scene_mentions": [
      {"expression": "kitchen", "frequency": 5},
      {"expression": "patio", "frequency": 3},
      {"expression": "window", "frequency": 3},
      {"expression": "shelf", "frequency": 4},
      {"expression": "garden", "frequency": 3}
    ],
    "use_case_mentions": [
      {"expression": "succulent", "frequency": 8},
      {"expression": "plant", "frequency": 40},
      {"expression": "utensil holder", "frequency": 2},
      {"expression": "decor", "frequency": 10}
    ],
    "note": "⚠️ 以上词汇仅供表达方式参考，不可作为产品事实来源。Listing中所有事实性描述必须来自P0真值。"
  }
}
```

**buyer_vocabulary的用途**：
- Phase B在撰写五点时，可参考买家自然语言称呼（如"planter"比"flower pot"更常用）
- 正面描述词可作为Description的语言风格参考
- 场景/用途词可辅助Description的场景描绘

**严格限制**：
- 不参与L1-L4锚点词配置
- 不可替代P0产品真值
- 仅为语言层面的参考

---

## 输出质量校验

### 必须校验项（output_validator.py执行）

| 校验项 | 规则 | 失败处理 |
|--------|------|----------|
| JSON有效性 | 可被JSON.parse解析 | 报错终止 |
| 必需字段完整 | 6个顶层字段全部存在 | 缺失字段填充`{"insufficient_data": true}` |
| 引用数量 | representative_quotes≤3条/主题 | 超出截断 |
| 情感值范围 | sentiment在[-1, 1]区间 | 越界修正为边界值 |
| 通用性标注 | 所有洞察包含cross_variant_count字段 | 缺失则警告 |
| P2定位标注 | meta中包含crd_positioning字段 | 缺失则自动补充 |

### 输出文件命名

```
# 默认命名
review_analysis.json
review_report.md

# 带时间戳
review_analysis_20250209_120000.json
review_report_20250209_120000.md
```
