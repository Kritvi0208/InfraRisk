# Graph Neural Network for Portfolio Risk - Full Implementation

import torch
import torch.nn as nn
from typing import Dict, List

class ProjectGNNNode(nn.Module):
    def __init__(self, node_features=25, hidden_dim=64):
        super().__init__()
        self.node_embedding = nn.Linear(node_features, hidden_dim)
        self.message_network = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.update_network = nn.GRUCell(hidden_dim, hidden_dim)

    def forward(self, node_features, edge_list, edge_weights):
        embeddings = self.node_embedding(node_features)
        for src, dst in edge_list:
            message = self.message_network(
                torch.cat([embeddings[src], embeddings[dst]], dim=-1)
            )
            embeddings[dst] = self.update_network(message, embeddings[dst])
        return embeddings

class PortfolioGNN(nn.Module):
    def __init__(self, node_features=25, hidden_dim=64):
        super().__init__()
        self.gnn = ProjectGNNNode(node_features, hidden_dim)
        self.risk_head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.contagion_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, projects, dependencies):
        embeddings = self.gnn(projects, dependencies['edges'], dependencies['weights'])
        project_risks = self.risk_head(embeddings)
        return {
            'project_risks': project_risks,
            'embeddings': embeddings
        }

    def compute_contagion(self, embeddings, edge_list):
        contagion_matrix = []
        for src, dst in edge_list:
            combined = torch.cat([embeddings[src], embeddings[dst]], dim=-1)
            contagion = self.contagion_head(combined)
            contagion_matrix.append(contagion)
        return torch.stack(contagion_matrix)
