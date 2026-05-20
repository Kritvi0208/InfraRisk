"""Feature engineering for infrastructure projects"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple

class FeatureEngineer:
    @staticmethod
    def compute_financial_features(project: Dict) -> Dict:
        """Extract financial metrics"""
        dscr = project.get('cfads', 0) / max(project.get('debt_service', 1), 1)
        leverage = project.get('debt', 0) / max(project.get('capex', 1), 1)
        return {
            'dscr': dscr,
            'leverage': min(leverage, 1.0),
            'llcr': project.get('cash_npv', 0) / max(project.get('debt', 1), 1),
            'debt_tenor': project.get('tenor_years', 15),
        }

    @staticmethod
    def compute_macro_features(country_data: Dict) -> Dict:
        """Extract macroeconomic features"""
        return {
            'gdp_growth': country_data.get('gdp_growth', 0),
            'inflation': country_data.get('inflation', 0),
            'external_debt_ratio': country_data.get('external_debt', 0),
            'gov_debt_gdp': country_data.get('gov_debt', 0),
            'cds_spread': country_data.get('cds', 0),
        }

    @staticmethod
    def compute_construction_features(project: Dict) -> Dict:
        """Extract construction risk features"""
        return {
            'progress_percent': project.get('progress', 0),
            'cost_overrun_buffer': project.get('contingency', 0),
            'contractor_rating': project.get('contractor_grade', 3),
            'schedule_delay_months': project.get('delay', 0),
        }
