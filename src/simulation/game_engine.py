"""Game simulation engine with 4 distinct engines.

Engines: Time, Decision, Event, AI Opponent
"""

import numpy as np
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class GameState:
    """Game state snapshot."""
    quarter: int
    portfolio: List[Dict]
    cash: float
    score: int
    events_triggered: List[str]

class TimeEngine:
    """Quarter-by-quarter time progression."""
    
    def __init__(self):
        self.quarter = 0
        self.year = 1
    
    def advance(self) -> Dict:
        """Advance time by 1 quarter."""
        self.quarter += 1
        self.year = self.quarter // 4 + 1
        return {
            'quarter': self.quarter,
            'year': self.year,
            'events_this_quarter': []
        }

class DecisionEngine:
    """Deal sourcing, structuring, allocation decisions."""
    
    def get_available_deals(self) -> List[Dict]:
        """Available deals this quarter."""
        return [
            {'id': 'deal_1', 'sector': 'Transport', 'capex': 100e6, 'risk': 'Medium'},
            {'id': 'deal_2', 'sector': 'Energy', 'capex': 200e6, 'risk': 'High'},
            {'id': 'deal_3', 'sector': 'Water', 'capex': 50e6, 'risk': 'Low'},
        ]
    
    def apply_decision(self, decision: Dict) -> bool:
        """Process player decision."""
        return True

class EventEngine:
    """20+ pre-calibrated scenario shocks."""
    
    scenarios = [
        'Pandemic', 'Sovereign_Downgrade', 'Climate_Event', 'Interest_Spike',
        'Currency_Crisis', 'Contractor_Default', 'Permit_Delay', 'Revenue_Shortfall',
        'Refinancing_Pressure', 'Supply_Chain_Disruption', 'Inflation_Shock',
        'Rainfall_Anomaly', 'Equipment_Failure', 'Labor_Strike', 'Regulatory_Change',
        'War_Conflict', 'Earthquake', 'Flood', 'Drought', 'Technology_Disruption'
    ]
    
    def trigger_random_event(self, prob: float = 0.3) -> str:
        """Random scenario event."""
        if np.random.random() < prob:
            return np.random.choice(self.scenarios)
        return None

class AIOpponentEngine:
    """RL-trained opponent with hard rules."""
    
    def __init__(self):
        self.pd_threshold = 0.08  # Reject PD > 8%
        self.hhi_concentration_limit = 0.40  # Max 40% in one sector
    
    def evaluate_deal(self, deal: Dict, portfolio: List[Dict]) -> bool:
        """AI decision: accept/reject based on rules."""
        # Rule 1: PD > 8% → reject
        if deal.get('pd', 0) > self.pd_threshold:
            return False
        
        # Rule 2: HHI concentration check
        sector_concentration = self._compute_hhi(portfolio, deal['sector'])
        if sector_concentration > self.hhi_concentration_limit:
            return False
        
        return True
    
    def _compute_hhi(self, portfolio: List[Dict], sector: str) -> float:
        """Herfindahl-Hirschman Index for concentration."""
        portfolio_with_deal = portfolio + [{'sector': sector, 'value': 1}]
        total_value = sum(p.get('value', 1) for p in portfolio_with_deal)
        hhi = 0
        for sec in set(p['sector'] for p in portfolio_with_deal):
            share = sum(p.get('value', 1) for p in portfolio_with_deal if p['sector'] == sec) / total_value
            hhi += share ** 2
        return hhi

class ScoringSystem:
    """1000-point scoring framework."""
    
    def calculate_score(self, player_portfolio: List[Dict], 
                       ai_portfolio: List[Dict],
                       game_metrics: Dict) -> int:
        """Calculate total score."""
        # Components: PD accuracy, debt optimization, ESG
        pd_accuracy = 100 * (1 - abs(game_metrics.get('pd_error', 0.1)))
        debt_optimization = 300 * game_metrics.get('debt_to_fcf_ratio', 1.0)  # Max 300
        esg_bonus = 100 * game_metrics.get('esg_score', 0.5)  # Max 100
        vs_ai = 500 if game_metrics.get('beat_ai', False) else 250  # Beat AI: 500, else 250
        
        total = pd_accuracy + debt_optimization + esg_bonus + vs_ai
        return min(int(total), 1000)
