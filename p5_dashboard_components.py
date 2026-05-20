"""
Reusable Streamlit Components - Widgets and layouts
Complete implementation: 180 lines
"""

from typing import Dict, List, Any, Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


class DashboardComponents:
    """Reusable dashboard components"""
    
    @staticmethod
    def metric_card(label: str, value: Any, delta: Optional[float] = None,
                   color: str = "#3498db", icon: str = "📊") -> None:
        """Display metric card"""
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"## {icon}")
        with col2:
            st.metric(label, value, delta=delta)
    
    @staticmethod
    def portfolio_overview(portfolio: Dict) -> None:
        """Display portfolio overview"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Number of Deals", portfolio.get("num_deals", 0))
        with col2:
            st.metric("Portfolio Value", f"${portfolio.get('total_value', 0)/1e9:.2f}B")
        with col3:
            dscr = portfolio.get("portfolio_dscr", 0)
            st.metric("Portfolio DSCR", f"{dscr:.2f}x")
        with col4:
            defaults = portfolio.get("default_count", 0)
            st.metric("Defaults", defaults, delta=None)
    
    @staticmethod
    def dscr_chart(deals_data: List[Dict]) -> None:
        """Display DSCR trends chart"""
        if not deals_data:
            st.warning("No deal data available")
            return
        
        df = pd.DataFrame(deals_data)
        
        fig = px.line(df, x="quarter", y="dscr", color="deal_name",
                     title="DSCR Trends by Deal",
                     labels={"quarter": "Quarter", "dscr": "DSCR (x)"})
        
        fig.add_hline(y=1.25, line_dash="dash", line_color="red",
                     annotation_text="Minimum DSCR")
        
        st.plotly_chart(fig, width='stretch')
    
    @staticmethod
    def sector_distribution(portfolio: Dict) -> None:
        """Display sector distribution pie chart"""
        sector_data = portfolio.get("sector_allocation", {})
        
        if not sector_data:
            st.info("No sector data available")
            return
        
        fig = go.Figure(data=[go.Pie(
            labels=list(sector_data.keys()),
            values=list(sector_data.values()),
            title="Sector Distribution"
        )])
        
        st.plotly_chart(fig, width='stretch')
    
    @staticmethod
    def risk_heatmap(portfolio_metrics: Dict) -> None:
        """Display risk metrics heatmap"""
        metrics = portfolio_metrics.get("metrics", {})
        
        if not metrics:
            st.info("No metrics available")
            return
        
        heatmap_data = {
            "DSCR": metrics.get("portfolio_dscr", 0),
            "Leverage": metrics.get("leverage", 0),
            "Default Rate": metrics.get("default_rate", 0),
            "Concentration": metrics.get("sector_hhi", 0),
        }
        
        # Normalize to 0-1 for color scale
        z_data = [list(heatmap_data.values())]
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=list(heatmap_data.keys()),
            colorscale="RdYlGn_r",
            text=z_data,
            texttemplate="%{text:.2f}",
        ))
        
        st.plotly_chart(fig, width='stretch')
    
    @staticmethod
    def ai_strategy_display(ai_summary: Dict) -> None:
        """Display AI opponent strategy"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### AI Strategy")
            st.write(f"**Risk Profile:** {ai_summary.get('risk_profile', 'N/A')}")
            st.write(f"**Max Leverage:** {ai_summary.get('max_leverage', 0):.1%}")
            st.write(f"**Decisions Made:** {ai_summary.get('decisions_made', 0)}")
        
        with col2:
            st.write("### DSCR Target")
            dscr_target = ai_summary.get('dscr_target', '1.25-2.5x')
            st.write(f"{dscr_target}")
    
    @staticmethod
    def leaderboard_display(leaderboard: List[Dict]) -> None:
        """Display leaderboard"""
        if not leaderboard:
            st.info("Leaderboard is empty")
            return
        
        df = pd.DataFrame(leaderboard)
        
        st.dataframe(
            df[["rank", "player_id", "score", "deals_managed"]],
            width='stretch',
            hide_index=True
        )
    
    @staticmethod
    def deal_details_table(deals: List[Dict]) -> None:
        """Display detailed deal table"""
        if not deals:
            st.info("No deals to display")
            return
        
        df = pd.DataFrame(deals)
        
        st.dataframe(df, width='stretch')
    
    @staticmethod
    def progress_bar(current: int, total: int, label: str = "Progress") -> None:
        """Display progress bar"""
        progress = min(1.0, current / total) if total > 0 else 0
        st.progress(progress)
        st.write(f"{label}: {current}/{total} ({progress*100:.1f}%)")
    
    @staticmethod
    def deal_card(deal: Dict) -> None:
        """Display individual deal card"""
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{deal.get('name', 'Unknown')}**")
                st.write(f"Sector: {deal.get('sector', 'N/A')}")
                st.write(f"Country: {deal.get('country', 'N/A')}")
            
            with col2:
                st.write(f"**Capex:** ${deal.get('capex', 0)/1e6:.0f}M")
                st.write(f"**Tenure:** {deal.get('tenor_years', 0)} years")
                st.write(f"**PD:** {deal.get('probability_of_default', 0):.2%}")
            
            with col3:
                dscr = deal.get('dscr', 0)
                st.write(f"**DSCR:** {dscr:.2f}x")
                status = deal.get('status', 'Unknown')
                st.write(f"**Status:** {status}")
                
                # Color code status
                if status == "Active":
                    st.write("🟢 Active")
                elif status == "Default":
                    st.write("🔴 Default")
                elif status == "Matured":
                    st.write("✅ Matured")
    
    @staticmethod
    def scenario_impact_display(scenario: Dict) -> None:
        """Display scenario impact details"""
        with st.container(border=True):
            st.write(f"### {scenario.get('scenario_type', 'Unknown')}")
            st.write(f"**Severity:** {scenario.get('severity', 0):.2f}")
            st.write(f"**Affected Deals:** {scenario.get('affected_deals', 0)}")
            
            impacts = scenario.get('impacts', {})
            if impacts:
                st.write("**Impacts:**")
                for impact_type, value in impacts.items():
                    st.write(f"- {impact_type}: {value}")
