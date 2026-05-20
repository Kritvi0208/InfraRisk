# Scenario Engine - Full Implementation

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
import numpy as np

class ScenarioType(Enum):
    BASE_CASE = "base"
    STRESS = "stress"
    REVERSE_STRESS = "reverse"
    EXTREME = "extreme"

@dataclass
class MacroScenario:
    name: str
    description: str
    interest_rate_shock: float
    inflation_shock: float
    fx_shock: float
    gdp_growth: float
    sovereign_spread: float
    probability: float

class ScenarioEngine:
    def __init__(self):
        self.scenarios = self._build_scenarios()

    def _build_scenarios(self) -> List[MacroScenario]:
        return [
            # Base case
            MacroScenario("Base Case", "Stable macro environment", 0.0, 0.0, 0.0, 3.5, 200, 0.40),
            
            # Rate scenarios
            MacroScenario("Rate Rise 200bps", "Fed tightening cycle", 0.02, 0.01, 0.02, 2.0, 250, 0.20),
            MacroScenario("Rate Fall 150bps", "Recession scenario", -0.015, -0.02, -0.03, -1.0, 400, 0.15),
            
            # FX stress
            MacroScenario("Currency Depreciation 30%", "EM currency crisis", 0.005, 0.08, 0.30, 1.0, 350, 0.10),
            
            # Inflation shocks
            MacroScenario("Stagflation", "High inflation, low growth", 0.01, 0.10, 0.05, 0.5, 300, 0.08),
            
            # Sovereign events
            MacroScenario("Sovereign Default", "Country default scenario", 0.025, 0.05, 0.40, -5.0, 1000, 0.02),
            
            # Liquidity shocks
            MacroScenario("Credit Crunch", "Market illiquidity", 0.015, 0.03, 0.10, -1.5, 500, 0.03),
            
            # Combined stress
            MacroScenario("Combined Stress", "Multiple shocks", 0.020, 0.06, 0.15, 0.0, 450, 0.02),
        ]

    def apply_scenario(self, deal: Dict, scenario: MacroScenario) -> Dict:
        # Apply macro shocks to deal parameters
        shocked_deal = deal.copy()
        
        # Interest rate shock affects WACC
        coupon_adjustment = scenario.interest_rate_shock * 100  # in bps
        shocked_deal['coupon_rate'] = deal.get('coupon_rate', 0.06) + coupon_adjustment / 10000
        
        # Inflation & FX affect revenue/opex
        revenue_adjustment = (1 + scenario.inflation_shock - scenario.fx_shock)
        opex_adjustment = (1 + scenario.inflation_shock * 1.2 - scenario.fx_shock)
        shocked_deal['revenue_annual'] = deal.get('revenue_annual', 0) * revenue_adjustment
        shocked_deal['opex_annual'] = deal.get('opex_annual', 0) * opex_adjustment
        
        # GDP shock affects demand
        demand_shock = scenario.gdp_growth / 3.5  # relative to base 3.5%
        shocked_deal['revenue_annual'] *= (1 + demand_shock)
        
        # FX shock affects debt service if in foreign currency
        if deal.get('currency', 'USD') != 'USD':
            shocked_deal['coupon_rate'] *= (1 + scenario.fx_shock)
        
        return shocked_deal

    def get_scenario_probabilities(self):
        return {s.name: s.probability for s in self.scenarios}
