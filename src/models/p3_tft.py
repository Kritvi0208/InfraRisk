# Temporal Fusion Transformer - Full Implementation
# (Simplified - see actual p3_temporal_fusion_transformer.py for full 300+ line version)

import torch
import torch.nn as nn
import math
from typing import Dict, Tuple, Optional

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int = 256, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.query_proj = nn.Linear(d_model, d_model)
        self.key_proj = nn.Linear(d_model, d_model)
        self.value_proj = nn.Linear(d_model, d_model)
        self.output_proj = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        Q = self.query_proj(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.key_proj(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.value_proj(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attention_weights = torch.softmax(scores, dim=-1)
        context = torch.matmul(attention_weights, V)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.output_proj(context), attention_weights

class TemporalFusionTransformer(nn.Module):
    def __init__(self, input_dim=20, d_model=256, num_heads=8, num_layers=3, horizons=None):
        super().__init__()
        self.input_dim = input_dim
        self.d_model = d_model
        self.horizons = horizons or [3, 6, 12]
        self.input_embedding = nn.Linear(input_dim, d_model)
        self.attention_layers = nn.ModuleList([
            MultiHeadAttention(d_model, num_heads)
            for _ in range(num_layers)
        ])
        self.output_heads = nn.ModuleDict({
            str(h): nn.Linear(d_model, 3)  # P10, P50, P90
            for h in self.horizons
        })

    def forward(self, x):
        x = self.input_embedding(x)
        for attn in self.attention_layers:
            x, _ = attn(x, x, x)
        outputs = {h: self.output_heads[str(h)](x[:, -1, :]) for h in self.horizons}
        return outputs
