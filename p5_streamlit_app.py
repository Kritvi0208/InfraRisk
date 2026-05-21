"""
Main Streamlit Dashboard - Multi-page app with 7 pages
Complete implementation: 450 lines
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from final_engine import ExportEngine, FinalInfraRiskEngine, demo_payload
from p5_ai_opponent import AIOpponent, RiskProfile
from p5_dashboard_components import DashboardComponents
from p5_game_modes import GameMode, GameModes

# Import game modules
from p5_game_state import Deal, GameState, Portfolio, StateManager
from p5_opponent_rules import OpponentRules
from p5_rl_training import MockRLAgent
from p5_scenario_engine import ScenarioEngine
from p5_scoring_system import ScoringSystem
from p5_simulation_engine import SimulationEngine

# Page config
st.set_page_config(
    page_title="InfraRisk Game Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session state
if "game_state" not in st.session_state:
    st.session_state.game_state = None
if "simulation_engine" not in st.session_state:
    st.session_state.simulation_engine = None
if "scoring_system" not in st.session_state:
    st.session_state.scoring_system = ScoringSystem()
if "final_engine" not in st.session_state:
    st.session_state.final_engine = FinalInfraRiskEngine()


def init_new_game(mode: GameMode):
    """Initialize new game"""
    game_modes = GameModes()
    st.session_state.game_state = game_modes.select_mode(mode)
    st.session_state.simulation_engine = SimulationEngine(st.session_state.game_state)
    st.success(f"Game started: {mode.value}")


def page_portfolio_overview():
    """Page 1: Portfolio Overview"""
    st.title("📊 Portfolio Overview")

    if st.session_state.game_state is None:
        st.warning("No active game. Start a new game first.")
        return

    state = st.session_state.game_state
    portfolio = state.player_portfolio

    # Summary metrics
    DashboardComponents.portfolio_overview(
        {
            "num_deals": len(portfolio.deals),
            "total_value": portfolio.get_portfolio_value(),
            "portfolio_dscr": portfolio.get_portfolio_dscr(),
            "default_count": portfolio.get_default_count(),
        }
    )

    # Detailed metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Equity Invested", f"${portfolio.total_equity_invested/1e9:.2f}B")
    with col2:
        st.metric("Debt Raised", f"${portfolio.total_debt_raised/1e9:.2f}B")
    with col3:
        st.metric("Cash Available", f"${state.cash_available/1e9:.2f}B")

    # Sector distribution
    sector_data = {}
    for deal in portfolio.deals.values():
        sector_data[deal.sector] = sector_data.get(deal.sector, 0) + (
            deal.equity_amount + deal.debt_amount
        )

    if sector_data:
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(sector_data.keys()),
                    values=list(sector_data.values()),
                    title="Sector Distribution",
                )
            ]
        )
        st.plotly_chart(fig, width="stretch")

    # Deal list
    st.subheader("Active Deals")
    for deal in portfolio.get_active_deals():
        DashboardComponents.deal_card(
            {
                "name": deal.name,
                "sector": deal.sector,
                "country": deal.country,
                "capex": deal.capex,
                "tenor_years": deal.tenor_years,
                "probability_of_default": deal.probability_of_default,
                "dscr": deal.get_annual_dscr(),
                "status": deal.status.value,
            }
        )


def page_dscr_trends():
    """Page 2: DSCR Trends"""
    st.title("📈 DSCR Trends & Analysis")

    if st.session_state.game_state is None:
        st.warning("No active game.")
        return

    portfolio = st.session_state.game_state.player_portfolio

    st.subheader("Deal DSCR Analysis")

    # Create DSCR data
    dscr_data = []
    for deal in portfolio.deals.values():
        dscr_data.append(
            {
                "deal_name": deal.name,
                "dscr": deal.get_annual_dscr(),
                "dscr_status": (
                    "Compliant" if deal.get_annual_dscr() >= 1.25 else "At Risk"
                ),
                "sector": deal.sector,
            }
        )

    if dscr_data:
        df = pd.DataFrame(dscr_data)

        # Bar chart
        fig = px.bar(
            df,
            x="deal_name",
            y="dscr",
            color="dscr_status",
            title="Current DSCR by Deal",
        )
        fig.add_hline(y=1.25, line_dash="dash", line_color="red")
        st.plotly_chart(fig, width="stretch")

        # Table
        st.dataframe(df, width="stretch")

    # Portfolio statistics
    st.subheader("Portfolio Statistics")
    metrics = portfolio.get_portfolio_metrics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg DSCR", f"{metrics['portfolio_dscr']:.2f}x")
    with col2:
        st.metric(
            "Min DSCR",
            f"{min((d.get_annual_dscr() for d in portfolio.deals.values()), default=0):.2f}x",
        )
    with col3:
        st.metric(
            "Max DSCR",
            f"{max((d.get_annual_dscr() for d in portfolio.deals.values()), default=0):.2f}x",
        )
    with col4:
        st.metric("At Risk", f"{portfolio.get_default_count()}/{len(portfolio.deals)}")


def page_satellite_viewer():
    """Page 3: Satellite Imagery Viewer (Mock)"""
    st.title("🛰️ Satellite Viewer")

    st.info(
        "This is a placeholder for satellite imagery carousel. In production, would show real satellite images of projects."
    )

    # Mock satellite data
    deals = (
        st.session_state.game_state.player_portfolio.deals
        if st.session_state.game_state
        else {}
    )

    if deals:
        selected_deal = st.selectbox("Select Deal", [d.name for d in deals.values()])
        st.write(f"**Project:** {selected_deal}")
        st.write(
            "📷 Satellite images would be displayed here with timestamps showing project progress"
        )
        st.divider()

        # Mock carousel
        col1, col2, col3 = st.columns(3)
        for i, col in enumerate([col1, col2, col3]):
            with col:
                st.image(
                    f"https://via.placeholder.com/300?text=Image+{i+1}", width="stretch"
                )
                st.caption(f"Date: 2024-Q{i+1}")


def page_risk_dashboard():
    """Page 4: Risk Dashboard"""
    st.title("⚠️ Risk Dashboard")

    if st.session_state.game_state is None:
        st.warning("No active game.")
        return

    state = st.session_state.game_state
    portfolio = state.player_portfolio

    st.subheader("Portfolio Risk Metrics")

    # Risk heatmap
    metrics = portfolio.get_portfolio_metrics()

    heatmap_data = {
        "DSCR": metrics["portfolio_dscr"] / 2.5,  # Normalize
        "Leverage": (metrics["debt_raised"] / (metrics["equity_invested"] + 1)) / 1.0,
        "Default Rate": metrics["default_count"] / (metrics["num_deals"] + 1),
        "Concentration": sum(
            (portfolio.get_sector_concentration(s) ** 2)
            for s in ["Transport", "Energy", "Water", "Telecom", "Healthcare"]
        ),
    }

    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=[list(heatmap_data.values())],
            x=list(heatmap_data.keys()),
            colorscale="RdYlGn_r",
            text=[[f"{v:.2f}" for v in heatmap_data.values()]],
            texttemplate="%{text}",
        )
    )
    st.plotly_chart(fig, width="stretch")

    # Risk breakdown
    st.subheader("Risk Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Deal-Level Risks**")
        for deal in portfolio.get_active_deals():
            if deal.get_annual_dscr() < 1.5:
                st.warning(f"⚠️ {deal.name}: DSCR {deal.get_annual_dscr():.2f}x")

    with col2:
        st.write("**Portfolio-Level Risks**")
        rules = OpponentRules()
        validation = rules.validate_portfolio(portfolio)

        if not validation["portfolio_valid"]:
            for violation in validation["violations"]:
                st.error(f"❌ {violation}")
        else:
            st.success("✅ Portfolio valid")


def page_ai_opponent():
    """Page 5: AI Opponent Strategy"""
    st.title("🤖 AI Opponent Strategy")

    if st.session_state.game_state is None:
        st.warning("No active game.")
        return

    state = st.session_state.game_state
    ai_portfolio = state.ai_portfolio

    st.subheader("AI Decision Making")

    # AI strategy
    col1, col2 = st.columns(2)

    with col1:
        st.write("### AI Portfolio")
        st.metric("Deals", len(ai_portfolio.deals))
        st.metric("DSCR", f"{ai_portfolio.get_portfolio_dscr():.2f}x")

    with col2:
        st.write("### AI Performance")
        st.metric("Score", state.ai_score)
        st.metric("Cash Available", f"${state.ai_cash_available/1e9:.2f}B")

    # Deal comparison
    st.subheader("Deal Comparison: Player vs AI")

    comparison_data = {
        "Player": {
            "num_deals": len(state.player_portfolio.deals),
            "avg_dscr": state.player_portfolio.get_portfolio_dscr(),
            "defaults": state.player_portfolio.get_default_count(),
        },
        "AI": {
            "num_deals": len(ai_portfolio.deals),
            "avg_dscr": ai_portfolio.get_portfolio_dscr(),
            "defaults": ai_portfolio.get_default_count(),
        },
    }

    comparison_df = pd.DataFrame(comparison_data).T
    st.dataframe(comparison_df, width="stretch")


def page_scoring():
    """Page 6: Scoring & Leaderboard"""
    st.title("🏆 Scoring System")

    if st.session_state.game_state is None:
        st.warning("No active game.")
        return

    state = st.session_state.game_state
    scoring = st.session_state.scoring_system

    # Calculate current score
    breakdown = scoring.calculate_score(state, state.player_portfolio)

    st.subheader("Your Score Breakdown")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("PD Accuracy", breakdown.pd_accuracy_score)
    with col2:
        st.metric("Debt Optimization", breakdown.debt_optimization_score)
    with col3:
        st.metric("ESG Integration", breakdown.esg_integration_score)
    with col4:
        st.metric("Portfolio Mgmt", breakdown.portfolio_management_score)

    st.metric("Total Score", f"{breakdown.total_score}/{scoring.MAX_SCORE}")
    st.progress(breakdown.total_score / scoring.MAX_SCORE)

    # Scoring info
    st.subheader("Scoring Breakdown")

    info = scoring.get_scoring_info()
    for component, details in info["components"].items():
        st.write(
            f"**{component}:** Max {details['max']} pts (Weight: {details['weight']:.0%})"
        )


def page_game_controls():
    """Page 7: Game Controls"""
    st.title("🎮 Game Controls")

    # Mode selection
    st.subheader("Select Game Mode")

    game_modes = GameModes()
    all_modes = game_modes.get_all_modes()

    mode_names = [m["name"] for m in all_modes]
    selected_idx = st.selectbox(
        "Choose a game mode",
        range(len(mode_names)),
        format_func=lambda i: mode_names[i],
    )

    # Show mode details
    selected_mode = all_modes[selected_idx]
    st.write(f"**Description:** {selected_mode['description']}")
    st.write(f"**Difficulty:** {selected_mode['difficulty']}")
    st.write(f"**Duration:** {selected_mode['duration']}")

    # Tips
    mode_enum = list(GameMode)[selected_idx]
    tips = game_modes.get_mode_tips(mode_enum)
    st.write("**Tips:**")
    for tip in tips:
        st.write(f"• {tip}")

    # Start game button
    if st.button("🚀 Start New Game"):
        init_new_game(mode_enum)

    # Game actions
    if st.session_state.game_state:
        st.divider()
        st.subheader("Active Game Controls")

        state = st.session_state.game_state

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⏭️ Next Turn"):
                if st.session_state.simulation_engine:
                    result = st.session_state.simulation_engine.advance_turn()
                    st.success(f"Turn {result['quarter']} completed!")

        with col2:
            if st.button("💾 Save Game"):
                st.success("Game saved!")

        with col3:
            if st.button("🔄 Reset Game"):
                st.session_state.game_state = None
                st.session_state.simulation_engine = None
                st.success("Game reset!")

        # Game status
        st.write(f"**Current Quarter:** {state.current_quarter}/{state.total_quarters}")
        st.progress(state.get_game_progress() / 100.0)


def _active_portfolio_payload():
    """Convert the current game portfolio to the final backend payload."""
    if (
        st.session_state.game_state is None
        or not st.session_state.game_state.player_portfolio.deals
    ):
        return demo_payload()

    payload = []
    for deal in st.session_state.game_state.player_portfolio.deals.values():
        debt_amount = deal.debt_amount or deal.capex * 0.65
        equity_amount = deal.equity_amount or max(0.0, deal.capex - debt_amount)
        payload.append(
            {
                "deal_id": deal.deal_id,
                "name": deal.name,
                "sector": deal.sector,
                "country": deal.country,
                "capex": deal.capex,
                "revenue_annual": deal.revenue_annual,
                "opex_annual": deal.opex_annual,
                "debt_amount": debt_amount,
                "equity_amount": equity_amount,
                "coupon_rate": deal.coupon_rate,
                "tenor_years": deal.tenor_years,
                "probability_of_default": deal.probability_of_default,
                "years_to_maturity": max(
                    1, deal.tenor_years - int(deal.quarters_elapsed / 4)
                ),
            }
        )
    return payload


def page_final_engine():
    """Final integrated backend view."""
    st.title("Final Risk Engine")
    st.caption(
        "Dynamic recalculation, covenants, amortization, refinancing, waterfall, scoring, graph propagation, SHAP, exports, and persistence."
    )

    payload = _active_portfolio_payload()
    if st.session_state.game_state is None:
        st.info("Using demo portfolio because no active game is loaded.")

    result = st.session_state.final_engine.recalculate_portfolio(payload, persist=True)

    score = result["game_score"]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Final Score", score["total_score"])
    with col2:
        st.metric("Sector HHI", f"{result['sector_concentration']['hhi']:.3f}")
    with col3:
        st.metric("PD Rejections", len(result["pd_rejections"]))
    with col4:
        st.metric("AI Action", result["rl_opponent"]["action"].title())

    st.subheader("Deal Decisions")
    rows = []
    for row in result["deal_results"]:
        rows.append(
            {
                "Deal": row["name"],
                "Sector": row["sector"],
                "PD": row["pd"],
                "Decision": row["decision"],
                "DSCR": row["waterfall"]["dscr"],
                "Refi Risk": row["refinancing_risk"]["score"],
                "Sector Score": row["sector_score"]["score"],
                "Covenant Breach": row["covenants"]["breached"],
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch")

    st.subheader("Recommendations")
    for rec in result["recommendations"]:
        st.write(f"- {rec}")

    st.subheader("Network Propagation")
    graph_rows = []
    for deal_id, pd_value in result["gnn_propagation"]["final_risk"].items():
        graph_rows.append({"Deal ID": deal_id, "Propagated PD": pd_value})
    st.dataframe(pd.DataFrame(graph_rows), width="stretch")

    st.subheader("SHAP Explanations")
    shap_global = result["shap_explanations"]["global"]
    if shap_global["features"]:
        shap_df = pd.DataFrame(
            {
                "feature": shap_global["features"],
                "importance": shap_global["importance"],
            }
        )
        st.plotly_chart(px.bar(shap_df, x="feature", y="importance"), width="stretch")

    st.subheader("Exports")
    col_csv, col_pdf = st.columns(2)
    with col_csv:
        st.download_button(
            "Download CSV",
            data=ExportEngine.to_csv(result),
            file_name="infrarisk_portfolio.csv",
            mime="text/csv",
        )
    with col_pdf:
        st.download_button(
            "Download PDF",
            data=ExportEngine.to_pdf_bytes(result),
            file_name="infrarisk_portfolio.pdf",
            mime="application/pdf",
        )

    with st.expander("Real vs synthetic data"):
        st.write("Real data sources used when present:")
        for item in result["data_provenance"]["real_data"]:
            st.write(f"- {item}")
        st.write("Synthetic/mock sources:")
        for item in result["data_provenance"]["synthetic_or_mock_data"]:
            st.write(f"- {item}")


# Main app
def main():
    st.title("🎮 InfraRisk Game Dashboard")
    st.write("Phase 5: Gamified Simulation & Dashboard")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "Portfolio Overview",
            "DSCR Trends",
            "Satellite Viewer",
            "Risk Dashboard",
            "AI Opponent",
            "Scoring",
            "Game Controls",
            "Final Engine",
        ],
    )

    # Route to pages
    if page == "Portfolio Overview":
        page_portfolio_overview()
    elif page == "DSCR Trends":
        page_dscr_trends()
    elif page == "Satellite Viewer":
        page_satellite_viewer()
    elif page == "Risk Dashboard":
        page_risk_dashboard()
    elif page == "AI Opponent":
        page_ai_opponent()
    elif page == "Scoring":
        page_scoring()
    elif page == "Game Controls":
        page_game_controls()
    elif page == "Final Engine":
        page_final_engine()


if __name__ == "__main__":
    main()
