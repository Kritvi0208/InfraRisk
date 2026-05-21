"""
Phase 3 Integration Package __init__.py
Complete analytical framework: simulation, interpretation, backtesting, monitoring
"""

try:
    from .monte_carlo_pd import MCScenario, MonteCarloPDEngine
except (ImportError, ModuleNotFoundError):
    MonteCarloPDEngine = None
    MCScenario = None

try:
    from .shap_interpreter import SHAPInterpreter
except (ImportError, ModuleNotFoundError):
    SHAPInterpreter = None

try:
    from .attention_extractor import AttentionExtractor
except (ImportError, ModuleNotFoundError):
    AttentionExtractor = None

try:
    from .centrality_analyzer import CentralityAnalyzer
except (ImportError, ModuleNotFoundError):
    CentralityAnalyzer = None

try:
    from .backtesting import BacktestingFramework
except (ImportError, ModuleNotFoundError):
    BacktestingFramework = None

try:
    from .model_registry import ModelMetrics, ModelRegistry, ModelVersion
except (ImportError, ModuleNotFoundError):
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


def register_model(
    model_name, metrics, hyperparameters=None, description="", tags=None
):
    """Register model in global registry"""
    registry = get_registry()
    if registry is None:
        raise RuntimeError("ModelRegistry not available")
    return registry.register_model(
        model_name, metrics, hyperparameters, description, tags
    )


def get_production_model(model_name):
    """Get production model"""
    registry = get_registry()
    if registry is None:
        return None
    return registry.get_prod_version(model_name)
