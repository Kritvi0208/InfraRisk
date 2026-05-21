"""
Automated risk scoring module for Phase 4 NLP pipeline.
Combines NER + classification scores for comprehensive risk assessment.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from contract_types import (
    ClassificationResult,
    Clause,
    ContractRiskScore,
    NamedEntity,
    RiskCategory,
    SeverityLevel,
)
from risk_rules import (
    CATEGORY_WEIGHTS,
    COUNTRY_RISK_FACTORS,
    GREEN_FLAG_KEYWORDS,
    INDUSTRY_RISK_FACTORS,
    MISSING_ELEMENT_PENALTIES,
    RED_FLAG_KEYWORDS,
    apply_adjustment_factors,
    calculate_base_score,
    get_red_flag_impact,
    get_severity_from_score,
    is_green_flag,
)


class ContractRiskScorer:
    """Automated risk scoring for contracts."""

    def __init__(self):
        """Initialize scorer."""
        self.scoring_history = []

    def score_contract(
        self,
        clauses: List[Clause],
        classification_results: List[ClassificationResult],
        entities: List[NamedEntity],
        industry: str = "default",
        country: str = "default",
    ) -> ContractRiskScore:
        """Calculate comprehensive contract risk score."""

        category_scores = {}
        red_flags = []
        green_flags = []

        # Score each risk category
        for category in RiskCategory:
            score = self._score_category(
                category, clauses, classification_results, entities
            )
            category_scores[category] = score

        # Aggregate scores
        overall_score = self._aggregate_scores(category_scores)

        # Detect red flags
        red_flags = self._detect_red_flags(clauses, entities)

        # Detect green flags
        green_flags = self._detect_green_flags(clauses, entities)

        # Apply missing element penalties
        missing_penalties = self._assess_missing_elements(clauses)
        overall_score += missing_penalties

        # Apply industry and country adjustments
        overall_score = apply_adjustment_factors(
            overall_score,
            industry=industry,
            country=country,
            missing_penalties=0.0,  # Already applied
        )

        # Clamp score
        overall_score = max(1.0, min(5.0, overall_score))

        # Determine severity
        severity = get_severity_from_score(overall_score)

        # Generate recommendation
        recommendation = self._generate_recommendation(
            overall_score, red_flags, green_flags
        )

        result = ContractRiskScore(
            overall_severity=severity,
            overall_score=overall_score,
            category_scores=category_scores,
            red_flags=red_flags,
            green_flags=green_flags,
            confidence=0.85,
            recommendation=recommendation,
        )

        self.scoring_history.append(result)
        return result

    def _score_category(
        self,
        category: RiskCategory,
        clauses: List[Clause],
        classification_results: List[ClassificationResult],
        entities: List[NamedEntity],
    ) -> float:
        """Score a specific risk category."""

        # Find clauses in this category
        category_clauses = [
            cr for cr in classification_results if cr.predicted_category == category
        ]

        if not category_clauses:
            return 1.0  # Minimal risk if no clauses in category

        # Calculate average confidence
        avg_confidence = sum(c.confidence for c in category_clauses) / len(
            category_clauses
        )

        # Get weight for category
        weight = CATEGORY_WEIGHTS.get(category, 1.0)

        # Base score from weight and confidence
        base = 2.5 + (weight - 1.0) * 0.5 + avg_confidence * 0.5

        # Check for red flags in category clauses
        red_flag_boost = 0.0
        for result in category_clauses:
            # Find corresponding clause
            clause = next((c for c in clauses if c.clause_id == result.clause_id), None)
            if clause and clause.text:
                for flag_keyword in RED_FLAG_KEYWORDS:
                    if flag_keyword in clause.text.lower():
                        severity, impact = get_red_flag_impact(flag_keyword)
                        red_flag_boost += impact * 0.3

        base += min(red_flag_boost, 1.5)

        return min(5.0, base)

    def _aggregate_scores(self, category_scores: Dict[RiskCategory, float]) -> float:
        """Aggregate category scores to overall score."""

        total_weight = 0.0
        weighted_sum = 0.0

        for category, score in category_scores.items():
            weight = CATEGORY_WEIGHTS.get(category, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 3.0

    def _detect_red_flags(
        self, clauses: List[Clause], entities: List[NamedEntity]
    ) -> List[str]:
        """Detect risk red flags in contract."""
        red_flags = []

        # Check for problematic keywords in clause text
        for clause in clauses:
            for flag_keyword, (severity, impact) in RED_FLAG_KEYWORDS.items():
                if flag_keyword in clause.text.lower():
                    red_flags.append(
                        f"{severity.value} - {flag_keyword} in {clause.full_reference}"
                    )

        # Check for missing key entities
        entity_types_found = set(e.entity_type for e in entities)
        required_entities = {
            "sponsor": "No Sponsor entity identified",
            "lender": "No Lender entity identified",
            "amount": "No financial Amount identified",
        }

        for entity_name, message in required_entities.items():
            # This is simplified - in reality would need better mapping
            if (
                len([e for e in entities if e.entity_type.value.lower() == entity_name])
                == 0
            ):
                red_flags.append(message)

        # Remove duplicates
        red_flags = list(set(red_flags))[:10]  # Limit to 10

        return red_flags

    def _detect_green_flags(
        self, clauses: List[Clause], entities: List[NamedEntity]
    ) -> List[str]:
        """Detect positive risk mitigators."""
        green_flags = []

        # Check for positive keywords
        all_text = " ".join(c.text for c in clauses).lower()

        for flag_keyword in GREEN_FLAG_KEYWORDS:
            if flag_keyword in all_text:
                green_flags.append(flag_keyword)

        # Check for comprehensive entities
        entity_types = {e.entity_type for e in entities}
        if len(entity_types) >= 4:
            green_flags.append("Comprehensive entity coverage detected")

        # Check for high-confidence classifications
        high_confidence_count = len([c for c in clauses if c.confidence >= 0.90])
        if high_confidence_count > len(clauses) * 0.5:
            green_flags.append("High extraction confidence across clauses")

        # Remove duplicates, limit to 5
        green_flags = list(set(green_flags))[:5]

        return green_flags

    def _assess_missing_elements(self, clauses: List[Clause]) -> float:
        """Assess penalties for missing key elements."""
        penalty = 0.0

        # Check for key clause types
        clause_refs = set(c.full_reference.lower() for c in clauses)

        missing_checks = {
            "milestone": "missing_milestones",
            "covenant": "missing_financial_covenants",
            "insurance": "missing_insurance",
            "termination": "missing_termination_clause",
        }

        for keyword, penalty_key in missing_checks.items():
            if not any(keyword in ref for ref in clause_refs):
                penalty += MISSING_ELEMENT_PENALTIES.get(penalty_key, 0.0)

        return penalty * 0.1  # Scale down overall impact

    def _generate_recommendation(
        self, score: float, red_flags: List[str], green_flags: List[str]
    ) -> str:
        """Generate risk mitigation recommendation."""

        if score >= 4.5:
            base = "CRITICAL RISK: Recommend thorough legal review before proceeding."
        elif score >= 3.5:
            base = "HIGH RISK: Consider legal review and risk mitigation strategies."
        elif score >= 2.5:
            base = "MEDIUM RISK: Standard due diligence recommended."
        else:
            base = "LOW RISK: Standard monitoring sufficient."

        # Add specific recommendations
        recommendations = [base]

        if red_flags:
            most_critical = red_flags[0]
            recommendations.append(f"Priority: Address '{most_critical}'")

        if len(green_flags) >= 3:
            recommendations.append("Positive: Strong mitigating factors present.")

        return " ".join(recommendations)

    def score_clause(self, clause: Clause, weight_multiplier: float = 1.0) -> float:
        """Score an individual clause."""

        # Base score from severity
        severity_map = {
            "Critical": 5.0,
            "High": 4.0,
            "Medium": 3.0,
            "Low": 2.0,
            "Minimal": 1.0,
        }
        base = severity_map.get(clause.severity.value, 3.0)

        # Apply category weight
        category_weight = CATEGORY_WEIGHTS.get(clause.risk_category, 1.0)

        # Apply confidence
        final_score = base * category_weight * clause.confidence * weight_multiplier

        return min(5.0, final_score)

    def compare_to_benchmark(
        self, contract_score: ContractRiskScore, benchmark_scores: List[float]
    ) -> Dict:
        """Compare contract risk score to benchmark transactions."""

        benchmark_mean = (
            sum(benchmark_scores) / len(benchmark_scores) if benchmark_scores else 3.0
        )
        benchmark_std = (
            (
                sum((s - benchmark_mean) ** 2 for s in benchmark_scores)
                / len(benchmark_scores)
            )
            ** 0.5
            if benchmark_scores
            else 0.5
        )

        deviation = (
            abs(contract_score.overall_score - benchmark_mean) / benchmark_std
            if benchmark_std > 0
            else 0
        )

        # Percentile rank
        better_than_count = sum(
            1 for s in benchmark_scores if s > contract_score.overall_score
        )
        percentile = (
            (better_than_count / len(benchmark_scores) * 100)
            if benchmark_scores
            else 50
        )

        return {
            "benchmark_mean": benchmark_mean,
            "benchmark_std": benchmark_std,
            "contract_score": contract_score.overall_score,
            "deviation": deviation,
            "percentile": percentile,
            "assessment": (
                "Above average risk" if percentile < 50 else "Below average risk"
            ),
        }

    def export_risk_report_json(self, risk_score: ContractRiskScore) -> str:
        """Export risk score as JSON."""
        return json.dumps(risk_score.to_dict(), indent=2, default=str)

    def generate_risk_report(self, risk_score: ContractRiskScore) -> str:
        """Generate human-readable risk report."""
        lines = ["=== CONTRACT RISK ASSESSMENT REPORT ===\n"]

        lines.append(f"Overall Risk Severity: {risk_score.overall_severity.value}")
        lines.append(f"Risk Score: {risk_score.overall_score:.2f}/5.0")
        lines.append(f"Confidence: {risk_score.confidence:.2%}\n")

        lines.append("Category Risk Breakdown:")
        for category, score in sorted(
            risk_score.category_scores.items(), key=lambda x: x[1], reverse=True
        ):
            severity = get_severity_from_score(score)
            lines.append(f"  {category.value}: {score:.2f} ({severity.value})")

        if risk_score.red_flags:
            lines.append(f"\n🚩 Red Flags ({len(risk_score.red_flags)}):")
            for flag in risk_score.red_flags[:5]:
                lines.append(f"  • {flag}")
            if len(risk_score.red_flags) > 5:
                lines.append(f"  ... and {len(risk_score.red_flags) - 5} more")

        if risk_score.green_flags:
            lines.append(f"\n✅ Green Flags ({len(risk_score.green_flags)}):")
            for flag in risk_score.green_flags[:5]:
                lines.append(f"  • {flag}")

        lines.append(f"\n📋 Recommendation:")
        lines.append(f"  {risk_score.recommendation}")

        return "\n".join(lines)
