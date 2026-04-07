from __future__ import annotations

import re
from typing import Any


def confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.60:
        return "medium"
    return "low"


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]{1,}", _normalize_text(text))


def _unique_terms(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        term = _normalize_text(item)
        if not term:
            continue
        if term in seen:
            continue
        seen.add(term)
        result.append(term)
    return result


def _field_match(query_terms: list[str], field_value: Any) -> tuple[float, list[str]]:
    field_text = _normalize_text(field_value)
    if not field_text:
        return 0.0, []

    terms = _unique_terms(query_terms)
    if not terms:
        return 0.0, []

    matched = [term for term in terms if term in field_text]
    if matched:
        score = min(1.0, len(matched) / max(1, min(len(terms), 5)))
        return score, matched[:6]

    query_tokens: set[str] = set()
    for term in terms:
        query_tokens.update(_tokenize(term))
    field_tokens = set(_tokenize(field_text))
    token_hits = sorted(query_tokens & field_tokens)
    if not token_hits:
        return 0.0, []

    score = min(1.0, len(token_hits) / max(1, min(len(query_tokens), 5)))
    return score, token_hits[:6]


def _contains_any(field_value: Any, hints: list[str]) -> bool:
    text = _normalize_text(field_value)
    if not text:
        return False
    for hint in _unique_terms(hints):
        if hint and hint in text:
            return True
    return False


def _clamp(score: float) -> float:
    return max(0.0, min(1.0, score))


def _sort_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda item: (-float(item["score"]), str(item["id"])),
    )


def _format_top3(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top3: list[dict[str, Any]] = []
    for item in _sort_candidates(candidates)[:3]:
        top3.append(
            {
                "id": item["id"],
                "name": item["name"],
                "score": round(float(item["score"]), 4),
                "evidence": item.get("evidence", []),
            }
        )
    return top3


def _empty_result(id_field: str, name_field: str, source: str) -> dict[str, Any]:
    return {
        "id_field": id_field,
        "name_field": name_field,
        "source": source,
        "score": 0.0,
        "confidence": "low",
        "top1": None,
        "top3": [],
        "score_breakdown": {},
        "matched_fields": [],
    }


def match_audience(rows: list[dict[str, Any]], features: dict[str, Any]) -> dict[str, Any]:
    if not rows:
        return _empty_result("人群ID", "人群名称", "audience_rows.json")

    audience_terms = list(features.get("audience", {}).get("keywords", []))
    style_terms = list(features.get("style", {}).get("main_candidates", [])) + list(
        features.get("style", {}).get("keywords", [])
    )
    tokens = list(features.get("tokens", []))

    component_queries = {
        "标签": audience_terms,
        "概述": tokens,
        "生活方式": audience_terms + tokens,
        "风格偏好": style_terms + tokens,
        "雕塑偏好": ["sculpture", "statue", "figurine", "雕塑", "摆件"] + tokens,
        "花瓶偏好": ["vase", "flower", "planter", "花瓶", "花器"] + tokens,
        "购物行为": audience_terms + tokens,
        "痛点": audience_terms + tokens,
    }

    weights = {
        "标签": 0.20,
        "概述": 0.15,
        "生活方式": 0.15,
        "风格偏好": 0.20,
        "雕塑偏好": 0.10,
        "花瓶偏好": 0.10,
        "购物行为": 0.05,
        "痛点": 0.05,
    }

    field_map = {
        "标签": "人群标签（Tag，中英）",
        "概述": "一句话概述",
        "生活方式": "生活方式与情绪需求",
        "风格偏好": "家居整体风格偏好",
        "雕塑偏好": "雕塑偏好",
        "花瓶偏好": "花瓶偏好",
        "购物行为": "购物行为与决策重点",
        "痛点": "典型痛点",
    }

    candidates: list[dict[str, Any]] = []
    for row in rows:
        breakdown: dict[str, float] = {}
        evidence_by_field: dict[str, list[str]] = {}

        for component, row_field in field_map.items():
            comp_score, comp_evidence = _field_match(component_queries[component], row.get(row_field))
            breakdown[component] = comp_score
            if comp_evidence:
                evidence_by_field[row_field] = comp_evidence

        total_score = sum(weights[key] * breakdown[key] for key in weights)
        row_id = str(row.get("人群ID") or "")
        row_name = str(row.get("人群名称") or row_id)

        evidence_flat: list[str] = []
        for evidence in evidence_by_field.values():
            for item in evidence:
                if item not in evidence_flat:
                    evidence_flat.append(item)

        candidates.append(
            {
                "id": row_id,
                "name": row_name,
                "score": _clamp(total_score),
                "evidence": evidence_flat[:8],
                "score_breakdown": breakdown,
                "matched_fields": sorted(evidence_by_field.keys()),
                "row": row,
            }
        )

    sorted_candidates = _sort_candidates(candidates)
    top1 = sorted_candidates[0]
    return {
        "id_field": "人群ID",
        "name_field": "人群名称",
        "source": "audience_rows.json",
        "score": round(float(top1["score"]), 4),
        "confidence": confidence_label(float(top1["score"])),
        "top1": top1,
        "top3": _format_top3(sorted_candidates),
        "score_breakdown": top1["score_breakdown"],
        "matched_fields": top1["matched_fields"],
    }


def match_theme(rows: list[dict[str, Any]], features: dict[str, Any]) -> dict[str, Any]:
    if not rows:
        return _empty_result("题材编码", "题材L1", "theme_rows.json")

    l1_candidates = list(features.get("theme", {}).get("l1_candidates", []))
    l2_candidates = list(features.get("theme", {}).get("l2_candidates", []))
    l3_keywords = list(features.get("theme", {}).get("l3_keywords", []))

    weights = {"L1": 0.45, "L2": 0.30, "L3": 0.25}

    candidates: list[dict[str, Any]] = []
    for row in rows:
        l1_score, l1_evidence = _field_match(l1_candidates, row.get("题材L1"))
        l2_score, l2_evidence = _field_match(l2_candidates, row.get("题材L2"))
        l3_score, l3_evidence = _field_match(l3_keywords, row.get("题材L3"))

        breakdown = {"L1": l1_score, "L2": l2_score, "L3": l3_score}
        total_score = (
            weights["L1"] * l1_score
            + weights["L2"] * l2_score
            + weights["L3"] * l3_score
        )

        row_id = str(row.get("题材编码") or "")
        row_name = "/".join(
            part
            for part in [
                str(row.get("题材L1") or ""),
                str(row.get("题材L2") or ""),
            ]
            if part
        ) or row_id

        evidence = []
        for item in l1_evidence + l2_evidence + l3_evidence:
            if item not in evidence:
                evidence.append(item)

        matched_fields = []
        if l1_evidence:
            matched_fields.append("题材L1")
        if l2_evidence:
            matched_fields.append("题材L2")
        if l3_evidence:
            matched_fields.append("题材L3")

        candidates.append(
            {
                "id": row_id,
                "name": row_name,
                "score": _clamp(total_score),
                "evidence": evidence[:8],
                "score_breakdown": breakdown,
                "matched_fields": matched_fields,
                "row": row,
            }
        )

    sorted_candidates = _sort_candidates(candidates)
    top1 = sorted_candidates[0]
    return {
        "id_field": "题材编码",
        "name_field": "题材L1",
        "source": "theme_rows.json",
        "score": round(float(top1["score"]), 4),
        "confidence": confidence_label(float(top1["score"])),
        "top1": top1,
        "top3": _format_top3(sorted_candidates),
        "score_breakdown": top1["score_breakdown"],
        "matched_fields": top1["matched_fields"],
    }


def _hard_filter_scene_rows(rows: list[dict[str, Any]], scene_features: dict[str, Any]) -> list[dict[str, Any]]:
    filtered = list(rows)
    filters = [
        ("scene_type_candidates", "场景类型（Scene Type）"),
        ("room_candidates", "房间/区域"),
        ("surface_candidates", "承载面/位置"),
    ]

    for feature_key, row_field in filters:
        hints = list(scene_features.get(feature_key, []))
        if not hints:
            continue
        narrowed = [row for row in filtered if _contains_any(row.get(row_field), hints)]
        if narrowed:
            filtered = narrowed

    return filtered


def match_scene(rows: list[dict[str, Any]], features: dict[str, Any]) -> dict[str, Any]:
    if not rows:
        return _empty_result("场景ID", "场景名称_CN", "scene_rows.json")

    scene_features = dict(features.get("scene", {}))
    style_features = dict(features.get("style", {}))
    element_keywords = list(features.get("elements", {}).get("keywords", []))
    category_keywords = list(features.get("categories", {}).get("keywords", []))
    scene_keywords = list(scene_features.get("keywords", []))

    candidates_pool = _hard_filter_scene_rows(rows, scene_features)

    weights = {
        "类型": 0.20,
        "房间": 0.20,
        "承载面": 0.20,
        "层级": 0.05,
        "摆放组合": 0.10,
        "适配品类": 0.10,
        "产品标签": 0.05,
        "构图": 0.03,
        "风格提示": 0.03,
        "光线": 0.02,
    }

    candidates: list[dict[str, Any]] = []
    for row in candidates_pool:
        type_score, type_ev = _field_match(scene_features.get("scene_type_candidates", []), row.get("场景类型（Scene Type）"))
        room_score, room_ev = _field_match(scene_features.get("room_candidates", []), row.get("房间/区域"))
        surface_score, surface_ev = _field_match(scene_features.get("surface_candidates", []), row.get("承载面/位置"))
        hierarchy_score, hierarchy_ev = _field_match(scene_keywords, row.get("场景层级"))
        layout_score, layout_ev = _field_match(scene_keywords + element_keywords, row.get("典型摆放组合"))
        category_score, category_ev = _field_match(category_keywords, row.get("适配品类"))
        product_tag_score, product_tag_ev = _field_match(scene_keywords, row.get("适配产品属性标签"))
        composition_score, composition_ev = _field_match(scene_keywords, row.get("关键构图模板"))
        style_hint_score, style_hint_ev = _field_match(
            list(style_features.get("main_candidates", [])) + list(style_features.get("keywords", [])),
            row.get("适配风格提示"),
        )
        light_score, light_ev = _field_match(scene_keywords, row.get("光线/色温建议"))

        black_score, black_ev = _field_match(element_keywords, row.get("道具黑名单"))
        penalty = 0.25 if black_score > 0 else 0.0

        breakdown = {
            "类型": type_score,
            "房间": room_score,
            "承载面": surface_score,
            "层级": hierarchy_score,
            "摆放组合": layout_score,
            "适配品类": category_score,
            "产品标签": product_tag_score,
            "构图": composition_score,
            "风格提示": style_hint_score,
            "光线": light_score,
            "黑名单惩罚": -penalty,
        }

        base_score = sum(weights[key] * breakdown[key] for key in weights)
        total_score = _clamp(base_score - penalty)

        evidence = []
        for item in (
            type_ev
            + room_ev
            + surface_ev
            + hierarchy_ev
            + layout_ev
            + category_ev
            + product_tag_ev
            + composition_ev
            + style_hint_ev
            + light_ev
        ):
            if item not in evidence:
                evidence.append(item)

        matched_fields = []
        field_evidence = {
            "场景类型（Scene Type）": type_ev,
            "房间/区域": room_ev,
            "承载面/位置": surface_ev,
            "场景层级": hierarchy_ev,
            "典型摆放组合": layout_ev,
            "适配品类": category_ev,
            "适配产品属性标签": product_tag_ev,
            "关键构图模板": composition_ev,
            "适配风格提示": style_hint_ev,
            "光线/色温建议": light_ev,
            "道具黑名单": black_ev,
        }
        for field_name, field_hits in field_evidence.items():
            if field_hits:
                matched_fields.append(field_name)

        candidates.append(
            {
                "id": str(row.get("场景ID") or ""),
                "name": str(row.get("场景名称_CN") or row.get("场景ID") or ""),
                "score": total_score,
                "evidence": evidence[:8],
                "score_breakdown": breakdown,
                "matched_fields": matched_fields,
                "row": row,
            }
        )

    sorted_candidates = _sort_candidates(candidates)
    top1 = sorted_candidates[0]
    return {
        "id_field": "场景ID",
        "name_field": "场景名称_CN",
        "source": "scene_rows.json",
        "score": round(float(top1["score"]), 4),
        "confidence": confidence_label(float(top1["score"])),
        "top1": top1,
        "top3": _format_top3(sorted_candidates),
        "score_breakdown": top1["score_breakdown"],
        "matched_fields": top1["matched_fields"],
    }


def _audience_compat_score(audience_hint_field: Any, audience_ids: list[str]) -> tuple[float, list[str]]:
    hint_text = _normalize_text(audience_hint_field)
    if not hint_text or not audience_ids:
        return 0.0, []

    primary = _normalize_text(audience_ids[0])
    if primary and primary in hint_text:
        return 1.0, [audience_ids[0]]

    for candidate in audience_ids[1:]:
        candidate_norm = _normalize_text(candidate)
        if candidate_norm and candidate_norm in hint_text:
            return 0.6, [candidate]

    return 0.0, []


def match_style(
    rows: list[dict[str, Any]],
    features: dict[str, Any],
    audience_match: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not rows:
        return _empty_result("风格组合ID_F", "组合名称_CN", "style_rows.json")

    style_features = dict(features.get("style", {}))
    style_keywords = list(style_features.get("keywords", []))
    main_candidates = list(style_features.get("main_candidates", []))
    secondary_candidates = list(style_features.get("secondary_candidates", []))
    element_keywords = list(features.get("elements", {}).get("keywords", []))

    audience_ids: list[str] = []
    if audience_match and audience_match.get("top3"):
        audience_ids = [str(item.get("id") or "") for item in audience_match["top3"] if item.get("id")]

    weights = {
        "主风格": 0.25,
        "辅风格": 0.15,
        "执行口径": 0.20,
        "必须元素": 0.20,
        "适配人群": 0.20,
    }

    candidates: list[dict[str, Any]] = []
    for row in rows:
        main_style_score, main_ev = _field_match(main_candidates + style_keywords, row.get("主风格名称_CN"))
        secondary_style_score, secondary_ev = _field_match(
            secondary_candidates + style_keywords,
            f"{row.get('辅风格1名称_CN', '')} {row.get('辅风格2名称_CN', '')}",
        )
        execution_score, execution_ev = _field_match(style_keywords, row.get("执行口径标签"))
        must_score, must_ev = _field_match(element_keywords + style_keywords, row.get("必须元素_≤3条"))
        audience_score, audience_ev = _audience_compat_score(row.get("适配人群ID_建议"), audience_ids)

        forbid_score, forbid_ev = _field_match(element_keywords, row.get("禁忌元素_≤3条"))
        penalty = 0.30 if forbid_score > 0 else 0.0

        breakdown = {
            "主风格": main_style_score,
            "辅风格": secondary_style_score,
            "执行口径": execution_score,
            "必须元素": must_score,
            "适配人群": audience_score,
            "禁忌惩罚": -penalty,
        }

        base_score = sum(weights[key] * breakdown[key] for key in weights)
        total_score = _clamp(base_score - penalty)

        evidence = []
        for item in main_ev + secondary_ev + execution_ev + must_ev + audience_ev:
            if item not in evidence:
                evidence.append(item)

        matched_fields = []
        field_evidence = {
            "主风格名称_CN": main_ev,
            "辅风格1名称_CN": secondary_ev,
            "执行口径标签": execution_ev,
            "必须元素_≤3条": must_ev,
            "适配人群ID_建议": audience_ev,
            "禁忌元素_≤3条": forbid_ev,
        }
        for field_name, field_hits in field_evidence.items():
            if field_hits:
                matched_fields.append(field_name)

        candidates.append(
            {
                "id": str(row.get("风格组合ID_F") or ""),
                "name": str(row.get("组合名称_CN") or row.get("风格组合ID_F") or ""),
                "score": total_score,
                "evidence": evidence[:8],
                "score_breakdown": breakdown,
                "matched_fields": matched_fields,
                "row": row,
            }
        )

    sorted_candidates = _sort_candidates(candidates)
    top1 = sorted_candidates[0]
    return {
        "id_field": "风格组合ID_F",
        "name_field": "组合名称_CN",
        "source": "style_rows.json",
        "score": round(float(top1["score"]), 4),
        "confidence": confidence_label(float(top1["score"])),
        "top1": top1,
        "top3": _format_top3(sorted_candidates),
        "score_breakdown": top1["score_breakdown"],
        "matched_fields": top1["matched_fields"],
    }
