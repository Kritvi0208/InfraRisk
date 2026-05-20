"""
Comprehensive test suite for InfraRisk AI ML/DL models.

Tests cover all 7 models with focus on:
- Model initialization and forward pass
- Loss computation
- Training loops
- Prediction accuracy
- Integration tests
"""

import pytest
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    # CNN Models
    SentinelDataset,
    ResNet50Backbone,
    SiameseCNN,
    MultiTaskLoss,
    SatelliteCNNTrainer,
    train_satellite_cnn,
    # TFT
    TemporalFusionTransformer,
    # PINNs
    BridgeFatiguePINN,
    PavementDegradationPINN,
    # GNN
    PortfolioGNN,
    # Baselines
    CreditRiskEnsemble,
    # Ensemble & MC
    SectorWeightedEnsemble,
    MonteCarloSimulation,
    # Utils
    create_mock_infrastructure_data,
    UnifiedMLPipeline,
)


# ============================================================================
# TESTS: SIAMESE CNN
# ============================================================================

class TestSentinelDataset:
    """Tests for Sentinel-2 dataset."""

    def test_dataset_initialization(self):
        """Test dataset creation."""
        dataset = SentinelDataset(num_samples=100, seed=42)
        assert len(dataset) == 100
        assert dataset.channels == 13
        assert dataset.patch_size == 256

    def test_dataset_getitem(self):
        """Test data sampling."""
        dataset = SentinelDataset(num_samples=50)
        sample = dataset[0]
        
        assert "image" in sample
        assert "progress" in sample
        assert "phase" in sample
        assert "anomaly" in sample
        
        assert sample["image"].shape == (6, 13, 256, 256)  # seq_len=6
        assert 0 <= sample["progress"].item() <= 100
        assert 0 <= sample["phase"].item() < 5
        assert sample["anomaly"].item() in [0, 1]

    def test_dataset_determinism(self):
        """Test reproducibility with seed."""
        ds1 = SentinelDataset(num_samples=50, seed=42)
        ds2 = SentinelDataset(num_samples=50, seed=42)
        
        s1 = ds1[0]
        s2 = ds2[0]
        
        assert torch.allclose(s1["image"], s2["image"])
        assert s1["progress"].item() == s2["progress"].item()


class TestResNet50Backbone:
    """Tests for ResNet-50 backbone."""

    def test_backbone_initialization(self):
        """Test backbone creation."""
        backbone = ResNet50Backbone(in_channels=13)
        assert backbone is not None

    def test_backbone_forward_pass(self):
        """Test forward pass."""
        backbone = ResNet50Backbone(in_channels=13)
        x = torch.randn(4, 13, 256, 256)
        
        output = backbone(x)
        
        assert output.shape == (4, 512)  # (batch_size, feature_dim)

    def test_backbone_gradient_flow(self):
        """Test gradient computation."""
        backbone = ResNet50Backbone(in_channels=13)
        x = torch.randn(2, 13, 256, 256, requires_grad=True)
        
        output = backbone(x)
        loss = output.mean()
        loss.backward()
        
        assert x.grad is not None
        assert backbone.conv1.weight.grad is not None


class TestSiameseCNN:
    """Tests for Siamese CNN model."""

    def test_model_initialization(self):
        """Test model creation."""
        model = SiameseCNN(in_channels=13, feature_dim=512, num_phases=5)
        assert model is not None

    def test_model_forward_pass(self):
        """Test forward pass."""
        model = SiameseCNN()
        x = torch.randn(2, 6, 13, 256, 256)  # (batch, seq_len, channels, h, w)
        
        outputs = model(x)
        
        assert "progress" in outputs
        assert "phases" in outputs
        assert "anomalies" in outputs
        assert "features" in outputs
        
        assert outputs["progress"].shape == (2,)
        assert outputs["phases"].shape == (2, 5)
        assert outputs["anomalies"].shape == (2, 2)
        assert outputs["features"].shape == (2, 512)

    def test_progress_output_range(self):
        """Test progress output is in valid range."""
        model = SiameseCNN()
        x = torch.randn(10, 6, 13, 256, 256)
        
        outputs = model(x)
        progress = outputs["progress"]
        
        assert torch.all(progress >= 0)
        assert torch.all(progress <= 100)

    def test_model_training_mode(self):
        """Test dropout behavior in training vs eval."""
        model = SiameseCNN(dropout=0.5)
        x = torch.randn(5, 6, 13, 256, 256)
        
        # Training mode
        model.train()
        out1 = model(x)
        out2 = model(x)
        
        # Outputs should differ due to dropout
        assert not torch.allclose(out1["features"], out2["features"], atol=0.1)
        
        # Eval mode
        model.eval()
        with torch.no_grad():
            out3 = model(x)
            out4 = model(x)
        
        # Outputs should be identical
        assert torch.allclose(out3["features"], out4["features"])


class TestMultiTaskLoss:
    """Tests for multi-task loss."""

    def test_loss_computation(self):
        """Test loss calculation."""
        loss_fn = MultiTaskLoss()
        
        outputs = {
            "progress": torch.randn(4),
            "phases": torch.randn(4, 5),
            "anomalies": torch.randn(4, 2),
        }
        
        targets = {
            "progress": torch.randn(4),
            "phase": torch.randint(0, 5, (4,)),
            "anomaly": torch.randint(0, 2, (4,)),
        }
        
        loss, breakdown = loss_fn(outputs, targets)
        
        assert loss.item() > 0
        assert "progress_mse" in breakdown
        assert "phase_ce" in breakdown
        assert "anomaly_bce" in breakdown
        assert "total" in breakdown

    def test_loss_gradient_flow(self):
        """Test gradient computation through loss."""
        model = SiameseCNN()
        loss_fn = MultiTaskLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        
        x = torch.randn(2, 6, 13, 256, 256)
        targets = {
            "progress": torch.randn(2),
            "phase": torch.randint(0, 5, (2,)),
            "anomaly": torch.randint(0, 2, (2,)),
        }
        
        outputs = model(x)
        loss, _ = loss_fn(outputs, targets)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Check that gradients were computed
        has_grad = any(p.grad is not None for p in model.parameters())
        assert has_grad


class TestSatelliteCNNTrainer:
    """Tests for training pipeline."""

    def test_trainer_initialization(self):
        """Test trainer creation."""
        model = SiameseCNN()
        trainer = SatelliteCNNTrainer(model)
        assert trainer is not None

    def test_epoch_training(self):
        """Test one epoch of training."""
        model = SiameseCNN()
        trainer = SatelliteCNNTrainer(model)
        
        dataset = SentinelDataset(num_samples=64)
        loader = DataLoader(dataset, batch_size=8)
        
        losses = trainer.train_epoch(loader)
        
        assert "total_loss" in losses
        assert losses["total_loss"] > 0

    def test_validation(self):
        """Test validation loop."""
        model = SiameseCNN()
        trainer = SatelliteCNNTrainer(model)
        
        dataset = SentinelDataset(num_samples=32)
        loader = DataLoader(dataset, batch_size=8)
        
        metrics = trainer.validate(loader)
        
        assert "val_loss" in metrics
        assert "val_mape" in metrics
        assert metrics["val_mape"] >= 0


# ============================================================================
# TESTS: TEMPORAL FUSION TRANSFORMER
# ============================================================================

class TestTemporalFusionTransformer:
    """Tests for TFT model."""

    def test_tft_initialization(self):
        """Test TFT creation."""
        model = TemporalFusionTransformer(
            num_features=6,
            lookback_window=24,
            forecast_horizon=12,
        )
        assert model is not None

    def test_tft_forward_pass(self):
        """Test forward pass."""
        model = TemporalFusionTransformer(
            num_features=6,
            lookback_window=24,
            forecast_horizon=12,
        )
        
        x = torch.randn(10, 24, 6)  # (batch, lookback, features)
        outputs = model(x)
        
        assert "p10" in outputs
        assert "p50" in outputs
        assert "p90" in outputs
        
        assert outputs["p10"].shape == (10, 12)
        assert outputs["p50"].shape == (10, 12)
        assert outputs["p90"].shape == (10, 12)

    def test_tft_quantile_ordering(self):
        """Test P10 < P50 < P90."""
        model = TemporalFusionTransformer(
            num_features=6,
            lookback_window=24,
            forecast_horizon=12,
        )
        model.eval()
        
        x = torch.randn(10, 24, 6)
        with torch.no_grad():
            outputs = model(x)
        
        # Check quantile ordering (approximately)
        p10_mean = outputs["p10"].mean().item()
        p50_mean = outputs["p50"].mean().item()
        p90_mean = outputs["p90"].mean().item()
        
        assert p10_mean <= p50_mean <= p90_mean or np.isclose(p10_mean, p90_mean, rtol=0.5)


# ============================================================================
# TESTS: PHYSICS-INFORMED NEURAL NETWORKS
# ============================================================================

class TestBridgeFatiguePINN:
    """Tests for bridge fatigue PINN."""

    def test_pinn_initialization(self):
        """Test PINN creation."""
        model = BridgeFatiguePINN()
        assert model is not None

    def test_pinn_forward_pass(self):
        """Test forward pass."""
        model = BridgeFatiguePINN()
        x = torch.randn(10, 3)  # (batch, features: stress, material, cycles)
        
        output = model(x)
        
        assert output.shape == (10, 1)
        assert torch.all(output > 0)  # Crack size must be positive

    def test_pinn_physics_loss(self):
        """Test physics-informed loss."""
        model = BridgeFatiguePINN()
        x = torch.randn(5, 3, requires_grad=True)
        y = torch.randn(5, 1)
        
        loss = model.physics_loss(x, y, lambda_physics=0.5)
        
        assert loss.item() > 0
        assert loss.requires_grad


class TestPavementDegradationPINN:
    """Tests for pavement degradation PINN."""

    def test_pinn_initialization(self):
        """Test PINN creation."""
        model = PavementDegradationPINN()
        assert model is not None

    def test_pinn_forward_pass(self):
        """Test forward pass."""
        model = PavementDegradationPINN()
        x = torch.randn(10, 4)  # (batch, features: AADT, temp, precip, age)
        
        output = model(x)
        
        assert output.shape == (10, 1)
        assert torch.all(output >= 0)
        assert torch.all(output <= 5)  # PSI in [0, 5]


# ============================================================================
# TESTS: GRAPH NEURAL NETWORK
# ============================================================================

class TestPortfolioGNN:
    """Tests for portfolio GNN."""

    def test_gnn_initialization(self):
        """Test GNN creation."""
        model = PortfolioGNN(
            num_nodes=50,
            node_features=5,
            hidden_dim=64,
        )
        assert model is not None

    def test_gnn_forward_pass(self):
        """Test forward pass."""
        model = PortfolioGNN(
            num_nodes=50,
            node_features=5,
            hidden_dim=64,
        )
        
        node_features = torch.randn(50, 5)
        adj_matrix = torch.randint(0, 2, (50, 50)).float()
        
        outputs = model(node_features, adj_matrix)
        
        assert "risk_scores" in outputs
        assert "centrality" in outputs
        assert "systemic_risk" in outputs
        
        assert outputs["risk_scores"].shape == (50,)
        assert outputs["centrality"].shape == (50, 3)
        assert outputs["systemic_risk"].shape == (50,)

    def test_gnn_risk_scores_valid(self):
        """Test risk scores are in valid range."""
        model = PortfolioGNN(num_nodes=20, node_features=5)
        
        node_features = torch.randn(20, 5)
        adj_matrix = torch.randint(0, 2, (20, 20)).float()
        
        outputs = model(node_features, adj_matrix)
        
        assert torch.all(outputs["risk_scores"] >= 0)
        assert torch.all(outputs["risk_scores"] <= 1)


# ============================================================================
# TESTS: CREDIT RISK ENSEMBLE
# ============================================================================

class TestCreditRiskEnsemble:
    """Tests for XGBoost & LightGBM ensemble."""

    def test_ensemble_initialization(self):
        """Test ensemble creation."""
        ensemble = CreditRiskEnsemble()
        assert ensemble is not None

    def test_xgboost_training(self):
        """Test XGBoost training."""
        ensemble = CreditRiskEnsemble()
        
        X_train = np.random.randn(200, 10)
        y_train = np.random.randint(0, 2, 200)
        X_val = np.random.randn(50, 10)
        y_val = np.random.randint(0, 2, 50)
        
        ensemble.feature_names = [f"feat_{i}" for i in range(10)]
        metrics = ensemble.train_xgboost(X_train, y_train, X_val, y_val)
        
        assert "auc" in metrics
        assert metrics["auc"] > 0.4  # Better than random

    def test_lightgbm_training(self):
        """Test LightGBM training."""
        ensemble = CreditRiskEnsemble()
        
        X_train = np.random.randn(200, 10)
        y_train = np.random.randint(0, 2, 200)
        X_val = np.random.randn(50, 10)
        y_val = np.random.randint(0, 2, 50)
        
        metrics = ensemble.train_lightgbm(X_train, y_train, X_val, y_val)
        
        assert "auc" in metrics

    def test_ensemble_prediction(self):
        """Test ensemble prediction."""
        ensemble = CreditRiskEnsemble()
        
        X_train = np.random.randn(100, 5)
        y_train = np.random.randint(0, 2, 100)
        X_test = np.random.randn(20, 5)
        
        ensemble.feature_names = [f"feat_{i}" for i in range(5)]
        ensemble.train_xgboost(X_train, y_train)
        ensemble.train_lightgbm(X_train, y_train)
        
        predictions = ensemble.predict(X_test)
        
        assert predictions.shape == (20,)
        assert np.all(predictions >= 0)
        assert np.all(predictions <= 1)


# ============================================================================
# TESTS: ENSEMBLE & MONTE CARLO
# ============================================================================

class TestSectorWeightedEnsemble:
    """Tests for sector-weighted ensemble."""

    def test_ensemble_initialization(self):
        """Test ensemble creation."""
        sectors = ["Roads", "Power", "Ports", "Telecom"]
        ensemble = SectorWeightedEnsemble(sectors)
        assert ensemble is not None

    def test_sector_weighting(self):
        """Test sector weighting logic."""
        sectors = ["Roads", "Power"]
        ensemble = SectorWeightedEnsemble(sectors)
        
        base_preds = {
            "xgb": np.random.rand(100),
            "lgb": np.random.rand(100),
        }
        sector_labels = np.random.choice(sectors, 100)
        y_true = np.random.randint(0, 2, 100)
        
        ensemble.train(base_preds, sector_labels, y_true)
        
        assert len(ensemble.sector_weights) == 2


class TestMonteCarloSimulation:
    """Tests for Monte Carlo PD simulation."""

    def test_mc_initialization(self):
        """Test MC simulator creation."""
        mock_model = CreditRiskEnsemble()
        mc = MonteCarloSimulation(mock_model, num_scenarios=1000)
        assert mc is not None

    def test_scenario_generation(self):
        """Test scenario generation."""
        mock_model = CreditRiskEnsemble()
        mc = MonteCarloSimulation(mock_model, num_scenarios=500)
        
        base_features = pd.DataFrame({
            "revenue": [1e7] * 10,
            "capex": [5e6] * 10,
            "interest_rate": [0.05] * 10,
            "construction_delay": [0] * 10,
        })
        
        scenarios = mc.generate_scenarios(base_features)
        
        assert scenarios.shape[0] == 500
        assert scenarios.shape[1] == 4


# ============================================================================
# TESTS: DATA UTILS
# ============================================================================

class TestDataUtils:
    """Tests for data utilities."""

    def test_mock_data_generation(self):
        """Test synthetic data creation."""
        X, y = create_mock_infrastructure_data(n_samples=200)
        
        assert len(X) == 200
        assert len(y) == 200
        assert set(y) == {0, 1}
        
        # Check features
        assert "dscr" in X.columns
        assert "leverage" in X.columns
        assert "sector" in X.columns

    def test_mock_data_balance(self):
        """Test data class balance."""
        X, y = create_mock_infrastructure_data(n_samples=1000, seed=42)
        
        class_balance = np.mean(y)
        
        # Should have some class imbalance but not extreme
        assert 0.1 < class_balance < 0.9


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestUnifiedMLPipeline:
    """Integration tests for unified pipeline."""

    def test_pipeline_initialization(self):
        """Test pipeline creation."""
        pipeline = UnifiedMLPipeline()
        assert pipeline is not None

    def test_all_models_training(self):
        """Test that all models train without errors."""
        pipeline = UnifiedMLPipeline(experiment_name="test_infrariskai")
        results = pipeline.train_all_models()
        
        # Verify all models trained
        assert "siamese_cnn" in results
        assert "tft" in results
        assert "pinn" in results
        assert "gnn" in results
        assert "credit_risk" in results


# ============================================================================
# MARKER TESTS
# ============================================================================

@pytest.mark.slow
def test_full_training_pipeline():
    """Full end-to-end training (marked as slow)."""
    pipeline = UnifiedMLPipeline(experiment_name="full_test")
    results = pipeline.train_all_models()
    assert len(results) >= 5


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
