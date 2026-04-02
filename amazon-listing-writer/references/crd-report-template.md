> **调用方**：Phase A Step A3（输出CRD分析结果）
> **读取时机**：执行Step A3前必须读取本文档

# Markdown报告模板

## 报告结构概览（V2.0）

```
# CRD分析报告（P2辅助验证层）
├── 概览
├── 1. 买家表达词库（角色3：表达参考）
├── 2. 正面卖点（角色3：表达参考）
├── 3. 负面痛点（角色1：预期管理）
├── 4. 礼品意图信号（角色2：S2辅助信号）
├── 5. 尺寸/材质关注（角色1：预期管理）
├── 6. Rufus问答覆盖建议（角色1+3）
└── 附录
```

V2.0变更：
- 删除原"关键词洞察"章节（L1-L4锚点配置不再由CRD输出）
- 删除原"差异化机会"章节（无法全自动化）
- 删除原"intent_extractor配置建议"章节
- 新增"买家表达词库"章节
- 全文新增P2辅助定位标注

---

## 完整模板

```markdown
# CRD分析报告（P2辅助验证层）

**生成日期**：{generated_date}  
**数据来源**：{source_file}  
**分析版本**：amazon-listing-writer V6.0 Phase A  
**数据定位**：P2辅助验证层 — 所有结论仅供参考，不替代P0产品真值和P1关键词库

---

## 概览

| 指标 | 数值 |
|------|------|
| 评论总数 | {total_reviews} |
| 有效评论 | {valid_reviews} |
| VP占比 | {vp_rate}% |
| 平均评分 | {avg_rating} ⭐ |
| 变体数量 | {variant_count} |
| 数据置信度 | {confidence_level} |

### 星级分布

| 星级 | 数量 | 占比 |
|------|------|------|
| ⭐⭐⭐⭐⭐ | {5_star} | {5_star_pct}% |
| ⭐⭐⭐⭐ | {4_star} | {4_star_pct}% |
| ⭐⭐⭐ | {3_star} | {3_star_pct}% |
| ⭐⭐ | {2_star} | {2_star_pct}% |
| ⭐ | {1_star} | {1_star_pct}% |

### 变体分布

| 变体 | 评论数 | 平均星级 |
|------|--------|---------|
{variant_rows}

### 通用性过滤规则

本报告中所有洞察均已通过通用性过滤：
- 条件A：出现在 ≥2个变体 中 **或**
- 条件B：总提及数 ≥3条

不满足以上任一条件的洞察已被自动过滤。

---

## 1. 买家表达词库（角色3：表达参考）

⚠️ **以下词汇仅供表达方式参考，不可作为产品事实来源。**

### 买家怎么称呼这类产品

| 表达 | 频次 |
|------|------|
{product_name_rows}

### 买家常用正面描述词

| 描述词 | 频次 |
|--------|------|
{positive_descriptor_rows}

### 买家提及的场景/位置

| 场景 | 频次 |
|------|------|
{scene_rows}

### 买家提及的用途

| 用途 | 频次 |
|------|------|
{use_case_rows}

---

## 2. 正面卖点（角色3：表达参考）

⚠️ 以下卖点方向仅供语言风格参考，Listing中的事实性描述必须来自P0真值。

{for each selling_point:}

### 卖点{index}：{theme}

- **提及次数**：{evidence_count}次
- **跨变体数**：{cross_variant_count}个变体

**代表性评论**：
> "{quote_1}"

> "{quote_2}"

**买家常用表达**：{buyer_expressions}

**Listing语言参考**：
- 参考角度：{suggested_angle}

---

{/for}

## 3. 负面痛点（角色1：预期管理）

{for each pain_point:}

### {severity_icon} {severity}风险：{theme}

- **提及次数**：{evidence_count}次
- **跨变体数**：{cross_variant_count}个变体
- **严重程度**：{severity}
- **判定依据**：{severity_reason}

**代表性评论**：
> "{quote_1}"

**根因分析**：
{root_causes}

**⚠️ 合规警示**：
{compliance_warning}

**Listing预期管理建议**：
- 优先级：{priority}
- 建议措施：{suggested_approach}

---

{/for}

## 4. 礼品意图信号（角色2：S2辅助信号）

### 检测结果：{detected_icon} {detected_text}

| 指标 | 数值 |
|------|------|
| 置信度 | {confidence} |
| 礼品提及率 | {gift_mention_rate}% |
| 礼品相关评论数 | {gift_mention_count} |

### 礼品关键词分布

| 关键词 | 频次 |
|--------|------|
{gift_keyword_rows}

### 礼品接收对象

| 对象 | 频次 |
|------|------|
{recipient_rows}

### S2模式建议

{if suggest_s2:}
📋 **建议考虑S2模式**（精准+礼品平衡）

置信依据：{confidence_reason}

⚠️ 此为P2辅助信号，S2模式的最终决定需结合P0产品真值和P1关键词库综合判定。
{else:}
ℹ️ **建议保持S1模式**（极致精准）

礼品意图信号不够强，无需特别强化礼品场景。
{/if}

---

## 5. 尺寸/材质关注（角色1：预期管理）

### 5.1 尺寸敏感度

| 指标 | 数值 |
|------|------|
| 尺寸提及次数 | {size_total} |
| 正面提及 | {size_positive} |
| 负面提及 | {size_negative} |
| 敏感度评分 | {size_sensitivity}/10 |

**买家常用尺寸表达**：
- 正面：{size_positive_expressions}
- 负面：{size_negative_expressions}

**预期管理建议**：
{size_recommendation}

### 5.2 材质关注

| 指标 | 数值 |
|------|------|
| 材质提及次数 | {material_total} |
| 正面提及 | {material_positive} |
| 负面提及 | {material_negative} |

**期望差距**：
{expectation_gaps}

**预期管理建议**：
{material_recommendation}

---

## 6. Rufus问答覆盖建议（角色1+3）

| 问题主题 | 优先级 | 常见问题 | 建议覆盖位置 |
|----------|--------|----------|--------------|
{qa_rows}

### 五点覆盖矩阵建议

以下为默认建议，Phase B可根据P0真值和P1关键词调整：

| Bullet | 建议主题 | 对应Rufus问答 |
|--------|----------|---------------|
| Bullet 1 | 核心卖点/题材 | What is this? |
| Bullet 2 | 尺寸规格 | How big is it? |
| Bullet 3 | 材质工艺 | What material? |
| Bullet 4 | 场景用途 | Where to use? |
| Bullet 5 | 礼品/包装（如S2触发） | Good gift? |

---

## 附录

### A. CRD定位说明

本报告由amazon-listing-writer V6.0 Phase A生成，分析定位为**P2辅助验证层**。

在本技能体系中的优先级：
```
P0 产品真值（最高优先级）
P1 关键词库数据
P2 CRD辅助验证 ← 本报告
P3 补充信息
P4 补充信息
```

本报告的所有结论均为辅助参考，不替代P0产品真值和P1关键词库的核心驱动作用。

### B. 数据质量说明

- 评论时间范围：{date_range}
- 过滤评论数：{filtered_count}条
- 置信度档位：{confidence_level}
- 通用性过滤规则：≥2变体 OR ≥3条

### C. 分析局限性

{limitations}

---

*报告由 amazon-listing-writer V6.0 Phase A 自动生成*
*定位：P2辅助验证层（Auxiliary Validation Layer）*
```

---

## 模板变量说明

### 基础变量

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `generated_date` | string | 生成日期 YYYY-MM-DD |
| `source_file` | string | CRD文件名 |
| `total_reviews` | int | 评论总数 |
| `valid_reviews` | int | 有效评论数 |
| `vp_rate` | float | VP占比 |
| `avg_rating` | float | 平均评分 |
| `variant_count` | int | 变体数量 |
| `confidence_level` | string | HIGH/MEDIUM/LOW/VERY_LOW/INSUFFICIENT |

### 严重程度图标

| 级别 | 图标 |
|------|------|
| HIGH | ⛔ |
| MEDIUM | ⚠️ |
| LOW | ℹ️ |
