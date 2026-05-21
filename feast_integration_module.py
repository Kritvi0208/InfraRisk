"""
Feast Feature Store Integration Module

Minimal in-memory Feast feature store setup with versioning, TTL management,
and lineage tracking.

Example usage:
    >>> feast_store = FeastFeatureStore()
    >>> feast_store.register_feature("climate_adjusted_rul", version="1.0")
    >>> feast_store.store_features(features_df)
    >>> retrieved = feast_store.get_features(project_ids, timestamp)
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class FeatureDataType(Enum):
    """Feature data types"""

    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    STRING = "string"
    BOOL = "bool"


@dataclass
class FeatureDefinition:
    """Defines a single feature for registration"""

    name: str
    description: str
    data_type: FeatureDataType
    owner: str = "infrarisk_team"
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class FeatureStore:
    """In-memory feature storage with versioning"""

    feature_name: str
    feature_version: str
    data: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    ttl_days: int = 90
    lineage: List[str] = field(default_factory=list)

    def is_expired(self) -> bool:
        """Check if feature store data has expired"""
        expiration = self.created_at + timedelta(days=self.ttl_days)
        return datetime.now() > expiration

    def get_data_hash(self) -> str:
        """Generate hash of stored data for integrity check"""
        data_str = self.data.to_json()
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class FeatureLineage:
    """Track feature derivation lineage"""

    feature_name: str
    feature_version: str
    source_features: List[str] = field(default_factory=list)
    transformation: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class FeastFeatureStore:
    """
    Lightweight Feast-compatible feature store for InfraRisk.

    Provides feature registration, storage, retrieval, and lineage tracking
    without requiring a full Feast server deployment.
    """

    def __init__(self, max_stores: int = 100):
        """
        Initialize feature store.

        Args:
            max_stores: Maximum number of feature stores to maintain
        """
        self.feature_registry: Dict[str, FeatureDefinition] = {}
        self.feature_stores: Dict[str, List[FeatureStore]] = {}
        self.lineage_graph: List[FeatureLineage] = []
        self.max_stores = max_stores
        self._version_counter: Dict[str, int] = {}
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        """Define standard feature schema for InfraRisk"""
        self.standard_features = {
            "climate_adjusted_rul": FeatureDefinition(
                name="climate_adjusted_rul",
                description="RUL adjusted for climate impacts (temp, precip)",
                data_type=FeatureDataType.FLOAT32,
                tags=["climate", "degradation", "rul"],
            ),
            "contagion_score": FeatureDefinition(
                name="contagion_score",
                description="Portfolio systemic risk from network analysis",
                data_type=FeatureDataType.FLOAT32,
                tags=["systemic_risk", "network", "contagion"],
            ),
            "sovereign_risk_score": FeatureDefinition(
                name="sovereign_risk_score",
                description="Country-level sovereign risk index",
                data_type=FeatureDataType.FLOAT32,
                tags=["macro", "sovereign", "country_risk"],
            ),
            "revenue_demand_index": FeatureDefinition(
                name="revenue_demand_index",
                description="Sector-specific revenue demand curves",
                data_type=FeatureDataType.FLOAT32,
                tags=["revenue", "demand", "sector"],
            ),
            "financial_dscr": FeatureDefinition(
                name="financial_dscr",
                description="Debt service coverage ratio",
                data_type=FeatureDataType.FLOAT32,
                tags=["financial", "debt", "coverage"],
            ),
            "satellite_ndvi": FeatureDefinition(
                name="satellite_ndvi",
                description="Normalized Difference Vegetation Index",
                data_type=FeatureDataType.FLOAT32,
                tags=["satellite", "vegetation", "geospatial"],
            ),
        }

        for feature_name, feature_def in self.standard_features.items():
            self.register_feature(feature_def)

    def register_feature(
        self, feature_def: FeatureDefinition, overwrite: bool = False
    ) -> bool:
        """
        Register a feature in the feature registry.

        Args:
            feature_def: Feature definition
            overwrite: Whether to overwrite existing registration

        Returns:
            True if registration successful
        """
        if feature_def.name in self.feature_registry and not overwrite:
            return False

        self.feature_registry[feature_def.name] = feature_def
        if feature_def.name not in self._version_counter:
            self._version_counter[feature_def.name] = 1
        else:
            self._version_counter[feature_def.name] += 1

        return True

    def store_features(
        self,
        features_df: pd.DataFrame,
        feature_name: str,
        feature_version: str = "1.0",
        metadata: Optional[Dict] = None,
        source_features: Optional[List[str]] = None,
        transformation: str = "",
    ) -> bool:
        """
        Store feature data in the feature store.

        Args:
            features_df: DataFrame with features
            feature_name: Name of the feature
            feature_version: Version of the feature
            metadata: Additional metadata
            source_features: List of source features used
            transformation: Description of transformation

        Returns:
            True if storage successful
        """
        if feature_name not in self.feature_registry:
            return False

        if feature_name not in self.feature_stores:
            self.feature_stores[feature_name] = []

        store = FeatureStore(
            feature_name=feature_name,
            feature_version=feature_version,
            data=features_df.copy(),
            metadata=metadata or {},
            ttl_days=90,
            lineage=source_features or [],
        )

        self.feature_stores[feature_name].append(store)

        if len(self.feature_stores[feature_name]) > self.max_stores:
            self.feature_stores[feature_name].pop(0)

        lineage = FeatureLineage(
            feature_name=feature_name,
            feature_version=feature_version,
            source_features=source_features or [],
            transformation=transformation,
        )
        self.lineage_graph.append(lineage)

        return True

    def get_features(
        self,
        feature_name: str,
        entity_ids: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Retrieve features from store.

        Args:
            feature_name: Name of feature
            entity_ids: Optional list of entity IDs to filter
            timestamp: Optional timestamp for point-in-time retrieval

        Returns:
            DataFrame with requested features
        """
        if feature_name not in self.feature_stores:
            return pd.DataFrame()

        stores = self.feature_stores[feature_name]
        if not stores:
            return pd.DataFrame()

        latest_store = stores[-1]

        if latest_store.is_expired():
            self.feature_stores[feature_name].remove(latest_store)
            return self.get_features(feature_name, entity_ids, timestamp)

        features_df = latest_store.data.copy()

        if entity_ids:
            if "entity_id" in features_df.columns:
                features_df = features_df[features_df["entity_id"].isin(entity_ids)]
            elif "project_id" in features_df.columns:
                features_df = features_df[features_df["project_id"].isin(entity_ids)]

        return features_df

    def list_features(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List registered features with optional tag filtering.

        Args:
            tags: Optional tags to filter by

        Returns:
            List of feature definitions
        """
        features = []
        for feature_def in self.feature_registry.values():
            if tags:
                if any(tag in feature_def.tags for tag in tags):
                    features.append(asdict(feature_def))
            else:
                features.append(asdict(feature_def))

        return features

    def get_feature_stats(self, feature_name: str) -> Dict[str, Any]:
        """
        Get statistics for a feature.

        Args:
            feature_name: Feature name

        Returns:
            Dictionary with feature statistics
        """
        features_df = self.get_features(feature_name)
        if features_df.empty:
            return {}

        stats = {}
        for col in features_df.select_dtypes(include=[np.number]).columns:
            stats[col] = {
                "mean": features_df[col].mean(),
                "std": features_df[col].std(),
                "min": features_df[col].min(),
                "max": features_df[col].max(),
                "median": features_df[col].median(),
            }

        return stats

    def get_feature_lineage(self, feature_name: str) -> List[Dict]:
        """
        Get lineage for a feature (what inputs created it).

        Args:
            feature_name: Feature name

        Returns:
            List of lineage records
        """
        lineage = [
            asdict(l) for l in self.lineage_graph if l.feature_name == feature_name
        ]
        return lineage

    def validate_features(self, feature_name: str) -> Dict[str, Any]:
        """
        Validate feature data quality and integrity.

        Args:
            feature_name: Feature name

        Returns:
            Validation report
        """
        features_df = self.get_features(feature_name)

        report = {
            "feature_name": feature_name,
            "rows": len(features_df),
            "columns": len(features_df.columns),
            "null_counts": features_df.isnull().sum().to_dict(),
            "data_hash": None,
        }

        if feature_name in self.feature_stores and self.feature_stores[feature_name]:
            report["data_hash"] = self.feature_stores[feature_name][-1].get_data_hash()

        return report

    def export_feature_manifest(self) -> Dict[str, Any]:
        """
        Export feature store manifest for deployment/versioning.

        Returns:
            Manifest dictionary
        """
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "registered_features": list(self.feature_registry.keys()),
            "feature_count": len(self.feature_registry),
            "stored_versions": {
                name: len(stores) for name, stores in self.feature_stores.items()
            },
            "lineage_records": len(self.lineage_graph),
        }

        return manifest

    def cleanup_expired(self) -> int:
        """
        Remove expired feature stores.

        Returns:
            Number of stores removed
        """
        removed = 0
        for feature_name, stores in self.feature_stores.items():
            self.feature_stores[feature_name] = [
                s for s in stores if not s.is_expired()
            ]
            removed += len(stores) - len(self.feature_stores[feature_name])

        return removed


def create_feast_store() -> FeastFeatureStore:
    """Factory function to create feature store"""
    return FeastFeatureStore()
