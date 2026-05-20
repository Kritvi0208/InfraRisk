"""Temporal Fusion Transformer for demand forecasting"""
import torch
import torch.nn as nn

class TemporalFusionTransformer(nn.Module):
    def __init__(self, input_dim: int = 32, output_dim: int = 7, hidden_dim: int = 64):
        super().__init__()
        self.encoder = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=4)
        self.decoder = nn.Linear(hidden_dim, output_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        encoded, _ = self.encoder(x)
        attended, _ = self.attention(encoded, encoded, encoded)
        return self.decoder(attended[:, -1, :])
