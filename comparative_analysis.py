"""
Comparative analysis module for Phase 4 NLP pipeline.
Compares extracted clauses against benchmark database.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from contract_types import (
    BenchmarkTransaction,
    Clause,
    ComparativeAnalysisResult,
    SeverityLevel,
)


class ComparativeAnalyzer:
    """Analyzes contracts against benchmark transactions."""

    def __init__(self, benchmark_db):
        """Initialize analyzer with benchmark database."""
        self.benchmark_db = benchmark_db
        self.analysis_cache = {}

    def analyze_contract(
        self,
        contract_id: str,
        clauses: List[Clause],
        sector: str,
        country: str,
        project_value: float,
        tenor_years: int,
        equity_percentage: float,
        milestone_count: int,
    ) -> ComparativeAnalysisResult:
        """Perform comprehensive comparative analysis."""

        # Find comparable transactions
        comparables = self.benchmark_db.find_similar_deals(
            sector=sector,
            country=country,
            project_value=project_value,
            tenor_years=tenor_years,
            tolerance=0.30,
            max_results=5,
        )

        if not comparables:
            return ComparativeAnalysisResult(
                transaction_id=contract_id,
                benchmark_transaction=BenchmarkTransaction(
                    transaction_id="NONE",
                    sector=sector,
                    country=country,
                    project_value=project_value,
                    tenor_years=tenor_years,
                    equity_percentage=equity_percentage,
                    debt_percentage=100 - equity_percentage,
                    key_milestones=milestone_count,
                ),
                similarity_score=0.0,
                non_standard_terms=["No comparable transactions found"],
                deviation_severity=SeverityLevel.MEDIUM,
            )

        # Use median comparable as reference
        median_comparable = comparables[len(comparables) // 2]

        # Calculate similarity
        similarity = self._calculate_similarity(
            project_value,
            project_value_benchmark=median_comparable.project_value,
            tenor=tenor_years,
            tenor_benchmark=median_comparable.tenor_years,
            equity=equity_percentage,
            equity_benchmark=median_comparable.equity_percentage,
        )

        # Detect deviations
        deviations = self._detect_deviations(
            clauses=clauses,
            benchmark_txn=median_comparable,
            equity_percentage=equity_percentage,
            milestone_count=milestone_count,
        )

        # Identify non-standard terms
        non_standard = self._identify_non_standard_terms(clauses, median_comparable)

        # Determine severity
        deviation_severity = self._assess_deviation_severity(deviations)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            clauses, median_comparable, deviations
        )

        # Detect outliers
        outlier_flags = self._detect_outlier_conditions(
            project_value=project_value,
            equity=equity_percentage,
            milestone_count=milestone_count,
            comparables=comparables,
        )

        result = ComparativeAnalysisResult(
            transaction_id=contract_id,
            benchmark_transaction=median_comparable,
            similarity_score=similarity,
            deviations=deviations,
            non_standard_terms=non_standard,
            deviation_severity=deviation_severity,
            recommendations=recommendations,
            outlier_flags=outlier_flags,
        )

        self.analysis_cache[contract_id] = result
        return result

    def _calculate_similarity(
        self,
        project_value: float,
        project_value_benchmark: float,
        tenor: int,
        tenor_benchmark: int,
        equity: float,
        equity_benchmark: float,
    ) -> float:
        """Calculate similarity score (0-1) between contracts."""

        # Normalize differences
        value_diff = min(
            1.0,
            abs(project_value - project_value_benchmark)
            / max(project_value, project_value_benchmark, 1),
        )
        tenor_diff = min(
            1.0, abs(tenor - tenor_benchmark) / max(tenor, tenor_benchmark, 1)
        )
        equity_diff = abs(equity - equity_benchmark) / 100.0

        # Weight the differences
        similarity = 1.0 - (0.4 * value_diff + 0.3 * tenor_diff + 0.3 * equity_diff)

        return max(0.0, min(1.0, similarity))

    def _detect_deviations(
        self,
        clauses: List[Clause],
        benchmark_txn: BenchmarkTransaction,
        equity_percentage: float,
        milestone_count: int,
    ) -> List[Dict]:
        """Detect deviations from benchmark norms."""

        deviations = []

        # Check equity percentage
        bench_equity = benchmark_txn.equity_percentage
        if abs(equity_percentage - bench_equity) > 5.0:
            direction = "higher" if equity_percentage > bench_equity else "lower"
            deviations.append(
                {
                    "type": "equity_percentage",
                    "value": equity_percentage,
                    "benchmark": bench_equity,
                    "deviation": equity_percentage - bench_equity,
                    "description": f"Equity {direction} than benchmark ({equity_percentage}% vs {bench_equity}%)",
                    "severity": (
                        SeverityLevel.MEDIUM
                        if abs(equity_percentage - bench_equity) > 10
                        else SeverityLevel.LOW
                    ),
                }
            )

        # Check milestone count
        bench_milestones = benchmark_txn.key_milestones
        if abs(milestone_count - bench_milestones) > 2:
            direction = "more" if milestone_count > bench_milestones else "fewer"
            deviations.append(
                {
                    "type": "milestone_count",
                    "value": milestone_count,
                    "benchmark": bench_milestones,
                    "deviation": milestone_count - bench_milestones,
                    "description": f"{direction.capitalize()} milestones than benchmark ({milestone_count} vs {bench_milestones})",
                    "severity": (
                        SeverityLevel.LOW
                        if abs(milestone_count - bench_milestones) <= 3
                        else SeverityLevel.MEDIUM
                    ),
                }
            )

        # Check financial covenant stringency
        clause_refs = [c.full_reference.lower() for c in clauses]
        has_covenants = any(
            "covenant" in ref or "dscr" in ref or "leverage" in ref
            for ref in clause_refs
        )

        if not has_covenants and benchmark_txn.financial_covenants:
            deviations.append(
                {
                    "type": "missing_covenants",
                    "value": 0,
                    "benchmark": len(benchmark_txn.financial_covenants),
                    "deviation": 0,
                    "description": "Missing explicit financial covenants found in benchmarks",
                    "severity": SeverityLevel.HIGH,
                }
            )

        # Check insurance clause presence
        has_insurance = any("insurance" in ref for ref in clause_refs)
        if not has_insurance:
            deviations.append(
                {
                    "type": "missing_insurance",
                    "value": 0,
                    "benchmark": 1,
                    "deviation": -1,
                    "description": "Missing explicit insurance requirements",
                    "severity": SeverityLevel.MEDIUM,
                }
            )

        return deviations

    def _identify_non_standard_terms(
        self,
        clauses: List[Clause],
        benchmark_txn: BenchmarkTransaction,
    ) -> List[str]:
        """Identify non-standard clause terms."""

        non_standard = []
        clause_text_lower = " ".join(c.text.lower() for c in clauses)

        # Check for unusual termination rights
        if "termination for convenience" in clause_text_lower:
            non_standard.append(
                "Unusual: Termination for Convenience (not standard in comparable deals)"
            )

        # Check for unusual equity kickers
        if "equity kicker" in clause_text_lower or "warrant" in clause_text_lower:
            non_standard.append("Non-standard: Equity kicker/warrant provision")

        # Check for negative pledge relaxation
        if "negative pledge waived" in clause_text_lower:
            non_standard.append("Non-standard: Waived negative pledge restriction")

        # Check for sponsor support requirements
        if (
            "sponsor support" not in clause_text_lower
            and benchmark_txn.equity_percentage > 25
        ):
            non_standard.append("Missing: Explicit sponsor support undertakings")

        # Check for unusual lender protections
        if "cross-default" not in clause_text_lower:
            non_standard.append("Non-standard: No cross-default provision")

        return non_standard[:5]  # Limit to 5

    def _assess_deviation_severity(self, deviations: List[Dict]) -> SeverityLevel:
        """Assess overall deviation severity."""

        if not deviations:
            return SeverityLevel.MINIMAL

        severity_values = {
            SeverityLevel.CRITICAL: 5,
            SeverityLevel.HIGH: 4,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.LOW: 2,
            SeverityLevel.MINIMAL: 1,
        }

        max_severity = max(
            (
                severity_values.get(d.get("severity", SeverityLevel.LOW), 2)
                for d in deviations
            ),
            default=1,
        )

        # Map back to severity
        for severity, value in severity_values.items():
            if value == max_severity:
                return severity

        return SeverityLevel.MEDIUM

    def _generate_recommendations(
        self,
        clauses: List[Clause],
        benchmark_txn: BenchmarkTransaction,
        deviations: List[Dict],
    ) -> List[str]:
        """Generate recommendations based on analysis."""

        recommendations = []

        # Check for high-risk deviations
        high_severity_deviations = [
            d
            for d in deviations
            if d.get("severity") in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
        ]

        if high_severity_deviations:
            recommendations.append(
                f"Address {len(high_severity_deviations)} high-severity deviation(s) before proceeding"
            )

        # Benchmark-specific recommendations
        if benchmark_txn.risk_score > 3.5:
            recommendations.append(
                "Note: Benchmark transaction has elevated risk profile - consider lower-risk alternatives"
            )

        # Check for missing protections
        clause_refs = [c.full_reference.lower() for c in clauses]
        if not any("change of control" in ref for ref in clause_refs):
            recommendations.append(
                "Consider adding explicit Change of Control provisions"
            )

        # Check for adequate milestones
        if len(clauses) < 5:
            recommendations.append(
                "Consider expanding clause coverage for better protection"
            )

        # Equity structure recommendation
        if len([d for d in deviations if d.get("type") == "equity_percentage"]) > 0:
            recommendations.append(
                "Review equity structure consistency with market norms"
            )

        return recommendations[:5]  # Limit to 5

    def _detect_outlier_conditions(
        self,
        project_value: float,
        equity: float,
        milestone_count: int,
        comparables: List[BenchmarkTransaction],
    ) -> List[str]:
        """Detect outlier conditions."""

        outliers = []

        if not comparables:
            return outliers

        # Value outlier
        values = [t.project_value for t in comparables]
        avg_value = sum(values) / len(values)
        if (
            abs(project_value - avg_value)
            > 2 * (sum((v - avg_value) ** 2 for v in values) / len(values)) ** 0.5
        ):
            outliers.append("PROJECT_VALUE_OUTLIER")

        # Equity outlier
        equities = [t.equity_percentage for t in comparables]
        avg_equity = sum(equities) / len(equities)
        if abs(equity - avg_equity) > 15:
            outliers.append("EQUITY_STRUCTURE_OUTLIER")

        # Milestone outlier
        milestones = [t.key_milestones for t in comparables]
        avg_milestones = sum(milestones) / len(milestones)
        if abs(milestone_count - avg_milestones) > 3:
            outliers.append("MILESTONE_COUNT_OUTLIER")

        return outliers

    def generate_comparative_report(self, analysis: ComparativeAnalysisResult) -> str:
        """Generate comparative analysis report."""

        lines = ["=== COMPARATIVE ANALYSIS REPORT ===\n"]

        lines.append(f"Transaction ID: {analysis.transaction_id}")
        lines.append(
            f"Benchmark Transaction: {analysis.benchmark_transaction.transaction_id}"
        )
        lines.append(f"Similarity Score: {analysis.similarity_score:.2%}\n")

        lines.append(f"Deviation Severity: {analysis.deviation_severity.value}")
        lines.append(f"Total Deviations Found: {len(analysis.deviations)}\n")

        if analysis.deviations:
            lines.append("Deviations:")
            for dev in analysis.deviations:
                lines.append(f"  • {dev.get('description', 'Unknown deviation')}")

        if analysis.non_standard_terms:
            lines.append(f"\nNon-Standard Terms ({len(analysis.non_standard_terms)}):")
            for term in analysis.non_standard_terms:
                lines.append(f"  • {term}")

        if analysis.outlier_flags:
            lines.append(f"\nOutlier Flags ({len(analysis.outlier_flags)}):")
            for flag in analysis.outlier_flags:
                lines.append(f"  ⚠ {flag}")

        if analysis.recommendations:
            lines.append(f"\nRecommendations ({len(analysis.recommendations)}):")
            for rec in analysis.recommendations:
                lines.append(f"  → {rec}")

        return "\n".join(lines)

    def export_analysis_json(self, analysis: ComparativeAnalysisResult) -> str:
        """Export analysis as JSON."""
        return json.dumps(analysis.to_dict(), indent=2, default=str)
