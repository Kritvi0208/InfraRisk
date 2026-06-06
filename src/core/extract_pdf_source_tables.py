"""
Extract source catalog tables from the InfraRisk AI PDF.

Outputs:
- data/extracted/pdf_source_catalog/infrastructure_engineering_sources.csv
- data/extracted/pdf_source_catalog/macro_financial_sources.csv
- data/extracted/pdf_source_catalog/source_catalog.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

import pdfplumber


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "483555C_Data_Scientist_InfraRisk_AI.docx.pdf"
OUT_DIR = ROOT / "data" / "extracted" / "pdf_source_catalog"


def clean_cell(value: object) -> str:
    text = "" if value is None else str(value)
    return " ".join(text.replace("\n", " ").split())


def normalize_table(table: List[List[object]]) -> List[Dict[str, str]]:
    rows = [[clean_cell(cell) for cell in row] for row in table if row]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return []
    header = rows[0]
    output = []
    for row in rows[1:]:
        padded = row + [""] * max(0, len(header) - len(row))
        output.append({header[i]: padded[i] for i in range(len(header))})
    return output


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(PDF_PATH)

    extracted = []
    with pdfplumber.open(PDF_PATH) as pdf:
        # Screenshot shows viewer page 21 and the following page. Try those first,
        # then keep any table whose header matches the source catalog shape.
        candidate_pages = [20, 21]
        for page_index in candidate_pages:
            if page_index >= len(pdf.pages):
                continue
            page = pdf.pages[page_index]
            for table in page.extract_tables() or []:
                normalized = normalize_table(table)
                if normalized:
                    extracted.append(
                        {
                            "pdf_page_index": page_index,
                            "printed_page_hint": page_index + 1,
                            "headers": list(normalized[0].keys()),
                            "rows": normalized,
                        }
                    )

    infrastructure_rows = []
    macro_rows = []
    for table in extracted:
        headers = [h.lower() for h in table["headers"]]
        if "database" in headers and "entries" in headers:
            infrastructure_rows = table["rows"]
        elif "source" in headers and "coverage" in headers:
            macro_rows = table["rows"]

    if not infrastructure_rows or not macro_rows:
        raise RuntimeError(
            f"Expected two source catalog tables, found infrastructure={len(infrastructure_rows)}, macro={len(macro_rows)}"
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "infrastructure_engineering_sources.csv", infrastructure_rows)
    write_csv(OUT_DIR / "macro_financial_sources.csv", macro_rows)
    (OUT_DIR / "source_catalog.json").write_text(
        json.dumps(
            {
                "source_pdf": str(PDF_PATH.name),
                "extraction_method": "pdfplumber table extraction from PDF pages visible in screenshot",
                "tables": {
                    "infrastructure_engineering_sources": infrastructure_rows,
                    "macro_financial_sources": macro_rows,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Extracted {len(infrastructure_rows)} infrastructure rows")
    print(f"Extracted {len(macro_rows)} macro/financial rows")
    print(f"Output directory: {OUT_DIR}")


if __name__ == "__main__":
    main()

