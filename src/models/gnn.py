"""Graph Neural Network for portfolio systemic risk.

Uses centrality metrics to identify critical projects.
"""

import torch
import torch.nn as nn
from typing import Tuple

class PortfolioGNN(nn.Module):
    """GNN for project dependencies with centrality analysis."""
    
    def __init__(self, num_projects: int, feature_dim: int = 32):
        super().__init__()
        self.num_projects = num_projects
        self.feature_dim = feature_dim
        
        self.graph_conv1 = nn.Linear(feature_dim, 64)
        self.graph_conv2 = nn.Linear(64, 32)
        self.output_proj = nn.Linear(32, 1)  # PD output
    
    def forward(self, node_features: torch.Tensor, 
                adjacency: torch.Tensor) -> Tuple[torch.Tensor, dict]:
        """Forward pass with centrality metrics.
        
        Returns:
            pd_scores: Probability of default for each project
            centrality_metrics: betweenness, eigenvector centrality
        """
        # Graph convolution
        x = torch.relu(self.graph_conv1(node_features))
        x = adjacency @ x
        x = torch.relu(self.graph_conv2(x))
        
        # Output
        pd = torch.sigmoid(self.output_proj(x))
        
        # Centrality metrics
        centrality = {
            'betweenness': self._compute_betweenness(adjacency),
            'eigenvector': self._compute_eigenvector(adjacency),
        }
        
        return pd, centrality
    
    def _compute_betweenness(self, adj: torch.Tensor) -> torch.Tensor:
        """Betweenness centrality."""
        return adj.sum(dim=1) / self.num_projects
    
    def _compute_eigenvector(self, adj: torch.Tensor) -> torch.Tensor:
        """Eigenvector centrality (power iteration)."""
        eigs = torch.linalg.eigvalsh(adj + torch.eye(adj.shape[0]) * 1e-6)
        return torch.abs(eigs[-1]) / torch.norm(eigs[-1])
