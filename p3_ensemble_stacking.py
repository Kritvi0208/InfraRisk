"""
Stacking Ensemble with Meta-Learner
Combines TFT, GNN, PINN, GBT outputs with sector-weighted base models
"""

import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
import numpy as np


class MetaLearner(nn.Module):
    """
    Meta-learner for ensemble stacking.
    Learns optimal combination of base model predictions.
    """
    
    def __init__(
        self,
        num_base_models: int = 4,
        num_features: int = 32,
        hidden_dim: int = 64
    ):
        super(MetaLearner, self).__init__()
        
        self.num_base_models = num_base_models
        self.num_features = num_features
        
        # Feature embedding for meta-level information
        self.feature_embedding = nn.Linear(num_features, hidden_dim)
        
        # Stacking network
        self.stack_network = nn.Sequential(
            nn.Linear(num_base_models + hidden_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        # Learn base model weights
        self.base_model_weights = nn.Parameter(torch.ones(num_base_models) / num_base_models)
        
        # Attention for dynamic weight adjustment
        self.attention_layer = nn.Sequential(
            nn.Linear(num_base_models, num_base_models),
            nn.Softmax(dim=1)
        )
    
    def forward(
        self,
        base_predictions: torch.Tensor,
        meta_features: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for meta-learner.
        
        Args:
            base_predictions: (batch_size, num_base_models) predictions from base models
            meta_features: (batch_size, num_features) additional features
            
        Returns:
            Dict with 'ensemble_prediction', 'base_weights', 'attention_weights'
        """
        batch_size = base_predictions.shape[0]
        
        # Embed meta features if provided
        if meta_features is not None:
            meta_embedded = self.feature_embedding(meta_features)
        else:
            meta_embedded = torch.zeros(batch_size, 32, device=base_predictions.device)
        
        # Compute dynamic attention weights
        attention_weights = self.attention_layer(base_predictions)
        
        # Combine base predictions with attention
        weighted_base_predictions = base_predictions * attention_weights
        
        # Concatenate for stacking network
        stacking_input = torch.cat([weighted_base_predictions, meta_embedded], dim=1)
        
        # Final ensemble prediction
        ensemble_prediction = self.stack_network(stacking_input)
        
        return {
            'ensemble_prediction': ensemble_prediction,
            'base_weights': self.base_model_weights,
            'attention_weights': attention_weights,
            'weighted_predictions': weighted_base_predictions
        }


class StackingEnsemble(nn.Module):
    """
    Stacking ensemble combining multiple base models.
    
    Mock Input/Output:
    - Base model 1 (TFT): (batch_size, 3, 3) quantile forecasts
    - Base model 2 (GNN): (batch_size, 1) portfolio risk
    - Base model 3 (PINN): (batch_size, 1) physics prediction
    - Base model 4 (GBT): (batch_size, 1) credit risk
    
    - Ensemble output: (batch_size, 1) combined prediction
    
    Features:
    - Sector-weighted combination
    - Learnable meta-learner
    - SHAP compatibility
    """
    
    def __init__(
        self,
        num_sectors: int = 3,
        meta_feature_dim: int = 32
    ):
        super(StackingEnsemble, self).__init__()
        
        self.num_sectors = num_sectors
        self.meta_feature_dim = meta_feature_dim
        
        # Sector embeddings
        self.sector_embeddings = nn.Embedding(num_sectors, 16)
        
        # Base model output processors
        self.tft_processor = nn.Linear(9, 1)  # 3 horizons * 3 quantiles
        self.gnn_processor = nn.Linear(1, 1)
        self.pinn_processor = nn.Linear(1, 1)
        self.gbt_processor = nn.Linear(1, 1)
        
        # Meta-learner
        self.meta_learner = MetaLearner(
            num_base_models=4,
            num_features=meta_feature_dim,
            hidden_dim=64
        )
        
        # Sector-specific weightings
        self.sector_weights = nn.Linear(16, 4)  # Map sector embedding to 4 base model weights
        
        self.shap_values = None
    
    def forward(
        self,
        tft_output: torch.Tensor,
        gnn_output: torch.Tensor,
        pinn_output: torch.Tensor,
        gbt_output: torch.Tensor,
        sector_ids: torch.Tensor,
        meta_features: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass combining base model predictions.
        
        Args:
            tft_output: (batch_size, 3, 3) or (batch_size, 1) TFT predictions
            gnn_output: (batch_size, 1) GNN portfolio risk
            pinn_output: (batch_size, 1) PINN physics prediction
            gbt_output: (batch_size, 1) GBT credit risk
            sector_ids: (batch_size,) sector identifiers
            meta_features: (batch_size, meta_feature_dim) additional features
            
        Returns:
            Dict with 'ensemble_prediction', 'base_predictions', 'sector_weights'
        """
        batch_size = tft_output.shape[0]
        
        # Process TFT output (flatten if needed)
        if tft_output.dim() > 2:
            tft_output = tft_output.view(batch_size, -1)
        tft_pred = self.tft_processor(tft_output)
        
        # Process other outputs
        gnn_pred = self.gnn_processor(gnn_output)
        pinn_pred = self.pinn_processor(pinn_output)
        gbt_pred = self.gbt_processor(gbt_output)
        
        # Stack base predictions
        base_predictions = torch.cat([tft_pred, gnn_pred, pinn_pred, gbt_pred], dim=1)
        
        # Sector-specific weighting
        sector_embedding = self.sector_embeddings(sector_ids)  # (batch_size, 16)
        sector_weights = torch.softmax(self.sector_weights(sector_embedding), dim=1)  # (batch_size, 4)
        
        # Apply sector weights to base predictions
        weighted_base_predictions = base_predictions * sector_weights
        
        # Meta-learner for final combination
        meta_input = weighted_base_predictions
        meta_learner_output = self.meta_learner(
            weighted_base_predictions,
            meta_features=meta_features if meta_features is not None else sector_embedding
        )
        
        ensemble_prediction = meta_learner_output['ensemble_prediction']
        
        # Compute SHAP-like values
        shap_values = self._compute_shap_values(base_predictions, ensemble_prediction)
        self.shap_values = shap_values
        
        return {
            'ensemble_prediction': ensemble_prediction,
            'base_predictions': base_predictions,
            'sector_weights': sector_weights,
            'meta_weights': meta_learner_output['attention_weights'],
            'shap_values': shap_values,
            'individual_predictions': {
                'tft': tft_pred,
                'gnn': gnn_pred,
                'pinn': pinn_pred,
                'gbt': gbt_pred
            }
        }
    
    def _compute_shap_values(
        self,
        base_predictions: torch.Tensor,
        ensemble_prediction: torch.Tensor
    ) -> torch.Tensor:
        """
        Approximate SHAP values for base model contributions.
        """
        batch_size = base_predictions.shape[0]
        num_models = base_predictions.shape[1]
        
        shap_values = torch.zeros_like(base_predictions)
        
        # Simplified SHAP: marginal contribution
        for i in range(num_models):
            # Prediction with model i
            pred_with = ensemble_prediction.clone()
            
            # Prediction without model i (set to mean)
            pred_without = ensemble_prediction - base_predictions[:, i:i+1]
            
            # Marginal contribution
            shap_values[:, i] = (pred_with - pred_without).squeeze()
        
        return shap_values
    
    def blend_predictions(
        self,
        tft_output: torch.Tensor,
        gnn_output: torch.Tensor,
        pinn_output: torch.Tensor,
        gbt_output: torch.Tensor,
        sector_ids: torch.Tensor,
        blend_weights: Optional[Dict[str, float]] = None
    ) -> torch.Tensor:
        """
        Simple blending with fixed weights (alternative to meta-learner).
        """
        if blend_weights is None:
            blend_weights = {
                'tft': 0.25,
                'gnn': 0.25,
                'pinn': 0.25,
                'gbt': 0.25
            }
        
        batch_size = tft_output.shape[0]
        
        # Ensure 1D predictions
        tft_flat = tft_output.view(batch_size, -1).mean(dim=1, keepdim=True) if tft_output.dim() > 2 else tft_output
        
        blended = (
            blend_weights['tft'] * tft_flat +
            blend_weights['gnn'] * gnn_output +
            blend_weights['pinn'] * pinn_output +
            blend_weights['gbt'] * gbt_output
        )
        
        return blended
    
    def get_model_importances(self) -> Dict[str, float]:
        """Extract base model importance scores from meta-learner."""
        base_weights = self.meta_learner.base_model_weights.detach()
        
        return {
            'tft': base_weights[0].item(),
            'gnn': base_weights[1].item(),
            'pinn': base_weights[2].item(),
            'gbt': base_weights[3].item()
        }


class StackingLoss(nn.Module):
    """Loss for stacking ensemble training."""
    
    def __init__(self):
        super(StackingLoss, self).__init__()
        self.mse_loss = nn.MSELoss()
        self.l1_loss = nn.L1Loss()
    
    def forward(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: torch.Tensor,
        use_l1: bool = False
    ) -> Tuple[torch.Tensor, Dict]:
        """
        Compute loss with optional L1 regularization for model selection.
        """
        ensemble_pred = predictions['ensemble_prediction']
        
        if use_l1:
            loss = self.mse_loss(ensemble_pred, targets) + 0.01 * self.l1_loss(ensemble_pred, targets)
        else:
            loss = self.mse_loss(ensemble_pred, targets)
        
        return loss, {'loss': loss.item()}


if __name__ == "__main__":
    model = StackingEnsemble(num_sectors=3, meta_feature_dim=32)
    loss_fn = StackingLoss()
    
    # Mock base model outputs
    batch_size = 32
    tft_output = torch.randn(batch_size, 3, 3)  # 3 horizons, 3 quantiles
    gnn_output = torch.randn(batch_size, 1)
    pinn_output = torch.randn(batch_size, 1)
    gbt_output = torch.randn(batch_size, 1)
    
    sector_ids = torch.randint(0, 3, (batch_size,))
    meta_features = torch.randn(batch_size, 32)
    
    # Forward pass
    output = model(
        tft_output=tft_output,
        gnn_output=gnn_output,
        pinn_output=pinn_output,
        gbt_output=gbt_output,
        sector_ids=sector_ids,
        meta_features=meta_features
    )
    
    assert output['ensemble_prediction'].shape == (batch_size, 1)
    assert output['base_predictions'].shape == (batch_size, 4)
    assert output['sector_weights'].shape == (batch_size, 4)
    assert output['shap_values'].shape == (batch_size, 4)
    
    # Compute loss
    y_true = torch.randn(batch_size, 1)
    loss, loss_dict = loss_fn(output, y_true)
    
    # Test blending
    blended = model.blend_predictions(tft_output, gnn_output, pinn_output, gbt_output, sector_ids)
    assert blended.shape == (batch_size, 1)
    
    # Get model importances
    importances = model.get_model_importances()
    
    print("✓ StackingEnsemble architecture validation passed")
    print(f"  Ensemble prediction shape: {output['ensemble_prediction'].shape}")
    print(f"  Base predictions shape: {output['base_predictions'].shape}")
    print(f"  Model importances: {importances}")
    print(f"  Ensemble output range: [{output['ensemble_prediction'].min():.3f}, {output['ensemble_prediction'].max():.3f}]")
