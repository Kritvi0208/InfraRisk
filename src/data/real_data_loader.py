"""Real data loaders using actual CSV files."""

import os
from pathlib import Path

import pandas as pd


class RealDataLoaders:
    """Load actual data from data/raw/."""

    DATA_PATH = Path(os.getenv("INFRARISK_DATA_PATH", "./data/raw")).resolve()

    @classmethod
    def _read_csv(cls, relative_path: str, **kwargs) -> pd.DataFrame:
        path = cls.DATA_PATH / relative_path
        if path.exists():
            return pd.read_csv(path, **kwargs)
        return pd.DataFrame()

    @classmethod
    def load_ppi_projects(cls) -> pd.DataFrame:
        """Load World Bank PPI projects (~10K records)."""
        df = cls._read_csv("ppi/ppi_projects.csv")
        if not df.empty:
            print(f"Loaded {len(df)} PPI projects")
        return df

    @classmethod
    def load_macro_data(cls) -> pd.DataFrame:
        """Load WDI macro indicators (220+ countries)."""
        df = cls._read_csv("worldbank/wdi_macro.csv")
        if not df.empty and "country" in df.columns:
            print(f"Loaded macro data for {df['country'].nunique()} countries")
        return df

    @classmethod
    def load_cds_spreads(cls) -> pd.DataFrame:
        """Load CDS spreads (50+ sovereigns, 10+ years)."""
        df = cls._read_csv("worldbank/cds_spreads.csv")
        if not df.empty:
            print(f"Loaded CDS data: {len(df)} records")
        return df

    @classmethod
    def load_nbi_bridges(cls) -> pd.DataFrame:
        """Load National Bridge Inventory (620K+ records)."""
        df = cls._read_csv("nbi/nbi_bridges.csv", low_memory=False)
        if not df.empty:
            print(f"Loaded {len(df)} NBI bridges")
        return df

    @classmethod
    def load_all(cls) -> dict:
        """Load all real data sources."""
        return {
            "ppi": cls.load_ppi_projects(),
            "macro": cls.load_macro_data(),
            "cds": cls.load_cds_spreads(),
            "nbi": cls.load_nbi_bridges(),
        }


if __name__ == "__main__":
    data = RealDataLoaders.load_all()
    for name, df in data.items():
        print(f"{name}: {len(df)} rows, {len(df.columns)} columns")
