# Simulation Engine
from typing import Dict, List
import numpy as np

class SimulationEngine:
    def __init__(self):
        self.name = "InfraRisk Simulation Engine"
        self.version = "1.0"

    def run_scenario_analysis(self, portfolio: List[Dict], scenarios: List[Dict]) -> Dict:
        results = {}
        for scenario in scenarios:
            scenario_results = []
            for deal in portfolio:
                adjusted_deal = self._apply_shock(deal, scenario)
                scenario_results.append(adjusted_deal)
            results[scenario['name']] = scenario_results
        return results

    def _apply_shock(self, deal: Dict, scenario: Dict) -> Dict:
        shocked = deal.copy()
        if scenario.get('rate_shock'):
            shocked['coupon_rate'] += scenario['rate_shock']
        if scenario.get('revenue_shock'):
            shocked['revenue_annual'] *= (1 + scenario['revenue_shock'])
        return shocked

    def run_stress_test(self, portfolio: List[Dict], stress_level: float = 0.2) -> Dict:
        metrics = {
            'stressed_dscr': [],
            'stressed_pd': [],
            'recovery_rates': []
        }
        
        for deal in portfolio:
            shocked_revenue = deal.get('revenue_annual', 0) * (1 - stress_level)
            debt_service = deal.get('debt_amount', 0) * deal.get('coupon_rate', 0.06)
            stressed_dscr = shocked_revenue / debt_service if debt_service > 0 else 0
            metrics['stressed_dscr'].append(stressed_dscr)
            metrics['stressed_pd'].append(max(0, 1 - stressed_dscr / 1.25))
            metrics['recovery_rates'].append(0.65)
        
        return metrics
