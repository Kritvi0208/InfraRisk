"""
Game State Management - State machines and data structures
Complete implementation: 250 lines
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import pickle
from pathlib import Path
import uuid


class GamePhase(Enum):
    """Game phase states"""
    INITIALIZATION = "initialization"
    DEAL_SOURCING = "deal_sourcing"
    STRUCTURING = "structuring"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    CRISIS_MANAGEMENT = "crisis_management"
    GAME_OVER = "game_over"


class DealStatus(Enum):
    """Deal lifecycle status"""
    SOURCED = "sourced"
    STRUCTURED = "structured"
    ACTIVE = "active"
    REFINANCING = "refinancing"
    DEFAULT = "default"
    MATURED = "matured"


@dataclass
class Deal:
    """Individual infrastructure deal (80 lines)"""
    deal_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    sector: str = ""
    country: str = ""
    capex: float = 0.0
    tenor_years: int = 10
    revenue_annual: float = 0.0
    opex_annual: float = 0.0
    status: DealStatus = DealStatus.SOURCED
    probability_of_default: float = 0.05
    recovery_rate: float = 0.65
    dscr: float = 1.5
    debt_amount: float = 0.0
    equity_amount: float = 0.0
    coupon_rate: float = 0.06
    quarters_elapsed: int = 0
    quarters_total: int = 40
    original_capex: float = 0.0
    completion_date: Optional[datetime] = None
    construction_delay_quarters: int = 0
    revenue_shock: float = 1.0
    cost_shock: float = 1.0
    cumulative_cash_flow: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    sector_concentration: float = 0.0
    
    def get_annual_ebitda(self) -> float:
        """Calculate annual EBITDA"""
        revenue = self.revenue_annual * self.revenue_shock
        opex = self.opex_annual * self.cost_shock
        return revenue - opex
    
    def get_debt_service(self) -> float:
        """Annual debt service"""
        if self.debt_amount <= 0:
            return 0.0
        return self.debt_amount * self.coupon_rate
    
    def get_annual_dscr(self) -> float:
        """Calculate DSCR for current year"""
        ebitda = self.get_annual_ebitda()
        debt_service = self.get_debt_service()
        if debt_service <= 0:
            return 0.0
        return ebitda / debt_service
    
    def is_in_default(self) -> bool:
        """Check if deal is in default"""
        return self.get_annual_dscr() < 1.0 or self.status == DealStatus.DEFAULT
    
    def apply_shock(self, revenue_shock: float, cost_shock: float, delay: int) -> None:
        """Apply shock to deal"""
        self.revenue_shock *= revenue_shock
        self.cost_shock *= cost_shock
        self.construction_delay_quarters += delay


@dataclass
class Portfolio:
    """Player's portfolio (100 lines)"""
    deals: Dict[str, Deal] = field(default_factory=dict)
    total_equity_invested: float = 0.0
    total_debt_raised: float = 0.0
    cumulative_returns: float = 0.0
    total_defaults: int = 0
    total_recoveries: float = 0.0
    
    def add_deal(self, deal: Deal) -> None:
        """Add deal to portfolio"""
        self.deals[deal.deal_id] = deal
        self.total_equity_invested += deal.equity_amount
        self.total_debt_raised += deal.debt_amount
    
    def remove_deal(self, deal_id: str) -> Optional[Deal]:
        """Remove deal from portfolio"""
        if deal_id in self.deals:
            deal = self.deals.pop(deal_id)
            self.total_equity_invested -= deal.equity_amount
            self.total_debt_raised -= deal.debt_amount
            return deal
        return None
    
    def get_portfolio_value(self) -> float:
        """Total portfolio value"""
        return self.total_equity_invested + self.total_debt_raised
    
    def get_portfolio_dscr(self) -> float:
        """Weighted average DSCR"""
        if not self.deals:
            return 0.0
        total_ebitda = 0.0
        total_debt_service = 0.0
        
        for deal in self.deals.values():
            total_ebitda += deal.get_annual_ebitda()
            total_debt_service += deal.get_debt_service()
        
        if total_debt_service <= 0:
            return 0.0
        return total_ebitda / total_debt_service
    
    def get_sector_concentration(self, sector: str) -> float:
        """Sector concentration as % of portfolio"""
        if self.get_portfolio_value() == 0:
            return 0.0
        sector_value = sum(
            d.equity_amount + d.debt_amount 
            for d in self.deals.values() 
            if d.sector == sector
        )
        return sector_value / self.get_portfolio_value()
    
    def get_default_count(self) -> int:
        """Count of deals in default"""
        return sum(1 for d in self.deals.values() if d.is_in_default())
    
    def get_active_deals(self) -> List[Deal]:
        """Get all active deals"""
        return [d for d in self.deals.values() 
                if d.status in (DealStatus.ACTIVE, DealStatus.REFINANCING)]
    
    def get_portfolio_metrics(self) -> Dict[str, float]:
        """Get key portfolio metrics"""
        active_deals = self.get_active_deals()
        return {
            "total_value": self.get_portfolio_value(),
            "num_deals": len(self.deals),
            "active_deals": len(active_deals),
            "default_count": self.get_default_count(),
            "portfolio_dscr": self.get_portfolio_dscr(),
            "equity_invested": self.total_equity_invested,
            "debt_raised": self.total_debt_raised,
            "cumulative_returns": self.cumulative_returns,
        }


@dataclass
class GameState:
    """Complete game state (70 lines)"""
    game_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    game_mode: str = "portfolio_manager"
    current_quarter: int = 0
    total_quarters: int = 40
    current_year: float = 0.0
    game_phase: GamePhase = GamePhase.INITIALIZATION
    
    player_portfolio: Portfolio = field(default_factory=Portfolio)
    ai_portfolio: Portfolio = field(default_factory=Portfolio)
    
    cash_available: float = 1_000_000_000.0
    ai_cash_available: float = 1_000_000_000.0
    
    active_events: List[str] = field(default_factory=list)
    market_conditions: Dict[str, float] = field(default_factory=lambda: {
        "interest_rate": 0.05,
        "inflation": 0.02,
        "fx_volatility": 0.10,
        "default_rate": 0.03
    })
    
    player_score: int = 0
    ai_score: int = 0
    turn_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def advance_quarter(self) -> None:
        """Advance game by one quarter"""
        self.current_quarter += 1
        self.current_year = self.current_quarter / 4.0
        self.updated_at = datetime.now()
        
        if self.current_quarter >= self.total_quarters:
            self.game_phase = GamePhase.GAME_OVER
    
    def is_game_over(self) -> bool:
        """Check if game is finished"""
        return self.current_quarter >= self.total_quarters
    
    def get_game_progress(self) -> float:
        """Get game progress as percentage"""
        return (self.current_quarter / self.total_quarters) * 100.0
    
    def save_to_file(self, filepath: str) -> None:
        """Save game state"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load_from_file(filepath: str) -> 'GameState':
        """Load game state"""
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export as dictionary"""
        return {
            "game_id": self.game_id,
            "game_mode": self.game_mode,
            "current_quarter": self.current_quarter,
            "current_year": self.current_year,
            "player_score": self.player_score,
            "ai_score": self.ai_score,
            "progress": self.get_game_progress(),
        }


class StateManager:
    """Manages game state and persistence (70 lines)"""
    
    def __init__(self, state: GameState):
        self.state = state
        self.snapshots: List[GameState] = []
    
    def create_snapshot(self) -> None:
        """Create state snapshot for undo"""
        import copy
        self.snapshots.append(copy.deepcopy(self.state))
    
    def restore_snapshot(self, index: int = -1) -> bool:
        """Restore from snapshot"""
        if 0 <= index < len(self.snapshots) or index == -1:
            import copy
            self.state = copy.deepcopy(self.snapshots[index])
            return True
        return False
    
    def clear_snapshots(self) -> None:
        """Clear all snapshots"""
        self.snapshots = []
    
    def record_action(self, action: Dict[str, Any]) -> None:
        """Record player action in history"""
        self.state.turn_history.append({
            "quarter": self.state.current_quarter,
            "timestamp": datetime.now().isoformat(),
            **action
        })
    
    def update_market_conditions(self, conditions: Dict[str, float]) -> None:
        """Update market conditions"""
        self.state.market_conditions.update(conditions)
        self.state.updated_at = datetime.now()
    
    def get_snapshot_count(self) -> int:
        """Get number of saved snapshots"""
        return len(self.snapshots)
    
    def get_action_history(self, limit: int = 10) -> List[Dict]:
        """Get recent actions"""
        return self.state.turn_history[-limit:]
