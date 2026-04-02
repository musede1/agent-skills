#!/usr/bin/env python3
"""
Amazon Keyword Analyzer V2 - 亚马逊广告关键词量化分析脚本
版本: V9.5.2

修复内容（相比V1）：
1. 增加完整的"风格/场景词"排除列表，防止风格词被误判为L1
2. 新增"词性分类"功能，区分题材词vs风格词vs场景词
3. L1选取逻辑优化：题材词优先，风格词仅作为备选并标记警告
4. 输出增加词性标签，便于模型二次判断
"""

import pandas as pd
import re
import json
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any


class KeywordAnalyzerV2:
    """关键词量化分析器V2"""
    
    # ==================== 词库定义 ====================
    
    # CT词列表（类目词）
    CT_WORDS = [
        'statue', 'sculpture', 'figurine', 'decor', 'decoration', 
        'ornament', 'art', 'centerpiece', 'figure', 'accent', 'accents'
    ]
    
    # CT2泛类目词
    CT2_WORDS = ['decor', 'decoration', 'home decor', 'centerpiece', 'decorations']
    
    # 功能词候选
    FUNCTION_WORDS = [
        'candy', 'dish', 'bowl', 'key', 'holder', 'tray', 'trinket',
        'storage', 'organizer', 'container', 'box', 'jar', 'planter', 
        'vase', 'pot', 'basket', 'rack', 'stand', 'hook', 'hanger'
    ]
    
    # 材质词候选
    MATERIAL_WORDS = [
        'resin', 'ceramic', 'glass', 'metal', 'wood', 'plastic',
        'polyresin', 'stone', 'concrete', 'bronze', 'copper', 'iron',
        'brass', 'aluminum', 'steel', 'porcelain', 'crystal', 'acrylic',
        'blown', 'handblown', 'hand-blown'  # 工艺相关但常与材质连用
    ]
    
    # 摆放位置词候选
    LOCATION_WORDS = [
        'desk', 'table', 'office', 'entryway', 'entry', 'shelf', 
        'counter', 'tabletop', 'nightstand', 'bedside', 'bathroom',
        'kitchen', 'living', 'room', 'bedroom', 'garden', 'outdoor', 
        'indoor', 'patio', 'porch', 'mantel', 'fireplace', 'window',
        'wall', 'floor', 'ceiling', 'bookshelf', 'cabinet'
    ]
    
    # ==================== 风格/场景词（关键修复）====================
    # 这些词不应该成为L1题材词，应该进入LayerC-风格或LayerC-空间场景
    
    STYLE_SCENE_WORDS = [
        # 海洋/海岸风格（本次问题的根源）
        'coastal', 'beach', 'nautical', 'ocean', 'oceanic', 'marine',
        'seaside', 'maritime', 'tropical', 'island', 'mediterranean',
        'lakehouse', 'lake', 'river', 'seashore',
        
        # 乡村/田园风格
        'farmhouse', 'rustic', 'country', 'cottage', 'provincial',
        'pastoral', 'rural', 'barn', 'ranch',
        
        # 现代/简约风格
        'modern', 'contemporary', 'minimalist', 'minimal', 'sleek',
        'streamlined', 'futuristic', 'industrial', 'urban', 'loft',
        
        # 古典/复古风格
        'vintage', 'retro', 'antique', 'classic', 'classical',
        'traditional', 'victorian', 'baroque', 'rococo', 'gothic',
        'medieval', 'renaissance', 'colonial', 'heritage',
        
        # 异域风格
        'bohemian', 'boho', 'moroccan', 'asian', 'oriental', 'zen',
        'japanese', 'chinese', 'indian', 'african', 'tribal',
        'scandinavian', 'nordic', 'french', 'italian', 'spanish',
        'european', 'british', 'american',
        
        # 奢华/高端风格
        'luxury', 'luxurious', 'elegant', 'glamorous', 'glam',
        'sophisticated', 'upscale', 'premium', 'designer', 'boutique',
        'high end', 'exclusive', 'chic', 'posh',
        
        # 自然/有机风格
        'natural', 'organic', 'earthy', 'botanical', 'floral',
        'nature', 'eco', 'green', 'sustainable', 'woodland', 'forest',
        
        # 季节性/节日
        'christmas', 'holiday', 'easter', 'halloween', 'thanksgiving',
        'spring', 'summer', 'fall', 'autumn', 'winter', 'seasonal',
        'festive', 'valentines', 'patriotic',
        
        # 场景/用途描述词
        'decorative', 'ornamental', 'accent', 'statement', 'focal',
        'artistic', 'creative', 'handmade', 'handcrafted', 'artisan',
        'unique', 'quirky', 'whimsical', 'fun', 'funny', 'cute', 'cool',
        
        # 尺寸/程度描述词
        'large', 'small', 'mini', 'big', 'tall', 'short', 'tiny',
        'oversized', 'giant', 'huge', 'medium', 'little',
        
        # 其他修饰词
        'home', 'house', 'living', 'beautiful', 'pretty', 'gorgeous',
        'stunning', 'lovely', 'nice', 'best', 'perfect', 'ideal',
        'great', 'good', 'new', 'popular', 'trending', 'hot',
        'gifts', 'gift', 'present', 'presents', 'women', 'men', 'kids'
    ]
    
    # 工艺词候选
    CRAFT_WORDS = [
        'hand painted', 'handpainted', 'hand-painted', 'handmade', 
        'hand made', 'hand-made', 'handcrafted', 'hand crafted',
        'carved', 'molded', 'cast', 'blown', 'woven', 'stitched'
    ]
    
    # 表面工艺/光感词候选
    FINISH_WORDS = [
        'glossy', 'matte', 'metallic', 'gold', 'golden', 'silver',
        'bronze', 'copper', 'patina', 'antique', 'distressed', 'polished',
        'brushed', 'hammered', 'textured', 'smooth', 'shiny', 'sparkle'
    ]
    
    # 颜色词候选
    COLOR_WORDS = [
        'blue', 'gold', 'golden', 'black', 'white', 'red', 'green', 
        'pink', 'purple', 'orange', 'yellow', 'brown', 'grey', 'gray',
        'silver', 'bronze', 'copper', 'teal', 'turquoise', 'navy',
        'beige', 'cream', 'ivory', 'tan', 'coral', 'aqua', 'mint'
    ]
    
    # 常见品牌词模式
    KNOWN_BRANDS = [
        'aboxoo', 'nora fleming', 'mibung', 'katlot', 'leekung',
        'hodao', 'joyvano', 'fantask', 'dovdov', 'bella', 'kasa'
    ]
    
    def __init__(self, df: pd.DataFrame, l1_user: Optional[str] = None):
        """
        初始化分析器
        """
        self.df = df.copy()
        self.df['keyword'] = self.df['keyword'].str.lower().str.strip()
        self.l1_user = l1_user.lower().strip() if l1_user else None
        
        # 构建完整的排除词集合（用于L1候选筛选）
        self.l1_exclude_words = set(
            self.CT_WORDS + self.CT2_WORDS + self.FUNCTION_WORDS + 
            self.MATERIAL_WORDS + self.LOCATION_WORDS + self.STYLE_SCENE_WORDS +
            self.COLOR_WORDS + self.FINISH_WORDS + self.CRAFT_WORDS +
            ['for', 'and', 'the', 'with', 'of', 'to', 'in', 'on', 'a', 'an',
             'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
             'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
             'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought',
             'used', 'set', 'sets', 'piece', 'pieces', 'pack', 'pcs', 'lot']
        )
        
        # 分析结果存储
        self.results = {
            'meta': {
                'total_keywords': len(df),
                'l1_user_provided': l1_user,
                'script_version': 'V9.5.2'
            },
            'l1_analysis': {},
            'l2_analysis': {},
            'layerc_analysis': {},
            'color_analysis': {},
            'brand_analysis': {},
            'ct_analysis': {}
        }
    
    def _word_pattern(self, word: str, include_plural: bool = True) -> str:
        """生成词的正则匹配模式"""
        if include_plural:
            return rf'\b{re.escape(word)}s?\b'
        return rf'\b{re.escape(word)}\b'
    
    def _classify_word(self, word: str) -> str:
        """
        对词进行分类（关键新增功能）
        
        Returns:
            'theme': 题材词（如dog, cat, shell, angel）- 具体对象/生物
            'style': 风格词（如coastal, modern, vintage）
            'scene': 场景词（如beach, garden, sea, ocean）
            'material': 材质词
            'color': 颜色词
            'function': 功能词
            'ct': 类目词
            'other': 其他
        """
        word_lower = word.lower()
        
        # 检查是否在各个词库中
        if word_lower in [w.lower() for w in self.CT_WORDS + self.CT2_WORDS]:
            return 'ct'
        if word_lower in [w.lower() for w in self.MATERIAL_WORDS]:
            return 'material'
        if word_lower in [w.lower() for w in self.COLOR_WORDS]:
            return 'color'
        if word_lower in [w.lower() for w in self.FUNCTION_WORDS]:
            return 'function'
        if word_lower in [w.lower() for w in self.LOCATION_WORDS]:
            return 'location'
        
        # 风格词（纯风格描述）
        style_words = [
            'modern', 'vintage', 'rustic', 'coastal', 'nautical', 
            'bohemian', 'minimalist', 'industrial', 'farmhouse',
            'traditional', 'contemporary', 'elegant', 'luxury',
            'boho', 'chic', 'glam', 'retro', 'antique', 'classic'
        ]
        if word_lower in style_words:
            return 'style'
        
        # 场景/环境词（地点、环境、抽象场景）- 不应作为L1
        scene_words = [
            'sea', 'ocean', 'beach', 'marine', 'oceanic', 'seaside',
            'lake', 'river', 'pond', 'water', 'aquatic', 'underwater',
            'garden', 'outdoor', 'indoor', 'patio', 'yard', 'lawn',
            'forest', 'woodland', 'jungle', 'desert', 'mountain',
            'home', 'house', 'room', 'space', 'area', 'place',
            'themed', 'theme', 'style', 'inspired', 'look', 'vibe'
        ]
        if word_lower in scene_words:
            return 'scene'
        
        # 检查是否在STYLE_SCENE_WORDS大列表中
        if word_lower in [w.lower() for w in self.STYLE_SCENE_WORDS]:
            return 'scene'
        
        # 动作/状态词 - 不应作为L1
        action_words = [
            'hand', 'made', 'blown', 'painted', 'carved', 'crafted',
            'handmade', 'handcrafted', 'handpainted', 'handblown'
        ]
        if word_lower in action_words:
            return 'craft'
        
        # 默认认为是题材词（具体对象名词）
        return 'theme'
    
    def _calculate_evidence(self, word: str, subset_df: pd.DataFrame = None) -> Dict:
        """计算某个词的强证据指标"""
        df = subset_df if subset_df is not None else self.df
        pattern = self._word_pattern(word)
        mask = df['keyword'].str.contains(pattern, regex=True, na=False)
        matched_df = df[mask]
        
        F = len(matched_df)
        U = matched_df['keyword'].nunique()
        SV = int(matched_df['search_volume'].sum()) if 'search_volume' in matched_df.columns else 0
        R = int(matched_df['natural_rank'].min()) if len(matched_df) > 0 and 'natural_rank' in matched_df.columns else 999
        
        conditions = {
            'F>=2': F >= 2,
            'U>=2': U >= 2,
            'SV>=500': SV >= 500,
            'R<=30': R <= 30
        }
        conditions_met = sum(conditions.values())
        is_strong = conditions_met >= 2
        
        return {
            'word': word,
            'word_type': self._classify_word(word),  # 新增：词性分类
            'F': F,
            'U': U,
            'SV': SV,
            'R': R,
            'conditions': conditions,
            'conditions_met': conditions_met,
            'is_strong': is_strong,
            'matched_keywords': matched_df['keyword'].tolist()[:10]
        }
    
    def _calculate_strict_evidence(self, word: str, subset_df: pd.DataFrame) -> Dict:
        """计算严格阈值的强证据"""
        result = self._calculate_evidence(word, subset_df)
        
        strict_conditions = {
            'F>=3': result['F'] >= 3,
            'U>=3': result['U'] >= 3,
            'SV>=800': result['SV'] >= 800,
            'R<=25': result['R'] <= 25
        }
        strict_met = sum(strict_conditions.values())
        result['strict_conditions'] = strict_conditions
        result['strict_conditions_met'] = strict_met
        result['is_strong_strict'] = strict_met >= 2
        
        return result
    
    def _check_cooccurrence(self, word1: str, word2_list: List[str], 
                            exclude_word: str = None) -> Tuple[bool, List[str]]:
        """检查词的共现关系"""
        w1_pattern = self._word_pattern(word1)
        w2_pattern = '|'.join([self._word_pattern(w) for w in word2_list])
        
        mask = (
            self.df['keyword'].str.contains(w1_pattern, regex=True, na=False) &
            self.df['keyword'].str.contains(w2_pattern, regex=True, na=False)
        )
        
        if exclude_word:
            exclude_pattern = self._word_pattern(exclude_word)
            mask = mask & ~self.df['keyword'].str.contains(exclude_pattern, regex=True, na=False)
        
        matched = self.df[mask]
        return len(matched) > 0, matched['keyword'].tolist()[:5]
    
    def analyze_l1(self) -> Dict:
        """
        分析L1强证据题材词（修复版）
        
        关键改进：
        1. 排除风格/场景词，只保留真正的题材词
        2. 对所有候选词进行词性分类
        3. 题材词优先，风格词仅作为备选并标记警告
        """
        word_freq = defaultdict(lambda: {'count': 0, 'keywords': [], 'sv_sum': 0, 'best_rank': 999})
        
        for _, row in self.df.iterrows():
            words = re.findall(r'\b[a-z]+\b', row['keyword'])
            for word in words:
                # 使用扩展后的排除词集合
                if word not in self.l1_exclude_words and len(word) > 2:
                    word_freq[word]['count'] += 1
                    word_freq[word]['keywords'].append(row['keyword'])
                    word_freq[word]['sv_sum'] += row.get('search_volume', 0)
                    if row.get('natural_rank', 999) < word_freq[word]['best_rank']:
                        word_freq[word]['best_rank'] = row.get('natural_rank', 999)
        
        # 筛选出现≥2次的词作为候选
        candidates = {k: v for k, v in word_freq.items() if v['count'] >= 2}
        
        # 对每个候选计算强证据并分类
        theme_candidates = []  # 题材词
        style_candidates = []  # 风格/场景词（漏网之鱼）
        
        for word in candidates:
            evidence = self._calculate_evidence(word)
            if evidence['is_strong']:
                word_type = evidence['word_type']
                if word_type == 'theme':
                    theme_candidates.append(evidence)
                elif word_type in ['style', 'scene', 'craft']:
                    style_candidates.append(evidence)
                # 其他类型（material, color等）已经被排除，但double check
        
        # 按SV降序排序
        theme_candidates.sort(key=lambda x: (-x['SV'], x['R'], -x['U'], -x['F']))
        style_candidates.sort(key=lambda x: (-x['SV'], x['R'], -x['U'], -x['F']))
        
        # 确定主L1
        if self.l1_user:
            # 用户指定L1
            user_evidence = self._calculate_evidence(self.l1_user)
            primary_l1 = {
                'word': self.l1_user,
                'source': 'user_provided',
                'evidence': user_evidence,
                'warning': None
            }
            alternatives = theme_candidates[:3] if theme_candidates else []
        else:
            # 优先从题材词中选取
            if theme_candidates:
                primary_l1 = {
                    'word': theme_candidates[0]['word'],
                    'source': 'keyword_library_theme',
                    'evidence': theme_candidates[0],
                    'warning': None
                }
                alternatives = theme_candidates[1:4]
            elif style_candidates:
                # 如果没有题材词，才考虑风格词，但要警告
                primary_l1 = {
                    'word': style_candidates[0]['word'],
                    'source': 'keyword_library_style',
                    'evidence': style_candidates[0],
                    'warning': '⚠️ 该词是风格/场景词而非题材词，建议结合产品图确认真正的L1题材'
                }
                alternatives = style_candidates[1:4]
            else:
                primary_l1 = None
                alternatives = []
        
        self.results['l1_analysis'] = {
            'primary_l1': primary_l1,
            'alternatives': [{'word': a['word'], 'word_type': a['word_type'], 
                            'F': a['F'], 'U': a['U'], 'SV': a['SV'], 'R': a['R'],
                            'conditions_met': a['conditions_met'], 'is_strong': a['is_strong'],
                            'matched_keywords': a['matched_keywords']} for a in alternatives],
            'all_theme_candidates': theme_candidates,
            'all_style_candidates': style_candidates,  # 新增：单独列出风格词候选
            'analysis_note': '题材词(theme)优先作为L1；风格词(style/scene)应进入LayerC-风格'
        }
        
        return self.results['l1_analysis']
    
    def analyze_l2(self, l1_word: str) -> Dict:
        """分析L2准入"""
        potential_l2 = ['animal', 'bird', 'pet', 'wildlife', 'creature', 'figure',
                       'sea', 'ocean', 'marine', 'fish', 'plant', 'flower']
        
        l2_results = []
        l1_pattern = self._word_pattern(l1_word)
        l1_subset = self.df[self.df['keyword'].str.contains(l1_pattern, regex=True, na=False)]
        
        for l2 in potential_l2:
            # 跳过风格/场景词
            if l2 in [w.lower() for w in self.STYLE_SCENE_WORDS]:
                continue
                
            result = {'word': l2, 'l2a': {}, 'l2b': {}}
            
            # L2a准入检验
            has_cooccur, cooccur_examples = self._check_cooccurrence(l1_word, [l2])
            result['l2a']['condition1_l1_l2_cooccur'] = {
                'passed': has_cooccur,
                'examples': cooccur_examples
            }
            
            l2_in_l1_evidence = self._calculate_evidence(l2, l1_subset)
            result['l2a']['condition2_strong_in_l1_subset'] = {
                'passed': l2_in_l1_evidence['is_strong'],
                'evidence': l2_in_l1_evidence
            }
            
            result['l2a']['passed'] = has_cooccur and l2_in_l1_evidence['is_strong']
            
            # L2b准入检验
            full_evidence = self._calculate_evidence(l2)
            result['l2b']['condition1_strong_full'] = {
                'passed': full_evidence['is_strong'],
                'evidence': full_evidence
            }
            
            has_ct_cooccur, ct_examples = self._check_cooccurrence(l2, self.CT_WORDS)
            result['l2b']['condition2_l2_ct_cooccur'] = {
                'passed': has_ct_cooccur,
                'examples': ct_examples
            }
            
            result['l2b']['passed'] = full_evidence['is_strong'] and has_ct_cooccur
            
            l2_results.append(result)
        
        l2a_passed = [r for r in l2_results if r['l2a']['passed']]
        l2b_passed = [r for r in l2_results if r['l2b']['passed'] and not r['l2a']['passed']]
        
        self.results['l2_analysis'] = {
            'l1_used': l1_word,
            'all_candidates': l2_results,
            'l2a_passed': l2a_passed,
            'l2b_passed': l2b_passed
        }
        
        return self.results['l2_analysis']
    
    def analyze_layerc(self, l1_word: str) -> Dict:
        """分析LayerC各维度启用准入"""
        l1_pattern = self._word_pattern(l1_word)
        
        non_l1_df = self.df[~self.df['keyword'].str.contains(l1_pattern, regex=True, na=False)]
        
        ct_pattern = '|'.join([self._word_pattern(ct) for ct in self.CT_WORDS])
        category_subset = non_l1_df[non_l1_df['keyword'].str.contains(ct_pattern, regex=True, na=False)]
        
        layerc_results = {
            'l1_used': l1_word,
            'non_l1_count': len(non_l1_df),
            'category_subset_count': len(category_subset),
            'dimensions': {}
        }
        
        dimensions = {
            '功能': {'words': self.FUNCTION_WORDS, 'threshold': 'loose', 'is_fallback': True},
            '材质': {'words': self.MATERIAL_WORDS, 'threshold': 'loose', 'is_fallback': True},
            '摆放位置': {'words': self.LOCATION_WORDS, 'threshold': 'loose', 'is_fallback': True},
            '工艺': {'words': self.CRAFT_WORDS, 'threshold': 'loose', 'is_fallback': False},
            '表面工艺光感': {'words': self.FINISH_WORDS, 'threshold': 'loose', 'is_fallback': False},
            '风格': {'words': self.STYLE_SCENE_WORDS[:50], 'threshold': 'strict', 'is_fallback': False},  # 风格词子集
            '空间场景': {'words': self.LOCATION_WORDS, 'threshold': 'strict', 'is_fallback': False},
        }
        
        for dim_name, config in dimensions.items():
            dim_result = {
                'is_fallback': config['is_fallback'],
                'threshold_type': config['threshold'],
                'words': []
            }
            
            for word in config['words']:
                if config['threshold'] == 'strict':
                    evidence = self._calculate_strict_evidence(word, category_subset)
                    is_strong = evidence.get('is_strong_strict', False)
                else:
                    evidence = self._calculate_evidence(word, category_subset)
                    is_strong = evidence['is_strong']
                
                has_cooccur, cooccur_examples = self._check_cooccurrence(
                    word, self.CT_WORDS, exclude_word=l1_word
                )
                
                if config['is_fallback']:
                    can_output = True
                    output_note = '保底输出' if not (is_strong and has_cooccur) else '强证据'
                else:
                    can_output = is_strong and has_cooccur
                    output_note = '可输出' if can_output else '不输出（证据不足或无共现承接）'
                
                if evidence['F'] > 0 or config['is_fallback']:
                    dim_result['words'].append({
                        'word': word,
                        'evidence': {
                            'F': evidence['F'],
                            'U': evidence['U'],
                            'SV': evidence['SV'],
                            'R': evidence['R'],
                            'is_strong': is_strong
                        },
                        'non_l1_cooccurrence': {
                            'exists': has_cooccur,
                            'examples': cooccur_examples
                        },
                        'can_output': can_output,
                        'output_note': output_note
                    })
            
            dim_result['words'].sort(key=lambda x: -x['evidence']['SV'])
            layerc_results['dimensions'][dim_name] = dim_result
        
        self.results['layerc_analysis'] = layerc_results
        return self.results['layerc_analysis']
    
    def analyze_colors(self, l1_word: str = None) -> Dict:
        """分析颜色词"""
        color_results = []
        
        for color in self.COLOR_WORDS:
            pattern = self._word_pattern(color, include_plural=False)
            mask = self.df['keyword'].str.contains(pattern, regex=True, na=False)
            matched = self.df[mask]
            
            if len(matched) > 0:
                color_results.append({
                    'color': color,
                    'count': len(matched),
                    'sv_sum': int(matched['search_volume'].sum()),
                    'best_rank': int(matched['natural_rank'].min()),
                    'examples': matched['keyword'].tolist()[:5]
                })
        
        color_results.sort(key=lambda x: (-x['sv_sum'], x['best_rank']))
        
        self.results['color_analysis'] = {
            'l1_used': l1_word,
            'colors_found': color_results,
            'total_colors': len(color_results)
        }
        
        return self.results['color_analysis']
    
    def analyze_brands(self) -> Dict:
        """识别品牌词"""
        brand_results = []
        
        for brand in self.KNOWN_BRANDS:
            mask = self.df['keyword'].str.contains(brand, na=False, regex=False)
            matched = self.df[mask]
            
            if len(matched) > 0:
                brand_results.append({
                    'brand': brand,
                    'count': len(matched),
                    'keywords': matched['keyword'].tolist(),
                    'sv_sum': int(matched['search_volume'].sum()),
                    'best_rank': int(matched['natural_rank'].min())
                })
        
        self.results['brand_analysis'] = {
            'brands_found': brand_results,
            'total_brands': len(brand_results)
        }
        
        return self.results['brand_analysis']
    
    def analyze_ct(self) -> Dict:
        """分析CT类目词"""
        ct_results = []
        
        for ct in self.CT_WORDS:
            evidence = self._calculate_evidence(ct)
            if evidence['F'] > 0:
                ct_results.append({
                    'ct': ct,
                    'F': evidence['F'],
                    'SV': evidence['SV'],
                    'best_rank': evidence['R'],
                    'examples': evidence['matched_keywords'][:5]
                })
        
        ct_results.sort(key=lambda x: -x['SV'])
        
        self.results['ct_analysis'] = {
            'ct_found': ct_results,
            'ct1_recommended': [c['ct'] for c in ct_results if c['SV'] >= 500][:3],
            'ct2_available': [c['ct'] for c in ct_results if c['ct'] in self.CT2_WORDS]
        }
        
        return self.results['ct_analysis']
    
    def run_full_analysis(self) -> Dict:
        """运行完整分析流程"""
        # Step 1: 分析L1
        self.analyze_l1()
        
        l1_word = None
        if self.results['l1_analysis']['primary_l1']:
            l1_word = self.results['l1_analysis']['primary_l1']['word']
        
        if l1_word:
            self.analyze_l2(l1_word)
            self.analyze_layerc(l1_word)
            self.analyze_colors(l1_word)
        else:
            self.results['l2_analysis'] = {'error': 'No L1 found'}
            self.results['layerc_analysis'] = {'error': 'No L1 found'}
            self.analyze_colors()
        
        self.analyze_brands()
        self.analyze_ct()
        
        return self.results
    
    def get_summary(self) -> str:
        """生成人类可读的分析摘要"""
        lines = []
        lines.append("=" * 60)
        lines.append("【亚马逊关键词量化分析报告 V2】")
        lines.append("=" * 60)
        
        # L1摘要（增强版）
        lines.append("\n【L1题材词分析】")
        l1 = self.results.get('l1_analysis', {})
        if l1.get('primary_l1'):
            p = l1['primary_l1']
            e = p['evidence']
            word_type = e.get('word_type', 'unknown')
            type_label = {'theme': '✓题材词', 'style': '⚠️风格词', 'scene': '⚠️场景词'}.get(word_type, word_type)
            lines.append(f"  主L1: {p['word']} [{type_label}] (来源: {p['source']})")
            lines.append(f"    F={e['F']}, U={e['U']}, SV={e['SV']}, R={e['R']}")
            if p.get('warning'):
                lines.append(f"    {p['warning']}")
        else:
            lines.append("  主L1: 无")
        
        # 显示备选题材词
        if l1.get('alternatives'):
            alt_str = ', '.join([f"{a['word']}[{a.get('word_type', '?')}]" for a in l1['alternatives']])
            lines.append(f"  备选: {alt_str}")
        
        # 显示风格词候选（如果有）
        if l1.get('all_style_candidates'):
            style_str = ', '.join([f"{s['word']}(SV={s['SV']})" for s in l1['all_style_candidates'][:3]])
            lines.append(f"  风格词候选（应进入LayerC-风格）: {style_str}")
        
        # L2摘要
        lines.append("\n【L2上位类分析】")
        l2 = self.results.get('l2_analysis', {})
        lines.append(f"  L2a通过: {len(l2.get('l2a_passed', []))} 个")
        lines.append(f"  L2b通过: {len(l2.get('l2b_passed', []))} 个")
        
        # LayerC摘要
        lines.append("\n【LayerC维度分析】")
        lc = self.results.get('layerc_analysis', {})
        if 'dimensions' in lc:
            lines.append(f"  非L1子集: {lc.get('non_l1_count', 0)} 条")
            lines.append(f"  类目子集: {lc.get('category_subset_count', 0)} 条")
            for dim_name, dim_data in lc['dimensions'].items():
                strong = [w['word'] for w in dim_data['words'] if w['can_output'] and w['evidence']['is_strong']]
                fallback = [w['word'] for w in dim_data['words'] if w['can_output'] and not w['evidence']['is_strong']]
                status = "保底" if dim_data['is_fallback'] else "非保底"
                lines.append(f"  LayerC-{dim_name} ({status}):")
                if strong:
                    lines.append(f"    强证据可输出: {', '.join(strong[:5])}")
                if fallback and dim_data['is_fallback']:
                    lines.append(f"    保底输出: {', '.join(fallback[:3])}")
                if not strong and not (fallback and dim_data['is_fallback']):
                    lines.append(f"    无可输出词")
        
        # 颜色摘要
        lines.append("\n【颜色组分析】")
        colors = self.results.get('color_analysis', {})
        if colors.get('colors_found'):
            color_list = [f"{c['color']}(SV={c['sv_sum']})" for c in colors['colors_found'][:5]]
            lines.append(f"  发现颜色: {', '.join(color_list)}")
        else:
            lines.append("  发现颜色: 无")
        
        # 品牌词摘要
        lines.append("\n【品牌词分析】")
        brands = self.results.get('brand_analysis', {})
        if brands.get('brands_found'):
            lines.append(f"  发现品牌: {', '.join([b['brand'] for b in brands['brands_found']])}")
        else:
            lines.append("  发现品牌: 无")
        
        # CT摘要
        lines.append("\n【CT类目词分析】")
        ct = self.results.get('ct_analysis', {})
        if ct.get('ct1_recommended'):
            lines.append(f"  推荐CT1: {', '.join(ct['ct1_recommended'])}")
        
        lines.append("\n" + "=" * 60)
        
        return '\n'.join(lines)


def load_keyword_file(filepath: str) -> pd.DataFrame:
    """加载关键词文件"""
    if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath)
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath}")
    
    col_mapping = {}
    for col in df.columns:
        col_lower = str(col).lower()
        if '关键词' in str(col) or 'keyword' in col_lower:
            col_mapping[col] = 'keyword'
        elif '搜索量' in str(col) or 'search' in col_lower or 'volume' in col_lower:
            col_mapping[col] = 'search_volume'
        elif '排名' in str(col) or 'rank' in col_lower:
            col_mapping[col] = 'natural_rank'
    
    df = df.rename(columns=col_mapping)
    
    if 'keyword' not in df.columns:
        raise ValueError("Cannot find keyword column")
    
    if 'search_volume' not in df.columns:
        df['search_volume'] = 0
    if 'natural_rank' not in df.columns:
        df['natural_rank'] = 999
    
    df['search_volume'] = df['search_volume'].fillna(0).astype(int)
    df['natural_rank'] = df['natural_rank'].fillna(999).astype(int)
    
    return df


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python keyword_analyzer_v2.py <keyword_file> [l1_word] [output_json]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    l1_word = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    output_json = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"Loading keywords from: {filepath}")
    df = load_keyword_file(filepath)
    print(f"Loaded {len(df)} keywords")
    
    analyzer = KeywordAnalyzerV2(df, l1_user=l1_word)
    results = analyzer.run_full_analysis()
    
    print(analyzer.get_summary())
    
    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nFull results saved to: {output_json}")
    
    return results


if __name__ == '__main__':
    main()
