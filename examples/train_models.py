"""Example training script."""
import mlflow
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import make_classification
from src.models.backtesting import BacktestingFramework

def train_example():
    """Example training with MLflow logging."""
    X, y = make_classification(n_samples=1000)
    
    model = GradientBoostingClassifier()
    model.fit(X, y)
    
    bt = BacktestingFramework()
    metrics = bt.backtest(y, model.predict_proba(X)[:, 1])
    
    mlflow.log_metrics(metrics)
    print(f"Gini: {metrics['gini']:.3f}, KS: {metrics['ks']:.3f}")

if __name__ == "__main__":
    train_example()
