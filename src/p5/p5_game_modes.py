"""
Game Modes - Single Deal, Portfolio Manager, Crisis Manager, Deal Structurer
Complete implementation: 320 lines
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    from .p5_game_state import GameState, Deal, DealStatus, Portfolio
except ImportError:  # pragma: no cover - supports direct script execution
    from p5_game_state import GameState, Deal, DealStatus, Portfolio


class GameMode(Enum):
    """Available game modes"""
    SINGLE_DEAL = "single_deal"
    PORTFOLIO_MANAGER = "portfolio_manager"
    CRISIS_MANAGER = "crisis_manager"
    DEAL_STRUCTURER = "deal_structurer"


@dataclass
class GameModeConfig:
    """Configuration for game mode"""
    mode: GameMode
    name: str
    description: str
    duration_quarters: int
    initial_cash: float
    num_initial_deals: int
    difficulty: str
    learning_curve: str


class GameModes:
    """Game mode manager (320 lines)"""
    
    MODES = {
        GameMode.SINGLE_DEAL: GameModeConfig(
            mode=GameMode.SINGLE_DEAL,
            name="Single Deal (Tutorial)",
            description="Manage one infrastructure project for 5 years. Learn debt structuring.",
            duration_quarters=20,
            initial_cash=500_000_000,
            num_initial_deals=1,
            difficulty="Beginner",
            learning_curve="5 years: Basic structuring → DSCR management → Refinancing",
        ),
        GameMode.PORTFOLIO_MANAGER: GameModeConfig(
            mode=GameMode.PORTFOLIO_MANAGER,
            name="Portfolio Manager (Main)",
            description="Build portfolio of 5-15 projects over 10 years. Diversify sectors/geographies.",
            duration_quarters=40,
            initial_cash=1_000_000_000,
            num_initial_deals=2,
            difficulty="Intermediate",
            learning_curve="Deal sourcing → Structuring → Risk mgmt → ESG integration",
        ),
        GameMode.CRISIS_MANAGER: GameModeConfig(
            mode=GameMode.CRISIS_MANAGER,
            name="Crisis Manager",
            description="Handle construction delays and refinancing crises. Stress management.",
            duration_quarters=16,
            initial_cash=750_000_000,
            num_initial_deals=4,
            difficulty="Expert",
            learning_curve="Crisis response → Covenant negotiation → Portfolio restructuring",
        ),
        GameMode.DEAL_STRUCTURER: GameModeConfig(
            mode=GameMode.DEAL_STRUCTURER,
            name="Deal Structurer (Optimization)",
            description="Minimize cost of capital. Maximize DSCR within constraints.",
            duration_quarters=8,
            initial_cash=500_000_000,
            num_initial_deals=3,
            difficulty="Advanced",
            learning_curve="Debt optimization → Tenor structuring → Covenant design",
        ),
    }
    
    def __init__(self):
        self.current_mode: Optional[GameMode] = None
    
    def select_mode(self, mode: GameMode) -> GameState:
        """Initialize game for selected mode"""
        self.current_mode = mode
        config = self.MODES[mode]
        
        # Create initial game state
        state = GameState(
            game_mode=mode.value,
            total_quarters=config.duration_quarters,
            cash_available=config.initial_cash,
            ai_cash_available=config.initial_cash,
        )
        
        # Initialize with starter deals
        if config.num_initial_deals > 0:
            starter_deals = self._generate_starter_deals(config.num_initial_deals, mode)
            for deal in starter_deals:
                state.player_portfolio.add_deal(deal)
                state.ai_portfolio.add_deal(self._create_ai_deal())
        
        return state
    
    def _generate_starter_deals(self, num_deals: int, mode: GameMode) -> List[Deal]:
        """Generate starter deals based on mode"""
        deals = []
        
        if mode == GameMode.SINGLE_DEAL:
            deal = Deal(
                name="National Highway Project",
                sector="Transport",
                country="India",
                capex=300_000_000,
                tenor_years=25,
                revenue_annual=40_000_000,
                opex_annual=15_000_000,
                probability_of_default=0.04,
                dscr=1.8,
            )
            deal.status = DealStatus.SOURCED
            deals.append(deal)
        
        elif mode == GameMode.PORTFOLIO_MANAGER:
            # Two initial deals
            deal1 = Deal(
                name="Solar Farm (Gujarat)",
                sector="Energy",
                country="India",
                capex=150_000_000,
                tenor_years=20,
                revenue_annual=25_000_000,
                opex_annual=8_000_000,
                probability_of_default=0.03,
                dscr=1.8,
            )
            deal1.status = DealStatus.SOURCED
            deals.append(deal1)
            
            deal2 = Deal(
                name="Water Treatment Plant",
                sector="Water",
                country="Brazil",
                capex=120_000_000,
                tenor_years=15,
                revenue_annual=18_000_000,
                opex_annual=6_000_000,
                probability_of_default=0.05,
                dscr=1.6,
            )
            deal2.status = DealStatus.SOURCED
            deals.append(deal2)
        
        elif mode == GameMode.CRISIS_MANAGER:
            # Four risky deals
            for i in range(4):
                deal = Deal(
                    name=f"Crisis Deal {i+1}",
                    sector=["Transport", "Energy", "Water", "Telecom"][i],
                    country=["India", "Nigeria", "Egypt", "Vietnam"][i],
                    capex=100_000_000 + (i * 50_000_000),
                    tenor_years=10 + (i * 2),
                    revenue_annual=15_000_000 + (i * 5_000_000),
                    opex_annual=7_000_000 + (i * 2_000_000),
                    probability_of_default=0.08 + (i * 0.02),
                    dscr=1.3 + (i * 0.1),
                    construction_delay_quarters=2 + (i * 1),
                )
                deal.status = DealStatus.ACTIVE
                deals.append(deal)
        
        elif mode == GameMode.DEAL_STRUCTURER:
            # Three deals needing optimization
            for i in range(3):
                deal = Deal(
                    name=f"Optimization Deal {i+1}",
                    sector=["Transport", "Energy", "Healthcare"][i],
                    country=["India", "Brazil", "Nigeria"][i],
                    capex=80_000_000 + (i * 40_000_000),
                    tenor_years=12 + (i * 3),
                    revenue_annual=12_000_000 + (i * 6_000_000),
                    opex_annual=5_000_000 + (i * 2_000_000),
                    probability_of_default=0.05 + (i * 0.01),
                    dscr=1.5 + (i * 0.2),
                )
                deal.status = DealStatus.SOURCED
                deals.append(deal)
        
        return deals
    
    def _create_ai_deal(self) -> Deal:
        """Create deal for AI opponent"""
        import random
        return Deal(
            name=f"AI_Deal_{random.randint(1000, 9999)}",
            sector=random.choice(["Transport", "Energy", "Water"]),
            country=random.choice(["India", "Brazil", "Nigeria"]),
            capex=random.uniform(100_000_000, 250_000_000),
            tenor_years=random.randint(12, 20),
            revenue_annual=random.uniform(15_000_000, 50_000_000),
            opex_annual=random.uniform(7_000_000, 25_000_000),
        )
    
    def get_mode_info(self, mode: GameMode = None) -> Dict[str, Any]:
        """Get information about game mode"""
        if mode is None:
            mode = self.current_mode
        
        if mode is None:
            return {}
        
        config = self.MODES[mode]
        
        return {
            "mode": config.mode.value,
            "name": config.name,
            "description": config.description,
            "difficulty": config.difficulty,
            "duration": f"{config.duration_quarters} quarters ({config.duration_quarters // 4} years)",
            "initial_cash": f"${config.initial_cash:,.0f}",
            "starter_deals": config.num_initial_deals,
            "learning_curve": config.learning_curve,
            "objectives": self._get_mode_objectives(mode),
        }
    
    def _get_mode_objectives(self, mode: GameMode) -> List[str]:
        """Get objectives for each mode"""
        objectives = {
            GameMode.SINGLE_DEAL: [
                "Achieve DSCR > 1.5x",
                "Keep PD < 5%",
                "Complete project on time",
                "Minimize cost of capital",
            ],
            GameMode.PORTFOLIO_MANAGER: [
                "Build portfolio of 5+ deals",
                "Achieve portfolio DSCR > 1.4x",
                "Diversify: no sector > 35%",
                "Cumulative returns > $200M",
                "Minimize defaults < 5%",
            ],
            GameMode.CRISIS_MANAGER: [
                "Handle refinancing crises",
                "Manage construction delays",
                "Keep covenant compliance",
                "Prevent cascade defaults",
                "Recover from crisis",
            ],
            GameMode.DEAL_STRUCTURER: [
                "Minimize weighted avg cost of capital",
                "Optimize debt/tenor mix",
                "Design covenants",
                "Achieve DSCR target",
                "Complete 3 deals",
            ],
        }
        return objectives.get(mode, [])
    
    def get_all_modes(self) -> List[Dict[str, Any]]:
        """Get all available modes"""
        modes_list = []
        for mode in GameMode:
            modes_list.append(self.get_mode_info(mode))
        return modes_list
    
    def validate_mode_completion(self, state: GameState, portfolio: Portfolio) -> Dict[str, bool]:
        """Validate if mode objectives were met"""
        if state.game_mode == GameMode.SINGLE_DEAL.value:
            return {
                "dscr_target": portfolio.get_portfolio_dscr() > 1.5,
                "pd_acceptable": portfolio.get_default_count() == 0,
                "deals_completed": any(d.status == DealStatus.MATURED for d in portfolio.deals.values()),
            }
        
        elif state.game_mode == GameMode.PORTFOLIO_MANAGER.value:
            return {
                "portfolio_size": len(portfolio.deals) >= 5,
                "dscr_target": portfolio.get_portfolio_dscr() > 1.4,
                "diversification": all(
                    portfolio.get_sector_concentration(s) < 0.35
                    for s in ["Transport", "Energy", "Water", "Telecom", "Healthcare"]
                ),
                "returns_target": portfolio.cumulative_returns > 200_000_000,
                "default_acceptable": portfolio.get_default_count() <= 1,
            }
        
        elif state.game_mode == GameMode.CRISIS_MANAGER.value:
            return {
                "crisis_handled": len(portfolio.deals) > 0,
                "covenant_compliance": portfolio.get_portfolio_dscr() > 1.1,
                "recovery": portfolio.cumulative_returns > 0,
            }
        
        elif state.game_mode == GameMode.DEAL_STRUCTURER.value:
            avg_coupon = sum(d.coupon_rate for d in portfolio.deals.values()) / (len(portfolio.deals) + 1)
            return {
                "deals_completed": len(portfolio.deals) >= 3,
                "dscr_optimized": portfolio.get_portfolio_dscr() > 1.4,
                "wacc_minimized": avg_coupon < 0.06,
            }
        
        return {}
    
    def get_mode_tips(self, mode: GameMode) -> List[str]:
        """Get tips for game mode"""
        tips = {
            GameMode.SINGLE_DEAL: [
                "Start with structuring: set debt/equity ratio",
                "Monitor DSCR quarterly - it's your key metric",
                "Build cash reserves for unexpected delays",
                "Understand how construction delays impact DSCR",
            ],
            GameMode.PORTFOLIO_MANAGER: [
                "Diversify: aim for 5-7 deals in different sectors",
                "Balance growth with risk: not all deals are equal",
                "Watch portfolio DSCR, not just individual deals",
                "ESG integration scores 300/1000 points!",
                "React to events: can't plan for everything",
            ],
            GameMode.CRISIS_MANAGER: [
                "Refinancing crises last 2 quarters - prepare!",
                "Construction delays compound: 1 month → 3 months",
                "Default cascades: save deals before covenant breach",
                "Restructure early: high coupon means default risk",
            ],
            GameMode.DEAL_STRUCTURER: [
                "Cost of capital = weighted avg coupon rate",
                "Tenor optimization: longer tenors → lower DSCR",
                "Covenant staircase: gradually tighter restrictions",
                "Test your structure against scenarios",
            ],
        }
        return tips.get(mode, [])
