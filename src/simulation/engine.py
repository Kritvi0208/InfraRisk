"""InfraRisk Lab simulation engine"""
from dataclasses import dataclass
from typing import Dict, List
import random

@dataclass
class SimulationState:
    quarter: int
    portfolio_dscr: float
    events: List[str]
    score: int

class SimulationEngine:
    def __init__(self, initial_dscr: float = 1.38):
        self.state = SimulationState(quarter=0, portfolio_dscr=initial_dscr, events=[], score=0)

    def step(self) -> SimulationState:
        """Advance simulation by one quarter"""
        self.state.quarter += 1
        
        # Random events
        if random.random() < 0.15:
            self.state.events.append("cost_overrun")
            self.state.portfolio_dscr *= 0.95
        
        if random.random() < 0.08:
            self.state.events.append("demand_shortfall")
            self.state.portfolio_dscr *= 0.98
        
        self.state.score += max(0, int((self.state.portfolio_dscr - 1.0) * 100))
        return self.state

    def reset(self):
        self.state = SimulationState(quarter=0, portfolio_dscr=1.38, events=[], score=0)
