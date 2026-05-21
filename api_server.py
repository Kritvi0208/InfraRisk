"""
Lightweight API endpoints for the final InfraRiskAI backend.

Run with:
    uvicorn api_server:app --reload
"""

from __future__ import annotations

import base64
from typing import Any, Dict, List

from final_engine import (
    DATA_PROVENANCE,
    ContractBenchmarkEngine,
    ExportEngine,
    FinalInfraRiskEngine,
    GraphPropagationEngine,
    StorageEngine,
    demo_payload,
)

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except Exception:  # pragma: no cover - lets the module import without optional API deps
    FastAPI = None
    HTTPException = Exception

    class BaseModel:  # type: ignore
        pass


if FastAPI is not None:
    app = FastAPI(title="InfraRiskAI Final API", version="1.0.0")
else:
    app = None


class PortfolioRequest(BaseModel):
    deals: List[Dict[str, Any]]
    persist: bool = True


class BenchmarkRequest(BaseModel):
    sector: str
    country: str
    project_value: float
    tenor_years: int


class ClauseRequest(BaseModel):
    clauses: List[Dict[str, Any]]


engine = FinalInfraRiskEngine()
benchmarks = ContractBenchmarkEngine()
storage = StorageEngine()


if app is not None:

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/provenance")
    def provenance() -> Dict[str, Any]:
        return DATA_PROVENANCE

    @app.post("/portfolio/recalculate")
    def recalculate(req: PortfolioRequest) -> Dict[str, Any]:
        if not req.deals:
            raise HTTPException(status_code=400, detail="At least one deal is required")
        return engine.recalculate_portfolio(req.deals, persist=req.persist)

    @app.get("/portfolio/demo")
    def demo() -> Dict[str, Any]:
        return engine.recalculate_portfolio(demo_payload(), persist=False)

    @app.get("/portfolio/runs")
    def runs(limit: int = 5) -> Dict[str, Any]:
        return {"runs": storage.latest_runs(limit)}

    @app.post("/contract/benchmark")
    def contract_benchmark(req: BenchmarkRequest) -> Dict[str, Any]:
        return benchmarks.compare(
            req.sector, req.country, req.project_value, req.tenor_years
        )

    @app.post("/contract/resolve-clauses")
    def resolve_clauses(req: ClauseRequest) -> Dict[str, Any]:
        return benchmarks.resolve_nested_clauses(req.clauses)

    @app.post("/graph/node/{node_id}")
    def graph_node(node_id: str, req: PortfolioRequest) -> Dict[str, Any]:
        result = engine.recalculate_portfolio(req.deals, persist=False)
        return GraphPropagationEngine.node_interaction(
            node_id, result["gnn_propagation"]
        )

    @app.post("/export/csv")
    def export_csv(req: PortfolioRequest) -> Dict[str, Any]:
        result = engine.recalculate_portfolio(req.deals, persist=False)
        return {
            "filename": "infrarisk_portfolio.csv",
            "content": ExportEngine.to_csv(result),
        }

    @app.post("/export/pdf")
    def export_pdf(req: PortfolioRequest) -> Dict[str, Any]:
        result = engine.recalculate_portfolio(req.deals, persist=False)
        encoded = base64.b64encode(ExportEngine.to_pdf_bytes(result)).decode("ascii")
        return {"filename": "infrarisk_portfolio.pdf", "content_base64": encoded}
