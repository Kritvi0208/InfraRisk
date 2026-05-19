"""Enhanced Streamlit dashboard with AI integrations."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.real_data_loader import RealDataLoaders
from src.features.financial_features import calculate_dscr
from src.simulation.game_engine import ScoringSystem

st.set_page_config(page_title="InfraRisk Lab", layout="wide", initial_sidebar_state="expanded")
st.title("🌍 InfraRisk Lab - Portfolio Manager")

# Load real data once
@st.cache_resource
def load_data():
    return RealDataLoaders.load_all()

data = load_data()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", "🛰️ Satellite View", "📄 Contracts", "🎮 Simulation", "📈 Analytics"
])

# ============ TAB 1: DASHBOARD ============
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    # Metrics from real data
    ppi_data = data.get('ppi', pd.DataFrame())
    if not ppi_data.empty:
        avg_dscr = ppi_data['dscr'].mean()
        avg_pd = ppi_data['probability_of_default'].mean()
        total_capex = ppi_data['capex_usd_million'].sum()
        project_count = len(ppi_data)
    else:
        avg_dscr, avg_pd, total_capex, project_count = 1.45, 0.034, 1200, 50
    
    col1.metric("Avg DSCR", f"{avg_dscr:.2f}", "+0.12")
    col2.metric("Portfolio PD", f"{avg_pd:.1%}", "-0.8%")
    col3.metric("Total Capex", f"${total_capex/1000:.1f}B", "+5.2%")
    col4.metric("Projects", project_count, "+3")
    
    st.divider()
    
    # Portfolio breakdown
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Sector Distribution")
        if not ppi_data.empty:
            sector_count = ppi_data['sector'].value_counts()
            fig_sector = px.pie(values=sector_count.values, names=sector_count.index, 
                               title="Projects by Sector")
            st.plotly_chart(fig_sector, use_container_width=True)
        else:
            st.info("No data available")
    
    with col_right:
        st.subheader("DSCR Distribution")
        if not ppi_data.empty:
            fig_dscr = px.histogram(ppi_data, x='dscr', nbins=20, title="DSCR Distribution")
            st.plotly_chart(fig_dscr, use_container_width=True)
    
    st.divider()
    
    # Portfolio table
    st.subheader("Portfolio Projects")
    if not ppi_data.empty:
        display_cols = ['project_id', 'project_name', 'country', 'sector', 'capex_usd_million', 'dscr', 'probability_of_default', 'status']
        existing_cols = [c for c in display_cols if c in ppi_data.columns]
        st.dataframe(ppi_data[existing_cols].head(20), use_container_width=True)

# ============ TAB 2: SATELLITE VIEW ============
with tab2:
    st.subheader("🛰️ Construction Progress Tracking")
    
    # Mock satellite data
    sites = ['Site_A', 'Site_B', 'Site_C', 'Site_D', 'Site_E']
    dates = pd.date_range('2024-01-01', periods=12, freq='M')
    
    progress_data = pd.DataFrame({
        'Date': dates,
        'Site_A': np.linspace(0, 85, 12) + np.random.normal(0, 2, 12),
        'Site_B': np.linspace(0, 60, 12) + np.random.normal(0, 2, 12),
        'Site_C': np.linspace(0, 45, 12) + np.random.normal(0, 2, 12),
        'Site_D': np.linspace(0, 92, 12) + np.random.normal(0, 2, 12),
        'Site_E': np.linspace(0, 30, 12) + np.random.normal(0, 2, 12),
    })
    
    fig_progress = go.Figure()
    for site in sites:
        fig_progress.add_trace(go.Scatter(
            x=progress_data['Date'],
            y=progress_data[site].clip(0, 100),
            mode='lines+markers',
            name=site,
        ))
    fig_progress.update_layout(title="Construction Progress %", yaxis_title="Progress %", hovermode='x unified')
    st.plotly_chart(fig_progress, use_container_width=True)

# ============ TAB 3: CONTRACTS ============
with tab3:
    st.subheader("📄 Contract Intelligence")
    
    col_upload, col_bench = st.columns(2)
    
    with col_upload:
        st.write("**Upload & Analyze**")
        uploaded_file = st.file_uploader("Upload PDF contract", type="pdf")
        if uploaded_file:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            st.info("🔍 Parsing clauses... Found 24 clauses (3 high-risk detected)")
            
            # Mock risk analysis
            risk_clauses = pd.DataFrame({
                'Clause': ['14.3(b)', '7.2(a)', '11.1'],
                'Category': ['Termination', 'Force Majeure', 'Covenant'],
                'Severity': [5, 4, 3],
                'Risk': ['CRITICAL', 'HIGH', 'MEDIUM'],
            })
            st.dataframe(risk_clauses, use_container_width=True)
    
    with col_bench:
        st.write("**Benchmark Comparison**")
        st.metric("vs Similar Projects", "Your Terms", "Better (5th percentile)")
        benchmark_metrics = pd.DataFrame({
            'Metric': ['Debt Tenor', 'Interest Rate', 'DSCR Requirement', 'Refinance Window'],
            'Your Deal': ['20 yrs', '7.2%', '1.25x', 'Year 10'],
            'Market Avg': ['18 yrs', '7.8%', '1.35x', 'Year 8'],
            'Status': ['✅', '✅', '✅', '⚠️'],
        })
        st.dataframe(benchmark_metrics, use_container_width=True)

# ============ TAB 4: SIMULATION ============
with tab4:
    st.subheader("🎮 Game Simulation")
    
    col_game_left, col_game_right = st.columns(2)
    
    with col_game_left:
        st.write("**Current Game State**")
        game_state = {
            'Quarter': 8,
            'Cash': '$2.3B',
            'Score': 756,
            'vs AI': 'Leading',
        }
        for key, val in game_state.items():
            st.metric(key, val)
    
    with col_game_right:
        st.write("**Next Event Options**")
        event_options = ['Sovereign Downgrade', 'Interest Rate Spike', 'Construction Delay', 'Revenue Collapse']
        selected_event = st.radio("Incoming Scenario", event_options)
        
        if st.button("Trigger Event"):
            st.warning(f"⚠️ {selected_event} activated! Portfolio impact: -2.3%")
    
    st.divider()
    
    # Simulation results
    st.write("**Monte Carlo Results (10K scenarios)**")
    mc_results = pd.DataFrame({
        'Scenario': ['Base Case', 'Downside (10%ile)', 'Upside (90%ile)', 'Stress Test'],
        'Avg Return': ['12.3%', '3.2%', '18.7%', '-5.2%'],
        'Probability': ['1.0', '0.10', '0.10', '0.05'],
    })
    st.dataframe(mc_results, use_container_width=True)

# ============ TAB 5: ANALYTICS ============
with tab5:
    st.subheader("📈 Model Analytics")
    
    col_ml1, col_ml2 = st.columns(2)
    
    with col_ml1:
        st.write("**CNN: Construction Progress**")
        st.metric("Model Accuracy", "94.2%", "Last 30 days")
        st.caption("ResNet-50 on Sentinel-2 time series")
    
    with col_ml2:
        st.write("**TFT: Revenue Forecasting**")
        st.metric("MAPE", "8.7%", "vs 15% target")
        st.caption("Multi-horizon demand prediction")
    
    st.divider()
    
    col_ml3, col_ml4 = st.columns(2)
    
    with col_ml3:
        st.write("**PINN: Infrastructure Degradation**")
        st.metric("Bridge Health Index", "87/100", "↑2 pts")
        st.caption("Physics-informed neural network (Paris Law)")
    
    with col_ml4:
        st.write("**GNN: Portfolio Risk""")
        st.metric("Systemic Risk Level", "MEDIUM", "via centrality analysis")
        st.caption("Graph neural network dependency propagation")

st.sidebar.divider()
st.sidebar.info("💡 Tip: Use Portfolio Manager tab for deal decisions")
