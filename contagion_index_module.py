"""
Portfolio Contagion Index Module

Implements systemic risk assessment through project dependency graphs and
eigenvector centrality-based risk propagation analysis.

Example usage:
    >>> contagion = PortfolioContagionIndex(projects=10)
    >>> contagion.add_dependency("proj_1", "proj_2", correlation=0.65)
    >>> risk_scores = contagion.calculate_contagion_index()
    >>> print(risk_scores[['project_id', 'contagion_score']])
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd


@dataclass
class ProjectNode:
    """Represents a project in the dependency graph"""

    project_id: str
    sector: str  # transportation, energy, water, social
    country: str
    baseline_risk: float  # 0-1, risk score
    exposure: float  # Financial exposure in USD millions
    recovery_rate: float = 0.5  # Loss recovery capacity
    correlation_dependencies: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContagionMetrics:
    """Contagion risk metrics for a project"""

    project_id: str
    eigenvector_centrality: float
    in_degree_centrality: float
    out_degree_centrality: float
    betweenness_centrality: float
    contagion_score: float
    shock_amplification: float
    systemic_importance: float


class PortfolioContagionIndex:
    """
    Calculates portfolio-level systemic risk through network analysis.

    Uses adjacency matrix representation of project dependencies and
    eigenvector centrality to measure risk propagation potential.
    """

    def __init__(self, projects: int = 50, num_sectors: int = 4):
        """
        Initialize contagion index calculator.

        Args:
            projects: Number of projects in portfolio
            num_sectors: Number of infrastructure sectors
        """
        self.projects = projects
        self.num_sectors = num_sectors
        self.project_nodes: Dict[str, ProjectNode] = {}
        self.adjacency_matrix = np.zeros((projects, projects))
        self.project_id_to_idx = {}
        self.idx_to_project_id = {}
        self._initialize_mock_portfolio()

    def _initialize_mock_portfolio(self) -> None:
        """Create mock portfolio with realistic correlations"""
        sectors = ["transportation", "energy", "water", "social"]
        countries = ["Country_A", "Country_B", "Country_C", "Country_D"]

        idx = 0
        for i in range(self.projects):
            sector = sectors[i % self.num_sectors]
            country = countries[i % len(countries)]
            project_id = f"proj_{i:03d}"

            self.project_nodes[project_id] = ProjectNode(
                project_id=project_id,
                sector=sector,
                country=country,
                baseline_risk=np.random.uniform(0.1, 0.6),
                exposure=np.random.uniform(10, 500),  # Million USD
                recovery_rate=np.random.uniform(0.3, 0.8),
            )

            self.project_id_to_idx[project_id] = idx
            self.idx_to_project_id[idx] = project_id
            idx += 1

        # Generate sector-based correlations
        self._generate_sector_correlations()

    def _generate_sector_correlations(self) -> None:
        """Add realistic within-sector and cross-sector correlations"""
        sectors_dict = defaultdict(list)

        for proj_id, node in self.project_nodes.items():
            sectors_dict[node.sector].append(proj_id)

        # Strong correlations within sectors
        for sector_projects in sectors_dict.values():
            for i, proj1 in enumerate(sector_projects):
                for proj2 in sector_projects[i + 1 :]:
                    correlation = np.random.uniform(0.4, 0.8)
                    self.add_dependency(proj1, proj2, correlation)
                    self.add_dependency(proj2, proj1, correlation)

        # Weaker cross-country/sector correlations
        country_dict = defaultdict(list)
        for proj_id, node in self.project_nodes.items():
            country_dict[node.country].append(proj_id)

        for country_projects in country_dict.values():
            for proj1 in country_projects:
                for proj2 in country_projects:
                    if proj1 != proj2:
                        existing_corr = self.adjacency_matrix[
                            self.project_id_to_idx[proj1],
                            self.project_id_to_idx[proj2],
                        ]
                        if existing_corr == 0:
                            correlation = np.random.uniform(0.1, 0.4)
                            self.add_dependency(proj1, proj2, correlation)

    def add_dependency(
        self, source_proj: str, target_proj: str, correlation: float
    ) -> None:
        """
        Add dependency edge between two projects.

        Args:
            source_proj: Source project ID
            target_proj: Target project ID
            correlation: Correlation strength 0-1
        """
        if (
            source_proj in self.project_id_to_idx
            and target_proj in self.project_id_to_idx
        ):
            source_idx = self.project_id_to_idx[source_proj]
            target_idx = self.project_id_to_idx[target_proj]
            self.adjacency_matrix[source_idx, target_idx] = correlation
            self.project_nodes[source_proj].correlation_dependencies[
                target_proj
            ] = correlation

    def _calculate_eigenvector_centrality(self) -> Dict[str, float]:
        """
        Calculate eigenvector centrality for each project.

        Higher centrality = project is in more important positions
        """
        try:
            eigenvalues, eigenvectors = np.linalg.eig(self.adjacency_matrix)
            max_eigenvalue_idx = np.argmax(eigenvalues.real)
            eigenvector = np.abs(eigenvectors[:, max_eigenvalue_idx].real)
            eigenvector = eigenvector / np.sum(eigenvector)

            centrality_dict = {}
            for idx, project_id in self.idx_to_project_id.items():
                centrality_dict[project_id] = eigenvector[idx]

            return centrality_dict
        except Exception as e:
            print(f"Eigenvalue calculation warning: {e}")
            return {proj_id: 0.5 for proj_id in self.project_nodes.keys()}

    def _calculate_degree_centrality(
        self,
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Calculate in-degree and out-degree centrality"""
        in_degree = {}
        out_degree = {}

        for project_id in self.project_nodes.keys():
            idx = self.project_id_to_idx[project_id]
            out_degree[project_id] = np.sum(self.adjacency_matrix[idx, :])
            in_degree[project_id] = np.sum(self.adjacency_matrix[:, idx])

        max_out = max(out_degree.values()) if out_degree else 1
        max_in = max(in_degree.values()) if in_degree else 1

        out_degree = {k: v / max_out for k, v in out_degree.items()}
        in_degree = {k: v / max_in for k, v in in_degree.items()}

        return in_degree, out_degree

    def _calculate_betweenness_centrality(self) -> Dict[str, float]:
        """
        Approximate betweenness centrality.

        Projects with high betweenness are critical for shock transmission.
        """
        betweenness = {proj_id: 0.0 for proj_id in self.project_nodes.keys()}

        project_list = list(self.project_nodes.keys())
        n_projects = len(project_list)

        for i, proj_i in enumerate(project_list):
            idx_i = self.project_id_to_idx[proj_i]
            for j, proj_j in enumerate(project_list):
                if i != j:
                    idx_j = self.project_id_to_idx[proj_j]
                    # Path length proxy: 1 / correlation
                    corr = self.adjacency_matrix[idx_i, idx_j]
                    if corr > 0:
                        path_weight = 1.0 / (corr + 0.1)
                        for k, proj_k in enumerate(project_list):
                            if k != i and k != j:
                                idx_k = self.project_id_to_idx[proj_k]
                                # Check if k lies on shortest path i->j
                                if (
                                    self.adjacency_matrix[idx_i, idx_k] > 0
                                    and self.adjacency_matrix[idx_k, idx_j] > 0
                                ):
                                    betweenness[proj_k] += 1.0 / (
                                        n_projects * n_projects
                                    )

        return betweenness

    def calculate_contagion_index(self) -> pd.DataFrame:
        """
        Calculate comprehensive contagion metrics.

        Returns:
            DataFrame with contagion scores for all projects
        """
        eigenvector = self._calculate_eigenvector_centrality()
        in_degree, out_degree = self._calculate_degree_centrality()
        betweenness = self._calculate_betweenness_centrality()

        results = []

        for project_id, node in self.project_nodes.items():
            eig_centrality = eigenvector.get(project_id, 0.5)
            in_cent = in_degree.get(project_id, 0.0)
            out_cent = out_degree.get(project_id, 0.0)
            between_cent = betweenness.get(project_id, 0.0)

            shock_amplification = (
                eig_centrality * 0.4
                + (in_cent + out_cent) / 2 * 0.3
                + between_cent * 0.3
            )

            contagion_score = node.baseline_risk * 0.5 + shock_amplification * 0.5

            systemic_importance = eig_centrality * (
                node.exposure / 1000
            )  # Exposure-weighted

            results.append(
                {
                    "project_id": project_id,
                    "sector": node.sector,
                    "country": node.country,
                    "baseline_risk": node.baseline_risk,
                    "exposure_millions": node.exposure,
                    "eigenvector_centrality": eig_centrality,
                    "in_degree_centrality": in_cent,
                    "out_degree_centrality": out_cent,
                    "betweenness_centrality": between_cent,
                    "shock_amplification": shock_amplification,
                    "contagion_score": contagion_score,
                    "systemic_importance": systemic_importance,
                    "num_dependencies": len(node.correlation_dependencies),
                }
            )

        df = pd.DataFrame(results)
        df = df.sort_values("contagion_score", ascending=False)

        return df

    def identify_systemic_risks(self, threshold: float = 0.65) -> Dict[str, List]:
        """
        Identify projects with systemic importance above threshold.

        Args:
            threshold: Contagion score threshold

        Returns:
            Dictionary grouping high-risk projects by sector
        """
        contagion_df = self.calculate_contagion_index()
        systemic_projects = contagion_df[contagion_df["contagion_score"] >= threshold]

        by_sector = defaultdict(list)
        for _, row in systemic_projects.iterrows():
            by_sector[row["sector"]].append(
                {
                    "project_id": row["project_id"],
                    "contagion_score": row["contagion_score"],
                    "exposure": row["exposure_millions"],
                }
            )

        return dict(by_sector)

    def shock_propagation_analysis(
        self, shocked_project: str, shock_magnitude: float = 0.5
    ) -> pd.DataFrame:
        """
        Simulate shock propagation from a single project failure.

        Args:
            shocked_project: Project ID experiencing shock
            shock_magnitude: Magnitude of shock (0-1)

        Returns:
            DataFrame showing impact on all connected projects
        """
        shock_impacts = {proj_id: 0.0 for proj_id in self.project_nodes.keys()}
        shock_impacts[shocked_project] = shock_magnitude

        for iteration in range(3):  # 3 rounds of propagation
            new_impacts = shock_impacts.copy()
            for proj_id, current_impact in shock_impacts.items():
                if current_impact > 0.01:
                    neighbors = self.project_nodes[proj_id].correlation_dependencies
                    for neighbor_id, correlation in neighbors.items():
                        propagated_shock = current_impact * correlation
                        new_impacts[neighbor_id] = max(
                            new_impacts[neighbor_id], propagated_shock
                        )
            shock_impacts = new_impacts

        impacts_df = pd.DataFrame(
            [
                {
                    "project_id": proj_id,
                    "shock_impact": impact,
                    "impacted": impact > 0.05,
                }
                for proj_id, impact in shock_impacts.items()
            ]
        )

        return impacts_df.sort_values("shock_impact", ascending=False)

    def export_dependency_graph(self) -> Dict:
        """Export dependency graph for visualization"""
        nodes = []
        edges = []

        for proj_id, node in self.project_nodes.items():
            nodes.append(
                {
                    "id": proj_id,
                    "sector": node.sector,
                    "country": node.country,
                    "exposure": node.exposure,
                    "baseline_risk": node.baseline_risk,
                }
            )

        for source_id, correlations in [
            (proj_id, node.correlation_dependencies)
            for proj_id, node in self.project_nodes.items()
        ]:
            for target_id, correlation in correlations.items():
                edges.append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "weight": correlation,
                    }
                )

        return {"nodes": nodes, "edges": edges}

    def export_adjacency_matrix(self) -> np.ndarray:
        """Export adjacency matrix for external analysis"""
        return self.adjacency_matrix.copy()


def create_contagion_index(num_projects: int = 50) -> PortfolioContagionIndex:
    """Factory function"""
    return PortfolioContagionIndex(projects=num_projects)
