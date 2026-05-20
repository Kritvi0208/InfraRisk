"""Streamlit dashboard for InfraRisk AI"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="InfraRisk Lab", layout="wide")

st.title("🏗️ InfraRisk Lab - Simulation Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Portfolio Value", "$4.6B", "+2.5%")

with col2:
    st.metric("Avg DSCR", "1.38x", "-0.05x")

with col3:
    st.metric("Portfolio Risk", "6.2%", "+0.3%")

st.subheader("Project Portfolio")
portfolio_data = {
    'Project': ['Toll Road A', 'Power Plant B', 'Port C'],
    'Sector': ['Transport', 'Energy', 'Ports'],
    'DSCR': [1.42, 1.35, 1.28],
    'Risk Rating': ['AA', 'A', 'BBB']
}
st.dataframe(pd.DataFrame(portfolio_data))

st.subheader("DSCR Profile")
fig = go.Figure()
fig.add_trace(go.Scatter(y=[1.5, 1.45, 1.40, 1.38, 1.35], mode='lines', name='DSCR'))
fig.add_hline(y=1.2, line_dash="dash", annotation_text="Covenant Threshold")
st.plotly_chart(fig, use_container_width=True)
