"""Streamlit dashboard for InfraRisk Lab."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.simulation.game_engine import GameState

def render_dashboard():
    """Main dashboard."""
    st.set_page_config(page_title="InfraRisk Lab", layout="wide")
    st.title("🌟 InfraRisk Lab")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Portfolio", "Dashboard", "Satellite View", "Leaderboard"]
    )
    
    with tab1:
        st.subheader("Your Portfolio")
        portfolio_data = {
            'Deal ID': ['deal_001', 'deal_002', 'deal_003'],
            'Sector': ['Transport', 'Energy', 'Water'],
            'DSCR': [1.5, 1.2, 1.8],
            'PD (%)': [2.3, 5.1, 1.8],
            'Status': ['Operational', 'Construction', 'Development'],
        }
        st.dataframe(pd.DataFrame(portfolio_data))
    
    with tab2:
        st.subheader("Real-time Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Portfolio Value", "$1.2B", "+5.2%")
        col2.metric("Avg DSCR", "1.52", "+0.12")
        col3.metric("Portfolio PD", "3.4%", "-0.8%")
    
    with tab3:
        st.subheader("Satellite Imagery Viewer")
        st.info("NDVI, NDBI construction progress tracking for 50+ sites")
    
    with tab4:
        st.subheader("Leaderboard")
        leaderboard = pd.DataFrame({
            'Rank': [1, 2, 3],
            'Player': ['AlexAI', 'You', 'CobraAI'],
            'Score': [892, 765, 634],
        })
        st.dataframe(leaderboard)

if __name__ == "__main__":
    render_dashboard()
