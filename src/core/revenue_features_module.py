"""
Revenue and Macroeconomic Features Module

Comprehensive module for infrastructure revenue modeling including:
- Toll rates as % of value of time savings
- Competing route ratios
- Revenue demand curves by sector
- Sovereign risk composite scores
- Fiscal stress indices
- External vulnerability indices
- Sector-specific traffic/energy/port metrics

Example usage:
    >>> revenue = RevenueFeatures()
    >>> toll_features = revenue.calculate_toll_rate_features(
    ...     vot_savings=45.0,
    ...     distance=25.0,
    ...     sector="road"
    ... )
    >>> macro = MacroeconomicFeatures()
    >>> sovereign = macro.calculate_sovereign_risk_score(country="Country_A")
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class InfrastructureSector(Enum):
    """Infrastructure sectors"""
    ROAD = "road"
    POWER = "power"
    PORT = "port"
    WATER = "water"


@dataclass
class DemandCurveParameters:
    """Parameters for revenue demand curves"""
    sector: str
    elasticity: float
    base_volume: float
    saturation_level: float
    peak_factor: float


class RevenueFeatures:
    """Calculates revenue-related features for infrastructure projects."""

    def __init__(self):
        """Initialize revenue feature calculator"""
        self.demand_curves = self._initialize_demand_curves()

    def _initialize_demand_curves(self) -> Dict[str, DemandCurveParameters]:
        """Initialize realistic demand curve parameters by sector"""
        return {
            "road": DemandCurveParameters(
                sector="road",
                elasticity=-0.7,
                base_volume=45000.0,
                saturation_level=120000.0,
                peak_factor=1.35,
            ),
            "power": DemandCurveParameters(
                sector="power",
                elasticity=-0.5,
                base_volume=500.0,
                saturation_level=2000.0,
                peak_factor=1.25,
            ),
            "port": DemandCurveParameters(
                sector="port",
                elasticity=-0.6,
                base_volume=5000.0,
                saturation_level=20000.0,
                peak_factor=1.15,
            ),
            "water": DemandCurveParameters(
                sector="water",
                elasticity=-0.4,
                base_volume=150000.0,
                saturation_level=400000.0,
                peak_factor=1.20,
            ),
        }

    def calculate_toll_rate_features(
        self,
        vot_savings: float,
        distance: float,
        sector: str = "road",
        willingness_to_pay_ratio: float = 0.35,
    ) -> Dict[str, float]:
        """Calculate toll rate as % of value of time savings."""
        toll_per_km = (vot_savings * willingness_to_pay_ratio) / max(distance, 1)
        toll_percentage = (toll_per_km / vot_savings) * 100
        toll_as_pct_of_vot = willingness_to_pay_ratio * 100

        return {
            "toll_rate_per_km": toll_per_km,
            "toll_percentage_of_vot": toll_as_pct_of_vot,
            "daily_toll_revenue_per_vehicle": toll_per_km * distance,
            "toll_feasibility_score": min(toll_as_pct_of_vot / 50, 1.0),
        }

    def calculate_competing_route_ratio(
        self,
        alternative_distance: float,
        alternative_time: float,
        project_distance: float,
        project_time: float,
        toll_rate: float,
        vot: float = 15.0,
    ) -> Dict[str, float]:
        """Calculate impact of competing routes on revenue."""
        alt_cost = alternative_distance * 0.15 + alternative_time * vot
        project_cost = project_distance * 0.15 + project_time * vot + toll_rate

        cost_difference = alt_cost - project_cost
        cost_difference_pct = (cost_difference / alt_cost * 100) if alt_cost > 0 else 0

        time_savings = alternative_time - project_time
        distance_savings = alternative_distance - project_distance

        competitive_ratio = (
            0.5
            if cost_difference > 0
            else min(abs(cost_difference_pct) / 50, 1.0)
        )

        return {
            "cost_difference_pct": cost_difference_pct,
            "time_savings_hours": max(time_savings, 0),
            "distance_savings_km": max(distance_savings, 0),
            "competing_route_diversion_rate": competitive_ratio,
            "market_penetration_potential": max(1.0 - competitive_ratio, 0.0),
        }

    def calculate_revenue_demand_curve(
        self, sector: str, toll_rate: float, growth_rate: float = 0.03
    ) -> pd.DataFrame:
        """Generate revenue demand curve for sector."""
        params = self.demand_curves.get(sector, self.demand_curves["road"])

        years = np.arange(0, 31)
        toll_rates = np.linspace(toll_rate * 0.5, toll_rate * 2.0, 30)

        results = []
        for year, annual_toll in zip(years, toll_rates):
            demand_factor = 1 + (growth_rate * year)
            price_elasticity_effect = (annual_toll / toll_rate) ** params.elasticity
            volume = params.base_volume * demand_factor * price_elasticity_effect
            volume = min(volume, params.saturation_level)
            annual_revenue = volume * annual_toll

            results.append(
                {
                    "year": 2024 + year,
                    "toll_rate": annual_toll,
                    "demand_volume": volume,
                    "annual_revenue": annual_revenue,
                    "growth_factor": demand_factor,
                }
            )

        return pd.DataFrame(results)

    def calculate_sector_metrics(
        self, sector: str, volume: float, utilization_rate: float = 0.75
    ) -> Dict[str, float]:
        """Calculate sector-specific metrics."""
        sector_lower = sector.lower()

        if sector_lower in ["road", "transportation"]:
            annual_vehicles = volume
            daily_traffic = volume / 365
            peak_hour_traffic = daily_traffic / 24 * 3
            revenue_per_vehicle = 2.5

            return {
                "annual_vehicle_count": annual_vehicles,
                "daily_traffic_count": daily_traffic,
                "peak_hour_traffic": peak_hour_traffic,
                "estimated_annual_toll_revenue": annual_vehicles * revenue_per_vehicle,
                "utilization_rate": utilization_rate,
                "excess_capacity": max(1.0 - utilization_rate, 0),
            }

        elif sector_lower == "power":
            annual_mwh = volume
            average_mw = annual_mwh / 8760
            capacity_factor = utilization_rate
            revenue_per_mwh = 65.0

            return {
                "annual_generation_mwh": annual_mwh,
                "average_mw": average_mw,
                "capacity_factor": capacity_factor,
                "estimated_annual_revenue": annual_mwh * revenue_per_mwh,
                "peak_capacity_mw": average_mw / capacity_factor,
                "dispatch_flexibility": min(1.0 - capacity_factor, 1.0),
            }

        elif sector_lower == "port":
            annual_teus = volume
            avg_teus_per_day = annual_teus / 365
            revenue_per_teu = 85.0

            return {
                "annual_teu_volume": annual_teus,
                "daily_teu_average": avg_teus_per_day,
                "estimated_annual_revenue": annual_teus * revenue_per_teu,
                "utilization_rate": utilization_rate,
                "berth_productivity_teus_per_day": avg_teus_per_day / (1 - utilization_rate + 0.1),
            }

        return {"volume": volume, "utilization_rate": utilization_rate}

    def generate_mock_sector_data(
        self, sector: str, num_projects: int = 20
    ) -> pd.DataFrame:
        """Generate realistic mock sector data."""
        sector_lower = sector.lower()
        data = []

        for i in range(num_projects):
            if sector_lower in ["road", "transportation"]:
                volume = np.random.normal(50000, 15000)
                metrics = self.calculate_sector_metrics(sector, volume)
            elif sector_lower == "power":
                volume = np.random.normal(700, 250)
                metrics = self.calculate_sector_metrics(sector, volume)
            elif sector_lower == "port":
                volume = np.random.normal(8000, 3000)
                metrics = self.calculate_sector_metrics(sector, volume)
            else:
                volume = np.random.normal(100000, 30000)
                metrics = self.calculate_sector_metrics(sector, volume)

            metrics["project_id"] = f"{sector}_proj_{i:03d}"
            metrics["sector"] = sector
            data.append(metrics)

        return pd.DataFrame(data)


class MacroeconomicFeatures:
    """Calculates macroeconomic features including sovereign risk and vulnerabilities."""

    def __init__(self):
        """Initialize macro features calculator"""
        self.country_indicators = self._initialize_country_data()

    def _initialize_country_data(self) -> Dict[str, Dict]:
        """Initialize mock country-level indicators"""
        countries = ["Country_A", "Country_B", "Country_C", "Country_D"]

        return {
            country: {
                "gdp_growth": np.random.uniform(1.5, 4.5),
                "inflation_rate": np.random.uniform(1.0, 8.0),
                "debt_to_gdp": np.random.uniform(30, 120),
                "fx_reserves_months": np.random.uniform(2, 12),
                "current_account_deficit": np.random.uniform(-8, 2),
                "interest_rate": np.random.uniform(1.5, 8.0),
            }
            for country in countries
        }

    def calculate_sovereign_risk_score(
        self, country: str, lookback_years: int = 5
    ) -> Dict[str, float]:
        """Calculate sovereign risk composite score."""
        if country not in self.country_indicators:
            return {}

        indicators = self.country_indicators[country]

        growth_score = 1.0 - min(
            abs(indicators["gdp_growth"] - 3.0) / 5.0, 1.0
        )
        inflation_score = 1.0 - min(
            abs(indicators["inflation_rate"] - 2.5) / 6.0, 1.0
        )
        debt_score = 1.0 - min(indicators["debt_to_gdp"] / 150.0, 1.0)
        reserves_score = min(indicators["fx_reserves_months"] / 6.0, 1.0)
        cad_score = 1.0 - min(
            abs(indicators["current_account_deficit"] / 10.0), 1.0
        )

        composite_score = (
            growth_score * 0.20
            + inflation_score * 0.20
            + debt_score * 0.25
            + reserves_score * 0.20
            + cad_score * 0.15
        )

        return {
            "growth_score": growth_score,
            "inflation_score": inflation_score,
            "debt_sustainability_score": debt_score,
            "reserves_adequacy_score": reserves_score,
            "external_balance_score": cad_score,
            "sovereign_risk_composite": composite_score,
            "country": country,
            "risk_rating": self._score_to_rating(composite_score),
        }

    def calculate_fiscal_stress_index(
        self, country: str, capex_spending: float, tax_revenue: float
    ) -> Dict[str, float]:
        """Calculate fiscal stress index."""
        if country not in self.country_indicators:
            return {}

        indicators = self.country_indicators[country]

        fiscal_deficit = capex_spending - tax_revenue
        deficit_sustainability = 1.0 - min(abs(fiscal_deficit) / 10.0, 1.0)

        debt_trajectory = (
            1.0
            if (indicators["gdp_growth"] > indicators["interest_rate"])
            else 0.5
        )

        revenue_adequacy = min(tax_revenue / 20.0, 1.0)
        interest_coverage = indicators["gdp_growth"] / max(
            indicators["interest_rate"], 0.5
        )

        fiscal_stress = (
            (1.0 - deficit_sustainability) * 0.30
            + (1.0 - debt_trajectory) * 0.30
            + (1.0 - revenue_adequacy) * 0.20
            + min(1.0 / (interest_coverage + 0.1), 1.0) * 0.20
        )

        return {
            "fiscal_deficit_pct_gdp": fiscal_deficit,
            "deficit_sustainability_score": deficit_sustainability,
            "debt_trajectory_sustainability": debt_trajectory,
            "revenue_adequacy_ratio": revenue_adequacy,
            "interest_coverage_ratio": interest_coverage,
            "fiscal_stress_index": fiscal_stress,
        }

    def calculate_external_vulnerability_index(
        self, country: str, fdi_stock: float = 25.0
    ) -> Dict[str, float]:
        """Calculate external vulnerability index."""
        if country not in self.country_indicators:
            return {}

        indicators = self.country_indicators[country]

        cad = abs(indicators["current_account_deficit"])
        cad_vuln = min(cad / 8.0, 1.0)
        reserves_vuln = 1.0 - min(indicators["fx_reserves_months"] / 6.0, 1.0)
        short_term_debt = np.random.uniform(10, 40)
        debt_maturity_vuln = min(short_term_debt / 50.0, 1.0)
        fdi_dependence = 1.0 - min(fdi_stock / 30.0, 1.0)

        external_vulnerability = (
            cad_vuln * 0.30
            + reserves_vuln * 0.25
            + debt_maturity_vuln * 0.25
            + fdi_dependence * 0.20
        )

        return {
            "current_account_deficit_vulnerability": cad_vuln,
            "reserves_vulnerability": reserves_vuln,
            "debt_maturity_vulnerability": debt_maturity_vuln,
            "fdi_dependence_ratio": fdi_dependence,
            "external_vulnerability_index": external_vulnerability,
        }

    def _score_to_rating(self, score: float) -> str:
        """Convert composite score to risk rating"""
        if score >= 0.75:
            return "Low Risk"
        elif score >= 0.50:
            return "Moderate Risk"
        elif score >= 0.25:
            return "High Risk"
        return "Very High Risk"

    def generate_portfolio_macro_features(
        self, num_projects: int = 30
    ) -> pd.DataFrame:
        """Generate macro features for portfolio of projects."""
        countries = list(self.country_indicators.keys())
        data = []

        for i in range(num_projects):
            country = countries[i % len(countries)]
            sovereign = self.calculate_sovereign_risk_score(country)
            fiscal = self.calculate_fiscal_stress_index(
                country,
                capex_spending=np.random.uniform(4, 8),
                tax_revenue=np.random.uniform(15, 25),
            )
            external = self.calculate_external_vulnerability_index(country)

            features = {
                "project_id": f"proj_{i:03d}",
                "country": country,
                **sovereign,
                **fiscal,
                **external,
            }
            data.append(features)

        return pd.DataFrame(data)
