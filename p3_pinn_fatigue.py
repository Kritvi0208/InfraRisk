"""
Physics-Informed NN for Fatigue Crack Growth
Embeds Paris Law: da/dN = C(ΔK)^m into PINN loss
Bridge fatigue modeling with stress cycle processing
"""

import torch
import torch.nn as nn
import torch.autograd as autograd
from typing import Dict, Tuple, Optional
import numpy as np


class ParisMaterial:
    """
    Paris Law material properties for fatigue crack growth.
    da/dN = C(ΔK)^m
    """
    
    def __init__(self, material_name: str = "steel", C: float = 1e-11, m: float = 3.0):
        self.material_name = material_name
        self.C = C  # Paris constant
        self.m = m  # Paris exponent
        
        # Material-specific parameters
        self.E = 210e9  # Young's modulus (Pa)
        self.nu = 0.3  # Poisson ratio
        self.K_IC = 50e6  # Fracture toughness (Pa√m)
    
    def stress_intensity_factor(self, stress: torch.Tensor, crack_length: torch.Tensor) -> torch.Tensor:
        """Compute stress intensity factor K = Y * σ * √(πa)."""
        Y = 1.12  # Shape factor for edge crack
        return Y * stress * torch.sqrt(np.pi * crack_length)
    
    def delta_K(self, max_stress: torch.Tensor, min_stress: torch.Tensor, crack_length: torch.Tensor) -> torch.Tensor:
        """Stress intensity range ΔK = K_max - K_min."""
        K_max = self.stress_intensity_factor(max_stress, crack_length)
        K_min = self.stress_intensity_factor(min_stress, crack_length)
        return K_max - K_min
    
    def paris_law(self, delta_K: torch.Tensor) -> torch.Tensor:
        """Paris Law: da/dN = C(ΔK)^m."""
        return self.C * torch.pow(delta_K, self.m)


class PINNFatigue(nn.Module):
    """
    Physics-Informed NN for fatigue crack growth prediction.
    
    Mock Input/Output:
    - Input: (batch_size, 5) -> [initial_crack_mm, max_stress, min_stress, cycles, material_id]
    - Output: (batch_size, 1) -> final_crack_length_mm
    
    Physics constraint: Embed Paris Law into loss function
    Loss = MSE_data + λ × MSE_paris_law
    """
    
    def __init__(
        self,
        hidden_dims: list = None,
        num_materials: int = 1,
        physics_weight: float = 1.0
    ):
        super(PINNFatigue, self).__init__()
        
        self.physics_weight = physics_weight
        self.num_materials = num_materials
        
        if hidden_dims is None:
            hidden_dims = [256, 256, 128, 64]
        
        # Neural network for crack growth prediction
        layers = []
        input_dim = 5
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.Tanh())
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, 1))  # Output: final crack length
        
        self.network = nn.Sequential(*layers)
        
        # Material properties for each class
        self.materials = [
            ParisMaterial(material_name="steel", C=1e-11, m=3.0),
            ParisMaterial(material_name="aluminum", C=2e-10, m=2.8),
            ParisMaterial(material_name="titanium", C=5e-12, m=3.2)
        ][:num_materials]
    
    def forward(self, x: torch.Tensor, compute_physics: bool = False) -> Dict[str, torch.Tensor]:
        """
        Forward pass with optional physics residual computation.
        
        Args:
            x: (batch_size, 5) -> [initial_crack, max_stress, min_stress, cycles, material_id]
            compute_physics: Compute Paris Law residuals
            
        Returns:
            Dict with 'prediction' and optionally 'physics_residual'
        """
        x_orig = x.clone()
        x.requires_grad_(True)
        
        # Predict final crack length
        output = self.network(x)
        
        result = {'prediction': output}
        
        if compute_physics:
            # Extract input components
            initial_crack = x_orig[:, 0:1]
            max_stress = x_orig[:, 1:2]
            min_stress = x_orig[:, 2:3]
            num_cycles = x_orig[:, 3:4]
            material_id = x_orig[:, 4:5].long()
            
            # Compute physics residuals
            physics_residual = self._compute_paris_residual(
                initial_crack, output, max_stress, min_stress, num_cycles, material_id
            )
            result['physics_residual'] = physics_residual
        
        return result
    
    def _compute_paris_residual(
        self,
        a_initial: torch.Tensor,
        a_final: torch.Tensor,
        max_stress: torch.Tensor,
        min_stress: torch.Tensor,
        num_cycles: torch.Tensor,
        material_id: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute Paris Law residual.
        Residual = |Δa_predicted - Δa_paris|
        """
        batch_size = a_initial.shape[0]
        residuals = []
        
        for i in range(batch_size):
            mat_idx = min(int(material_id[i].item()), len(self.materials) - 1)
            material = self.materials[mat_idx]
            
            # Average crack length during growth
            a_avg = (a_initial[i] + a_final[i]) / 2
            
            # Stress intensity range
            delta_K = material.delta_K(max_stress[i], min_stress[i], a_avg)
            
            # Predicted crack growth via Paris Law
            da_dN = material.paris_law(delta_K)
            da_predicted_paris = da_dN * num_cycles[i]
            
            # Actual prediction from network
            da_predicted_nn = a_final[i] - a_initial[i]
            
            # Residual
            residual = da_predicted_nn - da_predicted_paris
            residuals.append(residual)
        
        return torch.stack(residuals)
    
    def predict_safe_life(self, x: torch.Tensor, a_critical: float = 10.0) -> torch.Tensor:
        """
        Predict safe life (number of cycles before critical crack length).
        Binary search for critical cycle count.
        """
        initial_crack = x[:, 0]
        max_stress = x[:, 1]
        min_stress = x[:, 2]
        material_id = x[:, 4].long()
        
        safe_lives = []
        for i in range(x.shape[0]):
            material = self.materials[min(int(material_id[i].item()), len(self.materials) - 1)]
            delta_K = material.delta_K(max_stress[i], min_stress[i], initial_crack[i])
            da_dN = material.paris_law(delta_K)
            
            if da_dN.item() > 0:
                safe_life = (a_critical - initial_crack[i].item()) / da_dN.item()
            else:
                safe_life = float('inf')
            
            safe_lives.append(safe_life)
        
        return torch.tensor(safe_lives)
    
    def batch_process_stress_cycles(self, x: torch.Tensor, num_steps: int = 10) -> Dict[str, torch.Tensor]:
        """
        Process multiple stress cycles with intermediate predictions.
        
        Returns:
            Dict with:
            - 'trajectory': (batch_size, num_steps) crack growth trajectory
            - 'final_prediction': (batch_size, 1) final crack length
        """
        batch_size = x.shape[0]
        trajectory = []
        
        current_x = x.clone()
        for step in range(num_steps):
            output = self.network(current_x)
            trajectory.append(output)
            
            # Update cycles for next iteration
            current_x[:, 3] *= 0.9  # Reduce cycles for next step
        
        trajectory = torch.cat(trajectory, dim=1)  # (batch_size, num_steps)
        
        final_output = self.network(x)
        
        return {
            'trajectory': trajectory,
            'final_prediction': final_output
        }


class FatigueLoss(nn.Module):
    """Loss function combining data and Paris Law physics."""
    
    def __init__(self, data_weight: float = 1.0, physics_weight: float = 1.0):
        super(FatigueLoss, self).__init__()
        self.data_weight = data_weight
        self.physics_weight = physics_weight
        self.mse_loss = nn.MSELoss()
    
    def forward(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: torch.Tensor,
        physics_residuals: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict]:
        """Compute combined loss."""
        pred = predictions['prediction']
        data_loss = self.mse_loss(pred, targets)
        
        physics_loss = torch.tensor(0.0, device=pred.device)
        if physics_residuals is not None:
            physics_loss = self.mse_loss(physics_residuals, torch.zeros_like(physics_residuals))
        
        total_loss = self.data_weight * data_loss + self.physics_weight * physics_loss
        
        return total_loss, {
            'data': data_loss.item(),
            'physics': physics_loss.item(),
            'total': total_loss.item()
        }


if __name__ == "__main__":
    model = PINNFatigue(hidden_dims=[256, 256, 128, 64], num_materials=3)
    loss_fn = FatigueLoss(data_weight=1.0, physics_weight=1.0)
    
    # Mock input: [initial_crack, max_stress, min_stress, cycles, material_id]
    x = torch.tensor([
        [2.0, 300e6, 100e6, 1000, 0.0],
        [1.5, 350e6, 120e6, 1500, 1.0],
        [3.0, 280e6, 90e6, 800, 2.0],
        [2.5, 320e6, 110e6, 1200, 0.0]
    ])
    
    y_true = torch.tensor([[5.0], [4.2], [6.5], [5.8]])
    
    output = model(x, compute_physics=True)
    assert output['prediction'].shape == (4, 1)
    assert output['physics_residual'].shape == (4, 1)
    
    loss, loss_dict = loss_fn(output, y_true, output['physics_residual'])
    
    # Test trajectory
    trajectory = model.batch_process_stress_cycles(x, num_steps=10)
    assert trajectory['trajectory'].shape == (4, 10)
    assert trajectory['final_prediction'].shape == (4, 1)
    
    # Test safe life prediction
    safe_lives = model.predict_safe_life(x, a_critical=10.0)
    assert safe_lives.shape == (4,)
    
    print("✓ PINNFatigue architecture validation passed")
    print(f"  Prediction shape: {output['prediction'].shape}")
    print(f"  Physics residual: {output['physics_residual'].shape}")
    print(f"  Loss: {loss_dict}")
