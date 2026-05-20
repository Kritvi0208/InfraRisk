"""
InfraRisk AI Complete Dashboard
Combines all AI outputs + Contract Intelligence + Forecasts + Contagion
Self-contained file for immediate use
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import json
import io
import math
import sqlite3
from pathlib import Path
from typing import Dict, Tuple, List, Optional

from advanced_features import CashflowWaterfallEngine, ContractIntelligenceEngine

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="InfraRisk Lab",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ STYLING ============
st.markdown("""
<style>
    .metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;}
    .risk-high {background: #ff6b6b; color: white; padding: 10px; border-radius: 5px;}
    .risk-medium {background: #ffa500; color: white; padding: 10px; border-radius: 5px;}
    .risk-low {background: #51cf66; color: white; padding: 10px; border-radius: 5px;}
    .alert-box {background: #fff3cd; border: 1px solid #ffc107; padding: 12px; border-radius: 5px; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

DATA_ROOT = Path(__file__).resolve().parent / "data" / "raw"
PROCESSED_ROOT = Path(__file__).resolve().parent / "data" / "processed"
DB_PATH = PROCESSED_ROOT / "infrarisk.db"

COUNTRY_CODE_MAP = {
    "India": "IN",
    "China": "CN",
    "Brazil": "BR",
    "South Africa": "ZA",
    "Nigeria": "NG",
    "Kenya": "KE",
    "Ghana": "GH",
    "Egypt": "EG",
    "Vietnam": "VN",
    "Philippines": "PH",
    "Indonesia": "ID",
    "Thailand": "TH",
    "Mexico": "MX",
    "Colombia": "CO",
    "Peru": "PE",
    "Chile": "CL",
    "Turkey": "TR",
    "Pakistan": "PK",
    "Bangladesh": "BD",
    "Morocco": "MA",
    "United States": "US",
    "United Kingdom": "GB",
    "Germany": "DE",
    "France": "FR",
    "Japan": "JP",
    "South Korea": "KR",
    "Singapore": "SG",
    "United Arab Emirates": "AE",
    "Saudi Arabia": "SA",
    "Qatar": "QA",
    "Oman": "OM",
}

SECTOR_MAP = {
    "Roads": "Transport",
    "Railways": "Transport",
    "Airports": "Transport",
    "Ports": "Transport",
    "Power": "Energy",
    "Water": "Water",
    "Telecom": "Telecom",
}

SECTOR_FINANCE = {
    "Transport": {"rev_multiple": 0.18, "opex_ratio": 0.35},
    "Energy": {"rev_multiple": 0.22, "opex_ratio": 0.30},
    "Water": {"rev_multiple": 0.14, "opex_ratio": 0.32},
    "Telecom": {"rev_multiple": 0.26, "opex_ratio": 0.28},
    "Social": {"rev_multiple": 0.12, "opex_ratio": 0.38},
    "Other": {"rev_multiple": 0.16, "opex_ratio": 0.33},
}

PPI_COUNTRY_CODES = {
    1: "Afghanistan",
    6: "Argentina",
    8: "Albania",
    11: "Armenia",
    14: "Azerbaijan",
    19: "Bangladesh",
    24: "Bolivia",
    26: "Brazil",
    31: "Bulgaria",
    35: "Cambodia",
    38: "Chile",
    41: "China",
    45: "Colombia",
    53: "Dominican Republic",
    56: "Ecuador",
    57: "Egypt",
    65: "Georgia",
    68: "Ghana",
    70: "Guatemala",
    75: "Honduras",
    79: "India",
    80: "Indonesia",
    89: "Jordan",
    91: "Kazakhstan",
    93: "Kenya",
    101: "Russian Federation",
    105: "Malaysia",
    108: "Mexico",
    114: "Morocco",
    121: "Nigeria",
    128: "Pakistan",
    129: "Panama",
    130: "Peru",
    131: "Philippines",
    138: "Romania",
    151: "South Africa",
    154: "Sri Lanka",
    162: "Thailand",
    166: "Turkey",
    172: "Ukraine",
    179: "Vietnam",
}

PPI_SECTOR_CODES = {
    1: "Transport",
    2: "Energy",
    3: "Telecom",
    4: "Water",
}

PPI_STATUS_CODES = {
    1: "Operational",
    2: "Under Construction",
    3: "Canceled",
    4: "Distressed",
    5: "Concluded",
}

SAMPLE_CONTRACT_TEXT = """
INFRASTRUCTURE PROJECT FINANCE AGREEMENT

This Agreement entered into this 1st day of June, 2024

PARTIES:
- Sponsor: ABC Solar Energy Private Limited
- Lender: Development Finance Corporation
- Project Location: Tamil Nadu, India

ARTICLE 1: DEFINITIONS
1.1 "Sponsor" means ABC Solar Energy Private Limited.

ARTICLE 2: FINANCING STRUCTURE
2.1 Total Project Cost: USD 300 Million
2.2 Senior Debt: USD 200 Million
2.3 Equity Investment: USD 100 Million

SECTION 3: CREDIT TERMS
3.1 Debt Tenor: 20 years (360 months)
3.2 Interest Rate: SOFR + 2.5% per annum

SECTION 4: FINANCIAL COVENANTS
4.1 DSCR Maintenance: Borrower must maintain minimum DSCR of 1.25x
4.2 Debt Service Reserve Account: Borrower shall maintain DSRA equal to 6 months of debt service.

ARTICLE 5: FORCE MAJEURE
5.1 Force Majeure Events include acts of god, pandemics, and regulatory changes.

ARTICLE 8: TERMINATION RIGHTS
8.1 Lender may terminate upon material breach or covenant violation.

ARTICLE 12: REFINANCING
12.1 Limited refinancing rights available only after Year 15, subject to DSCR of 1.5x.
"""


@st.cache_data(show_spinner=False)
def load_real_data() -> Dict[str, pd.DataFrame]:
    def read_csv(path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        return pd.read_csv(path, low_memory=False)

    return {
        "ppi": normalize_ppi_schema(read_csv(DATA_ROOT / "ppi" / "ppi_projects.csv")),
        "ijglobal": read_csv(DATA_ROOT / "ppi" / "ijglobal_alternative.csv"),
        "wdi": read_csv(DATA_ROOT / "worldbank" / "wdi_macro.csv"),
        "cds": read_csv(DATA_ROOT / "worldbank" / "cds_spreads.csv"),
        "nbi": read_csv(DATA_ROOT / "nbi" / "nbi_bridges.csv"),
    }


def resolve_country_code(country: str, wdi_df: pd.DataFrame, cds_df: pd.DataFrame) -> Optional[str]:
    if not isinstance(country, str):
        return None
    mapped = COUNTRY_CODE_MAP.get(country)
    if mapped:
        return mapped
    candidate = country.strip().upper()[:2]
    if not wdi_df.empty and candidate in set(wdi_df["country"]):
        return candidate
    if not cds_df.empty and candidate in set(cds_df["country"]):
        return candidate
    return None


def latest_macro_snapshot(wdi_df: pd.DataFrame, cds_df: pd.DataFrame, country_code: Optional[str]) -> Dict[str, float]:
    default = {
        "gdp_growth": 3.0,
        "inflation": 4.0,
        "govt_debt_gdp": 55.0,
        "current_account_gdp": -2.0,
        "rule_of_law": 0.0,
        "regulatory_quality": 0.0,
        "govt_effectiveness": 0.0,
        "control_of_corruption": 0.0,
        "cds_5y_bps": 220.0,
    }
    if not country_code:
        return default

    if not wdi_df.empty:
        wdi_country = wdi_df[wdi_df["country"] == country_code]
        if not wdi_country.empty:
            latest = wdi_country.sort_values("year").tail(1).iloc[0].to_dict()
            default.update({
                "gdp_growth": float(latest.get("gdp_growth", default["gdp_growth"])),
                "inflation": float(latest.get("inflation", default["inflation"])),
                "govt_debt_gdp": float(latest.get("govt_debt_gdp", default["govt_debt_gdp"])),
                "current_account_gdp": float(latest.get("current_account_gdp", default["current_account_gdp"])),
                "rule_of_law": float(latest.get("rule_of_law", default["rule_of_law"])),
                "regulatory_quality": float(latest.get("regulatory_quality", default["regulatory_quality"])),
                "govt_effectiveness": float(latest.get("govt_effectiveness", default["govt_effectiveness"])),
                "control_of_corruption": float(latest.get("control_of_corruption", default["control_of_corruption"])),
            })

    if not cds_df.empty:
        cds_country = cds_df[cds_df["country"] == country_code]
        if not cds_country.empty:
            latest_cds = cds_country.sort_values("date").tail(1).iloc[0].to_dict()
            default["cds_5y_bps"] = float(latest_cds.get("cds_5y_bps", default["cds_5y_bps"]))

    return default


def normalize_sector(sector: str) -> str:
    if not isinstance(sector, str):
        return "Other"
    return SECTOR_MAP.get(sector, sector.title() if sector.title() in SECTOR_FINANCE else "Other")


def decode_ppi_country(value) -> str:
    if isinstance(value, str) and not value.isdigit():
        return value
    try:
        return PPI_COUNTRY_CODES.get(int(value), f"Country {int(value)}")
    except (TypeError, ValueError):
        return "Unknown"


def decode_ppi_sector(value) -> str:
    if isinstance(value, str) and not value.isdigit():
        return value
    try:
        return PPI_SECTOR_CODES.get(int(value), "Other")
    except (TypeError, ValueError):
        return "Other"


def decode_ppi_status(value) -> str:
    if isinstance(value, str) and not value.isdigit():
        return value
    try:
        return PPI_STATUS_CODES.get(int(value), "Unknown")
    except (TypeError, ValueError):
        return "Unknown"


def normalize_ppi_schema(ppi_df: pd.DataFrame) -> pd.DataFrame:
    """Map real World Bank PPI columns to the dashboard's canonical schema."""
    if ppi_df.empty:
        return ppi_df
    df = ppi_df.copy()

    if "capex_usd_million" not in df.columns:
        investment = pd.to_numeric(df.get("investment", 0), errors="coerce")
        capacity_dollar = pd.to_numeric(df.get("CapacityDollar", 0), errors="coerce")
        df["capex_usd_million"] = investment.fillna(capacity_dollar).fillna(0.0)

    if "debt_usd_million" not in df.columns:
        debt = pd.to_numeric(df.get("debt", 0), errors="coerce").fillna(0.0)
        df["debt_usd_million"] = debt.where(debt > 0, df["capex_usd_million"] * 0.65)

    if "equity_usd_million" not in df.columns:
        equity = pd.to_numeric(df.get("equity", 0), errors="coerce").fillna(0.0)
        df["equity_usd_million"] = equity.where(equity > 0, (df["capex_usd_million"] - df["debt_usd_million"]).clip(lower=0.0))

    if "leverage_pct" not in df.columns:
        df["leverage_pct"] = np.where(
            df["capex_usd_million"] > 0,
            df["debt_usd_million"] / df["capex_usd_million"] * 100,
            65.0,
        )

    if "debt_tenor_years" not in df.columns:
        df["debt_tenor_years"] = 20

    if "financial_close_year" not in df.columns:
        df["financial_close_year"] = pd.to_numeric(df.get("FCY", df.get("IY", 2020)), errors="coerce").fillna(2020).astype(int)

    if "project_id" not in df.columns:
        df["project_id"] = df.get("ID", pd.Series(range(1, len(df) + 1), index=df.index)).apply(lambda x: f"PPI-{x}")

    if "project_name" not in df.columns:
        df["project_name"] = df.get("name", df["project_id"]).fillna(df["project_id"]).astype(str)

    df["country"] = df.get("country", "Unknown").apply(decode_ppi_country)
    df["sector"] = df.get("sector", "Other").apply(decode_ppi_sector)
    df["status"] = df.get("status", df.get("status_n", "Unknown")).apply(decode_ppi_status)
    df = df[df["capex_usd_million"] > 0].copy()
    return df


def derive_coupon_rate(cds_bps: float) -> float:
    base_rate = 0.04
    spread = cds_bps / 10000
    return base_rate + spread + 0.01


def amortization_payment(principal: float, annual_rate: float, years: int) -> float:
    if years <= 0:
        return principal
    if annual_rate <= 0:
        return principal / years
    rate = annual_rate
    factor = (rate * (1 + rate) ** years) / ((1 + rate) ** years - 1)
    return principal * factor


def npv(rate: float, cashflows: List[float]) -> float:
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows, start=1))


def estimate_revenue_and_opex(capex_m: float, sector_group: str, macro: Dict[str, float]) -> Tuple[float, float, float]:
    finance = SECTOR_FINANCE.get(sector_group, SECTOR_FINANCE["Other"])
    gdp_adj = 1 + (macro["gdp_growth"] / 100)
    inflation_drag = 1 - min(0.15, macro["inflation"] / 100 * 0.5)
    revenue_m = capex_m * finance["rev_multiple"] * gdp_adj * inflation_drag
    opex_m = revenue_m * finance["opex_ratio"]
    maintenance_m = capex_m * 0.02
    return revenue_m, opex_m, maintenance_m


def compute_financial_metrics(
    capex_m: float,
    debt_m: float,
    equity_m: float,
    tenor_years: int,
    sector_group: str,
    macro: Dict[str, float],
) -> Dict[str, float]:
    coupon = derive_coupon_rate(macro["cds_5y_bps"])
    revenue_m, opex_m, maintenance_m = estimate_revenue_and_opex(capex_m, sector_group, macro)
    annual_capex_m = capex_m / max(tenor_years, 1)
    debt_service_m = amortization_payment(debt_m, coupon, tenor_years)

    waterfall = CashflowWaterfallEngine.calculate_full_waterfall(
        revenue=revenue_m,
        opex=opex_m,
        capex=annual_capex_m,
        debt_service=debt_service_m,
        tax_rate=0.25,
        reserve_pct=0.05,
    )
    dscr = waterfall["metrics"]["dscr"]
    leverage = debt_m / max(equity_m, 1)
    macro_risk = (macro["inflation"] / 1000) + (macro["cds_5y_bps"] / 10000) + (macro["govt_debt_gdp"] / 1000)
    pd = 0.02 + max(0.0, 1.5 - dscr) * 0.08 + max(0.0, leverage - 2.0) * 0.02 + macro_risk
    pd = max(0.005, min(pd, 0.30))

    ocf = waterfall["waterfall"]["ocf"]
    llcr = npv(max(0.03, coupon), [ocf] * max(tenor_years, 1)) / max(debt_m, 1)
    plcr = npv(max(0.03, coupon), [ocf] * max(tenor_years + 5, 1)) / max(debt_m, 1)

    reserve_account = debt_service_m * 0.5
    covenant_breach = dscr < 1.2 or leverage > 3.5 or reserve_account < debt_service_m * 0.25
    refinancing_risk = "HIGH" if dscr < 1.25 or coupon > 0.09 else "MEDIUM" if dscr < 1.5 else "LOW"

    return {
        "coupon_rate": coupon,
        "revenue_m": revenue_m,
        "opex_m": opex_m,
        "maintenance_m": maintenance_m,
        "debt_service_m": debt_service_m,
        "dscr": dscr,
        "leverage": leverage,
        "pd": pd,
        "llcr": llcr,
        "plcr": plcr,
        "reserve_account_m": reserve_account,
        "covenant_breach": covenant_breach,
        "refinancing_risk": refinancing_risk,
        "waterfall": waterfall["waterfall"],
    }


def apply_contract_adjustment(portfolio_df: pd.DataFrame, risk_score: Optional[float]) -> pd.DataFrame:
    if risk_score is None or portfolio_df.empty:
        return portfolio_df
    adjustment = 1 - min(0.15, risk_score / 500)
    updated = portfolio_df.copy()
    if "dscr_base" not in updated.columns:
        updated["dscr_base"] = updated["dscr"]
    if "pd_base" not in updated.columns:
        updated["pd_base"] = updated["pd"]
    updated["dscr"] = updated["dscr_base"] * adjustment
    updated["pd"] = (updated["pd_base"] + risk_score / 1000).clip(0.005, 0.35)
    updated["contract_risk_score"] = risk_score
    updated["covenant_breach"] = updated["dscr"] < 1.2
    return updated


def build_portfolio_df(
    ppi_df: pd.DataFrame,
    wdi_df: pd.DataFrame,
    cds_df: pd.DataFrame,
    num_projects: int,
    sectors: List[str],
    countries: List[str],
) -> pd.DataFrame:
    if ppi_df.empty:
        return pd.DataFrame()

    df = ppi_df.copy()
    df["sector_group"] = df["sector"].apply(normalize_sector)
    if sectors:
        # Normalize the sector filter to match normalized sector_group values
        normalized_sectors = [normalize_sector(s) for s in sectors]
        df = df[df["sector_group"].isin(normalized_sectors)]
    if countries:
        df = df[df["country"].isin(countries)]

    df = df.sort_values("capex_usd_million", ascending=False).head(num_projects)
    rows = []
    for _, row in df.iterrows():
        capex_m = float(row.get("capex_usd_million", 0.0))
        leverage_pct = float(row.get("leverage_pct", 70))
        debt_m = float(row.get("debt_usd_million", capex_m * leverage_pct / 100))
        equity_m = float(row.get("equity_usd_million", max(capex_m - debt_m, 0.0)))
        tenor_years = int(row.get("debt_tenor_years", 20))

        country_code = resolve_country_code(str(row.get("country", "")), wdi_df, cds_df)
        macro = latest_macro_snapshot(wdi_df, cds_df, country_code)
        sector_group = row.get("sector_group", "Other")
        metrics = compute_financial_metrics(
            capex_m=capex_m,
            debt_m=debt_m,
            equity_m=equity_m,
            tenor_years=tenor_years,
            sector_group=sector_group,
            macro=macro,
        )

        rows.append({
            "project_id": row.get("project_id", row.get("project_name", "")),
            "project_name": row.get("project_name", "Unnamed Project"),
            "country": row.get("country", "Unknown"),
            "sector": row.get("sector", "Unknown"),
            "sector_group": sector_group,
            "status": row.get("status", "Unknown"),
            "financial_close_year": int(row.get("financial_close_year", 2020)),
            "capex_m": capex_m,
            "debt_m": debt_m,
            "equity_m": equity_m,
            "tenor_years": tenor_years,
            **metrics,
            "macro_gdp_growth": macro["gdp_growth"],
            "macro_inflation": macro["inflation"],
            "macro_cds_bps": macro["cds_5y_bps"],
        })

    return pd.DataFrame(rows)


def portfolio_summary(portfolio_df: pd.DataFrame) -> Dict[str, float]:
    if portfolio_df.empty:
        return {
            "projects": 0,
            "value": 0.0,
            "avg_dscr": 0.0,
            "avg_pd": 0.0,
            "avg_llcr": 0.0,
            "avg_plcr": 0.0,
        }
    return {
        "projects": len(portfolio_df),
        "value": float((portfolio_df["debt_m"] + portfolio_df["equity_m"]).sum() * 1e6),
        "avg_dscr": float(portfolio_df["dscr"].mean()),
        "avg_pd": float(portfolio_df["pd"].mean()),
        "avg_llcr": float(portfolio_df["llcr"].mean()),
        "avg_plcr": float(portfolio_df["plcr"].mean()),
    }


def forecast_dscr_pd(base_dscr: float, base_pd: float, macro: Dict[str, float], quarters: int) -> pd.DataFrame:
    gdp_adj = 1 + (macro["gdp_growth"] / 1000)
    inflation_drag = 1 - min(0.06, macro["inflation"] / 1000)
    trend = base_dscr * gdp_adj * inflation_drag
    dscr_path = np.linspace(base_dscr, trend, quarters)
    pd_path = np.linspace(base_pd, base_pd * (1 + macro["cds_5y_bps"] / 5000), quarters)
    return pd.DataFrame({
        "Quarter": [f"Q{i+1}" for i in range(quarters)],
        "DSCR": dscr_path,
        "PD": pd_path,
    })


def monte_carlo_stress(dscr: float, volatility: float = 0.25, scenarios: int = 10000, seed: int = 42) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    simulated = rng.normal(dscr, volatility, scenarios)
    simulated = np.clip(simulated, 0.3, 3.5)
    breach_count = int((simulated < 1.2).sum())
    breach_pct = breach_count / scenarios * 100
    var_95 = np.percentile(simulated, 5)
    cvar_95 = simulated[simulated <= var_95].mean() if breach_count > 0 else var_95
    return {
        "mean": float(np.mean(simulated)),
        "std": float(np.std(simulated)),
        "p5": float(np.percentile(simulated, 5)),
        "p50": float(np.percentile(simulated, 50)),
        "p95": float(np.percentile(simulated, 95)),
        "var_95": float(var_95),
        "cvar_95": float(cvar_95),
        "breach_pct": float(breach_pct),
        "distribution": simulated,
    }


def build_contagion_edges(portfolio_df: pd.DataFrame) -> List[Tuple[int, int, float]]:
    edges = []
    if portfolio_df.empty:
        return edges
    for i, row_i in portfolio_df.iterrows():
        for j, row_j in portfolio_df.iterrows():
            if j <= i:
                continue
            weight = 0.0
            if row_i["sector_group"] == row_j["sector_group"]:
                weight += 0.6
            if row_i["country"] == row_j["country"]:
                weight += 0.4
            if weight > 0:
                edges.append((i, j, weight))
    return edges


def compute_contagion_metrics(portfolio_df: pd.DataFrame) -> Dict[str, float]:
    edges = build_contagion_edges(portfolio_df)
    if portfolio_df.empty:
        return {"direct": 0, "indirect": 0, "propagation_score": 0, "systemic_risk": "LOW"}
    risk_scores = portfolio_df["pd"].fillna(0).to_numpy()
    total_weight = sum(weight for _, _, weight in edges) or 1.0
    propagation_score = min(100, (risk_scores.mean() * 1000) + (total_weight / len(portfolio_df) * 20))
    systemic_risk = "HIGH" if propagation_score > 70 else "MEDIUM" if propagation_score > 40 else "LOW"
    direct = max(1, math.ceil(len(portfolio_df) * risk_scores.mean()))
    indirect = max(0, int(len(portfolio_df) * 0.3))
    return {
        "direct": direct,
        "indirect": indirect,
        "propagation_score": propagation_score,
        "systemic_risk": systemic_risk,
    }


def apply_event_to_portfolio(portfolio_df: pd.DataFrame, event: Dict[str, float]) -> pd.DataFrame:
    if portfolio_df.empty:
        return portfolio_df
    updated = portfolio_df.copy()
    updated["revenue_m"] = updated["revenue_m"] * event["revenue_multiplier"]
    updated["opex_m"] = updated["opex_m"] * event["cost_multiplier"]
    updated["capex_m"] = updated["capex_m"] * event["capex_multiplier"]
    updated["coupon_rate"] = updated["coupon_rate"] + event["coupon_delta"]
    if "dscr_base" in updated.columns:
        updated["dscr_base"] = (updated["dscr_base"] * event["dscr_multiplier"]).clip(0.3, 3.5)
        updated["pd_base"] = (updated["pd_base"] + event["pd_delta"]).clip(0.005, 0.35)
        updated["dscr"] = updated["dscr_base"]
        updated["pd"] = updated["pd_base"]
    else:
        updated["dscr"] = (updated["dscr"] * event["dscr_multiplier"]).clip(0.3, 3.5)
        updated["pd"] = (updated["pd"] + event["pd_delta"]).clip(0.005, 0.35)
    updated["covenant_breach"] = updated["dscr"] < 1.2
    return updated


def build_network_figure(portfolio_df: pd.DataFrame) -> go.Figure:
    n = len(portfolio_df)
    if n == 0:
        return go.Figure()
    nodes_x, nodes_y = [], []
    for i in range(n):
        angle = 2 * math.pi * i / n
        nodes_x.append(math.cos(angle))
        nodes_y.append(math.sin(angle))
    edges_x, edges_y = [], []
    for i, j, weight in build_contagion_edges(portfolio_df):
        edges_x.extend([nodes_x[i], nodes_x[j], None])
        edges_y.extend([nodes_y[i], nodes_y[j], None])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edges_x, y=edges_y, mode="lines", line=dict(width=1, color="#aaa")))
    fig.add_trace(go.Scatter(
        x=nodes_x,
        y=nodes_y,
        mode="markers+text",
        marker=dict(size=15, color="#667eea"),
        text=[f"P{i+1}" for i in range(n)],
    ))
    fig.update_layout(showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=400)
    return fig


def build_satellite_timeline(project_row: pd.Series, quarters: int = 12) -> pd.DataFrame:
    if project_row is None or project_row.empty:
        return pd.DataFrame({"Date": [], "Progress": []})
    base_progress = AIModels.cnn_satellite(project_row)["progress"] / 100
    start_year = int(project_row.get("financial_close_year", 2020))
    timeline = pd.date_range(f"{start_year}-01-01", periods=quarters, freq="QE")
    progress = np.linspace(0.1, max(0.2, base_progress), quarters)
    return pd.DataFrame({"Date": timeline, "Progress": progress})


def extract_pdf_text(uploaded_file: Optional[object]) -> str:
    if uploaded_file is None:
        return ""
    try:
        import pdfplumber
    except ImportError:
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        text_parts = [(page.extract_text() or "") for page in pdf.pages]
    return "\n".join(text_parts)


def analyze_contract_text(text: str) -> Dict[str, object]:
    clauses = ContractIntelligenceEngine.extract_clauses(text)
    risk_score, high_risk = ContractIntelligenceEngine.calculate_contract_risk_score(clauses)
    benchmark = ContractIntelligenceEngine.benchmark_analysis(risk_score, len(clauses))
    recommendations = ContractIntelligenceEngine.generate_recommendations(clauses, risk_score)
    return {
        "clauses": clauses,
        "risk_score": risk_score,
        "high_risk": high_risk,
        "benchmark": benchmark,
        "recommendations": recommendations,
    }


def init_db() -> None:
    PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                created_at TEXT NOT NULL,
                portfolio_json TEXT NOT NULL,
                events_json TEXT NOT NULL,
                contract_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contract_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                contract_text TEXT NOT NULL,
                analysis_json TEXT NOT NULL
            )
            """
        )


def save_portfolio_snapshot(label: str, portfolio_df: pd.DataFrame, events: List[Dict], contract_summary: Optional[Dict]) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO portfolio_snapshots (label, created_at, portfolio_json, events_json, contract_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                label,
                datetime.now().isoformat(),
                portfolio_df.to_json(orient="records"),
                json.dumps(events),
                json.dumps(contract_summary) if contract_summary else None,
            ),
        )


def list_portfolio_snapshots() -> List[str]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT label FROM portfolio_snapshots ORDER BY id DESC").fetchall()
    return [row[0] for row in rows]


def load_portfolio_snapshot(label: str) -> Optional[Dict[str, object]]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT portfolio_json, events_json, contract_json FROM portfolio_snapshots WHERE label = ? ORDER BY id DESC LIMIT 1",
            (label,),
        ).fetchone()
    if not row:
        return None
    portfolio_df = pd.read_json(row[0])
    events = json.loads(row[1])
    contract = json.loads(row[2]) if row[2] else None
    return {"portfolio_df": portfolio_df, "events": events, "contract": contract}


def save_contract_upload(filename: str, contract_text: str, analysis: Dict[str, object]) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO contract_uploads (created_at, filename, contract_text, analysis_json)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), filename, contract_text, json.dumps(analysis)),
        )


def normalize_forecast_frame(forecast: pd.DataFrame, quarters: int, base_dscr: float, base_pd: float, macro: Dict[str, float]) -> pd.DataFrame:
    if forecast is None or forecast.empty:
        fallback = forecast_dscr_pd(base_dscr, base_pd, macro, quarters)
        fallback["Upper_95"] = fallback["DSCR"] + 0.2
        fallback["Lower_5"] = fallback["DSCR"] - 0.2
        return fallback[["Quarter", "DSCR", "Upper_95", "Lower_5"]]

    normalized = forecast.copy()
    if "Quarter" not in normalized.columns:
        normalized = normalized.rename(columns={normalized.columns[0]: "Quarter"})
    if "DSCR" not in normalized.columns and len(normalized.columns) > 1:
        normalized = normalized.rename(columns={normalized.columns[1]: "DSCR"})
    if "Upper_95" not in normalized.columns:
        normalized["Upper_95"] = normalized["DSCR"] + 0.2
    if "Lower_5" not in normalized.columns:
        normalized["Lower_5"] = normalized["DSCR"] - 0.2
    return normalized[["Quarter", "DSCR", "Upper_95", "Lower_5"]]

# ============ AI MODEL INFERENCE (DATA-DRIVEN) ============
class AIModels:
    @staticmethod
    def cnn_satellite(project_row: pd.Series) -> Dict[str, object]:
        """Deterministic construction progress from project status and DSCR."""
        status = str(project_row.get("status", "")).lower()
        base = 0.3
        if "operational" in status:
            base = 0.95
        elif "construction" in status:
            base = 0.65
        elif "development" in status:
            base = 0.35
        elif "distressed" in status:
            base = 0.45

        dscr = float(project_row.get("dscr", 1.3))
        progress = max(0.1, min(1.0, base + (dscr - 1.2) * 0.05))
        anomaly = dscr < 1.1 or "distressed" in status
        anomaly_type = "Funding gap" if dscr < 1.1 else "Construction delay" if "distressed" in status else "None"
        confidence = 0.92 if not anomaly else 0.86
        images_captured = max(6, int(project_row.get("tenor_years", 20) / 2))

        return {
            "progress": progress * 100,
            "anomaly": anomaly,
            "anomaly_type": anomaly_type,
            "confidence": confidence,
            "images_captured": images_captured,
        }

    @staticmethod
    def tft_forecasts(base_dscr: float, macro: Dict[str, float], quarters: int = 8) -> pd.DataFrame:
        """Deterministic DSCR forecast conditioned on macro trends."""
        forecast = forecast_dscr_pd(base_dscr, base_pd=0.03, macro=macro, quarters=quarters)
        return normalize_forecast_frame(forecast, quarters, base_dscr, 0.03, macro)

    @staticmethod
    def pinn_degradation(asset: str, nbi_df: pd.DataFrame) -> Dict[str, object]:
        """PINN-style degradation using real NBI condition distribution."""
        if nbi_df.empty:
            current = 70.0
        else:
            condition_col = "overall_condition" if "overall_condition" in nbi_df.columns else nbi_df.columns[0]
            current = float(nbi_df[condition_col].mean()) * 10
        projected_5yr = max(5, current - 12)
        urgency = "CRITICAL" if current < 40 else "HIGH" if current < 60 else "MEDIUM"
        return {
            "current": current,
            "projected_5yr": projected_5yr,
            "failure_years": max(8, (100 - current) / 2.5),
            "urgency": urgency,
        }

    @staticmethod
    def gnn_contagion(portfolio_df: pd.DataFrame) -> Dict[str, object]:
        """Contagion metrics derived from portfolio links."""
        return compute_contagion_metrics(portfolio_df)

# ============ FINANCIAL ENGINE ============
class FinancialEngine:
    @staticmethod
    def calculate_metrics(
        capex_m: float,
        debt_m: float,
        equity_m: float,
        tenor_years: int,
        sector_group: str,
        macro: Dict[str, float],
    ) -> Dict[str, float]:
        """Financial calculations using waterfall + covenant logic."""
        return compute_financial_metrics(
            capex_m=capex_m,
            debt_m=debt_m,
            equity_m=equity_m,
            tenor_years=tenor_years,
            sector_group=sector_group,
            macro=macro,
        )
    
    @staticmethod
    def stress_test(base_dscr: float, scenarios: int = 10000) -> Dict[str, float]:
        """Monte Carlo stress testing with VaR/CVaR."""
        return monte_carlo_stress(base_dscr, volatility=0.25, scenarios=scenarios)

# ============ EVENT ENGINE ============
class EventEngine:
    @staticmethod
    def trigger(event_type: str) -> Dict[str, float]:
        """Trigger event with deterministic portfolio impacts."""
        events = {
            "sovereign_downgrade": {
                "label": "Sovereign Downgrade",
                "dscr_multiplier": 0.90,
                "pd_delta": 0.04,
                "revenue_multiplier": 0.95,
                "cost_multiplier": 1.05,
                "capex_multiplier": 1.00,
                "coupon_delta": 0.01,
                "description": "Country credit rating downgrade raises funding costs.",
                "severity": "HIGH",
                "duration": 4,
            },
            "inflation_shock": {
                "label": "📈 Inflation Spike",
                "dscr_multiplier": 0.94,
                "pd_delta": 0.02,
                "revenue_multiplier": 0.98,
                "cost_multiplier": 1.08,
                "capex_multiplier": 1.02,
                "coupon_delta": 0.00,
                "description": "Input costs rise faster than revenue escalation.",
                "severity": "MEDIUM",
                "duration": 2,
            },
            "construction_delay": {
                "label": "🏗️ Construction Delay",
                "dscr_multiplier": 0.88,
                "pd_delta": 0.03,
                "revenue_multiplier": 0.90,
                "cost_multiplier": 1.10,
                "capex_multiplier": 1.05,
                "coupon_delta": 0.00,
                "description": "Schedule slippage reduces near-term cashflows.",
                "severity": "HIGH",
                "duration": 5,
            },
            "revenue_collapse": {
                "label": "📉 Revenue Collapse",
                "dscr_multiplier": 0.75,
                "pd_delta": 0.08,
                "revenue_multiplier": 0.60,
                "cost_multiplier": 1.05,
                "capex_multiplier": 1.00,
                "coupon_delta": 0.00,
                "description": "Demand shock cuts revenues materially.",
                "severity": "CRITICAL",
                "duration": 6,
            },
            "refinancing_crisis": {
                "label": "💰 Refinancing Crisis",
                "dscr_multiplier": 0.82,
                "pd_delta": 0.06,
                "revenue_multiplier": 0.98,
                "cost_multiplier": 1.02,
                "capex_multiplier": 1.00,
                "coupon_delta": 0.02,
                "description": "Refinancing at higher spreads erodes coverage.",
                "severity": "HIGH",
                "duration": 3,
            },
            "climate_event": {
                "label": "🌊 Climate Event",
                "dscr_multiplier": 0.92,
                "pd_delta": 0.025,
                "revenue_multiplier": 0.93,
                "cost_multiplier": 1.12,
                "capex_multiplier": 1.08,
                "coupon_delta": 0.00,
                "description": "Extreme weather increases capex and downtime.",
                "severity": "MEDIUM",
                "duration": 2,
            },
        }
        return events.get(event_type, events["inflation_shock"])


def trigger_event(evt_type: str, state: Dict) -> None:
    """Apply an event shock and keep the UI action code in one place."""
    event = EventEngine.trigger(evt_type)
    st.session_state.last_event = event

    updated_df = apply_event_to_portfolio(state["portfolio_df"], event)
    if state.get("contract"):
        updated_df = apply_contract_adjustment(updated_df, state["contract"]["risk_score"])
    state["portfolio_df"] = updated_df
    state["events"].append({
        "type": evt_type,
        "timestamp": datetime.now().isoformat(),
        "impact": event,
    })


# ============ MAIN APP ============
def main():
    # Header
    st.markdown("# 🏗️ InfraRisk AI Lab")
    st.markdown("**Infrastructure Finance Platform with AI-Powered Risk Intelligence**")
    
    # Sidebar
    st.sidebar.title("⚙️ Portfolio Setup")
    portfolio_name = st.sidebar.text_input("Portfolio Name", value="Infrastructure Fund 2026")

    data = load_real_data()
    ppi_df = data["ppi"]
    wdi_df = data["wdi"]
    cds_df = data["cds"]
    nbi_df = data["nbi"]

    if ppi_df.empty:
        st.warning("Real PPI dataset not found. Expected data/raw/ppi/ppi_projects.csv.")

    available_sectors = sorted(ppi_df["sector"].dropna().unique()) if not ppi_df.empty else []
    available_countries = sorted(ppi_df["country"].dropna().unique()) if not ppi_df.empty else []

    num_projects = st.sidebar.slider("Projects in Portfolio", min_value=4, max_value=15, value=8)
    sector_filter = st.sidebar.multiselect("Sector Filter", available_sectors, default=available_sectors[:3])
    country_filter = st.sidebar.multiselect("Country Filter", available_countries, default=available_countries[:3])
    rebuild = st.sidebar.button("🔄 Rebuild Portfolio")

    settings = {
        "num_projects": num_projects,
        "sectors": sector_filter,
        "countries": country_filter,
    }

    if "portfolio_state" not in st.session_state or rebuild or st.session_state.portfolio_state.get("settings") != settings:
        portfolio_df = build_portfolio_df(
            ppi_df=ppi_df,
            wdi_df=wdi_df,
            cds_df=cds_df,
            num_projects=num_projects,
            sectors=sector_filter,
            countries=country_filter,
        )
        st.session_state.portfolio_state = {
            "settings": settings,
            "portfolio_df": portfolio_df,
            "events": [],
            "contract": None,
        }

    state = st.session_state.portfolio_state
    portfolio_df = state["portfolio_df"]
    summary = portfolio_summary(portfolio_df)
    
    # Tabs
    tabs = st.tabs([
        "📊 Dashboard",
        "🛰️ Satellite & CNN",
        "📋 Contract Intelligence",
        "🎲 Events & Simulation",
        "📈 Forecasts",
        "🕸️ Contagion",
        "💾 State Management"
    ])
    
    # ============ TAB 1: DASHBOARD ============
    with tabs[0]:
        st.subheader("Portfolio Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💼 Portfolio Value", f"${summary['value']/1e9:.1f}B", f"{summary['projects']} projects")
        with col2:
            st.metric("📊 Avg DSCR", f"{summary['avg_dscr']:.2f}x", "vs 1.5x min")
        with col3:
            st.metric("⚠️ Portfolio PD", f"{summary['avg_pd']*100:.1f}%", f"LLCR {summary['avg_llcr']:.2f}x")
        with col4:
            st.metric("🏦 Avg PLCR", f"{summary['avg_plcr']:.2f}x", "Debt headroom")
        
        st.divider()
        st.markdown("### 🤖 AI Model Outputs")
        
        ai_c1, ai_c2, ai_c3 = st.columns(3)
        sample_project = portfolio_df.iloc[0] if not portfolio_df.empty else None
        
        with ai_c1:
            st.markdown("**CNN Satellite Progress**")
            if sample_project is not None:
                cnn = AIModels.cnn_satellite(sample_project)
                st.metric("Progress", f"{cnn['progress']:.0f}%", f"Conf: {cnn['confidence']*100:.0f}%")
                if cnn['anomaly']:
                    st.warning(f"⚠️ {cnn['anomaly_type']}")
                else:
                    st.success("No anomalies")
            else:
                st.info("No projects loaded.")
        
        with ai_c2:
            st.markdown("**Financial Health (Realistic)**")
            if sample_project is not None:
                st.metric("DSCR", f"{sample_project['dscr']:.2f}x", f"Leverage: {sample_project['leverage']:.1f}x")
                if sample_project["covenant_breach"]:
                    st.error("🚨 Covenant Risk")
                else:
                    st.success("Covenants OK")
            else:
                st.info("No financial metrics available.")
        
        with ai_c3:
            st.markdown("**GNN Contagion Score**")
            gnn = AIModels.gnn_contagion(portfolio_df)
            st.metric("Systemic Risk", gnn["systemic_risk"], f"Score: {gnn['propagation_score']:.0f}")
        
        st.divider()
        
        # Sector breakdown
        st.markdown("#### Sector Exposure")
        if not portfolio_df.empty:
            exposure = (
                portfolio_df.groupby("sector_group")["capex_m"].sum().sort_values(ascending=False)
            )
            fig = go.Figure(data=[go.Pie(labels=exposure.index, values=exposure.values)])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sector exposure unavailable.")
        
        # DSCR forecast
        st.markdown("#### Multi-Horizon Forecast (TFT)")
        if sample_project is not None:
            macro = {
                "gdp_growth": sample_project["macro_gdp_growth"],
                "inflation": sample_project["macro_inflation"],
                "cds_5y_bps": sample_project["macro_cds_bps"],
            }
            tft = AIModels.tft_forecasts(sample_project["dscr"], macro, quarters=12)
        else:
            tft = pd.DataFrame({"Quarter": [], "DSCR": [], "Upper_95": [], "Lower_5": []})
        
        fig_tft = go.Figure()
        fig_tft.add_trace(go.Scatter(x=tft['Quarter'], y=tft['DSCR'], mode='lines+markers', name='Forecast', line=dict(color='#667eea')))
        fig_tft.add_trace(go.Scatter(x=tft['Quarter'], y=tft['Upper_95'], fill=None, mode='lines', line=dict(width=0), name='95% Upper'))
        fig_tft.add_trace(go.Scatter(x=tft['Quarter'], y=tft['Lower_5'], fill='tonexty', mode='lines', line=dict(width=0), name='5% Lower'))
        fig_tft.add_hline(y=1.2, line_dash="dash", line_color="red", annotation_text="Min Covenant 1.2x")
        fig_tft.update_layout(height=300, hovermode='x')
        st.plotly_chart(fig_tft, use_container_width=True)
        st.caption("Why this happened: forecasts adjust DSCR using GDP growth, inflation drag, and sovereign spread headwinds.")
        st.caption("Recommended action: rebalance toward higher-DSCR sectors or extend tenor where coverage is tight.")

        if sample_project is not None:
            st.markdown("#### Debt Structure & Waterfall")
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                st.metric("DSRA", f"${sample_project['reserve_account_m']:.1f}M")
            with dc2:
                st.metric("Refinancing Risk", sample_project["refinancing_risk"])
            with dc3:
                st.metric("Covenant", "BREACH" if sample_project["covenant_breach"] else "OK")

            with st.expander("Cashflow Waterfall (Annualized)"):
                waterfall_df = pd.DataFrame(
                    sample_project["waterfall"].items(),
                    columns=["Stage", "Value (USD M)"],
                )
                st.dataframe(waterfall_df, use_container_width=True)

            with st.expander("Debt Amortization Snapshot"):
                annual_payment = amortization_payment(
                    sample_project["debt_m"], sample_project["coupon_rate"], sample_project["tenor_years"]
                )
                schedule = []
                balance = sample_project["debt_m"]
                for year in range(1, 6):
                    interest = balance * sample_project["coupon_rate"]
                    principal = max(0.0, annual_payment - interest)
                    balance = max(0.0, balance - principal)
                    schedule.append({
                        "Year": year,
                        "Payment (USD M)": annual_payment,
                        "Interest (USD M)": interest,
                        "Principal (USD M)": principal,
                        "Balance (USD M)": balance,
                    })
                st.dataframe(pd.DataFrame(schedule), use_container_width=True)
    
    # ============ TAB 2: SATELLITE ============
    with tabs[1]:
        st.subheader("🛰️ Satellite & CNN Construction Tracking")
        if portfolio_df.empty:
            st.info("Load portfolio data to view satellite outputs.")
        else:
            project = st.selectbox("Select Project", portfolio_df["project_name"].tolist())
            project_row = portfolio_df[portfolio_df["project_name"] == project].iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                cnn = AIModels.cnn_satellite(project_row)
                st.markdown(f"### Progress: **{cnn['progress']:.0f}%**")
                st.progress(int(cnn["progress"]) / 100)
                st.write(f"Confidence: {cnn['confidence']*100:.0f}%")
                st.write(f"Images Captured: {cnn['images_captured']}")
                if cnn["anomaly"]:
                    st.error(f"🚨 ANOMALY: {cnn['anomaly_type']}")
                else:
                    st.success("All systems normal")

                st.markdown("**Anomaly Signal**: Progress vs. DSCR deviation and status flags.")

            with col2:
                timeline = build_satellite_timeline(project_row)
                fig_timeline = go.Figure()
                fig_timeline.add_trace(go.Scatter(
                    x=timeline["Date"],
                    y=timeline["Progress"] * 100,
                    mode="lines+markers",
                    fill="tozeroy",
                ))
                fig_timeline.update_layout(
                    title="Construction Progress Timeline",
                    xaxis_title="Date",
                    yaxis_title="Progress %",
                    height=300,
                )
                st.plotly_chart(fig_timeline, use_container_width=True)

            st.markdown("### Sample Satellite Tiles")
            tile_cols = st.columns(3)
            for idx, col in enumerate(tile_cols):
                with col:
                    heat = np.outer(np.linspace(0, 1, 20), np.linspace(0, 1, 20)) * (0.7 + idx * 0.1)
                    fig_tile = px.imshow(heat, color_continuous_scale="Greens")
                    fig_tile.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig_tile, use_container_width=True)
                    st.caption(f"Quarter {idx + 1}: {project_row['sector_group']} site")
    
    # ============ TAB 3: CONTRACTS ============
    with tabs[2]:
        st.subheader("📋 Contract Intelligence & NLP Analysis")
        
        st.markdown("### PDF Upload & Clause Analysis")
        uploaded = st.file_uploader("Upload contract PDF", type=['pdf'], key='contract')

        analyze_sample = st.button("Analyze Sample Contract")
        if uploaded or analyze_sample:
            contract_text = extract_pdf_text(uploaded) if uploaded else SAMPLE_CONTRACT_TEXT
            analysis = analyze_contract_text(contract_text)

            clause_count = sum(1 for c in analysis["clauses"].values() if c["found"])
            high_risk = analysis["high_risk"]
            benchmark = analysis["benchmark"]

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Clauses Found", clause_count)
            with c2:
                st.metric("High-Risk", len(high_risk))
            with c3:
                st.metric("Risk Score", f"{analysis['risk_score']}", f"{benchmark['percentile']:.0f}th %ile")
            with c4:
                st.metric("Recommendation", benchmark["recommendation"])

            st.divider()

            clause_table = []
            for clause_name, info in analysis["clauses"].items():
                clause_table.append({
                    "Clause": clause_name.replace("_", " ").title(),
                    "Category": info["category"],
                    "Found": "Yes" if info["found"] else "No",
                    "Risk Score": info["risk_score"],
                })
            st.markdown("#### Clause Extraction")
            st.dataframe(pd.DataFrame(clause_table), use_container_width=True)

            st.markdown("#### High-Risk Clause Highlights")
            if high_risk:
                for risk in high_risk:
                    st.warning(f"• {risk.replace('_', ' ').title()}")
            else:
                st.success("No high-risk clauses detected.")

            st.markdown("#### Recommended Actions")
            for rec in analysis["recommendations"]:
                st.write(f"- {rec}")

            if uploaded:
                save_contract_upload(uploaded.name, contract_text, analysis)

            state["contract"] = analysis
            state["portfolio_df"] = apply_contract_adjustment(state["portfolio_df"], analysis["risk_score"])
            adjusted = portfolio_summary(state["portfolio_df"])
            st.info(f"Contract risk applied → Avg DSCR {adjusted['avg_dscr']:.2f}x, Avg PD {adjusted['avg_pd']*100:.1f}%")
    
    # ============ TAB 4: EVENTS ============
    with tabs[3]:
        st.subheader("🎲 Event Simulation & Crisis Scenarios")
        
        col1, col2, col3 = st.columns(3)
        
        event_types = [
            ('sovereign_downgrade', '📉'),
            ('inflation_shock', '📈'),
            ('construction_delay', '🏗️'),
            ('revenue_collapse', '💸'),
            ('refinancing_crisis', '💰'),
            ('climate_event', '🌊')
        ]
        event_button_labels = {
            "sovereign_downgrade": "Apply Sovereign Downgrade",
            "inflation_shock": "Apply Inflation Spike",
            "construction_delay": "Apply Construction Delay",
            "revenue_collapse": "Apply Revenue Collapse",
            "refinancing_crisis": "Apply Refinancing Crisis",
            "climate_event": "Apply Climate Event",
        }
        
        for (evt_type, emoji), col in zip(event_types[:3], [col1, col2, col3]):
            with col:
                if st.button(f"{emoji} {event_button_labels[evt_type]}", key=f"btn_{evt_type}", use_container_width=True):
                    event = EventEngine.trigger(evt_type)
                    st.session_state.last_event = event

                    updated_df = apply_event_to_portfolio(state["portfolio_df"], event)
                    if state.get("contract"):
                        updated_df = apply_contract_adjustment(updated_df, state["contract"]["risk_score"])
                    state["portfolio_df"] = updated_df
                    state["events"].append({
                        "type": evt_type,
                        "timestamp": datetime.now().isoformat(),
                        "impact": event,
                    })
                event_preview = EventEngine.trigger(evt_type)
                st.caption(
                    f"{event_preview['severity']} | ~{event_preview['duration']} qtrs | "
                    f"PD +{event_preview['pd_delta']*100:.1f}%"
                )

        col4, col5, col6 = st.columns(3)
        for (evt_type, emoji), col in zip(event_types[3:], [col4, col5, col6]):
            with col:
                if st.button(f"{emoji} {event_button_labels[evt_type]}", key=f"btn_{evt_type}", use_container_width=True):
                    event = EventEngine.trigger(evt_type)
                    st.session_state.last_event = event

                    updated_df = apply_event_to_portfolio(state["portfolio_df"], event)
                    if state.get("contract"):
                        updated_df = apply_contract_adjustment(updated_df, state["contract"]["risk_score"])
                    state["portfolio_df"] = updated_df
                    state["events"].append({
                        "type": evt_type,
                        "timestamp": datetime.now().isoformat(),
                        "impact": event,
                    })
                event_preview = EventEngine.trigger(evt_type)
                st.caption(
                    f"{event_preview['severity']} | ~{event_preview['duration']} qtrs | "
                    f"PD +{event_preview['pd_delta']*100:.1f}%"
                )
        
        st.divider()
        
        if 'last_event' in st.session_state:
            evt = st.session_state.last_event
            st.markdown(f"### {evt['label']}")
            st.write(f"{evt['description']} | Severity: **{evt['severity']}** | Duration: ~{evt['duration']} quarters")
            
            impactc1, impactc2 = st.columns(2)
            with impactc1:
                new_summary = portfolio_summary(state["portfolio_df"])
                st.metric("New Avg DSCR", f"{new_summary['avg_dscr']:.2f}x", delta_color="inverse")
                if new_summary["avg_dscr"] < 1.2:
                    st.error("⚠️ Below covenant!")
            with impactc2:
                st.metric("New Avg PD", f"{new_summary['avg_pd']*100:.1f}%", f"+{evt['pd_delta']*100:.1f}%")
            st.caption("Why this happened: event shocks apply directly to revenue, costs, and funding spreads.")
            st.caption("Recommended action: build liquidity reserves and reprice risk for exposed sectors.")
        
        st.divider()
        
        st.markdown("### Monte Carlo Stress Test (10K Scenarios)")
        if st.button("Run Simulation"):
            stress = FinancialEngine.stress_test(portfolio_summary(state["portfolio_df"])["avg_dscr"])
            
            fig_mc = go.Figure()
            fig_mc.add_histogram(x=stress['distribution'], nbinsx=50, name='DSCR Distribution')
            fig_mc.add_vline(x=1.2, line_dash="dash", line_color="red", annotation_text="Min 1.2x")
            fig_mc.update_layout(title="DSCR Distribution (10K Scenarios)", xaxis_title="DSCR", yaxis_title="Count")
            st.plotly_chart(fig_mc, use_container_width=True)

            st.warning(f"**Covenant Breach Probability**: {stress['breach_pct']:.1f}%")
            st.write(f"VaR (95%): {stress['var_95']:.2f}x | CVaR (95%): {stress['cvar_95']:.2f}x")
    
    # ============ TAB 5: FORECASTS ============
    with tabs[4]:
        st.subheader("📈 Forecast Center - AI Predictions")
        
        fc1, fc2 = st.columns(2)
        if portfolio_df.empty:
            st.info("Forecasts require portfolio data.")
        else:
            sample_project = portfolio_df.iloc[0]
            macro = {
                "gdp_growth": sample_project["macro_gdp_growth"],
                "inflation": sample_project["macro_inflation"],
                "cds_5y_bps": sample_project["macro_cds_bps"],
            }
            forecast = forecast_dscr_pd(sample_project["dscr"], sample_project["pd"], macro, 12)
        if portfolio_df.empty:
            forecast = pd.DataFrame({"Quarter": [], "DSCR": [], "PD": []})
        
        with fc1:
            st.markdown("#### DSCR Forecast (TFT)")
            tft = AIModels.tft_forecasts(sample_project["dscr"], macro, 12) if not portfolio_df.empty else pd.DataFrame()
            fig_dscr = go.Figure()
            tft_x = tft["Quarter"] if not tft.empty and "Quarter" in tft.columns else list(range(1, len(tft) + 1))
            tft_y = tft["DSCR"] if not tft.empty and "DSCR" in tft.columns else []
            fig_dscr.add_trace(go.Scatter(x=tft_x, y=tft_y, mode='lines+markers', line=dict(color='#667eea')))
            fig_dscr.add_hline(y=1.2, line_dash="dash", line_color="red")
            st.plotly_chart(fig_dscr, use_container_width=True)
        
        with fc2:
            st.markdown("#### Default Probability Forecast")
            pd_fcast = forecast["PD"] if not portfolio_df.empty else []
            fig_pd = go.Figure()
            pd_x = forecast["Quarter"] if not forecast.empty and "Quarter" in forecast.columns else list(range(1, len(forecast) + 1))
            fig_pd.add_trace(go.Scatter(x=pd_x, y=pd_fcast*100, mode='lines+markers', line=dict(color='#ff6b6b')))
            st.plotly_chart(fig_pd, use_container_width=True)
            if not portfolio_df.empty:
                st.caption("Why this happened: PD increases with widening CDS spreads and lower DSCR.")
                st.caption("Recommended action: improve covenant headroom or add credit enhancement.")
        
        st.divider()
        
        st.markdown("#### Infrastructure Degradation (PINN)")
        asset = st.radio("Asset Type", ['Bridge', 'Pavement'])
        pinn = AIModels.pinn_degradation(asset.lower(), nbi_df)
        
        pc1, pc2 = st.columns(2)
        with pc1:
            st.metric("Current Condition", f"{pinn['current']:.0f}/100", f"→ {pinn['projected_5yr']:.0f}/100 in 5yr")
        with pc2:
            st.metric("Maintenance Urgency", pinn['urgency'], f"Failure in ~{pinn['failure_years']:.0f} years")

        if not portfolio_df.empty:
            st.markdown("#### Stress Scenario Assumptions")
            st.write(f"Macro baseline: GDP {macro['gdp_growth']:.1f}%, Inflation {macro['inflation']:.1f}%, CDS {macro['cds_5y_bps']:.0f} bps.")
            st.write("Model uses macro headwinds to adjust DSCR and PD trajectories.")
    
    # ============ TAB 6: CONTAGION ============
    with tabs[5]:
        st.subheader("🕸️ Portfolio Contagion (GNN Analysis)")
        if portfolio_df.empty:
            st.info("Load portfolio data to view contagion.")
        else:
            gnn = AIModels.gnn_contagion(portfolio_df)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Direct Impact", gnn['direct'], "projects")
            with c2:
                st.metric("Indirect Impact", gnn['indirect'], "projects")
            with c3:
                st.metric("Propagation Score", f"{gnn['propagation_score']:.0f}", "/100")
            with c4:
                if gnn['systemic_risk'] == 'HIGH':
                    st.error(f"🔴 {gnn['systemic_risk']}")
                else:
                    st.warning(f"🟡 {gnn['systemic_risk']}")
            
            st.divider()
            
            st.markdown("### Network Graph")
            fig_net = build_network_figure(portfolio_df)
            st.plotly_chart(fig_net, use_container_width=True)
            st.caption("Why this happened: shared sector/country exposure creates correlated stress transmission paths.")
            st.caption("Recommended action: diversify away from concentrated country/sector clusters.")
    
    # ============ TAB 7: STATE MANAGEMENT ============
    with tabs[6]:
        st.subheader("💾 Portfolio Persistence")
        
        sc1, sc2 = st.columns(2)
        
        with sc1:
            st.markdown("### Save State")
            version_label = st.text_input("Version Label", value="Q1-2026-Baseline")
            if st.button("💾 Save Portfolio"):
                save_portfolio_snapshot(
                    version_label,
                    state["portfolio_df"],
                    state["events"],
                    state.get("contract"),
                )
                st.success(f"✅ Saved: {version_label}")
        
        with sc2:
            st.markdown("### Load State")
            versions = list_portfolio_snapshots()
            selected = st.selectbox("Select version", versions if versions else ["No saved versions"])
            if st.button("📂 Load"):
                if versions:
                    loaded = load_portfolio_snapshot(selected)
                    if loaded:
                        state["portfolio_df"] = loaded["portfolio_df"]
                        state["events"] = loaded["events"]
                        state["contract"] = loaded["contract"]
                        st.success(f"Loaded: {selected}")
    
    # Sidebar status
    st.sidebar.divider()
    st.sidebar.markdown("### 📊 Session Status")
    st.sidebar.write(f"**Portfolio**: {portfolio_name}")
    st.sidebar.write(f"**Projects**: {summary['projects']}")
    st.sidebar.write(f"**Avg DSCR**: {summary['avg_dscr']:.2f}x")
    st.sidebar.write(f"**Avg PD**: {summary['avg_pd']*100:.1f}%")
    st.sidebar.write(f"**Events**: {len(state['events'])}")

if __name__ == "__main__":
    main()

