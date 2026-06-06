"""Run only the lightweight public sources that may fail independently."""

from __future__ import annotations

import json
from pathlib import Path

from src.core.ingest_public_real_sources import ingest_osm_small_bbox, ingest_yahoo_finance_proxy
from src.core.real_data_ingestion import build_availability_report


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "data" / "processed" / "remaining_public_ingestion_report.json"


def main() -> None:
    results = []
    for task in [ingest_yahoo_finance_proxy, ingest_osm_small_bbox]:
        try:
            result = task()
        except Exception as exc:
            result = {"task": task.__name__, "status": "failed", "error": str(exc)}
        print(json.dumps(result, indent=2))
        results.append(result)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    build_availability_report()


if __name__ == "__main__":
    main()

