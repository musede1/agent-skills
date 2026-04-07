from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


DOMAIN_OUTPUT_FILES = {
    "audience": "audience_rows.json",
    "theme": "theme_rows.json",
    "scene": "scene_rows.json",
    "style": "style_rows.json",
}

DOMAIN_SIGNATURES: dict[str, set[str]] = {
    "audience": {"人群ID", "人群名称", "一句话概述"},
    "theme": {"题材编码", "题材L1", "题材L2", "题材L3"},
    "scene": {"场景ID", "场景名称_CN", "场景类型（Scene Type）"},
    "style": {"风格组合ID_F", "组合名称_CN", "执行口径标签"},
}


def normalize_cell(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def read_workbook_rows(xlsx_path: Path) -> list[dict[str, Any]]:
    xls = pd.ExcelFile(xlsx_path)
    all_rows: list[dict[str, Any]] = []
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
        df.columns = [str(c).strip() for c in df.columns]
        for raw_row in df.to_dict(orient="records"):
            row = {str(k).strip(): normalize_cell(v) for k, v in raw_row.items()}
            if all(v is None for v in row.values()):
                continue
            all_rows.append(row)
    return all_rows


def infer_domain(rows: list[dict[str, Any]]) -> str | None:
    if not rows:
        return None
    columns: set[str] = set()
    for row in rows:
        columns.update(str(k).strip() for k in row.keys())
    for domain, required in DOMAIN_SIGNATURES.items():
        if required.issubset(columns):
            return domain
    return None


def workbook_to_legacy_json(xlsx_path: Path) -> dict[str, Any]:
    xls = pd.ExcelFile(xlsx_path)
    data: dict[str, Any] = {
        "source_file": xlsx_path.name,
        "sheet_order": list(xls.sheet_names),
        "sheets": {},
    }
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
        df.columns = [str(c).strip() for c in df.columns]
        rows = []
        for raw_row in df.to_dict(orient="records"):
            row = {str(k).strip(): normalize_cell(v) for k, v in raw_row.items()}
            if all(v is None for v in row.values()):
                continue
            rows.append(row)
        data["sheets"][sheet_name] = {
            "row_count": len(rows),
            "columns": list(df.columns),
            "rows": rows,
        }
    return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert product-positioning xlsx files to JSON knowledge base files."
    )
    parser.add_argument(
        "--out-dir",
        default="references/json",
        help="Output directory relative to skill root (default: references/json).",
    )
    parser.add_argument(
        "--row-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Generate row-only JSON files (default: true).",
    )
    parser.add_argument(
        "--keep-workbook-json",
        action="store_true",
        help="Also generate workbook-level legacy JSON files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    out_dir = (skill_dir / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    workbook_paths = sorted(skill_dir.glob("*.xlsx"))
    if not workbook_paths:
        raise SystemExit(f"No xlsx files found in {skill_dir}")

    manifest: list[dict[str, Any]] = []
    grouped_rows: dict[str, list[dict[str, Any]]] = {k: [] for k in DOMAIN_OUTPUT_FILES}
    unmatched_files: list[str] = []

    for xlsx in workbook_paths:
        rows = read_workbook_rows(xlsx)
        domain = infer_domain(rows)
        if args.row_only:
            if domain is None:
                unmatched_files.append(xlsx.name)
            else:
                grouped_rows[domain].extend(rows)
                manifest.append(
                    {
                        "source_file": xlsx.name,
                        "domain": domain,
                        "row_count": len(rows),
                        "json_file": str((out_dir / DOMAIN_OUTPUT_FILES[domain]).relative_to(skill_dir)).replace("\\", "/"),
                    }
                )
        if args.keep_workbook_json:
            legacy_payload = workbook_to_legacy_json(xlsx)
            legacy_file = out_dir / f"{xlsx.stem}.json"
            legacy_file.write_text(
                json.dumps(legacy_payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    if args.row_only:
        for domain, file_name in DOMAIN_OUTPUT_FILES.items():
            out_file = out_dir / file_name
            out_file.write_text(
                json.dumps(grouped_rows[domain], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        if unmatched_files:
            manifest.append({"unmatched_files": unmatched_files})

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Converted {len(workbook_paths)} xlsx files -> {out_dir}")
    if args.row_only:
        for domain, file_name in DOMAIN_OUTPUT_FILES.items():
            print(f"- {file_name}: {len(grouped_rows[domain])} rows")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
