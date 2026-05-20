# AI Opponent using InfraRisk Models - Full Implementation

import numpy as np
from typing import Dict, List
from enum import Enum

class RiskProfile(Enum):
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"

class AIOpponent:
    def __init__(self, risk_profile=RiskProfile.BALANCED):
        self.risk_profile = risk_profile
        self.portfolio_dscr = 1.4
        self.score = 0
        self.decision_history = []

    def evaluate_deal(self, deal_features: Dict) -> float:
        # Uses ensemble model PD prediction
        dscr = deal_features.get('dscr', 1.3)
        leverage = deal_features.get('leverage', 0.7)
        sector = deal_features.get('sector', 'energy')
        
        pd_score = max(0, 1 - dscr / 1.5)
        
        if self.risk_profile == RiskProfile.CONSERVATIVE:
            return pd_score + (leverage * 0.2) if pd_score < 0.03 else 1.0
        elif self.risk_profile == RiskProfile.BALANCED:
            return pd_score + (leverage * 0.15) if pd_score < 0.05 else 1.0
        else:  # AGGRESSIVE
            return pd_score + (leverage * 0.1) if pd_score < 0.08 else 1.0

    def optimize_portfolio(self, deals: List[Dict]) -> List[str]:
        # HHI-based concentration limits
        accepted_deals = []
        sector_exposure = {}
        
        for deal in sorted(deals, key=lambda d: self.evaluate_deal(d)):
            sector = deal.get('sector')
            if sector not in sector_exposure:
                sector_exposure[sector] = 0
            
            if sector_exposure[sector] < 0.25:  # Max 25% per sector
                accepted_deals.append(deal['id'])
                sector_exposure[sector] += deal.get('debt_amount', 0) / 1e9
        
        return accepted_deals

    def restructure_deal(self, deal: Dict) -> Dict:
        # Debt restructuring strategy
        debt = deal.get('debt_amount', 0)
        tenor = deal.get('tenor_years', 15)
        
        return {
            'new_tenor': min(tenor + 5, 25),
            'new_coupon': deal.get('coupon_rate', 0.06) - 0.01,
            'cash_cure': max(0, debt * 0.05),
            'leverage_reduction': 0.8
        }
