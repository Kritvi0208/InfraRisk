"""Portfolio Contagion Index.

Measures systemic risk from project dependencies.
"""

import numpy as np
import pandas as pd
from typing import Dict, List

class PortfolioContagionIndex:
    """Systemic risk from project dependency graph."""
    
    def __init__(self, projects: List[Dict]):
        """Initialize with project dependency graph."""
        self.projects = projects
        self.dependency_matrix = self._build_dependency_matrix()
    
    def _build_dependency_matrix(self) -> np.ndarray:
        """Build adjacency matrix of dependencies."""
        n = len(self.projects)
        matrix = np.zeros((n, n))
        for i, proj in enumerate(self.projects):
            for dep_idx in proj.get('depends_on', []):
                matrix[i, dep_idx] = 1
        return matrix
    
    def calculate_contagion(self) -> Dict:
        """Calculate contagion spread."""
        # Eigenvalue of dependency matrix = systemic importance
        eigenvalues = np.linalg.eigvalsh(self.dependency_matrix)
        spectral_radius = np.max(eigenvalues)
        
        # Contagion spread rate
        contagion_index = spectral_radius / len(self.projects)
        
        return {
            'contagion_index': contagion_index,
            'systemic_risk_level': 'High' if contagion_index > 0.5 else 'Medium' if contagion_index > 0.2 else 'Low',
            'spectral_radius': spectral_radius,
        }
