"""
Phase 5: Gamified Simulation & Dashboard
Integrated simulation platform with game modes, scoring, and dashboard.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

__version__ = "5.0.0"
__all__ = [
    "GameState",
    "StateManager",
    "Portfolio",
    "Deal",
    "SimulationEngine",
    "ScenarioEngine",
    "AIOpponent",
    "OpponentRules",
    "RLEnvironment",
    "ScoringSystem",
    "GameMode",
    "EventTrigger",
]
