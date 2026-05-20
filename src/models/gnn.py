"""Graph Neural Network for portfolio risk propagation"""
from typing import Optional, Tuple
import torch
import torch.nn as nn

class ProjectGNN(nn.Module):
    def __init__(self, node_features: int = 25, hidden_dim: int = 64):
        super().__init__()
        self.node_embedder = nn.Linear(node_features, hidden_dim)
        self.message_pass = nn.Linear(hidden_dim, hidden_dim)
        self.risk_head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, nodes: torch.Tensor, edges: torch.Tensor) -> torch.Tensor:
        embeddings = self.node_embedder(nodes)
        return self.risk_head(embeddings)
