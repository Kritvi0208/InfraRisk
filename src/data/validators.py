"""
Infrastructure-specific data validators with sector bounds.

Provides validation for infrastructure costs, DSCR, toll rates,
and other financial metrics with realistic sector-specific constraints.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class InfrastructureSector(str, Enum):
    """Infrastructure project sectors."""
    HYDRO = "hydro"
    THERMAL = "thermal"
    WIND = "wind"
    SOLAR = "solar"
    TRANSMISSION = "transmission"
    ROAD = "road"
    RAIL = "rail"
    PORT = "port"
    WATER = "water"


@dataclass
class InfrastructureBounds:
    """Realistic bounds for infrastructure financial metrics."""
    # Cost per MW (in millions USD)
    cost_per_mw_min: float
    cost_per_mw_max: float
    # Debt Service Coverage Ratio
    dscr_min: float
    dscr_max: float
    # Toll rates (fraction of value of time savings)
    toll_rate_min: float
    toll_rate_max: float
    # Capital cost overrun (percentage)
    cost_overrun_max: float
    # Schedule delay (percentage)
    schedule_delay_max: float
    # Typical project size (MW)
    typical_capacity_min: float
    typical_capacity_max: float


class InfrastructureValidator:
    """Validate infrastructure project data against sector-specific bounds."""

    # Sector-specific bounds (in millions USD, ratios, percentages)
    SECTOR_BOUNDS = {
        InfrastructureSector.HYDRO: InfrastructureBounds(
            cost_per_mw_min=1.0,
            cost_per_mw_max=3.0,
            dscr_min=1.0,
            dscr_max=3.0,
            toll_rate_min=0.05,
            toll_rate_max=0.15,
            cost_overrun_max=0.50,  # 50%
            schedule_delay_max=0.40,  # 40%
            typical_capacity_min=10,
            typical_capacity_max=1000,
        ),
        InfrastructureSector.THERMAL: InfrastructureBounds(
            cost_per_mw_min=0.8,
            cost_per_mw_max=1.5,
            dscr_min=1.2,
            dscr_max=2.5,
            toll_rate_min=0.08,
            toll_rate_max=0.12,
            cost_overrun_max=0.45,
            schedule_delay_max=0.35,
            typical_capacity_min=50,
            typical_capacity_max=800,
        ),
        InfrastructureSector.WIND: InfrastructureBounds(
            cost_per_mw_min=1.5,
            cost_per_mw_max=2.5,
            dscr_min=1.1,
            dscr_max=2.8,
            toll_rate_min=0.06,
            toll_rate_max=0.14,
            cost_overrun_max=0.40,
            schedule_delay_max=0.25,
            typical_capacity_min=5,
            typical_capacity_max=500,
        ),
        InfrastructureSector.SOLAR: InfrastructureBounds(
            cost_per_mw_min=0.7,
            cost_per_mw_max=1.3,
            dscr_min=1.0,
            dscr_max=2.2,
            toll_rate_min=0.05,
            toll_rate_max=0.10,
            cost_overrun_max=0.30,
            schedule_delay_max=0.20,
            typical_capacity_min=1,
            typical_capacity_max=300,
        ),
        InfrastructureSector.TRANSMISSION: InfrastructureBounds(
            cost_per_mw_min=1.2,
            cost_per_mw_max=2.0,
            dscr_min=1.3,
            dscr_max=2.5,
            toll_rate_min=0.07,
            toll_rate_max=0.13,
            cost_overrun_max=0.55,
            schedule_delay_max=0.45,
            typical_capacity_min=100,
            typical_capacity_max=5000,
        ),
        InfrastructureSector.ROAD: InfrastructureBounds(
            cost_per_mw_min=0.5,  # Per km (normalized)
            cost_per_mw_max=1.0,
            dscr_min=1.2,
            dscr_max=2.0,
            toll_rate_min=0.08,
            toll_rate_max=0.15,
            cost_overrun_max=0.60,
            schedule_delay_max=0.50,
            typical_capacity_min=100,
            typical_capacity_max=1000,
        ),
        InfrastructureSector.RAIL: InfrastructureBounds(
            cost_per_mw_min=2.0,  # Per km
            cost_per_mw_max=4.0,
            dscr_min=1.1,
            dscr_max=2.2,
            toll_rate_min=0.06,
            toll_rate_max=0.12,
            cost_overrun_max=0.70,
            schedule_delay_max=0.60,
            typical_capacity_min=50,
            typical_capacity_max=500,
        ),
        InfrastructureSector.PORT: InfrastructureBounds(
            cost_per_mw_min=1.5,
            cost_per_mw_max=3.5,
            dscr_min=1.3,
            dscr_max=2.5,
            toll_rate_min=0.10,
            toll_rate_max=0.20,
            cost_overrun_max=0.65,
            schedule_delay_max=0.55,
            typical_capacity_min=50,
            typical_capacity_max=500,
        ),
        InfrastructureSector.WATER: InfrastructureBounds(
            cost_per_mw_min=0.8,
            cost_per_mw_max=1.8,
            dscr_min=1.0,
            dscr_max=2.5,
            toll_rate_min=0.05,
            toll_rate_max=0.12,
            cost_overrun_max=0.55,
            schedule_delay_max=0.45,
            typical_capacity_min=5,
            typical_capacity_max=200,
        ),
    }

    def __init__(self, sector: InfrastructureSector):
        """
        Initialize validator for a specific infrastructure sector.

        Args:
            sector: Infrastructure sector to validate
        """
        self.sector = sector
        self.bounds = self.SECTOR_BOUNDS.get(
            sector,
            self.SECTOR_BOUNDS[InfrastructureSector.HYDRO]  # Default
        )
        self.validation_errors: List[str] = []

    def validate_cost_per_mw(self, cost_per_mw: float) -> bool:
        """
        Validate cost per MW is within sector bounds.

        Args:
            cost_per_mw: Cost per MW in millions USD

        Returns:
            True if valid, False otherwise
        """
        valid = self.bounds.cost_per_mw_min <= cost_per_mw <= self.bounds.cost_per_mw_max
        if not valid:
            self.validation_errors.append(
                f"Cost/MW ${cost_per_mw:.2f}M out of bounds "
                f"[${self.bounds.cost_per_mw_min:.2f}M-${self.bounds.cost_per_mw_max:.2f}M]"
            )
        return valid

    def validate_dscr(self, dscr: float) -> bool:
        """
        Validate Debt Service Coverage Ratio.

        Args:
            dscr: DSCR (typically 1.0x to 3.0x)

        Returns:
            True if valid, False otherwise
        """
        valid = self.bounds.dscr_min <= dscr <= self.bounds.dscr_max
        if not valid:
            self.validation_errors.append(
                f"DSCR {dscr:.2f}x out of bounds "
                f"[{self.bounds.dscr_min:.2f}x-{self.bounds.dscr_max:.2f}x]"
            )
        return valid

    def validate_toll_rate(self, toll_rate: float) -> bool:
        """
        Validate toll rate (as fraction of value of time savings).

        Args:
            toll_rate: Toll rate as fraction (0.05-0.15 typical)

        Returns:
            True if valid, False otherwise
        """
        valid = self.bounds.toll_rate_min <= toll_rate <= self.bounds.toll_rate_max
        if not valid:
            self.validation_errors.append(
                f"Toll rate {toll_rate:.2%} out of bounds "
                f"[{self.bounds.toll_rate_min:.2%}-{self.bounds.toll_rate_max:.2%}]"
            )
        return valid

    def validate_cost_overrun(self, overrun: float) -> bool:
        """
        Validate cost overrun percentage.

        Args:
            overrun: Cost overrun as percentage (0.0-1.0)

        Returns:
            True if valid, False otherwise
        """
        valid = 0.0 <= overrun <= self.bounds.cost_overrun_max
        if not valid:
            self.validation_errors.append(
                f"Cost overrun {overrun:.2%} exceeds sector max {self.bounds.cost_overrun_max:.2%}"
            )
        return valid

    def validate_schedule_delay(self, delay: float) -> bool:
        """
        Validate schedule delay percentage.

        Args:
            delay: Schedule delay as percentage (0.0-1.0)

        Returns:
            True if valid, False otherwise
        """
        valid = 0.0 <= delay <= self.bounds.schedule_delay_max
        if not valid:
            self.validation_errors.append(
                f"Schedule delay {delay:.2%} exceeds sector max {self.bounds.schedule_delay_max:.2%}"
            )
        return valid

    def validate_project(
        self,
        cost_per_mw: float,
        dscr: float,
        toll_rate: float,
        cost_overrun: float = 0.0,
        schedule_delay: float = 0.0
    ) -> Tuple[bool, List[str]]:
        """
        Validate entire project against sector bounds.

        Args:
            cost_per_mw: Cost per MW in millions USD
            dscr: Debt Service Coverage Ratio
            toll_rate: Toll rate as fraction
            cost_overrun: Cost overrun as percentage (optional)
            schedule_delay: Schedule delay as percentage (optional)

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        self.validation_errors = []

        self.validate_cost_per_mw(cost_per_mw)
        self.validate_dscr(dscr)
        self.validate_toll_rate(toll_rate)
        self.validate_cost_overrun(cost_overrun)
        self.validate_schedule_delay(schedule_delay)

        return len(self.validation_errors) == 0, self.validation_errors

    def get_bounds_summary(self) -> Dict[str, Tuple[float, float]]:
        """
        Get summary of validation bounds.

        Returns:
            Dictionary of metric bounds
        """
        return {
            'cost_per_mw': (self.bounds.cost_per_mw_min, self.bounds.cost_per_mw_max),
            'dscr': (self.bounds.dscr_min, self.bounds.dscr_max),
            'toll_rate': (self.bounds.toll_rate_min, self.bounds.toll_rate_max),
            'cost_overrun_max': (0.0, self.bounds.cost_overrun_max),
            'schedule_delay_max': (0.0, self.bounds.schedule_delay_max),
        }
