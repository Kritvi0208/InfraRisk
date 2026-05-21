"""
Final integration engine for InfraRiskAI.

This module keeps the project lightweight while making the major product
capabilities callable from the dashboard, tests, scripts, and API layer.
"""

from __future__ import annotations

import csv
import io
import json
import math
import sqlite3
from dataclasses import asdict, dataclass
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
            deal_id=str(
                payload.get("deal_id")
                or payload.get("id")
                or payload.get("name")
                or "deal"
            ),
            name=str(payload.get("name") or payload.get("deal_id") or "Unnamed Deal"),
            sector=str(payload.get("sector") or "Other"),
            country=str(payload.get("country") or "Unknown"),
            capex=float(payload.get("capex", 0.0)),
            revenue_annual=float(
                payload.get("revenue_annual", payload.get("revenue", 0.0))
            ),
            opex_annual=float(payload.get("opex_annual", payload.get("opex", 0.0))),
            debt_amount=float(payload.get("debt_amount", payload.get("debt", 0.0))),
            equity_amount=float(
                payload.get("equity_amount", payload.get("equity", 0.0))
            ),
            coupon_rate=float(
                payload.get("coupon_rate", payload.get("interest_rate", 0.06))
            ),
            tenor_years=int(payload.get("tenor_years", payload.get("tenor", 15))),
            probability_of_default=float(
                payload.get("probability_of_default", payload.get("pd", 0.05))
            ),
            dscr_minimum=float(payload.get("dscr_minimum", 1.25)),
            leverage_maximum=float(payload.get("leverage_maximum", 0.75)),
            liquidity=float(payload.get("liquidity", 0.0)),
            min_liquidity=float(payload.get("min_liquidity", 0.0)),
            years_to_maturity=(
                int(payload["years_to_maturity"])
                if payload.get("years_to_maturity") is not None
                else None
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


class DebtAmortizationEngine:
    @staticmethod
    def annual_payment(principal: float, annual_rate: float, years: int) -> float:
        if principal <= 0 or years <= 0:
            return 0.0
        if annual_rate <= 0:
            return principal / years
        factor = (1 + annual_rate) ** years
        return principal * annual_rate * factor / (factor - 1)

    @classmethod
    def schedule(
        cls, principal: float, annual_rate: float, years: int
    ) -> List[Dict[str, float]]:
        payment = cls.annual_payment(principal, annual_rate, years)
        balance = principal
        rows = []
        for year in range(1, years + 1):
            interest = balance * annual_rate
            principal_paid = min(balance, max(0.0, payment - interest))
            balance = max(0.0, balance - principal_paid)
            rows.append(
                {
                    "year": year,
                    "opening_balance": round(balance + principal_paid, 2),
                    "payment": round(payment, 2),
                    "interest": round(interest, 2),
                    "principal": round(principal_paid, 2),
                    "closing_balance": round(balance, 2),
                }
            )
        return rows


class CashWaterfallEngine:
    @staticmethod
    def calculate(
        deal: ProjectDeal,
        debt_service: float,
        tax_rate: float = 0.25,
        reserve_pct: float = 0.05,
    ) -> Dict:
        gross_revenue = deal.revenue_annual
        reserve = gross_revenue * reserve_pct
        available_revenue = gross_revenue - reserve
        ebitda = available_revenue - deal.opex_annual
        depreciation = deal.capex / max(deal.tenor_years, 1)
        ebit = ebitda - depreciation
        taxes = max(0.0, ebit * tax_rate)
        cash_available_for_debt = ebitda - taxes
        equity_cashflow = cash_available_for_debt - debt_service
        dscr = cash_available_for_debt / debt_service if debt_service > 0 else 0.0
        return {
            "gross_revenue": gross_revenue,
            "reserve": reserve,
            "available_revenue": available_revenue,
            "opex": deal.opex_annual,
            "ebitda": ebitda,
            "depreciation": depreciation,
            "taxes": taxes,
            "cash_available_for_debt": cash_available_for_debt,
            "debt_service": debt_service,
            "equity_cashflow": equity_cashflow,
            "dscr": dscr,
        }


class CovenantEngine:
    @staticmethod
    def evaluate(deal: ProjectDeal, dscr: float) -> Dict[str, Any]:
        breaches = []
        if dscr < deal.dscr_minimum:
            breaches.append(
                {
                    "covenant": "minimum_dscr",
                    "actual": round(dscr, 3),
                    "limit": deal.dscr_minimum,
                    "severity": "critical" if dscr < 1.0 else "high",
                }
            )
        if deal.leverage > deal.leverage_maximum:
            breaches.append(
                {
                    "covenant": "maximum_leverage",
                    "actual": round(deal.leverage, 3),
                    "limit": deal.leverage_maximum,
                    "severity": "high",
                }
            )
        if deal.min_liquidity > 0 and deal.liquidity < deal.min_liquidity:
            breaches.append(
                {
                    "covenant": "minimum_liquidity",
                    "actual": round(deal.liquidity, 2),
                    "limit": deal.min_liquidity,
                    "severity": "medium",
                }
            )
        return {"breached": bool(breaches), "breaches": breaches}


class RefinancingRiskEngine:
    @staticmethod
    def assess(
        deal: ProjectDeal, dscr: float, market_spread_bps: float = 250.0
    ) -> Dict[str, Any]:
        years_to_maturity = (
            deal.years_to_maturity
            if deal.years_to_maturity is not None
            else deal.tenor_years
        )
        maturity_pressure = max(0.0, (4 - years_to_maturity) / 4)
        balloon_pressure = deal.balloon_payment / max(deal.debt_amount, 1.0)
        spread_pressure = min(1.0, market_spread_bps / 600.0)
        dscr_pressure = max(0.0, (1.35 - dscr) / 1.35)
        score = 100 * (
            0.30 * maturity_pressure
            + 0.25 * balloon_pressure
            + 0.20 * spread_pressure
            + 0.25 * dscr_pressure
        )
        return {
            "score": round(min(100.0, score), 2),
            "band": "high" if score >= 60 else "medium" if score >= 30 else "low",
            "drivers": {
                "maturity_pressure": round(maturity_pressure, 3),
                "balloon_pressure": round(balloon_pressure, 3),
                "spread_pressure": round(spread_pressure, 3),
                "dscr_pressure": round(dscr_pressure, 3),
            },
        }


class PortfolioRulesEngine:
    @staticmethod
    def hhi(deals: Iterable[ProjectDeal], field: str) -> float:
        buckets: Dict[str, float] = {}
        total = 0.0
        for deal in deals:
            value = deal.portfolio_value
            total += value
            buckets[getattr(deal, field)] = (
                buckets.get(getattr(deal, field), 0.0) + value
            )
        if total <= 0:
            return 0.0
        return sum((value / total) ** 2 for value in buckets.values())

    @staticmethod
    def concentration_details(deals: List[ProjectDeal], field: str) -> Dict[str, Any]:
        total = sum(d.portfolio_value for d in deals)
        shares = {}
        for deal in deals:
            shares[getattr(deal, field)] = (
                shares.get(getattr(deal, field), 0.0) + deal.portfolio_value
            )
        shares = (
            {key: value / total for key, value in shares.items()} if total > 0 else {}
        )
        return {
            "hhi": PortfolioRulesEngine.hhi(deals, field),
            "shares": shares,
            "flag": any(share > 0.35 for share in shares.values()),
        }

    @staticmethod
    def pd_rejections(
        deals: List[ProjectDeal], max_pd: float = 0.08
    ) -> List[Dict[str, Any]]:
        return [
            {
                "deal_id": deal.deal_id,
                "name": deal.name,
                "pd": deal.probability_of_default,
                "reason": "PD exceeds 8% hard rejection limit",
            }
            for deal in deals
            if deal.probability_of_default > max_pd
        ]


class SectorScoringEngine:
    BASE = {
        "Energy": 82,
        "Water": 80,
        "Transport": 74,
        "Telecom": 76,
        "Healthcare": 78,
        "Social": 72,
        "Other": 65,
    }

    @classmethod
    def score(cls, deal: ProjectDeal, dscr: float) -> Dict[str, Any]:
        base = cls.BASE.get(deal.sector, cls.BASE["Other"])
        pd_penalty = min(35.0, deal.probability_of_default * 250)
        dscr_bonus = min(12.0, max(0.0, dscr - 1.25) * 15)
        leverage_penalty = max(0.0, deal.leverage - 0.70) * 50
        score = max(0.0, min(100.0, base + dscr_bonus - pd_penalty - leverage_penalty))
        return {
            "score": round(score, 2),
            "band": "strong" if score >= 75 else "watch" if score >= 55 else "weak",
        }


class RecommendationEngine:
    @staticmethod
    def recommend(
        deal_results: List[Dict[str, Any]], portfolio_results: Dict[str, Any]
    ) -> List[str]:
        recs = []
        if portfolio_results["sector_concentration"]["flag"]:
            recs.append(
                "Reduce largest sector exposure; HHI/concentration limit is breached or close to breach."
            )
        if portfolio_results["country_concentration"]["flag"]:
            recs.append(
                "Add country diversification before sourcing another deal in the largest geography."
            )
        for result in deal_results:
            if result["decision"] == "reject":
                recs.append(f"Reject {result['name']}: PD is above 8% hard limit.")
            elif result["covenants"]["breached"]:
                recs.append(
                    f"Renegotiate {result['name']}: covenant breach detected before approval."
                )
            elif result["refinancing_risk"]["band"] == "high":
                recs.append(
                    f"Refinance early or extend tenor for {result['name']}; refinancing risk is high."
                )
        if not recs:
            recs.append(
                "Portfolio passes hard gates; proceed with monitoring and quarterly recalculation."
            )
        return recs


class GraphPropagationEngine:
    @staticmethod
    def build_edges(deals: List[ProjectDeal]) -> List[Dict[str, Any]]:
        edges = []
        for i, left in enumerate(deals):
            for j, right in enumerate(deals[i + 1 :], start=i + 1):
                same_sector = left.sector == right.sector
                same_country = left.country == right.country
                if same_sector or same_country:
                    weight = 0.55 if same_sector and same_country else 0.35
                    edges.append(
                        {
                            "source": left.deal_id,
                            "target": right.deal_id,
                            "weight": weight,
                        }
                    )
        return edges

    @staticmethod
    def propagate(
        deals: List[ProjectDeal],
        edges: Optional[List[Dict[str, Any]]] = None,
        iterations: int = 3,
    ) -> Dict[str, Any]:
        edges = (
            edges if edges is not None else GraphPropagationEngine.build_edges(deals)
        )
        risk = {deal.deal_id: deal.probability_of_default for deal in deals}
        timeline = [{"iteration": 0, "risk": dict(risk)}]
        for iteration in range(1, iterations + 1):
            updated = dict(risk)
            for edge in edges:
                s, t, w = edge["source"], edge["target"], float(edge["weight"])
                updated[t] = min(1.0, updated[t] + risk[s] * w * 0.15)
                updated[s] = min(1.0, updated[s] + risk[t] * w * 0.15)
            risk = updated
            timeline.append({"iteration": iteration, "risk": dict(risk)})
        return {"edges": edges, "final_risk": risk, "timeline": timeline}

    @staticmethod
    def node_interaction(node_id: str, graph: Dict[str, Any]) -> Dict[str, Any]:
        neighbors = []
        for edge in graph.get("edges", []):
            if edge["source"] == node_id:
                neighbors.append(edge["target"])
            elif edge["target"] == node_id:
                neighbors.append(edge["source"])
        return {
            "node_id": node_id,
            "neighbors": neighbors,
            "propagated_pd": graph.get("final_risk", {}).get(node_id),
        }


class GameCompletionEngine:
    MODES = ["single_deal", "portfolio_manager", "crisis_manager", "deal_structurer"]

    @staticmethod
    def score(deals: List[ProjectDeal], portfolio: Dict[str, Any]) -> Dict[str, Any]:
        avg_dscr = (
            np.mean([d["waterfall"]["dscr"] for d in portfolio["deal_results"]])
            if deals
            else 0.0
        )
        default_penalty = 160 * len(portfolio["pd_rejections"])
        concentration_penalty = 80 if portfolio["sector_concentration"]["flag"] else 0
        covenant_penalty = 50 * sum(
            1 for d in portfolio["deal_results"] if d["covenants"]["breached"]
        )
        sector_score = (
            np.mean([d["sector_score"]["score"] for d in portfolio["deal_results"]])
            if deals
            else 0.0
        )
        total = (
            400
            + min(180, avg_dscr * 75)
            + sector_score * 3
            - default_penalty
            - concentration_penalty
            - covenant_penalty
        )
        return {
            "total_score": int(max(0, min(1000, total))),
            "components": {
                "coverage": round(float(avg_dscr), 3),
                "sector_quality": round(float(sector_score), 2),
                "pd_penalty": default_penalty,
                "concentration_penalty": concentration_penalty,
                "covenant_penalty": covenant_penalty,
            },
            "available_modes": list(GameCompletionEngine.MODES),
        }


class RLOpponentEngine:
    ACTIONS = ["source", "hold", "rebalance", "refinance"]

    @staticmethod
    def choose_action(portfolio: Dict[str, Any]) -> Dict[str, Any]:
        hhi = portfolio["sector_concentration"]["hhi"]
        breached = any(d["covenants"]["breached"] for d in portfolio["deal_results"])
        high_refi = any(
            d["refinancing_risk"]["band"] == "high" for d in portfolio["deal_results"]
        )
        if breached or high_refi:
            action = "refinance"
            q_value = 0.82
        elif hhi > 0.30:
            action = "rebalance"
            q_value = 0.76
        elif len(portfolio["pd_rejections"]) == 0:
            action = "source"
            q_value = 0.68
        else:
            action = "hold"
            q_value = 0.55
        return {
            "action": action,
            "q_value": q_value,
            "policy": "deterministic lightweight RL surrogate",
        }


class ContractBenchmarkEngine:
    def __init__(self) -> None:
        self.db = BenchmarkDatabase()

    def compare(
        self, sector: str, country: str, project_value: float, tenor_years: int
    ) -> Dict[str, Any]:
        sector_key = sector.lower().replace(" ", "_")
        country_key = country.lower()
        similar = self.db.find_similar_deals(
            sector_key, country_key, project_value, tenor_years
        )
        stats = self.db.get_sector_statistics(sector_key)
        return {
            "benchmark_type": "synthetic_1000_contract_sample",
            "similar_count": len(similar),
            "sector_statistics": stats,
            "sample_matches": [asdict(txn) for txn in similar[:3]],
        }

    @staticmethod
    def resolve_nested_clauses(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        by_id = {str(c["id"]): c for c in clauses}
        resolved = {}
        dead_links = []
        circular = []

        def walk(clause_id: str, seen: Tuple[str, ...] = ()) -> List[str]:
            if clause_id in seen:
                circular.append(list(seen) + [clause_id])
                return []
            refs = [str(r) for r in by_id.get(clause_id, {}).get("references", [])]
            out = []
            for ref in refs:
                if ref not in by_id:
                    dead_links.append(f"{clause_id}->{ref}")
                else:
                    out.append(ref)
                    out.extend(walk(ref, seen + (clause_id,)))
            return out

        for clause_id in by_id:
            resolved[clause_id] = sorted(set(walk(clause_id)))
        return {
            "resolved": resolved,
            "dead_links": sorted(set(dead_links)),
            "circular": circular,
        }


class ExportEngine:
    @staticmethod
    def to_csv(payload: Dict[str, Any]) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "deal_id",
                "name",
                "decision",
                "dscr",
                "pd",
                "sector_score",
                "refinancing_risk",
            ],
        )
        writer.writeheader()
        for row in payload.get("deal_results", []):
            writer.writerow(
                {
                    "deal_id": row["deal_id"],
                    "name": row["name"],
                    "decision": row["decision"],
                    "dscr": round(row["waterfall"]["dscr"], 4),
                    "pd": row["pd"],
                    "sector_score": row["sector_score"]["score"],
                    "refinancing_risk": row["refinancing_risk"]["score"],
                }
            )
        return output.getvalue()

    @staticmethod
    def to_pdf_bytes(payload: Dict[str, Any]) -> bytes:
        lines = [
            "InfraRiskAI Final Portfolio Report",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            f"Score: {payload.get('game_score', {}).get('total_score', 'n/a')}",
            "",
            "Recommendations:",
            *[f"- {rec}" for rec in payload.get("recommendations", [])],
        ]
        text = (
            "\n".join(lines)
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )
        stream = f"BT /F1 11 Tf 50 760 Td ({text[:1800]}) Tj ET".encode(
            "latin-1", errors="replace"
        )
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"\nendstream",
        ]
        pdf = io.BytesIO()
        pdf.write(b"%PDF-1.4\n")
        offsets = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(pdf.tell())
            pdf.write(f"{idx} 0 obj\n".encode() + obj + b"\nendobj\n")
        xref_at = pdf.tell()
        pdf.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
        for offset in offsets[1:]:
            pdf.write(f"{offset:010d} 00000 n \n".encode())
        pdf.write(
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode()
        )
        return pdf.getvalue()


class StorageEngine:
    def __init__(
        self, db_path: Path = DEFAULT_DB_PATH, database_url: Optional[str] = None
    ) -> None:
        self.db_path = Path(db_path)
        self.database_url = database_url

    @property
    def backend(self) -> str:
        if self.database_url and self.database_url.startswith(
            ("postgresql://", "postgres://")
        ):
            return "postgresql"
        return "sqlite"

    def _connect_sqlite(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _connect_postgres(self):
        try:
            import psycopg
        except Exception as exc:  # pragma: no cover - optional production dependency
            raise RuntimeError(
                "PostgreSQL selected but psycopg is not installed"
            ) from exc
        return psycopg.connect(self.database_url)

    def initialize(self) -> None:
        if self.backend == "postgresql":
            with self._connect_postgres() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_runs (
                        run_id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    )
                    """)
            return

        with self._connect_sqlite() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_runs (
                    run_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """)

    def save_run(self, run_id: str, payload: Dict[str, Any]) -> None:
        self.initialize()
        if self.backend == "postgresql":
            with self._connect_postgres() as conn:
                conn.execute(
                    """
                    INSERT INTO portfolio_runs(run_id, created_at, payload_json)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE
                    SET created_at = EXCLUDED.created_at,
                        payload_json = EXCLUDED.payload_json
                    """,
                    (
                        run_id,
                        datetime.now(timezone.utc).isoformat(),
                        json.dumps(payload, default=str),
                    ),
                )
            return

        with self._connect_sqlite() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO portfolio_runs(run_id, created_at, payload_json) VALUES (?, ?, ?)",
                (
                    run_id,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(payload, default=str),
                ),
            )

    def latest_runs(self, limit: int = 5) -> List[Dict[str, Any]]:
        self.initialize()
        if self.backend == "postgresql":
            with self._connect_postgres() as conn:
                rows = conn.execute(
                    "SELECT run_id, created_at, payload_json FROM portfolio_runs ORDER BY created_at DESC LIMIT %s",
                    (limit,),
                ).fetchall()
            return [
                {"run_id": r[0], "created_at": r[1], "payload": json.loads(r[2])}
                for r in rows
            ]

        with self._connect_sqlite() as conn:
            rows = conn.execute(
                "SELECT run_id, created_at, payload_json FROM portfolio_runs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"run_id": r[0], "created_at": r[1], "payload": json.loads(r[2])}
            for r in rows
        ]


class FinalInfraRiskEngine:
    FEATURE_NAMES = ["pd", "dscr", "leverage", "refi_score", "sector_score", "hhi"]

    def __init__(self, storage: Optional[StorageEngine] = None) -> None:
        self.storage = storage or StorageEngine()

    def recalculate_portfolio(
        self, raw_deals: List[Dict[str, Any]], persist: bool = True
    ) -> Dict[str, Any]:
        deals = [ProjectDeal.from_dict(d) for d in raw_deals]
        deal_results = []
        for deal in deals:
            schedule = DebtAmortizationEngine.schedule(
                deal.debt_amount, deal.coupon_rate, deal.tenor_years
            )
            debt_service = schedule[0]["payment"] if schedule else 0.0
            waterfall = CashWaterfallEngine.calculate(deal, debt_service)
            covenants = CovenantEngine.evaluate(deal, waterfall["dscr"])
            refi = RefinancingRiskEngine.assess(deal, waterfall["dscr"])
            sector_score = SectorScoringEngine.score(deal, waterfall["dscr"])
            decision = (
                "reject"
                if deal.probability_of_default > 0.08
                else "review" if covenants["breached"] else "approve"
            )
            deal_results.append(
                {
                    "deal_id": deal.deal_id,
                    "name": deal.name,
                    "sector": deal.sector,
                    "country": deal.country,
                    "pd": deal.probability_of_default,
                    "decision": decision,
                    "amortization_schedule": schedule,
                    "waterfall": waterfall,
                    "covenants": covenants,
                    "refinancing_risk": refi,
                    "sector_score": sector_score,
                }
            )

        portfolio = {
            "deal_results": deal_results,
            "sector_concentration": PortfolioRulesEngine.concentration_details(
                deals, "sector"
            ),
            "country_concentration": PortfolioRulesEngine.concentration_details(
                deals, "country"
            ),
            "pd_rejections": PortfolioRulesEngine.pd_rejections(deals),
        }
        graph = GraphPropagationEngine.propagate(deals)
        portfolio["gnn_propagation"] = graph
        portfolio["recommendations"] = RecommendationEngine.recommend(
            deal_results, portfolio
        )
        portfolio["game_score"] = GameCompletionEngine.score(deals, portfolio)
        portfolio["rl_opponent"] = RLOpponentEngine.choose_action(portfolio)
        portfolio["shap_explanations"] = self._shap(portfolio)
        portfolio["data_provenance"] = DATA_PROVENANCE
        portfolio["run_id"] = (
            f"run_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        )
        if persist:
            self.storage.save_run(portfolio["run_id"], portfolio)
        return portfolio

    def _shap(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        rows = []
        hhi = portfolio["sector_concentration"]["hhi"]
        for row in portfolio["deal_results"]:
            rows.append(
                [
                    row["pd"],
                    row["waterfall"]["dscr"],
                    1.0 if row["decision"] == "reject" else 0.0,
                    row["refinancing_risk"]["score"] / 100,
                    row["sector_score"]["score"] / 100,
                    hhi,
                ]
            )
        if not rows:
            return {"features": [], "importance": [], "local": []}
        interpreter = SHAPInterpreter(feature_names=self.FEATURE_NAMES)
        shap_values = interpreter.compute_shap_values(np.array(rows, dtype=float))
        return {
            "global": interpreter.global_feature_importance(shap_values),
            "local": [
                interpreter.local_feature_impact(i, shap_values)
                for i in range(len(rows))
            ],
        }


DATA_PROVENANCE = {
    "real_data": [
        "data/raw/ppi/ppi_projects.csv - real World Bank PPI 2024 public DTA converted to CSV",
        "data/raw/worldbank/wdi_macro.csv - World Bank macro indicators when present",
        "data/raw/worldbank/cds_spreads.csv - market spread proxy feed when present",
        "data/raw/nbi/nbi_bridges.csv and AL23.txt - US bridge/NBI sample files when present",
        "data/raw/osm/osm_roads.geojson - real OpenStreetMap/Overpass small-bbox road network sample",
        "data/raw/market/yahoo_finance_prices.csv - public Yahoo Finance market proxy history",
        "data/source_registry/real_data_sources.json - source registry extracted from the PDF table",
        "data/processed/real_data_availability_report.json - strict availability report; flags old synthetic fallbacks",
        "data/processed/infrarisk.db - local SQLite persistence for generated analysis runs",
        "PostgreSQL - supported through StorageEngine(database_url='postgresql://...') when psycopg is installed",
    ],
    "synthetic_or_mock_data": [
        "benchmark_database.py - 1000 generated comparable contract transactions",
        "p5_* starter deals, AI deals, scenario events, and RL policy surrogate",
        "shap_interpreter.py - SHAP-inspired local explanation approximation",
        "Graph propagation in final_engine.py - deterministic lightweight GNN-style message passing",
        "SAMPLE_CONTRACT_TEXT in dashboard_v2_complete.py - demo contract text",
    ],
}


def demo_payload() -> List[Dict[str, Any]]:
    return [
        {
            "deal_id": "SOLAR-IN-001",
            "name": "Gujarat Solar Farm",
            "sector": "Energy",
            "country": "India",
            "capex": 150_000_000,
            "revenue_annual": 28_000_000,
            "opex_annual": 7_500_000,
            "debt_amount": 95_000_000,
            "equity_amount": 55_000_000,
            "coupon_rate": 0.075,
            "tenor_years": 18,
            "probability_of_default": 0.045,
            "years_to_maturity": 4,
        },
        {
            "deal_id": "ROAD-BR-002",
            "name": "Sao Paulo Toll Road",
            "sector": "Transport",
            "country": "Brazil",
            "capex": 240_000_000,
            "revenue_annual": 34_000_000,
            "opex_annual": 14_000_000,
            "debt_amount": 175_000_000,
            "equity_amount": 65_000_000,
            "coupon_rate": 0.09,
            "tenor_years": 20,
            "probability_of_default": 0.082,
            "years_to_maturity": 2,
            "balloon_payment": 45_000_000,
        },
    ]
