from __future__ import annotations

import unittest
from pathlib import Path

from knowledge_loader import load_knowledge
from matchers import confidence_label
from positioning_pipeline import run_pipeline


class TestProductPositioningPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.knowledge_dir = (
            Path(__file__).resolve().parents[1] / "references" / "json"
        )
        cls.domains = load_knowledge(cls.knowledge_dir)

    def test_row_files_loaded(self) -> None:
        self.assertEqual(set(self.domains.keys()), {"audience", "theme", "scene", "style"})
        self.assertGreater(len(self.domains["audience"].rows), 0)
        self.assertGreater(len(self.domains["theme"].rows), 0)
        self.assertGreater(len(self.domains["scene"].rows), 0)
        self.assertGreater(len(self.domains["style"].rows), 0)

    def test_confidence_label(self) -> None:
        self.assertEqual(confidence_label(0.80), "high")
        self.assertEqual(confidence_label(0.60), "medium")
        self.assertEqual(confidence_label(0.59), "low")

    def test_pipeline_output_schema(self) -> None:
        payload = {
            "product_id": "JD25507SZ25112402-silver",
            "image_path": "living_room_coastal_shell_vase.jpg",
            "extra_text": "coastal living room mantel decor shell vase modern style",
        }
        result = run_pipeline(payload, knowledge_dir=self.knowledge_dir)

        self.assertIn("audience", result)
        self.assertIn("theme", result)
        self.assertIn("scene", result)
        self.assertIn("style", result)
        self.assertIn("warnings", result)
        self.assertIn("traceability", result)

        self.assertIn("人群ID", result["audience"])
        self.assertIn("题材编码", result["theme"])
        self.assertIn("场景ID", result["scene"])
        self.assertIn("风格组合ID_F", result["style"])

        self.assertEqual(len(result["audience"]["top3"]) > 0, True)
        self.assertEqual(len(result["theme"]["top3"]) > 0, True)
        self.assertEqual(len(result["scene"]["top3"]) > 0, True)
        self.assertEqual(len(result["style"]["top3"]) > 0, True)

        for item in result["traceability"]:
            self.assertIn("source", item)
            self.assertIn("row_id", item)
            self.assertIn("matched_fields", item)
            self.assertIn("score_breakdown", item)


if __name__ == "__main__":
    unittest.main()
