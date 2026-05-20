"""Ensemble stacking with meta-learner for credit risk prediction"""
import torch
import torch.nn as nn
from typing import Dict, List, Tuple

class MetaLearner(nn.Module):
    def __init__(self, num_base_models: int = 5, hidden_dim: int = 64):
        super().__init__()
        self.stack = nn.Sequential(
            nn.Linear(num_base_models, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.weights = nn.Parameter(torch.ones(num_base_models) / num_base_models)

    def forward(self, base_predictions: torch.Tensor) -> torch.Tensor:
        weighted = base_predictions * self.weights.unsqueeze(0)
        return self.stack(base_predictions)
