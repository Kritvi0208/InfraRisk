"""
Graph Neural Network for Portfolio Risk Propagation
PyTorch Geometric implementation for project dependencies
Centrality metrics and message passing for risk contagion
"""

import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv, GraphConv, MessagePassing
from torch_geometric.data import Data
from typing import Dict, Tuple, Optional
import numpy as np


class RiskPropagationLayer(MessagePassing):
    """
    Custom message passing layer for risk propagation through graph.
    Risk spreads based on edge weights and node vulnerabilities.
    """
    
    def __init__(self, in_channels: int, out_channels: int, aggr: str = 'mean'):
        super(RiskPropagationLayer, self).__init__(aggr=aggr)
        self.lin = nn.Linear(in_channels, out_channels)
        self.bias = nn.Parameter(torch.Tensor(out_channels))
        self.reset_parameters()
    
    def reset_parameters(self):
        self.lin.reset_parameters()
        self.bias.data.zero_()
    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_weight: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Message passing forward."""
        x = self.lin(x)
        return self.propagate(edge_index, x=x, edge_weight=edge_weight)
    
    def message(self, x_j: torch.Tensor, edge_weight: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Message computation with edge weights."""
        if edge_weight is not None:
            return x_j * edge_weight.view(-1, 1)
        return x_j
    
    def update(self, aggr_out: torch.Tensor) -> torch.Tensor:
        """Update node embeddings."""
        return aggr_out + self.bias


class CentralityMetrics:
    """Compute graph centrality metrics for importance ranking."""
    
    @staticmethod
    def betweenness_centrality(edge_index: torch.Tensor, num_nodes: int) -> torch.Tensor:
        """Approximate betweenness centrality via random walks."""
        edge_index_numpy = edge_index.cpu().numpy()
        betweenness = np.zeros(num_nodes)
        
        # Simplified: count in/out degree
        for node in range(num_nodes):
            in_degree = np.sum(edge_index_numpy[1] == node)
            out_degree = np.sum(edge_index_numpy[0] == node)
            betweenness[node] = (in_degree + out_degree) / (2 * num_nodes)
        
        return torch.tensor(betweenness, dtype=torch.float32)
    
    @staticmethod
    def eigenvector_centrality(edge_index: torch.Tensor, num_nodes: int, num_iter: int = 10) -> torch.Tensor:
        """Power iteration for eigenvector centrality."""
        # Build adjacency matrix
        adj = torch.zeros(num_nodes, num_nodes)
        adj[edge_index[0], edge_index[1]] = 1.0
        
        # Normalize
        degrees = adj.sum(dim=1, keepdim=True)
        degrees[degrees == 0] = 1
        adj = adj / degrees
        
        # Power iteration
        x = torch.ones(num_nodes) / np.sqrt(num_nodes)
        for _ in range(num_iter):
            x = adj.T @ x
            x = x / (torch.norm(x) + 1e-6)
        
        return x
    
    @staticmethod
    def pagerank(edge_index: torch.Tensor, num_nodes: int, alpha: float = 0.15, num_iter: int = 10) -> torch.Tensor:
        """PageRank for importance scoring."""
        # Build adjacency
        adj = torch.zeros(num_nodes, num_nodes)
        adj[edge_index[0], edge_index[1]] = 1.0
        
        # Normalize by out-degree
        out_degree = adj.sum(dim=1, keepdim=True)
        out_degree[out_degree == 0] = 1
        adj = adj / out_degree
        
        # PageRank iteration
        pr = torch.ones(num_nodes) / num_nodes
        for _ in range(num_iter):
            pr = alpha / num_nodes + (1 - alpha) * (adj.T @ pr)
        
        return pr


class GNNPortfolio(nn.Module):
    """
    Graph Neural Network for infrastructure portfolio risk analysis.
    
    Mock Input/Output:
    - Nodes: (num_projects, 10) -> [risk_score, budget, duration, criticality, completion%, ...]
    - Edges: (num_dependencies, 2) -> [source_project, target_project]
    - Output: (num_projects, 1) -> risk_impact after propagation
    
    Architecture:
    - Project nodes with features
    - Dependency edges with weights
    - Message passing for risk contagion
    - Centrality metrics for vulnerability
    """
    
    def __init__(
        self,
        num_features: int = 10,
        hidden_dim: int = 64,
        num_layers: int = 3,
        num_projects_max: int = 100
    ):
        super(GNNPortfolio, self).__init__()
        
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Input embedding
        self.input_embedding = nn.Linear(num_features, hidden_dim)
        
        # GNN layers with risk propagation
        self.gnn_layers = nn.ModuleList([
            RiskPropagationLayer(hidden_dim, hidden_dim)
            for _ in range(num_layers)
        ])
        
        # Attention mechanism for edge importance
        self.edge_attention = nn.Sequential(
            nn.Linear(2 * hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        # Risk aggregation head
        self.risk_head = nn.Sequential(
            nn.Linear(hidden_dim * (num_layers + 1), 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
        
        self.centrality_cache = {}
    
    def forward(
        self,
        node_features: torch.Tensor,
        edge_index: torch.Tensor,
        edge_weight: Optional[torch.Tensor] = None,
        compute_centrality: bool = True
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass with risk propagation.
        
        Args:
            node_features: (num_nodes, num_features)
            edge_index: (2, num_edges)
            edge_weight: (num_edges,) optional edge weights
            compute_centrality: Compute centrality metrics
            
        Returns:
            Dict with 'risk_scores', 'propagated_risk', 'centrality_metrics'
        """
        num_nodes = node_features.shape[0]
        
        # Embed node features
        x = self.input_embedding(node_features)  # (num_nodes, hidden_dim)
        
        # Store layer outputs for risk aggregation
        layer_outputs = [x]
        
        # Risk propagation through GNN layers
        for gnn_layer in self.gnn_layers:
            # Compute edge weights if not provided
            if edge_weight is None:
                edge_weight = self._compute_edge_weights(x, edge_index)
            
            x = gnn_layer(x, edge_index, edge_weight)
            x = torch.relu(x)
            layer_outputs.append(x)
        
        # Aggregate layer outputs
        aggregated = torch.cat(layer_outputs, dim=1)
        
        # Final risk scoring
        risk_scores = self.risk_head(aggregated)  # (num_nodes, 1)
        
        result = {
            'risk_scores': risk_scores,
            'node_embeddings': x,
            'edge_weights': edge_weight if edge_weight is not None else torch.ones(edge_index.shape[1])
        }
        
        if compute_centrality:
            centrality_metrics = self._compute_centrality_metrics(edge_index, num_nodes)
            result['centrality_metrics'] = centrality_metrics
        
        return result
    
    def _compute_edge_weights(self, node_features: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Compute edge weights using attention mechanism."""
        num_edges = edge_index.shape[1]
        edge_weights = []
        
        for i in range(num_edges):
            src, dst = edge_index[0, i], edge_index[1, i]
            src_feat = node_features[src]
            dst_feat = node_features[dst]
            combined = torch.cat([src_feat, dst_feat])
            
            weight = self.edge_attention(combined)
            edge_weights.append(weight)
        
        return torch.cat(edge_weights)
    
    def _compute_centrality_metrics(self, edge_index: torch.Tensor, num_nodes: int) -> Dict[str, torch.Tensor]:
        """Compute multiple centrality metrics."""
        return {
            'betweenness': CentralityMetrics.betweenness_centrality(edge_index, num_nodes),
            'eigenvector': CentralityMetrics.eigenvector_centrality(edge_index, num_nodes),
            'pagerank': CentralityMetrics.pagerank(edge_index, num_nodes)
        }
    
    def cascade_failure_analysis(
        self,
        node_features: torch.Tensor,
        edge_index: torch.Tensor,
        failure_node: int
    ) -> Dict[str, torch.Tensor]:
        """
        Analyze cascade failure when a critical node fails.
        """
        num_nodes = node_features.shape[0]
        
        # Create synthetic graph without failed node
        mask = torch.ones(num_nodes, dtype=torch.bool)
        mask[failure_node] = False
        
        # Forward pass
        output = self.forward(node_features, edge_index, compute_centrality=False)
        
        original_risk = output['risk_scores']
        
        # Simulate node removal
        node_features_reduced = node_features[mask]
        edge_index_reduced = edge_index[:, (edge_index[0] != failure_node) & (edge_index[1] != failure_node)]
        
        # Reindex edges
        idx_map = torch.full((num_nodes,), -1, dtype=torch.long)
        idx_map[mask] = torch.arange(mask.sum())
        edge_index_reduced = idx_map[edge_index_reduced]
        
        if edge_index_reduced.shape[1] > 0:
            output_reduced = self.forward(node_features_reduced, edge_index_reduced, compute_centrality=False)
            risk_after = torch.zeros_like(original_risk)
            risk_after[mask] = output_reduced['risk_scores']
        else:
            risk_after = torch.zeros_like(original_risk)
        
        # Compute cascade effect
        risk_increase = (risk_after - original_risk).abs()
        
        return {
            'original_risk': original_risk,
            'risk_after_failure': risk_after,
            'cascade_effect': risk_increase,
            'critical_nodes': (risk_increase > 0.1).squeeze()
        }
    
    def visualize_importance_ranking(self, centrality_metrics: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Rank projects by importance using ensemble of centrality metrics."""
        ensemble_rank = (
            centrality_metrics['betweenness'] +
            centrality_metrics['eigenvector'] +
            centrality_metrics['pagerank']
        ) / 3.0
        
        return torch.argsort(ensemble_rank, descending=True)


class PortfolioLoss(nn.Module):
    """Loss for portfolio risk prediction."""
    
    def __init__(self):
        super(PortfolioLoss, self).__init__()
        self.mse_loss = nn.MSELoss()
    
    def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> Tuple[torch.Tensor, Dict]:
        """Compute loss."""
        loss = self.mse_loss(predictions, targets)
        return loss, {'loss': loss.item()}


if __name__ == "__main__":
    model = GNNPortfolio(num_features=10, hidden_dim=64, num_layers=3)
    
    # Mock portfolio: 20 projects with 10 features each
    num_projects = 20
    num_features = 10
    node_features = torch.randn(num_projects, num_features)
    
    # Mock dependencies: 30 random edges
    num_edges = 30
    edge_index = torch.randint(0, num_projects, (2, num_edges))
    
    # Forward pass
    output = model(node_features, edge_index, compute_centrality=True)
    
    assert output['risk_scores'].shape == (num_projects, 1)
    assert output['edge_weights'].shape[0] == num_edges
    assert 'betweenness' in output['centrality_metrics']
    
    # Test cascade failure
    cascade = model.cascade_failure_analysis(node_features, edge_index, failure_node=0)
    assert cascade['original_risk'].shape == (num_projects, 1)
    assert cascade['cascade_effect'].shape == (num_projects, 1)
    
    # Test ranking
    ranking = model.visualize_importance_ranking(output['centrality_metrics'])
    assert ranking.shape[0] == num_projects
    
    print("✓ GNNPortfolio architecture validation passed")
    print(f"  Risk scores shape: {output['risk_scores'].shape}")
    print(f"  Centrality metrics computed: {list(output['centrality_metrics'].keys())}")
    print(f"  Top 3 important projects: {ranking[:3].tolist()}")
