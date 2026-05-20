"""
Model Registry: MLflow-Compatible In-Memory Model Management
Track model versions, metrics, lifecycle stages (dev → staging → prod)
No MLflow server required - pure Python implementation
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    auc: float = 0.0
    gini: float = 0.0
    ks_statistic: float = 0.0
    calibration_error: float = 0.0
    psi: float = 0.0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ModelVersion:
    """Single model version"""
    version_id: str
    model_name: str
    stage: str  # 'dev', 'staging', 'prod', 'archived'
    timestamp: str
    metrics: ModelMetrics
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    parent_version: Optional[str] = None
    artifact_path: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['metrics'] = self.metrics.to_dict()
        return d


class ModelRegistry:
    """
    Simple, lightweight model registry (no MLflow needed).
    Tracks model versions, metrics, and lifecycle stages.
    """
    
    def __init__(self):
        """Initialize model registry"""
        self.models: Dict[str, List[ModelVersion]] = {}
        self.stage_index: Dict[str, str] = {}  # model_name -> current_prod_version
        self.history: List[Dict] = []
    
    def register_model(self,
                       model_name: str,
                       metrics: Dict,
                       hyperparameters: Optional[Dict] = None,
                       description: str = "",
                       tags: Optional[List[str]] = None) -> str:
        """
        Register a new model version.
        
        Args:
            model_name: Name of model
            metrics: Dictionary of metrics
            hyperparameters: Model hyperparameters
            description: Model description
            tags: Tags for organization
            
        Returns:
            Version ID
        """
        if model_name not in self.models:
            self.models[model_name] = []
        
        # Create version ID
        version_number = len(self.models[model_name]) + 1
        version_id = f"{model_name}_v{version_number}"
        
        # Create metrics object
        model_metrics = ModelMetrics(**metrics) if isinstance(metrics, dict) else metrics
        
        # Create version
        version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            stage='dev',
            timestamp=datetime.now().isoformat(),
            metrics=model_metrics,
            hyperparameters=hyperparameters or {},
            description=description,
            tags=tags or [],
        )
        
        # Store version
        self.models[model_name].append(version)
        
        # Log to history
        self.history.append({
            'action': 'register',
            'version_id': version_id,
            'timestamp': version.timestamp,
        })
        
        return version_id
    
    def promote_version(self, version_id: str, target_stage: str) -> bool:
        """
        Promote model to different stage: dev → staging → prod.
        
        Args:
            version_id: Version to promote
            target_stage: Target stage ('dev', 'staging', 'prod')
            
        Returns:
            True if successful
        """
        # Valid stage transitions
        valid_transitions = {
            'dev': ['staging', 'archived'],
            'staging': ['prod', 'dev', 'archived'],
            'prod': ['staging', 'archived'],
            'archived': ['dev'],
        }
        
        # Find version
        version = self._find_version(version_id)
        if not version:
            return False
        
        # Check valid transition
        if target_stage not in valid_transitions.get(version.stage, []):
            return False
        
        # If promoting to prod, demote current prod version
        if target_stage == 'prod':
            current_prod = self.stage_index.get(version.model_name)
            if current_prod:
                current_version = self._find_version(current_prod)
                if current_version:
                    current_version.stage = 'staging'
            
            self.stage_index[version.model_name] = version_id
        
        version.stage = target_stage
        
        # Log to history
        self.history.append({
            'action': 'promote',
            'version_id': version_id,
            'new_stage': target_stage,
            'timestamp': datetime.now().isoformat(),
        })
        
        return True
    
    def get_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get specific version"""
        return self._find_version(version_id)
    
    def get_latest_version(self, model_name: str, stage: Optional[str] = None) -> Optional[ModelVersion]:
        """
        Get latest version of model (optionally filter by stage).
        
        Args:
            model_name: Model name
            stage: Optional stage filter
            
        Returns:
            Latest version or None
        """
        versions = self.models.get(model_name, [])
        
        if stage:
            versions = [v for v in versions if v.stage == stage]
        
        if not versions:
            return None
        
        return versions[-1]
    
    def get_prod_version(self, model_name: str) -> Optional[ModelVersion]:
        """Get production version of model"""
        prod_version_id = self.stage_index.get(model_name)
        if prod_version_id:
            return self._find_version(prod_version_id)
        return None
    
    def list_versions(self, model_name: str) -> List[ModelVersion]:
        """List all versions of a model"""
        return self.models.get(model_name, [])
    
    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.models.keys())
    
    def compare_versions(self, version_ids: List[str]) -> Dict:
        """
        Compare multiple model versions side-by-side.
        
        Args:
            version_ids: List of version IDs to compare
            
        Returns:
            Comparison table
        """
        comparison = {
            'versions': [],
            'metrics': {},
        }
        
        for vid in version_ids:
            version = self._find_version(vid)
            if not version:
                continue
            
            comparison['versions'].append({
                'version_id': vid,
                'model_name': version.model_name,
                'stage': version.stage,
                'timestamp': version.timestamp,
            })
            
            # Add metrics
            for metric_name, metric_value in version.metrics.to_dict().items():
                if metric_value > 0:  # Only include non-zero metrics
                    if metric_name not in comparison['metrics']:
                        comparison['metrics'][metric_name] = []
                    comparison['metrics'][metric_name].append(float(metric_value))
        
        return comparison
    
    def get_model_lineage(self, version_id: str) -> List[Dict]:
        """
        Get model lineage/ancestry.
        
        Args:
            version_id: Starting version
            
        Returns:
            List of ancestor versions
        """
        lineage = []
        current = self._find_version(version_id)
        
        while current:
            lineage.append({
                'version_id': current.version_id,
                'timestamp': current.timestamp,
                'stage': current.stage,
            })
            
            if current.parent_version:
                current = self._find_version(current.parent_version)
            else:
                break
        
        return lineage
    
    def archive_version(self, version_id: str) -> bool:
        """Archive a model version"""
        return self.promote_version(version_id, 'archived')
    
    def get_registry_summary(self) -> Dict:
        """
        Get summary of entire registry.
        
        Returns:
            Registry statistics
        """
        summary = {
            'total_models': len(self.models),
            'total_versions': sum(len(v) for v in self.models.values()),
            'models_by_stage': {
                'dev': 0,
                'staging': 0,
                'prod': 0,
                'archived': 0,
            },
            'production_models': [],
            'staged_models': [],
        }
        
        for model_name, versions in self.models.items():
            for version in versions:
                summary['models_by_stage'][version.stage] += 1
                
                if version.stage == 'prod':
                    summary['production_models'].append({
                        'version_id': version.version_id,
                        'auc': version.metrics.auc,
                        'gini': version.metrics.gini,
                    })
                
                if version.stage == 'staging':
                    summary['staged_models'].append({
                        'version_id': version.version_id,
                        'auc': version.metrics.auc,
                        'gini': version.metrics.gini,
                    })
        
        return summary
    
    def export_registry(self) -> str:
        """Export registry to JSON string"""
        export_data = {
            'models': {
                name: [v.to_dict() for v in versions]
                for name, versions in self.models.items()
            },
            'stage_index': self.stage_index,
            'history': self.history,
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def _find_version(self, version_id: str) -> Optional[ModelVersion]:
        """Find version by ID"""
        for versions in self.models.values():
            for version in versions:
                if version.version_id == version_id:
                    return version
        return None


def main():
    """Example usage"""
    registry = ModelRegistry()
    
    # Register models
    v1_id = registry.register_model(
        model_name='credit_risk_pd',
        metrics={
            'auc': 0.82,
            'gini': 0.64,
            'ks_statistic': 0.45,
        },
        hyperparameters={'learning_rate': 0.01, 'n_estimators': 100},
        description='Initial credit risk model',
        tags=['production', 'credit-risk'],
    )
    print(f"Registered version: {v1_id}")
    
    # Register improved version
    v2_id = registry.register_model(
        model_name='credit_risk_pd',
        metrics={
            'auc': 0.85,
            'gini': 0.70,
            'ks_statistic': 0.48,
        },
        hyperparameters={'learning_rate': 0.005, 'n_estimators': 200},
        description='Improved model with more features',
        tags=['production', 'credit-risk', 'v2'],
    )
    print(f"Registered version: {v2_id}")
    
    # Promote to staging
    registry.promote_version(v2_id, 'staging')
    print(f"Promoted {v2_id} to staging")
    
    # Promote to production
    registry.promote_version(v2_id, 'prod')
    print(f"Promoted {v2_id} to production")
    
    # Get summary
    summary = registry.get_registry_summary()
    print(f"\nRegistry Summary:")
    print(f"  Total models: {summary['total_models']}")
    print(f"  Total versions: {summary['total_versions']}")
    print(f"  Production models: {len(summary['production_models'])}")
    
    # Get production model
    prod = registry.get_prod_version('credit_risk_pd')
    if prod:
        print(f"\nProduction model: {prod.version_id}")
        print(f"  AUC: {prod.metrics.auc:.3f}")
        print(f"  Gini: {prod.metrics.gini:.3f}")


if __name__ == '__main__':
    main()
