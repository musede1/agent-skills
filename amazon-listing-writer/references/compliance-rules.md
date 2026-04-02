> **调用方**：Phase B Step B2（P0冲突初筛）、Phase B Step B5（Claude复核）
> **读取时机**：执行Step B2和Step B5前必须读取本文档

# 合规与风控检查规则

## 严禁事项

### 未经证实的功能/认证/工艺

| 禁用词 | 原因 |
|--------|------|
| handmade | 需工艺证明 |
| hand-painted | 需工艺证明 |
| UV resistant | 需测试认证 |
| waterproof | 需测试认证 |
| odorless | 需检测证明 |
| certified | 需证书编号 |
| eco-friendly | 需认证支撑 |
| non-toxic | 需安全认证 |

**规则**：除非用户明确提供证明，否则不得使用

---

### 制造误购风险

| 风险点 | 防范措施 |
|--------|----------|
| 尺寸 | 必须明确标注，含单位与换算 |
| 数量 | 单个/一对/套装必须清楚 |
| 包含物 | 有什么写什么（底座/挂钩/礼盒等） |

**正向表述原则**：只写"包含什么"，不主动写"不包含什么"

---

### 品牌/IP侵权

| 禁止项 | 说明 |
|--------|------|
| 他人品牌名 | 任何非用户自有品牌 |
| IP角色名 | Disney、Marvel等版权角色 |
| 受保护形象 | 商标、专利保护的设计 |
| 竞品品牌词 | 即使做比较也不可使用 |

### 品牌词禁用清单（严禁使用）

以下品牌词在Listing任何位置均**严禁使用**，违反将导致侵权投诉和Listing下架：

| 品牌词 | 所属公司 | 品类 |
|--------|----------|------|
| willow tree | DEMDACO | 雕像/雕塑 |
| willow | DEMDACO | 雕像/雕塑 |
| precious moments | Enesco | 雕像/雕塑 |
| hallmark | Hallmark | 礼品/雕像 |
| lenox | Lenox | 陶瓷/雕像 |
| lladro / lladró | Lladró | 陶瓷雕塑 |
| hummel | Hummel | 陶瓷雕像 |
| disney | Disney | 全品类IP |
| marvel | Marvel | 全品类IP |
| angel star | Angel Star | 天使雕像 |
| foundations | Foundations/Enesco | 雕像 |
| jim shore | Jim Shore/Enesco | 民俗雕像 |
| dept 56 / department 56 | Department 56 | 节日装饰 |
| fontanini | Fontanini | 宗教雕像 |
| nao | NAO by Lladró | 陶瓷雕塑 |

**替代表达方案**：

| 禁用词 | 替代表达 |
|--------|----------|
| willow tree style | faceless style / minimalist figure style / abstract sculptural style |
| precious moments style | cherubic style / collectible figurine style |
| lladro style | fine porcelain style / spanish ceramic style |
| hummel style | bavarian figurine style / vintage collectible style |

**检测规则**：
1. 生成前必须检查全文是否包含上述品牌词
2. 品牌词的任何变体（大小写、复数、所有格）均禁止
3. 即使描述风格也不可使用品牌词（如"willow tree style"禁止）

---

### 无法保证的效果承诺

| 禁用表达 | 原因 |
|----------|------|
| 永不褪色 | 无法保证 |
| 不碎/不破 | 无法保证 |
| 终身保修 | 需品牌授权 |
| 100%满意 | 过度承诺 |
| best/top quality | 夸大营销词 |
| #1/world's best | 无法证明 |

---

## 预期管理要求

### 必须在五点中明确的信息

1. **尺寸规格**
   - 高/宽/深
   - 必须标注单位（cm/in）
   - 只给一种单位时自动换算并标注"approx."

2. **材质**
   - 主材质
   - 表面工艺（如有）

3. **组合数量**
   - 单个/一对/套装
   - 具体数量

4. **包含物说明（正向表述原则）**
   - **有什么写什么**：含底座/挂钩等配件时说明
   - **不主动说"不包含"**：避免负面暗示影响转化
   - **有礼盒才写"含礼盒"**：无礼盒则不提

5. **使用场景限制**
   - indoor use only（如适用）
   - not suitable for outdoor use（如适用）
   - decorative item only（如适用）

### 礼盒/不包含物特殊处理

| 情况 | 处理方式 |
|------|----------|
| 有礼盒 | 写明"comes in gift box"或"includes gift packaging" |
| 无礼盒 | **不写**，不提"不含礼盒" |
| 有配件（底座/挂钩等） | 写明包含什么 |
| 无配件 | **不写**，不提"不含" |

**例外情况**：仅当CRD/差评分析明确显示买家因预期落差而投诉（如大量差评提到"以为有礼盒"），且用户主动要求时，才建议写明"does not include gift box"以降误购。此为用户决策，非默认规则。

---

## 功能词使用规则

| 功能词 | 使用条件 |
|--------|----------|
| decorative | 可自由使用（低风险） |
| indoor | 可自由使用（低风险） |
| outdoor | 仅在P0确认时使用 |
| hangable | 需有挂孔/挂钩配件 |
| watertight | 需P0明确确认 |
| can hold flowers | 需有开口且P0确认 |

---

## 风格词使用规则

### 允许使用（低争议）

- modern
- minimalist
- farmhouse
- boho / bohemian
- rustic
- contemporary
- vintage
- abstract
- classic
- traditional
- timeless
- decorative
- functional
- versatile
- sturdy

**前提**：与产品图片外观一致

### 夸大词/侵权风险词禁用清单（必须遵守）

以下词汇在Listing任何位置均**禁止使用**：

| 禁用词 | 原因 | 替代词 |
|--------|------|--------|
| stunning | 主观夸张 | striking, eye-catching |
| exquisite | 主观夸张 | detailed, intricate |
| gorgeous | 主观夸张 | attractive, appealing |
| magnificent | 主观夸张 | impressive, notable |
| amazing | 主观夸张 | remarkable, noteworthy |
| elegant | 主观夸张 | refined, sophisticated |
| premium | 主观夸张 | quality, sturdy |
| luxury | 主观夸张 | upscale, high-end |
| beautiful | 主观夸张 | attractive, decorative |
| perfect | 过度承诺 | ideal, suitable |
| best | 无法证明 | quality, reliable |
| top quality | 无法证明 | quality, sturdy |
| #1 | 无法证明 | popular, trusted |
| world's best | 无法证明 | （删除） |
| **durable** | **侵权风险** | **sturdy, solid, well-made, long-lasting** |

**例外情况**：仅当用户P0中明确定位为高端产品，且有价格档次支撑时，可酌情使用elegant/premium

---

## 自检清单（生成前必须验证）

- [ ] 所有尺寸数据来自P0或用户确认
- [ ] 所有材质/工艺来自P0或用户确认
- [ ] 无未经证实的功能宣称
- [ ] 无他人品牌/IP词
- [ ] 无夸大营销词
- [ ] 组合数量/包含物已明确（正向表述）
- [ ] 使用场景限制已标注（如适用）
- [ ] **配额词无P0真值冲突**（材质/题材/品类）

---

## 配额词与P0真值冲突检测（重要）

### 冲突类型

| 冲突类型 | 示例 | 后果 |
|----------|------|------|
| **材质冲突** | 产品是resin，使用`brass bookends` | 误导消费者材质 |
| **题材冲突** | 产品是conch，使用`starfish sculpture` | 误导消费者题材 |
| **品类冲突** | 产品是bookend，使用`tree of life statue` | 品类不匹配 |

### 处理规则

1. **材质冲突**：**必须剔除**，不可在任何位置使用
2. **题材冲突**：**必须剔除**，不可在任何位置使用
3. **品类冲突**：评估是否兼容，不兼容则剔除

### 执行检查

在使用脚本输出的配额词前，Claude必须逐一检查：

```
配额词: brass bookends
P0材质: resin
检查: brass ≠ resin → 材质冲突 → 剔除，使用下一个候选词
```

**违反此规则将导致误导消费者，属于严重合规问题。**

---

## Step B5 Claude复核清单（强制执行）

在coverage_checker.py脚本检测通过后，Claude必须执行以下四项人工复核。任一项不通过则修改后返回Step B4重新检测。

### 5.1 品牌词二次检测

脚本只能检测已知品牌词，Claude需要检测未知品牌词：

识别可疑品牌词特征：
- 首字母大写的专有名词（非通用词）
- 看起来像公司名/人名的词组
- 竞品关键词库中反复出现但与产品功能无关的词

处理方式：
- 确认是品牌词 → 直接删除
- 疑似品牌词（高度可疑） → 直接删除
- **原则：宁可错杀，不可放过（API调用无法二次确认）**

### 5.2 P0冲突复核

- [ ] 配额词无P0真值冲突（材质/题材/品类）
- [ ] 已剔除的冲突词没有误判
- [ ] 写入的词没有遗漏冲突

### 5.3 真值覆盖检测

- [ ] ≥8个P0真值点已覆盖
- [ ] 无虚假宣称
- [ ] 无未经证实的功能宣称

### 5.4 颜色词检测

- [ ] 标题无具体颜色词
- [ ] 五点无具体颜色词
- [ ] Search Terms无具体颜色词
- [ ] 长描述无具体颜色词
