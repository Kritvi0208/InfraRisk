"""
Phase 2 Multi-Modal Feature Engineering Test Suite

Tests for all feature modules created in Phase 2.
"""

import numpy as np
import pandas as pd
import pytest

from climate_rul_module import ClimateAdjustedRUL, batch_calculate_ca_rul
from contagion_index_module import PortfolioContagionIndex, create_contagion_index
from feast_integration_module import (
    FeastFeatureStore,
    FeatureDataType,
    FeatureDefinition,
)
from revenue_features_module import MacroeconomicFeatures, RevenueFeatures


class TestClimateAdjustedRUL:
    """Test CA-RUL calculations"""

    def test_ca_rul_initialization(self):
        """Test CA-RUL calculator initialization"""
        ca_rul = ClimateAdjustedRUL(baseline_rul=30, infrastructure_type="road")
        assert ca_rul.baseline_rul == 30
        assert ca_rul.infrastructure_type == "road"

    def test_ca_rul_calculation(self):
        """Test CA-RUL calculation"""
        ca_rul = ClimateAdjustedRUL(baseline_rul=30)
        result = ca_rul.calculate_ca_rul(
            temp_increase=2.5, precip_change=-15.0, scenario="rcp85"
        )
        assert "ca_rul" in result
        assert result["ca_rul"] >= 0
        assert "degradation_factor" in result

    def test_degradation_curve(self):
        """Test degradation curve generation"""
        ca_rul = ClimateAdjustedRUL(baseline_rul=30)
        curve = ca_rul.generate_degradation_curve(years_ahead=10)
        assert len(curve) >= 1
        assert "ca_rul" in curve.columns
        assert "degradation_factor" in curve.columns

    def test_scenario_comparison(self):
        """Test scenario comparison"""
        ca_rul = ClimateAdjustedRUL(baseline_rul=30)
        comparison = ca_rul.compare_scenarios()
        assert len(comparison) == 3  # baseline, rcp45, rcp85
        assert all(comparison["scenario"].isin(["baseline", "rcp45", "rcp85"]))

    def test_batch_calculation(self):
        """Test batch CA-RUL calculation"""
        assets = [
            {"id": "asset_1", "baseline_rul": 30, "type": "road", "age": 5},
            {"id": "asset_2", "baseline_rul": 40, "type": "bridge", "age": 3},
        ]
        results = batch_calculate_ca_rul(assets)
        assert len(results) == 2
        assert all(results["asset_id"].isin(["asset_1", "asset_2"]))


class TestContagionIndex:
    """Test portfolio contagion analysis"""

    def test_initialization(self):
        """Test contagion index initialization"""
        contagion = create_contagion_index(num_projects=20)
        assert contagion.projects == 20
        assert len(contagion.project_nodes) == 20

    def test_calculate_contagion(self):
        """Test contagion score calculation"""
        contagion = create_contagion_index(num_projects=10)
        contagion_df = contagion.calculate_contagion_index()
        assert len(contagion_df) == 10
        assert "contagion_score" in contagion_df.columns
        assert "eigenvector_centrality" in contagion_df.columns

    def test_identify_systemic_risks(self):
        """Test systemic risk identification"""
        contagion = create_contagion_index(num_projects=20)
        systemic = contagion.identify_systemic_risks(threshold=0.60)
        assert isinstance(systemic, dict)

    def test_shock_propagation(self):
        """Test shock propagation analysis"""
        contagion = create_contagion_index(num_projects=15)
        impacts = contagion.shock_propagation_analysis("proj_000", shock_magnitude=0.5)
        assert len(impacts) == 15
        assert "shock_impact" in impacts.columns


class TestFeastFeatureStore:
    """Test Feast feature store"""

    def test_initialization(self):
        """Test feature store initialization"""
        store = FeastFeatureStore()
        assert len(store.feature_registry) >= 6  # Standard features registered
        assert "climate_adjusted_rul" in store.feature_registry

    def test_register_feature(self):
        """Test feature registration"""
        store = FeastFeatureStore()
        feat_def = FeatureDefinition(
            name="test_feature",
            description="Test feature",
            data_type=FeatureDataType.FLOAT32,
        )
        result = store.register_feature(feat_def)
        assert result is True
        assert "test_feature" in store.feature_registry

    def test_store_and_retrieve_features(self):
        """Test feature storage and retrieval"""
        store = FeastFeatureStore()
        df = pd.DataFrame(
            {
                "project_id": ["proj_001", "proj_002"],
                "climate_adjusted_rul": [25.5, 28.3],
            }
        )
        result = store.store_features(df, "climate_adjusted_rul")
        assert result is True

        retrieved = store.get_features("climate_adjusted_rul")
        assert len(retrieved) >= 1

    def test_list_features(self):
        """Test listing features"""
        store = FeastFeatureStore()
        all_features = store.list_features()
        assert len(all_features) >= 1

        climate_features = store.list_features(tags=["climate"])
        assert len(climate_features) >= 1

    def test_feature_validation(self):
        """Test feature validation"""
        store = FeastFeatureStore()
        df = pd.DataFrame({"project_id": ["proj_001"], "sovereign_risk_score": [0.65]})
        store.store_features(df, "sovereign_risk_score")
        validation = store.validate_features("sovereign_risk_score")
        assert "rows" in validation
        assert validation["rows"] >= 1


class TestRevenueFeatures:
    """Test revenue features"""

    def test_initialization(self):
        """Test revenue features initialization"""
        revenue = RevenueFeatures()
        assert len(revenue.demand_curves) == 4

    def test_toll_rate_features(self):
        """Test toll rate feature calculation"""
        revenue = RevenueFeatures()
        features = revenue.calculate_toll_rate_features(
            vot_savings=45.0, distance=25.0, sector="road"
        )
        assert "toll_rate_per_km" in features
        assert "toll_feasibility_score" in features
        assert features["toll_rate_per_km"] > 0

    def test_competing_route_ratio(self):
        """Test competing route calculation"""
        revenue = RevenueFeatures()
        ratio = revenue.calculate_competing_route_ratio(
            alternative_distance=30.0,
            alternative_time=1.5,
            project_distance=25.0,
            project_time=1.0,
            toll_rate=2.5,
        )
        assert "cost_difference_pct" in ratio
        assert "market_penetration_potential" in ratio

    def test_revenue_demand_curve(self):
        """Test demand curve generation"""
        revenue = RevenueFeatures()
        curve = revenue.calculate_revenue_demand_curve("road", toll_rate=2.5)
        assert len(curve) >= 30
        assert "annual_revenue" in curve.columns

    def test_sector_metrics(self):
        """Test sector-specific metrics"""
        revenue = RevenueFeatures()

        road_metrics = revenue.calculate_sector_metrics("road", 50000)
        assert "daily_traffic_count" in road_metrics

        power_metrics = revenue.calculate_sector_metrics("power", 700)
        assert "average_mw" in power_metrics

        port_metrics = revenue.calculate_sector_metrics("port", 8000)
        assert "daily_teu_average" in port_metrics

    def test_mock_sector_data(self):
        """Test mock data generation"""
        revenue = RevenueFeatures()
        mock_data = revenue.generate_mock_sector_data("road", num_projects=10)
        assert len(mock_data) == 10
        assert all(mock_data["sector"] == "road")


class TestMacroeconomicFeatures:
    """Test macroeconomic features"""

    def test_initialization(self):
        """Test macro features initialization"""
        macro = MacroeconomicFeatures()
        assert len(macro.country_indicators) == 4

    def test_sovereign_risk_score(self):
        """Test sovereign risk calculation"""
        macro = MacroeconomicFeatures()
        score = macro.calculate_sovereign_risk_score("Country_A")
        assert "sovereign_risk_composite" in score
        assert "risk_rating" in score
        assert 0 <= score["sovereign_risk_composite"] <= 1.0

    def test_fiscal_stress_index(self):
        """Test fiscal stress calculation"""
        macro = MacroeconomicFeatures()
        stress = macro.calculate_fiscal_stress_index(
            "Country_A", capex_spending=6.0, tax_revenue=20.0
        )
        assert "fiscal_stress_index" in stress
        assert 0 <= stress["fiscal_stress_index"] <= 1.0

    def test_external_vulnerability_index(self):
        """Test external vulnerability calculation"""
        macro = MacroeconomicFeatures()
        vuln = macro.calculate_external_vulnerability_index("Country_A")
        assert "external_vulnerability_index" in vuln
        assert 0 <= vuln["external_vulnerability_index"] <= 1.0

    def test_portfolio_macro_features(self):
        """Test portfolio macro feature generation"""
        macro = MacroeconomicFeatures()
        portfolio = macro.generate_portfolio_macro_features(num_projects=15)
        assert len(portfolio) == 15
        assert "sovereign_risk_composite" in portfolio.columns
        assert "fiscal_stress_index" in portfolio.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
