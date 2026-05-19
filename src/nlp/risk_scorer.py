"""Automated contract risk scoring (1-5 severity scale)."""

from typing import Dict, List

class ContractRiskScorer:
    """Score contract clauses on 1-5 severity."""
    
    def score_clause(self, clause: Dict) -> int:
        """Score clause: 1=minimal, 5=critical."""
        # Mock scoring logic
        if clause['category'] in ['FORCE_MAJEURE', 'MISCELLANEOUS']:
            return 1
        elif clause['category'] in ['TERMINATION', 'EVENT_OF_DEFAULT']:
            return 4
        else:
            return 2
    
    def score_contract(self, clauses: List[Dict]) -> Dict:
        """Aggregate clause scores."""
        scores = [self.score_clause(c) for c in clauses]
        return {
            'avg_severity': sum(scores) / len(scores),
            'max_severity': max(scores),
            'high_risk_count': sum(1 for s in scores if s >= 4),
            'overall_risk': 'MEDIUM' if sum(scores) / len(scores) > 2.5 else 'LOW'
        }
