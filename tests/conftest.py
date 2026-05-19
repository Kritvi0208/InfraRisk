"""Data fixtures for testing."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@pytest.fixture
def sample_wbppi_data():
    """World Bank PPI sample (100 projects)."""
    return pd.DataFrame({
        'project_id': range(100),
        'country': np.random.choice(['IN', 'BR', 'NG', 'KE'], 100),
        'sector': np.random.choice(['Transport', 'Energy', 'Water'], 100),
        'capex_usd': np.random.uniform(50e6, 500e6, 100),
        'status': np.random.choice(['Development', 'Construction', 'Operational'], 100),
        'inception_date': [datetime(2015, 1, 1) + timedelta(days=i*10) for i in range(100)],
    })

@pytest.fixture
def sample_macro_data():
    """Macro data (50 countries)."""
    return pd.DataFrame({
        'country': np.random.choice(['IN', 'BR', 'NG', 'KE', 'US', 'GB'], 50),
        'gdp_growth': np.random.uniform(0, 10, 50),
        'inflation': np.random.uniform(0, 15, 50),
        'debt_to_gdp': np.random.uniform(20, 120, 50),
    })

@pytest.fixture
def sample_rates_data():
    """Interest rates (500 days)."""
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    return pd.DataFrame({
        'date': dates,
        'sofr': np.random.uniform(0.5, 3, 500),
        'cds_bps': np.random.uniform(50, 400, 500),
    })

@pytest.fixture
def sample_nbi_data():
    """NBI bridges (1000 records)."""
    return pd.DataFrame({
        'bridge_id': range(1000),
        'state': np.random.choice(['CA', 'TX', 'NY'], 1000),
        'year_built': np.random.randint(1950, 2020, 1000),
        'condition_rating': np.random.randint(1, 10, 1000),
    })

@pytest.fixture
def sample_portfolio():
    """Sample project portfolio."""
    return [
        {'id': 'p1', 'sector': 'Transport', 'capex': 100e6, 'dscr': 1.5, 'pd': 0.02},
        {'id': 'p2', 'sector': 'Energy', 'capex': 200e6, 'dscr': 1.2, 'pd': 0.05},
        {'id': 'p3', 'sector': 'Water', 'capex': 50e6, 'dscr': 1.8, 'pd': 0.01},
    ]
