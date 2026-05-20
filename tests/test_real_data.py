"""Tests for real data loaders."""

from pathlib import Path

import pandas as pd
import pytest

from src.data.real_data_loader import RealDataLoaders


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


@pytest.fixture()
def sample_data_root(tmp_path, monkeypatch):
    data_root = tmp_path / "data" / "raw"

    _write_csv(
        data_root / "ppi" / "ppi_projects.csv",
        [
            {
                "project_id": "PPI_0001",
                "country": "Morocco",
                "sector": "Railways",
                "capex_usd_million": 9531.8,
                "dscr": 1.74,
            }
        ],
    )
    _write_csv(
        data_root / "worldbank" / "wdi_macro.csv",
        [
            {
                "country": "MA",
                "year": 2024,
                "gdp_growth": 3.1,
                "inflation": 2.4,
            }
        ],
    )
    _write_csv(
        data_root / "worldbank" / "cds_spreads.csv",
        [
            {
                "country": "MA",
                "date": "2024-12-31",
                "cds_5y_bps": 245.0,
            }
        ],
    )
    _write_csv(
        data_root / "nbi" / "nbi_bridges.csv",
        [
            {
                "bridge_id": "B-001",
                "state": "CA",
                "condition_rating": 7,
            }
        ],
    )

    monkeypatch.setattr(RealDataLoaders, "DATA_PATH", data_root)
    return data_root


@pytest.fixture()
def empty_data_root(tmp_path, monkeypatch):
    data_root = tmp_path / "missing"
    monkeypatch.setattr(RealDataLoaders, "DATA_PATH", data_root)
    return data_root


def test_load_ppi_projects(sample_data_root):
    df = RealDataLoaders.load_ppi_projects()
    assert not df.empty
    assert list(df.columns) == ["project_id", "country", "sector", "capex_usd_million", "dscr"]


def test_load_macro_data(sample_data_root):
    df = RealDataLoaders.load_macro_data()
    assert not df.empty
    assert set(["country", "year", "gdp_growth", "inflation"]).issubset(df.columns)


def test_load_cds_spreads(sample_data_root):
    df = RealDataLoaders.load_cds_spreads()
    assert not df.empty
    assert set(["country", "date", "cds_5y_bps"]).issubset(df.columns)


def test_load_nbi_bridges(sample_data_root):
    df = RealDataLoaders.load_nbi_bridges()
    assert not df.empty
    assert set(["bridge_id", "state", "condition_rating"]).issubset(df.columns)


def test_load_all_returns_expected_keys(sample_data_root):
    data = RealDataLoaders.load_all()
    assert set(data.keys()) == {"ppi", "macro", "cds", "nbi"}
    assert all(not frame.empty for frame in data.values())


def test_missing_sources_return_empty_frames(empty_data_root):
    data = RealDataLoaders.load_all()
    assert all(frame.empty for frame in data.values())
