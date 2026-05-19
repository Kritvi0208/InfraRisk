"""Tests for data loaders."""

import pytest
import pandas as pd
from src.data.loaders import (
    WorldBankLoader, InterestRatesLoader, MacroDataLoader,
    NBILoader, SatelliteImageryHandler, CommodityPricesLoader
)

class TestWorldBankLoader:
    def test_load(self):
        loader = WorldBankLoader()
        df = loader.load()
        assert len(df) >= 10000
        assert 'project_id' in df.columns
        assert 'capex_usd' in df.columns
    
    def test_sectors(self):
        loader = WorldBankLoader()
        df = loader.load()
        assert df['sector'].nunique() >= 5

class TestInterestRates:
    def test_load(self):
        loader = InterestRatesLoader()
        df = loader.load()
        assert len(df) >= 2600
        assert 'cds_spread_bps' in df.columns

class TestMacroData:
    def test_load(self):
        loader = MacroDataLoader()
        df = loader.load()
        assert len(df) >= 220
        assert 'gdp_growth' in df.columns

class TestNBILoader:
    def test_load(self):
        loader = NBILoader()
        df = loader.load()
        assert len(df) >= 620000
        assert 'condition_rating' in df.columns

class TestSatellite:
    def test_load(self):
        handler = SatelliteImageryHandler()
        imagery = handler.load(sites=50)
        assert len(imagery) == 50

class TestCommodities:
    def test_load(self):
        loader = CommodityPricesLoader()
        df = loader.load()
        assert len(df) >= 2600
        assert 'oil_usd_bbl' in df.columns
