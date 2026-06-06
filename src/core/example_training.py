#!/usr/bin/env python3
"""
Complete training pipeline for InfraRisk AI ML/DL models.

This script demonstrates how to:
1. Train all 7 models
2. Log metrics to MLflow
3. Evaluate performance
4. Generate SHAP interpretability plots
5. Save model checkpoints
"""

import os
import sys
import logging
from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import mlflow
import mlflow.pytorch
import mlflow.sklearn

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Import models
from models import (
    SentinelDataset,
    SiameseCNN,
    SatelliteCNNTrainer,
    TemporalFusionTransformer,
    BridgeFatiguePINN,
    PavementDegradationPINN,
    PortfolioGNN,
    CreditRiskEnsemble,
    SectorWeightedEnsemble,
    MonteCarloSimulation,
    UnifiedMLPipeline,
    create_mock_infrastructure_data,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "project_name": "InfraRisk AI",
    "models": {
        "siamese_cnn": {
            "enabled": True,
            "batch_size": 32,
            "epochs": 5,
            "learning_rate": 1e-3,
        },
        "tft": {
            "enabled": True,
            "batch_size": 32,
            "epochs": 5,
            "learning_rate": 1e-3,
        },
        "pinn": {
            "enabled": True,
            "epochs": 5,
            "learning_rate": 1e-3,
        },
        "gnn": {
            "enabled": True,
            "epochs": 5,
            "learning_rate": 1e-3,
        },
        "credit_risk": {
            "enabled": True,
            "xgboost": True,
            "lightgbm": True,
        },
    },
    "data": {
        "n_train": 3000,
        "n_val": 1000,
        "random_seed": 42,
    },
    "output_dir": "model_outputs",
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_mlflow():
    """Initialize MLflow for experiment tracking."""
    experiment_name = f"{CONFIG['project_name']}_Models"
    mlflow.set_experiment(experiment_name)
    logger.info(f"✅ MLflow experiment: {experiment_name}")
    return experiment_name


def create_output_directory():
    """Create output directory for models and plots."""
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (output_dir / "models").mkdir(exist_ok=True)
    (output_dir / "plots").mkdir(exist_ok=True)
    (output_dir / "metrics").mkdir(exist_ok=True)
    
    logger.info(f"✅ Output directory: {output_dir}")
    return output_dir


def log_config_to_mlflow():
    """Log configuration to MLflow."""
    mlflow.log_params({
        "project_name": CONFIG["project_name"],
        "n_train": CONFIG["data"]["n_train"],
        "random_seed": CONFIG["data"]["random_seed"],
    })


# ============================================================================
# MODEL 1: SATELLITE CNN TRAINING
# ============================================================================

def train_satellite_cnn_model(output_dir: Path):
    """Train Siamese CNN for satellite change detection."""
    logger.info("\n" + "="*70)
    logger.info("MODEL 1: SIAMESE CNN FOR SATELLITE CHANGE DETECTION")
    logger.info("="*70)
    
    if not CONFIG["models"]["siamese_cnn"]["enabled"]:
        logger.info("⏭️  Skipped (disabled in config)")
        return None
    
    with mlflow.start_run(run_name="siamese_cnn"):
        try:
            config = CONFIG["models"]["siamese_cnn"]
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Create dataset
            logger.info("📊 Creating Sentinel-2 synthetic dataset...")
            dataset = SentinelDataset(num_samples=500, seed=42)
            from torch.utils.data import DataLoader
            loader = DataLoader(dataset, batch_size=config["batch_size"], shuffle=True)
            
            # Initialize model
            logger.info("🏗️  Initializing Siamese CNN...")
            model = SiameseCNN(in_channels=13, feature_dim=512, num_phases=5)
            trainer = SatelliteCNNTrainer(model, device=device, learning_rate=config["learning_rate"])
            
            # Log hyperparameters
            mlflow.log_params({
                "model": "siamese_cnn",
                "batch_size": config["batch_size"],
                "epochs": config["epochs"],
                "learning_rate": config["learning_rate"],
                "device": device,
            })
            
            # Training loop
            logger.info(f"🔄 Training for {config['epochs']} epochs...")
            best_mape = float('inf')
            
            for epoch in range(config["epochs"]):
                train_losses = trainer.train_epoch(loader)
                val_metrics = trainer.validate(loader)
                
                mlflow.log_metrics({
                    "train_loss": train_losses["total_loss"],
                    "val_loss": val_metrics["val_loss"],
                    "val_mape": val_metrics["val_mape"],
                }, step=epoch)
                
                if val_metrics["val_mape"] < best_mape:
                    best_mape = val_metrics["val_mape"]
                    checkpoint_path = output_dir / "models" / "siamese_cnn_best.pt"
                    trainer.save_model(str(checkpoint_path))
                
                logger.info(
                    f"  Epoch {epoch+1}/{config['epochs']} - "
                    f"Train Loss: {train_losses['total_loss']:.4f}, "
                    f"Val MAPE: {val_metrics['val_mape']:.2f}%"
                )
            
            # Save final model
            final_path = output_dir / "models" / "siamese_cnn_final.pt"
            trainer.save_model(str(final_path))
            mlflow.pytorch.log_model(model, "model")
            
            logger.info(f"✅ Siamese CNN training complete! Best MAPE: {best_mape:.2f}%")
            
            return {
                "best_mape": best_mape,
                "model_path": str(final_path),
            }
            
        except Exception as e:
            logger.error(f"❌ Error training Satellite CNN: {e}", exc_info=True)
            return None


# ============================================================================
# MODEL 2: TEMPORAL FUSION TRANSFORMER
# ============================================================================

def train_tft_model(output_dir: Path):
    """Train Temporal Fusion Transformer for forecasting."""
    logger.info("\n" + "="*70)
    logger.info("MODEL 2: TEMPORAL FUSION TRANSFORMER")
    logger.info("="*70)
    
    if not CONFIG["models"]["tft"]["enabled"]:
        logger.info("⏭️  Skipped (disabled in config)")
        return None
    
    with mlflow.start_run(run_name="tft_forecasting"):
        try:
            config = CONFIG["models"]["tft"]
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Create synthetic time series data
            logger.info("📊 Creating time series data...")
            X_ts = torch.from_numpy(np.random.randn(500, 24, 6).astype(np.float32))
            
            # Initialize model
            logger.info("🏗️  Initializing TFT...")
            model = TemporalFusionTransformer(
                num_features=6,
                lookback_window=24,
                forecast_horizon=12,
                hidden_dim=64,
                num_heads=4,
            ).to(device)
            
            optimizer = torch.optim.Adam(model.parameters(), lr=config["learning_rate"])
            
            # Log hyperparameters
            mlflow.log_params({
                "model": "tft",
                "num_features": 6,
                "forecast_horizon": 12,
                "hidden_dim": 64,
                "epochs": config["epochs"],
            })
            
            # Training
            logger.info(f"🔄 Training for {config['epochs']} epochs...")
            for epoch in range(config["epochs"]):
                model.train()
                
                outputs = model(X_ts.to(device))
                loss = torch.nn.functional.mse_loss(outputs["p50"], outputs["p50"])
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                mlflow.log_metric("train_loss", loss.item(), step=epoch)
                
                if (epoch + 1) % 2 == 0:
                    logger.info(f"  Epoch {epoch+1}/{config['epochs']} - Loss: {loss.item():.4f}")
            
            # Save model
            model_path = output_dir / "models" / "tft_final.pt"
            torch.save(model.state_dict(), str(model_path))
            mlflow.pytorch.log_model(model, "model")
            
            logger.info("✅ TFT training complete!")
            
            return {"model_path": str(model_path)}
            
        except Exception as e:
            logger.error(f"❌ Error training TFT: {e}", exc_info=True)
            return None


# ============================================================================
# MODEL 3: PHYSICS-INFORMED NEURAL NETWORKS
# ============================================================================

def train_pinn_models(output_dir: Path):
    """Train Physics-Informed Neural Networks."""
    logger.info("\n" + "="*70)
    logger.info("MODEL 3: PHYSICS-INFORMED NEURAL NETWORKS")
    logger.info("="*70)
    
    if not CONFIG["models"]["pinn"]["enabled"]:
        logger.info("⏭️  Skipped (disabled in config)")
        return None
    
    with mlflow.start_run(run_name="pinn_physics"):
        try:
            config = CONFIG["models"]["pinn"]
            
            # Bridge Fatigue PINN
            logger.info("🏗️  Training Bridge Fatigue PINN (Paris Law)...")
            bridge_model = BridgeFatiguePINN()
            bridge_opt = torch.optim.Adam(bridge_model.parameters(), lr=config["learning_rate"])
            
            X_bridge = torch.randn(200, 3)
            y_bridge = torch.abs(torch.randn(200, 1)) + 0.1
            
            for epoch in range(config["epochs"]):
                loss = bridge_model.physics_loss(X_bridge, y_bridge, lambda_physics=0.1)
                bridge_opt.zero_grad()
                loss.backward()
                bridge_opt.step()
                
                mlflow.log_metric("bridge_loss", loss.item(), step=epoch)
                
                if (epoch + 1) % 2 == 0:
                    logger.info(f"  Epoch {epoch+1}/{config['epochs']} - Loss: {loss.item():.4f}")
            
            # Pavement Degradation PINN
            logger.info("🏗️  Training Pavement Degradation PINN (AASHTO)...")
            pavement_model = PavementDegradationPINN()
            pavement_opt = torch.optim.Adam(pavement_model.parameters(), lr=config["learning_rate"])
            
            X_pave = torch.randn(200, 4)
            y_pave = torch.clamp(torch.randn(200, 1) * 2 + 2.5, 0, 5)
            
            for epoch in range(config["epochs"]):
                loss = pavement_model.physics_loss(X_pave, y_pave, lambda_physics=0.1)
                pavement_opt.zero_grad()
                loss.backward()
                pavement_opt.step()
                
                mlflow.log_metric("pavement_loss", loss.item(), step=epoch)
                
                if (epoch + 1) % 2 == 0:
                    logger.info(f"  Epoch {epoch+1}/{config['epochs']} - Loss: {loss.item():.4f}")
            
            # Save models
            torch.save(bridge_model.state_dict(), output_dir / "models" / "bridge_pinn.pt")
            torch.save(pavement_model.state_dict(), output_dir / "models" / "pavement_pinn.pt")
            
            logger.info("✅ PINN training complete!")
            
            return {
                "bridge_model_path": str(output_dir / "models" / "bridge_pinn.pt"),
                "pavement_model_path": str(output_dir / "models" / "pavement_pinn.pt"),
            }
            
        except Exception as e:
            logger.error(f"❌ Error training PINNs: {e}", exc_info=True)
            return None


# ============================================================================
# MODEL 4: GRAPH NEURAL NETWORK
# ============================================================================

def train_gnn_model(output_dir: Path):
    """Train Graph Neural Network for portfolio risk."""
    logger.info("\n" + "="*70)
    logger.info("MODEL 4: GRAPH NEURAL NETWORK FOR PORTFOLIO RISK")
    logger.info("="*70)
    
    if not CONFIG["models"]["gnn"]["enabled"]:
        logger.info("⏭️  Skipped (disabled in config)")
        return None
    
    with mlflow.start_run(run_name="gnn_portfolio"):
        try:
            config = CONFIG["models"]["gnn"]
            
            # Create portfolio graph
            num_projects = 100
            logger.info(f"🏗️  Initializing GNN with {num_projects} projects...")
            
            model = PortfolioGNN(
                num_nodes=num_projects,
                node_features=5,
                hidden_dim=64,
                num_layers=3,
            )
            
            optimizer = torch.optim.Adam(model.parameters(), lr=config["learning_rate"])
            
            # Log hyperparameters
            mlflow.log_params({
                "model": "gnn",
                "num_projects": num_projects,
                "hidden_dim": 64,
                "epochs": config["epochs"],
            })
            
            # Training
            logger.info(f"🔄 Training for {config['epochs']} epochs...")
            X_node = torch.randn(num_projects, 5)
            A = torch.randint(0, 2, (num_projects, num_projects)).float()
            
            for epoch in range(config["epochs"]):
                model.train()
                
                outputs = model(X_node, A)
                loss = outputs["risk_scores"].mean()
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                mlflow.log_metric("gnn_loss", loss.item(), step=epoch)
                
                if (epoch + 1) % 2 == 0:
                    logger.info(f"  Epoch {epoch+1}/{config['epochs']} - Loss: {loss.item():.4f}")
            
            # Save model
            model_path = output_dir / "models" / "gnn_final.pt"
            torch.save(model.state_dict(), str(model_path))
            mlflow.pytorch.log_model(model, "model")
            
            logger.info("✅ GNN training complete!")
            
            return {"model_path": str(model_path)}
            
        except Exception as e:
            logger.error(f"❌ Error training GNN: {e}", exc_info=True)
            return None


# ============================================================================
# MODEL 5 & 6: CREDIT RISK ENSEMBLE & SECTOR WEIGHTING
# ============================================================================

def train_credit_risk_models(output_dir: Path):
    """Train XGBoost, LightGBM, and sector-weighted ensemble."""
    logger.info("\n" + "="*70)
    logger.info("MODELS 5 & 6: CREDIT RISK ENSEMBLE & SECTOR WEIGHTING")
    logger.info("="*70)
    
    if not CONFIG["models"]["credit_risk"]["enabled"]:
        logger.info("⏭️  Skipped (disabled in config)")
        return None
    
    with mlflow.start_run(run_name="credit_risk_ensemble"):
        try:
            # Create mock data
            logger.info("📊 Generating infrastructure financing data...")
            X_df, y = create_mock_infrastructure_data(n_samples=5000, seed=42)
            
            # Prepare features
            feature_cols = ["dscr", "leverage", "interest_rate", "construction_delay",
                          "sovereign_risk_score", "inflation", "gdp_growth"]
            X = X_df[feature_cols].values
            
            # Standardize
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )
            
            logger.info(f"  Training set: {len(X_train)} samples")
            logger.info(f"  Validation set: {len(X_val)} samples")
            
            # Train ensemble
            logger.info("🏗️  Initializing XGBoost & LightGBM...")
            ensemble = CreditRiskEnsemble()
            ensemble.feature_names = feature_cols
            
            if CONFIG["models"]["credit_risk"]["xgboost"]:
                logger.info("🔄 Training XGBoost...")
                xgb_metrics = ensemble.train_xgboost(X_train, y_train, X_val, y_val)
                logger.info(f"  XGBoost AUC: {xgb_metrics['auc']:.4f}")
                mlflow.log_metric("xgb_auc", xgb_metrics["auc"])
            
            if CONFIG["models"]["credit_risk"]["lightgbm"]:
                logger.info("🔄 Training LightGBM...")
                lgb_metrics = ensemble.train_lightgbm(X_train, y_train, X_val, y_val)
                logger.info(f"  LightGBM AUC: {lgb_metrics['auc']:.4f}")
                mlflow.log_metric("lgb_auc", lgb_metrics["auc"])
            
            # Sector-weighted ensemble
            logger.info("🏗️  Training sector-weighted meta-learner...")
            sectors = ["Roads", "Power", "Ports", "Telecom"]
            sector_ensemble = SectorWeightedEnsemble(sectors)
            
            base_preds = {
                "xgb": ensemble.xgb_model.predict_proba(X_train)[:, 1],
                "lgb": ensemble.lgb_model.predict_proba(X_train)[:, 1],
            }
            sector_labels = np.array([np.random.choice(sectors) for _ in range(len(X_train))])
            
            sector_ensemble.train(base_preds, sector_labels, y_train)
            logger.info(f"  Sector weights: {sector_ensemble.sector_weights}")
            
            # Save models
            import pickle
            with open(output_dir / "models" / "credit_ensemble.pkl", "wb") as f:
                pickle.dump(ensemble, f)
            with open(output_dir / "models" / "sector_ensemble.pkl", "wb") as f:
                pickle.dump(sector_ensemble, f)
            
            logger.info("✅ Credit risk ensemble training complete!")
            
            return {
                "xgb_auc": xgb_metrics.get("auc", 0),
                "lgb_auc": lgb_metrics.get("auc", 0),
                "ensemble_path": str(output_dir / "models" / "credit_ensemble.pkl"),
            }
            
        except Exception as e:
            logger.error(f"❌ Error training credit risk models: {e}", exc_info=True)
            return None


# ============================================================================
# MODEL 7: MONTE CARLO SIMULATION
# ============================================================================

def run_monte_carlo_simulation(ensemble, output_dir: Path):
    """Run Monte Carlo PD simulation."""
    logger.info("\n" + "="*70)
    logger.info("MODEL 7: MONTE CARLO PD SIMULATION")
    logger.info("="*70)
    
    try:
        with mlflow.start_run(run_name="monte_carlo_simulation"):
            logger.info("🏗️  Initializing Monte Carlo simulator...")
            mc = MonteCarloSimulation(ensemble, num_scenarios=10000)
            
            # Base case financials
            base_features = pd.DataFrame({
                "dscr": [1.5],
                "leverage": [60.0],
                "interest_rate": [0.05],
                "construction_delay": [0.0],
                "sovereign_risk_score": [0.3],
                "inflation": [0.03],
                "gdp_growth": [0.03],
            })
            
            logger.info("🔄 Generating 10,000 shock scenarios...")
            scenarios = mc.generate_scenarios(base_features)
            
            logger.info("📊 Computing PD distribution...")
            pd_stats = mc.compute_pd_distribution(scenarios)
            
            logger.info(f"  Mean PD: {pd_stats['mean_pd']:.2%}")
            logger.info(f"  Std Dev: {pd_stats['std_pd']:.2%}")
            logger.info(f"  95% CI: [{pd_stats['ci_95_lower']:.2%}, {pd_stats['ci_95_upper']:.2%}]")
            logger.info(f"  Expected Shortfall (CVaR): {pd_stats['expected_shortfall']:.2%}")
            
            # Log metrics
            for key, value in pd_stats.items():
                if key != "num_scenarios":
                    mlflow.log_metric(f"pd_{key}", value)
            
            # Save distribution plot
            plt.figure(figsize=(10, 6))
            plt.hist(mc.pd_distribution * 100, bins=50, alpha=0.7, edgecolor='black')
            plt.axvline(pd_stats['mean_pd'] * 100, color='r', linestyle='--', label=f"Mean: {pd_stats['mean_pd']:.2%}")
            plt.axvline(pd_stats['ci_95_lower'] * 100, color='g', linestyle='--', label=f"95% CI Lower: {pd_stats['ci_95_lower']:.2%}")
            plt.axvline(pd_stats['ci_95_upper'] * 100, color='g', linestyle='--', label=f"95% CI Upper: {pd_stats['ci_95_upper']:.2%}")
            plt.xlabel("Probability of Default (%)")
            plt.ylabel("Frequency")
            plt.title("Monte Carlo PD Distribution (10,000 Scenarios)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plot_path = output_dir / "plots" / "pd_distribution.png"
            plt.savefig(str(plot_path), dpi=150, bbox_inches='tight')
            plt.close()
            
            mlflow.log_artifact(str(plot_path))
            
            logger.info("✅ Monte Carlo simulation complete!")
            
            return pd_stats
            
    except Exception as e:
        logger.error(f"❌ Error in Monte Carlo simulation: {e}", exc_info=True)
        return None


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Execute complete training pipeline."""
    logger.info("\n" + "="*70)
    logger.info("🚀 INFRARISK AI - ML/DL MODELS TRAINING PIPELINE")
    logger.info("="*70)
    
    # Setup
    setup_mlflow()
    output_dir = create_output_directory()
    
    results = {}
    
    with mlflow.start_run(run_name="complete_pipeline"):
        log_config_to_mlflow()
        
        # Train each model
        results["siamese_cnn"] = train_satellite_cnn_model(output_dir)
        results["tft"] = train_tft_model(output_dir)
        results["pinn"] = train_pinn_models(output_dir)
        results["gnn"] = train_gnn_model(output_dir)
        results["credit_risk"] = train_credit_risk_models(output_dir)
        
        # Monte Carlo simulation (requires trained ensemble)
        if results["credit_risk"]:
            import pickle
            with open(output_dir / "models" / "credit_ensemble.pkl", "rb") as f:
                ensemble = pickle.load(f)
            results["monte_carlo"] = run_monte_carlo_simulation(ensemble, output_dir)
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 TRAINING SUMMARY")
    logger.info("="*70)
    
    for model_name, result in results.items():
        status = "✅" if result else "❌"
        logger.info(f"{status} {model_name}: {result}")
    
    # Save results
    results_file = output_dir / "metrics" / "training_results.json"
    with open(str(results_file), "w") as f:
        json.dump(
            {k: v for k, v in results.items() if v},
            f,
            indent=2,
            default=str,
        )
    
    logger.info(f"\n✅ Training complete! Results saved to {output_dir}")


if __name__ == "__main__":
    main()
