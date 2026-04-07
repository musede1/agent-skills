from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROW_FILES = {
    "audience": "audience_rows.json",
    "theme": "theme_rows.json",
    "scene": "scene_rows.json",
    "style": "style_rows.json",
}

ID_FIELDS = {
    "audience": "人群ID",
    "theme": "题材编码",
    "scene": "场景ID",
    "style": "风格组合ID_F",
}

NAME_FIELDS = {
    "audience": "人群名称",
    "theme": "题材L1",
    "scene": "场景名称_CN",
    "style": "组合名称_CN",
}


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {str(k).strip(): _normalize_value(v) for k, v in row.items()}


def _build_search_text(row: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in row.values():
        if value is None:
            continue
        text = str(value).strip()
        if text:
            parts.append(text)
    return " ".join(parts).lower()


@dataclass(slots=True)
class KnowledgeDomain:
    name: str
    rows: list[dict[str, Any]]
    id_field: str
    name_field: str
    by_id: dict[str, dict[str, Any]]
    search_text_by_id: dict[str, str]

    @property
    def row_count(self) -> int:
        return len(self.rows)


class KnowledgeLoader:
    def __init__(self, knowledge_dir: Path | str):
        self.knowledge_dir = Path(knowledge_dir).resolve()

    def _load_row_file(self, file_path: Path) -> list[dict[str, Any]]:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Knowledge file must be a list: {file_path}")

        rows: list[dict[str, Any]] = []
        for idx, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ValueError(f"Row {idx} in {file_path} is not an object")
            row = _normalize_row(item)
            if any(v is not None for v in row.values()):
                rows.append(row)
        return rows

    def load(self) -> dict[str, KnowledgeDomain]:
        missing: list[str] = []
        domains: dict[str, KnowledgeDomain] = {}

        for domain, file_name in ROW_FILES.items():
            file_path = self.knowledge_dir / file_name
            if not file_path.exists():
                missing.append(str(file_path))
                continue

            rows = self._load_row_file(file_path)
            id_field = ID_FIELDS[domain]
            name_field = NAME_FIELDS[domain]

            by_id: dict[str, dict[str, Any]] = {}
            search_text_by_id: dict[str, str] = {}

            for idx, row in enumerate(rows):
                row_id = row.get(id_field)
                if row_id is None:
                    row_id = f"{domain}_{idx + 1:04d}"
                row_id = str(row_id).strip()
                by_id[row_id] = row
                search_text_by_id[row_id] = _build_search_text(row)

            domains[domain] = KnowledgeDomain(
                name=domain,
                rows=rows,
                id_field=id_field,
                name_field=name_field,
                by_id=by_id,
                search_text_by_id=search_text_by_id,
            )

        if missing:
            raise FileNotFoundError(
                "Missing knowledge files:\n" + "\n".join(missing)
            )

        return domains


def load_knowledge(knowledge_dir: Path | str) -> dict[str, KnowledgeDomain]:
    return KnowledgeLoader(knowledge_dir).load()
