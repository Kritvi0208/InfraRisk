"""
Nested clause resolver module for Phase 4 NLP pipeline.
Resolves cross-references, builds dependency graphs, detects issues.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from contract_types import Clause, RiskCategory, SeverityLevel


@dataclass
class ClauseDependencyGraph:
    """Represents clause dependencies."""

    clauses: Dict[str, Clause] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)
    circular_refs: List[Tuple[str, str]] = field(default_factory=list)
    dead_links: List[str] = field(default_factory=list)
    depth_map: Dict[str, int] = field(default_factory=dict)


class ClauseResolver:
    """Resolves clause cross-references and dependencies."""

    def __init__(self):
        """Initialize resolver."""
        self.graph = ClauseDependencyGraph()
        self.resolution_cache = {}

    def build_dependency_graph(self, clauses: List[Clause]) -> ClauseDependencyGraph:
        """Build complete clause dependency graph."""
        self.graph.clauses = {c.clause_id: c for c in clauses}
        self.graph.edges = {}

        # Build edges from references
        for clause in clauses:
            self.graph.edges[clause.clause_id] = clause.referenced_clauses.copy()

            # Add parent-child edges
            if clause.parent_clause_id:
                if clause.parent_clause_id not in self.graph.edges:
                    self.graph.edges[clause.parent_clause_id] = []
                if clause.clause_id not in self.graph.edges[clause.parent_clause_id]:
                    self.graph.edges[clause.parent_clause_id].append(clause.clause_id)

        # Calculate depths
        self._calculate_depths()

        # Detect issues
        self.graph.circular_refs = self._detect_circular_references()
        self.graph.dead_links = self._detect_dead_links()

        return self.graph

    def _calculate_depths(self):
        """Calculate nesting depth for each clause."""
        self.graph.depth_map = {}

        def calculate_depth(clause_id: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()

            if clause_id in visited:
                return 0  # Prevent infinite recursion

            if clause_id in self.graph.depth_map:
                return self.graph.depth_map[clause_id]

            visited.add(clause_id)

            # Get parent depth
            clause = self.graph.clauses.get(clause_id)
            if clause and clause.parent_clause_id:
                parent_depth = calculate_depth(clause.parent_clause_id, visited)
                depth = parent_depth + 1
            else:
                depth = 1

            self.graph.depth_map[clause_id] = depth
            return depth

        for clause_id in self.graph.clauses:
            calculate_depth(clause_id)

    def _detect_circular_references(self) -> List[Tuple[str, str]]:
        """Detect circular clause references."""
        circular = []
        visited_global = set()

        def has_cycle(node: str, path: List[str], visited: Set[str]) -> bool:
            if node in visited:
                # Found cycle
                if node in path:
                    idx = path.index(node)
                    circular.append((path[idx], node))
                return True

            if node in visited_global:
                return False

            visited.add(node)
            path.append(node)

            for neighbor in self.graph.edges.get(node, []):
                if has_cycle(neighbor, path.copy(), visited):
                    return True

            visited_global.add(node)
            return False

        for clause_id in self.graph.clauses:
            if clause_id not in visited_global:
                has_cycle(clause_id, [], set())

        return circular

    def _detect_dead_links(self) -> List[str]:
        """Detect references to non-existent clauses."""
        dead_links = []

        for clause_id, references in self.graph.edges.items():
            for ref in references:
                if ref not in self.graph.clauses and ref not in self.graph.edges:
                    dead_links.append(f"{clause_id} -> {ref}")

        return dead_links

    def resolve_clause_reference(self, clause_id: str, max_depth: int = 10) -> Dict:
        """Resolve all direct and transitive references."""
        if clause_id in self.resolution_cache:
            return self.resolution_cache[clause_id]

        result = {
            "clause_id": clause_id,
            "direct_references": [],
            "transitive_references": [],
            "depth": self.graph.depth_map.get(clause_id, 1),
            "is_circular": False,
        }

        visited = set()
        queue = [(clause_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)

            if depth > max_depth or current_id in visited:
                continue

            visited.add(current_id)

            for ref in self.graph.edges.get(current_id, []):
                if depth == 0:
                    result["direct_references"].append(ref)
                else:
                    if ref not in result["transitive_references"]:
                        result["transitive_references"].append(ref)

                if ref in visited:
                    result["is_circular"] = True
                else:
                    queue.append((ref, depth + 1))

        self.resolution_cache[clause_id] = result
        return result

    def get_clause_summary(self) -> Dict[str, Dict]:
        """Generate comprehensive clause summary index."""
        summary = {}

        for clause_id, clause in self.graph.clauses.items():
            resolution = self.resolve_clause_reference(clause_id)

            summary[clause_id] = {
                "reference": clause.full_reference,
                "title": clause.title,
                "depth": self.graph.depth_map.get(clause_id, 1),
                "parent_id": clause.parent_clause_id,
                "child_count": len(clause.child_clauses),
                "direct_refs": len(resolution["direct_references"]),
                "transitive_refs": len(resolution["transitive_references"]),
                "is_circular": resolution["is_circular"],
                "has_dead_links": any(
                    ref in self.graph.dead_links
                    for ref in self.graph.edges.get(clause_id, [])
                ),
                "risk_category": clause.risk_category.value,
                "severity": clause.severity.value,
            }

        return summary

    def find_clause_chain(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """Find shortest path between two clauses."""
        if start_id not in self.graph.clauses or end_id not in self.graph.clauses:
            return None

        from collections import deque

        queue = deque([(start_id, [start_id])])
        visited = {start_id}

        while queue:
            current, path = queue.popleft()

            if current == end_id:
                return path

            for neighbor in self.graph.edges.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_related_clauses(self, clause_id: str, depth: int = 2) -> List[str]:
        """Get all related clauses within specified depth."""
        related = set()
        visited = set()
        queue = [(clause_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_depth > depth or current_id in visited:
                continue

            visited.add(current_id)

            if current_id != clause_id:
                related.add(current_id)

            # Add references
            for ref in self.graph.edges.get(current_id, []):
                if ref not in visited:
                    queue.append((ref, current_depth + 1))

            # Add parent and children
            clause = self.graph.clauses.get(current_id)
            if clause:
                if clause.parent_clause_id and clause.parent_clause_id not in visited:
                    queue.append((clause.parent_clause_id, current_depth + 1))

                for child_id in clause.child_clauses:
                    if child_id not in visited:
                        queue.append((child_id, current_depth + 1))

        return list(related)

    def export_graph_json(self) -> str:
        """Export dependency graph as JSON."""
        output = {
            "total_clauses": len(self.graph.clauses),
            "total_dependencies": sum(len(v) for v in self.graph.edges.values()),
            "circular_references": self.graph.circular_refs,
            "dead_links": self.graph.dead_links,
            "summary": self.get_clause_summary(),
        }

        return json.dumps(output, indent=2, default=str)

    def get_risk_propagation(self, clause_id: str) -> Dict[str, float]:
        """Calculate how risk propagates through references."""
        propagation = {}
        base_severity = self.graph.clauses.get(clause_id)

        if not base_severity:
            return propagation

        severity_map = {
            "Critical": 5.0,
            "High": 4.0,
            "Medium": 3.0,
            "Low": 2.0,
            "Minimal": 1.0,
        }
        base_score = severity_map.get(base_severity.severity.value, 3.0)

        # BFS through references, decaying risk
        visited = set()
        queue = [(clause_id, base_score, 0)]

        while queue:
            current_id, current_score, depth = queue.pop(0)

            if current_id in visited or depth > 5:
                continue

            visited.add(current_id)

            if current_id != clause_id:
                # Decay risk by depth
                decayed_score = current_score * (0.8**depth)
                propagation[current_id] = decayed_score

            for ref in self.graph.edges.get(current_id, []):
                if ref not in visited:
                    queue.append((ref, current_score, depth + 1))

        return propagation

    def generate_report(self) -> str:
        """Generate comprehensive dependency analysis report."""
        lines = ["=== CLAUSE DEPENDENCY ANALYSIS REPORT ===\n"]

        lines.append(f"Total Clauses: {len(self.graph.clauses)}")
        lines.append(
            f"Total Dependencies: {sum(len(v) for v in self.graph.edges.values())}"
        )
        lines.append(f"Circular References: {len(self.graph.circular_refs)}")
        lines.append(f"Dead Links: {len(self.graph.dead_links)}\n")

        if self.graph.circular_refs:
            lines.append("CIRCULAR REFERENCES:")
            for source, target in self.graph.circular_refs:
                lines.append(f"  {source} <-> {target}")
            lines.append("")

        if self.graph.dead_links:
            lines.append("DEAD LINKS:")
            for link in self.graph.dead_links[:10]:  # Show first 10
                lines.append(f"  {link}")
            if len(self.graph.dead_links) > 10:
                lines.append(f"  ... and {len(self.graph.dead_links) - 10} more")
            lines.append("")

        # Show highest-depth clauses
        sorted_by_depth = sorted(
            self.graph.depth_map.items(), key=lambda x: x[1], reverse=True
        )
        lines.append("DEEPEST CLAUSES (highest nesting):")
        for clause_id, depth in sorted_by_depth[:5]:
            clause = self.graph.clauses.get(clause_id)
            if clause:
                lines.append(f"  {clause.full_reference}: Depth {depth}")

        return "\n".join(lines)
