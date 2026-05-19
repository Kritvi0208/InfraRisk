"""Backtesting framework."""

from sklearn.metrics import roc_auc_score, gini
import numpy as np

class BacktestingFramework:
    """Model validation metrics."""
    
    @staticmethod
    def calculate_gini(y_true, y_pred):
        """Gini coefficient (2*AUC - 1)."""
        auc = roc_auc_score(y_true, y_pred)
        return 2 * auc - 1
    
    @staticmethod
    def calculate_ks(y_true, y_pred):
        """Kolmogorov-Smirnov statistic."""
        fpr = np.sum((y_pred >= y_pred[y_true == 0].max()) & (y_true == 0)) / np.sum(y_true == 0)
        tpr = np.sum((y_pred >= y_pred[y_true == 0].max()) & (y_true == 1)) / np.sum(y_true == 1)
        return abs(fpr - tpr)
    
    def backtest(self, y_true, y_pred):
        """Full backtesting report."""
        return {
            'auc_roc': roc_auc_score(y_true, y_pred),
            'gini': self.calculate_gini(y_true, y_pred),
            'ks': self.calculate_ks(y_true, y_pred),
        }
