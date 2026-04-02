#!/usr/bin/env python3
"""
Amazon Listing Writer - 关键词分析与配额分配脚本
版本: V3.0

功能: 
1. 基于4层锚点词的语义评分系统（自动过滤不相关词，无需手动黑名单）
2. 自动计算关键词优先级并按配额分配到标题/五点/Search Terms
3. 提炼意图词（风格词/礼品场景词/节日场合词/受众词）

输出: JSON格式的配额分配方案

使用方法:
    python3 intent_extractor.py <关键词文件.xlsx或.csv> \\
        --L1-subject "conch,shell,seashell" \\
        --L2-category "sculpture,figurine,decor" \\
        --L3-attribute "glass,blown,aqua" \\
        --L4-scene "coastal,nautical,beach" \\
        [--output result.json]

参数说明:
    --L1-subject: 题材形状锚点词（核心层，+30-40分）
    --L2-category: 品类功能锚点词（品类层，+25分）
    --L3-attribute: 材质工艺颜色锚点词（属性层，+10-15分）
    --L4-scene: 风格场景锚点词（场景层，+5分）
    --title-quota: 标题配额（默认3）
    --bullet-quota: 五点配额（默认5）
    --output: 输出JSON文件路径，默认为 intent_result.json

评分规则:
    语义评分 = 基础分 + L1分 + L2分 + L3分 + L4分
    - 基础分: 关键词2-4词=20分，其他=10分
    - L1分: 命中≥2个=40分，命中1个=30分，未命中=0分
    - L2分: 命中≥1个=25分，未命中=0分
    - L3分: 命中≥2个=15分，命中1个=10分，未命中=0分
    - L4分: 命中≥1个=5分，未命中=0分
    - EXCLUDE判定: L1、L2、L3均未命中 → 直接剔除

等级划分:
    ≥60分: P0_P1_HIGH（标题或五点）
    45-59分: P2_NORMAL（五点或ST）
    30-44分: ST_ONLY（仅ST）
    <30分: EXCLUDE（剔除）
"""

import argparse
import json
import re
import sys
import math
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import warnings

try:
    import pandas as pd
except ImportError:
    print("错误: 请先安装pandas库: pip install pandas openpyxl")
    sys.exit(1)


# ============================================================
# 意图词候选词库（用于意图词提炼）
# ============================================================

STYLE_WORDS = {
    "modern", "minimalist", "farmhouse", "boho", "bohemian", "rustic",
    "contemporary", "vintage", "industrial", "scandinavian", "mid-century",
    "traditional", "coastal", "nautical", "tropical", "zen", "japanese",
    "abstract", "geometric", "art deco", "shabby chic", "cottage",
    "mediterranean", "french country", "transitional", "eclectic"
}

GIFT_SCENE_WORDS = {
    "wedding gift", "anniversary gift", "birthday gift", "christmas gift",
    "valentine gift", "valentines gift", "mothers day gift", "fathers day gift",
    "housewarming gift", "engagement gift", "bridal shower gift",
    "graduation gift", "retirement gift", "thank you gift", "sympathy gift",
    "get well gift", "hostess gift", "teacher gift", "boss gift",
    "gift for couple", "gift for her", "gift for him", "gift for wife",
    "gift for husband", "gift for mom", "gift for dad", "gift for friend"
}

OCCASION_WORDS = {
    "valentine", "valentines", "valentine's day", "anniversary", "wedding",
    "christmas", "mothers day", "mother's day", "fathers day", "father's day",
    "birthday", "housewarming", "engagement", "bridal shower", "baby shower",
    "graduation", "retirement", "thanksgiving", "easter", "new year"
}

AUDIENCE_WORDS = {
    "couple", "couples", "newlywed", "newlyweds", "husband", "wife",
    "boyfriend", "girlfriend", "lover", "lovers", "partner", "spouse",
    "mom", "dad", "mother", "father", "parents", "grandma", "grandpa",
    "family", "friend", "friends"
}

ALL_INTENT_WORDS = {
    "style": STYLE_WORDS,
    "gift_scene": GIFT_SCENE_WORDS,
    "occasion": OCCASION_WORDS,
    "audience": AUDIENCE_WORDS
}


def normalize_keyword(kw: str) -> str:
    """标准化关键词：小写、去除多余空格"""
    return re.sub(r'\s+', ' ', kw.lower().strip())


def load_keyword_file(filepath: str) -> pd.DataFrame:
    """加载关键词文件（支持xlsx和csv）"""
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    if path.suffix.lower() == '.xlsx':
        df = pd.read_excel(filepath, engine='openpyxl')
    elif path.suffix.lower() == '.csv':
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"无法解析CSV文件编码: {filepath}")
    else:
        raise ValueError(f"不支持的文件格式: {path.suffix}")
    
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    # 查找关键词列
    keyword_col = None
    for col in df.columns:
        if '关键词' in col or 'keyword' in col or 'kw' in col:
            keyword_col = col
            break
    if keyword_col is None:
        keyword_col = df.columns[0]
        warnings.warn(f"未找到关键词列，使用第一列: {keyword_col}")
    
    # 查找搜索量列
    sv_col = None
    for col in df.columns:
        if '搜索量' in col or 'search volume' in col or 'sv' in col or 'volume' in col:
            sv_col = col
            break
    
    # 查找自然排名列
    rank_col = None
    for col in df.columns:
        if '自然排名' in col or 'rank' in col or '排名' in col:
            rank_col = col
            break
    
    result = pd.DataFrame()
    result['keyword'] = df[keyword_col].astype(str).apply(normalize_keyword)
    result['search_volume'] = pd.to_numeric(df[sv_col], errors='coerce').fillna(0).astype(int) if sv_col else 0
    result['rank'] = pd.to_numeric(df[rank_col], errors='coerce').fillna(999).astype(int) if rank_col else 999
    
    result = result.drop_duplicates(subset=['keyword'])
    result = result[result['keyword'].str.len() > 0]
    
    return result


def count_anchor_hits(keyword: str, anchor_set: Set[str]) -> int:
    """计算关键词命中锚点词的数量"""
    keyword_lower = keyword.lower()
    hits = 0
    for anchor in anchor_set:
        if anchor in keyword_lower:
            hits += 1
    return hits


def calculate_semantic_score_v3(
    keyword: str,
    L1_subject: Set[str],
    L2_category: Set[str],
    L3_attribute: Set[str],
    L4_scene: Set[str]
) -> Tuple[int, Dict]:
    """
    基于4层锚点的语义评分系统 V3.0
    
    返回: (总分, 详细得分字典)
    """
    keyword_lower = keyword.lower()
    word_count = len(keyword.split())
    
    # 基础分（根据关键词长度）
    if 2 <= word_count <= 4:
        base_score = 20
    else:
        base_score = 10
    
    # L1 题材层得分（核心层）
    L1_hits = count_anchor_hits(keyword_lower, L1_subject)
    if L1_hits >= 2:
        L1_score = 40
    elif L1_hits == 1:
        L1_score = 30
    else:
        L1_score = 0
    
    # L2 品类层得分
    L2_hits = count_anchor_hits(keyword_lower, L2_category)
    L2_score = 25 if L2_hits >= 1 else 0
    
    # L3 属性层得分
    L3_hits = count_anchor_hits(keyword_lower, L3_attribute)
    if L3_hits >= 2:
        L3_score = 15
    elif L3_hits == 1:
        L3_score = 10
    else:
        L3_score = 0
    
    # L4 场景层得分
    L4_hits = count_anchor_hits(keyword_lower, L4_scene)
    L4_score = 5 if L4_hits >= 1 else 0
    
    total_score = base_score + L1_score + L2_score + L3_score + L4_score
    
    # EXCLUDE判定：L1、L2、L3都未命中 → 与产品完全无关
    is_excluded = (L1_hits == 0 and L2_hits == 0 and L3_hits == 0)
    if is_excluded:
        total_score = 0  # 强制归零
    
    detail = {
        "base": base_score,
        "L1_subject": {"hits": L1_hits, "score": L1_score},
        "L2_category": {"hits": L2_hits, "score": L2_score},
        "L3_attribute": {"hits": L3_hits, "score": L3_score},
        "L4_scene": {"hits": L4_hits, "score": L4_score},
        "is_excluded": is_excluded
    }
    
    return total_score, detail


def calculate_priority_score(rank: int, sv: int, semantic_score: int) -> float:
    """
    计算综合优先级分数
    
    Priority = R_score × 0.4 + SV_score × 0.3 + Semantic_score × 0.3
    """
    r_score = 100 - min(rank, 100)
    sv_score = min(math.log10(sv + 1) * 25, 100) if sv > 0 else 0
    priority = r_score * 0.4 + sv_score * 0.3 + semantic_score * 0.3
    return round(priority, 2)


def classify_keyword_level(semantic_score: int) -> str:
    """
    根据语义评分判定关键词等级
    """
    if semantic_score >= 60:
        return "P0_P1_HIGH"
    elif semantic_score >= 45:
        return "P2_NORMAL"
    elif semantic_score >= 30:
        return "ST_ONLY"
    else:
        return "EXCLUDE"


def allocate_keywords(
    keywords_df: pd.DataFrame,
    L1_subject: Set[str],
    L2_category: Set[str],
    L3_attribute: Set[str],
    L4_scene: Set[str],
    title_quota: int = 3,
    bullet_quota: int = 5
) -> Dict:
    """核心功能：关键词配额分配"""
    keyword_analysis = []
    
    for _, row in keywords_df.iterrows():
        kw = row['keyword']
        rank = row['rank']
        sv = row['search_volume']
        
        semantic_score, score_detail = calculate_semantic_score_v3(
            kw, L1_subject, L2_category, L3_attribute, L4_scene
        )
        priority_score = calculate_priority_score(rank, sv, semantic_score)
        level = classify_keyword_level(semantic_score)
        
        keyword_analysis.append({
            "keyword": kw,
            "rank": int(rank),
            "search_volume": int(sv),
            "semantic_score": semantic_score,
            "score_detail": score_detail,
            "priority_score": priority_score,
            "level": level
        })
    
    # 分离不同等级的词
    p0_p1 = [kw for kw in keyword_analysis if kw['level'] == "P0_P1_HIGH"]
    p2 = [kw for kw in keyword_analysis if kw['level'] == "P2_NORMAL"]
    st_only = [kw for kw in keyword_analysis if kw['level'] == "ST_ONLY"]
    excluded = [kw for kw in keyword_analysis if kw['level'] == "EXCLUDE"]
    
    # 各等级内部按优先级排序
    p0_p1.sort(key=lambda x: x['priority_score'], reverse=True)
    p2.sort(key=lambda x: x['priority_score'], reverse=True)
    st_only.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # 分配到各位置
    title_keywords = []
    bullet_keywords = []
    st_keywords = []
    
    # Step 1: P0_P1优先进入标题，溢出进入五点
    for kw_info in p0_p1:
        if len(title_keywords) < title_quota:
            title_keywords.append(kw_info)
        elif len(bullet_keywords) < bullet_quota:
            bullet_keywords.append(kw_info)
        else:
            st_keywords.append(kw_info)
    
    # Step 2: P2填充五点剩余配额
    for kw_info in p2:
        if len(bullet_keywords) < bullet_quota:
            bullet_keywords.append(kw_info)
        else:
            st_keywords.append(kw_info)
    
    # Step 3: ST_ONLY直接进入ST
    st_keywords.extend(st_only)
    
    # 重新按优先级排序
    title_keywords.sort(key=lambda x: x['priority_score'], reverse=True)
    bullet_keywords.sort(key=lambda x: x['priority_score'], reverse=True)
    st_keywords.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return {
        "title_keywords": title_keywords,
        "bullet_keywords": bullet_keywords,
        "st_keywords": st_keywords,
        "excluded_keywords": excluded,
        "all_analyzed": keyword_analysis
    }


def extract_intent_words(keywords_df: pd.DataFrame, L1_subject: Set[str]) -> Dict:
    """提取意图词（风格词/礼品词等）"""
    results = {
        "strong_evidence": [],
        "usable_evidence": [],
        "filtered_out": []
    }
    
    for word_type, word_set in ALL_INTENT_WORDS.items():
        for candidate in word_set:
            mask = keywords_df['keyword'].apply(lambda kw: bool(re.search(r'\b' + re.escape(candidate) + r'\b', kw)))
            matched_df = keywords_df[mask]
            
            if len(matched_df) < 3:
                continue
            
            F = len(matched_df)
            U = matched_df['keyword'].nunique()
            SVsum = int(matched_df['search_volume'].sum())
            valid_ranks = matched_df[matched_df['rank'] < 999]['rank']
            Rbest = int(valid_ranks.min()) if len(valid_ranks) > 0 else 999
            
            # 同框过滤
            U_core = 0
            for _, row in matched_df.iterrows():
                kw = row['keyword']
                for anchor in L1_subject:
                    if anchor in kw:
                        U_core += 1
                        break
            
            is_strong = (Rbest <= 12) or (Rbest <= 18 and U >= 4) or (SVsum >= 8000 and U >= 5)
            is_usable = (Rbest <= 25 and U >= 3) or (SVsum >= 4000 and U >= 4)
            
            entry = {
                "word": candidate,
                "type": word_type,
                "F": F, "U": U, "SVsum": SVsum, "Rbest": Rbest,
                "U_core": U_core,
                "coframe_pass": U_core >= 2
            }
            
            if is_strong:
                entry["level"] = "strong"
                entry["usage"] = "标题+五点+ST" if U_core >= 2 else "仅ST"
                results["strong_evidence"].append(entry)
            elif is_usable:
                entry["level"] = "usable"
                entry["usage"] = "五点+ST" if U_core >= 2 else "仅ST"
                results["usable_evidence"].append(entry)
    
    return results


def generate_search_terms(st_keywords: List[Dict], existing_words: Set[str], target_bytes: int = 245) -> str:
    """生成Search Terms字符串"""
    used_words = set(w.lower() for w in existing_words)
    st_parts = []
    current_bytes = 0
    
    for kw_info in st_keywords:
        kw = kw_info['keyword'].lower()
        words = kw.split()
        new_words = [w for w in words if w not in used_words]
        if not new_words:
            continue
        
        new_phrase = ' '.join(new_words)
        phrase_bytes = len(new_phrase.encode('utf-8')) + (1 if st_parts else 0)
        
        if current_bytes + phrase_bytes <= target_bytes:
            st_parts.extend(new_words)
            used_words.update(new_words)
            current_bytes += phrase_bytes
    
    # 填充通用词
    remaining_space = target_bytes - current_bytes
    if remaining_space > 10:
        filler_words = [
            "accent", "piece", "ornament", "collectible", "display",
            "tabletop", "shelf", "mantel", "centerpiece",
            "artistic", "unique", "handmade", "artisan", "crafted"
        ]
        for word in filler_words:
            if word not in used_words:
                word_bytes = len(word.encode('utf-8')) + 1
                if current_bytes + word_bytes <= target_bytes:
                    st_parts.append(word)
                    used_words.add(word)
                    current_bytes += word_bytes
    
    return ' '.join(st_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Amazon Listing Writer - 关键词分析与配额分配脚本 V3.0（4层锚点评分系统）",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("keyword_file", help="关键词文件路径（.xlsx或.csv）")
    parser.add_argument("--L1-subject", required=True, help="L1题材形状锚点词（核心层），逗号分隔")
    parser.add_argument("--L2-category", required=True, help="L2品类功能锚点词（品类层），逗号分隔")
    parser.add_argument("--L3-attribute", default="", help="L3材质工艺颜色锚点词（属性层），逗号分隔")
    parser.add_argument("--L4-scene", default="", help="L4风格场景锚点词（场景层），逗号分隔")
    parser.add_argument("--title-quota", type=int, default=3, help="标题配额（默认3）")
    parser.add_argument("--bullet-quota", type=int, default=5, help="五点配额（默认5）")
    parser.add_argument("--output", "-o", default="intent_result.json", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    # 解析4层锚点词
    L1_subject = {normalize_keyword(w) for w in args.L1_subject.split(",") if w.strip()}
    L2_category = {normalize_keyword(w) for w in args.L2_category.split(",") if w.strip()}
    L3_attribute = {normalize_keyword(w) for w in args.L3_attribute.split(",") if w.strip()} if args.L3_attribute else set()
    L4_scene = {normalize_keyword(w) for w in args.L4_scene.split(",") if w.strip()} if args.L4_scene else set()
    
    print(f"正在加载关键词文件: {args.keyword_file}")
    keywords_df = load_keyword_file(args.keyword_file)
    print(f"成功加载 {len(keywords_df)} 条关键词")
    print(f"\n锚点词配置:")
    print(f"  L1 题材层: {L1_subject}")
    print(f"  L2 品类层: {L2_category}")
    print(f"  L3 属性层: {L3_attribute if L3_attribute else '(未设置)'}")
    print(f"  L4 场景层: {L4_scene if L4_scene else '(未设置)'}")
    
    print("\n===== Step 1: 关键词配额分配 =====")
    allocation = allocate_keywords(
        keywords_df, L1_subject, L2_category, L3_attribute, L4_scene,
        title_quota=args.title_quota,
        bullet_quota=args.bullet_quota
    )
    
    print(f"\n标题配额 ({len(allocation['title_keywords'])}/{args.title_quota}):")
    for kw in allocation['title_keywords']:
        detail = kw['score_detail']
        print(f"  ✓ {kw['keyword']}")
        print(f"    R:{kw['rank']} | SV:{kw['search_volume']} | 语义:{kw['semantic_score']} | 优先级:{kw['priority_score']}")
        print(f"    得分: 基础{detail['base']} + L1({detail['L1_subject']['hits']}命中)+{detail['L1_subject']['score']} + L2+{detail['L2_category']['score']} + L3+{detail['L3_attribute']['score']} + L4+{detail['L4_scene']['score']}")
    
    print(f"\n五点配额 ({len(allocation['bullet_keywords'])}/{args.bullet_quota}):")
    for kw in allocation['bullet_keywords']:
        print(f"  ✓ {kw['keyword']} (R:{kw['rank']}, 语义:{kw['semantic_score']}, 等级:{kw['level']})")
    
    print(f"\nSearch Terms候选 ({len(allocation['st_keywords'])} 个):")
    for kw in allocation['st_keywords'][:10]:
        print(f"  · {kw['keyword']} (R:{kw['rank']}, 语义:{kw['semantic_score']}, 等级:{kw['level']})")
    if len(allocation['st_keywords']) > 10:
        print(f"  ... 还有 {len(allocation['st_keywords']) - 10} 个")
    
    if allocation['excluded_keywords']:
        print(f"\n已剔除 ({len(allocation['excluded_keywords'])} 个):")
        for kw in allocation['excluded_keywords'][:5]:
            print(f"  ✗ {kw['keyword']} (语义:{kw['semantic_score']}, 原因: L1/L2/L3均未命中)")
        if len(allocation['excluded_keywords']) > 5:
            print(f"  ... 还有 {len(allocation['excluded_keywords']) - 5} 个")
    
    print("\n===== Step 2: 意图词提炼 =====")
    intent_words = extract_intent_words(keywords_df, L1_subject)
    print(f"强证据意图词: {len(intent_words['strong_evidence'])} 个")
    print(f"可用证据意图词: {len(intent_words['usable_evidence'])} 个")
    
    # 生成Search Terms建议
    existing_words = set()
    for kw in allocation['title_keywords'] + allocation['bullet_keywords']:
        existing_words.update(kw['keyword'].split())
    suggested_st = generate_search_terms(allocation['st_keywords'], existing_words, target_bytes=245)
    
    print(f"\n===== Step 3: Search Terms建议 =====")
    print(f"长度: {len(suggested_st.encode('utf-8'))} bytes")
    print(f"内容: {suggested_st[:100]}..." if len(suggested_st) > 100 else f"内容: {suggested_st}")
    
    # 转换numpy类型
    def convert_to_native(obj):
        if isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(i) for i in obj]
        elif hasattr(obj, 'item'):
            return obj.item()
        else:
            return obj
    
    output = {
        "summary": {
            "total_keywords": len(keywords_df),
            "anchors": {
                "L1_subject": list(L1_subject),
                "L2_category": list(L2_category),
                "L3_attribute": list(L3_attribute),
                "L4_scene": list(L4_scene)
            },
            "title_quota": args.title_quota,
            "bullet_quota": args.bullet_quota,
            "title_allocated": len(allocation['title_keywords']),
            "bullet_allocated": len(allocation['bullet_keywords']),
            "st_candidates": len(allocation['st_keywords']),
            "excluded": len(allocation['excluded_keywords'])
        },
        "allocation": {
            "title_keywords": allocation['title_keywords'],
            "bullet_keywords": allocation['bullet_keywords'],
            "st_keywords": allocation['st_keywords'][:30],
            "excluded_keywords": allocation['excluded_keywords'][:10]
        },
        "suggested_search_terms": suggested_st,
        "intent_words": intent_words
    }
    
    output = convert_to_native(output)
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析完成！结果已保存至: {output_path}")


if __name__ == "__main__":
    main()
