"""Climate-adjusted Remaining Useful Life.

Formula: RUL_CA = RUL_0 × (1 - k_t × ΔT) × (1 - k_p × |ΔP|)
where:
  RUL_0 = baseline RUL (design life)
  ΔT = temperature change from baseline
  ΔP = precipitation anomaly
"""

import numpy as np
from typing import Dict, Tuple

class ClimateAdjustedRUL:
    """CA-RUL module using IPCC scenarios (RCP 4.5, RCP 8.5)."""
    
    def __init__(self):
        # Degradation sensitivity parameters
        self.k_temperature = 0.02  # 2% RUL loss per °C
        self.k_precipitation = 0.01  # 1% RUL loss per 10% precip change
        
    def calculate(self, asset_type: str, design_life: float, 
                  temp_baseline: float, precip_baseline: float,
                  rcp_scenario: str = 'RCP45') -> Dict:
        """Calculate climate-adjusted RUL.
        
        Args:
            asset_type: 'bridge', 'pavement', 'building'
            design_life: Baseline design life (years)
            temp_baseline: Historical temperature (°C)
            precip_baseline: Historical precipitation (mm/yr)
            rcp_scenario: 'RCP45' or 'RCP85'
        """
        # IPCC projections (2050)
        if rcp_scenario == 'RCP45':
            delta_temp = 1.5  # +1.5°C by 2050
            delta_precip_pct = 0.10  # +10% on average
        else:  # RCP85
            delta_temp = 2.5  # +2.5°C by 2050
            delta_precip_pct = 0.18  # +18% on average
        
        # Calculate degradation factors
        temp_factor = 1 - self.k_temperature * delta_temp
        precip_factor = 1 - self.k_precipitation * abs(delta_precip_pct * 10)
        
        # Climate-adjusted RUL
        rul_ca = design_life * temp_factor * precip_factor
        
        return {
            'asset_type': asset_type,
            'design_life': design_life,
            'rul_climate_adjusted': rul_ca,
            'rul_degradation_pct': (1 - rul_ca / design_life) * 100,
            'scenario': rcp_scenario,
        }
