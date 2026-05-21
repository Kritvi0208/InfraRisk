"""
Siamese CNN with Multi-Head Architecture
ResNet-50 backbone with 3 heads: regression, classification, anomaly detection
"""

from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import resnet50


class SiameseCNN(nn.Module):
    """
    Siamese CNN with ResNet-50 backbone and multi-head architecture.

    Mock Input/Output:
    - Input: (batch_size, 3, 224, 224) RGB images
    - Output regression: (batch_size, 1) -> float 0-100 (construction progress %)
    - Output classification: (batch_size, 5) -> 5-class softmax (construction phases)
    - Output anomaly: (batch_size, 1) -> sigmoid (site abandonment)

    Args:
        backbone_pretrained: Use pretrained ResNet-50 weights (bool)
        freeze_backbone: Freeze backbone during training (bool)
        head_dim: Hidden dimension for head MLPs (int)
    """

    def __init__(
        self,
        backbone_pretrained: bool = True,
        freeze_backbone: bool = False,
        head_dim: int = 512,
    ):
        super(SiameseCNN, self).__init__()

        # ResNet-50 backbone
        self.backbone = resnet50(pretrained=backbone_pretrained)
        backbone_out_dim = self.backbone.fc.in_features

        # Remove classification head
        self.backbone = nn.Sequential(*list(self.backbone.children())[:-1])
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        # Regression head: construction progress (0-100%)
        self.regression_head = nn.Sequential(
            nn.Linear(backbone_out_dim, head_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(head_dim, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid(),
        )

        # Classification head: 5 construction phases
        self.classification_head = nn.Sequential(
            nn.Linear(backbone_out_dim, head_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(head_dim, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 5),
        )

        # Anomaly detection head: binary (site abandonment)
        self.anomaly_head = nn.Sequential(
            nn.Linear(backbone_out_dim, head_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(head_dim, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 1),
            nn.Sigmoid(),
        )

    def forward(
        self, x: torch.Tensor, return_features: bool = False
    ) -> Dict[str, torch.Tensor]:
        """Forward pass through all three heads."""
        features = self.backbone(x)
        features = self.global_pool(features)
        features = features.view(features.size(0), -1)

        regression_out = self.regression_head(features) * 100
        classification_out = self.classification_head(features)
        anomaly_out = self.anomaly_head(features)

        output = {
            "regression": regression_out,
            "classification": classification_out,
            "anomaly": anomaly_out,
        }

        if return_features:
            output["features"] = features

        return output

    def _extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract backbone features."""
        features = self.backbone(x)
        features = self.global_pool(features)
        features = features.view(features.size(0), -1)
        return features


class SiameseLoss(nn.Module):
    """Combined loss for Siamese multi-head CNN."""

    def __init__(self, alpha: float = 0.4, beta: float = 0.4, gamma: float = 0.2):
        super(SiameseLoss, self).__init__()
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.regression_loss = nn.MSELoss()
        self.classification_loss = nn.CrossEntropyLoss()
        self.anomaly_loss = nn.BCELoss()

    def forward(
        self, predictions: Dict[str, torch.Tensor], targets: Dict[str, torch.Tensor]
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Compute combined loss."""
        reg_loss = self.regression_loss(
            predictions["regression"] / 100, targets["regression"] / 100
        )
        clf_loss = self.classification_loss(
            predictions["classification"], targets["classification"].long()
        )
        anom_loss = self.anomaly_loss(
            predictions["anomaly"], targets["anomaly"].float()
        )

        total_loss = (
            self.alpha * reg_loss + self.beta * clf_loss + self.gamma * anom_loss
        )

        loss_dict = {
            "regression": reg_loss.item(),
            "classification": clf_loss.item(),
            "anomaly": anom_loss.item(),
            "total": total_loss.item(),
        }

        return total_loss, loss_dict


if __name__ == "__main__":
    model = SiameseCNN(backbone_pretrained=False, head_dim=512)
    x = torch.randn(4, 3, 224, 224)
    outputs = model(x, return_features=True)
    assert outputs["regression"].shape == (4, 1)
    assert outputs["classification"].shape == (4, 5)
    assert outputs["anomaly"].shape == (4, 1)
    print("✓ SiameseCNN architecture validation passed")
