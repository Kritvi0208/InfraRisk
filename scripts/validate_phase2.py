#!/usr/bin/env python3
"""
Phase 2 Features Validation Script

Validates that all Phase 2 feature modules are properly implemented
and can be imported and used without errors.
"""

import sys
import traceback

def validate_climate_rul():
    """Validate climate RUL module"""
    try:
        from src.core.climate_rul_module import (
            ClimateAdjustedRUL,
            ClimateScenario,
            DegradationParameters,
            create_climate_adjusted_rul,
            batch_calculate_ca_rul
        )
        
        ca_rul = ClimateAdjustedRUL(baseline_rul=30)
        result = ca_rul.calculate_ca_rul(temp_increase=2.5, scenario="rcp85")
        
        assert "ca_rul" in result
        assert "degradation_factor" in result
        assert result["ca_rul"] >= 0
        
        print("✅ Climate RUL Module - PASS")
        return True
    except Exception as e:
        print(f"❌ Climate RUL Module - FAIL: {e}")
        traceback.print_exc()
        return False


def validate_contagion_index():
    """Validate contagion index module"""
    try:
        from src.core.contagion_index_module import (
            PortfolioContagionIndex,
            ProjectNode,
            create_contagion_index
        )
        
        contagion = create_contagion_index(num_projects=20)
        contagion_df = contagion.calculate_contagion_index()
        
        assert len(contagion_df) == 20
        assert "contagion_score" in contagion_df.columns
        assert all(contagion_df["contagion_score"] >= 0)
        assert all(contagion_df["contagion_score"] <= 1)
        
        print("✅ Contagion Index Module - PASS")
        return True
    except Exception as e:
        print(f"❌ Contagion Index Module - FAIL: {e}")
        traceback.print_exc()
        return False


def validate_feast_store():
    """Validate Feast feature store module"""
    try:
        from src.core.feast_integration_module import (
            FeastFeatureStore,
            FeatureDefinition,
            FeatureDataType,
            create_feast_store
        )
        import pandas as pd
        
        store = create_feast_store()
        assert len(store.feature_registry) >= 6
        
        df = pd.DataFrame({"project_id": ["p1", "p2"], "value": [1.0, 2.0]})
        assert store.store_features(df, "climate_adjusted_rul")
        
        retrieved = store.get_features("climate_adjusted_rul")
        assert len(retrieved) >= 1
        
        print("✅ Feast Integration Module - PASS")
        return True
    except Exception as e:
        print(f"❌ Feast Integration Module - FAIL: {e}")
        traceback.print_exc()
        return False


def validate_revenue_features():
    """Validate revenue and macro features module"""
    try:
        from src.core.revenue_features_module import (
            RevenueFeatures,
            MacroeconomicFeatures,
            InfrastructureSector,
            DemandCurveParameters
        )
        
        revenue = RevenueFeatures()
        toll = revenue.calculate_toll_rate_features(vot_savings=45.0, distance=25.0)
        assert "toll_rate_per_km" in toll
        assert toll["toll_rate_per_km"] > 0
        
        curve = revenue.calculate_revenue_demand_curve("road", toll_rate=2.5)
        assert len(curve) >= 30
        
        macro = MacroeconomicFeatures()
        sovereign = macro.calculate_sovereign_risk_score("Country_A")
        assert "sovereign_risk_composite" in sovereign
        assert 0 <= sovereign["sovereign_risk_composite"] <= 1
        
        fiscal = macro.calculate_fiscal_stress_index("Country_A", 6.0, 20.0)
        assert "fiscal_stress_index" in fiscal
        
        print("✅ Revenue & Macro Features Module - PASS")
        return True
    except Exception as e:
        print(f"❌ Revenue & Macro Features Module - FAIL: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all validations"""
    print("\n" + "="*60)
    print("Phase 2 Feature Modules - Validation Report")
    print("="*60 + "\n")
    
    results = []
    
    results.append(validate_climate_rul())
    results.append(validate_contagion_index())
    results.append(validate_feast_store())
    results.append(validate_revenue_features())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nValidation Results: {passed}/{total} modules passed")
    
    if all(results):
        print("✅ ALL PHASE 2 MODULES VALIDATED SUCCESSFULLY\n")
        return 0
    else:
        print("❌ SOME MODULES FAILED VALIDATION\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
