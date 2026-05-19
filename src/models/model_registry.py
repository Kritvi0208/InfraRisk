"""MLflow model registry."""

import mlflow
import json

class ModelRegistry:
    """Register and track models in MLflow."""
    
    def __init__(self, experiment_name="InfraRisk"):
        mlflow.set_experiment(experiment_name)
    
    def log_model(self, model, name: str, metrics: dict, params: dict):
        """Log model with metrics and params."""
        with mlflow.start_run(run_name=name):
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, artifact_path="model")
    
    def register_model(self, model_uri: str, name: str):
        """Register model version."""
        mlflow.register_model(model_uri, name)
