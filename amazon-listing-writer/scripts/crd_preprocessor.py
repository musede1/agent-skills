#!/usr/bin/env python3
"""
CRD Preprocessor V2.0
CRD（Competitor Review Dataset）数据预处理脚本

功能：
- 读取CRD文件（Excel/CSV）
- 自动识别列名（中英文映射）
- 数据清洗（空值/重复/超短/星级校验）
- 统计摘要（评论总数、星级分布、VP占比、变体分布）
- 5档置信度判定
- 输出统计摘要JSON + 清洗后数据

定位：amazon-review-analyzer处理流程的Step 1
后续Step 2-4由Claude大模型执行深度语义分析

用法：
    python3 crd_preprocessor.py <input_file> [--output <dir>] [--encoding <enc>]
"""

import sys
import os
import json
import re
from datetime import datetime
from collections import Counter

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas is required. Install with: pip install pandas openpyxl")
    sys.exit(1)


# ============================================================
# 列名映射（中文优先，兼容英文）
# ============================================================

COLUMN_MAPPING = {
    'content': {
        'standard': '内容',
        'aliases': [
            '内容', '评论内容', '评论正文',
            'review_text', 'text', 'comment', 'body', 'content', 'review'
        ]
    },
    'rating': {
        'standard': '星级',
        'aliases': [
            '星级', '评分',
            'rating', 'star', 'stars', 'score', 'rate'
        ]
    },
    'title': {
        'standard': '标题',
        'aliases': [
            '标题', '评论标题',
            'review_title', 'title', 'headline', 'subject'
        ]
    },
    'asin': {
        'standard': 'ASIN',
        'aliases': ['ASIN', 'asin', 'Asin']
    },
    'variant': {
        'standard': '型号',
        'aliases': [
            '型号', '变体', '款式', '子体',
            'variant', 'style', 'model', 'Style'
        ]
    },
    'vp': {
        'standard': 'VP评论',
        'aliases': [
            'VP评论', 'VP', '验证购买',
            'verified_purchase', 'verified', 'vp', 'is_verified'
        ]
    },
    'helpful': {
        'standard': '赞同数',
        'aliases': [
            '赞同数', '有用数', '有用票数',
            'helpful_votes', 'helpful', 'votes', 'upvotes'
        ]
    },
    'date': {
        'standard': '评论时间',
        'aliases': [
            '评论时间', '日期',
            'date', 'review_date', 'time', 'timestamp', 'created_at'
        ]
    }
}

# 必需列（standard名）
REQUIRED_COLUMNS = ['内容', '星级', '标题', 'ASIN', '型号']

# 可选列（standard名）
OPTIONAL_COLUMNS = ['VP评论', '赞同数', '评论时间']


def map_columns(df):
    """
    自动映射列名到标准列名
    
    Returns:
        df: 列名已映射的DataFrame
        mapped: dict，记录映射关系
        missing_required: list，缺失的必需列
    """
    mapped = {}
    original_cols = list(df.columns)
    rename_map = {}
    
    for field_key, field_info in COLUMN_MAPPING.items():
        standard_name = field_info['standard']
        found = False
        
        for alias in field_info['aliases']:
            # 精确匹配（不区分大小写，但保留原始case进行匹配）
            for orig_col in original_cols:
                if orig_col.strip().lower() == alias.strip().lower():
                    rename_map[orig_col] = standard_name
                    mapped[standard_name] = orig_col
                    found = True
                    break
            if found:
                break
        
        if not found:
            mapped[standard_name] = None
    
    df = df.rename(columns=rename_map)
    
    # 检查必需列
    missing_required = []
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            missing_required.append(col)
    
    return df, mapped, missing_required


def clean_data(df):
    """
    数据清洗
    
    Returns:
        df_clean: 清洗后的DataFrame
        filter_log: 过滤记录
    """
    filter_log = []
    original_count = len(df)
    
    # 1. 去除内容为空的评论
    mask_empty = df['内容'].isna() | (df['内容'].astype(str).str.strip() == '')
    empty_count = mask_empty.sum()
    if empty_count > 0:
        filter_log.append(f"空评论: {empty_count}条")
    df = df[~mask_empty].copy()
    
    # 2. 去除完全重复的评论
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['内容'], keep='first')
    dup_count = before_dedup - len(df)
    if dup_count > 0:
        filter_log.append(f"重复评论: {dup_count}条")
    
    # 3. 去除超短评论（<10字符）
    df['_content_len'] = df['内容'].astype(str).str.len()
    mask_short = df['_content_len'] < 10
    short_count = mask_short.sum()
    if short_count > 0:
        filter_log.append(f"超短评论(<10字符): {short_count}条")
    df = df[~mask_short].copy()
    
    # 4. 星级校验（必须是1-5的整数）
    df['星级'] = pd.to_numeric(df['星级'], errors='coerce')
    mask_invalid_rating = df['星级'].isna() | ~df['星级'].isin([1, 2, 3, 4, 5])
    invalid_count = mask_invalid_rating.sum()
    if invalid_count > 0:
        filter_log.append(f"无效星级: {invalid_count}条")
    df = df[~mask_invalid_rating].copy()
    df['星级'] = df['星级'].astype(int)
    
    # 5. 赞同数容错
    if '赞同数' in df.columns:
        df['赞同数'] = pd.to_numeric(df['赞同数'], errors='coerce').fillna(0).astype(int)
    else:
        df['赞同数'] = 0
    
    # 6. VP评论容错
    if 'VP评论' not in df.columns:
        df['VP评论'] = 'Y'  # 默认全部视为VP
    else:
        df['VP评论'] = df['VP评论'].fillna('Y')  # 空值默认为VP
    
    # 清理临时列
    df = df.drop(columns=['_content_len'], errors='ignore')
    
    filtered_count = original_count - len(df)
    
    return df, filter_log, filtered_count


def determine_confidence(total_reviews):
    """5档置信度判定"""
    if total_reviews >= 100:
        return "HIGH"
    elif total_reviews >= 50:
        return "MEDIUM"
    elif total_reviews >= 20:
        return "LOW"
    elif total_reviews >= 10:
        return "VERY_LOW"
    else:
        return "INSUFFICIENT"


def generate_summary(df, source_file, filter_log, filtered_count):
    """生成统计摘要JSON"""
    total = len(df)
    
    # 星级分布
    rating_dist = df['星级'].value_counts().sort_index()
    rating_distribution = {
        f"{i}_star": int(rating_dist.get(i, 0)) for i in range(1, 6)
    }
    
    # 变体分布
    variant_dist = df['型号'].value_counts()
    variant_distribution = {str(k): int(v) for k, v in variant_dist.items()}
    
    # 变体×星级交叉
    variant_rating = {}
    for variant in df['型号'].unique():
        subset = df[df['型号'] == variant]
        variant_rating[str(variant)] = {
            "count": int(len(subset)),
            "avg_rating": round(float(subset['星级'].mean()), 2),
            "rating_distribution": {
                f"{i}_star": int((subset['星级'] == i).sum()) for i in range(1, 6)
            }
        }
    
    # VP占比
    vp_count = (df['VP评论'].astype(str).str.upper() == 'Y').sum()
    vp_rate = round(vp_count / total, 3) if total > 0 else 0
    
    # 评论长度统计
    content_lengths = df['内容'].astype(str).str.len()
    
    # 日期范围
    date_range = {"earliest": "N/A", "latest": "N/A"}
    if '评论时间' in df.columns:
        try:
            dates = pd.to_datetime(df['评论时间'], errors='coerce').dropna()
            if len(dates) > 0:
                date_range = {
                    "earliest": str(dates.min().date()),
                    "latest": str(dates.max().date())
                }
        except Exception:
            pass
    
    # 置信度
    confidence = determine_confidence(total)
    
    # 动态阈值
    dynamic_thresholds = get_dynamic_thresholds(total, confidence)
    
    # 生成warnings
    warnings = []
    if total < 50:
        warnings.append(f"评论仅{total}条，分析结论可能存在偶然性")
    
    neg_count = rating_distribution.get('1_star', 0) + rating_distribution.get('2_star', 0)
    if neg_count < 5:
        warnings.append(f"负面评论仅{neg_count}条，痛点分析可信度低")
    
    pos_count = rating_distribution.get('4_star', 0) + rating_distribution.get('5_star', 0)
    if pos_count < 10:
        warnings.append(f"正面评论仅{pos_count}条，卖点分析可信度低")
    
    summary = {
        "meta": {
            "version": "2.0",
            "generated_at": datetime.now().isoformat(),
            "source_file": os.path.basename(source_file),
            "total_reviews": total,
            "valid_reviews": total,
            "filtered_reviews": filtered_count,
            "filter_reasons": filter_log,
            "rating_distribution": rating_distribution,
            "avg_rating": round(float(df['星级'].mean()), 2) if total > 0 else 0,
            "variant_count": int(df['型号'].nunique()),
            "variant_distribution": variant_distribution,
            "variant_rating_detail": variant_rating,
            "vp_rate": vp_rate,
            "avg_review_length": int(content_lengths.mean()) if total > 0 else 0,
            "date_range": date_range,
            "confidence_level": confidence,
            "dynamic_thresholds": dynamic_thresholds,
            "universality_filter": {
                "rule": "cross_variant_count>=2 OR evidence_count>=3",
                "description": "所有洞察必须通过通用性过滤才能纳入输出"
            },
            "warnings": warnings,
            "crd_positioning": "P2辅助验证层（Auxiliary Validation Layer）"
        }
    }
    
    return summary


def get_dynamic_thresholds(total_reviews, confidence):
    """根据评论总数返回动态阈值"""
    thresholds = {
        "HIGH": {
            "min_frequency": 3,
            "pain_severity_rule": "百分比驱动: evidence_rate>=5%=HIGH, 2-5%=MEDIUM, <2%=LOW",
            "gift_high_trigger": "gift_mention_rate >= 20%"
        },
        "MEDIUM": {
            "min_frequency": 2,
            "pain_severity_rule": "双重验证: evidence_rate>=3%且count>=5=HIGH",
            "gift_high_trigger": "gift_mention_rate>=15% 或 绝对数>=10条"
        },
        "LOW": {
            "min_frequency": 2,
            "pain_severity_rule": "绝对数驱动: count>=5=较强信号, count>=3=信号",
            "gift_high_trigger": "绝对数>=5条"
        },
        "VERY_LOW": {
            "min_frequency": 1,
            "pain_severity_rule": "仅定性描述，不做定量结论",
            "gift_high_trigger": "绝对数>=2条，标LOW_CONFIDENCE"
        },
        "INSUFFICIENT": {
            "min_frequency": 1,
            "pain_severity_rule": "仅列原文摘要，不做分析结论",
            "gift_high_trigger": "不判定"
        }
    }
    
    return thresholds.get(confidence, thresholds["INSUFFICIENT"])


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CRD Preprocessor V2.0')
    parser.add_argument('input_file', help='CRD文件路径（Excel/CSV）')
    parser.add_argument('--output', '-o', default='./output', help='输出目录')
    parser.add_argument('--encoding', default=None, help='CSV文件编码（默认自动检测）')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    # 读取文件
    input_file = args.input_file
    ext = os.path.splitext(input_file)[1].lower()
    
    print(f"[Step 1.1] 读取CRD文件: {input_file}")
    
    try:
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        elif ext == '.csv':
            encoding = args.encoding or 'utf-8'
            try:
                df = pd.read_csv(input_file, encoding=encoding)
            except UnicodeDecodeError:
                for enc in ['gbk', 'gb2312', 'latin-1']:
                    try:
                        df = pd.read_csv(input_file, encoding=enc)
                        print(f"  使用编码: {enc}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    print("ERROR: 无法识别文件编码")
                    sys.exit(1)
        elif ext == '.tsv':
            df = pd.read_csv(input_file, sep='\t', encoding=args.encoding or 'utf-8')
        else:
            print(f"ERROR: 不支持的文件格式: {ext}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: 读取文件失败: {e}")
        sys.exit(1)
    
    print(f"  原始数据: {len(df)}行 × {len(df.columns)}列")
    print(f"  原始列名: {list(df.columns)}")
    
    # 列名映射
    print(f"\n[Step 1.2] 列名映射")
    df, mapped, missing_required = map_columns(df)
    
    for std_name, orig_name in mapped.items():
        if orig_name:
            status = "✅" if std_name in REQUIRED_COLUMNS else "⚪"
            print(f"  {status} {orig_name} → {std_name}")
        elif std_name in REQUIRED_COLUMNS:
            print(f"  ❌ {std_name} — 未找到匹配列")
        else:
            print(f"  ⚪ {std_name} — 未找到（可选，使用默认值）")
    
    if missing_required:
        print(f"\n❌ ERROR: 缺少必需列: {missing_required}")
        print("请确保CRD文件包含以下列（或其兼容别名）：")
        for col in missing_required:
            aliases = COLUMN_MAPPING[[k for k, v in COLUMN_MAPPING.items() if v['standard'] == col][0]]['aliases']
            print(f"  {col}: {aliases}")
        sys.exit(1)
    
    # 数据清洗
    print(f"\n[Step 1.3] 数据清洗")
    df_clean, filter_log, filtered_count = clean_data(df)
    
    if filter_log:
        for log in filter_log:
            print(f"  过滤: {log}")
    print(f"  清洗后: {len(df_clean)}条有效评论（过滤{filtered_count}条）")
    
    # 生成统计摘要
    print(f"\n[Step 1.4] 生成统计摘要")
    summary = generate_summary(df_clean, input_file, filter_log, filtered_count)
    
    meta = summary['meta']
    print(f"  评论总数: {meta['total_reviews']}")
    print(f"  平均评分: {meta['avg_rating']}⭐")
    print(f"  星级分布: {meta['rating_distribution']}")
    print(f"  变体数量: {meta['variant_count']}")
    print(f"  VP占比: {meta['vp_rate']*100:.1f}%")
    print(f"  置信度: {meta['confidence_level']}")
    
    if meta['warnings']:
        print(f"\n  ⚠️ 警告:")
        for w in meta['warnings']:
            print(f"    - {w}")
    
    # 保存输出
    summary_path = os.path.join(args.output, 'crd_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n[输出] 统计摘要: {summary_path}")
    
    clean_path = os.path.join(args.output, 'crd_clean.xlsx')
    df_clean.to_excel(clean_path, index=False)
    print(f"[输出] 清洗后数据: {clean_path}")
    
    print(f"\n✅ CRD预处理完成。置信度: {meta['confidence_level']}")
    print(f"   后续由Claude大模型执行Step 2-4深度分析。")


if __name__ == '__main__':
    main()
