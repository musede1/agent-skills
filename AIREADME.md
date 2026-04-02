# AI 交接文档 — Skills（AI 技能）

本文档面向接手开发的 AI 会话，记录三个 OpenClaw 技能的架构、修改历史和注意事项。

## 一、技能列表

| 技能 | 目录 | 用途 | 版本 |
|------|------|------|------|
| amazon-keyword-builder | `amazon-keyword-builder/` | 亚马逊广告关键词生成（BMM 广泛 + Exact 精准）| V9.5.4 |
| amazon-listing-writer | `amazon-listing-writer/` | 亚马逊 Listing 文案撰写（标题/五点/Search Terms/长描述）| V6.1 |
| amazon-main-video | `amazon-main-video/` | 亚马逊主图视频提示词生成（三阶段：定位→脚本→分镜）| — |

## 二、统一的结果提交方式

### 2.1 当前方案：write 文件 + exec curl POST

所有技能完成后不直接输出文本，而是：

1. 用 `write` 工具将 JSON 写入 `/tmp/result_{task_id}.json`
2. 用 `exec` 工具执行 `curl -s -X POST http://42.194.187.253:5680/feishu_api/openclaw/submit -H "Content-Type: application/json" -d @/tmp/result_{task_id}.json`
3. 确认返回 `{"ok":true}` 后结束

### 2.2 为什么用这个方案

| 尝试过的方案 | 结果 | 问题 |
|-------------|------|------|
| 直接输出 TOON 文本 | ❌ | 内容被 deliver 回调分块截断 |
| 直接输出 JSON 文本 | ❌ | 同上，deliver 分块问题 |
| 插件注册 tool（submit_keyword_result）| ❌ | 工具注册成功但 AI 看不到，疑似 coding profile 限制 |
| web_fetch POST | ❌ | web_fetch 只支持 GET |
| exec curl -d '...' | ❌ | Windows PowerShell 中文乱码 |
| **write 文件 + exec curl -d @文件** | **✅** | 当前使用方案 |

### 2.3 提交 URL 和 task_id

- URL：`http://42.194.187.253:5680/feishu_api/openclaw/submit`（Fastify 通过穿透暴露）
- task_id：由 Fastify 生成，嵌入在发给 AI 的提示词中
- Fastify 的 `waitForHttpResult(taskId)` 等待此 task_id 的 HTTP 提交

## 三、各技能详情

### 3.1 amazon-keyword-builder

**输入**：产品图片 URL + 关键词文件 URL + 产品属性卡文本

**处理流程**：
```
Step 0: 运行 keyword_analyzer.py（量化分析）
Step 1: 识图兜底
Step 2: 综合判定
Step 3: 生成方案
Step 4: 输出 JSON（write + curl）
```

**提交 JSON 格式**：
```json
{
  "task_id": "uuid",
  "sheet1": [
    { "分组": "...", "关键词": "...", "翻译": "...", "层级": "...", "优先级": "P1", "精准度评分": 96, "颜色": "无", "用途": "广泛匹配", "参考搜索量": 381, "参考自然排名": 16, "关键词来源": "关键词库", "风险标记": "无", "建议广告组": "...", "备注": "无" }
  ],
  "sheet2": [
    { "分组": "...", "匹配方式": "Exact", "关键词": "...", "翻译": "...", "优先级": "P1", "精准度评分": 97, "颜色": "无", "用途": "精准匹配", "参考搜索量": 381, "参考自然排名": 16, "关键词来源": "关键词库", "风险标记": "无", "建议广告组": "...", "备注": "无" }
  ]
}
```

**历史修改**：
- 原版输出 TOON 文本，已改为 JSON + curl 提交
- 删除了 `references/toon-format.md`
- 移除了模型指定要求（原要求 Claude Opus 4.5，已删除）
- SKILL.md 版本从 V9.5.3 升级到 V9.5.4

**脚本**：`scripts/keyword_analyzer.py`（量化分析，AI 在 Step 0 执行）

### 3.2 amazon-listing-writer

**输入**：产品图片 URL + 关键词文件 URL + 评论文件 URL + 产品属性卡文本

**处理流程**：
```
Phase A（可选）: CRD 竞品评论分析（4 步）
Phase B（必选）: Listing 撰写（6 步）
  B0: P0信息整合
  B1: 关键词分析（intent_extractor.py）
  B2: P0冲突初筛
  B3: 生成初稿
  B4: 脚本检测（coverage_checker.py，最多3轮）
  B5: Claude复核
  B6: write + curl 提交
```

**提交 JSON 格式**：
```json
{
  "task_id": "uuid",
  "data": {
    "marketplace": "US",
    "language": "en",
    "title": "...",
    "bullet1": "...",
    "bullet2": "...",
    "bullet3": "...",
    "bullet4": "...",
    "bullet5": "...",
    "search_terms": "...",
    "description": "..."
  }
}
```

**重要：data 中禁止包含 toon、validation 或任何非 Listing 字段。**

**历史修改**：
- 删除了 `references/toon-format.md`
- 删除了 `references/description-rules.md` 中的 TOON 输出特殊要求章节
- `scripts/coverage_checker.py` 升级到 V2.0：
  - `load_listing` 从 TOON 格式解析改为 JSON 格式解析
  - 删除了 `check_toon_format` 函数及所有调用
  - 移除了退出码 4（TOON 格式错误）
- SKILL.md Step B4 检测项中移除了 "TOON格式"
- SKILL.md Step B6 从"直接输出TOON"改为 write + curl 提交

**脚本**：
- `scripts/intent_extractor.py`（关键词配额分配）
- `scripts/coverage_checker.py`（V2.0，JSON 输入，质量检测）
- `scripts/crd_preprocessor.py`（CRD 评论预处理）
- `scripts/crd_output_validator.py`（CRD 输出校验）

### 3.3 amazon-main-video

**输入**：产品图片 URL + 关键词文件 URL + 评论文件 URL + 产品属性卡文本

**处理流程**（三阶段，全自动无人工介入）：
```
阶段1: 产品定位（P1-positioning.md）
阶段2: 视频脚本生成（P2-script.md）
阶段3: 分镜生成（P3-storyboard.md）
```

**提交 JSON 格式**：
```json
{
  "task_id": "uuid",
  "data": {
    // 阶段1: 定位包
    // 阶段2: 风格 + 视觉参数 + 叙事主线 + 脚本
    // 阶段3: 分镜JSON / Shot提示词
  }
}
```

**历史修改**：
- 第八节从"最终输出内容"改为"最终提交方式"（write + curl）

## 四、注意事项

### 4.1 URL 硬编码

提交 URL `http://42.194.187.253:5680/feishu_api/openclaw/submit` 出现在：
- Fastify 的 `services/adListing.ts`（每个任务的提示词中）
- 三个 SKILL.md 的提交方式说明中（通用描述，实际 URL 从提示词获取）

如果穿透地址变了，需要同时更新 Fastify 提示词代码。

### 4.2 skill 路径问题

OpenClaw 日志中反复出现：
```
[skills] Skipping skill path that resolves outside its configured root.
```
这表示 skill 的路径解析有问题，可能导致 AI 找不到 skill 文件。需要排查 OpenClaw 的 skills 配置。

### 4.3 coverage_checker.py 输入格式变更

V2.0 改为接受 JSON 文件输入，AI 在 Step B4 调用时需要先把 Listing 写成 JSON 文件再传给脚本。SKILL.md 中的 `--listing` 参数说明已更新。

### 4.4 不要在 skill 里引用 toon-format.md

已删除的文件。如果 AI 在执行中尝试读取会报错，这是正常的——不需要这个文件。
