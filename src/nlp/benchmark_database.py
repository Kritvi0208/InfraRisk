"""Benchmark database of 1,000+ comparable transactions."""

from typing import Dict, List

class BenchmarkDatabase:
    """1,000+ comparable past transactions."""
    
    def __init__(self):
        self.transactions = self._mock_transactions()
    
    def _mock_transactions(self) -> List[Dict]:
        """Create mock benchmark database."""
        return [
            {
                'id': f'tx_{i:04d}',
                'sector': 'Transport' if i % 5 == 0 else 'Energy' if i % 5 == 1 else 'Water',
                'debt_amount': 100e6 * (1 + i % 10),
                'tenor_years': 15 + (i % 10),
                'pricing_bps': 250 + (i % 200),
                'dscr_required': 1.2 + (i % 5) * 0.1,
            }
            for i in range(1000)
        ]
    
    def find_comparables(self, project: Dict, count: int = 10) -> List[Dict]:
        """Find comparable transactions."""
        sector = project['sector']
        matches = [t for t in self.transactions if t['sector'] == sector][:count]
        return matches
