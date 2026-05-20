# Models Core Module - Central definitions

from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class ProjectDeal:
    deal_id: str
    name: str
    sector: str
    country: str
    capex: float
    revenue_annual: float
    opex_annual: float
    debt_amount: float
    equity_amount: float
    coupon_rate: float
    tenor_years: int
    probability_of_default: float
    dscr_target: float = 1.25
    status: str = "active"
    
    @property
    def ebitda(self):
        return self.revenue_annual - self.opex_annual
    
    @property
    def leverage(self):
        total = self.debt_amount + self.equity_amount
        return self.debt_amount / total if total > 0 else 0
    
    @property
    def dscr(self):
        debt_service = self.debt_amount * self.coupon_rate
        return self.ebitda / debt_service if debt_service > 0 else 0
    
    def to_dict(self):
        return {
            'deal_id': self.deal_id,
            'name': self.name,
            'sector': self.sector,
            'country': self.country,
            'capex': self.capex,
            'revenue_annual': self.revenue_annual,
            'opex_annual': self.opex_annual,
            'debt_amount': self.debt_amount,
            'equity_amount': self.equity_amount,
            'coupon_rate': self.coupon_rate,
            'tenor_years': self.tenor_years,
            'probability_of_default': self.probability_of_default,
            'ebitda': self.ebitda,
            'leverage': self.leverage,
            'dscr': self.dscr
        }

@dataclass
class Portfolio:
    portfolio_id: str
    deals: List[ProjectDeal]
    cash_balance: float = 0.0
    
    @property
    def total_debt(self):
        return sum(d.debt_amount for d in self.deals)
    
    @property
    def total_equity(self):
        return sum(d.equity_amount for d in self.deals)
    
    @property
    def total_ebitda(self):
        return sum(d.ebitda for d in self.deals)
    
    @property
    def portfolio_dscr(self):
        avg_dscr = sum(d.dscr for d in self.deals) / len(self.deals) if self.deals else 0
        return avg_dscr
    
    @property
    def portfolio_pd(self):
        # Correlated PD using Vasicek model
        if not self.deals:
            return 0
        sum_pd = sum(d.probability_of_default for d in self.deals)
        return min(sum_pd / len(self.deals), 0.10)  # capped at 10%
    
    def to_dict(self):
        return {
            'portfolio_id': self.portfolio_id,
            'num_deals': len(self.deals),
            'total_debt': self.total_debt,
            'total_ebitda': self.total_ebitda,
            'portfolio_dscr': self.portfolio_dscr,
            'portfolio_pd': self.portfolio_pd,
            'deals': [d.to_dict() for d in self.deals]
        }
