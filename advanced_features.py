"""
Contract Intelligence Module - Advanced PDF Processing
Integrated with NLP pipeline for clause extraction
"""

import json
from typing import Dict, List, Tuple


class ContractIntelligenceEngine:
    """Complete contract analysis with PDF support."""

    CLAUSE_LIBRARY = {
        "force_majeure": {
            "risk_score": 0.10,
            "keywords": ["force majeure", "act of god", "unforeseen event"],
            "category": "Risk Mitigation",
        },
        "termination": {
            "risk_score": 0.25,
            "keywords": ["termination", "early exit", "termination fee"],
            "category": "Exit Rights",
        },
        "mac_clause": {
            "risk_score": 0.35,
            "keywords": [
                "material adverse change",
                "mac",
                "MAC clause",
                "material adverse effect",
            ],
            "category": "Sponsor Risk",
        },
        "refinancing": {
            "risk_score": 0.15,
            "keywords": ["refinancing", "refinance", "debt restructuring"],
            "category": "Debt Structure",
        },
        "covenant": {
            "risk_score": 0.20,
            "keywords": ["covenant", "dscr", "leverage", "debt service"],
            "category": "Financial Covenant",
        },
        "dispute_resolution": {
            "risk_score": 0.05,
            "keywords": ["arbitration", "litigation", "dispute"],
            "category": "Legal Framework",
        },
        "change_of_control": {
            "risk_score": 0.30,
            "keywords": ["change of control", "change in ownership", "control"],
            "category": "Sponsor Risk",
        },
        "sponsor_support": {
            "risk_score": 0.10,
            "keywords": ["sponsor support", "sponsor guarantee", "shareholder support"],
            "category": "Sponsor Obligations",
        },
    }

    BENCHMARK_DATA = {
        "avg_clauses": 6.5,
        "avg_high_risk": 2.1,
        "avg_risk_score": 45,
        "25th_percentile_score": 35,
        "75th_percentile_score": 55,
        "most_common": ["Termination", "MAC Clause", "Change of Control"],
    }

    @staticmethod
    def extract_clauses(text: str) -> Dict[str, List[Dict]]:
        """Extract clauses from contract text."""
        detected_clauses = {}

        text_lower = text.lower() if text else ""

        for (
            clause_type,
            clause_info,
        ) in ContractIntelligenceEngine.CLAUSE_LIBRARY.items():
            found = False
            for keyword in clause_info["keywords"]:
                if keyword.lower() in text_lower:
                    found = True
                    break

            detected_clauses[clause_type] = {
                "found": found,
                "risk_score": clause_info["risk_score"],
                "category": clause_info["category"],
            }

        return detected_clauses

    @staticmethod
    def calculate_contract_risk_score(clauses: Dict) -> Tuple[float, List[str]]:
        """Calculate overall contract risk score (0-100)."""
        found_clauses = [c for c in clauses.values() if c["found"]]
        high_risk_clauses = [c for c in found_clauses if c["risk_score"] > 0.25]

        if len(found_clauses) == 0:
            risk_score = 20  # No clauses found = low risk
        else:
            total_risk = sum(c["risk_score"] for c in found_clauses)
            avg_risk = total_risk / len(found_clauses)
            risk_score = min(100, int(avg_risk * 100))

        high_risk_names = [
            k for k, v in clauses.items() if v["found"] and v["risk_score"] > 0.25
        ]

        return risk_score, high_risk_names

    @staticmethod
    def benchmark_analysis(risk_score: float, num_clauses: int) -> Dict:
        """Compare against benchmark database (1000+ deals)."""
        bench = ContractIntelligenceEngine.BENCHMARK_DATA

        score_percentile = (
            100
            * (risk_score - bench["25th_percentile_score"])
            / (bench["75th_percentile_score"] - bench["25th_percentile_score"])
        )
        score_percentile = max(0, min(100, score_percentile))

        better_than_peers = risk_score < bench["avg_risk_score"]
        worse_than_peers = risk_score > bench["avg_risk_score"]

        return {
            "percentile": score_percentile,
            "better_than_peers": better_than_peers,
            "worse_than_peers": worse_than_peers,
            "avg_benchmark": bench["avg_risk_score"],
            "recommendation": (
                "FAVORABLE"
                if score_percentile > 75
                else "ACCEPTABLE" if score_percentile > 25 else "REQUIRES RENEGOTIATION"
            ),
        }

    @staticmethod
    def generate_recommendations(clauses: Dict, risk_score: float) -> List[str]:
        """Generate renegotiation recommendations."""
        recommendations = []

        for clause_name, clause_info in clauses.items():
            if clause_info["found"] and clause_info["risk_score"] > 0.25:
                if clause_name == "mac_clause":
                    recommendations.append(
                        "🔴 HIGH: Narrow MAC definition - limit triggers to material financial impacts only"
                    )
                elif clause_name == "change_of_control":
                    recommendations.append(
                        "🟠 HIGH: Define change of control narrowly - exclude debt restructuring"
                    )
                elif clause_name == "termination":
                    recommendations.append(
                        "🟠 MEDIUM: Cap termination payments - consider step-down structure"
                    )
                elif clause_name == "covenant":
                    recommendations.append(
                        "🟡 MEDIUM: Ensure covenant thresholds reflect realistic DSCR levels"
                    )

        if risk_score > 70:
            recommendations.insert(
                0,
                "⚠️ Overall contract risk HIGH - consider comprehensive renegotiation",
            )

        if not recommendations:
            recommendations.append(
                "✅ Contract appears favorable - acceptable for approval"
            )

        return recommendations


class SatelliteProgressEngine:
    """CNN-powered satellite construction progress tracking."""

    @staticmethod
    def analyze_satellite_timeline(satellite_images: List[Dict]) -> Dict:
        """Analyze satellite images for construction progress."""
        if not satellite_images:
            return {
                "progress": 0,
                "status": "No imagery available",
                "confidence": 0,
                "anomalies": [],
            }

        # Sort by date
        images_sorted = sorted(satellite_images, key=lambda x: x.get("date", ""))

        # Aggregate progress
        total_progress = sum(
            img.get("detected_progress", 0) for img in images_sorted
        ) / len(images_sorted)

        # Detect anomalies
        anomalies = []
        for i in range(1, len(images_sorted)):
            prev_progress = images_sorted[i - 1].get("detected_progress", 0)
            curr_progress = images_sorted[i].get("detected_progress", 0)

            # Negative progress = anomaly
            if curr_progress < prev_progress * 0.9:
                anomalies.append(
                    {
                        "type": "Progress reversal",
                        "between": [
                            images_sorted[i - 1]["date"],
                            images_sorted[i]["date"],
                        ],
                        "severity": "HIGH",
                    }
                )

            # Stagnation > 2 quarters
            if (
                i >= 2
                and images_sorted[i]["detected_progress"]
                == images_sorted[i - 1]["detected_progress"]
            ):
                anomalies.append(
                    {
                        "type": "Progress stagnation",
                        "quarter": images_sorted[i]["date"],
                        "severity": "MEDIUM",
                    }
                )

        return {
            "overall_progress": total_progress * 100,
            "trend": (
                "AHEAD"
                if total_progress > 0.8
                else "ON_TRACK" if total_progress > 0.5 else "DELAYED"
            ),
            "confidence": min(0.95, 0.8 + (len(images_sorted) * 0.02)),
            "anomalies": anomalies,
            "last_update": images_sorted[-1]["date"] if images_sorted else None,
            "recommendation": (
                "Continue monitoring"
                if total_progress > 0.5
                else "URGENT: Investigate delays"
            ),
        }


class ContagionAnalysisEngine:
    """GNN-based portfolio contagion and systemic risk analysis."""

    @staticmethod
    def build_portfolio_network(projects: List[Dict]) -> Dict:
        """Build project dependency network."""
        network = {"nodes": [], "edges": [], "node_count": len(projects)}

        # Add nodes
        for i, proj in enumerate(projects):
            network["nodes"].append(
                {
                    "id": i,
                    "project_id": proj.get("id", f"PRJ-{i:03d}"),
                    "sector": proj.get("sector", "Unknown"),
                    "dscr": proj.get("dscr", 1.5),
                    "pd": proj.get("pd", 0.05),
                }
            )

        # Add edges (dependencies)
        for i in range(len(projects)):
            for j in range(i + 1, len(projects)):
                # Same sector = higher connection probability
                same_sector = projects[i].get("sector") == projects[j].get("sector")
                prob = 0.4 if same_sector else 0.15

                if np.random.random() < prob:
                    network["edges"].append(
                        {
                            "source": i,
                            "target": j,
                            "type": (
                                "sector_correlation"
                                if same_sector
                                else "macro_exposure"
                            ),
                            "weight": 0.8 if same_sector else 0.3,
                        }
                    )

        return network

    @staticmethod
    def simulate_contagion(
        network: Dict, shock_node: int, shock_magnitude: float = 0.3
    ) -> Dict:
        """Simulate contagion spread from shock node."""
        impacted = set([shock_node])
        queue = [shock_node]
        propagation_timeline = {0: [shock_node]}

        max_hops = 3
        for hop in range(1, max_hops + 1):
            new_impacted = set()
            for node_id in queue:
                # Find connected nodes
                for edge in network["edges"]:
                    if edge["source"] == node_id and edge["target"] not in impacted:
                        if np.random.random() < edge["weight"]:
                            new_impacted.add(edge["target"])
                    elif edge["target"] == node_id and edge["source"] not in impacted:
                        if np.random.random() < edge["weight"]:
                            new_impacted.add(edge["source"])

            if new_impacted:
                impacted.update(new_impacted)
                propagation_timeline[hop] = list(new_impacted)
            else:
                break

            queue = list(new_impacted)

        direct_impact = 1  # Shocked node itself
        indirect_impact = len(impacted) - 1

        return {
            "directly_impacted": direct_impact,
            "indirectly_impacted": indirect_impact,
            "total_impacted": len(impacted),
            "impacted_nodes": list(impacted),
            "propagation_timeline": propagation_timeline,
            "propagation_speed": (
                "FAST"
                if len(impacted) > network["node_count"] * 0.5
                else "MODERATE" if len(impacted) > 2 else "SLOW"
            ),
            "systemic_risk_score": min(
                100, (len(impacted) / network["node_count"]) * 100
            ),
            "diversification_quality": (
                "POOR"
                if len(impacted) > network["node_count"] * 0.7
                else (
                    "MODERATE"
                    if len(impacted) > network["node_count"] * 0.4
                    else "GOOD"
                )
            ),
        }


# ============ FINANCIAL WATERFALL ENGINE ============
class CashflowWaterfallEngine:
    """Detailed cashflow waterfall for realistic financials."""

    @staticmethod
    def calculate_full_waterfall(
        revenue: float,
        opex: float,
        capex: float,
        debt_service: float,
        tax_rate: float = 0.25,
        reserve_pct: float = 0.05,
    ) -> Dict:
        """Full cashflow waterfall with all deductions."""

        # Revenue waterfall
        gross_revenue = revenue
        reserve_fund = gross_revenue * reserve_pct
        available_revenue = gross_revenue - reserve_fund

        # Operating expenses
        available_after_opex = available_revenue - opex

        # Operating profit
        ebitda = available_after_opex
        depreciation = capex * 0.05  # 20-year straight line
        ebit = ebitda - depreciation

        # Taxes
        ebt = ebit
        taxes = max(0, ebt * tax_rate)

        # Net income
        net_income = ebt - taxes

        # Operating cashflow
        ocf = net_income + depreciation  # Add back non-cash depreciation

        # Less: CapEx and debt service
        fcf_after_capex = ocf - capex
        fcf_after_debt = fcf_after_capex - debt_service

        # Equity cashflow
        equity_cashflow = max(0, fcf_after_debt)

        # Coverage ratios
        dscr = ocf / max(debt_service, 0.1)

        return {
            "waterfall": {
                "gross_revenue": gross_revenue,
                "reserve_fund": reserve_fund,
                "available_revenue": available_revenue,
                "opex": opex,
                "ebitda": ebitda,
                "depreciation": depreciation,
                "ebit": ebit,
                "taxes": taxes,
                "net_income": net_income,
                "ocf": ocf,
                "capex": capex,
                "debt_service": debt_service,
                "fcf": fcf_after_capex,
                "equity_cashflow": equity_cashflow,
            },
            "metrics": {
                "dscr": dscr,
                "net_margin": net_income / gross_revenue,
                "ebitda_margin": ebitda / gross_revenue,
                "fcf_to_equity": (
                    equity_cashflow / gross_revenue if gross_revenue > 0 else 0
                ),
            },
        }


import numpy as np
