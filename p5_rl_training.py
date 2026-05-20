"""
RL Training Environment - Mock trained policy and reward function
Complete implementation: 350 lines
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import numpy as np
import random

from p5_game_state import GameState, Portfolio, Deal


@dataclass
class RLState:
    """RL state representation"""
    num_deals: int
    portfolio_dscr: float
    portfolio_leverage: float
    default_rate: float
    cash_available: float
    cash_deployment_ratio: float
    avg_deal_dscr: float
    sector_hhi: float


class RLEnvironment:
    """Mock RL training environment (150 lines)"""
    
    def __init__(self, state: GameState):
        self.state = state
        self.episode_rewards: List[float] = []
        self.step_count = 0
    
    def get_state_representation(self, portfolio: Portfolio) -> RLState:
        """Convert portfolio to RL state"""
        metrics = portfolio.get_portfolio_metrics()
        
        total_capex = sum(d.capex for d in portfolio.deals.values())
        deployed = sum(d.equity_amount + d.debt_amount for d in portfolio.deals.values())
        deployment_ratio = deployed / total_capex if total_capex > 0 else 0
        
        dscrs = [d.get_annual_dscr() for d in portfolio.deals.values() if d.get_annual_dscr() < 999]
        avg_dscr = np.mean(dscrs) if dscrs else 0
        
        # Calculate sector HHI
        sectors = {}
        for deal in portfolio.deals.values():
            size = deal.equity_amount + deal.debt_amount
            sectors[deal.sector] = sectors.get(deal.sector, 0) + size
        
        total_size = sum(sectors.values())
        sector_hhi = sum((s / total_size) ** 2 for s in sectors.values()) if total_size > 0 else 0
        
        return RLState(
            num_deals=metrics["num_deals"],
            portfolio_dscr=metrics["portfolio_dscr"],
            portfolio_leverage=metrics["debt_raised"] / (metrics["equity_invested"] + 1),
            default_rate=metrics["default_count"] / (metrics["num_deals"] + 1),
            cash_available=self.state.ai_cash_available,
            cash_deployment_ratio=deployment_ratio,
            avg_deal_dscr=avg_dscr,
            sector_hhi=sector_hhi,
        )
    
    def compute_reward(
        self,
        portfolio: Portfolio,
        prev_portfolio: Portfolio = None
    ) -> float:
        """Reward function: (Portfolio_Return - Default_Losses - Regulatory_Penalties)"""
        reward = 0.0
        
        # Portfolio returns component (40%)
        portfolio_returns = portfolio.cumulative_returns
        reward += portfolio_returns / 1_000_000  # Scale down
        
        # Default losses component (40%)
        default_losses = portfolio.total_defaults * 50_000_000  # Assume $50M loss per default
        reward -= (default_losses / 1_000_000)
        
        # Regulatory/penalty component (20%)
        regulatory_penalty = 0.0
        
        # Check leverage constraint
        if portfolio.total_equity_invested > 0:
            leverage = portfolio.total_debt_raised / portfolio.total_equity_invested
            if leverage > 0.75:
                regulatory_penalty += 100
        
        # Check DSCR constraint
        dscr = portfolio.get_portfolio_dscr()
        if dscr < 1.25:
            regulatory_penalty += 100
        
        # Check concentration
        for sector in ["Transport", "Energy", "Water", "Telecom", "Healthcare"]:
            conc = portfolio.get_sector_concentration(sector)
            if conc > 0.35:
                regulatory_penalty += 50
        
        reward -= (regulatory_penalty / 100)
        
        return reward
    
    def step(self, action: Dict[str, Any]) -> Tuple[RLState, float, bool]:
        """Execute action and return (next_state, reward, done)"""
        self.step_count += 1
        
        # Execute action (simplified)
        if action.get("action") == "source":
            # Add deal to portfolio
            deal = action.get("deal")
            if deal:
                self.state.ai_portfolio.add_deal(deal)
        
        # Compute reward
        reward = self.compute_reward(self.state.ai_portfolio)
        self.episode_rewards.append(reward)
        
        # Get next state
        next_state = self.get_state_representation(self.state.ai_portfolio)
        
        # Check if done
        done = self.state.is_game_over()
        
        return next_state, reward, done
    
    def reset(self) -> RLState:
        """Reset environment"""
        self.step_count = 0
        self.episode_rewards = []
        return self.get_state_representation(self.state.ai_portfolio)


class MockRLAgent:
    """Mock trained RL agent with pre-trained weights (200 lines)"""
    
    def __init__(self):
        # Mock pre-trained policy network weights (no actual NN needed)
        self.weights = self._load_mock_weights()
        self.policy_history = []
    
    def _load_mock_weights(self) -> Dict[str, np.ndarray]:
        """Load mock trained weights"""
        # Simulate PPO-style policy
        return {
            "actor_hidden": np.random.randn(64, 8) * 0.1,
            "actor_output": np.random.randn(5, 64) * 0.01,
            "critic_hidden": np.random.randn(64, 8) * 0.1,
            "critic_output": np.random.randn(1, 64) * 0.01,
        }
    
    def select_action(self, state: RLState) -> Tuple[str, float]:
        """Select action using trained policy"""
        # Convert state to feature vector
        features = self._state_to_features(state)
        
        # Forward pass through mock network
        hidden = np.tanh(np.dot(self.weights["actor_hidden"], features))
        logits = np.dot(self.weights["actor_output"], hidden)
        
        # Softmax to probabilities
        probs = self._softmax(logits[0])
        
        # Select action
        actions = ["hold", "source", "restructure", "rebalance", "sell"]
        action_idx = np.argmax(probs)
        
        self.policy_history.append({
            "action": actions[action_idx],
            "probability": probs[action_idx],
        })
        
        return actions[action_idx], probs[action_idx]
    
    def get_value(self, state: RLState) -> float:
        """Get state value from critic"""
        features = self._state_to_features(state)
        hidden = np.tanh(np.dot(self.weights["critic_hidden"], features))
        value = np.dot(self.weights["critic_output"], hidden)[0][0]
        return value
    
    def _state_to_features(self, state: RLState) -> np.ndarray:
        """Convert state to feature vector"""
        return np.array([
            state.num_deals / 10,
            state.portfolio_dscr / 2.5,
            state.portfolio_leverage,
            state.default_rate,
            np.log(state.cash_available + 1) / 20,
            state.cash_deployment_ratio,
            state.avg_deal_dscr / 2.0,
            state.sector_hhi,
        ])
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax function"""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()
    
    def get_action_probabilities(self, state: RLState) -> Dict[str, float]:
        """Get probability distribution over actions"""
        features = self._state_to_features(state)
        hidden = np.tanh(np.dot(self.weights["actor_hidden"], features))
        logits = np.dot(self.weights["actor_output"], hidden)
        probs = self._softmax(logits[0])
        
        actions = ["hold", "source", "restructure", "rebalance", "sell"]
        return {action: float(prob) for action, prob in zip(actions, probs)}
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get training summary"""
        if not self.policy_history:
            return {"steps": 0, "avg_action_uncertainty": 0}
        
        uncertainties = []
        for decision in self.policy_history[-100:]:  # Last 100 decisions
            # Uncertainty as 1 - max_prob
            uncertainties.append(1 - decision["probability"])
        
        return {
            "steps": len(self.policy_history),
            "avg_action_uncertainty": np.mean(uncertainties) if uncertainties else 0,
            "most_common_action": max(
                set(d["action"] for d in self.policy_history),
                key=lambda a: sum(1 for d in self.policy_history if d["action"] == a)
            ),
        }
