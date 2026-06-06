"""
Monte Carlo Probability of Default Simulation Engine
Generates 10K scenarios with random shocks (interest rates, defaults, delays)
Outputs P10/P50/P90 confidence intervals
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple
import warnings

warnings.filterwarnings('ignore')


@dataclass
class MCScenario:
    """Single Monte Carlo scenario"""
    interest_rate_shock: float
    default_rate_shock: float
    delay_shock: float
    portfolio_pd: float
    losses: np.ndarray


class MonteCarloPDEngine:
    """Monte Carlo simulation for Probability of Default distribution"""
    
    def __init__(self, n_scenarios: int = 10000, n_assets: int = 50, seed: int = 42):
        """
        Initialize Monte Carlo engine.
        
        Args:
            n_scenarios: Number of Monte Carlo scenarios
            n_assets: Number of assets in portfolio
            seed: Random seed for reproducibility
        """
        self.n_scenarios = n_scenarios
        self.n_assets = n_assets
        self.seed = seed
        np.random.seed(seed)
        
        self.scenarios: list = []
        self.pd_distribution: np.ndarray = None
        self.confidence_intervals: Dict = {}
    
    def generate_shocks(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate random shocks: interest rates, defaults, delays.
        Shocks follow normal distribution with correlation structure.
        
        Returns:
            Tuple of (interest_rate_shocks, default_shocks, delay_shocks)
        """
        # Interest rate shocks: mean 0%, std 1%
        ir_shocks = np.random.normal(0, 0.01, self.n_scenarios)
        
        # Default rate shocks: correlated with interest rates (0.6)
        default_component1 = ir_shocks * 0.6
        default_component2 = np.random.normal(0, 0.015, self.n_scenarios) * 0.4
        default_shocks = default_component1 + default_component2
        default_shocks = np.clip(default_shocks, -0.5, 0.5)
        
        # Delay shocks: correlated with default (0.4)
        delay_component1 = default_shocks * 0.4
        delay_component2 = np.random.normal(0, 0.02, self.n_scenarios) * 0.6
        delay_shocks = delay_component1 + delay_component2
        delay_shocks = np.clip(delay_shocks, -0.3, 0.3)
        
        return ir_shocks, default_shocks, delay_shocks
    
    def calculate_portfolio_pd(self, 
                               base_pd: float = 0.02,
                               ir_sensitivity: float = 0.5,
                               default_sensitivity: float = 1.0) -> np.ndarray:
        """
        Calculate portfolio PD for each scenario with shocks.
        
        Args:
            base_pd: Base probability of default (2%)
            ir_sensitivity: Sensitivity to interest rate shocks
            default_sensitivity: Sensitivity to default shocks
            
        Returns:
            Array of portfolio PDs (one per scenario)
        """
        ir_shocks, default_shocks, delay_shocks = self.generate_shocks()
        
        # Portfolio PD = base_pd + IR impact + Default impact
        portfolio_pds = base_pd + (ir_shocks * ir_sensitivity) + (default_shocks * default_sensitivity)
        portfolio_pds = np.clip(portfolio_pds, 0.001, 0.99)
        
        return portfolio_pds, ir_shocks, default_shocks, delay_shocks
    
    def simulate_asset_defaults(self, portfolio_pds: np.ndarray) -> np.ndarray:
        """
        Simulate individual asset defaults based on portfolio PD.
        
        Args:
            portfolio_pds: Portfolio PD for each scenario
            
        Returns:
            Asset default matrix (n_scenarios x n_assets)
        """
        defaults = np.zeros((self.n_scenarios, self.n_assets))
        
        for i in range(self.n_scenarios):
            pd = portfolio_pds[i]
            # Add idiosyncratic risk: each asset has independent default component
            idiosyncratic = np.random.beta(2, 98, self.n_assets) * 0.05
            asset_pds = np.clip(pd + idiosyncratic, 0.001, 0.99)
            defaults[i, :] = (np.random.random(self.n_assets) < asset_pds).astype(float)
        
        return defaults
    
    def calculate_losses(self, 
                        defaults: np.ndarray,
                        lgd: float = 0.4,
                        ead_mean: float = 100000) -> np.ndarray:
        """
        Calculate portfolio losses: Loss = Defaults × LGD × EAD.
        
        Args:
            defaults: Asset default matrix
            lgd: Loss Given Default (40%)
            ead_mean: Mean Exposure at Default
            
        Returns:
            Portfolio losses per scenario
        """
        # Random EAD for each asset
        eads = np.random.lognormal(np.log(ead_mean), 0.3, (self.n_scenarios, self.n_assets))
        
        # Loss = sum across assets
        losses = np.sum(defaults * lgd * eads, axis=1)
        
        return losses
    
    def run_simulation(self, verbose: bool = True) -> Dict:
        """
        Run full Monte Carlo simulation.
        
        Args:
            verbose: Print progress
            
        Returns:
            Dictionary with results
        """
        if verbose:
            print(f"Running {self.n_scenarios} Monte Carlo scenarios...")
        
        # Generate shocks and calculate portfolio PDs
        portfolio_pds, ir_shocks, default_shocks, delay_shocks = self.calculate_portfolio_pd()
        
        # Simulate defaults and losses
        defaults = self.simulate_asset_defaults(portfolio_pds)
        losses = self.calculate_losses(defaults)
        
        # Store PD distribution (scale to percentage)
        self.pd_distribution = portfolio_pds * 100
        
        # Calculate confidence intervals
        self.confidence_intervals = {
            'p10': np.percentile(self.pd_distribution, 10),
            'p25': np.percentile(self.pd_distribution, 25),
            'p50': np.percentile(self.pd_distribution, 50),
            'p75': np.percentile(self.pd_distribution, 75),
            'p90': np.percentile(self.pd_distribution, 90),
            'mean': np.mean(self.pd_distribution),
            'std': np.std(self.pd_distribution),
        }
        
        if verbose:
            print(f"PD Distribution (%):")
            print(f"  P10: {self.confidence_intervals['p10']:.3f}%")
            print(f"  P50: {self.confidence_intervals['p50']:.3f}%")
            print(f"  P90: {self.confidence_intervals['p90']:.3f}%")
            print(f"  Mean: {self.confidence_intervals['mean']:.3f}% ± {self.confidence_intervals['std']:.3f}%")
        
        return {
            'pd_distribution': self.pd_distribution,
            'confidence_intervals': self.confidence_intervals,
            'losses': losses,
            'defaults': defaults,
            'portfolio_pds': portfolio_pds,
            'ir_shocks': ir_shocks,
            'default_shocks': default_shocks,
            'delay_shocks': delay_shocks,
        }
    
    def get_var(self, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk at given confidence level.
        
        Args:
            confidence: Confidence level (0.95 for 95% VaR)
            
        Returns:
            VaR in percentage
        """
        if self.pd_distribution is None:
            raise ValueError("Must run simulation first")
        
        return np.percentile(self.pd_distribution, (1 - confidence) * 100)
    
    def get_cvar(self, confidence: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (Expected Shortfall).
        
        Args:
            confidence: Confidence level
            
        Returns:
            CVaR in percentage
        """
        if self.pd_distribution is None:
            raise ValueError("Must run simulation first")
        
        var = self.get_var(confidence)
        return np.mean(self.pd_distribution[self.pd_distribution > var])


def main():
    """Example usage"""
    engine = MonteCarloPDEngine(n_scenarios=10000, n_assets=50)
    results = engine.run_simulation(verbose=True)
    
    # Calculate risk metrics
    var_95 = engine.get_var(0.95)
    cvar_95 = engine.get_cvar(0.95)
    
    print(f"\nRisk Metrics:")
    print(f"  VaR (95%): {var_95:.3f}%")
    print(f"  CVaR (95%): {cvar_95:.3f}%")
    
    return results


if __name__ == '__main__':
    main()
