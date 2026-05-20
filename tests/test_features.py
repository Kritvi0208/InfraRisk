"""Feature engineering tests"""
import pytest
from src.features.engineering import FeatureEngineer

def test_financial_features():
    project = {
        'cfads': 30,
        'debt_service': 25,
        'debt': 300,
        'capex': 500,
        'cash_npv': 150,
        'tenor_years': 15
    }
    features = FeatureEngineer.compute_financial_features(project)
    assert features['dscr'] > 1.0
    assert 0 <= features['leverage'] <= 1.0
    assert features['debt_tenor'] == 15

def test_macro_features():
    country = {
        'gdp_growth': 5.0,
        'inflation': 3.5,
        'external_debt': 40.0,
        'gov_debt': 60.0,
        'cds': 150
    }
    features = FeatureEngineer.compute_macro_features(country)
    assert features['gdp_growth'] == 5.0
    assert features['cds_spread'] == 150
