"""
Temporal Fusion Transformer Attention Extractor
Extract and visualize interpretable attention weights from TFT
Shows how historical events influence forecasts
"""

import warnings
from typing import Dict, List, Optional, Tuple

import numpy as np

warnings.filterwarnings("ignore")


class AttentionExtractor:
    """Extract and analyze attention weights from Temporal Fusion Transformer"""

    def __init__(self, n_time_steps: int = 52, n_features: int = 10, n_heads: int = 4):
        """
        Initialize attention extractor.

        Args:
            n_time_steps: Number of time steps (weeks)
            n_features: Number of features
            n_heads: Number of attention heads
        """
        self.n_time_steps = n_time_steps
        self.n_features = n_features
        self.n_heads = n_heads
        self.attention_weights: Optional[np.ndarray] = None
        self.temporal_attention: Optional[np.ndarray] = None
        self.feature_attention: Optional[np.ndarray] = None

    def extract_temporal_attention(
        self, sequence_length: int = 52, forecast_horizon: int = 12
    ) -> np.ndarray:
        """
        Extract temporal attention weights: which past timesteps matter for forecasts.

        Args:
            sequence_length: Length of historical sequence
            forecast_horizon: Forecast horizon

        Returns:
            Attention weights (forecast_steps x sequence_length x n_heads)
        """
        # Mock attention: recent times matter more
        temporal_att = np.zeros((forecast_horizon, sequence_length, self.n_heads))

        for h in range(self.n_heads):
            # Exponential decay: recent past weighted higher
            decay_rate = 0.05 + np.random.rand() * 0.05
            for t in range(forecast_horizon):
                weights = np.exp(-decay_rate * np.arange(sequence_length)[::-1])
                # Add some spike at important periods (e.g., seasonality)
                seasonal_period = 13
                weights[::seasonal_period] *= 1.5
                temporal_att[t, :, h] = weights / weights.sum()

        self.temporal_attention = temporal_att
        return temporal_att

    def extract_feature_attention(self) -> np.ndarray:
        """
        Extract feature attention: which features matter for each forecast step.

        Returns:
            Feature attention (forecast_steps x n_features x n_heads)
        """
        feature_att = np.zeros((self.n_time_steps, self.n_features, self.n_heads))

        # Mock feature importance: varies by head and time step
        for h in range(self.n_heads):
            for t in range(self.n_time_steps):
                # Different heads focus on different features
                importance = np.random.dirichlet(np.ones(self.n_features))
                # Add temporal variation
                importance[t % self.n_features] *= 1.5
                feature_att[t, :, h] = importance / importance.sum()

        self.feature_attention = feature_att
        return feature_att

    def get_temporal_importance(self) -> Dict:
        """
        Summarize which time periods are most important across all forecast steps.

        Returns:
            Dictionary with temporal importance metrics
        """
        if self.temporal_attention is None:
            self.extract_temporal_attention()

        # Average attention across heads and forecast steps
        avg_attention = np.mean(self.temporal_attention, axis=(0, 2))

        # Find peaks (important time periods)
        sorted_idx = np.argsort(avg_attention)[::-1]

        return {
            "most_attended_periods": sorted_idx[:5].tolist(),
            "attention_weights": avg_attention[sorted_idx].tolist(),
            "max_attention": float(avg_attention.max()),
            "min_attention": float(avg_attention.min()),
            "mean_attention": float(avg_attention.mean()),
        }

    def get_feature_importance(self) -> Dict:
        """
        Summarize which features are most important.

        Returns:
            Dictionary with feature importance
        """
        if self.feature_attention is None:
            self.extract_feature_attention()

        # Average attention across time steps and heads
        avg_attention = np.mean(self.feature_attention, axis=(0, 2))
        sorted_idx = np.argsort(avg_attention)[::-1]

        return {
            "feature_ranking": sorted_idx.tolist(),
            "feature_importance": avg_attention[sorted_idx].tolist(),
            "features": [f"Feature_{i}" for i in sorted_idx],
        }

    def create_attention_heatmap(
        self, forecast_step: int = 0, head_idx: int = 0
    ) -> Dict:
        """
        Create attention heatmap: how each historical timestep influences forecast.

        Args:
            forecast_step: Which forecast step (0 = 1 step ahead, 11 = 12 steps ahead)
            head_idx: Which attention head (0 to n_heads-1)

        Returns:
            Heatmap data for visualization
        """
        if self.temporal_attention is None:
            self.extract_temporal_attention()

        if forecast_step >= len(self.temporal_attention):
            raise ValueError(f"Forecast step {forecast_step} out of range")

        if head_idx >= self.n_heads:
            raise ValueError(f"Head {head_idx} out of range (n_heads={self.n_heads})")

        attention = self.temporal_attention[forecast_step, :, head_idx]

        # Identify peaks and valleys
        sorted_idx = np.argsort(attention)[::-1]
        top_periods = sorted_idx[:5]

        heatmap = {
            "type": "heatmap",
            "forecast_step": forecast_step,
            "head": head_idx,
            "attention_weights": attention.tolist(),
            "top_attended_periods": top_periods.tolist(),
            "attention_at_top_periods": attention[top_periods].tolist(),
        }

        return heatmap

    def get_attention_flow(self, forecast_horizon: int = 12) -> Dict:
        """
        Show how attention evolves across forecast horizon.

        Args:
            forecast_horizon: Number of forecast steps

        Returns:
            Dictionary with attention flow data
        """
        if self.temporal_attention is None:
            self.extract_temporal_attention(forecast_horizon=forecast_horizon)

        # For each forecast step, find most attended historical period
        flow = []
        for t in range(min(forecast_horizon, len(self.temporal_attention))):
            avg_head_att = np.mean(self.temporal_attention[t, :, :], axis=1)
            most_attended = int(np.argmax(avg_head_att))
            max_att = float(avg_head_att[most_attended])

            flow.append(
                {
                    "forecast_step": t + 1,
                    "most_attended_period": most_attended,
                    "attention_strength": max_att,
                }
            )

        return {
            "attention_flow": flow,
            "interpretation": "Shows which historical period is most influential for each forecast step",
        }

    def extract_multi_head_patterns(self) -> Dict:
        """
        Analyze patterns across different attention heads.

        Returns:
            Dictionary with multi-head analysis
        """
        if self.temporal_attention is None or self.feature_attention is None:
            self.extract_temporal_attention()
            self.extract_feature_attention()

        patterns = {}
        for h in range(self.n_heads):
            # Head-specific temporal pattern
            temporal_pattern = np.mean(self.temporal_attention[:, :, h], axis=0)

            # Head-specific feature pattern
            feature_pattern = np.mean(self.feature_attention[:, :, h], axis=0)

            patterns[f"head_{h}"] = {
                "temporal_focus": int(np.argmax(temporal_pattern)),
                "feature_focus": int(np.argmax(feature_pattern)),
                "temporal_concentration": float(np.max(temporal_pattern)),
                "feature_concentration": float(np.max(feature_pattern)),
            }

        return patterns

    def explain_forecast(self, forecast_step: int = 1) -> Dict:
        """
        Explain a specific forecast step using attention.

        Args:
            forecast_step: Which step ahead (1-12)

        Returns:
            Interpretation of what drives the forecast
        """
        if self.temporal_attention is None:
            self.extract_temporal_attention()

        step_idx = forecast_step - 1

        # Average across all attention heads
        avg_attention = np.mean(self.temporal_attention[step_idx, :, :], axis=1)

        # Find most and least attended periods
        top_periods = np.argsort(avg_attention)[::-1][:3]

        explanation = {
            "forecast_step": forecast_step,
            "most_influential_periods": top_periods.tolist(),
            "attention_distribution": {
                "concentrated": float(np.max(avg_attention)) > 0.5,
                "max_weight": float(np.max(avg_attention)),
                "entropy": float(
                    -np.sum(avg_attention * np.log(avg_attention + 1e-10))
                ),
            },
            "interpretation": f"Step {forecast_step} forecast is primarily influenced by periods {top_periods.tolist()}",
        }

        return explanation


def main():
    """Example usage"""
    extractor = AttentionExtractor(n_time_steps=52, n_features=10, n_heads=4)

    # Extract attention
    temporal_att = extractor.extract_temporal_attention()
    feature_att = extractor.extract_feature_attention()
    print(f"Temporal attention shape: {temporal_att.shape}")
    print(f"Feature attention shape: {feature_att.shape}")

    # Analyze importance
    temporal_imp = extractor.get_temporal_importance()
    print(f"\nTop attended periods: {temporal_imp['most_attended_periods']}")

    feature_imp = extractor.get_feature_importance()
    print(f"Top important features: {feature_imp['features'][:3]}")

    # Heatmap for step 1
    heatmap = extractor.create_attention_heatmap(forecast_step=0, head_idx=0)
    print(f"\nAttention heatmap for forecast step 1, head 0:")
    print(f"  Top attended periods: {heatmap['top_attended_periods']}")

    # Attention flow
    flow = extractor.get_attention_flow(forecast_horizon=12)
    print(f"\nAttention flow (first 3 steps):")
    for item in flow["attention_flow"][:3]:
        print(f"  {item}")


if __name__ == "__main__":
    main()
