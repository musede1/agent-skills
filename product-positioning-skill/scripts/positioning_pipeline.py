from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from .feature_extractor import extract_features, extract_features_from_payload
    from .knowledge_loader import load_knowledge
    from .matchers import match_audience, match_scene, match_style, match_theme
except ImportError:
    from feature_extractor import extract_features, extract_features_from_payload
    from knowledge_loader import load_knowledge
    from matchers import match_audience, match_scene, match_style, match_theme


class PositioningPipeline:
    def __init__(self, knowledge_dir: Path | str):
        self.knowledge_dir = Path(knowledge_dir).resolve()
        self.knowledge = load_knowledge(self.knowledge_dir)

    def run(
        self,
        product_id: str = "",
        image_path: str = "",
        extra_text: str = "",
    ) -> dict[str, Any]:
        features = extract_features(product_id=product_id, image_path=image_path, extra_text=extra_text)
        return self._run_with_features(features)

    def run_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        features = extract_features_from_payload(payload)
        return self._run_with_features(features)

    def _run_with_features(self, features: dict[str, Any]) -> dict[str, Any]:
        audience_match = match_audience(self.knowledge["audience"].rows, features)
        theme_match = match_theme(self.knowledge["theme"].rows, features)
        scene_match = match_scene(self.knowledge["scene"].rows, features)
        style_match = match_style(self.knowledge["style"].rows, features, audience_match=audience_match)

        warnings = self._build_warnings(
            features=features,
            audience_match=audience_match,
            theme_match=theme_match,
            scene_match=scene_match,
            style_match=style_match,
        )

        return {
            "audience": {
                "人群ID": self._top1_id(audience_match),
                "人群名称": self._top1_name(audience_match),
                "score": audience_match["score"],
                "confidence": audience_match["confidence"],
                "top3": audience_match["top3"],
            },
            "theme": {
                "题材编码": self._top1_id(theme_match),
                "score": theme_match["score"],
                "confidence": theme_match["confidence"],
                "top3": theme_match["top3"],
            },
            "scene": {
                "场景ID": self._top1_id(scene_match),
                "场景名称_CN": self._top1_name(scene_match),
                "score": scene_match["score"],
                "confidence": scene_match["confidence"],
                "top3": scene_match["top3"],
            },
            "style": {
                "风格组合ID_F": self._top1_id(style_match),
                "组合名称_CN": self._top1_name(style_match),
                "score": style_match["score"],
                "confidence": style_match["confidence"],
                "top3": style_match["top3"],
            },
            "warnings": warnings,
            "traceability": self._build_traceability(
                audience_match=audience_match,
                theme_match=theme_match,
                scene_match=scene_match,
                style_match=style_match,
            ),
        }

    @staticmethod
    def _top1_id(match_result: dict[str, Any]) -> str:
        top1 = match_result.get("top1")
        return str((top1 or {}).get("id") or "")

    @staticmethod
    def _top1_name(match_result: dict[str, Any]) -> str:
        top1 = match_result.get("top1")
        return str((top1 or {}).get("name") or "")

    def _build_warnings(
        self,
        *,
        features: dict[str, Any],
        audience_match: dict[str, Any],
        theme_match: dict[str, Any],
        scene_match: dict[str, Any],
        style_match: dict[str, Any],
    ) -> list[str]:
        warnings: list[str] = []

        low_conf_domains = {
            "AUDIENCE": audience_match,
            "THEME": theme_match,
            "SCENE": scene_match,
            "STYLE": style_match,
        }
        for domain_name, result in low_conf_domains.items():
            if float(result.get("score", 0.0)) < 0.60:
                warnings.append(f"LOW_CONFIDENCE_{domain_name}")

        style_audience_score = float(style_match.get("score_breakdown", {}).get("适配人群", 0.0))
        if (
            float(audience_match.get("score", 0.0)) >= 0.60
            and float(style_match.get("score", 0.0)) >= 0.60
            and style_audience_score < 0.30
        ):
            warnings.append("STYLE_AUDIENCE_MISMATCH")

        scene_style_score = float(scene_match.get("score_breakdown", {}).get("风格提示", 0.0))
        if float(style_match.get("score", 0.0)) >= 0.60 and scene_style_score < 0.25:
            warnings.append("SCENE_STYLE_WEAK_MATCH")

        has_category_signal = bool(features.get("categories", {}).get("keywords"))
        scene_category_score = float(scene_match.get("score_breakdown", {}).get("适配品类", 0.0))
        if has_category_signal and scene_category_score < 0.20:
            warnings.append("SCENE_CATEGORY_MISMATCH")

        deduped: list[str] = []
        for item in warnings:
            if item not in deduped:
                deduped.append(item)
        return deduped

    def _build_traceability(self, **domain_matches: dict[str, Any]) -> list[dict[str, Any]]:
        traceability: list[dict[str, Any]] = []
        for domain_name, match_result in domain_matches.items():
            top1 = match_result.get("top1") or {}
            traceability.append(
                {
                    "source": match_result.get("source", ""),
                    "row_id": top1.get("id", ""),
                    "matched_fields": match_result.get("matched_fields", []),
                    "score_breakdown": match_result.get("score_breakdown", {}),
                    "domain": domain_name,
                }
            )
        return traceability


def run_pipeline(
    payload: dict[str, Any],
    knowledge_dir: Path | str | None = None,
) -> dict[str, Any]:
    base_dir = (
        Path(knowledge_dir).resolve()
        if knowledge_dir
        else Path(__file__).resolve().parents[1] / "references" / "json"
    )
    pipeline = PositioningPipeline(base_dir)
    return pipeline.run_payload(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run product positioning pipeline.")
    parser.add_argument("--product-id", default="", help="Product id")
    parser.add_argument("--image-path", default="", help="Image path")
    parser.add_argument("--extra-text", default="", help="Extra plain text context")
    parser.add_argument("--input-json", default="", help="Optional json payload path")
    parser.add_argument(
        "--knowledge-dir",
        default=str(Path(__file__).resolve().parents[1] / "references" / "json"),
        help="Knowledge base directory containing *_rows.json files",
    )
    parser.add_argument("--output", default="", help="Optional output json file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.input_json:
        payload = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    else:
        payload = {
            "product_id": args.product_id,
            "image_path": args.image_path,
            "extra_text": args.extra_text,
        }

    result = run_pipeline(payload=payload, knowledge_dir=args.knowledge_dir)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")

    print(rendered)


if __name__ == "__main__":
    main()
