"""
Comprehensive validation script for all Phase 3 models
Tests architecture, shapes, and forward passes
"""

import torch
import sys
import traceback

def test_siamese_cnn():
    """Test Siamese CNN model."""
    from p3_siamese_cnn import SiameseCNN, SiameseLoss
    
    model = SiameseCNN(backbone_pretrained=False, head_dim=512)
    loss_fn = SiameseLoss(alpha=0.4, beta=0.4, gamma=0.2)
    
    x = torch.randn(4, 3, 224, 224)
    outputs = model(x, return_features=True)
    
    assert outputs['regression'].shape == (4, 1), f"Regression shape mismatch: {outputs['regression'].shape}"
    assert outputs['classification'].shape == (4, 5), f"Classification shape mismatch: {outputs['classification'].shape}"
    assert outputs['anomaly'].shape == (4, 1), f"Anomaly shape mismatch: {outputs['anomaly'].shape}"
    assert outputs['features'].shape == (4, 2048), f"Features shape mismatch: {outputs['features'].shape}"
    
    # Test loss
    targets = {
        'regression': torch.randint(0, 101, (4, 1)).float(),
        'classification': torch.randint(0, 5, (4,)),
        'anomaly': torch.randint(0, 2, (4, 1)).float()
    }
    loss, loss_dict = loss_fn(outputs, targets)
    assert loss.item() > 0, "Loss is zero"
    
    print("✓ SiameseCNN PASSED")


def test_temporal_fusion_transformer():
    """Test Temporal Fusion Transformer."""
    from p3_temporal_fusion_transformer import TemporalFusionTransformer
    
    model = TemporalFusionTransformer(input_dim=20, d_model=256, num_heads=8, num_layers=3, horizons=[3, 6, 12])
    
    x = torch.randn(8, 12, 20)
    output = model(x)
    
    assert output['quantiles'].shape == (8, 3, 3), f"Quantiles shape mismatch: {output['quantiles'].shape}"
    assert output['attention_weights'] is not None, "Attention weights are None"
    assert output['temporal_features'].shape == (8, 12, 256), f"Temporal features shape mismatch"
    
    print("✓ TemporalFusionTransformer PASSED")


def test_pinn_base():
    """Test Physics-Informed NN base."""
    from p3_pinn_base import PhysicsInformedNN, PhysicsLoss
    
    model = PhysicsInformedNN(input_dim=10, output_dim=1, hidden_dims=[128, 128, 64])
    loss_fn = PhysicsLoss(data_weight=1.0, physics_weight=1.0)
    
    x = torch.randn(16, 10, requires_grad=True)
    y_true = torch.randn(16, 1)
    
    output = model(x, compute_physics=True)
    
    assert output['prediction'].shape == (16, 1), f"Prediction shape mismatch: {output['prediction'].shape}"
    assert output['physics_residual'] is not None, "Physics residual is None"
    
    loss, loss_dict = loss_fn(output, y_true, output['physics_residual'])
    assert loss.item() > 0, "Loss is zero"
    
    print("✓ PhysicsInformedNN PASSED")


def test_pinn_fatigue():
    """Test PINN Fatigue model."""
    from p3_pinn_fatigue import PINNFatigue, FatigueLoss
    
    model = PINNFatigue(hidden_dims=[256, 256, 128, 64], num_materials=3)
    loss_fn = FatigueLoss(data_weight=1.0, physics_weight=1.0)
    
    x = torch.tensor([
        [2.0, 300e6, 100e6, 1000, 0.0],
        [1.5, 350e6, 120e6, 1500, 1.0],
        [3.0, 280e6, 90e6, 800, 2.0],
        [2.5, 320e6, 110e6, 1200, 0.0]
    ])
    y_true = torch.tensor([[5.0], [4.2], [6.5], [5.8]])
    
    output = model(x, compute_physics=True)
    assert output['prediction'].shape == (4, 1), f"Prediction shape mismatch: {output['prediction'].shape}"
    assert output['physics_residual'].shape == (4, 1), f"Physics residual shape mismatch"
    
    trajectory = model.batch_process_stress_cycles(x, num_steps=10)
    assert trajectory['trajectory'].shape == (4, 10), f"Trajectory shape mismatch"
    
    safe_lives = model.predict_safe_life(x, a_critical=10.0)
    assert safe_lives.shape == (4,), f"Safe life shape mismatch"
    
    print("✓ PINNFatigue PASSED")


def test_pinn_pavement():
    """Test PINN Pavement model."""
    from p3_pinn_pavement import PINNPavement, PavementLoss
    
    model = PINNPavement(hidden_dims=[256, 256, 128], physics_weight=1.0)
    loss_fn = PavementLoss(data_weight=1.0, physics_weight=0.5)
    
    x = torch.tensor([
        [4.5, 5000, 5.0, 25, 800, 20, 5],
        [4.2, 6000, 4.5, 20, 900, 30, 8],
        [3.8, 7000, 4.0, 30, 700, 15, 10],
        [3.5, 8000, 3.5, 15, 1000, 40, 15]
    ], dtype=torch.float32)
    y_true = torch.tensor([[3.2], [2.8], [2.1], [1.8]], dtype=torch.float32)
    
    output = model(x, compute_physics=True)
    assert output['prediction'].shape == (4, 1), f"Prediction shape mismatch"
    assert torch.all(output['prediction'] >= 1.5) and torch.all(output['prediction'] <= 4.5), "PSI out of range"
    
    trajectory = model.layer_by_layer_prediction(x, num_steps=12)
    assert trajectory['trajectory'].shape == (4, 12), f"Trajectory shape mismatch"
    
    rating, names = model.condition_rating(output['prediction'])
    assert rating.shape == (4, 1), f"Rating shape mismatch"
    
    alert = model.maintenance_threshold_alert(x, threshold=2.5)
    assert alert['needs_maintenance'].shape == (4, 1), f"Maintenance alert shape mismatch"
    
    print("✓ PINNPavement PASSED")


def test_gnn_portfolio():
    """Test GNN Portfolio model."""
    from p3_gnn_portfolio import GNNPortfolio, PortfolioLoss
    
    model = GNNPortfolio(num_features=10, hidden_dim=64, num_layers=3)
    
    num_projects = 20
    num_edges = 30
    node_features = torch.randn(num_projects, 10)
    edge_index = torch.randint(0, num_projects, (2, num_edges))
    
    output = model(node_features, edge_index, compute_centrality=True)
    
    assert output['risk_scores'].shape == (num_projects, 1), f"Risk scores shape mismatch"
    assert 'betweenness' in output['centrality_metrics'], "Betweenness not computed"
    assert 'eigenvector' in output['centrality_metrics'], "Eigenvector not computed"
    assert 'pagerank' in output['centrality_metrics'], "PageRank not computed"
    
    cascade = model.cascade_failure_analysis(node_features, edge_index, failure_node=0)
    assert cascade['original_risk'].shape == (num_projects, 1), f"Cascade original risk shape mismatch"
    
    ranking = model.visualize_importance_ranking(output['centrality_metrics'])
    assert ranking.shape[0] == num_projects, f"Ranking shape mismatch"
    
    print("✓ GNNPortfolio PASSED")


def test_gradient_boosting():
    """Test XGBoost/LightGBM Ensemble."""
    from p3_gradient_boosting import XGBLGBEnsemble, BayesianOptimizer, CreditRiskLoss
    
    model = XGBLGBEnsemble(num_features=50, num_trees=100)
    loss_fn = CreditRiskLoss(pos_weight=10.0)
    
    x_train = torch.randn(100, 50)
    y_train = torch.randint(0, 2, (100, 1)).float()
    
    output = model(x_train)
    assert output['predictions'].shape == (100, 1), f"Predictions shape mismatch"
    assert output['feature_importance'].shape == (50,), f"Feature importance shape mismatch"
    
    threshold, metrics = model.optimize_threshold(output['predictions'], y_train)
    assert isinstance(threshold, float), "Threshold is not float"
    assert 'f1' in metrics, "F1 score not in metrics"
    
    optimizer = BayesianOptimizer()
    def mock_objective(params):
        return torch.rand(1).item()
    opt_result = optimizer.optimize(mock_objective, n_trials=5)
    assert 'best_params' in opt_result, "Best params not in result"
    
    print("✓ XGBLGBEnsemble PASSED")


def test_ensemble_stacking():
    """Test Stacking Ensemble."""
    from p3_ensemble_stacking import StackingEnsemble, StackingLoss
    
    model = StackingEnsemble(num_sectors=3, meta_feature_dim=32)
    loss_fn = StackingLoss()
    
    batch_size = 32
    tft_output = torch.randn(batch_size, 3, 3)
    gnn_output = torch.randn(batch_size, 1)
    pinn_output = torch.randn(batch_size, 1)
    gbt_output = torch.randn(batch_size, 1)
    sector_ids = torch.randint(0, 3, (batch_size,))
    
    output = model(
        tft_output=tft_output,
        gnn_output=gnn_output,
        pinn_output=pinn_output,
        gbt_output=gbt_output,
        sector_ids=sector_ids,
        meta_features=torch.randn(batch_size, 32)
    )
    
    assert output['ensemble_prediction'].shape == (batch_size, 1), f"Ensemble prediction shape mismatch"
    assert output['base_predictions'].shape == (batch_size, 4), f"Base predictions shape mismatch"
    assert output['shap_values'].shape == (batch_size, 4), f"SHAP values shape mismatch"
    
    blended = model.blend_predictions(tft_output, gnn_output, pinn_output, gbt_output, sector_ids)
    assert blended.shape == (batch_size, 1), f"Blended shape mismatch"
    
    importances = model.get_model_importances()
    assert len(importances) == 4, "Model importances count mismatch"
    
    print("✓ StackingEnsemble PASSED")


def main():
    """Run all tests."""
    tests = [
        ("Siamese CNN", test_siamese_cnn),
        ("Temporal Fusion Transformer", test_temporal_fusion_transformer),
        ("PINN Base", test_pinn_base),
        ("PINN Fatigue", test_pinn_fatigue),
        ("PINN Pavement", test_pinn_pavement),
        ("GNN Portfolio", test_gnn_portfolio),
        ("Gradient Boosting", test_gradient_boosting),
        ("Stacking Ensemble", test_ensemble_stacking),
    ]
    
    print("\n" + "="*60)
    print("PHASE 3 MODEL ARCHITECTURE VALIDATION")
    print("="*60 + "\n")
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"✗ {name} FAILED")
            print(f"  Error: {str(e)}")
            traceback.print_exc()
            failed += 1
        print()
    
    print("="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
