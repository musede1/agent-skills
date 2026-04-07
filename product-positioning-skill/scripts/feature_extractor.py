from __future__ import annotations

import re
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a", "an", "and", "or", "the", "for", "to", "of", "in", "on", "with", "is", "are",
    "that", "this", "it", "as", "at", "by", "from", "be", "was", "were", "into", "your",
    "our", "their", "产品", "图片", "风格", "场景", "题材", "人群",
}

THEME_L1_HINTS = {
    "动物": ["animal", "dog", "cat", "horse", "deer", "fox", "bear", "rabbit", "elephant", "giraffe", "鹿", "动物"],
    "人物/面部": ["figure", "person", "human", "face", "head", "bust", "angel", "人物", "面部", "头像", "人像"],
    "抽象几何": ["abstract", "geometry", "geometric", "shape", "ring", "sphere", "cube", "抽象", "几何"],
    "植物/花叶": ["flower", "floral", "leaf", "plant", "botanical", "rose", "tulip", "植物", "花", "花叶"],
    "海洋/航海": ["ocean", "sea", "coastal", "nautical", "shell", "conch", "anchor", "marine", "海洋", "航海", "贝壳"],
}

THEME_L2_HINTS = {
    "哺乳类": ["dog", "cat", "horse", "deer", "fox", "bear", "兔", "鹿", "马"],
    "人像-面部": ["face", "head", "bust", "portrait", "头像", "面部"],
    "基础几何体": ["sphere", "cube", "ring", "geometry", "几何", "立方", "圆环"],
    "花卉": ["flower", "rose", "tulip", "lily", "peony", "花", "花卉"],
    "航海器具": ["anchor", "helm", "rudder", "oar", "船舵", "船桨", "锚"],
}

SCENE_TYPE_HINTS = {
    "摆放/Placement": ["placement", "display", "vignette", "摆放", "陈列", "台面"],
}

ROOM_HINTS = {
    "客厅": ["living room", "living", "客厅"],
    "卧室": ["bedroom", "卧室"],
    "餐厅": ["dining", "dining room", "餐厅"],
    "玄关": ["entryway", "entry", "foyer", "玄关"],
    "书房": ["study", "office", "书房"],
    "厨房": ["kitchen", "厨房"],
    "浴室": ["bathroom", "浴室"],
    "户外": ["outdoor", "patio", "garden", "户外"],
}

SURFACE_HINTS = {
    "壁炉台(Mantel)": ["mantel", "fireplace", "壁炉"],
    "茶几(Coffee Table)": ["coffee table", "茶几"],
    "边几/角几(Side Table)": ["side table", "end table", "边几", "角几"],
    "餐桌(Dining Table)": ["dining table", "餐桌"],
    "玄关柜(Console)": ["console", "entry table", "玄关柜"],
    "书架/置物架(Shelf)": ["shelf", "bookshelf", "书架", "置物架"],
}

STYLE_HINTS = {
    "极简": ["minimal", "minimalist", "极简", "简约"],
    "当代": ["contemporary", "modern", "当代", "现代"],
    "有机现代": ["organic modern", "organic", "有机现代"],
    "当代几何/解构": ["geometric", "deconstruct", "geometry", "几何", "解构"],
    "金缮/侘寂": ["wabi", "japandi", "侘寂", "金缮"],
    "海岸": ["coastal", "nautical", "beach", "海岸", "航海"],
    "现代农舍": ["farmhouse", "现代农舍"],
}

AUDIENCE_HINTS = {
    "家庭导向": ["family", "kids", "child", "家庭", "亲子", "陪伴"],
    "礼物导向": ["gift", "present", "wedding", "anniversary", "生日", "礼物"],
    "设计导向": ["designer", "aesthetic", "minimal", "高级", "设计感"],
    "秩序收纳导向": ["organized", "tidy", "storage", "收纳", "秩序"],
}

ELEMENT_HINTS = {
    "book": ["book", "books", "书", "书本"],
    "tray": ["tray", "托盘"],
    "branch": ["branch", "twig", "干枝"],
    "candle": ["candle", "蜡烛"],
    "vase": ["vase", "花瓶", "花器"],
    "sculpture": ["sculpture", "statue", "figurine", "雕塑", "摆件"],
    "plant": ["plant", "leaf", "flower", "绿植", "花"],
    "lamp": ["lamp", "light", "台灯", "灯"],
}

CATEGORY_HINTS = {
    "雕塑": ["sculpture", "statue", "figurine", "雕塑", "摆件", "雕像"],
    "花瓶": ["vase", "planter", "花瓶", "花器"],
}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokenize(text: str) -> list[str]:
    raw_tokens = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]{1,}", text.lower())
    tokens: list[str] = []
    for token in raw_tokens:
        if token in STOPWORDS:
            continue
        if len(token) == 1 and token.isascii():
            continue
        tokens.append(token)
    return tokens


def _collect_hits(text: str, mapping: dict[str, list[str]]) -> list[str]:
    hits: list[str] = []
    for canonical, aliases in mapping.items():
        for alias in aliases:
            alias_norm = _normalize_text(alias)
            if alias_norm and alias_norm in text:
                hits.append(canonical)
                break
    return hits


def extract_features(product_id: str = "", image_path: str = "", extra_text: str = "") -> dict[str, Any]:
    image_stem = Path(image_path).stem if image_path else ""
    source_text = " ".join(part for part in [product_id, image_stem, extra_text] if part)
    normalized_text = _normalize_text(source_text)
    tokens = _tokenize(normalized_text)

    style_terms = _collect_hits(normalized_text, STYLE_HINTS)
    audience_terms = _collect_hits(normalized_text, AUDIENCE_HINTS)
    theme_l1 = _collect_hits(normalized_text, THEME_L1_HINTS)
    theme_l2 = _collect_hits(normalized_text, THEME_L2_HINTS)

    scene_types = _collect_hits(normalized_text, SCENE_TYPE_HINTS)
    rooms = _collect_hits(normalized_text, ROOM_HINTS)
    surfaces = _collect_hits(normalized_text, SURFACE_HINTS)

    element_terms = _collect_hits(normalized_text, ELEMENT_HINTS)
    category_terms = _collect_hits(normalized_text, CATEGORY_HINTS)

    return {
        "raw_text": source_text,
        "normalized_text": normalized_text,
        "tokens": tokens,
        "theme": {
            "l1_candidates": theme_l1,
            "l2_candidates": theme_l2,
            "l3_keywords": tokens,
        },
        "scene": {
            "scene_type_candidates": scene_types,
            "room_candidates": rooms,
            "surface_candidates": surfaces,
            "keywords": tokens,
        },
        "style": {
            "main_candidates": style_terms,
            "secondary_candidates": style_terms[1:],
            "keywords": tokens,
        },
        "audience": {
            "keywords": audience_terms + tokens,
        },
        "elements": {
            "keywords": element_terms,
        },
        "categories": {
            "keywords": category_terms,
        },
    }


def extract_features_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return extract_features(
        product_id=str(payload.get("product_id") or ""),
        image_path=str(payload.get("image_path") or ""),
        extra_text=str(payload.get("extra_text") or ""),
    )
