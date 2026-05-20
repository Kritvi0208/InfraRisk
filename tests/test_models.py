"""Unit tests for models"""
import pytest
import torch
from src.models.ensemble import MetaLearner
from src.models.tft import TemporalFusionTransformer
from src.models.cnn import ConstructionMonitorCNN

def test_meta_learner():
    model = MetaLearner(num_base_models=5)
    x = torch.randn(4, 5)
    out = model(x)
    assert out.shape == (4, 1)
    assert (out >= 0).all() and (out <= 1).all()

def test_tft():
    model = TemporalFusionTransformer(input_dim=32, output_dim=7)
    x = torch.randn(4, 10, 32)  # batch, seq_len, features
    out = model(x)
    assert out.shape == (4, 7)

def test_cnn():
    model = ConstructionMonitorCNN(input_channels=13)
    x = torch.randn(4, 13, 256, 256)  # batch, channels, height, width
    out = model(x)
    assert out.shape == (4, 1)
    assert (out >= 0).all() and (out <= 1).all()
