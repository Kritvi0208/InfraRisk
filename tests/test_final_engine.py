from pathlib import Path

from final_engine import (
    ContractBenchmarkEngine,
    ExportEngine,
    FinalInfraRiskEngine,
    GraphPropagationEngine,
    StorageEngine,
    demo_payload,
)


def test_final_engine_recalculates_core_risk_stack(tmp_path: Path):
    engine = FinalInfraRiskEngine(StorageEngine(tmp_path / "runs.db"))
    result = engine.recalculate_portfolio(demo_payload())

    assert len(result["deal_results"]) == 2
    assert result["deal_results"][0]["amortization_schedule"]
    assert result["deal_results"][1]["decision"] == "reject"
    assert result["pd_rejections"][0]["deal_id"] == "ROAD-BR-002"
    assert result["sector_concentration"]["hhi"] > 0
    assert result["game_score"]["total_score"] > 0
    assert result["rl_opponent"]["action"] in {"source", "hold", "rebalance", "refinance"}
    assert result["shap_explanations"]["global"]["features"]


def test_graph_node_interaction_and_exports(tmp_path: Path):
    engine = FinalInfraRiskEngine(StorageEngine(tmp_path / "runs.db"))
    result = engine.recalculate_portfolio(demo_payload(), persist=False)

    node = GraphPropagationEngine.node_interaction("SOLAR-IN-001", result["gnn_propagation"])
    assert node["node_id"] == "SOLAR-IN-001"
    assert node["propagated_pd"] is not None

    csv_text = ExportEngine.to_csv(result)
    pdf_bytes = ExportEngine.to_pdf_bytes(result)
    assert "deal_id,name,decision" in csv_text
    assert pdf_bytes.startswith(b"%PDF")


def test_contract_benchmark_and_nested_clause_resolution():
    engine = ContractBenchmarkEngine()
    comparison = engine.compare("Energy", "India", 150_000_000, 18)
    assert comparison["benchmark_type"] == "synthetic_1000_contract_sample"

    clauses = [
        {"id": "1", "references": ["2"]},
        {"id": "2", "references": ["3"]},
        {"id": "3", "references": []},
    ]
    resolved = engine.resolve_nested_clauses(clauses)
    assert resolved["resolved"]["1"] == ["2", "3"]

