# Scoring System - Full Implementation

from typing import Dict
import numpy as np

class ScoringSystem:
    def __init__(self):
        self.max_score = 1000
        self.weights = {
            'credit_risk': 0.30,
            'financial_structure': 0.20,
            'diversification': 0.15,
            'crisis_response': 0.15,
            'market_timing': 0.10,
            'esg': 0.10
        }

    def calculate_score(self, metrics: Dict) -> Dict:
        scores = {}
        
        # Credit Risk Management (0-300)
        pd_accuracy = max(0, 1 - abs(metrics.get('actual_pd', 0) - metrics.get('predicted_pd', 0)))
        covenant_breaches = max(0, 1 - metrics.get('breaches', 0) * 0.05)
        scores['credit_risk'] = (pd_accuracy * 0.6 + covenant_breaches * 0.4) * 300
        
        # Financial Structuring (0-200)
        dscr_efficiency = min(1, metrics.get('dscr', 1) / 1.4)
        leverage_optimization = min(1, (1 - metrics.get('leverage', 0.7) / 0.8))
        scores['financial_structure'] = (dscr_efficiency * 0.6 + leverage_optimization * 0.4) * 200
        
        # Portfolio Diversification (0-150)
        sector_hhi = metrics.get('sector_hhi', 0.3)
        country_hhi = metrics.get('country_hhi', 0.2)
        scores['diversification'] = ((1 - sector_hhi) * 0.6 + (1 - country_hhi) * 0.4) * 150
        
        # Crisis Response (0-150)
        restructure_success = metrics.get('restructure_success_rate', 0.8)
        recovery_rate = metrics.get('recovery_rate', 0.65)
        scores['crisis_response'] = (restructure_success * 0.6 + recovery_rate * 0.4) * 150
        
        # Market Timing (0-100)
        refi_savings = min(1, metrics.get('refi_savings_bps', 0) / 200)
        hedge_effectiveness = metrics.get('hedge_effectiveness', 0.7)
        scores['market_timing'] = (refi_savings * 0.5 + hedge_effectiveness * 0.5) * 100
        
        # ESG Integration (0-100)
        esg_score = metrics.get('esg_score', 0.6)
        scores['esg'] = esg_score * 100
        
        total_score = sum(scores.values())
        
        return {
            'total': total_score,
            'breakdown': scores,
            'rating': self.get_rating(total_score)
        }

    def get_rating(self, score: float) -> str:
        if score >= 850:
            return "Expert (Platinum)"
        elif score >= 750:
            return "Senior Analyst (Gold)"
        elif score >= 650:
            return "Associate (Silver)"
        elif score >= 500:
            return "Analyst (Bronze)"
        else:
            return "Novice"
