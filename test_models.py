"""Test suite for core models."""

import numpy as np
import torch
from models import (
    SentinelDataset,
    SiameseCNN,
    TemporalFusionTransformer,
    BridgeFatiguePINN,
    PavementDegradationPINN,
    PortfolioGNN,
    CreditRiskEnsemble,
    create_mock_infrastructure_data,
)


def test_sentinel_dataset():
    """Test Sentinel-2 dataset."""
    dataset = SentinelDataset(num_samples=100)
    assert len(dataset) == 100
    sample = dataset[0]
    assert sample["image"].shape == (6, 13, 256, 256)


def test_siamese_cnn():
    """Test Siamese CNN."""
    model = SiameseCNN()
    x = torch.randn(2, 6, 13, 256, 256)
    outputs = model(x)
    assert outputs["progress"].shape == (2,)
    assert outputs["phases"].shape == (2, 5)
    assert outputs["anomalies"].shape == (2, 2)


def test_temporal_fusion_transformer():
    """Test TFT."""
    model = TemporalFusionTransformer(
        num_features=6,
        lookback_window=24,
        forecast_horizon=12,
    )
    x = torch.randn(10, 24, 6)
    outputs = model(x)
    assert outputs["p50"].shape == (10, 12)


def test_bridge_fatigue_pinn():
    """Test bridge fatigue PINN."""
    model = BridgeFatiguePINN()
    x = torch.randn(10, 3)
    output = model(x)
    assert output.shape == (10, 1)
    assert torch.all(output > 0)


def test_pavement_degradation_pinn():
    """Test pavement PINN."""
    model = PavementDegradationPINN()
    x = torch.randn(10, 4)
    output = model(x)
    assert output.shape == (10, 1)
    assert torch.all(output >= 0) and torch.all(output <= 5)


def test_portfolio_gnn():
    """Test GNN."""
    model = PortfolioGNN(num_nodes=50, node_features=5)
    node_features = torch.randn(50, 5)
    adj_matrix = torch.randint(0, 2, (50, 50)).float()
    outputs = model(node_features, adj_matrix)
    assert outputs["risk_scores"].shape == (50,)


def test_credit_risk_ensemble():
    """Test ensemble."""
    ensemble = CreditRiskEnsemble()
    X_train = np.random.randn(200, 10)
    y_train = np.random.randint(0, 2, 200)
    ensemble.feature_names = [f"feat_{i}" for i in range(10)]
    metrics = ensemble.train_xgboost(X_train, y_train)
    assert "auc" in metrics


def test_mock_data_generation():
    """Test data generation."""
    X, y = create_mock_infrastructure_data(n_samples=200)
    assert len(X) == 200
    assert len(y) == 200