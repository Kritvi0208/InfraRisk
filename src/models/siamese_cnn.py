"""Siamese CNN with ResNet-50 backbone.

For multi-temporal satellite change detection.
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Tuple

class SiameseCNN(nn.Module):
    """ResNet-50 with 3 heads: regression (progress), classification (phase), anomaly."""
    
    def __init__(self, pretrained=True):
        super(SiameseCNN, self).__init__()
        self.backbone = models.resnet50(pretrained=pretrained)
        self.backbone.fc = nn.Identity()
        
        # Head 1: Progress estimation (MAPE < 15%)
        self.regression_head = nn.Sequential(
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 1),
            nn.Sigmoid(),
        )
        
        # Head 2: Construction phase (multinomial)
        self.classification_head = nn.Sequential(
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Linear(512, 5),  # Phases: Planning, Procurement, Construction, Testing, Operational
        )
        
        # Head 3: Anomaly detection
        self.anomaly_head = nn.Sequential(
            nn.Linear(2048, 256),
            nn.ReLU(),
            nn.Linear(256, 3),  # Classes: Normal, Abandoned, Equipment Removed
        )
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        features = self.backbone(x)
        progress = self.regression_head(features)
        phase = self.classification_head(features)
        anomaly = self.anomaly_head(features)
        return progress, phase, anomaly
