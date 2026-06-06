#!/usr/bin/env python3
"""
Phase 3 Integration Test & Validation
Quick smoke tests for all 6 models
"""

import sys
import os

def test_monte_carlo():
    """Test Monte Carlo PD Engine"""
    try:
        from src.models.monte_carlo_pd import MonteCarloPDEngine
        engine = MonteCarloPDEngine(n_scenarios=1000, n_assets=10)
        results = engine.run_simulation(verbose=False)
        
        assert 'confidence_intervals' in results
        assert 'p50' in results['confidence_intervals']
        assert 0 < results['confidence_intervals']['p50'] < 100
        print("✓ Monte Carlo PD Engine: PASS")
        return True
    except Exception as e:
        print(f"✗ Monte Carlo PD Engine: FAIL - {e}")
        return False

def test_shap():
    """Test SHAP Interpretability"""
    try:
        from src.core.shap_interpreter import SHAPInterpreter
        import numpy as np
        
        interpreter = SHAPInterpreter(feature_names=['f1', 'f2', 'f3', 'f4', 'f5'])
        X = np.random.randn(100, 5)
        shap_vals = interpreter.compute_shap_values(X)
        
        assert shap_vals.shape == X.shape
        importance = interpreter.global_feature_importance()
        assert 'features' in importance
        assert len(importance['features']) > 0
        print("✓ SHAP Interpretability: PASS")
        return True
    except Exception as e:
        print(f"✗ SHAP Interpretability: FAIL - {e}")
        return False

def test_attention():
    """Test TFT Attention Extraction"""
    try:
        from src.core.attention_extractor import AttentionExtractor
        
        extractor = AttentionExtractor(n_time_steps=52, n_features=10, n_heads=4)
        temporal = extractor.extract_temporal_attention(sequence_length=52, forecast_horizon=12)
        
        assert temporal.shape == (12, 52, 4)
        
        heatmap = extractor.create_attention_heatmap(forecast_step=0, head_idx=0)
        assert 'attention_weights' in heatmap
        assert len(heatmap['attention_weights']) == 52
        print("✓ TFT Attention Extraction: PASS")
        return True
    except Exception as e:
        print(f"✗ TFT Attention Extraction: FAIL - {e}")
        return False

def test_centrality():
    """Test GNN Centrality Analyzer"""
    try:
        from src.core.centrality_analyzer import CentralityAnalyzer
        
        analyzer = CentralityAnalyzer(n_nodes=15)
        degree = analyzer.compute_degree_centrality()
        
        assert len(degree) == 15
        assert 0 <= degree.min() <= 1
        assert 0 <= degree.max() <= 1
        
        systemic = analyzer.identify_systemic_projects(top_k=5)
        assert 'systemic_projects' in systemic
        assert len(systemic['systemic_projects']) <= 5
        print("✓ GNN Centrality Analysis: PASS")
        return True
    except Exception as e:
        print(f"✗ GNN Centrality Analysis: FAIL - {e}")
        return False

def test_backtesting():
    """Test Backtesting Framework"""
    try:
        from src.core.backtesting import BacktestingFramework
        import numpy as np
        
        framework = BacktestingFramework()
        
        # Test with synthetic data
        y_true = np.random.binomial(1, 0.02, 1000)
        y_pred = np.random.beta(3, 50, 1000)
        
        auc = framework.compute_auc_roc(y_true, y_pred)
        assert 0 <= auc <= 1
        
        gini = framework.compute_gini(y_true, y_pred)
        assert -1 <= gini <= 1
        
        ks, _ = framework.compute_ks_statistic(y_true, y_pred)
        assert 0 <= ks <= 1
        
        print("✓ Backtesting Framework: PASS")
        return True
    except Exception as e:
        print(f"✗ Backtesting Framework: FAIL - {e}")
        return False

def test_registry():
    """Test Model Registry"""
    try:
        from src.models.model_registry import ModelRegistry, ModelVersion, ModelMetrics
        
        registry = ModelRegistry()
        
        # Register a model
        v1 = registry.register_model(
            'test_model',
            metrics={'auc': 0.85, 'gini': 0.70},
            description='Test model'
        )
        
        assert v1 is not None
        
        # Promote version
        success = registry.promote_version(v1, 'staging')
        assert success
        
        # Get version
        version = registry.get_version(v1)
        assert version is not None
        assert version.stage == 'staging'
        
        # Get summary
        summary = registry.get_registry_summary()
        assert summary['total_models'] >= 1
        
        print("✓ Model Registry: PASS")
        return True
    except Exception as e:
        print(f"✗ Model Registry: FAIL - {e}")
        return False

def main():
    print("=== PHASE 3 INTEGRATION TEST ===\n")
    
    tests = [
        test_monte_carlo,
        test_shap,
        test_attention,
        test_centrality,
        test_backtesting,
        test_registry,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test execution error: {e}")
            results.append(False)
    
    # Summary
    print(f"\n=== RESULTS ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL PHASE 3 TESTS PASSED")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
