> **调用方**：Phase B Step B1（关键词分析）
> **读取时机**：执行Step B1前必须读取本文档

# 关键词配额分配规则

## 概述

本规则定义了如何将竞品关键词库中的词分配到Listing各位置（标题/五点/Search Terms），确保核心词完整覆盖且数量可控。

**核心机制**：基于4层锚点词的语义评分系统，自动过滤不相关词，无需手动维护黑名单。

---

## 一、4层锚点词体系

### 1.1 层级定义

| 层级 | 参数 | 词类型 | 得分权重 | 说明 |
|------|------|--------|----------|------|
| **L1** | --L1-subject | 题材形状词 | +30-40分 | 核心层，区分产品本质 |
| **L2** | --L2-category | 品类词+功能词 | +25分 | 品类层，定义产品类型 |
| **L3** | --L3-attribute | 材质词+工艺词+颜色词 | +10-15分 | 属性层，描述产品特征 |
| **L4** | --L4-scene | 风格词+场景词 | +5分 | 场景层，描述使用环境 |

### 1.2 各层级示例

**海螺玻璃雕塑产品**：
```bash
--L1-subject "conch,shell,seashell"
--L2-category "sculpture,figurine,statue,decor,paperweight,art"
--L3-attribute "glass,blown,hand blown,aqua,blue,teal"
--L4-scene "coastal,nautical,beach,ocean,sea,marine"
```

**情侣树脂雕像产品**：
```bash
--L1-subject "couple,lover,pair"
--L2-category "sculpture,figurine,statue,decor"
--L3-attribute "resin,hand painted,bronze"
--L4-scene "romantic,modern,minimalist"
```

**大象陶瓷花瓶产品**：
```bash
--L1-subject "elephant"
--L2-category "vase,planter,pot,decor"
--L3-attribute "ceramic,porcelain,white,blue"
--L4-scene "bohemian,farmhouse,rustic"
```

---

## 二、语义评分规则

### 2.1 评分公式

```
语义评分 = 基础分 + L1分 + L2分 + L3分 + L4分

基础分：
  - 关键词2-4词：20分
  - 关键词1词或5+词：10分

L1分（题材层）：
  - 命中≥2个锚点词：+40分
  - 命中1个锚点词：+30分
  - 未命中：+0分

L2分（品类层）：
  - 命中≥1个锚点词：+25分
  - 未命中：+0分

L3分（属性层）：
  - 命中≥2个锚点词：+15分
  - 命中1个锚点词：+10分
  - 未命中：+0分

L4分（场景层）：
  - 命中≥1个锚点词：+5分
  - 未命中：+0分
```

### 2.2 自动剔除规则（替代黑名单）

**EXCLUDE判定**：L1、L2、L3均未命中 → 与产品完全无关，语义评分强制归零

**效果**：
- `glass starfish`：仅命中L3(glass)，L1/L2未命中 → 语义30分 → ST_ONLY（不会进入标题/五点）
- `chihuly glass art`：命中L2(art)+L3(glass) → 语义55分 → P2_NORMAL（最多进入ST）
- `florida decor`：命中L2(decor)，L1/L3未命中 → 语义45分 → P2_NORMAL
- `random word`：L1/L2/L3均未命中 → 语义0分 → EXCLUDE

**无需手动黑名单**：通过锚点词的精确配置，系统自动将不相关词降级或剔除。

---

## 三、等级划分与配额分配

### 3.1 等级划分

| 语义评分 | 等级 | 分配位置 |
|----------|------|----------|
| ≥60分 | P0_P1_HIGH | 标题优先，溢出进入五点 |
| 45-59分 | P2_NORMAL | 五点优先，溢出进入ST |
| 30-44分 | ST_ONLY | 仅Search Terms |
| <30分 | EXCLUDE | 剔除，不使用 |

### 3.2 配额设定

| 位置 | 默认配额 | 可调范围 | 说明 |
|------|----------|----------|------|
| 标题 | 3个词组 | 2-4 | 核心高分词优先 |
| 五点 | 5个词组 | 3-7 | 中高分词填充 |
| Search Terms | 填满245 bytes | 230-250 | 剩余词+通用填充词 |
| 长描述 | 不设配额 | - | 自然覆盖即可 |

### 3.3 分配流程

```
Step 1: P0_P1_HIGH词按优先级进入标题（直到配额满）
Step 2: P0_P1_HIGH溢出词进入五点
Step 3: P2_NORMAL词填充五点剩余配额
Step 4: ST_ONLY词 + 剩余P2词进入Search Terms
Step 5: EXCLUDE词剔除，不使用
```

---

## 四、综合优先级公式

语义评分确定等级后，同等级内部按综合优先级排序：

```
Priority = R_score × 0.4 + SV_score × 0.3 + Semantic_score × 0.3

其中：
- R_score = 100 - min(R, 100)    // R越低分越高
- SV_score = min(log10(SV+1) × 25, 100)    // SV对数处理
- Semantic_score = 语义评分
```

---

## 五、完整使用示例

### 5.1 脚本调用

```bash
python3 scripts/intent_extractor.py keywords.xlsx \
  --L1-subject "conch,shell,seashell" \
  --L2-category "sculpture,figurine,statue,decor,paperweight,art" \
  --L3-attribute "glass,blown,hand blown,aqua,blue,teal" \
  --L4-scene "coastal,nautical,beach,ocean,sea,marine" \
  --title-quota 3 \
  --bullet-quota 5 \
  --output intent_result.json
```

### 5.2 输出示例

```
标题配额 (3/3):
  ✓ glass conch shell
    R:5 | SV:135 | 语义:70 | 优先级:75.0
    得分: 基础20 + L1(2命中)+40 + L2+0 + L3+10 + L4+0
  ✓ conch shell decor
    R:27 | SV:129 | 语义:85 | 优先级:70.55
    得分: 基础20 + L1(2命中)+40 + L2+25 + L3+0 + L4+0
  ✓ glass paperweights hand blown
    R:10 | SV:162 | 语义:60 | 优先级:70.59
    得分: 基础20 + L1(0命中)+0 + L2+25 + L3+15 + L4+0

五点配额 (5/5):
  ✓ blown glass art (R:12, 语义:60)
  ✓ blown glass figurines (R:18, 语义:60)
  ✓ hand blown glass decor (R:18, 语义:60)
  ✓ seashell glass (R:23, 语义:75)
  ✓ seaglass decor for home (R:21, 语义:60)

已自动降级 (ST_ONLY):
  · glass starfish (语义:30) → 仅L3命中，不进入标题/五点
  · luke adams glass (语义:30) → 仅L3命中，不进入标题/五点
```

---

## 六、P0真值冲突检测（重要）

### 6.1 冲突类型

| 冲突类型 | 说明 | 示例 |
|----------|------|------|
| **材质冲突** | 配额词的材质与P0材质不符 | 产品是resin，`brass bookends`冲突 |
| **题材冲突** | 配额词的题材与P0题材不符 | 产品是conch，`starfish sculpture`冲突 |
| **品类冲突** | 配额词的品类与P0品类不符 | 产品是bookend，`tree of life statue`需评估 |

### 6.2 冲突处理规则

1. **材质冲突**：**必须剔除**，不可使用（会误导消费者）
2. **题材冲突**：**必须剔除**，不可使用
3. **品类冲突**：评估是否兼容，不兼容则剔除

### 6.3 Claude执行要求

在使用配额词前，必须检查：
- 配额词中的材质描述是否与P0材质一致？
- 配额词中的题材描述是否与P0题材一致？
- 配额词中的品类词是否与P0品类兼容？

**有冲突则跳过该配额词，用下一个候选词替代。**

---

## 七、标题叠词与部分覆盖规则

### 7.1 问题背景

亚马逊严禁标题重复叠词。当多个配额词存在词根重复时，无法全部完整写入标题。

**示例**：
- 配额词：`tree of life bookends`, `religious bookends`, `tree bookends`
- 重复词根：`bookends`出现3次，`tree`有包含关系

### 7.2 部分覆盖规则

| 情况 | 处理方式 | 示例 |
|------|----------|------|
| 词组A完整包含词组B的核心词 | B视为已被A覆盖 | `tree of life bookends`覆盖`tree bookends` |
| 独立修饰词+整体语境 | 修饰词单独出现即可 | `religious`+标题整体含`bookends` |
| 无法部分覆盖 | 必须完整写入或进入五点/ST | - |

### 7.3 拆词补偿机制

被拆开未完整出现在标题的配额词，需要**补偿写入**：

```
优先级：五点 > Search Terms

Step 1: 检查哪些配额词在标题中被拆开
Step 2: 拆开的词组优先在五点中完整写入
Step 3: 五点空间不足时，进入Search Terms完整写入
```

**目的**：确保A9能在五点或ST中识别完整词组

### 7.4 示例

**配额词**：
1. `tree of life bookends` (R:1)
2. `religious bookends` (R:1)
3. `tree bookends` (R:8)

**标题处理**：
```
Tree of Life Bookends Set of 2 Decorative Book Ends Vintage Religious Celtic Design...
```
- ✓ `tree of life bookends` - 完整覆盖
- △ `religious bookends` - 部分覆盖（religious单独出现，bookends在标题中）
- △ `tree bookends` - 部分覆盖（被tree of life bookends包含）

**补偿处理**：
- `religious bookends` → 在五点中完整写入
- `tree bookends` → 可不补偿（已被完整包含）

---

## 八、与现有规则的关系

### 8.1 替代黑名单机制

| 原方案 | 新方案 | 说明 |
|--------|--------|------|
| 手动维护黑名单 | 4层锚点自动过滤 | 无需人工标记 |
| `--blacklist`参数 | **已移除** | 通过锚点配置实现相同效果 |

### 8.2 与SKILL.md的关系

| SKILL.md规则 | 本文档规则 | 关系 |
|--------------|-----------|------|
| 标题配额2-3个 | 标题配额3个（可配置） | 一致 |
| 五点配额3-5个 | 五点配额5个（可配置） | 一致 |
| ST 230-250 bytes | ST填满245 bytes | 一致 |

---

## 九、常见问题

### Q1: 如何处理竞品品牌词？

竞品品牌词（如`chihuly`）通常会：
- 命中L2（如`art`）或L3（如`glass`）
- 得分45-55分，归类为P2_NORMAL
- 最多进入ST，不会进入标题/五点核心位置

如果完全不想使用，可以从L2中移除相关品类词（如移除`art`）。

### Q2: 如何确保题材词被优先选中？

L1（题材层）权重最高（+30-40分），命中L1的词语义评分天然更高，会优先进入标题配额。

### Q3: 为什么有些高R值（低排名）的词没有进入标题？

因为语义评分优先于R值。一个R=50但语义90分的词，比R=10但语义40分的词更优先。

### Q4: 长描述为什么没有配额？

长描述的核心目标是**转化**而非SEO。按6段式结构写好内容后，核心词会自然出现。coverage_checker会检查长描述覆盖情况，但不强制。

### Q5: 配额词与P0材质冲突怎么办？

**必须剔除**。例如产品是resin材质，`brass bookends`不可使用。Claude在生成前必须检查冲突。

### Q6: 标题配额词有叠词怎么办？

允许部分覆盖。完整词组A包含词组B的核心词时，B视为已覆盖。被拆开的词组需在五点或ST中完整补偿。

### Q7: 如何判断品类词是否兼容？

评估配额词的品类词是否可以描述P0产品。例如：
- bookend产品，`tree of life statue`的`statue`与`bookend`不完全兼容
- 但`tree of life decor`的`decor`是通用词，可兼容
