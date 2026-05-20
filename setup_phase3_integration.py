"""
Setup Phase 3 Integration Files
Organize files into src/models structure and prepare for deployment
"""

import os
import shutil

def setup_phase3_integration():
    """Create src/models structure and organize all Phase 3 files"""
    
    # Create src/models directory
    src_models_dir = os.path.join(os.getcwd(), 'src', 'models')
    os.makedirs(src_models_dir, exist_ok=True)
    print(f"Created directory: {src_models_dir}")
    
    # Files to copy/create
    files_to_integrate = {
        'monte_carlo_pd.py': 'Monte Carlo PD engine',
        'shap_interpreter.py': 'SHAP interpretability',
        'attention_extractor.py': 'TFT attention extraction',
        'centrality_analyzer.py': 'GNN centrality metrics',
        'backtesting.py': 'Backtesting framework',
        'model_registry.py': 'Model registry',
    }
    
    # Copy files if they exist in root
    for filename, description in files_to_integrate.items():
        src_path = os.path.join(os.getcwd(), filename)
        dst_path = os.path.join(src_models_dir, filename)
        
        if os.path.exists(src_path):
            shutil.copy(src_path, dst_path)
            print(f"✓ {filename}: {description}")
        else:
            print(f"⚠ Missing: {filename}")
    
    # Create __init__.py with all exports
    init_content = '''"""
Phase 3 Model Integration Package
Complete analytical framework: simulation, interpretation, backtesting, monitoring
"""

try:
    from .monte_carlo_pd import MonteCarloPDEngine, MCScenario
except ImportError:
    MonteCarloPDEngine = None
    MCScenario = None

try:
    from .shap_interpreter import SHAPInterpreter
except ImportError:
    SHAPInterpreter = None

try:
    from .attention_extractor import AttentionExtractor
except ImportError:
    AttentionExtractor = None

try:
    from .centrality_analyzer import CentralityAnalyzer
except ImportError:
    CentralityAnalyzer = None

try:
    from .backtesting import BacktestingFramework
except ImportError:
    BacktestingFramework = None

try:
    from .model_registry import ModelRegistry, ModelVersion, ModelMetrics
except ImportError:
    ModelRegistry = None
    ModelVersion = None
    ModelMetrics = None

__version__ = "3.0.0"
__all__ = [
    "MonteCarloPDEngine",
    "MCScenario",
    "SHAPInterpreter",
    "AttentionExtractor",
    "CentralityAnalyzer",
    "BacktestingFramework",
    "ModelRegistry",
    "ModelVersion",
    "ModelMetrics",
]

# Global registry
_registry = None

def get_registry():
    """Get global model registry"""
    global _registry
    if _registry is None and ModelRegistry is not None:
        _registry = ModelRegistry()
    return _registry

def register_model(model_name, metrics, hyperparameters=None, description="", tags=None):
    """Register model in global registry"""
    registry = get_registry()
    if registry is None:
        raise RuntimeError("ModelRegistry not available")
    return registry.register_model(model_name, metrics, hyperparameters, description, tags)

def get_production_model(model_name):
    """Get production model"""
    registry = get_registry()
    if registry is None:
        return None
    return registry.get_prod_version(model_name)
'''
    
    init_path = os.path.join(src_models_dir, '__init__.py')
    with open(init_path, 'w') as f:
        f.write(init_content)
    print(f"✓ Created __init__.py with exports")
    
    # Create src/__init__.py if needed
    src_init_path = os.path.join(os.path.dirname(src_models_dir), '__init__.py')
    if not os.path.exists(src_init_path):
        with open(src_init_path, 'w') as f:
            f.write("# src package\n")
        print(f"✓ Created src/__init__.py")
    
    print(f"\n✅ Phase 3 integration complete!")
    print(f"Files organized in: {src_models_dir}")
    
    return src_models_dir


if __name__ == '__main__':
    setup_phase3_integration()
