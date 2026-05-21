"""
Custom Named Entity Recognition (NER) module for Phase 4 NLP pipeline.
Specialized NER for infrastructure contracts using spaCy + custom rules.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from contract_types import EntityType, NamedEntity


@dataclass
class NERMetrics:
    """Evaluation metrics for NER."""

    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    @property
    def precision(self) -> float:
        total_predicted = self.true_positives + self.false_positives
        return self.true_positives / total_predicted if total_predicted > 0 else 0.0

    @property
    def recall(self) -> float:
        total_actual = self.true_positives + self.false_negatives
        return self.true_positives / total_actual if total_actual > 0 else 0.0

    @property
    def f1_score(self) -> float:
        p = self.precision
        r = self.recall
        if p + r == 0:
            return 0.0
        return 2 * (p * r) / (p + r)


class ContractNER:
    """Named Entity Recognizer for infrastructure contracts."""

    def __init__(self):
        """Initialize NER with patterns and rules."""
        self.metrics = NERMetrics()
        self._init_patterns()

    def _init_patterns(self):
        """Initialize regex patterns for entity recognition."""
        # Sponsor patterns
        self.sponsor_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is\s+)?(?:the\s+)?[Ss]ponsor",
            r"[Ss]ponsor[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"[Pp]roject [Ss]ponsor[:\s]+([A-Z][\w\s]+)",
        ]

        # Lender patterns
        self.lender_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is\s+)?(?:the\s+)?[Ll]ender",
            r"[Ll]ender[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"[Ff]inancing [Pp]roviders?[:\s]+([A-Z][\w\s]+)",
            r"[Dd]ebt [Pp]roviders?[:\s]+([A-Z][\w\s]+)",
        ]

        # Amount patterns
        self.amount_patterns = [
            r"(?:total\s+)?(?:project\s+)?(?:loan\s+)?amount[:\s]+([A-Z]{3})?\s*([\d,]+(?:\.\d{2})?)\s*(?:million|billion|MM|bn)?",
            r"([A-Z]{3})?\s*([\d,]+(?:\.\d{2})?)\s*(?:million|billion|MM|bn|USD|EUR|GBP)",
            r"[Ll]oan[:\s]+([A-Z]{3})?\s*([\d,]+(?:\.\d+)?)",
        ]

        # Date patterns
        self.date_patterns = [
            r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b)",
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]

        # Milestone patterns
        self.milestone_patterns = [
            r"[Mm]ilestone[:\s]+([\w\s]+?)(?:\.|,|and)",
            r"(?:Financial|Technical|Operational)\s+[Mm]ilestone[:\s]+([\w\s]+)",
            r"[Cc]ompletion\s+(?:of\s+)?(?:the\s+)?([\w\s]+)",
        ]

        # Covenant patterns
        self.covenant_patterns = [
            r"[Cc]ovenant[:\s]+([\w\s]+?)(?:,|;|\.|and)",
            r"[Ff]inancial [Cc]ovenant[:\s]+([\w\s]+)",
            r"(?:Debt Service Coverage Ratio|Leverage Ratio|Minimum Liquidity)",
        ]

        # Party patterns
        self.party_patterns = [
            r"(?:[Bb]etween|entered into (?:as of|on|by and between))\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

    def extract_entities(self, text: str) -> List[NamedEntity]:
        """Extract all entities from contract text."""
        entities = []

        # Extract sponsors
        entities.extend(
            self._extract_with_pattern(text, self.sponsor_patterns, EntityType.SPONSOR)
        )

        # Extract lenders
        entities.extend(
            self._extract_with_pattern(text, self.lender_patterns, EntityType.LENDER)
        )

        # Extract amounts
        entities.extend(self._extract_amounts(text))

        # Extract dates
        entities.extend(
            self._extract_with_pattern(text, self.date_patterns, EntityType.DATE)
        )

        # Extract milestones
        entities.extend(
            self._extract_with_pattern(
                text, self.milestone_patterns, EntityType.MILESTONE
            )
        )

        # Extract covenants
        entities.extend(
            self._extract_with_pattern(
                text, self.covenant_patterns, EntityType.COVENANT
            )
        )

        # Extract parties
        entities.extend(
            self._extract_with_pattern(text, self.party_patterns, EntityType.PARTY)
        )

        # Remove duplicates
        entities = self._remove_duplicates(entities)

        return entities

    def _extract_with_pattern(
        self, text: str, patterns: List[str], entity_type: EntityType
    ) -> List[NamedEntity]:
        """Extract entities using regex patterns."""
        entities = []

        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                # Get the first captured group
                extracted_text = match.group(1) if match.groups() else match.group(0)
                extracted_text = extracted_text.strip()

                if len(extracted_text) > 2:  # Filter out very short matches
                    entity = NamedEntity(
                        text=extracted_text,
                        entity_type=entity_type,
                        start_pos=match.start(1 if match.groups() else 0),
                        end_pos=match.end(1 if match.groups() else 0),
                        confidence=0.85,
                        extracted_value=extracted_text,
                    )
                    entities.append(entity)

        return entities

    def _extract_amounts(self, text: str) -> List[NamedEntity]:
        """Extract financial amounts with special handling."""
        entities = []

        for pattern in self.amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract currency and amount
                currency = (
                    match.group(1) if match.groups() and match.group(1) else "USD"
                )
                amount = (
                    match.group(2)
                    if match.groups() and len(match.groups()) > 1
                    else match.group(0)
                )

                full_text = match.group(0)

                entity = NamedEntity(
                    text=full_text,
                    entity_type=EntityType.AMOUNT,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90,
                    extracted_value=f"{currency} {amount}",
                    metadata={"currency": currency, "amount": amount},
                )
                entities.append(entity)

        return entities

    def _remove_duplicates(self, entities: List[NamedEntity]) -> List[NamedEntity]:
        """Remove duplicate entities."""
        seen = set()
        unique = []

        for entity in entities:
            key = (entity.text, entity.entity_type, entity.start_pos)
            if key not in seen:
                seen.add(key)
                unique.append(entity)

        return unique

    def extract_percentages(self, text: str) -> List[NamedEntity]:
        """Extract percentage values."""
        entities = []

        patterns = [
            r"(\d+(?:\.\d{1,2})?)\s*%",
            r"(\d+(?:\.\d{1,2})?)\s*(?:per\s+)?cent",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                percentage = match.group(1)

                entity = NamedEntity(
                    text=match.group(0),
                    entity_type=EntityType.PERCENTAGE,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    extracted_value=percentage,
                    metadata={"percentage": percentage},
                )
                entities.append(entity)

        return entities

    def extract_locations(self, text: str) -> List[NamedEntity]:
        """Extract location information."""
        entities = []

        # Common countries and regions
        locations = [
            "United States",
            "USA",
            "India",
            "China",
            "Brazil",
            "Mexico",
            "United Kingdom",
            "UK",
            "Germany",
            "France",
            "Singapore",
            "Australia",
            "Canada",
            "UAE",
            "Saudi Arabia",
            "New York",
            "California",
        ]

        for location in locations:
            matches = re.finditer(
                r"\b" + re.escape(location) + r"\b", text, re.IGNORECASE
            )
            for match in matches:
                entity = NamedEntity(
                    text=match.group(0),
                    entity_type=EntityType.LOCATION,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    extracted_value=location,
                )
                entities.append(entity)

        return entities

    def generate_training_data(self, num_samples: int = 100) -> List[Dict]:
        """Generate mock training data for NER."""
        training_data = []

        # Sample contract texts with entities
        templates = [
            {
                "text": "This Agreement is between {sponsor} as Sponsor and {lender} as Lender. "
                "Total Project Amount: {amount} million. Effective Date: {date}. "
                "Key Milestone: {milestone}. Financial Covenant: {covenant}.",
                "entities": {
                    "sponsor": EntityType.SPONSOR,
                    "lender": EntityType.LENDER,
                    "amount": EntityType.AMOUNT,
                    "date": EntityType.DATE,
                    "milestone": EntityType.MILESTONE,
                    "covenant": EntityType.COVENANT,
                },
            }
        ]

        sample_sponsors = [
            "PowerCorp Ltd",
            "Infrastructure Partners",
            "Green Energy Solutions",
        ]
        sample_lenders = [
            "International Finance Bank",
            "Development Finance Institution",
        ]
        sample_amounts = ["500", "750", "1000"]
        sample_dates = ["January 15, 2024", "March 20, 2024"]
        sample_milestones = [
            "Financial Close",
            "Construction Start",
            "Commercial Operations",
        ]
        sample_covenants = [
            "Debt Service Coverage Ratio of 1.2x",
            "Minimum Liquidity of $50M",
        ]

        for i in range(num_samples):
            template = templates[0]
            text = template["text"].format(
                sponsor=sample_sponsors[i % len(sample_sponsors)],
                lender=sample_lenders[i % len(sample_lenders)],
                amount=sample_amounts[i % len(sample_amounts)],
                date=sample_dates[i % len(sample_dates)],
                milestone=sample_milestones[i % len(sample_milestones)],
                covenant=sample_covenants[i % len(sample_covenants)],
            )

            training_data.append(
                {"text": text, "entities": template["entities"], "example_id": i}
            )

        return training_data

    def evaluate(
        self, predicted: List[NamedEntity], ground_truth: List[NamedEntity]
    ) -> NERMetrics:
        """Evaluate NER performance."""
        metrics = NERMetrics()

        # Convert to sets for comparison
        pred_set = set((e.text, e.entity_type) for e in predicted)
        truth_set = set((e.text, e.entity_type) for e in ground_truth)

        metrics.true_positives = len(pred_set & truth_set)
        metrics.false_positives = len(pred_set - truth_set)
        metrics.false_negatives = len(truth_set - pred_set)

        return metrics

    def generate_evaluation_report(self, metrics: NERMetrics) -> str:
        """Generate NER evaluation report."""
        lines = ["=== NER EVALUATION REPORT ===\n"]

        lines.append(f"True Positives: {metrics.true_positives}")
        lines.append(f"False Positives: {metrics.false_positives}")
        lines.append(f"False Negatives: {metrics.false_negatives}\n")

        lines.append(f"Precision: {metrics.precision:.4f}")
        lines.append(f"Recall: {metrics.recall:.4f}")
        lines.append(f"F1-Score: {metrics.f1_score:.4f}\n")

        lines.append("Metrics Interpretation:")
        if metrics.f1_score > 0.85:
            lines.append("  ✓ Excellent NER performance")
        elif metrics.f1_score > 0.75:
            lines.append("  ✓ Good NER performance")
        elif metrics.f1_score > 0.60:
            lines.append("  ⚠ Acceptable NER performance")
        else:
            lines.append("  ✗ NER needs improvement")

        return "\n".join(lines)
