"""
Graph Neural Network Centrality Analyzer
Compute centrality metrics: betweenness, eigenvector, degree
Identify systemically important projects in portfolio
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class CentralityAnalyzer:
    """
    Analyze centrality in project portfolio network.
    Identifies systemically important projects based on network structure.
    """
    
    def __init__(self, adjacency_matrix: Optional[np.ndarray] = None, n_nodes: int = 20):
        """
        Initialize centrality analyzer.
        
        Args:
            adjacency_matrix: Graph adjacency matrix (n_nodes x n_nodes)
            n_nodes: Number of nodes if adjacency matrix not provided
        """
        if adjacency_matrix is not None:
            self.adjacency = adjacency_matrix
            self.n_nodes = adjacency_matrix.shape[0]
        else:
            # Create random network: 20% connection probability
            self.adjacency = (np.random.rand(n_nodes, n_nodes) > 0.8).astype(float)
            self.adjacency = (self.adjacency + self.adjacency.T) / 2  # Make symmetric
            np.fill_diagonal(self.adjacency, 0)  # No self-loops
            self.n_nodes = n_nodes
        
        self.node_labels = [f"Project_{i}" for i in range(self.n_nodes)]
        
        # Centrality measures
        self.degree_centrality: Optional[np.ndarray] = None
        self.betweenness_centrality: Optional[np.ndarray] = None
        self.eigenvector_centrality: Optional[np.ndarray] = None
        self.closeness_centrality: Optional[np.ndarray] = None
    
    def compute_degree_centrality(self) -> np.ndarray:
        """
        Compute degree centrality: normalized node degree.
        
        Returns:
            Degree centrality for each node
        """
        # Degree = sum of connections
        degrees = np.sum(self.adjacency, axis=1)
        
        # Normalize by max possible degree
        if self.n_nodes > 1:
            degree_centrality = degrees / (self.n_nodes - 1)
        else:
            degree_centrality = degrees
        
        self.degree_centrality = degree_centrality
        return degree_centrality
    
    def compute_betweenness_centrality(self) -> np.ndarray:
        """
        Compute betweenness centrality: proportion of shortest paths through each node.
        Uses approximate algorithm via random sampling for efficiency.
        
        Returns:
            Betweenness centrality for each node
        """
        betweenness = np.zeros(self.n_nodes)
        
        # Approximate: sample random source-target pairs
        n_samples = min(self.n_nodes * 10, 100)
        
        for _ in range(n_samples):
            # Random source and target
            source = np.random.randint(0, self.n_nodes)
            target = np.random.randint(0, self.n_nodes)
            
            if source == target:
                continue
            
            # Find shortest path (BFS)
            path = self._find_shortest_path(source, target)
            
            # Add to betweenness for intermediate nodes
            for node in path[1:-1]:
                betweenness[node] += 1
        
        # Normalize
        if n_samples > 0:
            betweenness /= n_samples
        
        self.betweenness_centrality = betweenness
        return betweenness
    
    def _find_shortest_path(self, source: int, target: int) -> List[int]:
        """
        Find shortest path using breadth-first search.
        
        Args:
            source: Source node
            target: Target node
            
        Returns:
            List of nodes in shortest path
        """
        from collections import deque
        
        visited = set([source])
        queue = deque([(source, [source])])
        
        while queue:
            node, path = queue.popleft()
            
            if node == target:
                return path
            
            # Explore neighbors
            neighbors = np.where(self.adjacency[node] > 0)[0]
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return [source, target]  # Direct if no path found
    
    def compute_eigenvector_centrality(self, max_iter: int = 100, tol: float = 1e-6) -> np.ndarray:
        """
        Compute eigenvector centrality: leading eigenvector of adjacency matrix.
        Uses power iteration method.
        
        Args:
            max_iter: Maximum iterations
            tol: Convergence tolerance
            
        Returns:
            Eigenvector centrality for each node
        """
        # Initialize random vector
        x = np.random.rand(self.n_nodes)
        x = x / np.linalg.norm(x)
        
        # Power iteration
        for _ in range(max_iter):
            x_new = self.adjacency @ x
            x_new = x_new / (np.linalg.norm(x_new) + 1e-8)
            
            if np.linalg.norm(x_new - x) < tol:
                break
            
            x = x_new
        
        # Normalize to [0, 1]
        eigenvector_centrality = np.abs(x) / (np.max(np.abs(x)) + 1e-8)
        
        self.eigenvector_centrality = eigenvector_centrality
        return eigenvector_centrality
    
    def compute_closeness_centrality(self) -> np.ndarray:
        """
        Compute closeness centrality: reciprocal of average distance to all other nodes.
        
        Returns:
            Closeness centrality for each node
        """
        closeness = np.zeros(self.n_nodes)
        
        # For each node, compute average distance
        for source in range(self.n_nodes):
            distances = np.full(self.n_nodes, np.inf)
            distances[source] = 0
            
            # BFS to find all distances
            queue = [source]
            while queue:
                node = queue.pop(0)
                neighbors = np.where(self.adjacency[node] > 0)[0]
                
                for neighbor in neighbors:
                    if distances[neighbor] == np.inf:
                        distances[neighbor] = distances[node] + 1
                        queue.append(neighbor)
            
            # Closeness = 1 / mean distance (exclude self)
            valid_distances = distances[distances != np.inf]
            if len(valid_distances) > 0:
                closeness[source] = (self.n_nodes - 1) / np.sum(valid_distances)
        
        self.closeness_centrality = closeness
        return closeness
    
    def identify_systemic_projects(self, top_k: int = 5) -> Dict:
        """
        Identify systemically important projects (high centrality).
        
        Args:
            top_k: Number of top projects to return
            
        Returns:
            Dictionary with systemic project rankings
        """
        # Compute all centrality measures
        degree = self.compute_degree_centrality()
        betweenness = self.compute_betweenness_centrality()
        eigenvector = self.compute_eigenvector_centrality()
        closeness = self.compute_closeness_centrality()
        
        # Combined systemic importance score (average of normalized centralities)
        systemic_score = (
            (degree / (np.max(degree) + 1e-8)) +
            (betweenness / (np.max(betweenness) + 1e-8)) +
            (eigenvector / (np.max(eigenvector) + 1e-8)) +
            (closeness / (np.max(closeness) + 1e-8))
        ) / 4
        
        # Rank nodes
        top_indices = np.argsort(systemic_score)[::-1][:top_k]
        
        systemic_projects = []
        for rank, idx in enumerate(top_indices, 1):
            systemic_projects.append({
                'rank': rank,
                'project': self.node_labels[idx],
                'systemic_score': float(systemic_score[idx]),
                'degree': float(degree[idx]),
                'betweenness': float(betweenness[idx]),
                'eigenvector': float(eigenvector[idx]),
                'closeness': float(closeness[idx]),
            })
        
        return {
            'systemic_projects': systemic_projects,
            'interpretation': 'Projects with high systemic importance can trigger cascading defaults',
        }
    
    def analyze_portfolio_concentration(self) -> Dict:
        """
        Analyze portfolio concentration in terms of systemic risk.
        
        Returns:
            Concentration metrics
        """
        degree = self.compute_degree_centrality()
        
        # Herfindahl index (concentration)
        herfindahl = np.sum(degree**2)
        
        # Normalized to [0, 1]
        herfindahl_norm = (herfindahl - 1/self.n_nodes) / (1 - 1/self.n_nodes)
        
        # Gini coefficient
        sorted_degree = np.sort(degree)
        gini = 2 * np.sum((np.arange(1, self.n_nodes + 1) - (self.n_nodes + 1) / 2) * sorted_degree) / (self.n_nodes * np.sum(sorted_degree))
        
        return {
            'herfindahl_index': float(herfindahl),
            'herfindahl_normalized': float(herfindahl_norm),
            'gini_coefficient': float(gini),
            'interpretation': 'High values indicate concentration risk (few dominant nodes)',
        }
    
    def compute_distance_matrix(self) -> np.ndarray:
        """
        Compute shortest path distance between all node pairs.
        
        Returns:
            Distance matrix
        """
        distances = np.full((self.n_nodes, self.n_nodes), np.inf)
        np.fill_diagonal(distances, 0)
        
        # Initialize with direct edges
        distances[self.adjacency > 0] = 1
        
        # Floyd-Warshall
        for k in range(self.n_nodes):
            for i in range(self.n_nodes):
                for j in range(self.n_nodes):
                    distances[i, j] = min(distances[i, j], distances[i, k] + distances[k, j])
        
        return distances
    
    def contagion_risk(self, source_node: int, impact_threshold: float = 0.5) -> Dict:
        """
        Analyze contagion risk from a specific node failure.
        
        Args:
            source_node: Node that fails
            impact_threshold: Minimum impact to propagate
            
        Returns:
            Contagion analysis
        """
        # Start with source node failure
        failed = np.zeros(self.n_nodes)
        failed[source_node] = 1
        
        # Propagate impact based on adjacency
        for _ in range(3):  # 3 rounds of contagion
            new_failures = np.zeros(self.n_nodes)
            for i in range(self.n_nodes):
                if failed[i] == 0:
                    # Probability of failure from neighbors
                    neighbor_impact = np.sum(self.adjacency[i, :] * failed)
                    if neighbor_impact > impact_threshold:
                        new_failures[i] = 1
            
            failed = np.maximum(failed, new_failures)
        
        n_failed = np.sum(failed)
        contagion_ratio = n_failed / self.n_nodes
        
        return {
            'source_node': self.node_labels[source_node],
            'initial_impact': float(self.eigenvector_centrality[source_node]) if self.eigenvector_centrality is not None else 0.0,
            'nodes_affected': int(n_failed),
            'contagion_ratio': float(contagion_ratio),
            'risk_level': 'HIGH' if contagion_ratio > 0.3 else 'MEDIUM' if contagion_ratio > 0.1 else 'LOW',
        }


def main():
    """Example usage"""
    analyzer = CentralityAnalyzer(n_nodes=20)
    
    # Compute centralities
    degree = analyzer.compute_degree_centrality()
    print(f"Degree centrality range: [{degree.min():.3f}, {degree.max():.3f}]")
    
    betweenness = analyzer.compute_betweenness_centrality()
    print(f"Betweenness centrality range: [{betweenness.min():.3f}, {betweenness.max():.3f}]")
    
    eigenvector = analyzer.compute_eigenvector_centrality()
    print(f"Eigenvector centrality range: [{eigenvector.min():.3f}, {eigenvector.max():.3f}]")
    
    # Systemic projects
    systemic = analyzer.identify_systemic_projects(top_k=5)
    print(f"\nTop 5 systemic projects:")
    for proj in systemic['systemic_projects']:
        print(f"  {proj['rank']}. {proj['project']}: {proj['systemic_score']:.3f}")
    
    # Concentration
    concentration = analyzer.analyze_portfolio_concentration()
    print(f"\nPortfolio concentration:")
    print(f"  Herfindahl: {concentration['herfindahl_normalized']:.3f}")
    print(f"  Gini: {concentration['gini_coefficient']:.3f}")
    
    # Contagion
    contagion = analyzer.contagion_risk(source_node=0)
    print(f"\nContagion from {contagion['source_node']}: {contagion['risk_level']}")


if __name__ == '__main__':
    main()
