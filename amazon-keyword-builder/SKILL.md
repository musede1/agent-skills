---
name: amazon-keyword-builder
description: |
  亚马逊广告关键词提炼与建库技能（Amazon PPC Keyword Builder）。用于新品期前期建库/出方案：生成BMM广泛种子词和预置Exact精准词池。
  
  触发场景：
  - 用户需要提炼亚马逊广告关键词/广告词
  - 用户提供产品属性卡+竞品关键词库，需要生成BMM种子词和Exact精准词
  - 用户需要分析产品图并生成广告投放方案
  - 用户提到"加号广泛"、"BMM"、"广泛匹配修饰符"、"Exact精准词"等亚马逊广告术语
  
  核心能力：
  - 产品图识别与兜底分析（识图推断题材/功能/工艺）
  - 竞品关键词库清洗与标注
  - BMM广泛种子词生成（LayerA/B/C/颜色组/品牌词专组）
  - 预置Exact精准词生成
  - 通过 exec + curl POST 提交结构化结果
  
---

# Amazon Keyword Builder（亚马逊广告关键词提炼技能）

**版本：V9.5.4**

## 任务范围

仅限**前期建库/出方案**：生成BMM种子词、预置Exact、品牌词专组

---

## 处理流程

```
Step 0: 运行量化脚本 → Step 1: 识图兜底 → Step 2: 综合判定 → Step 3: 生成方案 → Step 4: 输出JSON
```

### Step 0: 运行量化分析脚本（必须首先执行）

```bash
python3 scripts/keyword_analyzer.py <关键词文件> [L1词] [输出JSON]
```

脚本输出：L1候选、L2准入、LayerC启用判定、颜色词、品牌词、CT分布

### Step 1: 识图兜底

识别：产品大类、功能结构、题材对象、表面工艺。置信度≥0.7可作为候选。

### Step 2: 综合判定

L1优先级：用户指定 > 脚本题材词 > 识图推断

### Step 3: 基于脚本结果生成方案

严格按脚本量化结果组装BMM/Exact，详见 references/layer-templates.md

---

## 全局硬规则

1. BMM规则：只给"锚点词"加"+"；CT默认不加"+"
2. LayerC禁用L1：关键词中不允许出现L1/L2/题材词
3. 颜色组来源：只使用脚本从关键词库提取的颜色
4. L2来源：只使用脚本验证通过的L2
5. 品牌词隔离：必须独立专组，不混入普通组
6. CT规则：同一条关键词只保留一个CT；CT变体输出上限2-5个

---

## 输入要求

### A. 产品属性卡
站点、类目、功能属性、材质、L1题材词（必填）；工艺、L2（可选）

### B. 竞品关键词库
.xlsx/.csv 文件，含关键词、搜索量、自然排名

### C. 产品图（建议）

---

## 参考文档

- references/quantitative-rules.md（量化判定规则）
- references/layer-templates.md（Layer生成模板）
- references/exact-rules.md（Exact规则）
- references/naming-standards.md（分组命名标准）

---

# ⚠️ 输出硬规则（必须严格遵守）

## 输出方式

**完成分析后，使用 exec 工具执行 curl 命令将 JSON 结果 POST 提交到任务指令中指定的地址。**

### 提交方式

按以下两步提交（解决中文编码问题）：

1. 用 `write` 工具将完整 JSON 写入临时文件（路径从任务指令获取）
   文件内容格式：`{"task_id":"xxx","sheet1":[...],"sheet2":[...]}`
2. 用 `exec` 工具执行：`curl -s -X POST <提交URL> -H "Content-Type: application/json" -d @<临时文件路径>`

提交成功返回 `{"ok":true}`，确认成功后再结束任务。

### Sheet1 每条数据字段（全部必填，共14个）

| 字段 | 说明 |
|------|------|
| 分组 | 分组名称，按命名标准 |
| 关键词 | BMM格式，锚点词加"+" |
| 翻译 | 中文翻译 |
| 层级 | LayerA/LayerB/LayerC/颜色组 |
| 优先级 | P1/P2/P3/P4 |
| 精准度评分 | 整数或"无" |
| 颜色 | 颜色值或"无" |
| 用途 | "广泛匹配" |
| 参考搜索量 | 整数或"无" |
| 参考自然排名 | 整数或"无" |
| 关键词来源 | 关键词库/属性卡/产品图 等 |
| 风险标记 | 风险描述或"无" |
| 建议广告组 | 广告组名称 |
| 备注 | 补充说明或"无" |

### Sheet2 每条数据字段（全部必填，共14个）

与Sheet1相同，额外增加：
| 字段 | 说明 |
|------|------|
| 匹配方式 | "Exact" |

### ❌ 禁止事项

1. 禁止直接输出 JSON 文本作为回复
2. 禁止输出"以下是方案"、"生成完成"等说明
3. 禁止空字段（空值必须用"无"填充）

### ✅ 必须事项

1. 使用 exec + curl POST 提交结果
2. 所有字段必须填写，不允许空值
3. sheet1 和 sheet2 都必须有数据
4. 确认 curl 返回 {"ok":true} 后再结束

---

## 提交前自检清单（内部执行，不输出）

- [ ] sheet1 和 sheet2 都有数据
- [ ] 每条数据所有字段已填写，无空值
- [ ] 分组命名符合标准
- [ ] 使用 exec + curl POST 提交并确认返回 ok

---

## 分组命名标准

### Sheet1 分组名（固定）

- LayerA_A0基础覆盖
- LayerA_A0特征强化
- LayerA_A1功能结构
- LayerA_A1场景礼品
- LayerA_L1备选-{题材英文}
- LayerB_L2上位类扩量
- 颜色组
- LayerC-功能
- LayerC-材质
- LayerC-工艺
- LayerC-表面工艺光感
- LayerC-摆放位置
- LayerC-风格
- LayerC-空间场景
- LayerC-品牌
- 拼写组

### Sheet2 分组名（固定）

- Exact-E1核心成交
- Exact-E2高意图长尾
- Exact-E3颜色变体
- Exact-E4防御扩量
- 品牌词-Exact
