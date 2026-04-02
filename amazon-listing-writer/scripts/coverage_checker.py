#!/usr/bin/env python3
"""
Amazon Listing Writer - Listing质量检查脚本
版本: V2.0

功能:
1. 检查生成的Listing是否覆盖了必埋词清单
2. 检测品牌词侵权风险（V1.1新增）
3. 检测各字段长度是否符合规范（V1.2新增）
4. 部分覆盖判定：词根全部存在即计入覆盖率（V1.4新增）
5. 标题词根重复检测：单复数独立计，每词根≤2次（V1.5新增）
6. 新增durable为侵权风险词（V1.6新增）
7. V2.0：改为JSON格式输入，移除TOON格式检测

使用方法:
    python3 coverage_checker.py --listing listing.json --keywords intent_result.json [--output coverage_report.json]

参数说明:
    --listing: Listing JSON文件（含title/bullet1-5/search_terms/description字段）
    --keywords: intent_extractor.py输出的JSON文件
    --output: 输出报告路径，默认为 coverage_report.json

退出码:
    0 = 全部通过
    1 = 覆盖率不足80%
    2 = 品牌词侵权
    3 = 长度不合规
    5 = 标题词根重复
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple



# ============================================================
# 长度规范配置
# ============================================================
LENGTH_RULES = {
    "title": {"max": 190, "target_min": 150, "target_max": 190},
    "bullet": {"min": 170, "max": 250, "target_min": 170, "target_max": 230},
    "search_terms_bytes": {"min": 230, "max": 250},
    "description": {"min": 1200, "max": 1900}
}


# ============================================================
# 品牌词黑名单（严禁使用）
# ============================================================
BRAND_BLACKLIST = {
    # 雕像/雕塑品牌
    "willow tree", "willow", "precious moments", "hallmark",
    "lenox", "lladro", "lladró", "hummel", "angel star",
    "foundations", "jim shore", "dept 56", "department 56",
    "fontanini", "nao",
    # IP品牌
    "disney", "marvel", "pixar", "star wars", "harry potter",
    "sanrio", "hello kitty", "pokemon", "pikachu",
    # 其他常见品牌
    "yankee candle", "bath body works", "swarovski"
}


# ============================================================
# 夸大词/侵权风险词黑名单
# ============================================================
EXAGGERATION_BLACKLIST = {
    "stunning", "exquisite", "gorgeous", "magnificent", "amazing",
    "elegant", "premium", "luxury", "beautiful", "perfect",
    "best", "top quality", "#1", "world's best",
    "durable"  # V1.6新增：侵权风险词
}


def check_brand_violations(text: str) -> List[str]:
    """
    检测文本中是否包含品牌词
    返回: 检测到的品牌词列表
    """
    text_lower = text.lower()
    violations = []
    for brand in BRAND_BLACKLIST:
        # 使用词边界匹配，避免误判
        pattern = r'\b' + re.escape(brand) + r'\b'
        if re.search(pattern, text_lower):
            violations.append(brand)
    return violations


def check_exaggeration_words(text: str) -> List[str]:
    """
    检测文本中是否包含夸大词
    返回: 检测到的夸大词列表
    """
    text_lower = text.lower()
    violations = []
    for word in EXAGGERATION_BLACKLIST:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, text_lower):
            violations.append(word)
    return violations


def check_title_word_repetition(title: str) -> Dict:
    """
    检测标题词根重复（V1.5新增）
    规则：单数/复数视为独立词根，每个词根≤2次
    """
    # 提取所有单词并转小写
    words = re.findall(r'[a-zA-Z]+', title.lower())
    
    # 统计每个词出现次数
    word_count = {}
    for word in words:
        if len(word) > 1:  # 忽略单字母
            word_count[word] = word_count.get(word, 0) + 1
    
    # 检测超过2次的词
    violations = []
    for word, count in word_count.items():
        if count > 2:
            violations.append(f"'{word}' 出现{count}次（最多2次）")
    
    # 返回出现2次及以上的词（用于报告展示）
    repeated_words = {k: v for k, v in word_count.items() if v >= 2}
    
    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "word_counts": repeated_words
    }


def check_length_compliance(listing_raw: Dict[str, str]) -> Dict:
    """
    检测各字段长度是否符合规范
    返回: 长度检测报告
    """
    results = {
        "passed": True,
        "title": {"length": 0, "max": 190, "status": "✅", "passed": True},
        "bullets": [],
        "search_terms": {"bytes": 0, "min": 230, "max": 250, "status": "✅", "passed": True},
        "description": {"length": 0, "min": 1200, "max": 1900, "status": "✅", "passed": True},
        "violations": []
    }
    
    # 标题长度
    title_len = len(listing_raw.get("title_raw", ""))
    results["title"]["length"] = title_len
    if title_len > LENGTH_RULES["title"]["max"]:
        results["title"]["status"] = f"❌ 超出{title_len - 190}字符"
        results["title"]["passed"] = False
        results["passed"] = False
        results["violations"].append(f"标题超出上限: {title_len}/190字符")
    elif title_len < LENGTH_RULES["title"]["target_min"]:
        results["title"]["status"] = f"⚠️ 偏短"
    
    # 五点长度
    bullets_raw = listing_raw.get("bullets_raw", [])
    for i, bullet in enumerate(bullets_raw, 1):
        b_len = len(bullet)
        b_result = {"index": i, "length": b_len, "min": 170, "max": 250, "status": "✅", "passed": True}
        
        if b_len > LENGTH_RULES["bullet"]["max"]:
            b_result["status"] = f"❌ 超出{b_len - 250}字符"
            b_result["passed"] = False
            results["passed"] = False
            results["violations"].append(f"Bullet{i}超出上限: {b_len}/250字符")
        elif b_len < LENGTH_RULES["bullet"]["min"]:
            b_result["status"] = f"❌ 不足{170 - b_len}字符"
            b_result["passed"] = False
            results["passed"] = False
            results["violations"].append(f"Bullet{i}低于下限: {b_len}/170字符")
        elif b_len > LENGTH_RULES["bullet"]["target_max"]:
            b_result["status"] = f"⚠️ 接近上限"
        
        results["bullets"].append(b_result)
    
    # Search Terms字节数
    st_raw = listing_raw.get("search_terms_raw", "")
    st_bytes = len(st_raw.encode('utf-8'))
    results["search_terms"]["bytes"] = st_bytes
    if st_bytes < LENGTH_RULES["search_terms_bytes"]["min"]:
        results["search_terms"]["status"] = f"❌ 不足{230 - st_bytes}bytes"
        results["search_terms"]["passed"] = False
        results["passed"] = False
        results["violations"].append(f"Search Terms不足: {st_bytes}/230-250 bytes")
    elif st_bytes > LENGTH_RULES["search_terms_bytes"]["max"]:
        results["search_terms"]["status"] = f"❌ 超出{st_bytes - 250}bytes"
        results["search_terms"]["passed"] = False
        results["passed"] = False
        results["violations"].append(f"Search Terms超出: {st_bytes}/250 bytes")
    
    # 长描述长度
    desc_raw = listing_raw.get("description_raw", "")
    desc_len = len(desc_raw)
    results["description"]["length"] = desc_len
    if desc_len < LENGTH_RULES["description"]["min"]:
        results["description"]["status"] = f"❌ 不足{1200 - desc_len}字符"
        results["description"]["passed"] = False
        results["passed"] = False
        results["violations"].append(f"长描述不足: {desc_len}/1200-1900字符")
    elif desc_len > LENGTH_RULES["description"]["max"]:
        results["description"]["status"] = f"❌ 超出{desc_len - 1900}字符"
        results["description"]["passed"] = False
        results["passed"] = False
        results["violations"].append(f"长描述超出: {desc_len}/1900字符")
    
    return results


def load_listing(filepath: str) -> Tuple[Dict[str, str], Dict[str, any]]:
    """
    加载Listing JSON文件，提取各部分内容
    返回: (用于覆盖率检测的小写文本, 用于长度检测的原始文本)
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")

    content = path.read_text(encoding='utf-8')
    data = json.loads(content)

    title = data.get("title", "")
    bullets = [data.get(f"bullet{i}", "") for i in range(1, 6)]
    search_terms = data.get("search_terms", "")
    description = data.get("description", "")
    bullets_text = ' '.join(bullets)
    full_text = f"{title} {bullets_text} {search_terms} {description}"

    # 用于覆盖率检测（小写）
    listing = {
        "title": title.lower(),
        "bullets": bullets_text.lower(),
        "search_terms": search_terms.lower(),
        "description": description.lower(),
        "full_text": full_text.lower()
    }

    # 用于长度检测（原始大小写）
    listing_raw = {
        "title_raw": title,
        "bullets_raw": bullets,
        "search_terms_raw": search_terms,
        "description_raw": description
    }

    return listing, listing_raw


def check_keyword_coverage(listing: Dict[str, str], keyword: str) -> Dict[str, any]:
    """
    检查单个关键词在Listing各部分的覆盖情况
    V1.4更新：增加部分覆盖判定（词根全部存在但顺序不同）
    """
    kw_lower = keyword.lower()
    words = kw_lower.split()
    
    # 检查完整词组匹配
    pattern = r'\b' + re.escape(kw_lower).replace(r'\ ', r'\s+') + r'\b'
    
    # 完整匹配检测
    exact_in_title = bool(re.search(pattern, listing["title"]))
    exact_in_bullets = bool(re.search(pattern, listing["bullets"]))
    exact_in_st = bool(re.search(pattern, listing["search_terms"]))
    exact_in_desc = bool(re.search(pattern, listing["description"]))
    exact_in_any = bool(re.search(pattern, listing["full_text"]))
    
    # 部分覆盖检测（所有词根都存在）
    def check_partial(text: str) -> bool:
        text_lower = text.lower()
        return all(re.search(r'\b' + re.escape(w) + r'\b', text_lower) for w in words)
    
    partial_in_title = check_partial(listing["title"]) if not exact_in_title else False
    partial_in_bullets = check_partial(listing["bullets"]) if not exact_in_bullets else False
    partial_in_st = check_partial(listing["search_terms"]) if not exact_in_st else False
    partial_in_desc = check_partial(listing["description"]) if not exact_in_desc else False
    partial_in_any = check_partial(listing["full_text"]) if not exact_in_any else False
    
    # 综合判定：完整覆盖或部分覆盖都算覆盖
    covered_in_title = exact_in_title or partial_in_title
    covered_in_bullets = exact_in_bullets or partial_in_bullets
    covered_in_any = exact_in_any or partial_in_any
    
    return {
        "in_title": exact_in_title,
        "in_bullets": exact_in_bullets,
        "in_search_terms": exact_in_st,
        "in_description": exact_in_desc,
        "in_any": exact_in_any,
        # V1.4新增：部分覆盖标记
        "partial_in_title": partial_in_title,
        "partial_in_bullets": partial_in_bullets,
        "partial_in_any": partial_in_any,
        # V1.4新增：综合覆盖判定（完整或部分都算覆盖）
        "covered_in_title_or_bullets": covered_in_title or covered_in_bullets,
        "covered_in_any": covered_in_any
    }


def generate_coverage_report(listing: Dict[str, str], listing_raw: Dict[str, any], keywords_data: Dict, filepath: str) -> Dict:
    """
    生成完整质量检测报告
    """
    allocation = keywords_data.get("allocation", {})
    
    report = {
        "summary": {
            "title_coverage": {"required": 0, "covered": 0, "rate": 0},
            "bullet_coverage": {"required": 0, "covered": 0, "rate": 0},
            "overall_coverage": {"required": 0, "covered": 0, "rate": 0},
            "brand_check": {"passed": True, "violations": []},
            "exaggeration_check": {"passed": True, "violations": []},
            "length_check": {"passed": True, "violations": []},
            "title_repetition_check": {"passed": True, "violations": []}  # V1.5新增
        },
        "length_details": {},
        "title_repetition_details": {},  # V1.5新增
        "title_keywords": [],
        "bullet_keywords": [],
        "st_keywords_sample": [],
        "missing_critical": [],
        "brand_violations": [],
        "exaggeration_violations": [],
        "recommendations": []
    }
    
    # 长度检测（V1.2新增）
    length_results = check_length_compliance(listing_raw)
    report["length_details"] = length_results
    report["summary"]["length_check"]["passed"] = length_results["passed"]
    report["summary"]["length_check"]["violations"] = length_results["violations"]
    if not length_results["passed"]:
        for v in length_results["violations"]:
            report["recommendations"].insert(0, f"⚠️ 长度问题: {v}")
    
    # 标题词根重复检测（V1.5新增）
    title_raw = listing_raw.get("title_raw", "")
    repetition_results = check_title_word_repetition(title_raw)
    report["title_repetition_details"] = repetition_results
    report["summary"]["title_repetition_check"]["passed"] = repetition_results["passed"]
    report["summary"]["title_repetition_check"]["violations"] = repetition_results["violations"]
    if not repetition_results["passed"]:
        for v in repetition_results["violations"]:
            report["recommendations"].insert(0, f"🚨 标题词根重复: {v}")
    
    # 品牌词检测
    brand_violations = check_brand_violations(listing["full_text"])
    if brand_violations:
        report["summary"]["brand_check"]["passed"] = False
        report["summary"]["brand_check"]["violations"] = brand_violations
        report["brand_violations"] = brand_violations
        report["recommendations"].insert(0, f"🚨 严重：检测到品牌词侵权风险！发现: {', '.join(brand_violations)}")
    
    # 夸大词检测（V1.2新增）
    exaggeration_violations = check_exaggeration_words(listing["full_text"])
    if exaggeration_violations:
        report["summary"]["exaggeration_check"]["passed"] = False
        report["summary"]["exaggeration_check"]["violations"] = exaggeration_violations
        report["exaggeration_violations"] = exaggeration_violations
        report["recommendations"].insert(0, f"⚠️ 发现夸大词: {', '.join(exaggeration_violations)}")
    
    # 检查标题配额词
    for kw_info in allocation.get("title_keywords", []):
        kw = kw_info["keyword"]
        coverage = check_keyword_coverage(listing, kw)
        
        # V1.4更新：区分完整覆盖和部分覆盖
        if coverage["in_title"] or coverage["in_bullets"]:
            status_text = "✓ 完整覆盖"
        elif coverage["partial_in_title"] or coverage["partial_in_bullets"]:
            status_text = "✓ 部分覆盖"
        else:
            status_text = "✗ 缺失"
        
        status = {
            "keyword": kw,
            "rank": kw_info.get("rank"),
            "priority_score": kw_info.get("priority_score"),
            "coverage": coverage,
            "status": status_text
        }
        report["title_keywords"].append(status)
        
        report["summary"]["title_coverage"]["required"] += 1
        # V1.4更新：完整覆盖或部分覆盖都计入覆盖率
        if coverage["covered_in_title_or_bullets"]:
            report["summary"]["title_coverage"]["covered"] += 1
        else:
            report["missing_critical"].append({
                "keyword": kw,
                "level": "P0_TITLE",
                "suggestion": f"建议添加到标题或五点: {kw}"
            })
    
    # 检查五点配额词
    for kw_info in allocation.get("bullet_keywords", []):
        kw = kw_info["keyword"]
        coverage = check_keyword_coverage(listing, kw)
        
        # V1.4更新：区分完整覆盖和部分覆盖
        if coverage["in_any"]:
            status_text = "✓ 完整覆盖"
        elif coverage["partial_in_any"]:
            status_text = "✓ 部分覆盖"
        else:
            status_text = "✗ 缺失"
        
        status = {
            "keyword": kw,
            "rank": kw_info.get("rank"),
            "priority_score": kw_info.get("priority_score"),
            "coverage": coverage,
            "status": status_text
        }
        report["bullet_keywords"].append(status)
        
        report["summary"]["bullet_coverage"]["required"] += 1
        # V1.4更新：完整覆盖或部分覆盖都计入覆盖率
        if coverage["covered_in_any"]:
            report["summary"]["bullet_coverage"]["covered"] += 1
        else:
            report["missing_critical"].append({
                "keyword": kw,
                "level": "P1_BULLET",
                "suggestion": f"建议添加到五点或Search Terms: {kw}"
            })
    
    # 检查部分ST词（抽样）
    for kw_info in allocation.get("st_keywords", [])[:10]:
        kw = kw_info["keyword"]
        coverage = check_keyword_coverage(listing, kw)
        
        status = {
            "keyword": kw,
            "coverage": coverage,
            "status": "✓" if coverage["in_any"] else "○"
        }
        report["st_keywords_sample"].append(status)
    
    # 计算覆盖率
    title_req = report["summary"]["title_coverage"]["required"]
    title_cov = report["summary"]["title_coverage"]["covered"]
    bullet_req = report["summary"]["bullet_coverage"]["required"]
    bullet_cov = report["summary"]["bullet_coverage"]["covered"]
    
    report["summary"]["title_coverage"]["rate"] = round(title_cov / title_req * 100, 1) if title_req > 0 else 100
    report["summary"]["bullet_coverage"]["rate"] = round(bullet_cov / bullet_req * 100, 1) if bullet_req > 0 else 100
    
    total_req = title_req + bullet_req
    total_cov = title_cov + bullet_cov
    report["summary"]["overall_coverage"]["required"] = total_req
    report["summary"]["overall_coverage"]["covered"] = total_cov
    report["summary"]["overall_coverage"]["rate"] = round(total_cov / total_req * 100, 1) if total_req > 0 else 100
    
    # 生成建议
    if report["summary"]["title_coverage"]["rate"] < 100:
        report["recommendations"].append("⚠️ 标题配额词未完全覆盖，建议检查并补充缺失词")
    if report["summary"]["bullet_coverage"]["rate"] < 80:
        report["recommendations"].append("⚠️ 五点配额词覆盖率低于80%，建议优化五点内容")
    if report["summary"]["overall_coverage"]["rate"] >= 90:
        report["recommendations"].append("✅ 整体覆盖率良好")
    
    # 检查Search Terms长度
    st_length = len(listing["search_terms"].encode('utf-8'))
    if st_length < 230:
        report["recommendations"].append(f"⚠️ Search Terms仅{st_length} bytes，建议补充到230-250 bytes")
    elif st_length > 250:
        report["recommendations"].append(f"⚠️ Search Terms超过250 bytes（{st_length}），可能被截断")
    else:
        report["recommendations"].append(f"✅ Search Terms长度合适（{st_length} bytes）")
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Amazon Listing Writer - Listing质量检查脚本 V1.2"
    )
    
    parser.add_argument("--listing", "-l", required=True, help="Listing文本文件路径")
    parser.add_argument("--keywords", "-k", required=True, help="intent_extractor.py输出的JSON文件")
    parser.add_argument("--output", "-o", default="coverage_report.json", help="输出报告路径")
    
    args = parser.parse_args()
    
    print(f"正在加载Listing文件: {args.listing}")
    listing, listing_raw = load_listing(args.listing)
    
    print(f"正在加载关键词配置: {args.keywords}")
    with open(args.keywords, 'r', encoding='utf-8') as f:
        keywords_data = json.load(f)
    
    print("\n" + "=" * 60)
    print("【Listing质量检测报告 V1.6】")
    print("=" * 60)
    
    report = generate_coverage_report(listing, listing_raw, keywords_data, args.listing)
    
    # 1. 长度检测
    print("\n【一、长度检测】")
    ld = report["length_details"]
    print(f"  标题: {ld['title']['length']}字符 {ld['title']['status']} (≤190)")
    for b in ld["bullets"]:
        print(f"  Bullet{b['index']}: {b['length']}字符 {b['status']} (170-250)")
    print(f"  Search Terms: {ld['search_terms']['bytes']}bytes {ld['search_terms']['status']} (230-250)")
    print(f"  长描述: {ld['description']['length']}字符 {ld['description']['status']} (1200-1900)")
    
    if not ld["passed"]:
        print("\n  ⚠️ 长度问题:")
        for v in ld["violations"]:
            print(f"    ❌ {v}")
    
    # 2. 品牌词检测
    print("\n【二、品牌词检测】")
    if report["brand_violations"]:
        print("  " + "!" * 50)
        print("  🚨 检测到品牌词侵权风险！")
        for brand in report["brand_violations"]:
            print(f"    ❌ {brand}")
        print("  → 必须立即移除！")
        print("  " + "!" * 50)
    else:
        print("  ✅ 未发现已知品牌词（仍需Claude复核未知品牌）")
    
    # 3. 夸大词检测
    print("\n【三、夸大词检测】")
    if report["exaggeration_violations"]:
        print(f"  ⚠️ 发现夸大词: {', '.join(report['exaggeration_violations'])}")
    else:
        print("  ✅ 未发现夸大词")
    
    # 3.5 标题词根重复检测（V1.5新增）
    print("\n【三点五、标题词根重复检测】")
    tr = report["title_repetition_details"]
    if tr["passed"]:
        print("  ✅ 无词根重复超限")
        if tr["word_counts"]:
            print(f"    重复词统计: {tr['word_counts']}")
    else:
        print("  ❌ 标题词根重复超限:")
        for v in tr["violations"]:
            print(f"    ❌ {v}")
        print("  → 单数/复数视为独立词根，每个词根最多出现2次")
    
    # 4. 配额词覆盖
    print(f"\n【四、配额词覆盖】")
    print(f"  标题配额词: {report['summary']['title_coverage']['covered']}/{report['summary']['title_coverage']['required']} ({report['summary']['title_coverage']['rate']}%)")
    for kw in report["title_keywords"]:
        print(f"    {kw['status']} {kw['keyword']} (R:{kw['rank']})")
    
    print(f"  五点配额词: {report['summary']['bullet_coverage']['covered']}/{report['summary']['bullet_coverage']['required']} ({report['summary']['bullet_coverage']['rate']}%)")
    for kw in report["bullet_keywords"]:
        print(f"    {kw['status']} {kw['keyword']} (R:{kw['rank']})")
    
    print(f"\n  整体覆盖率: {report['summary']['overall_coverage']['rate']}%")
    
    # 5. 缺失关键词
    if report["missing_critical"]:
        print("\n【五、缺失的关键词】")
        for item in report["missing_critical"]:
            print(f"  ✗ [{item['level']}] {item['keyword']}")
            print(f"    → {item['suggestion']}")
    
    # 6. 总评
    print("\n" + "=" * 60)
    print("【总评】")
    
    all_passed = True
    exit_code = 0
    
    if not tr["passed"]:
        print("  ❌ 标题词根重复超限 - 必须修改")
        all_passed = False
        if exit_code == 0:
            exit_code = 5
    if report["brand_violations"]:
        print("  ❌ 品牌词侵权 - 必须修改")
        all_passed = False
        if exit_code == 0:
            exit_code = 2
    if not ld["passed"]:
        print("  ❌ 长度不符合规范 - 需要调整")
        all_passed = False
        if exit_code == 0:
            exit_code = 3
    if report["exaggeration_violations"]:
        print("  ⚠️ 存在夸大词 - 建议移除")
    if report["summary"]["overall_coverage"]["rate"] < 80:
        print("  ⚠️ 覆盖率不足80% - 建议优化")
        if exit_code == 0:
            exit_code = 1
    
    if all_passed and report["summary"]["overall_coverage"]["rate"] >= 80 and not report["exaggeration_violations"]:
        print("  ✅ 脚本检测全部通过！（仍需Claude复核）")
    
    print("=" * 60)
    
    # 保存报告
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存至: {output_path}")
    
    # 返回状态码
    # 5 = 标题词根重复
    # 3 = 长度不合规
    # 2 = 品牌词侵权
    # 1 = 覆盖率不足
    # 0 = 全部通过
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
