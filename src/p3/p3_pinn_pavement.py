"""
Physics-Informed NN for Pavement Degradation
AASHTO model: PSI_remaining = PSI_0 × (1 - traffic_norm ^ n)
Structural number and environmental effects
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple, Optional
import numpy as np


class AAshtoPSIModel:
    """
    AASHTO pavement present serviceability index model.
    PSI_remaining = PSI_0 * (1 - (traffic / capacity)^n)
    Also includes environmental degradation factor.
    """
    
    def __init__(
        self,
        PSI_0: float = 4.5,  # Initial serviceability
        PSI_terminal: float = 1.5,  # Terminal serviceability
        SN: float = 5.0  # Structural number
    ):
        self.PSI_0 = PSI_0
        self.PSI_terminal = PSI_terminal
        self.SN = SN  # Structural number (material/thickness)
        
        # Environmental parameters
        self.freeze_thaw_factor = 1.0
        self.moisture_factor = 1.0
        self.temperature_factor = 1.0
    
    def traffic_damage_factor(
        self,
        traffic_normalized: torch.Tensor,
        structural_number: torch.Tensor,
        exponent: float = 1.5
    ) -> torch.Tensor:
        """
        Compute damage from traffic.
        damage_factor = (traffic / SN) ^ exponent
        """
        return torch.pow(traffic_normalized / (structural_number + 1e-6), exponent)
    
    def environmental_degradation(
        self,
        temperature: torch.Tensor,
        precipitation: torch.Tensor,
        freeze_cycles: torch.Tensor
    ) -> torch.Tensor:
        """
        Environmental degradation factor.
        Combined effect of temperature, moisture, and freeze-thaw.
        """
        # Temperature effect (normalized)
        temp_effect = 1.0 + 0.01 * torch.clamp(temperature - 20, 0, 40) / 40
        
        # Moisture effect
        moisture_effect = 1.0 + 0.02 * torch.clamp(precipitation, 0, 2000) / 2000
        
        # Freeze-thaw effect
        freeze_effect = 1.0 + 0.05 * torch.clamp(freeze_cycles, 0, 100) / 100
        
        return temp_effect * moisture_effect * freeze_effect
    
    def compute_psi(
        self,
        traffic_normalized: torch.Tensor,
        structural_number: torch.Tensor,
        temperature: torch.Tensor,
        precipitation: torch.Tensor,
        freeze_cycles: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute remaining pavement serviceability index.
        PSI_remaining = PSI_0 * (1 - damage_factor * env_factor)
        """
        traffic_damage = self.traffic_damage_factor(traffic_normalized, structural_number, exponent=1.5)
        env_factor = self.environmental_degradation(temperature, precipitation, freeze_cycles)
        
        # Combined degradation
        degradation = torch.clamp(traffic_damage * env_factor, 0, 1)
        
        # Remaining PSI
        psi_remaining = self.PSI_0 * (1.0 - degradation)
        
        # Ensure minimum terminal PSI
        psi_remaining = torch.clamp(psi_remaining, self.PSI_terminal, self.PSI_0)
        
        return psi_remaining


class PINNPavement(nn.Module):
    """
    Physics-Informed NN for pavement degradation prediction.
    
    Mock Input/Output:
    - Input: (batch_size, 7) -> [initial_PSI, traffic_volume, SN, temp, precip, freeze_cycles, age_years]
    - Output: (batch_size, 1) -> remaining_PSI [1.5, 4.5]
    
    Physics constraint: AASHTO degradation model
    Loss = MSE_data + λ × MSE_aashto
    """
    
    def __init__(
        self,
        hidden_dims: list = None,
        physics_weight: float = 1.0
    ):
        super(PINNPavement, self).__init__()
        
        self.physics_weight = physics_weight
        
        if hidden_dims is None:
            hidden_dims = [256, 256, 128]
        
        # Neural network for PSI prediction
        layers = []
        input_dim = 7
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.Tanh())
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, 1))  # Output: remaining PSI
        
        self.network = nn.Sequential(*layers)
        
        # AASHTO model instance
        self.aashto = AAshtoPSIModel(PSI_0=4.5, PSI_terminal=1.5, SN=5.0)
    
    def forward(self, x: torch.Tensor, compute_physics: bool = False) -> Dict[str, torch.Tensor]:
        """
        Forward pass with optional AASHTO physics residual.
        
        Args:
            x: (batch_size, 7) -> [PSI_0, traffic, SN, temp, precip, freeze, age]
            compute_physics: Compute AASHTO model residuals
            
        Returns:
            Dict with 'prediction' and optionally 'physics_residual'
        """
        # Clamp output to valid PSI range
        output = self.network(x)
        output = torch.clamp(output, 1.5, 4.5)
        
        result = {'prediction': output}
        
        if compute_physics:
            # Extract input components
            psi_0 = x[:, 0:1]
            traffic = x[:, 1:2]
            SN = x[:, 2:3]
            temp = x[:, 3:4]
            precip = x[:, 4:5]
            freeze_cycles = x[:, 5:6]
            
            # Normalize traffic (0-1)
            traffic_normalized = torch.clamp(traffic / 10000, 0, 1)
            
            # Compute AASHTO model prediction
            psi_aashto = self.aashto.compute_psi(
                traffic_normalized, SN, temp, precip, freeze_cycles
            )
            
            # Physics residual: difference between NN and AASHTO
            physics_residual = output - psi_aashto
            result['physics_residual'] = physics_residual
        
        return result
    
    def layer_by_layer_prediction(self, x: torch.Tensor, num_steps: int = 12) -> Dict[str, torch.Tensor]:
        """
        Predict pavement degradation over multiple years.
        
        Args:
            x: (batch_size, 7) initial state
            num_steps: Number of years to predict
            
        Returns:
            Dict with trajectory of PSI over years
        """
        batch_size = x.shape[0]
        trajectory = []
        
        current_x = x.clone()
        for year in range(num_steps):
            psi_pred = self.network(current_x)
            psi_pred = torch.clamp(psi_pred, 1.5, 4.5)
            trajectory.append(psi_pred)
            
            # Update state: PSI decreases, age increases, traffic accumulates
            current_x[:, 0] = psi_pred.squeeze()  # Update PSI_0
            current_x[:, 1] += 500  # Accumulate traffic
            current_x[:, 6] += 1  # Increment age
        
        trajectory = torch.cat(trajectory, dim=1)  # (batch_size, num_steps)
        
        return {
            'trajectory': trajectory,
            'years': torch.arange(num_steps)
        }
    
    def condition_rating(self, psi: torch.Tensor) -> Tuple[torch.Tensor, list]:
        """
        Convert PSI to pavement condition rating (Excellent, Good, Fair, Poor, Critical).
        
        Returns:
            Tuple of (rating_class, rating_names)
        """
        rating_names = ['Excellent', 'Good', 'Fair', 'Poor', 'Critical']
        
        # PSI ranges: Excellent (4-4.5), Good (3-4), Fair (2-3), Poor (1.5-2), Critical (<1.5)
        rating = torch.zeros_like(psi)
        rating[psi >= 4.0] = 0
        rating[(psi >= 3.0) & (psi < 4.0)] = 1
        rating[(psi >= 2.0) & (psi < 3.0)] = 2
        rating[(psi >= 1.5) & (psi < 2.0)] = 3
        rating[psi < 1.5] = 4
        
        return rating.long(), rating_names
    
    def maintenance_threshold_alert(self, x: torch.Tensor, threshold: float = 2.5) -> Dict[str, torch.Tensor]:
        """
        Alert for maintenance when PSI drops below threshold.
        """
        output = self.forward(x, compute_physics=False)
        psi = output['prediction']
        
        needs_maintenance = (psi < threshold).float()
        urgency = (threshold - psi) / threshold * needs_maintenance
        
        return {
            'psi': psi,
            'needs_maintenance': needs_maintenance,
            'urgency_score': urgency
        }


class PavementLoss(nn.Module):
    """Loss combining data and AASHTO model physics."""
    
    def __init__(self, data_weight: float = 1.0, physics_weight: float = 0.5):
        super(PavementLoss, self).__init__()
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
    model = PINNPavement(hidden_dims=[256, 256, 128], physics_weight=1.0)
    loss_fn = PavementLoss(data_weight=1.0, physics_weight=0.5)
    
    # Mock input: [PSI_0, traffic, SN, temp, precip, freeze_cycles, age]
    x = torch.tensor([
        [4.5, 5000, 5.0, 25, 800, 20, 5],
        [4.2, 6000, 4.5, 20, 900, 30, 8],
        [3.8, 7000, 4.0, 30, 700, 15, 10],
        [3.5, 8000, 3.5, 15, 1000, 40, 15]
    ], dtype=torch.float32)
    
    y_true = torch.tensor([[3.2], [2.8], [2.1], [1.8]], dtype=torch.float32)
    
    output = model(x, compute_physics=True)
    assert output['prediction'].shape == (4, 1)
    assert output['physics_residual'].shape == (4, 1)
    
    # Verify PSI range
    assert torch.all(output['prediction'] >= 1.5) and torch.all(output['prediction'] <= 4.5)
    
    loss, loss_dict = loss_fn(output, y_true, output['physics_residual'])
    
    # Test layer-by-layer prediction
    trajectory = model.layer_by_layer_prediction(x, num_steps=12)
    assert trajectory['trajectory'].shape == (4, 12)
    
    # Test condition rating
    rating, names = model.condition_rating(output['prediction'])
    assert rating.shape == (4, 1)
    
    # Test maintenance alert
    alert = model.maintenance_threshold_alert(x, threshold=2.5)
    assert alert['needs_maintenance'].shape == (4, 1)
    
    print("✓ PINNPavement architecture validation passed")
    print(f"  Prediction shape: {output['prediction'].shape}")
    print(f"  PSI range: [{output['prediction'].min():.2f}, {output['prediction'].max():.2f}]")
    print(f"  Loss: {loss_dict}")
