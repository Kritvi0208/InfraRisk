"""SHAP interpretability."""

import shap
import numpy as np

class SHAPInterpreter:
    """Model interpretability via SHAP."""
    
    def __init__(self, model):
        self.model = model
        self.explainer = shap.TreeExplainer(model) if hasattr(model, 'tree_') else None
    
    def explain(self, X: np.ndarray) -> dict:
        """SHAP feature importance."""
        if self.explainer is None:
            return {'error': 'Model type not supported'}
        
        shap_values = self.explainer.shap_values(X)
        feature_importance = np.mean(np.abs(shap_values), axis=0)
        
        return {
            'shap_values': shap_values,
            'feature_importance': feature_importance,
        }
