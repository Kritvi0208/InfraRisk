# Ensemble Stacking Model
import numpy as np
from typing import List, Dict

class EnsembleStackingModel:
    def __init__(self, base_models: List, meta_model):
        self.base_models = base_models
        self.meta_model = meta_model
        self.weights = None

    def train(self, X_train, y_train, X_val, y_val):
        meta_features = np.zeros((X_train.shape[0], len(self.base_models)))
        
        for idx, model in enumerate(self.base_models):
            model.train(X_train, y_train, X_val, y_val)
            meta_features[:, idx] = model.predict(X_train).flatten()
        
        self.meta_model.fit(meta_features, y_train)
        return self

    def predict(self, X):
        meta_features = np.zeros((X.shape[0], len(self.base_models)))
        for idx, model in enumerate(self.base_models):
            meta_features[:, idx] = model.predict(X).flatten()
        return self.meta_model.predict(meta_features)

    def get_model_weights(self):
        return {f"model_{i}": w for i, w in enumerate(self.meta_model.coef_)}
