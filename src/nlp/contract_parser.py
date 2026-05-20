"""NLP for contract intelligence"""
from typing import Dict, List

class ContractParser:
    def __init__(self):
        self.risk_keywords = {
            'force_majeure': ['force majeure', 'acts of god', 'unforeseeable'],
            'termination': ['termination', 'early termination', 'step-in'],
            'covenant': ['dscr', 'leverage', 'debt service'],
            'payment': ['payment obligation', 'tariff', 'compensation'],
        }

    def extract_clauses(self, text: str) -> Dict[str, List[str]]:
        """Extract risk clauses from contract text"""
        clauses = {k: [] for k in self.risk_keywords.keys()}
        
        text_lower = text.lower()
        for category, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    clauses[category].append(keyword)
        
        return clauses

    def score_risk(self, clauses: Dict[str, List[str]]) -> float:
        """Score overall contract risk 0-1"""
        total_findings = sum(len(v) for v in clauses.values())
        return min(total_findings * 0.1, 1.0)
