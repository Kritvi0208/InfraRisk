"""
Example MLflow Training Script for InfraRisk AI
Demonstrates model training with automatic logging
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import mlflow
import mlflow.sklearn

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.loaders import load_all_data


def prepare_ppi_risk_features(data: dict) -> tuple:
    """
    Prepare features for PPI project risk prediction
    """
    ppi_df = data['ppi_projects'].copy()
    macro_df = data['macro_data'].copy()
    
    # Create synthetic target: 1 if high risk (project value > 90th percentile), 0 otherwise
    threshold = ppi_df['project_value'].quantile(0.9)
    ppi_df['high_risk'] = (ppi_df['project_value'] > threshold).astype(int)
    
    # Feature engineering
    features = pd.DataFrame()
    
    # Project value features
    features['project_value_log'] = np.log1p(ppi_df['project_value'])
    features['project_value_normalized'] = (ppi_df['project_value'] - ppi_df['project_value'].mean()) / ppi_df['project_value'].std()
    
    # Sector encoding
    sector_dummies = pd.get_dummies(ppi_df['sector'], prefix='sector')
    features = pd.concat([features, sector_dummies], axis=1)
    
    # Country features
    country_dummies = pd.get_dummies(ppi_df['country_code'], prefix='country')
    features = pd.concat([features, country_dummies.iloc[:, :10]], axis=1)  # Top 10 countries
    
    # Geographic features
    features['latitude'] = ppi_df['latitude'].fillna(0)
    features['longitude'] = ppi_df['longitude'].fillna(0)
    features['latitude_abs'] = np.abs(features['latitude'])
    
    # Duration features
    ppi_df['duration'] = (ppi_df['end_date'] - ppi_df['start_date']).dt.days
    features['duration_days'] = ppi_df['duration'].fillna(ppi_df['duration'].median())
    
    # Target
    target = ppi_df['high_risk']
    
    # Handle missing values
    features = features.fillna(0)
    
    return features, target


def train_ppi_risk_model(data: dict, experiment_name: str = "ppi-cost-risk"):
    """
    Train PPI project risk prediction model with MLflow logging
    """
    
    print("\n" + "="*80)
    print(f"Training {experiment_name} Model")
    print("="*80)
    
    # Set MLflow experiment
    mlflow.set_experiment(experiment_name)
    
    # Prepare data
    print("\nPreparing features...")
    X, y = prepare_ppi_risk_features(data)
    
    print(f"Features shape: {X.shape}")
    print(f"Target distribution: {y.value_counts().to_dict()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Start MLflow run
    with mlflow.start_run(run_name="RandomForest_v1"):
        
        # Log parameters
        params = {
            'algorithm': 'RandomForest',
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_features': X.shape[1],
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        mlflow.log_params(params)
        print(f"\nLogged parameters: {params}")
        
        # Train model
        print("\nTraining RandomForest classifier...")
        model = RandomForestClassifier(
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            min_samples_split=params['min_samples_split'],
            min_samples_leaf=params['min_samples_leaf'],
            random_state=params['random_state'],
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        print("\nEvaluating model...")
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'train_accuracy': accuracy_score(y_train, y_pred_train),
            'test_accuracy': accuracy_score(y_test, y_pred_test),
            'test_precision': precision_score(y_test, y_pred_test),
            'test_recall': recall_score(y_test, y_pred_test),
            'test_f1': f1_score(y_test, y_pred_test),
            'feature_importance_max': model.feature_importances_.max(),
            'feature_importance_mean': model.feature_importances_.mean()
        }
        
        # Log metrics
        mlflow.log_metrics(metrics)
        print(f"\nLogged metrics:")
        for metric_name, metric_value in metrics.items():
            print(f"  {metric_name}: {metric_value:.4f}")
        
        # Log model
        mlflow.sklearn.log_model(model, "model", registered_model_name="ppi-risk-model-v1")
        print("\nModel logged to MLflow")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        mlflow.log_artifact("model", "feature_importance.csv")
        print("\nTop 10 Important Features:")
        print(feature_importance.head(10))
        
        print("\n" + "="*80)
        print("Training Complete")
        print("="*80)
        
        return model, metrics


def train_macro_scenario_model(data: dict, experiment_name: str = "macro-scenario"):
    """
    Train macroeconomic scenario impact model
    """
    
    print("\n" + "="*80)
    print(f"Training {experiment_name} Model")
    print("="*80)
    
    mlflow.set_experiment(experiment_name)
    
    macro_df = data['macro_data'].copy()
    
    # Prepare panel data features
    print("\nPreparing macro features...")
    
    # Pivot to wide format
    macro_wide = macro_df.pivot_table(
        index=['country_code', 'year'],
        columns='indicator',
        values='value'
    ).reset_index()
    
    # Remove rows with missing values
    macro_wide = macro_wide.dropna()
    
    print(f"Macro data shape: {macro_wide.shape}")
    print(f"Indicators: {list(macro_wide.columns)[2:]}")
    
    with mlflow.start_run(run_name="MacroScenario_v1"):
        
        params = {
            'model_type': 'VAR',  # Vector Autoregression
            'lags': 2,
            'countries': macro_df['country'].nunique(),
            'years': len(macro_df['year'].unique()),
            'indicators': macro_df['indicator'].nunique()
        }
        
        mlflow.log_params(params)
        print(f"\nLogged parameters: {params}")
        
        # Calculate correlation matrix
        correlation = macro_wide[['GDP', 'Inflation', 'Unemployment']].corr()
        
        metrics = {
            'gdp_inflation_corr': correlation.loc['GDP', 'Inflation'],
            'unemployment_inflation_corr': correlation.loc['Unemployment', 'Inflation'],
            'countries_analyzed': macro_df['country'].nunique(),
            'mean_gdp': macro_wide['GDP'].mean(),
            'mean_inflation': macro_wide['Inflation'].mean(),
            'mean_unemployment': macro_wide['Unemployment'].mean()
        }
        
        mlflow.log_metrics(metrics)
        print(f"\nLogged metrics:")
        for metric_name, metric_value in metrics.items():
            print(f"  {metric_name}: {metric_value:.4f}")
        
        print("\n" + "="*80)
        print("Macro Scenario Analysis Complete")
        print("="*80)
        
        return metrics


def main():
    """
    Main training pipeline
    """
    
    print("\nInfraRisk AI - MLflow Training Pipeline")
    print("Loading data...")
    
    # Load all data
    data = load_all_data()
    
    print(f"\nData loaded successfully:")
    print(f"  - PPI Projects: {len(data['ppi_projects']):,}")
    print(f"  - Macro Data: {len(data['macro_data']):,}")
    print(f"  - Interest Rates: {len(data['interest_rates']):,}")
    print(f"  - NBI Bridges: {len(data['nbi_bridges']):,}")
    
    # Train models
    print("\nStarting model training...")
    
    # Model 1: PPI Risk
    ppi_model, ppi_metrics = train_ppi_risk_model(data)
    
    # Model 2: Macro Scenario
    macro_metrics = train_macro_scenario_model(data)
    
    print("\n" + "="*80)
    print("All Models Trained Successfully!")
    print("View MLflow UI: mlflow ui")
    print("="*80)


if __name__ == "__main__":
    main()
