"""
Temporal Fusion Transformer for Multi-Horizon Forecasting
Supports multi-quarter predictions with quantile regression (P10, P50, P90)
"""

import math
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn


class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism with learnable scaling."""

    def __init__(self, d_model: int = 256, num_heads: int = 8, dropout: float = 0.1):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.query_proj = nn.Linear(d_model, d_model)
        self.key_proj = nn.Linear(d_model, d_model)
        self.value_proj = nn.Linear(d_model, d_model)
        self.output_proj = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)
        self.attention_weights = None

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Multi-head attention forward pass."""
        batch_size = query.size(0)

        Q = (
            self.query_proj(query)
            .view(batch_size, -1, self.num_heads, self.d_k)
            .transpose(1, 2)
        )
        K = (
            self.key_proj(key)
            .view(batch_size, -1, self.num_heads, self.d_k)
            .transpose(1, 2)
        )
        V = (
            self.value_proj(value)
            .view(batch_size, -1, self.num_heads, self.d_k)
            .transpose(1, 2)
        )

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attention_weights = torch.softmax(scores, dim=-1)
        self.attention_weights = attention_weights
        attention_weights = self.dropout(attention_weights)

        context = torch.matmul(attention_weights, V)
        context = (
            context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        )
        output = self.output_proj(context)

        return output, attention_weights


class TemporalFusionTransformer(nn.Module):
    """
    Temporal Fusion Transformer for multi-horizon forecasting.

    Mock Input/Output:
    - Input: (batch_size, seq_len=12, num_features=20) time series
    - Output quantiles: (batch_size, 3, 3) -> 3 horizons, 3 quantiles (P10, P50, P90)
    - Attention weights: (batch_size, num_heads, seq_len, seq_len)

    Forecasts construction cost for 3, 6, 12 quarter horizons with uncertainty quantiles.
    """

    def __init__(
        self,
        input_dim: int = 20,
        d_model: int = 256,
        num_heads: int = 8,
        num_layers: int = 3,
        dropout: float = 0.1,
        horizons: list = None,
    ):
        super(TemporalFusionTransformer, self).__init__()

        self.input_dim = input_dim
        self.d_model = d_model
        self.horizons = horizons or [3, 6, 12]  # quarters
        self.num_quantiles = 3  # P10, P50, P90

        # Input embedding
        self.input_embedding = nn.Linear(input_dim, d_model)
        self.positional_encoding = self._build_positional_encoding(max_len=100)

        # Temporal attention layers
        self.attention_layers = nn.ModuleList(
            [
                MultiHeadAttention(
                    d_model=d_model, num_heads=num_heads, dropout=dropout
                )
                for _ in range(num_layers)
            ]
        )

        # Feedforward layers
        self.feedforward_layers = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(d_model, 4 * d_model),
                    nn.ReLU(),
                    nn.Dropout(dropout),
                    nn.Linear(4 * d_model, d_model),
                )
                for _ in range(num_layers)
            ]
        )

        self.layer_norms_attn = nn.ModuleList(
            [nn.LayerNorm(d_model) for _ in range(num_layers)]
        )
        self.layer_norms_ff = nn.ModuleList(
            [nn.LayerNorm(d_model) for _ in range(num_layers)]
        )

        # Quantile output heads
        self.quantile_heads = nn.ModuleList(
            [
                nn.Linear(d_model, len(self.horizons) * self.num_quantiles)
                for _ in range(len(self.horizons))
            ]
        )

        self.dropout = nn.Dropout(dropout)
        self.attention_weights_history = None

    def _build_positional_encoding(self, max_len: int = 100) -> torch.Tensor:
        """Build positional encoding (fixed or learnable)."""
        pe = torch.zeros(max_len, self.d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, self.d_model, 2).float()
            * (-math.log(10000.0) / self.d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass for multi-horizon quantile forecasting.

        Args:
            x: (batch_size, seq_len, input_dim)

        Returns:
            Dict with:
            - 'quantiles': (batch_size, len(horizons), num_quantiles)
            - 'attention_weights': (batch_size, num_heads, seq_len, seq_len)
        """
        batch_size, seq_len, _ = x.size()

        # Embed and add positional encoding
        x = self.input_embedding(x)
        pe = self.positional_encoding[:, :seq_len, :].to(x.device)
        x = x + pe
        x = self.dropout(x)

        # Transformer layers
        attention_weights_list = []
        for i in range(len(self.attention_layers)):
            # Self-attention
            attn_out, attn_weights = self.attention_layers[i](x, x, x)
            attention_weights_list.append(attn_weights)
            x = self.layer_norms_attn[i](x + attn_out)

            # Feedforward
            ff_out = self.feedforward_layers[i](x)
            x = self.layer_norms_ff[i](x + ff_out)

        # Store attention weights
        self.attention_weights_history = torch.stack(
            attention_weights_list, dim=0
        ).mean(dim=0)

        # Global average pooling
        x_global = x.mean(dim=1)  # (batch_size, d_model)

        # Generate quantile predictions for each horizon
        quantile_outputs = []
        for head in self.quantile_heads:
            quantile_preds = head(
                x_global
            )  # (batch_size, len(horizons) * num_quantiles)
            quantile_preds = quantile_preds.view(
                batch_size, len(self.horizons), self.num_quantiles
            )
            quantile_outputs.append(quantile_preds)

        # Average across heads
        quantiles = torch.stack(quantile_outputs, dim=0).mean(dim=0)

        return {
            "quantiles": quantiles,  # (batch_size, len(horizons), num_quantiles) -> P10, P50, P90
            "attention_weights": self.attention_weights_history,
            "temporal_features": x,  # (batch_size, seq_len, d_model)
        }

    def get_attention_weights(self) -> Optional[torch.Tensor]:
        """Extract learned attention weights."""
        return self.attention_weights_history


if __name__ == "__main__":
    model = TemporalFusionTransformer(
        input_dim=20, d_model=256, num_heads=8, num_layers=3, horizons=[3, 6, 12]
    )

    # Mock input: 12 quarters of historical data with 20 features
    x = torch.randn(8, 12, 20)
    output = model(x)

    assert output["quantiles"].shape == (
        8,
        3,
        3,
    ), f"Expected (8, 3, 3), got {output['quantiles'].shape}"
    assert output["attention_weights"].shape[0] == 8
    assert output["temporal_features"].shape == (8, 12, 256)

    print("✓ TemporalFusionTransformer architecture validation passed")
    print(
        f"  Quantiles shape: {output['quantiles'].shape} (batch, horizons, quantiles)"
    )
    print(f"  Attention weights: {output['attention_weights'].shape}")
