#!/usr/bin/env python3
"""
Final Phase 3 Setup: Move models to src/models and validate imports
"""

import os
import shutil
import sys


def main():
    base = r"c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"

    # Create directories
    src_dir = os.path.join(base, "src")
    models_dir = os.path.join(src_dir, "models")

    print("Creating directories...")
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    # Model files
    model_files = [
        "p3_siamese_cnn.py",
        "p3_temporal_fusion_transformer.py",
        "p3_pinn_base.py",
        "p3_pinn_fatigue.py",
        "p3_pinn_pavement.py",
        "p3_gnn_portfolio.py",
        "p3_gradient_boosting.py",
        "p3_ensemble_stacking.py",
    ]

    # Move files
    print("\nMoving model files to src/models/...")
    for fname in model_files:
        src = os.path.join(base, fname)
        dst = os.path.join(models_dir, fname)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"  ✓ {fname}")

    # Create src/__init__.py
    with open(os.path.join(src_dir, "__init__.py"), "w") as f:
        f.write("# src package\n")

    # Create models/__init__.py
    with open(os.path.join(models_dir, "__init__.py"), "w") as f:
        f.write('''"""Phase 3 Core ML Models Package"""

from .p3_siamese_cnn import SiameseCNN, SiameseLoss
from .p3_temporal_fusion_transformer import TemporalFusionTransformer
from .p3_pinn_base import PhysicsInformedNN, PhysicsLoss, ConservationLawPINN
from .p3_pinn_fatigue import PINNFatigue, ParisMaterial, FatigueLoss
from .p3_pinn_pavement import PINNPavement, AAshtoPSIModel, PavementLoss
from .p3_gnn_portfolio import GNNPortfolio, RiskPropagationLayer, CentralityMetrics
from .p3_gradient_boosting import XGBLGBEnsemble, BayesianOptimizer, CreditRiskLoss
from .p3_ensemble_stacking import StackingEnsemble, MetaLearner, StackingLoss

__all__ = [
    'SiameseCNN', 'SiameseLoss',
    'TemporalFusionTransformer',
    'PhysicsInformedNN', 'PhysicsLoss', 'ConservationLawPINN',
    'PINNFatigue', 'ParisMaterial', 'FatigueLoss',
    'PINNPavement', 'AAshtoPSIModel', 'PavementLoss',
    'GNNPortfolio', 'RiskPropagationLayer', 'CentralityMetrics',
    'XGBLGBEnsemble', 'BayesianOptimizer', 'CreditRiskLoss',
    'StackingEnsemble', 'MetaLearner', 'StackingLoss',
]
''')

    print("\n✓ Directory structure created")
    print(f"  src/: {src_dir}")
    print(f"  src/models/: {models_dir}")
    print(f"  {len(model_files)} model files organized")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
