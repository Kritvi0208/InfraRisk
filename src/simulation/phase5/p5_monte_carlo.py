# Monte Carlo Simulation
import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import lognorm, norm

class MonteCarloEngine:
    def __init__(self, n_simulations=10000, random_seed=42):
        self.n_simulations = n_simulations
        np.random.seed(random_seed)

    def simulate_deal_cash_flow(self, deal: Dict, years: int) -> Tuple[np.ndarray, Dict]:
        simulations = np.zeros((self.n_simulations, years))
        
        revenue_volatility = 0.15
        opex_volatility = 0.10
        base_revenue = deal.get('revenue_annual', 0)
        base_opex = deal.get('opex_annual', 0)
        debt_service = deal.get('debt_amount', 0) * deal.get('coupon_rate', 0.06)
        
        for sim in range(self.n_simulations):
            cumulative_cf = 0
            for year in range(years):
                revenue_shock = np.exp(np.random.normal(-revenue_volatility**2/2, revenue_volatility))
                revenue = base_revenue * revenue_shock * (1.02 ** year)
                
                opex_shock = np.exp(np.random.normal(-opex_volatility**2/2, opex_volatility))
                opex = base_opex * opex_shock * (1.03 ** year)
                
                ebitda = revenue - opex
                cf = ebitda - debt_service
                cumulative_cf += cf
                simulations[sim, year] = cumulative_cf
        
        stats = {
            'mean': np.mean(simulations[:, -1]),
            'median': np.median(simulations[:, -1]),
            'std': np.std(simulations[:, -1]),
            'percentile_10': np.percentile(simulations[:, -1], 10),
            'percentile_25': np.percentile(simulations[:, -1], 25),
            'percentile_75': np.percentile(simulations[:, -1], 75),
            'percentile_90': np.percentile(simulations[:, -1], 90),
            'prob_negative': np.mean(simulations[:, -1] < 0),
            'var_95': np.percentile(simulations[:, -1], 5),
            'cvar_95': np.mean(simulations[simulations[:, -1] < np.percentile(simulations[:, -1], 5), -1])
        }
        
        return simulations, stats

    def simulate_default_probability(self, deal: Dict, years: int) -> float:
        defaults = 0
        base_dscr = deal.get('dscr', 1.4)
        dscr_volatility = 0.20
        
        for sim in range(self.n_simulations):
            min_dscr = base_dscr
            for year in range(years):
                dscr_shock = np.exp(np.random.normal(-dscr_volatility**2/2, dscr_volatility))
                dscr_path = base_dscr * dscr_shock * (1 - 0.01 * year)
                min_dscr = min(min_dscr, dscr_path)
            
            if min_dscr < 1.0:
                defaults += 1
        
        return defaults / self.n_simulations
