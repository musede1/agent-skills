> **调用方**：Phase A Step A1（CRD数据预处理）
> **读取时机**：执行Step A1前必须读取本文档

# CRD文件输入规范

## CRD（Competitor Review Dataset）定义

CRD是本技能的标准输入数据，指竞品评论原始数据集。

### CRD文件命名建议

推荐格式：`CRD_{主ASIN或品类}_{站点}_{条数}.xlsx`

示例：
- `CRD_B0D7V67BNX_US_145.xlsx`
- `CRD_FacePlanter_US_80.xlsx`
- `CRD_AngelFigurine_US_200.xlsx`

---

## 必需列

| 列名 | 数据类型 | 说明 | 示例 |
|------|----------|------|------|
| `ASIN` | String | 竞品ASIN编号 | B0D7V67BNX |
| `标题` | String | 评论标题 | "Love this planter!" |
| `内容` | String | 评论正文（分析主体） | "Very cute! Love the colors..." |
| `星级` | Integer | 星级1-5 | 5 |
| `型号` | String | 变体/款式名称 | "Style: Classic" |

### 必需列的用途

| 列名 | 用途 |
|------|------|
| `ASIN` | 区分不同竞品，多竞品合并分析时标识来源 |
| `标题` | 评论标题往往是买家核心态度的浓缩，与内容合并分析 |
| `内容` | 分析主体，所有维度的洞察均从此提取 |
| `星级` | 情感分组基础（4-5星=正面，3星=中性，1-2星=负面） |
| `型号` | 通用性过滤校验：计算cross_variant_count，判断洞察是否跨变体通用 |

---

## 可选列

| 列名 | 数据类型 | 说明 | 缺失时处理 |
|------|----------|------|-----------|
| `VP评论` | String (Y/N) | 是否Verified Purchase评论 | 默认全部视为VP，权重=1.0 |
| `赞同数` | Integer | 评论赞同数/有用票数 | 默认0，不加权 |
| `评论时间` | Date/String | 评论日期 | 忽略时间维度分析 |

### 可选列的用途

| 列名 | 用途 |
|------|------|
| `VP评论` | VP评论权重×1.5，非VP评论权重×1.0 |
| `赞同数` | 高赞评论在选择代表性引用时优先 |
| `评论时间` | 标注数据时间跨度（不影响分析逻辑） |

---

## 列名兼容映射

脚本（crd_preprocessor.py）自动识别以下列名变体，**优先匹配中文列名**：

| 标准列名 | 兼容别名（中文） | 兼容别名（英文） |
|----------|-----------------|-----------------|
| `内容` | 评论内容, 评论正文 | review_text, text, comment, body, content, review |
| `星级` | 评分 | rating, star, stars, score, rate |
| `标题` | 评论标题 | review_title, title, headline, subject |
| `ASIN` | — | asin |
| `型号` | 变体, 款式, 子体 | variant, style, model |
| `VP评论` | VP, 验证购买 | verified_purchase, verified, vp, is_verified |
| `赞同数` | 有用数, 有用票数 | helpful_votes, helpful, votes, upvotes |
| `评论时间` | 日期 | date, review_date, time, timestamp, created_at |

---

## 不需要的列（建议在CRD文件中删除）

| 不需要的列 | 理由 |
|-----------|------|
| 评论人主页/个人链接 | 对分析零贡献，增加噪音 |
| Vine Voice评论 | 通常全部为空，且分析逻辑与VP一致 |
| 所属国家 | 通常单一站点数据，区分度极低 |

---

## 数据质量要求

### 5档置信度与最低数据量

| 评论总数 | 置信度标签 | 输出策略 |
|---------|-----------|---------|
| ≥100条 | `HIGH` | 正常输出5大维度 |
| 50-99条 | `MEDIUM` | 正常输出，阈值放宽 |
| 20-49条 | `LOW` | 仅输出明确信号，弱信号标注"待验证" |
| 10-19条 | `VERY_LOW` | 仅输出定性描述，不做定量统计 |
| <10条 | `INSUFFICIENT` | 仅输出原始评论摘要，不做分析结论 |

### 数据清洗规则

脚本（crd_preprocessor.py）自动执行：

1. **去除空评论**：`内容`为空或仅空白字符
2. **去除重复**：完全相同的评论内容
3. **去除超短评论**：<10字符（如"good", "ok"）→ 标记为`filtered`
4. **星级校验**：非1-5的值标记为无效
5. **编码处理**：自动检测UTF-8/GBK/Latin-1

### 缺失字段容错

| 缺失情况 | 处理方式 |
|----------|----------|
| `VP评论`列不存在 | 默认全部视为VP，weight=1.0 |
| `赞同数`列不存在 | 默认全部为0，不加权 |
| `评论时间`列不存在 | 跳过时间维度，meta中date_range标注"N/A" |
| `型号`列不存在 | 视为单一变体，跳过通用性过滤条件A |

---

## 文件格式支持

| 格式 | 扩展名 | 支持状态 |
|------|--------|----------|
| Excel | .xlsx, .xls | ✅ 完全支持 |
| CSV | .csv | ✅ 完全支持（UTF-8优先） |
| TSV | .tsv | ✅ 完全支持 |

### CSV编码处理

```bash
# 指定编码
python3 crd_preprocessor.py reviews.csv --encoding gbk
```

---

## 补充输入参数

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--category` | 产品品类 | 自动检测 |
| `--site` | 目标站点 | US |
| `--focus` | 分析侧重点 | 无 |
| `--output` | 输出目录 | ./output/ |

### 示例

```bash
# 基础用法
python3 crd_preprocessor.py CRD_B0D7V67BNX_US_145.xlsx --output ./analysis/

# 指定品类和侧重点
python3 crd_preprocessor.py CRD_file.xlsx \
  --category "planter" \
  --focus "gift,size" \
  --output ./analysis/
```
