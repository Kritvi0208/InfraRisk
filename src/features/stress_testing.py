"""Stress testing framework."""

import numpy as np
from typing import Dict, List

class StressTestingFramework:
    """Monte Carlo + scenario-based stress tests."""
    
    @staticmethod
    def monte_carlo_pv_analysis(annual_fcf: List[float], discount_rate: float = 0.08,
                               volatility: float = 0.15, scenarios: int = 10000) -> Dict:
        """MC simulation for NPV distribution."""
        npv_results = []
        
        for _ in range(scenarios):
            # Random shocks to FCF
            shock = np.random.normal(1, volatility, len(annual_fcf))
            shocked_fcf = np.array(annual_fcf) * shock
            npv = sum(cf / ((1 + discount_rate) ** (i + 1)) 
                     for i, cf in enumerate(shocked_fcf))
            npv_results.append(npv)
        
        return {
            'mean_npv': np.mean(npv_results),
            'std_npv': np.std(npv_results),
            'npv_5th_percentile': np.percentile(npv_results, 5),
            'npv_95th_percentile': np.percentile(npv_results, 95),
            'prob_negative_npv': sum(1 for x in npv_results if x < 0) / scenarios,
        }
    
    @staticmethod
    def scenario_analysis(base_case_fcf: List[float], discount_rate: float = 0.08) -> Dict:
        """Base, downside, upside scenarios."""
        scenarios = {}
        
        # Base case
        base_npv = sum(cf / ((1 + discount_rate) ** (i + 1)) 
                      for i, cf in enumerate(base_case_fcf))
        scenarios['base'] = {'npv': base_npv, 'label': 'Base Case'}
        
        # Downside: -20% FCF
        downside_fcf = [cf * 0.8 for cf in base_case_fcf]
        downside_npv = sum(cf / ((1 + discount_rate) ** (i + 1)) 
                          for i, cf in enumerate(downside_fcf))
        scenarios['downside'] = {'npv': downside_npv, 'label': 'Downside (-20% FCF)'}
        
        # Upside: +20% FCF
        upside_fcf = [cf * 1.2 for cf in base_case_fcf]
        upside_npv = sum(cf / ((1 + discount_rate) ** (i + 1)) 
                        for i, cf in enumerate(upside_fcf))
        scenarios['upside'] = {'npv': upside_npv, 'label': 'Upside (+20% FCF)'}
        
        return scenarios
