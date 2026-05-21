#!/usr/bin/env python3
"""
PHASE 3 FINAL SETUP: Build directory structure and move all models
This script creates src/models directory and places all 8 models there
"""

import os
import shutil
import sys


def setup_phase3():
    """Main setup function."""

    base_dir = r"c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"
    src_dir = os.path.join(base_dir, "src")
    models_dir = os.path.join(src_dir, "models")

    print("\n" + "=" * 70)
    print("PHASE 3: SETTING UP MODEL DIRECTORY STRUCTURE")
    print("=" * 70)

    try:
        # Create directories
        print("\n[1] Creating directory structure...")
        os.makedirs(models_dir, exist_ok=True)
        print(f"  ✓ Created: {models_dir}")

        # Model files to move
        model_files = {
            "p3_siamese_cnn.py": "siamese_cnn.py",
            "p3_temporal_fusion_transformer.py": "temporal_fusion_transformer.py",
            "p3_pinn_base.py": "pinn_base.py",
            "p3_pinn_fatigue.py": "pinn_fatigue.py",
            "p3_pinn_pavement.py": "pinn_pavement.py",
            "p3_gnn_portfolio.py": "gnn_portfolio.py",
            "p3_gradient_boosting.py": "gradient_boosting.py",
            "p3_ensemble_stacking.py": "ensemble_stacking.py",
        }

        # Copy model files (don't move, in case needed)
        print("\n[2] Organizing model files...")
        for src_name, dst_name in model_files.items():
            src_path = os.path.join(base_dir, src_name)
            dst_path = os.path.join(models_dir, dst_name)

            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"  ✓ {src_name} → models/{dst_name}")
            else:
                print(f"  ✗ File not found: {src_name}")
                return False

        # Create __init__.py for src
        print("\n[3] Creating package files...")
        src_init = os.path.join(src_dir, "__init__.py")
        with open(src_init, "w") as f:
            f.write("# src package\n")
        print(f"  ✓ src/__init__.py")

        # Create __init__.py for models
        models_init = os.path.join(models_dir, "__init__.py")
        init_content = '''"""Phase 3 Core ML Models

8 production-ready architectural implementations:
  1. SiameseCNN - Multi-head ResNet-50
  2. TemporalFusionTransformer - Multi-horizon quantile forecasting
  3. PhysicsInformedNN - Base class with physics constraints
  4. PINNFatigue - Paris Law crack growth
  5. PINNPavement - AASHTO degradation
  6. GNNPortfolio - Portfolio risk propagation
  7. XGBLGBEnsemble - Gradient boosting + Bayesian optimization
  8. StackingEnsemble - Meta-learner with sector weighting
"""

from .siamese_cnn import SiameseCNN, SiameseLoss
from .temporal_fusion_transformer import TemporalFusionTransformer
from .pinn_base import PhysicsInformedNN, PhysicsLoss, ConservationLawPINN
from .pinn_fatigue import PINNFatigue, ParisMaterial, FatigueLoss
from .pinn_pavement import PINNPavement, AAshtoPSIModel, PavementLoss
from .gnn_portfolio import GNNPortfolio, RiskPropagationLayer, CentralityMetrics
from .gradient_boosting import XGBLGBEnsemble, BayesianOptimizer, CreditRiskLoss
from .ensemble_stacking import StackingEnsemble, MetaLearner, StackingLoss

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
'''
        with open(models_init, "w") as f:
            f.write(init_content)
        print(f"  ✓ models/__init__.py")

        # Print summary
        print("\n" + "=" * 70)
        print("✓ PHASE 3 SETUP COMPLETE")
        print("=" * 70)
        print(f"\nDirectory Structure:")
        print(f"  src/")
        print(f"    __init__.py")
        print(f"    models/")
        for src_name, dst_name in model_files.items():
            print(f"      {dst_name}")
        print(f"      __init__.py")

        print(f"\nTotal Files: 8 models + 2 __init__.py = 10 files")
        print(f"Total Lines: ~2900 architecture code")

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_phase3()
    sys.exit(0 if success else 1)
