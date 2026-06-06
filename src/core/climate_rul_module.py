"""
Climate-Adjusted Remaining Useful Life (CA-RUL) Module

Implements climate-adjusted RUL calculations with IPCC scenarios (RCP 4.5, RCP 8.5).

Formula: CA-RUL = Baseline_RUL × (1 - temp_increase × 0.03) × (1 - |precip_change| × 0.01)

Example usage:
    >>> ca_rul = ClimateAdjustedRUL(baseline_rul=30)
    >>> features = ca_rul.calculate_ca_rul(
    ...     temp_increase=2.5,
    ...     precip_change=-15.0,
    ...     scenario="rcp85"
    ... )
    >>> print(features['ca_rul'], features['degradation_factor'])
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


class ClimateScenario(Enum):
    """IPCC Climate Scenario Definitions"""
    RCP45 = "rcp45"  # Stabilization at 4.5 W/m²
    RCP85 = "rcp85"  # High-emission scenario at 8.5 W/m²
    BASELINE = "baseline"  # No climate change


@dataclass
class DegradationParameters:
    """Material degradation factors for different infrastructure types"""
    infrastructure_type: str
    base_degradation_rate: float  # Annual baseline degradation rate
    temp_sensitivity: float = 0.03  # Degradation increase per °C
    precip_sensitivity: float = 0.01  # Degradation increase per % precipitation change
    humidity_multiplier: float = 1.2  # Moisture-related acceleration
    salt_exposure: float = 0.0  # For coastal infrastructure


@dataclass
class IPCCScenarioData:
    """IPCC climate scenario projections"""
    scenario: ClimateScenario
    year: int
    temperature_increase: float  # °C above baseline
    precipitation_change: float  # % change from baseline
    sea_level_rise: float  # cm
    frequency_extreme_events: float  # ratio multiplier


class ClimateAdjustedRUL:
    """
    Computes Climate-Adjusted RUL for infrastructure assets.
    
    Incorporates temperature and precipitation impacts on material degradation.
    Supports multiple IPCC RCP scenarios for scenario analysis.
    """

    def __init__(self, baseline_rul: float, infrastructure_type: str = "road"):
        """
        Initialize CA-RUL calculator.
        
        Args:
            baseline_rul: Design life in years (e.g., 30 for asphalt roads)
            infrastructure_type: Type of infrastructure (road, bridge, power, port)
        """
        self.baseline_rul = baseline_rul
        self.infrastructure_type = infrastructure_type
        self._initialize_degradation_params()

    def _initialize_degradation_params(self) -> None:
        """Set degradation parameters by infrastructure type"""
        params_map = {
            "road": DegradationParameters(
                infrastructure_type="road",
                base_degradation_rate=0.033,
                temp_sensitivity=0.035,
                precip_sensitivity=0.012,
                humidity_multiplier=1.3,
                salt_exposure=0.05,
            ),
            "bridge": DegradationParameters(
                infrastructure_type="bridge",
                base_degradation_rate=0.015,
                temp_sensitivity=0.025,
                precip_sensitivity=0.010,
                humidity_multiplier=1.5,
                salt_exposure=0.08,
            ),
            "power": DegradationParameters(
                infrastructure_type="power",
                base_degradation_rate=0.020,
                temp_sensitivity=0.040,
                precip_sensitivity=0.008,
                humidity_multiplier=1.2,
                salt_exposure=0.03,
            ),
            "port": DegradationParameters(
                infrastructure_type="port",
                base_degradation_rate=0.045,
                temp_sensitivity=0.030,
                precip_sensitivity=0.015,
                humidity_multiplier=1.8,
                salt_exposure=0.15,
            ),
        }
        self.degradation_params = params_map.get(
            self.infrastructure_type, params_map["road"]
        )

    def _generate_ipcc_scenario(
        self, scenario: ClimateScenario, projection_year: int = 2050
    ) -> IPCCScenarioData:
        """Generate realistic IPCC climate projections"""
        scenario_data = {
            ClimateScenario.RCP45: {
                "temp_2050": 1.8,
                "temp_2100": 2.4,
                "precip_change": -8.5,
            },
            ClimateScenario.RCP85: {
                "temp_2050": 2.8,
                "temp_2100": 4.3,
                "precip_change": -15.0,
            },
            ClimateScenario.BASELINE: {
                "temp_2050": 0.0,
                "temp_2100": 0.0,
                "precip_change": 0.0,
            },
        }

        data = scenario_data.get(scenario, scenario_data[ClimateScenario.BASELINE])

        if projection_year <= 2050:
            progress = (projection_year - 2020) / 30.0
            temp = data["temp_2050"] * progress
        else:
            progress = (projection_year - 2050) / 50.0
            temp = data["temp_2050"] + (data["temp_2100"] - data["temp_2050"]) * progress

        return IPCCScenarioData(
            scenario=scenario,
            year=projection_year,
            temperature_increase=temp,
            precipitation_change=data["precip_change"],
            sea_level_rise=0.35 if scenario == ClimateScenario.RCP45 else 0.63,
            frequency_extreme_events=1.2 if scenario == ClimateScenario.RCP85 else 1.05,
        )

    def calculate_ca_rul(
        self,
        temp_increase: Optional[float] = None,
        precip_change: Optional[float] = None,
        scenario: str = "rcp85",
        projection_year: int = 2050,
        current_age: float = 0.0,
    ) -> Dict[str, float]:
        """
        Calculate climate-adjusted RUL.
        
        Args:
            temp_increase: Temperature increase in °C (overrides scenario if provided)
            precip_change: Precipitation change as % (overrides scenario if provided)
            scenario: Climate scenario ("rcp45", "rcp85", "baseline")
            projection_year: Year for scenario projection
            current_age: Current age of asset in years
            
        Returns:
            Dictionary with CA-RUL and component factors
        """
        scenario_enum = ClimateScenario[scenario.upper()]
        ipcc_data = self._generate_ipcc_scenario(scenario_enum, projection_year)

        if temp_increase is None:
            temp_increase = ipcc_data.temperature_increase
        if precip_change is None:
            precip_change = ipcc_data.precipitation_change

        temp_factor = 1.0 - (temp_increase * self.degradation_params.temp_sensitivity)
        precip_factor = 1.0 - (
            abs(precip_change) * self.degradation_params.precip_sensitivity
        )

        total_degradation_factor = temp_factor * precip_factor

        ca_rul = self.baseline_rul * total_degradation_factor - current_age

        remaining_annual_degradation = (
            self.degradation_params.base_degradation_rate
            / total_degradation_factor
        )

        return {
            "ca_rul": max(0.0, ca_rul),
            "degradation_factor": total_degradation_factor,
            "temp_factor": temp_factor,
            "precip_factor": precip_factor,
            "annual_degradation_rate": remaining_annual_degradation,
            "projected_eol_year": projection_year + ca_rul,
            "scenario": scenario,
            "temp_increase_celsius": temp_increase,
            "precip_change_percent": precip_change,
        }

    def generate_degradation_curve(
        self,
        scenario: str = "rcp85",
        years_ahead: int = 30,
        step: int = 1,
    ) -> pd.DataFrame:
        """
        Generate degradation curves for multiple years.
        
        Args:
            scenario: Climate scenario
            years_ahead: Number of years to project
            step: Year intervals for calculation
            
        Returns:
            DataFrame with year, RUL, and degradation profile
        """
        results = []
        for year in range(0, years_ahead + 1, step):
            ca_rul_data = self.calculate_ca_rul(
                scenario=scenario, projection_year=2024 + year, current_age=year
            )
            results.append(
                {
                    "year": 2024 + year,
                    "asset_age": year,
                    "ca_rul": ca_rul_data["ca_rul"],
                    "degradation_factor": ca_rul_data["degradation_factor"],
                    "scenario": scenario,
                }
            )

        return pd.DataFrame(results)

    def compare_scenarios(
        self,
        temp_increase: float = 2.5,
        precip_change: float = -10.0,
        current_age: float = 0.0,
    ) -> pd.DataFrame:
        """
        Compare CA-RUL across different IPCC scenarios.
        
        Returns:
            DataFrame comparing RUL under RCP 4.5, RCP 8.5, and baseline
        """
        scenarios = ["baseline", "rcp45", "rcp85"]
        results = []

        for scenario in scenarios:
            ca_rul_data = self.calculate_ca_rul(
                temp_increase=temp_increase,
                precip_change=precip_change,
                scenario=scenario,
                current_age=current_age,
            )
            results.append(
                {
                    "scenario": scenario,
                    "ca_rul": ca_rul_data["ca_rul"],
                    "degradation_factor": ca_rul_data["degradation_factor"],
                    "annual_degradation": ca_rul_data["annual_degradation_rate"],
                }
            )

        return pd.DataFrame(results)

    def export_features(self) -> Dict:
        """Export feature definitions for MLOps pipeline"""
        return {
            "baseline_rul": self.baseline_rul,
            "infrastructure_type": self.infrastructure_type,
            "degradation_params": self.degradation_params.__dict__,
            "supported_scenarios": [s.value for s in ClimateScenario],
            "feature_version": "1.0",
        }


def create_climate_adjusted_rul(
    baseline_rul: float, infrastructure_type: str = "road"
) -> ClimateAdjustedRUL:
    """Factory function to create CA-RUL calculator"""
    return ClimateAdjustedRUL(baseline_rul, infrastructure_type)


def batch_calculate_ca_rul(
    assets: List[Dict], scenario: str = "rcp85"
) -> pd.DataFrame:
    """
    Batch calculate CA-RUL for multiple assets.
    
    Args:
        assets: List of dicts with keys: baseline_rul, type, age
        scenario: Climate scenario
        
    Returns:
        DataFrame with CA-RUL for all assets
    """
    results = []
    for asset in assets:
        calc = ClimateAdjustedRUL(asset["baseline_rul"], asset.get("type", "road"))
        ca_rul_data = calc.calculate_ca_rul(
            scenario=scenario, current_age=asset.get("age", 0.0)
        )
        ca_rul_data["asset_id"] = asset.get("id")
        results.append(ca_rul_data)

    return pd.DataFrame(results)
