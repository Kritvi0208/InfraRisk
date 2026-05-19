"""Monte Carlo PD simulation with 10K scenarios."""

import numpy as np

class MonteCarloSimulation:
    """10,000 scenario PD estimation."""
    
    def simulate(self, dscr: float, leverage: float, volatility: float, 
                 scenarios: int = 10000) -> dict:
        """MC simulation for PD."""
        # Correlated random paths
        dscr_paths = np.random.normal(dscr, volatility * dscr, scenarios)
        default_threshold = 1.0
        defaults = np.sum(dscr_paths < default_threshold)
        pd = defaults / scenarios
        
        return {
            'pd': pd,
            'pd_percentile_5': np.percentile(dscr_paths, 5),
            'pd_percentile_95': np.percentile(dscr_paths, 95),
            'scenarios': scenarios,
        }
