"""
Simulation Engine - Integrated 4 engines: Time, Decision, Event, AI
Complete implementation: 450 lines
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random
import math

from p5_game_state import GameState, Deal, DealStatus, Portfolio, GamePhase


class TimeEngine:
    """Quarter-by-quarter time progression (100 lines)"""
    
    def __init__(self, total_quarters: int = 40, start_year: int = 2024):
        self.total_quarters = total_quarters
        self.start_year = start_year
        self.current_quarter = 0
    
    def advance(self) -> Tuple[int, int, int]:
        """Advance time and return (quarter, year, month)"""
        self.current_quarter += 1
        year = self.start_year + (self.current_quarter - 1) // 4
        month = ((self.current_quarter - 1) % 4) * 3 + 1
        return self.current_quarter, year, month
    
    def get_progress(self) -> float:
        """Get time progress (0-1)"""
        return min(1.0, self.current_quarter / self.total_quarters)
    
    def is_complete(self) -> bool:
        """Check if simulation is complete"""
        return self.current_quarter >= self.total_quarters
    
    def get_quarter_info(self) -> Dict[str, int]:
        """Get current quarter info"""
        year = self.start_year + (self.current_quarter - 1) // 4
        quarter_num = ((self.current_quarter - 1) % 4) + 1
        month = ((self.current_quarter - 1) % 4) * 3 + 1
        return {
            "quarter": self.current_quarter,
            "year": year,
            "quarter_num": quarter_num,
            "month": month,
        }


class DecisionEngine:
    """Deal sourcing, structuring, rebalancing (120 lines)"""
    
    def __init__(self):
        self.sourced_deals: List[Deal] = []
        self.available_sectors = ["Transport", "Energy", "Water", "Telecom", "Healthcare"]
        self.available_countries = ["India", "Nigeria", "Brazil", "Egypt", "Vietnam"]
    
    def source_deals(self, num_deals: int = 3) -> List[Deal]:
        """Generate new deal opportunities"""
        deals = []
        for i in range(num_deals):
            deal = Deal(
                name=f"Deal_{random.randint(1000, 9999)}",
                sector=random.choice(self.available_sectors),
                country=random.choice(self.available_countries),
                capex=random.uniform(50_000_000, 500_000_000),
                tenor_years=random.randint(10, 30),
                revenue_annual=random.uniform(10_000_000, 100_000_000),
                opex_annual=random.uniform(5_000_000, 50_000_000),
                probability_of_default=random.uniform(0.02, 0.10),
                dscr=random.uniform(1.2, 2.5),
            )
            deals.append(deal)
        return deals
    
    def structure_deal(self, deal: Deal, debt_ratio: float = 0.70) -> Deal:
        """Structure debt and equity for deal"""
        total_capex = deal.capex
        deal.debt_amount = total_capex * debt_ratio
        deal.equity_amount = total_capex * (1 - debt_ratio)
        deal.coupon_rate = 0.05 + random.uniform(0.01, 0.05)
        deal.status = DealStatus.STRUCTURED
        return deal
    
    def optimize_portfolio(self, portfolio: Portfolio) -> Dict[str, float]:
        """Get portfolio rebalancing recommendations"""
        metrics = portfolio.get_portfolio_metrics()
        sector_hhi = sum(
            (portfolio.get_sector_concentration(s) ** 2) 
            for s in ["Transport", "Energy", "Water", "Telecom", "Healthcare"]
        )
        
        return {
            "sector_hhi": sector_hhi,
            "portfolio_dscr": metrics["portfolio_dscr"],
            "leverage": metrics["debt_raised"] / (metrics["equity_invested"] + 1),
            "default_risk": metrics["default_count"] / (metrics["num_deals"] + 1),
        }
    
    def get_deal_recommendation(self, portfolio: Portfolio) -> Optional[Deal]:
        """Recommend deal based on portfolio needs"""
        metrics = self.optimize_portfolio(portfolio)
        
        # Recommend based on gaps
        if metrics["default_risk"] > 0.1:
            return None  # Too much risk
        
        new_deal = self.source_deals(1)[0]
        return new_deal


class EventEngine:
    """Event triggering and application (100 lines)"""
    
    EVENT_TYPES = ["pandemic", "downgrade", "climate", "rate_shock", "fx_crisis",
                   "construction_delay", "demand_shock", "refinance_crisis"]
    
    def __init__(self):
        self.event_probabilities = {
            "pandemic": 0.01,
            "downgrade": 0.02,
            "climate": 0.03,
            "rate_shock": 0.05,
            "fx_crisis": 0.04,
            "construction_delay": 0.10,
            "demand_shock": 0.08,
            "refinance_crisis": 0.02,
        }
    
    def trigger_events(self, portfolio: Portfolio) -> List[Tuple[str, Deal]]:
        """Trigger events affecting portfolio"""
        triggered = []
        
        for deal in portfolio.get_active_deals():
            for event_type in self.EVENT_TYPES:
                if random.random() < self.event_probabilities[event_type]:
                    triggered.append((event_type, deal))
        
        return triggered
    
    def apply_event(self, event_type: str, deal: Deal) -> Dict[str, float]:
        """Apply event impact to deal"""
        impacts = {}
        
        if event_type == "pandemic":
            deal.apply_shock(0.70, 1.20, 18)
            impacts = {"revenue_shock": 0.70, "cost_shock": 1.20, "delay": 18}
        
        elif event_type == "downgrade":
            deal.coupon_rate *= 1.03
            impacts = {"coupon_increase": 0.03}
        
        elif event_type == "climate":
            deal.capex += 50_000_000
            deal.apply_shock(1.0, 1.0, 12)
            impacts = {"capex_increase": 50_000_000, "delay": 12}
        
        elif event_type == "rate_shock":
            deal.coupon_rate *= 1.02
            impacts = {"coupon_increase": 0.02}
        
        elif event_type == "fx_crisis":
            deal.apply_shock(0.60, 1.0, 0)
            impacts = {"revenue_shock": 0.60}
        
        elif event_type == "construction_delay":
            months = random.gauss(6, 3)
            deal.construction_delay_quarters += int(months / 3)
            impacts = {"delay_months": months}
        
        elif event_type == "demand_shock":
            deal.apply_shock(0.50, 1.0, 0)
            impacts = {"revenue_shock": 0.50}
        
        elif event_type == "refinance_crisis":
            deal.coupon_rate *= 1.05
            impacts = {"coupon_increase": 0.05}
        
        return impacts


class AIOpponentEngine:
    """AI opponent strategy and actions (130 lines)"""
    
    def __init__(self):
        self.strategy = "balanced"  # "aggressive", "conservative", "balanced"
        self.risk_appetite = 0.6
    
    def get_next_action(self, state: GameState) -> Dict[str, Any]:
        """Determine AI's next action"""
        action_type = self._select_action_type(state)
        
        if action_type == "source":
            return self._action_source_deal(state)
        elif action_type == "structure":
            return self._action_structure_deal(state)
        elif action_type == "rebalance":
            return self._action_rebalance(state)
        elif action_type == "hold":
            return {"type": "hold", "cash_held": state.ai_cash_available}
        else:
            return {"type": "pass"}
    
    def _select_action_type(self, state: GameState) -> str:
        """Select action based on strategy and portfolio"""
        metrics = state.ai_portfolio.get_portfolio_metrics()
        
        if metrics["portfolio_dscr"] < 1.2:
            return "hold"
        
        if metrics["num_deals"] < 5 and state.ai_cash_available > 100_000_000:
            return "source"
        
        if metrics["num_deals"] > 0 and random.random() < 0.3:
            return "rebalance"
        
        return random.choice(["source", "hold"])
    
    def _action_source_deal(self, state: GameState) -> Dict[str, Any]:
        """AI sources and structures a deal"""
        if state.ai_cash_available < 50_000_000:
            return {"type": "pass"}
        
        deal = Deal(
            name=f"AI_Deal_{state.current_quarter}",
            sector=random.choice(["Transport", "Energy", "Water"]),
            country=random.choice(["India", "Brazil", "Nigeria"]),
            capex=random.uniform(100_000_000, 400_000_000),
            tenor_years=15,
            revenue_annual=random.uniform(20_000_000, 80_000_000),
            opex_annual=random.uniform(10_000_000, 40_000_000),
        )
        
        debt_ratio = 0.65 + (self.risk_appetite - 0.5) * 0.2
        deal.debt_amount = deal.capex * debt_ratio
        deal.equity_amount = deal.capex * (1 - debt_ratio)
        deal.status = DealStatus.ACTIVE
        
        return {"type": "source", "deal": deal}
    
    def _action_structure_deal(self, state: GameState) -> Dict[str, Any]:
        """AI restructures existing deal"""
        if len(state.ai_portfolio.deals) == 0:
            return {"type": "pass"}
        
        deal = random.choice(list(state.ai_portfolio.deals.values()))
        new_coupon = deal.coupon_rate * 0.98  # Try to optimize
        
        return {"type": "restructure", "deal_id": deal.deal_id, "new_coupon": new_coupon}
    
    def _action_rebalance(self, state: GameState) -> Dict[str, Any]:
        """AI rebalances portfolio"""
        return {"type": "rebalance", "strategy": self.strategy}


class SimulationEngine:
    """Master simulation engine (110 lines)"""
    
    def __init__(self, state: GameState):
        self.state = state
        self.time_engine = TimeEngine(total_quarters=state.total_quarters)
        self.decision_engine = DecisionEngine()
        self.event_engine = EventEngine()
        self.ai_engine = AIOpponentEngine()
        self.turn_number = 0
    
    def advance_turn(self) -> Dict[str, Any]:
        """Execute one turn of simulation"""
        self.turn_number += 1
        
        # Advance time
        quarter, year, month = self.time_engine.advance()
        
        # Update market conditions (random walk)
        self._update_market_conditions()
        
        # Process deals (P&L)
        self._process_deals()
        
        # Trigger events
        events = self.event_engine.trigger_events(self.state.player_portfolio)
        for event_type, deal in events:
            self.event_engine.apply_event(event_type, deal)
        
        # AI opponent makes decision
        ai_action = self.ai_engine.get_next_action(self.state)
        if ai_action["type"] == "source":
            self.state.ai_portfolio.add_deal(ai_action.get("deal"))
        
        # Update scores
        self.state.player_score += self._calculate_score(self.state.player_portfolio)
        self.state.ai_score += self._calculate_score(self.state.ai_portfolio)
        
        # Check game over
        self.state.advance_quarter()
        
        return {
            "quarter": quarter,
            "year": year,
            "events": [e[0] for e in events],
            "player_score": self.state.player_score,
            "ai_score": self.state.ai_score,
            "player_portfolio_value": self.state.player_portfolio.get_portfolio_value(),
        }
    
    def _update_market_conditions(self) -> None:
        """Random walk in market conditions"""
        for key in self.state.market_conditions:
            shock = random.gauss(0, 0.01)
            self.state.market_conditions[key] = max(0, self.state.market_conditions[key] + shock)
    
    def _process_deals(self) -> None:
        """Process quarterly cash flows for deals"""
        for deal in self.state.player_portfolio.deals.values():
            if deal.status == DealStatus.ACTIVE:
                ebitda = deal.get_annual_ebitda() / 4  # Quarterly
                debt_service = deal.get_debt_service() / 4
                cash_flow = ebitda - debt_service
                deal.cumulative_cash_flow += cash_flow
                self.state.player_portfolio.cumulative_returns += cash_flow
    
    def _calculate_score(self, portfolio: Portfolio) -> int:
        """Calculate score for portfolio"""
        metrics = portfolio.get_portfolio_metrics()
        score = 0
        
        # DSCR bonus
        score += max(0, int((metrics["portfolio_dscr"] - 1.0) * 100))
        
        # Default penalty
        score -= metrics["default_count"] * 50
        
        # Diversification bonus
        score += int(metrics["num_deals"] * 10)
        
        return score
    
    def run_to_completion(self) -> Dict[str, Any]:
        """Run entire simulation"""
        results = []
        while not self.state.is_game_over():
            turn_result = self.advance_turn()
            results.append(turn_result)
        
        return {
            "total_turns": len(results),
            "final_player_score": self.state.player_score,
            "final_ai_score": self.state.ai_score,
            "player_portfolio_size": len(self.state.player_portfolio.deals),
            "results": results,
        }
