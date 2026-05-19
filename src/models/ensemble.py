"""Ensemble stacking meta-learner."""

import numpy as np
from sklearn.linear_model import LogisticRegression

class EnsembleStacking:
    """Sector-weighted stacking."""
    
    def __init__(self):
        self.meta_learner = LogisticRegression()
        self.sector_weights = {
            'Transport': 1.0,
            'Energy': 1.1,
            'Water': 0.9,
            'Telecom': 1.2,
            'Social': 0.8,
        }
    
    def stack(self, base_predictions: dict, sector: str) -> float:
        """Weighted combination of base models."""
        weight = self.sector_weights.get(sector, 1.0)
        predictions = np.array(list(base_predictions.values())).reshape(1, -1)
        ensemble_pred = self.meta_learner.predict_proba(predictions)[0, 1]
        return ensemble_pred * weight
