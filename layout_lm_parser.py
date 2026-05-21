"""
LayoutLM-based PDF parsing module for Phase 4 NLP pipeline.
Extracts sections, clauses, and nested references from contract PDFs.
Mock LayoutLM implementation using structure preservation patterns.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from contract_types import Clause, ClauseReference, RiskCategory, SeverityLevel


@dataclass
class PDFStructure:
    """Represents extracted PDF structure."""

    sections: List[Dict] = field(default_factory=list)
    clauses: List[Clause] = field(default_factory=list)
    pages: int = 0
    total_text: str = ""
    metadata: Dict = field(default_factory=dict)


class LayoutLMParser:
    """Mock LayoutLM-based parser for contract PDFs."""

    def __init__(self, model_name: str = "microsoft/layoutlm-base-uncased"):
        """Initialize parser with mock model."""
        self.model_name = model_name
        self.clause_pattern = re.compile(
            r"(?:Clause|Section|Article|Chapter)?\s*(\d+)(?:\.(\d+))?(?:\(([a-z])\))?(?:\(([ivxlc]+)\))?[\.\:\-\s]+(.+)?",
            re.IGNORECASE,
        )
        self.reference_pattern = re.compile(
            r"Clause\s+(\d+\.\d+(?:\([a-z]\))?(?:\([ivxlc]+\))?)"
        )

    def parse_pdf(self, pdf_path: str, extract_text: str = "") -> PDFStructure:
        """
        Parse PDF and extract structured information.
        Mock implementation - processes pre-extracted text.
        """
        structure = PDFStructure()
        structure.total_text = extract_text

        # Extract sections
        structure.sections = self._extract_sections(extract_text)

        # Extract clauses with hierarchy
        structure.clauses = self._extract_clauses(extract_text)

        # Estimate pages
        structure.pages = max(1, len(extract_text) // 3000)

        # Extract metadata
        structure.metadata = self._extract_metadata(extract_text)

        return structure

    def _extract_sections(self, text: str) -> List[Dict]:
        """Extract major sections from text."""
        sections = []

        # Look for section headers
        lines = text.split("\n")
        for i, line in enumerate(lines):
            # Check if line looks like a section header
            if re.match(r"^[A-Z][A-Z\s]+$", line.strip()) and len(line.strip()) > 3:
                section = {
                    "title": line.strip(),
                    "start_line": i,
                    "content": [],
                    "subsections": [],
                }

                # Collect content until next section
                j = i + 1
                while j < len(lines) and not re.match(
                    r"^[A-Z][A-Z\s]+$", lines[j].strip()
                ):
                    section["content"].append(lines[j])
                    j += 1

                section["end_line"] = j - 1
                sections.append(section)

        return sections

    def _extract_clauses(self, text: str) -> List[Clause]:
        """Extract clauses with hierarchical structure."""
        clauses = []
        clause_dict = {}

        lines = text.split("\n")
        current_clause = None
        clause_counter = 0

        for line_num, line in enumerate(lines):
            # Match clause headers
            match = self.clause_pattern.search(line)
            if match:
                chapter = match.group(1)
                section = match.group(2) or "0"
                subsection = match.group(3)
                subsubsection = match.group(4)

                # Create unique clause ID
                clause_id = (
                    f"cl_{chapter}_{section}_{subsection or 'a'}_{subsubsection or '0'}"
                )
                if clause_id in clause_dict:
                    clause_id = f"{clause_id}_{clause_counter}"

                clause_counter += 1

                # Determine parent clause
                parent_id = None
                if subsection or subsubsection:
                    parent_section = f"cl_{chapter}_{section}"
                    if parent_section in clause_dict:
                        parent_id = parent_section

                # Extract title from matched line
                title = line.split(match.group(0))[-1].strip() if match else "Untitled"
                title = title[:100]  # Truncate long titles

                # Create clause
                clause = Clause(
                    clause_id=clause_id,
                    title=title,
                    text="",
                    full_reference=f"Clause {chapter}.{section}"
                    + (f"({subsection})" if subsection else "")
                    + (f"({subsubsection})" if subsubsection else ""),
                    parent_clause_id=parent_id,
                    start_line=line_num,
                    confidence=0.95 if match else 0.70,
                )

                # Add to parent if applicable
                if parent_id and parent_id in clause_dict:
                    clause_dict[parent_id].child_clauses.append(clause_id)

                current_clause = clause
                clause_dict[clause_id] = clause
                clauses.append(clause)

            # Add content to current clause
            elif current_clause and line.strip():
                current_clause.text += line + "\n"
                current_clause.end_line = line_num

        # Extract cross-references
        for clause in clauses:
            clause.referenced_clauses = self._extract_references(clause.text)

        return clauses

    def _extract_references(self, text: str) -> List[str]:
        """Extract clause references from text."""
        references = []

        # Find all clause references
        matches = self.reference_pattern.findall(text)
        for match in matches:
            # Convert to clause ID format
            ref_id = f"cl_{match.replace('.', '_').replace('(', '').replace(')', '')}"
            references.append(ref_id)

        return references

    def _extract_metadata(self, text: str) -> Dict:
        """Extract metadata from contract text."""
        metadata = {
            "effective_date": None,
            "parties": [],
            "document_type": "Contract",
            "language": "English",
        }

        # Look for effective date
        date_patterns = [
            r"[Ee]ffective\s+[Dd]ate[:\s]+([A-Za-z]+\s+\d+,?\s+\d{4})",
            r"[Dd]ate\s+of\s+[Tt]his\s+[Aa]greement[:\s]+([A-Za-z]+\s+\d+,?\s+\d{4})",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["effective_date"] = match.group(1)
                break

        # Look for parties
        party_pattern = (
            r"(?:between|entered into by and between)\s+([A-Z][A-Za-z\s]+)\s+(?:and|,)"
        )
        matches = re.findall(party_pattern, text)
        metadata["parties"] = [m.strip() for m in matches[:3]]  # Limit to 3

        return metadata

    def resolve_cross_references(self, clauses: List[Clause]) -> Dict[str, List[str]]:
        """Build clause dependency graph."""
        graph = {clause.clause_id: clause.referenced_clauses for clause in clauses}
        return graph

    def detect_circular_references(
        self, clauses: List[Clause]
    ) -> List[Tuple[str, str]]:
        """Detect circular clause references."""
        graph = self.resolve_cross_references(clauses)
        circular = []

        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    circular.append((node, neighbor))
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        for clause_id in graph:
            if clause_id not in visited:
                has_cycle(clause_id, visited, set())

        return circular

    def generate_clause_summary(self, clauses: List[Clause]) -> Dict[str, Dict]:
        """Generate summary index of all clauses."""
        summary = {}

        for clause in clauses:
            summary[clause.clause_id] = {
                "reference": clause.full_reference,
                "title": clause.title,
                "text_length": len(clause.text),
                "parent": clause.parent_clause_id,
                "children": clause.child_clauses,
                "references": clause.referenced_clauses,
                "confidence": clause.confidence,
                "start_line": clause.start_line,
                "end_line": clause.end_line,
            }

        return summary

    def extract_to_json(self, clauses: List[Clause]) -> str:
        """Export extracted clauses as JSON."""
        output = {"total_clauses": len(clauses), "clauses": []}

        for clause in clauses:
            output["clauses"].append(clause.to_dict())

        return json.dumps(output, indent=2, default=str)

    def resolve_coreferences(self, clause_text: str) -> Dict[str, str]:
        """Resolve pronoun coreferences in clause text."""
        coreferences = {}

        # Simple heuristic-based coreference resolution
        lines = clause_text.split("\n")
        last_noun_phrase = ""

        for line in lines:
            # Extract potential noun phrases (simplified)
            nouns = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", line)

            if nouns:
                last_noun_phrase = nouns[0]

            # Find pronouns and map to last noun
            pronouns = re.findall(
                r"\b(it|its|this|that|they|their)\b", line, re.IGNORECASE
            )
            for pronoun in pronouns:
                if last_noun_phrase:
                    coreferences[pronoun] = last_noun_phrase

        return coreferences
