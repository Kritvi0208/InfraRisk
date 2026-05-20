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
        
        version_number = len(self.models[model_name]) + 1
        version_id = f"{model_name}_v{version_number}"
        
        model_metrics = ModelMetrics(**metrics) if isinstance(metrics, dict) else metrics
        
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
        
        self.models[model_name].append(version)
        
        self.history.append({
            'action': 'register',
            'version_id': version_id,
            'timestamp': version.timestamp,
        })
        
        return version_id
    
    def promote_version(self, version_id: str, target_stage: str) -> bool:
        """
        Promote model to different stage: dev → staging → prod.
        """
        valid_transitions = {
            'dev': ['staging', 'archived'],
            'staging': ['prod', 'dev', 'archived'],
            'prod': ['staging', 'archived'],
            'archived': ['dev'],
        }
        
        version = self._find_version(version_id)
        if not version:
            return False
        
        if target_stage not in valid_transitions.get(version.stage, []):
            return False
        
        if target_stage == 'prod':
            current_prod = self.stage_index.get(version.model_name)
            if current_prod:
                current_version = self._find_version(current_prod)
                if current_version:
                    current_version.stage = 'staging'
            
            self.stage_index[version.model_name] = version_id
        
        version.stage = target_stage
        
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
        """Get latest version of model (optionally filter by stage)."""
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