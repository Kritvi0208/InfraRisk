# Game State Management - Full Implementation

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid

class GamePhase(Enum):
    INITIALIZATION = "init"
    DEAL_SOURCING = "sourcing"
    STRUCTURING = "structuring"
    PORTFOLIO_MANAGEMENT = "management"
    CRISIS_MANAGEMENT = "crisis"
    GAME_OVER = "over"

class DealStatus(Enum):
    SOURCED = "sourced"
    STRUCTURED = "structured"
    ACTIVE = "active"
    REFINANCING = "refi"
    DEFAULT = "default"
    MATURED = "matured"

@dataclass
class Deal:
    deal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    sector: str = ""
    country: str = ""
    capex: float = 0.0
    tenor_years: int = 15
    revenue_annual: float = 0.0
    opex_annual: float = 0.0
    debt_amount: float = 0.0
    equity_amount: float = 0.0
    coupon_rate: float = 0.06
    dscr: float = 1.4
    status: DealStatus = DealStatus.SOURCED
    probability_of_default: float = 0.05
    quarters_elapsed: int = 0
    revenue_shock: float = 1.0
    cost_shock: float = 1.0

    def get_annual_ebitda(self):
        return (self.revenue_annual * self.revenue_shock) - (self.opex_annual * self.cost_shock)

    def get_debt_service(self):
        if self.debt_amount <= 0:
            return 0.0
        return self.debt_amount * self.coupon_rate

    def get_annual_dscr(self):
        ebitda = self.get_annual_ebitda()
        debt_service = self.get_debt_service()
        if debt_service <= 0:
            return 9999
        return ebitda / debt_service

@dataclass
class Portfolio:
    portfolio_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    deals: Dict[str, Deal] = field(default_factory=dict)
    cash: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def add_deal(self, deal: Deal):
        self.deals[deal.deal_id] = deal

    def get_portfolio_dscr(self):
        if not self.deals:
            return 0.0
        dscrs = [d.get_annual_dscr() for d in self.deals.values()]
        return sum(dscrs) / len(dscrs)

    def get_total_debt(self):
        return sum(d.debt_amount for d in self.deals.values())

    def get_total_ebitda(self):
        return sum(d.get_annual_ebitda() for d in self.deals.values())

class StateManager:
    def __init__(self):
        self.game_phase = GamePhase.INITIALIZATION
        self.portfolio = Portfolio()
        self.quarter = 0
        self.score = 0

    def advance_quarter(self):
        self.quarter += 1
        for deal in self.portfolio.deals.values():
            deal.quarters_elapsed += 1

    def transition_phase(self, new_phase: GamePhase):
        self.game_phase = new_phase

    def get_game_state(self):
        return {
            'phase': self.game_phase.value,
            'quarter': self.quarter,
            'portfolio_dscr': self.portfolio.get_portfolio_dscr(),
            'total_debt': self.portfolio.get_total_debt(),
            'score': self.score,
            'num_projects': len(self.portfolio.deals)
        }
