"""
Backtesting Framework for Credit Risk Models
Out-of-sample validation: Gini coefficient, AUC-ROC, KS statistic
Calibration plots and historical backtest (mock data)
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
import warnings

warnings.filterwarnings('ignore')


class BacktestingFramework:
    """
    Out-of-sample validation for credit risk models.
    Computes standard credit risk metrics: Gini, AUC, KS, PSI.
    """
    
    def __init__(self):
        """Initialize backtesting framework"""
        self.results: Dict = {}
    
    def compute_auc_roc(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Compute Area Under ROC Curve using trapezoidal rule.
        
        Args:
            y_true: True binary labels (0 or 1)
            y_pred: Predicted probabilities [0, 1]
            
        Returns:
            AUC-ROC score
        """
        # Sort by predictions descending
        sorted_idx = np.argsort(-y_pred)
        y_sorted = y_true[sorted_idx]
        
        # Cumulative TP and FP
        n_positives = np.sum(y_true)
        n_negatives = len(y_true) - n_positives
        
        if n_positives == 0 or n_negatives == 0:
            return 0.5
        
        # True positive rate and false positive rate
        tpr = np.cumsum(y_sorted) / n_positives
        fpr = np.cumsum(1 - y_sorted) / n_negatives
        
        # Prepend (0, 0)
        tpr = np.concatenate([[0], tpr])
        fpr = np.concatenate([[0], fpr])
        
        # Trapezoidal rule
        auc = np.trapz(tpr, fpr)
        
        return float(np.clip(auc, 0, 1))
    
    def compute_gini(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Compute Gini coefficient (2 * AUC - 1).
        Measures discriminatory power.
        
        Args:
            y_true: True binary labels
            y_pred: Predicted probabilities
            
        Returns:
            Gini coefficient
        """
        auc = self.compute_auc_roc(y_true, y_pred)
        gini = 2 * auc - 1
        
        return float(gini)
    
    def compute_ks_statistic(self, y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, int]:
        """
        Compute Kolmogorov-Smirnov statistic.
        Maximum separation between good and bad cumulative distributions.
        
        Args:
            y_true: True binary labels
            y_pred: Predicted probabilities
            
        Returns:
            Tuple of (KS statistic, optimal cutoff percentile)
        """
        # Sort by predictions descending
        sorted_idx = np.argsort(-y_pred)
        y_sorted = y_true[sorted_idx]
        
        n_total = len(y_true)
        n_positives = np.sum(y_true)
        n_negatives = n_total - n_positives
        
        if n_positives == 0 or n_negatives == 0:
            return 0.0, 50
        
        # Cumulative % of goods and bads
        cum_goods = np.cumsum(y_sorted) / n_positives
        cum_bads = np.cumsum(1 - y_sorted) / n_negatives
        
        # KS statistic: max difference
        ks_stat = np.max(np.abs(cum_goods - cum_bads))
        
        # Optimal cutoff (where difference is max)
        cutoff_idx = np.argmax(np.abs(cum_goods - cum_bads))
        cutoff_percentile = (cutoff_idx / n_total) * 100
        
        return float(ks_stat), int(cutoff_percentile)
    
    def compute_psi(self, 
                   y_pred_dev: np.ndarray,
                   y_pred_test: np.ndarray,
                   n_bins: int = 10) -> float:
        """
        Compute Population Stability Index (PSI).
        Detects model degradation due to data shift.
        
        Args:
            y_pred_dev: Predictions on development set
            y_pred_test: Predictions on test set
            n_bins: Number of bins
            
        Returns:
            PSI value
        """
        # Bin edges based on development set
        bins = np.percentile(y_pred_dev, np.linspace(0, 100, n_bins + 1))
        bins[0] -= 1e-8  # Include min value
        
        # Digitize predictions
        dev_bins = np.digitize(y_pred_dev, bins) - 1
        test_bins = np.digitize(y_pred_test, bins) - 1
        
        # Distribution percentages
        dev_dist = np.bincount(dev_bins, minlength=n_bins) / len(y_pred_dev)
        test_dist = np.bincount(test_bins, minlength=n_bins) / len(y_pred_test)
        
        # PSI calculation (avoid log(0))
        dev_dist = np.maximum(dev_dist, 1e-6)
        test_dist = np.maximum(test_dist, 1e-6)
        
        psi = np.sum((test_dist - dev_dist) * np.log(test_dist / dev_dist))
        
        return float(psi)
    
    def compute_calibration_error(self, y_true: np.ndarray, y_pred: np.ndarray, n_bins: int = 10) -> Dict:
        """
        Compute calibration error: expected vs actual default rates.
        
        Args:
            y_true: True binary labels
            y_pred: Predicted probabilities
            n_bins: Number of bins
            
        Returns:
            Calibration metrics
        """
        # Bin predictions
        bins = np.percentile(y_pred, np.linspace(0, 100, n_bins + 1))
        bins[0] -= 1e-8
        bin_idx = np.digitize(y_pred, bins) - 1
        
        calibration = []
        total_mae = 0
        
        for i in range(n_bins):
            mask = bin_idx == i
            if np.sum(mask) > 0:
                expected_rate = np.mean(y_pred[mask])
                actual_rate = np.mean(y_true[mask])
                sample_count = np.sum(mask)
                
                calibration.append({
                    'bin': i,
                    'expected_rate': float(expected_rate),
                    'actual_rate': float(actual_rate),
                    'sample_count': int(sample_count),
                })
                
                total_mae += abs(expected_rate - actual_rate)
        
        mae = total_mae / n_bins
        
        return {
            'calibration_data': calibration,
            'mean_absolute_error': float(mae),
            'interpretation': 'Perfect calibration: MAE = 0',
        }
    
    def backtest_historical(self, 
                           n_periods: int = 12,
                           n_samples: int = 1000,
                           base_default_rate: float = 0.02) -> Dict:
        """
        Backtest model on mock historical data (12 periods).
        
        Args:
            n_periods: Number of historical periods
            n_samples: Samples per period
            base_default_rate: Base default rate
            
        Returns:
            Backtest results
        """
        backtest_results = []
        
        for period in range(n_periods):
            # Generate mock predictions with drift
            drift = 0.002 * period  # Model drift over time
            y_pred = np.clip(
                np.random.beta(2, 50, n_samples) + drift,
                0, 1
            )
            
            # Generate actual defaults
            y_true = (np.random.random(n_samples) < y_pred).astype(int)
            
            # Compute metrics
            auc = self.compute_auc_roc(y_true, y_pred)
            gini = self.compute_gini(y_true, y_pred)
            ks, _ = self.compute_ks_statistic(y_true, y_pred)
            actual_default = np.mean(y_true)
            
            backtest_results.append({
                'period': period + 1,
                'auc': float(auc),
                'gini': float(gini),
                'ks_statistic': float(ks),
                'actual_default_rate': float(actual_default),
                'predicted_default_rate': float(np.mean(y_pred)),
                'sample_count': n_samples,
            })
        
        return {
            'backtest_periods': backtest_results,
            'avg_auc': float(np.mean([r['auc'] for r in backtest_results])),
            'avg_gini': float(np.mean([r['gini'] for r in backtest_results])),
            'avg_ks': float(np.mean([r['ks_statistic'] for r in backtest_results])),
            'interpretation': 'Monitor trends for model degradation',
        }
    
    def run_full_backtest(self, verbose: bool = True) -> Dict:
        """
        Run comprehensive backtest.
        
        Args:
            verbose: Print results
            
        Returns:
            Full backtest report
        """
        # Generate test data
        np.random.seed(42)
        n_test = 5000
        
        # Predictions and actuals
        y_pred = np.random.beta(3, 50, n_test)
        y_true = (np.random.random(n_test) < y_pred).astype(int)
        
        # Compute metrics
        auc = self.compute_auc_roc(y_true, y_pred)
        gini = self.compute_gini(y_true, y_pred)
        ks, cutoff = self.compute_ks_statistic(y_true, y_pred)
        
        calibration = self.compute_calibration_error(y_true, y_pred)
        
        # PSI (split into dev/test)
        split_idx = n_test // 2
        psi = self.compute_psi(y_pred[:split_idx], y_pred[split_idx:])
        
        # Historical backtest
        historical = self.backtest_historical()
        
        report = {
            'summary': {
                'auc_roc': auc,
                'gini': gini,
                'ks_statistic': ks,
                'ks_cutoff_percentile': cutoff,
                'psi': psi,
                'calibration_mae': calibration['mean_absolute_error'],
            },
            'calibration': calibration,
            'historical_backtest': historical,
            'test_sample_count': n_test,
            'actual_default_count': int(np.sum(y_true)),
        }
        
        if verbose:
            print("=== BACKTEST REPORT ===")
            print(f"Sample size: {n_test}")
            print(f"Default count: {np.sum(y_true)}")
            print(f"\nDiscriminatory Power:")
            print(f"  AUC-ROC: {auc:.4f}")
            print(f"  Gini: {gini:.4f}")
            print(f"  KS Statistic: {ks:.4f} (cutoff: {cutoff}th percentile)")
            print(f"\nModel Stability:")
            print(f"  PSI: {psi:.4f} ({'Acceptable' if psi < 0.1 else 'Warning' if psi < 0.25 else 'Degradation'})")
            print(f"\nCalibration:")
            print(f"  MAE: {calibration['mean_absolute_error']:.4f}")
            print(f"\nHistorical Performance (avg):")
            print(f"  AUC: {historical['avg_auc']:.4f}")
            print(f"  Gini: {historical['avg_gini']:.4f}")
        
        return report


def main():
    """Example usage"""
    framework = BacktestingFramework()
    report = framework.run_full_backtest(verbose=True)
    
    return report


if __name__ == '__main__':
    main()
