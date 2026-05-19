"""Enhanced simulation with realistic events."""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    SOVEREIGN_DOWNGRADE = "Sovereign Downgrade"
    INTEREST_SPIKE = "Interest Rate Spike (+200bps)"
    CONSTRUCTION_DELAY = "Construction Delay (6 months)"
    REVENUE_COLLAPSE = "Revenue Collapse (-40%)"
    INFLATION_SHOCK = "Inflation Shock (+5%)"
    REFINANCING_CRISIS = "Refinancing Crisis"
    CLIMATE_DISRUPTION = "Climate Disruption"
    LABOR_STRIKE = "Labor Strike"

@dataclass
class SimulationEvent:
    type: EventType
    quarter: int
    portfolio_impact_pct: float
    duration_quarters: int

class EnhancedEventEngine:
    """Realistic event scenarios."""
    
    def __init__(self):
        self.events_history = []
        self.active_events = {}
    
    def trigger_sovereign_downgrade(self, portfolio: List[Dict]) -> Dict:
        """Downgrade → higher borrowing costs."""
        # Impact: +100-200 bps on rates, DSCR decreased by 5-10%
        impact = {
            'rate_increase_bps': np.random.uniform(100, 200),
            'dscr_reduction_pct': np.random.uniform(5, 10),
            'refinance_blocked': True,
            'duration_quarters': np.random.randint(2, 6),
        }
        return impact
    
    def trigger_interest_spike(self, portfolio: List[Dict]) -> Dict:
        """SOFR/EURIBOR spike."""
        impact = {
            'rate_increase_bps': np.random.uniform(150, 300),
            'duration_quarters': 3,
            'sectors_affected': ['Energy', 'Power'],  # Floating rate heavy
        }
        return impact
    
    def trigger_construction_delay(self, portfolio: List[Dict]) -> Dict:
        """Delay → revenue postponed, capex balloon."""
        impact = {
            'capex_overrun_pct': np.random.uniform(10, 25),
            'revenue_delay_quarters': np.random.randint(2, 8),
            'dscr_impact_pct': np.random.uniform(-15, -5),
        }
        return impact
    
    def trigger_revenue_collapse(self, portfolio: List[Dict]) -> Dict:
        """Traffic/demand crash (pandemic, recession)."""
        impact = {
            'revenue_reduction_pct': np.random.uniform(30, 50),
            'duration_quarters': np.random.randint(4, 12),
            'refinance_pressure': True,
        }
        return impact
    
    def trigger_inflation_shock(self, portfolio: List[Dict]) -> Dict:
        """Inflation spike → opex up, margins squeezed."""
        impact = {
            'opex_increase_pct': np.random.uniform(15, 35),
            'dscr_reduction_pct': np.random.uniform(8, 15),
        }
        return impact
    
    def trigger_refinancing_crisis(self, portfolio: List[Dict]) -> Dict:
        """Cannot refinance expiring debt."""
        impact = {
            'refinance_blocked': True,
            'rate_if_possible_bps': np.random.uniform(400, 800),
            'debt_rollover_failure': 'CRITICAL',
            'portfolio_impact_pct': -20,
        }
        return impact
    
    def trigger_climate_disruption(self, portfolio: List[Dict]) -> Dict:
        """Flood/drought/extreme weather."""
        impact = {
            'revenue_reduction_pct': np.random.uniform(20, 40),
            'capex_overrun_pct': np.random.uniform(30, 60),
            'sectors_affected': ['Hydropower', 'Agriculture', 'Transport'],
            'duration_quarters': np.random.randint(3, 8),
        }
        return impact
    
    def get_random_event(self, prob: float = 0.25) -> Dict:
        """Random severe event."""
        if np.random.random() < prob:
            event_type = np.random.choice(list(EventType))
            if event_type == EventType.SOVEREIGN_DOWNGRADE:
                return self.trigger_sovereign_downgrade([])
            elif event_type == EventType.INTEREST_SPIKE:
                return self.trigger_interest_spike([])
            elif event_type == EventType.CONSTRUCTION_DELAY:
                return self.trigger_construction_delay([])
            elif event_type == EventType.REVENUE_COLLAPSE:
                return self.trigger_revenue_collapse([])
            elif event_type == EventType.INFLATION_SHOCK:
                return self.trigger_inflation_shock([])
            elif event_type == EventType.REFINANCING_CRISIS:
                return self.trigger_refinancing_crisis([])
            else:
                return self.trigger_climate_disruption([])
        return {}
