"""
Scoring System - 1000-point gamification system
Complete implementation: 300 lines
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import math

from p5_game_state import Portfolio, GameState


@dataclass
class ScoringBreakdown:
    """Detailed scoring breakdown"""
    pd_accuracy_score: int = 0
    debt_optimization_score: int = 0
    esg_integration_score: int = 0
    portfolio_management_score: int = 0
    total_score: int = 0
    multiplier: float = 1.0
    
    def get_percentage(self) -> Dict[str, float]:
        """Get score percentages"""
        total = self.total_score
        if total == 0:
            return {"each": 0}
        return {
            "pd_accuracy": (self.pd_accuracy_score / total) * 100,
            "debt_optimization": (self.debt_optimization_score / total) * 100,
            "esg_integration": (self.esg_integration_score / total) * 100,
            "portfolio_management": (self.portfolio_management_score / total) * 100,
        }


@dataclass
class PlayerScore:
    """Player score record"""
    player_id: str
    game_id: str
    score: int
    rank: int = 0
    breakdown: ScoringBreakdown = field(default_factory=ScoringBreakdown)
    timestamp: datetime = field(default_factory=datetime.now)
    game_summary: Dict[str, Any] = field(default_factory=dict)


class ScoringSystem:
    """1000-point scoring system (300 lines)"""
    
    MAX_SCORE = 1000
    
    # Scoring weights
    WEIGHTS = {
        "pd_accuracy": 0.25,
        "debt_optimization": 0.25,
        "esg_integration": 0.30,
        "portfolio_management": 0.20,
    }
    
    def __init__(self):
        self.leaderboard: List[PlayerScore] = []
        self.player_scores: Dict[str, int] = {}
    
    def calculate_score(
        self, state: GameState, portfolio: Portfolio
    ) -> ScoringBreakdown:
        """Calculate full score breakdown"""
        breakdown = ScoringBreakdown()
        
        # Component 1: PD Accuracy (250 pts)
        breakdown.pd_accuracy_score = self._score_pd_accuracy(portfolio)
        
        # Component 2: Debt Optimization (250 pts)
        breakdown.debt_optimization_score = self._score_debt_optimization(portfolio)
        
        # Component 3: ESG Integration (300 pts)
        breakdown.esg_integration_score = self._score_esg_integration(portfolio, state)
        
        # Component 4: Portfolio Management (200 pts)
        breakdown.portfolio_management_score = self._score_portfolio_management(portfolio)
        
        # Time-based multiplier
        progress = state.get_game_progress() / 100.0
        time_multiplier = 1.0 + (progress * 0.2)  # Up to 20% bonus for full game
        breakdown.multiplier = time_multiplier
        
        # Total
        breakdown.total_score = int(
            (breakdown.pd_accuracy_score * self.WEIGHTS["pd_accuracy"] +
             breakdown.debt_optimization_score * self.WEIGHTS["debt_optimization"] +
             breakdown.esg_integration_score * self.WEIGHTS["esg_integration"] +
             breakdown.portfolio_management_score * self.WEIGHTS["portfolio_management"])
            * breakdown.multiplier
        )
        
        breakdown.total_score = min(self.MAX_SCORE, breakdown.total_score)
        
        return breakdown
    
    def _score_pd_accuracy(self, portfolio: Portfolio) -> int:
        """PD Accuracy scoring (250 pts max)"""
        score = 0
        
        if not portfolio.deals:
            return 0
        
        # Penalize for defaults
        default_count = portfolio.get_default_count()
        deals_count = len(portfolio.deals)
        
        # Perfect: no defaults
        if default_count == 0:
            score = 250
        # Good: < 5% default rate
        elif (default_count / deals_count) < 0.05:
            score = 200
        # Fair: 5-15% default rate
        elif (default_count / deals_count) < 0.15:
            score = 100
        # Poor: > 15% default rate
        else:
            score = max(0, 250 - (default_count * 25))
        
        # Bonus for high average DSCR
        avg_dscr = portfolio.get_portfolio_dscr()
        if avg_dscr > 1.8:
            score += 50
        elif avg_dscr > 1.5:
            score += 25
        
        return min(250, score)
    
    def _score_debt_optimization(self, portfolio: Portfolio) -> int:
        """Debt Optimization scoring (250 pts max)"""
        score = 0
        
        if not portfolio.deals or portfolio.total_equity_invested == 0:
            return 0
        
        # Check leverage efficiency
        leverage = portfolio.total_debt_raised / portfolio.total_equity_invested
        
        # Optimal range: 0.60-0.75
        if 0.60 <= leverage <= 0.75:
            score = 200
        elif 0.50 <= leverage < 0.60:
            score = 150
        elif 0.75 < leverage <= 0.85:
            score = 100
        else:
            score = max(0, 50 - int(abs(leverage - 0.70) * 100))
        
        # Bonus for good DSCR coverage
        portfolio_dscr = portfolio.get_portfolio_dscr()
        if portfolio_dscr >= 1.5:
            score += 50
        elif portfolio_dscr >= 1.3:
            score += 25
        
        return min(250, score)
    
    def _score_esg_integration(self, portfolio: Portfolio, state: GameState) -> int:
        """ESG Integration scoring (300 pts max)"""
        score = 150  # Base score
        
        if not portfolio.deals:
            return 0
        
        # Green asset allocation (100 pts)
        green_sectors = ["Energy", "Water", "Healthcare"]  # Simplified
        green_value = sum(
            d.equity_amount + d.debt_amount
            for d in portfolio.deals.values()
            if d.sector in green_sectors
        )
        total_value = portfolio.get_portfolio_value()
        
        if total_value > 0:
            green_pct = green_value / total_value
            green_score = int(green_pct * 100)
            score += green_score
        
        # Carbon avoidance (100 pts)
        # Assume Energy/Green deals avoid carbon
        carbon_avoided = sum(
            (d.revenue_annual / 1_000_000)  # Simplified: revenue as proxy
            for d in portfolio.deals.values()
            if d.sector in green_sectors
        )
        carbon_score = min(100, int(carbon_avoided / 10))
        score += carbon_score
        
        # Social impact (100 pts)
        # Assume Energy/Water/Healthcare have social impact
        social_impact_sectors = ["Water", "Healthcare", "Transport"]
        social_value = sum(
            d.equity_amount + d.debt_amount
            for d in portfolio.deals.values()
            if d.sector in social_impact_sectors
        )
        if total_value > 0:
            social_pct = social_value / total_value
            social_score = int(social_pct * 100)
            score += social_score
        
        return min(300, score)
    
    def _score_portfolio_management(self, portfolio: Portfolio) -> int:
        """Portfolio Management scoring (200 pts max)"""
        score = 100  # Base score
        
        if not portfolio.deals:
            return 0
        
        # Diversification (50 pts)
        num_deals = len(portfolio.deals)
        if num_deals >= 5:
            score += 50
        elif num_deals >= 3:
            score += 30
        elif num_deals >= 1:
            score += 10
        
        # Concentration control (50 pts)
        sector_concentration_ok = True
        for sector in ["Transport", "Energy", "Water", "Telecom", "Healthcare"]:
            conc = portfolio.get_sector_concentration(sector)
            if conc > 0.40:  # Generous limit for scoring
                sector_concentration_ok = False
        
        if sector_concentration_ok:
            score += 50
        
        # Sharpe ratio proxy (using DSCR volatility)
        dscrs = [d.get_annual_dscr() for d in portfolio.deals.values() if d.get_annual_dscr() < 999]
        if dscrs:
            import numpy as np
            dscr_std = float(np.std(dscrs))
            sortino_proxy = 1.0 / (dscr_std + 0.1)  # Inverse of volatility
            sortino_score = min(50, int(sortino_proxy * 10))
            score += sortino_score
        
        return min(200, score)
    
    def record_score(self, player_id: str, game_id: str, score: int,
                    breakdown: ScoringBreakdown, portfolio: Portfolio) -> None:
        """Record player score"""
        game_summary = {
            "deals_managed": len(portfolio.deals),
            "total_invested": portfolio.total_equity_invested,
            "total_debt": portfolio.total_debt_raised,
            "defaults": portfolio.total_defaults,
            "returns": portfolio.cumulative_returns,
        }
        
        player_score = PlayerScore(
            player_id=player_id,
            game_id=game_id,
            score=score,
            breakdown=breakdown,
            game_summary=game_summary,
        )
        
        self.leaderboard.append(player_score)
        self.player_scores[player_id] = score
        
        # Update ranks
        self._update_ranks()
    
    def _update_ranks(self) -> None:
        """Update leaderboard ranks"""
        self.leaderboard.sort(key=lambda x: x.score, reverse=True)
        for rank, entry in enumerate(self.leaderboard, 1):
            entry.rank = rank
    
    def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """Get top players"""
        self._update_ranks()
        
        leaders = []
        for entry in self.leaderboard[:top_n]:
            leaders.append({
                "rank": entry.rank,
                "player_id": entry.player_id,
                "score": entry.score,
                "game_id": entry.game_id,
                "timestamp": entry.timestamp.isoformat(),
                "deals_managed": entry.game_summary.get("deals_managed", 0),
            })
        
        return leaders
    
    def get_player_history(self, player_id: str) -> List[Dict]:
        """Get player's game history"""
        player_games = [s for s in self.leaderboard if s.player_id == player_id]
        
        return [{
            "rank": game.rank,
            "score": game.score,
            "game_id": game.game_id,
            "date": game.timestamp.isoformat(),
            "breakdown": {
                "pd_accuracy": game.breakdown.pd_accuracy_score,
                "debt_optimization": game.breakdown.debt_optimization_score,
                "esg_integration": game.breakdown.esg_integration_score,
                "portfolio_management": game.breakdown.portfolio_management_score,
            }
        } for game in player_games]
    
    def get_scoring_info(self) -> Dict[str, Any]:
        """Get scoring system information"""
        return {
            "max_score": self.MAX_SCORE,
            "components": {
                "pd_accuracy": {"max": 250, "weight": self.WEIGHTS["pd_accuracy"]},
                "debt_optimization": {"max": 250, "weight": self.WEIGHTS["debt_optimization"]},
                "esg_integration": {"max": 300, "weight": self.WEIGHTS["esg_integration"]},
                "portfolio_management": {"max": 200, "weight": self.WEIGHTS["portfolio_management"]},
            },
            "time_bonus": "Up to 20% for completing full 40 quarters",
        }
