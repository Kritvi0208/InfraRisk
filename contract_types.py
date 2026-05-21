"""
Contract entity dataclasses and types for Phase 4 NLP pipeline.
Defines all data structures used across the NLP modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RiskCategory(str, Enum):
    """12 risk categories for contract classification."""

    FORCE_MAJEURE = "Force Majeure"
    TERMINATION = "Termination"
    COVENANTS = "Covenants"
    FINANCIAL = "Financial"
    ENVIRONMENTAL = "Environmental"
    LABOR = "Labor"
    SAFETY = "Safety"
    INTELLECTUAL_PROPERTY = "Intellectual Property"
    DISPUTES = "Disputes"
    INSURANCE = "Insurance"
    PENALTIES = "Penalties"
    OTHER = "Other"


class EntityType(str, Enum):
    """Named Entity types for contracts."""

    SPONSOR = "Sponsor"
    LENDER = "Lender"
    AMOUNT = "Amount"
    DATE = "Date"
    MILESTONE = "Milestone"
    COVENANT = "Covenant"
    PARTY = "Party"
    LOCATION = "Location"
    PERCENTAGE = "Percentage"


class SeverityLevel(str, Enum):
    """Severity levels for risk scoring."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    MINIMAL = "Minimal"


@dataclass
class NamedEntity:
    """Represents a named entity extracted from contract text."""

    text: str
    entity_type: EntityType
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    extracted_value: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "text": self.text,
            "entity_type": self.entity_type.value,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "confidence": self.confidence,
            "extracted_value": self.extracted_value,
            "metadata": self.metadata,
        }


@dataclass
class ClauseReference:
    """Represents a clause reference like 'Clause 14.3(b)(ii)'."""

    full_reference: str
    chapter: str
    section: str
    subsection: Optional[str] = None
    subsubsection: Optional[str] = None
    paragraph: Optional[str] = None
    depth: int = 1

    def to_dict(self):
        return {
            "full_reference": self.full_reference,
            "chapter": self.chapter,
            "section": self.section,
            "subsection": self.subsection,
            "subsubsection": self.subsubsection,
            "paragraph": self.paragraph,
            "depth": self.depth,
        }


@dataclass
class Clause:
    """Represents a contract clause with hierarchy and references."""

    clause_id: str
    title: str
    text: str
    full_reference: str
    risk_category: RiskCategory = RiskCategory.OTHER
    severity: SeverityLevel = SeverityLevel.MINIMAL
    parent_clause_id: Optional[str] = None
    child_clauses: List[str] = field(default_factory=list)
    referenced_clauses: List[str] = field(default_factory=list)
    entities: List[NamedEntity] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    confidence: float = 1.0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "clause_id": self.clause_id,
            "title": self.title,
            "text": self.text,
            "full_reference": self.full_reference,
            "risk_category": self.risk_category.value,
            "severity": self.severity.value,
            "parent_clause_id": self.parent_clause_id,
            "child_clauses": self.child_clauses,
            "referenced_clauses": self.referenced_clauses,
            "entities": [e.to_dict() for e in self.entities],
            "start_line": self.start_line,
            "end_line": self.end_line,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class ContractRiskScore:
    """Aggregated risk score for a contract or clause."""

    overall_severity: SeverityLevel
    overall_score: float
    category_scores: Dict[RiskCategory, float] = field(default_factory=dict)
    red_flags: List[str] = field(default_factory=list)
    green_flags: List[str] = field(default_factory=list)
    confidence: float = 1.0
    recommendation: str = ""

    def to_dict(self):
        return {
            "overall_severity": self.overall_severity.value,
            "overall_score": self.overall_score,
            "category_scores": {k.value: v for k, v in self.category_scores.items()},
            "red_flags": self.red_flags,
            "green_flags": self.green_flags,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
        }


@dataclass
class ClassificationResult:
    """Result of clause classification."""

    clause_id: str
    predicted_category: RiskCategory
    confidence: float
    top_k_predictions: List[Tuple[RiskCategory, float]] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self):
        return {
            "clause_id": self.clause_id,
            "predicted_category": self.predicted_category.value,
            "confidence": self.confidence,
            "top_k_predictions": [
                (cat.value, conf) for cat, conf in self.top_k_predictions
            ],
            "explanation": self.explanation,
        }


@dataclass
class BenchmarkTransaction:
    """Represents a comparable transaction from benchmark database."""

    transaction_id: str
    sector: str
    country: str
    project_value: float
    tenor_years: int
    equity_percentage: float
    debt_percentage: float
    key_milestones: int
    financial_covenants: Dict[str, float] = field(default_factory=dict)
    risk_score: float = 3.0
    completion_status: str = "Active"
    metadata: Dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "sector": self.sector,
            "country": self.country,
            "project_value": self.project_value,
            "tenor_years": self.tenor_years,
            "equity_percentage": self.equity_percentage,
            "debt_percentage": self.debt_percentage,
            "key_milestones": self.key_milestones,
            "financial_covenants": self.financial_covenants,
            "risk_score": self.risk_score,
            "completion_status": self.completion_status,
            "metadata": self.metadata,
        }


@dataclass
class ComparativeAnalysisResult:
    """Result of comparing extracted contract to benchmark."""

    transaction_id: str
    benchmark_transaction: BenchmarkTransaction
    similarity_score: float
    deviations: List[Dict] = field(default_factory=list)
    non_standard_terms: List[str] = field(default_factory=list)
    deviation_severity: SeverityLevel = SeverityLevel.MINIMAL
    recommendations: List[str] = field(default_factory=list)
    outlier_flags: List[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "benchmark_transaction": self.benchmark_transaction.to_dict(),
            "similarity_score": self.similarity_score,
            "deviations": self.deviations,
            "non_standard_terms": self.non_standard_terms,
            "deviation_severity": self.deviation_severity.value,
            "recommendations": self.recommendations,
            "outlier_flags": self.outlier_flags,
        }


@dataclass
class ContractAnalysisResult:
    """Complete analysis result from full pipeline."""

    contract_id: str
    filename: str
    extracted_clauses: List[Clause] = field(default_factory=list)
    named_entities: List[NamedEntity] = field(default_factory=list)
    risk_scores: ContractRiskScore = field(
        default_factory=lambda: ContractRiskScore(
            overall_severity=SeverityLevel.MEDIUM, overall_score=3.0
        )
    )
    classification_results: List[ClassificationResult] = field(default_factory=list)
    comparative_analysis: Optional[ComparativeAnalysisResult] = None
    extraction_time: float = 0.0
    processing_errors: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "contract_id": self.contract_id,
            "filename": self.filename,
            "extracted_clauses": [c.to_dict() for c in self.extracted_clauses],
            "named_entities": [e.to_dict() for e in self.named_entities],
            "risk_scores": self.risk_scores.to_dict(),
            "classification_results": [
                c.to_dict() for c in self.classification_results
            ],
            "comparative_analysis": (
                self.comparative_analysis.to_dict()
                if self.comparative_analysis
                else None
            ),
            "extraction_time": self.extraction_time,
            "processing_errors": self.processing_errors,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat(),
        }
