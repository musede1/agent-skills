# Product Positioning Knowledge Base

该目录保存 `product-Positioning` 技能的知识库数据。

## 当前数据格式（row-only）
所有运行时数据都使用数组结构，不再使用 `sheets -> <sheet_name>`：

- `json/audience_rows.json`
- `json/theme_rows.json`
- `json/scene_rows.json`
- `json/style_rows.json`
- `json/manifest.json`

每个 `*_rows.json` 文件结构：

```json
[
  {"字段A": "值A", "字段B": "值B"},
  {"字段A": "值A2", "字段B": "值B2"}
]
```

## 从 XLSX 重新生成
在仓库根目录运行：

```bash
python .claude/skills/product-Positioning/scripts/xlsx_to_json.py
```

默认行为：
- 开启 `--row-only`
- 自动生成四个标准文件：`audience_rows.json/theme_rows.json/scene_rows.json/style_rows.json`
- 生成 `manifest.json`

可选参数：

```bash
python .claude/skills/product-Positioning/scripts/xlsx_to_json.py --no-row-only
python .claude/skills/product-Positioning/scripts/xlsx_to_json.py --keep-workbook-json
```

## 校验建议
每次重生后建议检查：
1. 行数是否符合预期（人群7、题材41、场景84、风格66）。
2. 关键字段是否存在：
- 人群：`人群ID`
- 题材：`题材编码`
- 场景：`场景ID`
- 风格：`风格组合ID_F`
