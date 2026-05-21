"""
Smart public-data ingestion for InfraRiskAI.

Downloads only free/public sources from the PDF source list and avoids
synthetic fallback generation. Paid sources remain as registry placeholders.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd
import requests

from real_data_ingestion import (
    DEFAULT_COUNTRIES,
    WDI_INDICATORS,
    build_availability_report,
)

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

PPI_DTA_URL = (
    "https://www.worldbank.org/content/dam/PPI/documents/2024-PPI-Full-DTA.dta"
)


def download_file(url: str, target: Path, timeout: int = 120) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        tmp = target.with_suffix(target.suffix + ".tmp")
        with tmp.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
        tmp.replace(target)
    return target


def ingest_world_bank_ppi() -> Dict:
    dta_path = RAW / "ppi" / "ppi_projects_2024_real.dta"
    csv_path = RAW / "ppi" / "ppi_projects.csv"
    if not dta_path.exists() or dta_path.stat().st_size < 1_000_000:
        download_file(PPI_DTA_URL, dta_path)

    df = pd.read_stata(dta_path, convert_categoricals=False)
    df["source_id"] = "world_bank_ppi"
    df["source_url"] = PPI_DTA_URL
    df.to_csv(csv_path, index=False)
    return {
        "source_id": "world_bank_ppi",
        "status": "downloaded_real_data",
        "records": int(len(df)),
        "raw_file": str(dta_path),
        "csv_file": str(csv_path),
        "columns": list(df.columns),
    }


def ingest_world_bank_wdi(
    countries: Iterable[str] = DEFAULT_COUNTRIES,
    start_year: int = 2010,
    end_year: int = 2024,
) -> Dict:
    rows: List[Dict] = []
    for code, field in WDI_INDICATORS.items():
        for country in countries:
            url = (
                f"https://api.worldbank.org/v2/country/{country}/indicator/{code}"
                f"?date={start_year}:{end_year}&format=json&per_page=500"
            )
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            payload = response.json()
            if len(payload) > 1 and payload[1]:
                for item in payload[1]:
                    if item.get("value") is not None:
                        rows.append(
                            {
                                "country": country,
                                "year": int(item["date"]),
                                "indicator": field,
                                "value": float(item["value"]),
                                "source_id": "world_bank_wdi",
                            }
                        )
            time.sleep(0.03)

    long_df = pd.DataFrame(rows)
    wide_df = long_df.pivot_table(
        index=["country", "year"], columns="indicator", values="value"
    ).reset_index()
    target = RAW / "worldbank" / "wdi_macro.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    wide_df.to_csv(target, index=False)
    return {
        "source_id": "world_bank_wdi",
        "status": "downloaded_real_data",
        "records": int(len(wide_df)),
        "csv_file": str(target),
    }


def ingest_nbi_alabama_2024() -> Dict:
    # Small but real sample from FHWA; enough for project demos without huge storage use.
    url = "https://www.fhwa.dot.gov/bridge/nbi/2024/delimited/AL24.txt"
    raw_path = RAW / "nbi" / "AL24.txt"
    csv_path = RAW / "nbi" / "nbi_bridges.csv"
    download_file(url, raw_path)
    df = pd.read_csv(raw_path, delimiter=",", low_memory=False, encoding="latin-1")
    df["source_id"] = "national_bridge_inventory"
    df["source_url"] = url
    df.to_csv(csv_path, index=False)
    return {
        "source_id": "national_bridge_inventory",
        "status": "downloaded_real_data",
        "records": int(len(df)),
        "csv_file": str(csv_path),
    }


def ingest_yahoo_finance_proxy() -> Dict:
    # Yahoo chart endpoint is lightweight and public. These ETFs are market
    # proxies for equities, rates duration, USD, gold, and oil.
    symbols = ["SPY", "TLT", "UUP", "GLD", "USO"]
    frames = []
    now = int(datetime.now(timezone.utc).timestamp())
    period1 = now - (365 * 5 * 24 * 60 * 60)
    headers = {"User-Agent": "InfraRiskAI/1.0 public academic data ingestion"}
    for symbol in symbols:
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            f"?period1={period1}&period2={now}&interval=1d&events=history"
        )
        payload = requests.get(url, headers=headers, timeout=30).json()
        result = payload["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        adjclose = (
            result["indicators"]
            .get("adjclose", [{}])[0]
            .get("adjclose", [None] * len(timestamps))
        )
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(timestamps, unit="s").date.astype(str),
                "open": quote.get("open"),
                "high": quote.get("high"),
                "low": quote.get("low"),
                "close": quote.get("close"),
                "volume": quote.get("volume"),
                "adjclose": adjclose,
                "symbol": symbol,
                "source_id": "yahoo_finance",
                "source_url": url,
            }
        ).dropna(subset=["close"])
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    target = RAW / "market" / "yahoo_finance_prices.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(target, index=False)
    return {
        "source_id": "yahoo_finance",
        "status": "downloaded_public_market_proxy",
        "records": int(len(out)),
        "csv_file": str(target),
    }


def ingest_osm_small_bbox() -> Dict:
    # Tiny New Delhi bbox for network graph demos, not a global OSM download.
    south, west, north, east = 28.58, 77.16, 28.64, 77.24
    query = f"""
    [out:json][timeout:25];
    (
      way["highway"]({south},{west},{north},{east});
    );
    out body;
    >;
    out skel qt;
    """
    headers = {"User-Agent": "InfraRiskAI/1.0 small bbox academic request"}
    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data=query.encode("utf-8"),
        headers=headers,
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    target = RAW / "osm" / "osm_roads.geojson"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload), encoding="utf-8")
    return {
        "source_id": "openstreetmap",
        "status": "downloaded_real_small_bbox",
        "records": len(payload.get("elements", [])),
        "json_file": str(target),
    }


def main() -> None:
    results = []
    for task in [
        ingest_world_bank_ppi,
        ingest_world_bank_wdi,
        ingest_nbi_alabama_2024,
        ingest_yahoo_finance_proxy,
        ingest_osm_small_bbox,
    ]:
        name = task.__name__
        try:
            print(f"Running {name}...")
            result = task()
            print(json.dumps(result, indent=2))
            results.append(result)
        except Exception as exc:
            result = {"task": name, "status": "failed", "error": str(exc)}
            print(json.dumps(result, indent=2))
            results.append(result)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "public_real_ingestion_report.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    availability = build_availability_report()
    print("Availability report updated.")
    print(json.dumps(availability, indent=2))


if __name__ == "__main__":
    main()
