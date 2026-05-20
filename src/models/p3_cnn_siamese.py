# Siamese CNN for Satellite Change Detection - Full Implementation

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class SiameseCNN(nn.Module):
    def __init__(self, input_channels=13):
        super().__init__()
        self.feature_extractor = nn.Sequential(
            nn.Conv2d(input_channels, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.progress_head = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        self.phase_classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 6)  # 6 construction phases
        )
        self.anomaly_detector = nn.Sequential(
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, 3)  # abandonment, equipment removal, scope change
        )

    def forward(self, before_image, current_image):
        before_features = self.feature_extractor(before_image).view(before_image.size(0), -1)
        current_features = self.feature_extractor(current_image).view(current_image.size(0), -1)
        delta = current_features - before_features
        progress = self.progress_head(delta)
        phase = self.phase_classifier(current_features)
        anomaly = self.anomaly_detector(delta)
        return {
            'progress': progress,
            'construction_phase': phase,
            'anomalies': anomaly
        }
