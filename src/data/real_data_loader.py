"""Real data loaders using actual CSV files."""

import pandas as pd
import os
from typing import Optional

class RealDataLoaders:
    """Load actual data from data/raw/"""
    
    DATA_PATH = "./data/raw"
    
    @classmethod
    def load_ppi_projects(cls) -> pd.DataFrame:
        """Load World Bank PPI projects (~10K records)."""
        path = os.path.join(cls.DATA_PATH, "ppi/ppi_projects.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"Loaded {len(df)} PPI projects")
            return df
        return pd.DataFrame()
    
    @classmethod
    def load_macro_data(cls) -> pd.DataFrame:
        """Load WDI macro indicators (220+ countries)."""
        path = os.path.join(cls.DATA_PATH, "worldbank/wdi_macro.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"Loaded macro data for {df['country'].nunique()} countries")
            return df
        return pd.DataFrame()
    
    @classmethod
    def load_cds_spreads(cls) -> pd.DataFrame:
        """Load CDS spreads (50+ sovereigns, 10+ years)."""
        path = os.path.join(cls.DATA_PATH, "worldbank/cds_spreads.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"Loaded CDS data: {len(df)} records")
            return df
        return pd.DataFrame()
    
    @classmethod
    def load_nbi_bridges(cls) -> pd.DataFrame:
        """Load National Bridge Inventory (620K+ records)."""
        path = os.path.join(cls.DATA_PATH, "nbi/nbi_bridges.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, low_memory=False)
            print(f"Loaded {len(df)} NBI bridges")
            return df
        return pd.DataFrame()
    
    @classmethod
    def load_all(cls) -> dict:
        """Load all real data sources."""
        return {
            'ppi': cls.load_ppi_projects(),
            'macro': cls.load_macro_data(),
            'cds': cls.load_cds_spreads(),
            'nbi': cls.load_nbi_bridges(),
        }

# Usage example
if __name__ == "__main__":
    data = RealDataLoaders.load_all()
    for name, df in data.items():
        print(f"{name}: {len(df)} rows, {len(df.columns)} columns")
