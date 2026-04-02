> **调用方**：Phase B Step B1（关键词分析）
> **读取时机**：执行Step B1前必须读取本文档

# P2 关键词分析与配额分配规则

## 重要说明

**量化判定必须通过脚本执行**，Claude不进行数值计算。

脚本V3.0使用4层锚点词评分系统，自动完成：
1. **语义评分**：基于4层锚点词匹配度计算
2. **关键词分级**：根据语义评分自动分级（P0_P1/P2/ST_ONLY/EXCLUDE）
3. **配额分配**：按等级和优先级分配到标题/五点/ST
4. **意图词提炼**：提取风格词/礼品词/节日词/受众词

**无需手动黑名单**：通过4层锚点的精确配置，系统自动过滤不相关词。

---

## 使用流程

### Step 1: 运行量化脚本

```bash
python3 scripts/intent_extractor.py <关键词文件.xlsx或.csv> \
    --L1-subject "题材词1,题材词2" \
    --L2-category "品类词1,品类词2,功能词" \
    --L3-attribute "材质词,工艺词,颜色词" \
    --L4-scene "风格词,场景词" \
    --title-quota 3 \
    --bullet-quota 5 \
    --output intent_result.json
```

**参数说明**：

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| --L1-subject | ✅ | 题材形状锚点词（核心层） | `conch,shell,seashell` |
| --L2-category | ✅ | 品类功能锚点词（品类层） | `sculpture,figurine,decor` |
| --L3-attribute | ❌ | 材质工艺颜色锚点词（属性层） | `glass,blown,aqua` |
| --L4-scene | ❌ | 风格场景锚点词（场景层） | `coastal,nautical,beach` |
| --title-quota | ❌ | 标题配额（默认3） | `3` |
| --bullet-quota | ❌ | 五点配额（默认5） | `5` |

### Step 2: Claude读取脚本结果

脚本输出JSON包含：

```json
{
  "summary": {
    "anchors": {
      "L1_subject": ["conch", "shell"],
      "L2_category": ["sculpture", "decor"],
      "L3_attribute": ["glass", "blown"],
      "L4_scene": ["coastal", "beach"]
    },
    "title_allocated": 3,
    "bullet_allocated": 5,
    "excluded": 2
  },
  "allocation": {
    "title_keywords": [...],    // 标题配额词
    "bullet_keywords": [...],   // 五点配额词
    "st_keywords": [...],       // ST候选词
    "excluded_keywords": [...]  // 被剔除词
  },
  "suggested_search_terms": "...",
  "intent_words": {...}
}
```

### Step 3: Claude按配额生成文案

| JSON字段 | 落位 | 要求 |
|----------|------|------|
| `title_keywords` | 标题 | **全部必须出现**，保持词组完整性 |
| `bullet_keywords` | 五点 | 分散嵌入，覆盖率≥80% |
| `suggested_search_terms` | Search Terms | 直接使用或微调 |
| `intent_words.strong_evidence` | 标题/五点 | 根据`usage`字段决定 |
| `intent_words.usable_evidence` | 五点/ST | 根据`usage`字段决定 |

### Step 4: （可选）运行覆盖率检查

```bash
python3 scripts/coverage_checker.py --listing listing.txt --keywords intent_result.json
```

---

## 4层锚点词体系

### 层级说明

| 层级 | 词类型 | 得分 | 说明 |
|------|--------|------|------|
| **L1** | 题材形状词 | +30-40分 | 产品的核心题材，如conch/elephant/couple |
| **L2** | 品类词+功能词 | +25分 | 产品类型，如sculpture/vase/paperweight |
| **L3** | 材质词+工艺词+颜色词 | +10-15分 | 产品属性，如glass/resin/blue |
| **L4** | 风格词+场景词 | +5分 | 使用场景，如coastal/modern/beach |

### 配置示例

**海螺玻璃雕塑**：
```
L1: conch, shell, seashell
L2: sculpture, figurine, statue, decor, paperweight, art
L3: glass, blown, hand blown, aqua, blue, teal
L4: coastal, nautical, beach, ocean, sea, marine
```

**情侣树脂雕像**：
```
L1: couple, lover, pair, two
L2: sculpture, figurine, statue, decor
L3: resin, hand painted, bronze, gold
L4: romantic, modern, minimalist, anniversary
```

---

## 语义评分与等级划分

### 评分公式

```
语义评分 = 基础分(10-20) + L1分(0-40) + L2分(0-25) + L3分(0-15) + L4分(0-5)
```

### 等级划分

| 语义评分 | 等级 | 分配位置 | 说明 |
|----------|------|----------|------|
| ≥60分 | P0_P1_HIGH | 标题/五点 | 高相关度，优先使用 |
| 45-59分 | P2_NORMAL | 五点/ST | 中等相关度 |
| 30-44分 | ST_ONLY | 仅ST | 低相关度，仅补充 |
| <30分 | EXCLUDE | 剔除 | 不相关或有害 |

### 自动剔除规则

**EXCLUDE条件**：L1、L2、L3均未命中 → 语义评分强制归零

这意味着仅命中L4（场景词）的关键词会被剔除，因为它们与具体产品无关。

---

## 意图词提炼规则（保留）

### 适用对象

风格词、礼品场景词、节日场合词、受众词

### 量化指标

| 指标 | 定义 |
|------|------|
| F | 出现频次 |
| U | 覆盖关键词数（去重） |
| SVsum | 搜索量加总 |
| Rbest | 最佳自然排名（越小越好） |

### 判定阈值

**基础门槛**：U ≥ 3 且 F ≥ 3

**强证据**（任一满足）：
- Rbest ≤ 12
- Rbest ≤ 18 且 U ≥ 4
- SVsum ≥ 8000 且 U ≥ 5

**可用证据**（任一满足）：
- Rbest ≤ 25 且 U ≥ 3
- SVsum ≥ 4000 且 U ≥ 4

**同框过滤**：U_core ≥ 2（候选词+L1题材锚点词同时出现的关键词数）

---

## 风格词纳入策略

### 默认规则

1. 风格词不作为标题核心短语默认项
2. 优先从P0读取风格词
3. 若P0未提供，使用脚本筛出的强证据风格词
4. 风格词优先写入Bullets
5. **禁止**：luxury/premium/elegant 等主观夸张词

### 风格词入标题例外规则

同时满足以下所有条件：
1. 标题配额未满
2. 脚本判定为强证据
3. 与产品图片外观高度一致
4. 加入后不破坏前段优先

---

## 空间场景词生成规则

### 自动生成来源

1. **产品图片识别**：tabletop/shelf/mantel；living room/bedroom/entryway/office
   - **禁止推断**：bathroom/outdoor（除非P0确认）

2. **竞品关键词库**：含 room/space/desk/shelf/mantel 等语义的短语

### 场景词入标题门槛

1. 出现在`title_keywords`或`bullet_keywords`中
2. 不挤占标题核心短语名额
3. 可读性良好

**未满足则只能放入五点 + Search Terms**
