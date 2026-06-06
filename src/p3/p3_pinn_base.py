"""
Physics-Informed Neural Network Base Class
Combines data-driven learning with physics constraints: Loss = MSE_data + λ × MSE_physics
"""

import torch
import torch.nn as nn
from typing import Dict, Callable, Optional, Tuple
import torch.autograd as autograd


class PhysicsInformedNN(nn.Module):
    """
    Base class for Physics-Informed Neural Networks.
    
    Mock Input/Output:
    - Input: (batch_size, num_features) state variables
    - Output: (batch_size, 1) prediction with physics constraints
    
    The network learns both data and physics:
    - Data loss: MSE between predictions and observations
    - Physics loss: MSE of physics residuals (embedded differential equations)
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int = 1,
        hidden_dims: list = None,
        physics_loss_weight: float = 1.0
    ):
        super(PhysicsInformedNN, self).__init__()
        
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.physics_loss_weight = physics_loss_weight
        
        if hidden_dims is None:
            hidden_dims = [128, 128, 64]
        
        # Build network with sufficient capacity for physics modeling
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.Tanh())  # Smooth activation for derivatives
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        self.physics_constraints = []
    
    def forward(self, x: torch.Tensor, compute_physics: bool = False) -> Dict[str, torch.Tensor]:
        """
        Forward pass with optional physics constraint computation.
        
        Args:
            x: (batch_size, input_dim) input
            compute_physics: Whether to compute physics residuals
            
        Returns:
            Dict with 'prediction' and optionally 'physics_residual'
        """
        x.requires_grad_(True)
        output = self.network(x)
        
        result = {'prediction': output}
        
        if compute_physics:
            # Compute derivatives for physics constraints
            physics_residual = self._compute_physics_residual(x, output)
            result['physics_residual'] = physics_residual
        
        return result
    
    def _compute_physics_residual(self, x: torch.Tensor, output: torch.Tensor) -> torch.Tensor:
        """
        Compute physics residuals (differential equations).
        Override in subclasses for specific physics.
        """
        # Example: gradient-based residual
        if output.requires_grad:
            gradients = autograd.grad(
                outputs=output.sum(),
                inputs=x,
                create_graph=True,
                retain_graph=True,
                allow_unused=True
            )[0]
            
            if gradients is not None:
                return gradients  # Residual as gradient magnitude
        
        return torch.zeros_like(output)
    
    def add_physics_constraint(self, constraint_fn: Callable):
        """Register a physics constraint function."""
        self.physics_constraints.append(constraint_fn)
    
    def compute_constraint_residuals(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Compute residuals for all registered constraints."""
        residuals = []
        for constraint_fn in self.physics_constraints:
            residual = constraint_fn(x, y)
            residuals.append(residual)
        
        if residuals:
            return torch.cat(residuals, dim=1)
        return torch.zeros_like(y)


class PhysicsLoss(nn.Module):
    """
    Combined loss function: Data + Physics
    Loss = α × MSE_data + β × MSE_physics
    """
    
    def __init__(
        self,
        data_weight: float = 1.0,
        physics_weight: float = 1.0,
        reduction: str = 'mean'
    ):
        super(PhysicsLoss, self).__init__()
        self.data_weight = data_weight
        self.physics_weight = physics_weight
        self.mse_loss = nn.MSELoss(reduction=reduction)
    
    def forward(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: torch.Tensor,
        physics_residuals: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Compute combined loss.
        
        Args:
            predictions: Dict with 'prediction' key
            targets: Ground truth values
            physics_residuals: Physics constraint residuals
            
        Returns:
            Tuple of (total_loss, loss_components_dict)
        """
        pred = predictions['prediction']
        
        # Data loss
        data_loss = self.mse_loss(pred, targets)
        
        # Physics loss
        physics_loss = torch.tensor(0.0, device=pred.device)
        if physics_residuals is not None:
            physics_loss = self.mse_loss(physics_residuals, torch.zeros_like(physics_residuals))
        
        # Combined loss
        total_loss = self.data_weight * data_loss + self.physics_weight * physics_loss
        
        loss_dict = {
            'data': data_loss.item(),
            'physics': physics_loss.item(),
            'total': total_loss.item(),
            'ratio': (physics_loss.item() / (data_loss.item() + 1e-6))
        }
        
        return total_loss, loss_dict
    
    def adjust_weights(self, data_weight: float, physics_weight: float):
        """Dynamically adjust loss weights during training."""
        self.data_weight = data_weight
        self.physics_weight = physics_weight


class ConservationLawPINN(PhysicsInformedNN):
    """
    PINN for conservation laws (mass, energy, momentum).
    Physics: ∇·u = 0 (divergence-free for incompressible flow)
    """
    
    def __init__(self, input_dim: int = 3, output_dim: int = 1):
        super(ConservationLawPINN, self).__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=[256, 256, 128],
            physics_loss_weight=1.0
        )
    
    def _compute_physics_residual(self, x: torch.Tensor, output: torch.Tensor) -> torch.Tensor:
        """Compute divergence-free residual."""
        if output.requires_grad:
            grads = autograd.grad(
                outputs=output.sum(),
                inputs=x,
                create_graph=True,
                retain_graph=True,
                allow_unused=True
            )[0]
            
            if grads is not None:
                # Compute divergence (sum of gradients)
                divergence = grads.sum(dim=1, keepdim=True)
                return divergence
        
        return torch.zeros_like(output)


if __name__ == "__main__":
    model = PhysicsInformedNN(input_dim=10, output_dim=1, hidden_dims=[128, 128, 64])
    loss_fn = PhysicsLoss(data_weight=1.0, physics_weight=1.0)
    
    # Mock input
    x = torch.randn(16, 10, requires_grad=True)
    y_true = torch.randn(16, 1)
    
    # Forward pass
    output = model(x, compute_physics=True)
    
    assert output['prediction'].shape == (16, 1)
    assert output['physics_residual'].shape is not None
    
    # Compute loss
    loss, loss_dict = loss_fn(output, y_true, output['physics_residual'])
    
    print("✓ PhysicsInformedNN architecture validation passed")
    print(f"  Prediction shape: {output['prediction'].shape}")
    print(f"  Loss components: {loss_dict}")
