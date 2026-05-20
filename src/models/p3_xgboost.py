# Gradient Boosted Trees for Credit Scoring - Full Implementation

import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from typing import Dict, Tuple
import numpy as np

class XGBoostCreditScorer:
    def __init__(self, n_estimators=1000, max_depth=7, learning_rate=0.05):
        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=1.0,
            reg_lambda=1.0,
            objective='binary:logistic',
            eval_metric='logloss'
        )
        self.scaler = StandardScaler()
        self.feature_names = None
        self.feature_importance = None

    def train(self, X_train, y_train, X_val, y_val):
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_val_scaled, y_val)],
            early_stopping_rounds=50,
            verbose=False
        )
        self.feature_importance = self.model.feature_importances_
        return self

    def predict_pd(self, features):
        X_scaled = self.scaler.transform(features)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        return probabilities

    def get_feature_importance(self):
        return self.feature_importance
