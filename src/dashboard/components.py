# Dashboard Components - Reusable UI pieces

from typing import Dict, List
import json

class DashboardComponentBuilder:
    @staticmethod
    def build_scorecard(title: str, value: float, metric: str, color: str = "blue"):
        return {
            "type": "metric",
            "title": title,
            "value": value,
            "metric": metric,
            "color": color
        }

    @staticmethod
    def build_chart(chart_type: str, data: List[Dict], title: str):
        return {
            "type": chart_type,
            "data": data,
            "title": title,
            "options": {"responsive": True, "legend": {"position": "bottom"}}
        }

    @staticmethod
    def build_table(columns: List[str], rows: List[List], title: str):
        return {
            "type": "table",
            "title": title,
            "columns": columns,
            "rows": rows
        }

    @staticmethod
    def build_portfolio_summary(portfolio_metrics: Dict):
        return {
            "type": "portfolio_summary",
            "metrics": {
                "total_projects": portfolio_metrics.get('num_projects', 0),
                "total_debt": portfolio_metrics.get('total_debt', 0),
                "portfolio_dscr": portfolio_metrics.get('portfolio_dscr', 0),
                "total_ebitda": portfolio_metrics.get('total_ebitda', 0),
                "default_probability": portfolio_metrics.get('portfolio_pd', 0),
                "concentration": portfolio_metrics.get('hhi', 0)
            }
        }

    @staticmethod
    def build_risk_heatmap(deals: List[Dict]):
        return {
            "type": "heatmap",
            "title": "Portfolio Risk Heatmap",
            "dimensions": ["Sector", "Country", "Risk Level"],
            "data": deals
        }

    @staticmethod
    def build_scenario_analysis(scenario_results: Dict):
        return {
            "type": "scenario_chart",
            "title": "Portfolio Value Under Different Scenarios",
            "scenarios": scenario_results
        }
