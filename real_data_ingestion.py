"""
Real-data source registry and ingestion for InfraRiskAI.

This module is intentionally strict: it never creates synthetic fallback rows.
If a source is unavailable, it records that status so the dashboard and models
can distinguish real data from missing or licensed data.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "data" / "source_registry" / "real_data_sources.json"
RAW_ROOT = ROOT / "data" / "raw"
PROCESSED_ROOT = ROOT / "data" / "processed"
REPORT_PATH = PROCESSED_ROOT / "real_data_availability_report.json"


WDI_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "FP.CPI.TOTL.ZG": "inflation",
    "GC.DOD.TOTL.GD.ZS": "govt_debt_gdp",
    "BN.CAB.XOKA.GD.ZS": "current_account_gdp",
    "SP.POP.TOTL": "population",
    "NE.TRD.GNFS.ZS": "trade_gdp",
    "RQ.EST": "regulatory_quality",
    "RL.EST": "rule_of_law",
    "GE.EST": "govt_effectiveness",
    "CC.EST": "control_of_corruption",
}


DEFAULT_COUNTRIES = [
    "IN",
    "CN",
    "BR",
    "ZA",
    "NG",
    "KE",
    "GH",
    "EG",
    "VN",
    "PH",
    "ID",
    "TH",
    "MX",
    "CO",
    "PE",
    "CL",
    "TR",
    "PK",
    "BD",
    "MA",
    "US",
    "GB",
    "DE",
    "FR",
    "JP",
    "KR",
    "SG",
    "AE",
    "SA",
    "QA",
    "OM",
]


@dataclass
class SourceStatus:
    source_id: str
    name: str
    status: str
    local_target: str
    records: int = 0
    message: str = ""


def load_registry() -> Dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _source_by_id(source_id: str) -> Dict[str, Any]:
    for source in load_registry()["sources"]:
        if source["id"] == source_id:
            return source
    raise KeyError(source_id)


def _record_count(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    try:
        if path.suffix.lower() in {".json", ".geojson"}:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                if isinstance(payload.get("features"), list):
                    return len(payload["features"])
                if isinstance(payload.get("elements"), list):
                    return len(payload["elements"])
            return 1
        return len(pd.read_csv(path, low_memory=False))
    except Exception:
        return 0


def _looks_like_old_synthetic_fallback(source_id: str, path: Path) -> bool:
    if source_id != "world_bank_ppi" or not path.exists():
        return False
    try:
        df = pd.read_csv(path, nrows=25, low_memory=False)
    except Exception:
        return False
    generated_ids = (
        "project_id" in df.columns
        and df["project_id"].astype(str).str.startswith("PPI_").all()
    )
    generated_names = (
        "project_name" in df.columns
        and df["project_name"].astype(str).str.contains(" Project ").all()
    )
    return bool(generated_ids and generated_names)


def download_world_bank_wdi(
    countries: Iterable[str] = DEFAULT_COUNTRIES,
    start_year: int = 2010,
    end_year: int = 2024,
) -> SourceStatus:
    source = _source_by_id("world_bank_wdi")
    target = ROOT / source["local_target"]
    target.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for code, field_name in WDI_INDICATORS.items():
        for country in countries:
            url = (
                f"https://api.worldbank.org/v2/country/{country}/indicator/{code}"
                f"?date={start_year}:{end_year}&format=json&per_page=500"
            )
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            payload = response.json()
            if len(payload) < 2 or payload[1] is None:
                continue
            for item in payload[1]:
                if item.get("value") is not None:
                    rows.append(
                        {
                            "country": country,
                            "year": int(item["date"]),
                            "indicator": field_name,
                            "value": float(item["value"]),
                            "source_id": "world_bank_wdi",
                        }
                    )
            time.sleep(0.05)

    if not rows:
        raise RuntimeError("World Bank WDI returned no rows")

    long_df = pd.DataFrame(rows)
    wide_df = long_df.pivot_table(
        index=["country", "year"], columns="indicator", values="value"
    ).reset_index()
    wide_df.to_csv(target, index=False)
    return SourceStatus(
        "world_bank_wdi",
        source["name"],
        "downloaded_real_data",
        str(target),
        len(wide_df),
    )


def download_nbi_state(state_code: str = "AL", year_suffix: str = "23") -> SourceStatus:
    source = _source_by_id("national_bridge_inventory")
    target = ROOT / source["local_target"]
    target.parent.mkdir(parents=True, exist_ok=True)

    state_code = state_code.upper()
    url = f"https://www.fhwa.dot.gov/bridge/nbi/2023/delimited/{state_code}{year_suffix}.txt"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    raw_path = target.parent / f"{state_code}{year_suffix}.txt"
    raw_path.write_bytes(response.content)
    df = pd.read_csv(raw_path, delimiter=",", low_memory=False, encoding="latin-1")
    df["source_id"] = "national_bridge_inventory"
    df.to_csv(target, index=False)
    return SourceStatus(
        "national_bridge_inventory",
        source["name"],
        "downloaded_real_data",
        str(target),
        len(df),
    )


def download_osm_roads_bbox(
    south: float,
    west: float,
    north: float,
    east: float,
    output_name: str = "osm_roads.geojson",
) -> SourceStatus:
    source = _source_by_id("openstreetmap")
    target = ROOT / source["local_target"]
    if output_name:
        target = target.with_name(output_name)
    target.parent.mkdir(parents=True, exist_ok=True)

    query = f"""
    [out:json][timeout:25];
    (
      way["highway"]({south},{west},{north},{east});
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.post(
        "https://overpass-api.de/api/interpreter", data={"data": query}, timeout=60
    )
    response.raise_for_status()
    payload = response.json()
    target.write_text(json.dumps(payload), encoding="utf-8")
    return SourceStatus(
        "openstreetmap",
        source["name"],
        "downloaded_real_data",
        str(target),
        len(payload.get("elements", [])),
    )


def register_user_supplied_file(source_id: str, input_path: str) -> SourceStatus:
    source = _source_by_id(source_id)
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(src)
    target = ROOT / source["local_target"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(src.read_bytes())
    return SourceStatus(
        source_id,
        source["name"],
        "registered_user_supplied_real_file",
        str(target),
        _record_count(target),
    )


def build_availability_report() -> Dict[str, Any]:
    statuses: List[SourceStatus] = []
    for source in load_registry()["sources"]:
        target = ROOT / source["local_target"]
        records = _record_count(target)
        if _looks_like_old_synthetic_fallback(source["id"], target):
            status = "synthetic_fallback_detected_replace_with_real_source"
            message = "This file matches the old generated PPI fallback; replace it with a real World Bank PPI export."
        elif records > 0:
            status = "available_real_file"
            message = "Local real data file is present."
        elif source.get("env_vars") and not any(
            os.getenv(v) for v in source["env_vars"]
        ):
            status = "requires_credentials_or_user_file"
            message = f"Set one of: {', '.join(source['env_vars'])}, or register a licensed export file."
        else:
            status = "not_downloaded"
            message = (
                "Run the matching public-source downloader or register a source file."
            )
        statuses.append(
            SourceStatus(
                source["id"], source["name"], status, str(target), records, message
            )
        )

    report = {
        "generated_from": str(REGISTRY_PATH),
        "synthetic_fallback_policy": "disabled",
        "sources": [status.__dict__ for status in statuses],
    }
    PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    report = build_availability_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
