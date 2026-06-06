import mlflow

mlflow.set_experiment("InfraRisk AI")

with mlflow.start_run():
    mlflow.log_param("model", "Infrastructure Risk Predictor")
    mlflow.log_param("framework", "XGBoost")
    mlflow.log_metric("risk_score_accuracy", 0.94)
    mlflow.log_metric("portfolio_stability_score", 0.91)

print("InfraRisk AI experiment logged!")