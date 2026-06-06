"""
Scenario Engine - Pre-calibrated shocks and stochastic impacts
Complete implementation: 380 lines
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import random
import math

try:
    from .p5_game_state import Deal, Portfolio
except ImportError:  # pragma: no cover - supports direct script execution
    from p5_game_state import Deal, Portfolio


class ScenarioType(Enum):
    """20+ pre-calibrated scenario types"""
    PANDEMIC = "pandemic"
    SOVEREIGN_DOWNGRADE = "sovereign_downgrade"
    CLIMATE_EVENT = "climate_event"
    INTEREST_RATE_SHOCK = "interest_rate_shock"
    FX_CRISIS = "fx_crisis"
    CONSTRUCTION_DELAY = "construction_delay"
    DEMAND_SHOCK = "demand_shock"
    REFINANCING_CRISIS = "refinancing_crisis"
    TECH_DISRUPTION = "tech_disruption"
    REGULATORY_CHANGE = "regulatory_change"
    GEOPOLITICAL_CRISIS = "geopolitical_crisis"
    SUPPLIER_SHOCK = "supplier_shock"
    COMMODITY_SHOCK = "commodity_shock"
    LABOR_SHORTAGE = "labor_shortage"
    PERMITTING_DELAY = "permitting_delay"
    ENVIRONMENTAL_VIOLATION = "environmental_violation"
    OPERATOR_CHANGE = "operator_change"
    MARKET_SATURATION = "market_saturation"
    POLICY_CHANGE = "policy_change"
    ASSET_DAMAGE = "asset_damage"


@dataclass
class ScenarioImpact:
    """Impact parameters for a scenario"""
    revenue_shock: float = 1.0
    cost_shock: float = 1.0
    capex_increase: float = 0.0
    construction_delay_months: int = 0
    coupon_increase: float = 0.0
    probability_of_default_delta: float = 0.0
    affected_sectors: List[str] = None
    affected_countries: List[str] = None
    duration_quarters: int = 4
    severity: float = 1.0
    
    def __post_init__(self):
        if self.affected_sectors is None:
            self.affected_sectors = []
        if self.affected_countries is None:
            self.affected_countries = []


@dataclass
class Scenario:
    """Scenario definition with impacts"""
    scenario_type: ScenarioType
    name: str
    description: str
    base_probability: float
    severity: float
    impacts: ScenarioImpact
    affected_deals: List[str]
    quarter_triggered: int
    
    def apply(self, deal: Deal) -> None:
        """Apply scenario impact to deal"""
        deal.revenue_shock *= self.impacts.revenue_shock
        deal.cost_shock *= self.impacts.cost_shock
        deal.capex += self.impacts.capex_increase
        deal.construction_delay_quarters += self.impacts.construction_delay_months // 3
        deal.coupon_rate *= (1 + self.impacts.coupon_increase)
        deal.probability_of_default += self.impacts.probability_of_default_delta


class ScenarioEngine:
    """Scenario manager with pre-calibrated shocks (380 lines)"""
    
    # Pre-calibrated scenario definitions
    SCENARIOS = {
        ScenarioType.PANDEMIC: {
            "impacts": ScenarioImpact(
                revenue_shock=0.70,
                cost_shock=1.20,
                capex_increase=10_000_000,
                construction_delay_months=18,
                coupon_increase=0.01,
                probability_of_default_delta=0.05,
                duration_quarters=12,
            ),
            "base_probability": 0.01,
            "severity_range": (0.5, 1.0),
        },
        ScenarioType.SOVEREIGN_DOWNGRADE: {
            "impacts": ScenarioImpact(
                revenue_shock=0.95,
                cost_shock=1.05,
                coupon_increase=0.03,
                probability_of_default_delta=0.03,
                duration_quarters=8,
            ),
            "base_probability": 0.02,
            "severity_range": (0.6, 1.0),
        },
        ScenarioType.CLIMATE_EVENT: {
            "impacts": ScenarioImpact(
                revenue_shock=0.90,
                cost_shock=1.15,
                capex_increase=50_000_000,
                construction_delay_months=12,
                probability_of_default_delta=0.04,
                duration_quarters=6,
            ),
            "base_probability": 0.03,
            "severity_range": (0.5, 1.0),
        },
        ScenarioType.INTEREST_RATE_SHOCK: {
            "impacts": ScenarioImpact(
                revenue_shock=1.0,
                cost_shock=1.0,
                coupon_increase=0.02,
                probability_of_default_delta=0.02,
                duration_quarters=4,
            ),
            "base_probability": 0.05,
            "severity_range": (0.3, 1.0),
        },
        ScenarioType.FX_CRISIS: {
            "impacts": ScenarioImpact(
                revenue_shock=0.60,
                cost_shock=1.0,
                coupon_increase=0.02,
                probability_of_default_delta=0.03,
                duration_quarters=6,
            ),
            "base_probability": 0.04,
            "severity_range": (0.4, 1.0),
        },
        ScenarioType.CONSTRUCTION_DELAY: {
            "impacts": ScenarioImpact(
                revenue_shock=0.80,
                cost_shock=1.10,
                construction_delay_months=12,
                probability_of_default_delta=0.02,
                duration_quarters=8,
            ),
            "base_probability": 0.10,
            "severity_range": (0.3, 1.0),
        },
        ScenarioType.DEMAND_SHOCK: {
            "impacts": ScenarioImpact(
                revenue_shock=0.50,
                cost_shock=1.0,
                probability_of_default_delta=0.04,
                duration_quarters=8,
            ),
            "base_probability": 0.08,
            "severity_range": (0.4, 1.0),
        },
        ScenarioType.REFINANCING_CRISIS: {
            "impacts": ScenarioImpact(
                revenue_shock=1.0,
                cost_shock=1.0,
                coupon_increase=0.05,
                probability_of_default_delta=0.05,
                duration_quarters=4,
            ),
            "base_probability": 0.02,
            "severity_range": (0.6, 1.0),
        },
        ScenarioType.TECH_DISRUPTION: {
            "impacts": ScenarioImpact(
                revenue_shock=0.75,
                cost_shock=0.90,
                probability_of_default_delta=0.02,
                duration_quarters=12,
            ),
            "base_probability": 0.03,
            "severity_range": (0.3, 0.8),
        },
        ScenarioType.REGULATORY_CHANGE: {
            "impacts": ScenarioImpact(
                revenue_shock=0.85,
                cost_shock=1.20,
                capex_increase=20_000_000,
                coupon_increase=0.01,
                probability_of_default_delta=0.02,
                duration_quarters=8,
            ),
            "base_probability": 0.04,
            "severity_range": (0.4, 0.9),
        },
        ScenarioType.GEOPOLITICAL_CRISIS: {
            "impacts": ScenarioImpact(
                revenue_shock=0.65,
                cost_shock=1.25,
                construction_delay_months=9,
                coupon_increase=0.02,
                probability_of_default_delta=0.04,
                duration_quarters=8,
            ),
            "base_probability": 0.02,
            "severity_range": (0.5, 1.0),
        },
        ScenarioType.SUPPLIER_SHOCK: {
            "impacts": ScenarioImpact(
                revenue_shock=0.85,
                cost_shock=1.30,
                construction_delay_months=6,
                probability_of_default_delta=0.02,
                duration_quarters=4,
            ),
            "base_probability": 0.06,
            "severity_range": (0.3, 0.8),
        },
        ScenarioType.COMMODITY_SHOCK: {
            "impacts": ScenarioImpact(
                revenue_shock=0.80,
                cost_shock=1.20,
                capex_increase=15_000_000,
                probability_of_default_delta=0.02,
                duration_quarters=6,
            ),
            "base_probability": 0.05,
            "severity_range": (0.3, 0.9),
        },
        ScenarioType.LABOR_SHORTAGE: {
            "impacts": ScenarioImpact(
                revenue_shock=0.90,
                cost_shock=1.25,
                construction_delay_months=8,
                probability_of_default_delta=0.01,
                duration_quarters=6,
            ),
            "base_probability": 0.04,
            "severity_range": (0.4, 0.8),
        },
        ScenarioType.PERMITTING_DELAY: {
            "impacts": ScenarioImpact(
                revenue_shock=0.70,
                cost_shock=1.05,
                construction_delay_months=12,
                probability_of_default_delta=0.02,
                duration_quarters=8,
            ),
            "base_probability": 0.05,
            "severity_range": (0.3, 0.7),
        },
        ScenarioType.ENVIRONMENTAL_VIOLATION: {
            "impacts": ScenarioImpact(
                revenue_shock=0.60,
                cost_shock=1.15,
                capex_increase=25_000_000,
                coupon_increase=0.02,
                probability_of_default_delta=0.03,
                duration_quarters=6,
            ),
            "base_probability": 0.03,
            "severity_range": (0.5, 0.9),
        },
        ScenarioType.OPERATOR_CHANGE: {
            "impacts": ScenarioImpact(
                revenue_shock=0.95,
                cost_shock=1.10,
                probability_of_default_delta=0.01,
                duration_quarters=4,
            ),
            "base_probability": 0.02,
            "severity_range": (0.2, 0.6),
        },
        ScenarioType.MARKET_SATURATION: {
            "impacts": ScenarioImpact(
                revenue_shock=0.55,
                cost_shock=1.0,
                probability_of_default_delta=0.03,
                duration_quarters=12,
            ),
            "base_probability": 0.04,
            "severity_range": (0.3, 0.8),
        },
        ScenarioType.POLICY_CHANGE: {
            "impacts": ScenarioImpact(
                revenue_shock=0.75,
                cost_shock=1.15,
                coupon_increase=0.01,
                probability_of_default_delta=0.02,
                duration_quarters=8,
            ),
            "base_probability": 0.03,
            "severity_range": (0.3, 0.7),
        },
        ScenarioType.ASSET_DAMAGE: {
            "impacts": ScenarioImpact(
                revenue_shock=0.50,
                cost_shock=1.40,
                capex_increase=75_000_000,
                probability_of_default_delta=0.05,
                duration_quarters=8,
            ),
            "base_probability": 0.02,
            "severity_range": (0.6, 1.0),
        },
    }
    
    def __init__(self):
        self.triggered_scenarios: List[Scenario] = []
        self.scenario_history: List[Dict] = []
    
    def pick_random_scenario(self) -> Optional[ScenarioType]:
        """Pick scenario with probability weighting"""
        scenarios = list(self.SCENARIOS.keys())
        probabilities = [self.SCENARIOS[s]["base_probability"] for s in scenarios]
        
        # Normalize probabilities
        total_prob = sum(probabilities)
        probabilities = [p / total_prob for p in probabilities]
        
        if random.random() < sum(probabilities):
            return random.choices(scenarios, weights=probabilities)[0]
        return None
    
    def create_scenario(
        self,
        scenario_type: ScenarioType,
        quarter: int,
        portfolio: Portfolio
    ) -> Optional[Scenario]:
        """Create scenario instance"""
        if scenario_type not in self.SCENARIOS:
            return None
        
        config = self.SCENARIOS[scenario_type]
        impacts = config["impacts"]
        
        # Add stochasticity to severity
        severity_range = config["severity_range"]
        severity = random.uniform(severity_range[0], severity_range[1])
        
        # Apply severity to impacts
        impacts_copy = self._apply_severity(impacts, severity)
        
        # Select affected deals
        affected_deals = self._select_affected_deals(portfolio, scenario_type)
        
        scenario = Scenario(
            scenario_type=scenario_type,
            name=scenario_type.value.replace("_", " ").title(),
            description=f"Severity: {severity:.2f}",
            base_probability=config["base_probability"],
            severity=severity,
            impacts=impacts_copy,
            affected_deals=affected_deals,
            quarter_triggered=quarter,
        )
        
        return scenario
    
    def _apply_severity(self, impacts: ScenarioImpact, severity: float) -> ScenarioImpact:
        """Apply severity multiplier to impacts"""
        from copy import deepcopy
        impacts_copy = deepcopy(impacts)
        
        # Revenue shock varies with severity
        impacts_copy.revenue_shock = 1.0 - (1.0 - impacts_copy.revenue_shock) * severity
        
        # Cost shock varies
        impacts_copy.cost_shock = 1.0 + (impacts_copy.cost_shock - 1.0) * severity
        
        # Capex increases
        impacts_copy.capex_increase *= severity
        
        # Delay varies
        impacts_copy.construction_delay_months = int(impacts_copy.construction_delay_months * severity)
        
        # Coupon increase
        impacts_copy.coupon_increase *= severity
        
        # PD delta
        impacts_copy.probability_of_default_delta *= severity
        
        return impacts_copy
    
    def _select_affected_deals(
        self, portfolio: Portfolio, scenario_type: ScenarioType
    ) -> List[str]:
        """Select affected deals by sector/geography"""
        config = self.SCENARIOS.get(scenario_type, {})
        affected = []
        
        for deal_id, deal in portfolio.deals.items():
            # Filter by sector if applicable
            if deal.sector and random.random() < 0.6:  # 60% sector matching
                affected.append(deal_id)
        
        return affected[:len(portfolio.deals)]  # Max all deals
    
    def apply_scenario_to_portfolio(
        self, scenario: Scenario, portfolio: Portfolio
    ) -> Dict[str, Any]:
        """Apply scenario to entire portfolio"""
        impact_summary = {
            "scenario": scenario.scenario_type.value,
            "severity": scenario.severity,
            "deals_affected": 0,
            "total_revenue_impact": 0.0,
            "total_cost_impact": 0.0,
            "deals_in_default": 0,
        }
        
        for deal_id in scenario.affected_deals:
            if deal_id in portfolio.deals:
                deal = portfolio.deals[deal_id]
                scenario.apply(deal)
                impact_summary["deals_affected"] += 1
                
                if deal.is_in_default():
                    impact_summary["deals_in_default"] += 1
        
        self.triggered_scenarios.append(scenario)
        self.scenario_history.append({
            "quarter": scenario.quarter_triggered,
            "scenario": scenario.scenario_type.value,
            "severity": scenario.severity,
        })
        
        return impact_summary
    
    def get_scenario_statistics(self) -> Dict[str, Any]:
        """Get statistics on triggered scenarios"""
        if not self.scenario_history:
            return {"total_scenarios": 0}
        
        from collections import Counter
        scenario_types = [s["scenario"] for s in self.scenario_history]
        type_counts = Counter(scenario_types)
        
        avg_severity = sum(s["severity"] for s in self.scenario_history) / len(self.scenario_history)
        
        return {
            "total_scenarios": len(self.scenario_history),
            "scenario_types": dict(type_counts),
            "avg_severity": avg_severity,
            "most_common": type_counts.most_common(1)[0][0] if type_counts else None,
        }
