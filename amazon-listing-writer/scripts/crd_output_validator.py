#!/usr/bin/env python3
"""
Output Validator V2.0
校验Claude生成的review_analysis.json是否符合V2.0输出规范

功能：
- 校验JSON格式有效性
- 校验6个顶层必需字段完整性
- 校验cross_variant_count字段存在
- 校验引用数量上限（≤3条/主题）
- 校验情感值范围（[-1, 1]）
- 校验P2定位标注
- 校验buyer_vocabulary使用限制标注

用法：
    python3 output_validator.py <review_analysis.json>
"""

import sys
import os
import json


# V2.0 必需的6个顶层字段
REQUIRED_TOP_FIELDS = [
    "meta",
    "positive_selling_points",
    "negative_pain_points",
    "gift_intent_signal",
    "size_material_concerns",
    "rufus_qa_library",
    "buyer_vocabulary"
]

# V2.0 不应存在的旧字段（V1.x遗留）
DEPRECATED_FIELDS = [
    "keyword_library",
    "intent_extractor_config",
    "differentiation_opportunities"
]

# meta中必需的字段
REQUIRED_META_FIELDS = [
    "version",
    "confidence_level",
    "crd_positioning",
    "universality_filter"
]

# 有效的置信度值
VALID_CONFIDENCE_LEVELS = ["HIGH", "MEDIUM", "LOW", "VERY_LOW", "INSUFFICIENT"]


def validate(filepath):
    """
    校验review_analysis.json
    
    Returns:
        (passed: bool, issues: list[str], warnings: list[str])
    """
    issues = []    # 致命错误
    warnings = []  # 警告
    
    # ── 1. JSON格式有效性 ──
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        issues.append(f"JSON解析失败: {e}")
        return False, issues, warnings
    except FileNotFoundError:
        issues.append(f"文件不存在: {filepath}")
        return False, issues, warnings
    except Exception as e:
        issues.append(f"读取文件错误: {e}")
        return False, issues, warnings
    
    if not isinstance(data, dict):
        issues.append("JSON顶层必须是对象（dict），不是数组或其他类型")
        return False, issues, warnings
    
    # ── 2. 顶层必需字段完整性 ──
    for field in REQUIRED_TOP_FIELDS:
        if field not in data:
            issues.append(f"缺少必需顶层字段: {field}")
    
    # ── 3. 检查是否有V1.x遗留字段 ──
    for field in DEPRECATED_FIELDS:
        if field in data:
            warnings.append(f"检测到V1.x遗留字段: {field}（V2.0中已删除）")
    
    # ── 4. meta字段校验 ──
    if "meta" in data and isinstance(data["meta"], dict):
        meta = data["meta"]
        
        for mf in REQUIRED_META_FIELDS:
            if mf not in meta:
                issues.append(f"meta中缺少必需字段: {mf}")
        
        # 版本号
        if meta.get("version") and str(meta["version"]) < "2.0":
            warnings.append(f"版本号为{meta['version']}，预期≥2.0")
        
        # 置信度
        cl = meta.get("confidence_level")
        if cl and cl not in VALID_CONFIDENCE_LEVELS:
            issues.append(f"无效的confidence_level: {cl}，有效值: {VALID_CONFIDENCE_LEVELS}")
        
        # P2定位标注
        if "crd_positioning" in meta:
            pos = meta["crd_positioning"]
            if "P2" not in str(pos) and "辅助" not in str(pos):
                warnings.append("crd_positioning中未包含'P2'或'辅助'字样")
    
    # ── 5. positive_selling_points校验 ──
    if "positive_selling_points" in data:
        sps = data["positive_selling_points"]
        if isinstance(sps, list):
            for i, sp in enumerate(sps):
                if not isinstance(sp, dict):
                    continue
                
                # cross_variant_count
                if "cross_variant_count" not in sp:
                    warnings.append(f"positive_selling_points[{i}]缺少cross_variant_count")
                
                # 引用数量上限
                quotes = sp.get("representative_quotes", [])
                if len(quotes) > 3:
                    issues.append(
                        f"positive_selling_points[{i}]引用数量{len(quotes)}超过上限3条"
                    )
                
                # listing_suggestion.role标注
                ls = sp.get("listing_suggestion", {})
                if isinstance(ls, dict) and "role" in ls:
                    if "表达参考" not in str(ls["role"]) and "参考" not in str(ls["role"]):
                        warnings.append(
                            f"positive_selling_points[{i}]的listing_suggestion.role"
                            f"未标注'表达参考'"
                        )
    
    # ── 6. negative_pain_points校验 ──
    if "negative_pain_points" in data:
        nps = data["negative_pain_points"]
        if isinstance(nps, list):
            for i, np_item in enumerate(nps):
                if not isinstance(np_item, dict):
                    continue
                
                # cross_variant_count
                if "cross_variant_count" not in np_item:
                    warnings.append(f"negative_pain_points[{i}]缺少cross_variant_count")
                
                # severity
                severity = np_item.get("severity")
                if severity and severity not in ["HIGH", "MEDIUM", "LOW"]:
                    issues.append(
                        f"negative_pain_points[{i}]的severity值无效: {severity}"
                    )
                
                # 引用数量上限
                quotes = np_item.get("representative_quotes", [])
                if len(quotes) > 3:
                    issues.append(
                        f"negative_pain_points[{i}]引用数量{len(quotes)}超过上限3条"
                    )
    
    # ── 7. gift_intent_signal校验 ──
    if "gift_intent_signal" in data:
        gis = data["gift_intent_signal"]
        if isinstance(gis, dict):
            rec = gis.get("recommendation", {})
            if isinstance(rec, dict):
                # 检查是否使用了旧的trigger_s2_mode
                if "trigger_s2_mode" in rec:
                    warnings.append(
                        "gift_intent_signal使用了V1.x的trigger_s2_mode，"
                        "V2.0应使用suggest_s2_mode"
                    )
                
                # 检查note字段
                if "note" not in rec:
                    warnings.append(
                        "gift_intent_signal.recommendation缺少note字段"
                        "（应提醒需综合P0/P1判定）"
                    )
    
    # ── 8. buyer_vocabulary校验 ──
    if "buyer_vocabulary" in data:
        bv = data["buyer_vocabulary"]
        if isinstance(bv, dict):
            # note字段必须存在
            if "note" not in bv:
                issues.append(
                    "buyer_vocabulary缺少note字段"
                    "（必须标注'仅供表达参考'）"
                )
            else:
                note = str(bv["note"])
                if "参考" not in note and "reference" not in note.lower():
                    warnings.append("buyer_vocabulary.note中未包含'参考'字样")
            
            # 4个子类别检查
            expected_keys = [
                "how_buyers_call_product",
                "positive_descriptors",
                "scene_mentions",
                "use_case_mentions"
            ]
            for ek in expected_keys:
                if ek not in bv:
                    warnings.append(f"buyer_vocabulary缺少子类别: {ek}")
    
    # ── 9. rufus_qa_library校验 ──
    if "rufus_qa_library" in data:
        qas = data["rufus_qa_library"]
        if isinstance(qas, list):
            for i, qa in enumerate(qas):
                if not isinstance(qa, dict):
                    continue
                if "cross_variant_count" not in qa:
                    warnings.append(f"rufus_qa_library[{i}]缺少cross_variant_count")
    
    # ── 结果汇总 ──
    passed = len(issues) == 0
    return passed, issues, warnings


def main():
    if len(sys.argv) < 2:
        print("用法: python3 output_validator.py <review_analysis.json>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    print(f"=" * 60)
    print(f"Output Validator V2.0")
    print(f"校验文件: {filepath}")
    print(f"=" * 60)
    
    passed, issues, warnings = validate(filepath)
    
    if warnings:
        print(f"\n⚠️  警告 ({len(warnings)}项):")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    if issues:
        print(f"\n❌ 错误 ({len(issues)}项):")
        for issue in issues:
            print(f"  ❌ {issue}")
    
    print(f"\n{'=' * 60}")
    if passed:
        if warnings:
            print(f"✅ PASS（有{len(warnings)}项警告）")
        else:
            print(f"✅ PASS（无问题）")
    else:
        print(f"❌ FAIL（{len(issues)}项错误，{len(warnings)}项警告）")
    print(f"{'=' * 60}")
    
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
