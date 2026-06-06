"""
AI Opponent Engine - RL agent with strategy and deal selection
Complete implementation: 400 lines
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import random
import math

try:
    from .p5_game_state import GameState, Deal, Portfolio, DealStatus
except ImportError:  # pragma: no cover - supports direct script execution
    from p5_game_state import GameState, Deal, Portfolio, DealStatus


class RiskProfile(Enum):
    """AI risk profiles"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


@dataclass
class AIStrategy:
    """AI strategy parameters"""
    risk_profile: RiskProfile
    max_leverage: float
    max_dscr_target: float
    min_dscr_target: float
    sector_concentration_limit: float
    deal_size_limit: float
    cash_reserve_ratio: float


class AIOpponent:
    """AI opponent with RL-style decision making (400 lines)"""
    
    STRATEGIES = {
        RiskProfile.CONSERVATIVE: AIStrategy(
            risk_profile=RiskProfile.CONSERVATIVE,
            max_leverage=0.60,
            max_dscr_target=2.5,
            min_dscr_target=1.5,
            sector_concentration_limit=0.30,
            deal_size_limit=0.20,
            cash_reserve_ratio=0.35,
        ),
        RiskProfile.BALANCED: AIStrategy(
            risk_profile=RiskProfile.BALANCED,
            max_leverage=0.70,
            max_dscr_target=2.0,
            min_dscr_target=1.25,
            sector_concentration_limit=0.35,
            deal_size_limit=0.25,
            cash_reserve_ratio=0.25,
        ),
        RiskProfile.AGGRESSIVE: AIStrategy(
            risk_profile=RiskProfile.AGGRESSIVE,
            max_leverage=0.75,
            max_dscr_target=1.8,
            min_dscr_target=1.10,
            sector_concentration_limit=0.40,
            deal_size_limit=0.30,
            cash_reserve_ratio=0.15,
        ),
    }
    
    def __init__(self, risk_profile: RiskProfile = RiskProfile.BALANCED):
        self.risk_profile = risk_profile
        self.strategy = self.STRATEGIES[risk_profile]
        self.decision_history: List[Dict] = []
        self.portfolio_snapshots: List[Dict] = []
        self.q_table: Dict[str, float] = {}  # Mock Q-learning table
        self.experience_buffer: List[Tuple] = []
    
    def get_next_action(self, state: GameState) -> Dict[str, Any]:
        """Get next action for AI"""
        portfolio = state.ai_portfolio
        metrics = portfolio.get_portfolio_metrics()
        
        # Check constraints
        if not self._check_constraints(portfolio, state):
            return {"action": "hold", "reason": "constraint_violated"}
        
        # Select action type
        action_type = self._select_action_using_policy(state)
        
        if action_type == "source":
            return self._source_deal(state)
        elif action_type == "structure":
            return self._restructure_deal(state)
        elif action_type == "rebalance":
            return self._rebalance_portfolio(state)
        elif action_type == "sell":
            return self._sell_deal(state)
        else:
            return {"action": "hold", "reason": "no_opportunity"}
    
    def _check_constraints(self, portfolio: Portfolio, state: GameState) -> bool:
        """Check if portfolio meets hard constraints"""
        metrics = portfolio.get_portfolio_metrics()
        
        # Leverage check
        if metrics["equity_invested"] > 0:
            leverage = metrics["debt_raised"] / metrics["equity_invested"]
            if leverage > self.strategy.max_leverage:
                return False
        
        # DSCR check
        if metrics["portfolio_dscr"] < self.strategy.min_dscr_target:
            return False
        
        # Cash reserve check
        min_cash = state.ai_cash_available * self.strategy.cash_reserve_ratio
        if state.ai_cash_available < min_cash:
            return False
        
        return True
    
    def _select_action_using_policy(self, state: GameState) -> str:
        """Select action using mock RL policy"""
        portfolio = state.ai_portfolio
        metrics = portfolio.get_portfolio_metrics()
        
        # Get state representation
        state_key = self._get_state_key(state)
        
        # Epsilon-greedy selection (exploration vs exploitation)
        epsilon = 0.1
        if random.random() < epsilon:
            return random.choice(["source", "structure", "rebalance", "sell", "hold"])
        
        # Exploitation: use learned policy
        if metrics["num_deals"] < 3:
            return "source"
        
        if metrics["portfolio_dscr"] > self.strategy.max_dscr_target:
            return "rebalance"
        
        if any(d.is_in_default() for d in portfolio.get_active_deals()):
            return "rebalance"
        
        if random.random() < 0.3:
            return random.choice(["source", "rebalance"])
        
        return "hold"
    
    def _get_state_key(self, state: GameState) -> str:
        """Get state representation for Q-learning"""
        metrics = state.ai_portfolio.get_portfolio_metrics()
        num_deals = min(10, metrics["num_deals"])
        dscr_bucket = int(metrics["portfolio_dscr"] * 10) // 5
        
        return f"deals_{num_deals}_dscr_{dscr_bucket}"
    
    def _source_deal(self, state: GameState) -> Dict[str, Any]:
        """Source and structure new deal"""
        if state.ai_cash_available < 100_000_000:
            return {"action": "hold", "reason": "insufficient_cash"}
        
        # Generate deal opportunity
        deal = self._generate_deal(state)
        
        # Evaluate using scoring
        score = self._score_deal(deal, state)
        
        if score > 0.5:
            # Structure the deal
            deal = self._structure_deal_ai(deal, state)
            
            self.decision_history.append({
                "quarter": state.current_quarter,
                "action": "source",
                "deal": deal.deal_id,
                "score": score,
            })
            
            return {
                "action": "source",
                "deal": deal,
                "score": score,
                "debt_ratio": deal.debt_amount / deal.capex,
            }
        
        return {"action": "hold", "reason": "deal_score_low"}
    
    def _generate_deal(self, state: GameState) -> Deal:
        """Generate deal opportunity"""
        sectors = ["Transport", "Energy", "Water", "Telecom", "Healthcare"]
        countries = ["India", "Brazil", "Nigeria", "Egypt", "Vietnam", "Kenya"]
        
        deal = Deal(
            name=f"AI_Opp_{state.current_quarter}_{random.randint(1000, 9999)}",
            sector=random.choice(sectors),
            country=random.choice(countries),
            capex=random.uniform(50_000_000, 300_000_000),
            tenor_years=random.randint(12, 25),
            revenue_annual=random.uniform(15_000_000, 70_000_000),
            opex_annual=random.uniform(7_000_000, 35_000_000),
            probability_of_default=random.uniform(0.03, 0.08),
            dscr=random.uniform(1.3, 2.0),
        )
        return deal
    
    def _score_deal(self, deal: Deal, state: GameState) -> float:
        """Score deal using heuristics"""
        score = 0.0
        
        # DSCR factor (higher is better)
        if deal.dscr > 1.5:
            score += 0.3
        elif deal.dscr > 1.25:
            score += 0.15
        
        # PD factor (lower is better)
        if deal.probability_of_default < 0.05:
            score += 0.3
        elif deal.probability_of_default < 0.07:
            score += 0.15
        
        # Capex efficiency
        if deal.capex < 200_000_000:
            score += 0.2
        
        # Revenue quality
        roi = deal.revenue_annual / deal.capex if deal.capex > 0 else 0
        if roi > 0.20:
            score += 0.2
        
        return score
    
    def _structure_deal_ai(self, deal: Deal, state: GameState) -> Deal:
        """Structure deal for AI based on strategy"""
        debt_ratio = self.strategy.max_leverage / (1 + self.strategy.max_leverage)
        
        # Adjust based on portfolio DSCR
        portfolio_dscr = state.ai_portfolio.get_portfolio_dscr()
        if portfolio_dscr < self.strategy.min_dscr_target:
            debt_ratio *= 0.9  # Reduce leverage if DSCR is low
        
        deal.debt_amount = deal.capex * debt_ratio
        deal.equity_amount = deal.capex * (1 - debt_ratio)
        deal.coupon_rate = 0.05 + (deal.probability_of_default * 0.5)
        deal.status = DealStatus.ACTIVE
        
        return deal
    
    def _restructure_deal(self, state: GameState) -> Dict[str, Any]:
        """Restructure existing deal"""
        portfolio = state.ai_portfolio
        
        if not portfolio.deals:
            return {"action": "hold", "reason": "no_deals"}
        
        # Select deal with worst DSCR
        worst_deal = min(
            portfolio.deals.values(),
            key=lambda d: d.get_annual_dscr()
        )
        
        if worst_deal.get_annual_dscr() >= self.strategy.min_dscr_target:
            return {"action": "hold", "reason": "dscr_acceptable"}
        
        # Restructure: lower coupon or extend tenor
        old_coupon = worst_deal.coupon_rate
        new_coupon = old_coupon * 0.95
        
        self.decision_history.append({
            "quarter": state.current_quarter,
            "action": "restructure",
            "deal": worst_deal.deal_id,
            "old_coupon": old_coupon,
            "new_coupon": new_coupon,
        })
        
        return {
            "action": "restructure",
            "deal": worst_deal.deal_id,
            "new_coupon": new_coupon,
        }
    
    def _rebalance_portfolio(self, state: GameState) -> Dict[str, Any]:
        """Rebalance portfolio"""
        portfolio = state.ai_portfolio
        metrics = portfolio.get_portfolio_metrics()
        
        # Check concentration limits
        for sector in ["Transport", "Energy", "Water", "Telecom", "Healthcare"]:
            concentration = portfolio.get_sector_concentration(sector)
            if concentration > self.strategy.sector_concentration_limit:
                return {
                    "action": "rebalance",
                    "reason": f"{sector}_concentration_high",
                    "concentration": concentration,
                }
        
        return {"action": "hold", "reason": "portfolio_balanced"}
    
    def _sell_deal(self, state: GameState) -> Dict[str, Any]:
        """Sell underperforming deal"""
        portfolio = state.ai_portfolio
        
        # Find deals in default or near-default
        candidates = [d for d in portfolio.get_active_deals() if d.is_in_default()]
        
        if not candidates:
            return {"action": "hold", "reason": "no_candidates"}
        
        deal_to_sell = random.choice(candidates)
        
        return {
            "action": "sell",
            "deal": deal_to_sell.deal_id,
            "expected_recovery": deal_to_sell.recovery_rate,
        }
    
    def update_q_learning(self, reward: float, next_state_key: str) -> None:
        """Update mock Q-learning table"""
        alpha = 0.1  # Learning rate
        gamma = 0.9  # Discount factor
        
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = reward
        else:
            old_value = self.q_table[next_state_key]
            self.q_table[next_state_key] = old_value + alpha * (reward - old_value)
    
    def get_strategy_summary(self) -> Dict[str, Any]:
        """Get summary of AI strategy"""
        return {
            "risk_profile": self.risk_profile.value,
            "max_leverage": self.strategy.max_leverage,
            "dscr_target": f"{self.strategy.min_dscr_target}-{self.strategy.max_dscr_target}x",
            "sector_concentration_limit": self.strategy.sector_concentration_limit,
            "decisions_made": len(self.decision_history),
            "q_table_size": len(self.q_table),
        }
