# NLP Module for Contract Analysis - Full Implementation

from typing import Dict, List
import re

class ContractAnalyzer:
    def __init__(self):
        self.financial_terms = {
            'dscr': r'(?:DSCR|debt\s+service\s+coverage)\s*[:=]?\s*([0-9.]+)',
            'tenor': r'(?:tenor|maturity)\s*[:=]?\s*([0-9]+)\s*(?:years?|yrs)',
            'coupon': r'(?:coupon|rate)\s*[:=]?\s*([0-9.]+)%?',
            'debt': r'(?:debt|borrowing|loan)\s*[:=]?\s*\$?([0-9,.]+)',
            'leverage': r'(?:leverage|LTV|LDR)\s*[:=]?\s*([0-9.]+)%?'
        }
        self.risk_terms = {
            'cost_overrun': r'(?:cost\s+overrun|budget\s+overrun)',
            'schedule_delay': r'(?:schedule\s+delay|timeline\s+risk)',
            'demand_shortfall': r'(?:demand\s+shortfall|revenue\s+risk)',
            'refinancing_risk': r'(?:refinancing|refi|maturity\s+risk)',
            'force_majeure': r'(?:force\s+majeure|act\s+of\s+god)'
        }

    def extract_financial_terms(self, text: str) -> Dict:
        terms = {}
        for term, pattern in self.financial_terms.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    terms[term] = float(match.group(1).replace(',', ''))
                except (ValueError, AttributeError):
                    pass
        return terms

    def identify_risk_clauses(self, text: str) -> List[str]:
        risks = []
        for risk, pattern in self.risk_terms.items():
            if re.search(pattern, text, re.IGNORECASE):
                risks.append(risk)
        return risks

    def analyze_covenant_structure(self, text: str) -> Dict:
        # Identify covenant types
        covenants = {
            'financial_covenants': [
                'minimum_dscr',
                'maximum_leverage',
                'minimum_liquidity'
            ],
            'operational_covenants': [
                'capex_limitations',
                'asset_disposal_restrictions',
                'related_party_transaction_limits'
            ],
            'information_covenants': [
                'quarterly_reporting',
                'audit_requirements',
                'continuous_disclosure'
            ]
        }
        
        identified = {}
        for covenant_type, covenants_list in covenants.items():
            identified[covenant_type] = [c for c in covenants_list if c.lower() in text.lower()]
        
        return identified
