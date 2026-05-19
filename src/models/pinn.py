"""Physics-Informed Neural Networks (PINN).

Base PINN class and specialized variants for infrastructure physics.
"""

import torch
import torch.nn as nn
from typing import Callable

class PINNBase(nn.Module):
    """Base PINN with physics constraints in loss function."""
    
    def __init__(self, input_size=2, hidden_size=128, output_size=1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
    
    def physics_loss(self, x: torch.Tensor, physics_fn: Callable) -> torch.Tensor:
        """Enforce physics through loss."""
        y = self.forward(x)
        y.requires_grad_(True)
        dy_dx = torch.autograd.grad(y.sum(), x, create_graph=True)[0]
        physics_residual = physics_fn(x, y, dy_dx)
        return (physics_residual ** 2).mean()

class PINNBridgeFatigue(PINNBase):
    """PINN for bridge fatigue with Paris' Law: da/dN = C(\u0394K)^m."""
    
    def __init__(self):
        super().__init__(input_size=2, hidden_size=256)  # Input: stress_range, num_cycles
        self.C = 1.0e-11  # Paris law coefficient
        self.m = 3.0  # Paris law exponent
    
    def physics_loss(self, x: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
        """Paris law: da/dN = C(\u0394K)^m."""
        stress_range = x[:, 0]
        K = 1.12 * stress_range * torch.sqrt(torch.pi * a)
        da_dN_expected = self.C * (K ** self.m)
        return ((a - da_dN_expected) ** 2).mean()

class PINNPavementAASTHO(PINNBase):
    """PINN for pavement with AASHTO degradation model."""
    
    def __init__(self):
        super().__init__(input_size=3, hidden_size=256)  # Input: SN, traffic, climate
    
    def physics_loss(self, x: torch.Tensor, psi: torch.Tensor) -> torch.Tensor:
        """AASHTO PSI decline constrained."""
        # Structural number (SN), cumulative traffic (ESALs), climate factor
        sn, esals, climate = x[:, 0], x[:, 1], x[:, 2]
        psi_predicted = 4.2 - 0.001 * esals / (sn ** 1.3) * (1 + climate)
        return ((psi - psi_predicted) ** 2).mean()
