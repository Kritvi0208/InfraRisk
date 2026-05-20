"""
Setup script to organize Phase 3 models into src/models directory
"""

import os
import shutil

def setup_model_structure():
    """Create proper directory structure and move files."""
    base_dir = r"c:\Users\kayri\OneDrive - IIT BHU\Desktop\InfraRiskAI"
    src_dir = os.path.join(base_dir, "src")
    models_dir = os.path.join(src_dir, "models")
    
    # Create directories
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(src_dir, exist_ok=True)
    
    # Model files to move
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
    
    # Move model files
    for model_file in model_files:
        src_path = os.path.join(base_dir, model_file)
        dst_path = os.path.join(models_dir, model_file)
        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)
            print(f"✓ Moved: {model_file}")
        else:
            print(f"✗ File not found: {model_file}")
    
    # Create __init__.py for src
    src_init = os.path.join(src_dir, "__init__.py")
    if not os.path.exists(src_init):
        with open(src_init, 'w') as f:
            f.write("# src package\n")
        print("✓ Created src/__init__.py")
    
    # Create __init__.py for models
    models_init = os.path.join(models_dir, "__init__.py")
    with open(models_init, 'w') as f:
        f.write("""# Phase 3 Core ML Models Package

from .p3_siamese_cnn import SiameseCNN, SiameseLoss
from .p3_temporal_fusion_transformer import TemporalFusionTransformer
from .p3_pinn_base import PhysicsInformedNN, PhysicsLoss, ConservationLawPINN
from .p3_pinn_fatigue import PINNFatigue, ParisMaterial, FatigueLoss
from .p3_pinn_pavement import PINNPavement, AAshtoPSIModel, PavementLoss
from .p3_gnn_portfolio import GNNPortfolio, RiskPropagationLayer, CentralityMetrics, PortfolioLoss
from .p3_gradient_boosting import XGBLGBEnsemble, BayesianOptimizer, CreditRiskLoss, MockTrainingLoop
from .p3_ensemble_stacking import StackingEnsemble, MetaLearner, StackingLoss

__all__ = [
    'SiameseCNN',
    'SiameseLoss',
    'TemporalFusionTransformer',
    'PhysicsInformedNN',
    'PhysicsLoss',
    'ConservationLawPINN',
    'PINNFatigue',
    'ParisMaterial',
    'FatigueLoss',
    'PINNPavement',
    'AAshtoPSIModel',
    'PavementLoss',
    'GNNPortfolio',
    'RiskPropagationLayer',
    'CentralityMetrics',
    'PortfolioLoss',
    'XGBLGBEnsemble',
    'BayesianOptimizer',
    'CreditRiskLoss',
    'MockTrainingLoop',
    'StackingEnsemble',
    'MetaLearner',
    'StackingLoss',
]
""")
    print("✓ Created src/models/__init__.py")
    
    print(f"\n✓ Model structure setup complete")
    print(f"  Directory: {models_dir}")
    print(f"  Files: {len(model_files)} model files")

if __name__ == "__main__":
    setup_model_structure()
