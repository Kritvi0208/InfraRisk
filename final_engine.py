"""Final integration engine for InfraRiskAI.

This module keeps the project lightweight while making the major product
capabilities callable from the dashboard, tests, scripts, and API layer.
"""

from __future__ import annotations

import csv
import io
import json
import math
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np

from benchmark_database import BenchmarkDatabase
from shap_interpreter import SHAPInterpreter


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "processed" / "infrarisk.db"


@dataclass
class ProjectDeal:
    deal_id: str
    name: str
    sector: str
    country: str
    capex: float
    revenue_annual: float
    opex_annual: float
    debt_amount: float
    equity_amount: float
    coupon_rate: float
    tenor_years: int
    probability_of_default: float
    dscr_minimum: float = 1.25
    leverage_maximum: float = 0.75
    liquidity: float = 0.0
    min_liquidity: float = 0.0
    years_to_maturity: Optional[int] = None
    balloon_payment: float = 0.0
    status: str = "active"

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ProjectDeal":
        return cls(
            deal_id=str(payload.get("deal_id") or payload.get("id") or payload.get("name") or "deal"),
            name=str(payload.get("name") or payload.get("deal_id") or "Unnamed Deal"),
            sector=str(payload.get("sector") or "Other"),
            country=str(payload.get("country") or "Unknown"),
            capex=float(payload.get("capex", 0.0)),
            revenue_annual=float(payload.get("revenue_annual", payload.get("revenue", 0.0))),
            opex_annual=float(payload.get("opex_annual", payload.get("opex", 0.0))),
            debt_amount=float(payload.get("debt_amount", payload.get("debt", 0.0))),
            equity_amount=float(payload.get("equity_amount", payload.get("equity", 0.0))),
            coupon_rate=float(payload.get("coupon_rate", payload.get("interest_rate", 0.06))),
            tenor_years=int(payload.get("tenor_years", payload.get("tenor", 15))),
            probability_of_default=float(payload.get("probability_of_default", payload.get("pd", 0.05))),
            dscr_minimum=float(payload.get("dscr_minimum", 1.25)),
            leverage_maximum=float(payload.get("leverage_maximum", 0.75)),
            liquidity=float(payload.get("liquidity", 0.0)),
            min_liquidity=float(payload.get("min_liquidity", 0.0)),
            years_to_maturity=(
                int(payload["years_to_maturity"]) if payload.get("years_to_maturity") is not None else None
            ),
            balloon_payment=float(payload.get("balloon_payment", 0.0)),
            status=str(payload.get("status", "active")),
        )

    @property
    def ebitda(self) -> float:
        return self.revenue_annual - self.opex_annual

    @property
    def portfolio_value(self) -> float:
        return self.debt_amount + self.equity_amount

    @property
    def leverage(self) -> float:
        if self.portfolio_value <= 0:
            return 0.0
        return self.debt_amount / self.portfolio_value