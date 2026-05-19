"""Test real data loaders."""

from src.data.real_data_loader import RealDataLoaders
import pytest

class TestRealDataLoaders:
    
    def test_ppi_projects(self):
        df = RealDataLoaders.load_ppi_projects()
        if not df.empty:
            assert 'project_id' in df.columns
            assert 'capex_usd_million' in df.columns
            assert 'dscr' in df.columns
    
    def test_macro_data(self):
        df = RealDataLoaders.load_macro_data()
        if not df.empty:
            assert 'country' in df.columns
            assert 'gdp_growth' in df.columns
    
    def test_nbi_bridges(self):
        df = RealDataLoaders.load_nbi_bridges()
        if not df.empty:
            assert len(df) > 10000  # Should have large dataset
    
    def test_cds_spreads(self):
        df = RealDataLoaders.load_cds_spreads()
        if not df.empty:
            print(f"CDS data loaded: {len(df)} records")
