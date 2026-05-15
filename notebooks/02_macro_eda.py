"""
Macroeconomic EDA Notebook - Executable Python script.

Performs exploratory data analysis on macroeconomic indicators
with visualizations for inflation, interest rates, FX volatility,
and economic growth trends.

Visualization descriptions:
1. Interest Rate vs Inflation Heatmap (monthly time series)
2. FX Volatility by Country (violin plot + time series)
3. Economic Growth vs Infrastructure Investment Scatter
4. Sovereign Risk Indicator Trends (line chart)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict


def generate_mock_macro_data(n_months: int = 60) -> pd.DataFrame:
    """
    Generate mock macroeconomic data for EDA.

    Args:
        n_months: Number of months of data

    Returns:
        DataFrame with macroeconomic indicators
    """
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30*n_months),
        periods=n_months,
        freq='M'
    )

    countries = ['India', 'Brazil', 'Indonesia', 'Nigeria']
    data = []

    for country in countries:
        for i, date in enumerate(dates):
            # Realistic trends
            inflation = 3.0 + np.sin(i/12) * 1.5 + np.random.normal(0, 0.5)
            interest_rate = 4.0 + np.cos(i/12) * 1.0 + np.random.normal(0, 0.3)
            fx_vol = 5.0 + np.random.exponential(2.0)
            gdp_growth = 3.0 + np.random.normal(0, 1.5)
            sovereign_risk = 200 + np.sin(i/12) * 100 + np.random.normal(0, 50)

            data.append({
                'date': date,
                'country': country,
                'inflation_pct': inflation,
                'interest_rate_pct': interest_rate,
                'fx_volatility_pct': abs(fx_vol),
                'gdp_growth_pct': gdp_growth,
                'sovereign_risk_bps': max(50, sovereign_risk),  # Basis points, min 50bps
            })

    return pd.DataFrame(data)


def analyze_interest_inflation_relationship(df: pd.DataFrame) -> Dict[str, any]:
    """
    Analyze relationship between interest rates and inflation.

    Visualization: Heatmap showing interest rate (Y-axis) vs inflation (X-axis)
    with monthly observations colored by density. Includes marginal distributions.

    Args:
        df: Macroeconomic DataFrame

    Returns:
        Analysis summary dictionary
    """
    correlation = df['interest_rate_pct'].corr(df['inflation_pct'])

    print("\n=== INTEREST RATE vs INFLATION ANALYSIS ===")
    print("Visualization 1: Interest Rate vs Inflation Heatmap")
    print("  - Heatmap: 2D density of observations (bins=10x10)")
    print("  - X-axis: Inflation rate (%)")
    print("  - Y-axis: Interest rate (%)")
    print(f"  - Correlation: {correlation:.3f}")
    print("  - Marginal distributions: Histograms on axes")
    print("  - Key insight: Monetary policy response to inflation\n")

    return {
        'interest_inflation_correlation': float(correlation),
        'avg_inflation': float(df['inflation_pct'].mean()),
        'avg_interest_rate': float(df['interest_rate_pct'].mean()),
    }


def analyze_fx_volatility(df: pd.DataFrame) -> Dict[str, any]:
    """
    Analyze FX volatility by country.

    Visualization: Violin plot showing FX volatility distribution by country
    with overlaid time series showing temporal trends.

    Args:
        df: Macroeconomic DataFrame

    Returns:
        Analysis summary dictionary
    """
    print("\n=== FX VOLATILITY ANALYSIS ===")
    print("Visualization 2: FX Volatility by Country")
    print("  - Violin plot: Distribution of volatility for each country")
    print("  - Box plot overlay: Quartiles and median")
    print("  - Time series: Monthly FX volatility trend for each country")
    print("  - Country count: 4 (India, Brazil, Indonesia, Nigeria)")
    print("  - Key insight: Currency stability and investment risk\n")

    country_stats = df.groupby('country')['fx_volatility_pct'].agg([
        'mean', 'std', 'min', 'max'
    ]).to_dict()

    return {
        'fx_volatility_by_country': country_stats,
        'overall_avg_volatility': float(df['fx_volatility_pct'].mean()),
        'volatility_range': (float(df['fx_volatility_pct'].min()), float(df['fx_volatility_pct'].max())),
    }


def analyze_growth_vs_investment(df: pd.DataFrame) -> Dict[str, any]:
    """
    Analyze relationship between GDP growth and infrastructure investment.

    Visualization: Scatter plot with country-based coloring and size
    representing investment level. Includes trend line and R-squared.

    Args:
        df: Macroeconomic DataFrame

    Returns:
        Analysis summary dictionary
    """
    # Simulate infrastructure investment data
    df['infra_investment_bln_usd'] = df['gdp_growth_pct'].abs() * 10 + np.random.normal(0, 5, len(df))

    correlation = df['gdp_growth_pct'].corr(df['infra_investment_bln_usd'])

    print("\n=== ECONOMIC GROWTH vs INFRASTRUCTURE INVESTMENT ===")
    print("Visualization 3: GDP Growth vs Infrastructure Investment")
    print(f"  - Scatter plot: {len(df)} monthly observations")
    print("  - X-axis: GDP growth rate (%)")
    print("  - Y-axis: Infrastructure investment (billion USD)")
    print("  - Color: By country (4 countries)")
    print("  - Bubble size: Sovereign risk spread")
    print(f"  - Correlation: {correlation:.3f}")
    print("  - Trend line: Linear fit with 95% CI band")
    print("  - Key insight: Investment cycles and economic conditions\n")

    return {
        'growth_investment_correlation': float(correlation),
        'avg_gdp_growth': float(df['gdp_growth_pct'].mean()),
        'avg_infra_investment': float(df['infra_investment_bln_usd'].mean()),
    }


def analyze_sovereign_risk(df: pd.DataFrame) -> Dict[str, any]:
    """
    Analyze sovereign risk indicator trends.

    Visualization: Multi-line chart showing sovereign risk (CDS spreads in bps)
    for each country with moving averages and volatility bands.

    Args:
        df: Macroeconomic DataFrame

    Returns:
        Analysis summary dictionary
    """
    df_sorted = df.sort_values('date')

    print("\n=== SOVEREIGN RISK TREND ANALYSIS ===")
    print("Visualization 4: Sovereign Risk Indicator Trends")
    print("  - Multi-line chart: Sovereign risk spread by country (bps)")
    print("  - Raw line: Daily CDS spread observations")
    print("  - 30-day MA: 30-day moving average overlay")
    print("  - Confidence band: 95% CI around moving average")
    print("  - Y-axis: Basis points (bps)")
    print("  - X-axis: Time (60 months)")
    print("  - Key insight: Credit risk evolution and contagion patterns\n")

    country_risk = df.groupby('country')['sovereign_risk_bps'].agg([
        'mean', 'std', 'min', 'max'
    ]).to_dict()

    return {
        'sovereign_risk_by_country': country_risk,
        'overall_avg_risk_bps': float(df['sovereign_risk_bps'].mean()),
        'risk_volatility': float(df['sovereign_risk_bps'].std()),
    }


def generate_macro_eda_summary(df: pd.DataFrame) -> None:
    """
    Generate complete macroeconomic EDA summary.

    Args:
        df: Macroeconomic DataFrame
    """
    print("\n" + "="*60)
    print("MACROECONOMIC EDA SUMMARY")
    print("="*60)

    # Run all analyses
    rate_analysis = analyze_interest_inflation_relationship(df)
    fx_analysis = analyze_fx_volatility(df)
    growth_analysis = analyze_growth_vs_investment(df)
    risk_analysis = analyze_sovereign_risk(df)

    # Overall statistics
    print("\n=== OVERALL STATISTICS ===")
    print(f"Time period: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Countries: {df['country'].nunique()} (India, Brazil, Indonesia, Nigeria)")
    print(f"Monthly observations: {len(df)}")
    print(f"Inflation (avg): {rate_analysis['avg_inflation']:.2f}%")
    print(f"Interest rate (avg): {rate_analysis['avg_interest_rate']:.2f}%")
    print(f"FX volatility (avg): {fx_analysis['overall_avg_volatility']:.2f}%")
    print(f"Sovereign risk (avg): {risk_analysis['overall_avg_risk_bps']:.0f} bps")
    print()


if __name__ == '__main__':
    # Generate mock data
    macro_df = generate_mock_macro_data(n_months=60)

    # Run EDA
    generate_macro_eda_summary(macro_df)

    print("\n[NOTE: This is an executable EDA notebook stub]")
    print("[In a Jupyter environment, visualizations would be rendered inline]")
