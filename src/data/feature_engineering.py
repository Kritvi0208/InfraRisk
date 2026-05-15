"""Feature engineering for multi-modal infrastructure data.

Creates financial, geospatial, macroeconomic, and climate-adjusted features.
Integrates with Feast feature store for versioned, documented serving.
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class FinancialFeatureEngineer:
    """Engineer project-level financial features."""
    
    def __init__(self):
        """Initialize financial feature engineer."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_dscr(self, annual_net_cash_flow: np.ndarray, 
                      annual_debt_service: np.ndarray) -> np.ndarray:
        """Calculate Debt Service Coverage Ratio (DSCR).
        
        DSCR = Annual Net Cash Flow / Annual Debt Service
        Typical threshold: 1.2x - 1.5x
        
        Args:
            annual_net_cash_flow: Array of annual net cash flows
            annual_debt_service: Array of annual debt service payments
            
        Returns:
            Array of DSCR values
        """
        return annual_net_cash_flow / annual_debt_service
    
    def calculate_llcr(self, total_cash_flow_lcoe: np.ndarray,
                      total_debt_service: np.ndarray) -> np.ndarray:
        """Calculate Loan Life Coverage Ratio (LLCR).
        
        LLCR = PV of total cash flow / PV of total debt service
        Typical threshold: 1.2x - 1.5x
        
        Args:
            total_cash_flow_lcoe: PV of cash flows over loan life
            total_debt_service: PV of total debt service
            
        Returns:
            Array of LLCR values
        """
        return total_cash_flow_lcoe / total_debt_service
    
    def calculate_plcr(self, total_cash_flow_project_life: np.ndarray,
                      total_debt_service: np.ndarray) -> np.ndarray:
        """Calculate Project Life Coverage Ratio (PLCR).
        
        PLCR = PV of total cash flow over project life / PV of total debt service
        
        Args:
            total_cash_flow_project_life: PV of cash flows over project life
            total_debt_service: PV of total debt service
            
        Returns:
            Array of PLCR values
        """
        return total_cash_flow_project_life / total_debt_service
    
    def engineer_financial_features(self, projects: pd.DataFrame) -> pd.DataFrame:
        """Engineer all financial features for projects.
        
        Args:
            projects: DataFrame with financial data
            
        Returns:
            DataFrame with engineered financial features
        """
        self.logger.info(f"Engineering financial features for {len(projects)} projects...")
        
        features = projects.copy()
        
        # Leverage ratios
        features['debt_to_equity'] = features['debt_amount_usd'] / features['equity_amount_usd']
        features['debt_to_total_cap'] = features['debt_amount_usd'] / (
            features['debt_amount_usd'] + features['equity_amount_usd']
        )
        
        # Coverage ratios (placeholder - would need actual cash flow data)
        features['interest_coverage'] = features['ebitda'] / features['interest_expense']
        
        # Return metrics
        features['roi'] = features['annual_net_cash_flow'] / features['total_investment_usd']
        features['equity_irr_target'] = 0.12  # Placeholder
        
        # Profitability
        features['profit_margin'] = features['net_income'] / features['revenue']
        
        return features


class GeospatialFeatureEngineer:
    """Engineer geospatial features from satellite imagery and maps."""
    
    def __init__(self):
        """Initialize geospatial feature engineer."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_ndvi(self, nir_band: np.ndarray, red_band: np.ndarray) -> np.ndarray:
        """Calculate Normalized Difference Vegetation Index (NDVI).
        
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            nir_band: Near-infrared band values
            red_band: Red band values
            
        Returns:
            NDVI values (range -1 to 1)
        """
        return (nir_band - red_band) / (nir_band + red_band + 1e-8)
    
    def calculate_ndbi(self, swir_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """Calculate Normalized Difference Built-up Index (NDBI).
        
        NDBI = (SWIR - NIR) / (SWIR + NIR)
        
        Args:
            swir_band: Shortwave infrared band
            nir_band: Near-infrared band
            
        Returns:
            NDBI values (detects built-up areas)
        """
        return (swir_band - nir_band) / (swir_band + nir_band + 1e-8)
    
    def calculate_construction_progress(self, 
                                       ndbi_baseline: np.ndarray,
                                       ndbi_current: np.ndarray) -> np.ndarray:
        """Estimate construction progress from NDBI change detection.
        
        Construction progress (%) = (NDBI_current - NDBI_baseline) / Max_Change * 100
        
        Args:
            ndbi_baseline: Baseline NDBI before construction
            ndbi_current: Current NDBI
            
        Returns:
            Construction progress as percentage
        """
        max_ndbi_change = 1.0  # Max possible change
        progress = ((ndbi_current - ndbi_baseline) / max_ndbi_change) * 100
        return np.clip(progress, 0, 100)
    
    def detect_anomalies(self, ndbi_timeseries: np.ndarray, 
                        threshold: float = 2.0) -> np.ndarray:
        """Detect anomalies: site abandonment, equipment removal.
        
        Uses statistical anomaly detection (z-score > threshold).
        
        Args:
            ndbi_timeseries: Time series of NDBI values
            threshold: Z-score threshold for anomaly (default 2.0)
            
        Returns:
            Binary array indicating anomalies
        """
        mean = np.mean(ndbi_timeseries)
        std = np.std(ndbi_timeseries)
        z_scores = np.abs((ndbi_timeseries - mean) / (std + 1e-8))
        return (z_scores > threshold).astype(int)
    
    def engineer_geospatial_features(self, projects: pd.DataFrame,
                                     satellite_data: Dict) -> pd.DataFrame:
        """Engineer geospatial features from satellite data.
        
        Args:
            projects: DataFrame with project locations
            satellite_data: Dictionary with satellite imagery
            
        Returns:
            DataFrame with geospatial features
        """
        self.logger.info(f"Engineering geospatial features for {len(projects)} projects...")
        
        features = projects.copy()
        
        # Placeholder - would integrate actual satellite data
        features['ndvi_change'] = 0.0
        features['ndbi_change'] = 0.0
        features['construction_progress_pct'] = 0.0
        features['site_anomaly_detected'] = 0
        
        return features


class MacroeconomicFeatureEngineer:
    """Engineer macroeconomic features for sovereign and systemic risk."""
    
    def __init__(self):
        """Initialize macro feature engineer."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_sovereign_risk_composite(self, 
                                          macro_indicators: pd.DataFrame) -> pd.Series:
        """Calculate sovereign risk composite score.
        
        Combines World Bank governance indicators:
        - Government Effectiveness (20%)
        - Rule of Law (20%)
        - Control of Corruption (15%)
        - Political Stability (10%)
        - Regulatory Quality (20%)
        - Voice & Accountability (15%)
        
        Args:
            macro_indicators: DataFrame with governance indicators
            
        Returns:
            Series with sovereign risk scores (0-100)
        """
        weights = {
            'govt_effectiveness': 0.20,
            'rule_of_law': 0.20,
            'control_of_corruption': 0.15,
            'political_stability': 0.10,
            'regulatory_quality': 0.20,
            'voice_accountability': 0.15,
        }
        
        # Normalize indicators to 0-100 scale
        composite = pd.Series(0.0, index=macro_indicators.index)
        for indicator, weight in weights.items():
            if indicator in macro_indicators.columns:
                normalized = ((macro_indicators[indicator] + 2.5) / 5.0) * 100
                composite += normalized * weight
        
        return composite
    
    def calculate_fiscal_stress_index(self, macro_indicators: pd.DataFrame) -> pd.Series:
        """Calculate fiscal stress index from macro variables.
        
        Combines:
        - Debt-to-GDP ratio
        - Fiscal deficit-to-GDP
        - Interest payments-to-revenue
        
        Args:
            macro_indicators: DataFrame with fiscal data
            
        Returns:
            Series with fiscal stress scores
        """
        stress = pd.Series(0.0, index=macro_indicators.index)
        
        if 'debt_to_gdp' in macro_indicators.columns:
            stress += (macro_indicators['debt_to_gdp'] / 100) * 0.4
        if 'fiscal_deficit_to_gdp' in macro_indicators.columns:
            stress += (abs(macro_indicators['fiscal_deficit_to_gdp']) / 10) * 0.3
        if 'interest_to_revenue' in macro_indicators.columns:
            stress += (macro_indicators['interest_to_revenue'] / 50) * 0.3
        
        return stress.clip(0, 1)  # Normalize to 0-1
    
    def engineer_macro_features(self, macro_data: pd.DataFrame) -> pd.DataFrame:
        """Engineer macroeconomic features.
        
        Args:
            macro_data: DataFrame with macro indicators
            
        Returns:
            DataFrame with engineered macro features
        """
        self.logger.info(f"Engineering macro features for {len(macro_data)} records...")
        
        features = macro_data.copy()
        
        # Sovereign risk
        features['sovereign_risk_score'] = self.calculate_sovereign_risk_composite(macro_data)
        
        # Fiscal stress
        features['fiscal_stress_index'] = self.calculate_fiscal_stress_index(macro_data)
        
        # External vulnerability
        features['external_vulnerability_score'] = 0.5  # Placeholder
        
        return features


class ClimateAdjustedFeatureEngineer:
    """Engineer climate-adjusted features (CA-RUL, CA-DSCR)."""
    
    def __init__(self, ipcc_scenario: str = 'rcp45'):
        """Initialize climate feature engineer.
        
        Args:
            ipcc_scenario: IPCC warming scenario (rcp45, rcp85, etc.)
        """
        self.ipcc_scenario = ipcc_scenario
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_ca_rul(self, baseline_rul: np.ndarray,
                        temperature_increase: np.ndarray,
                        precipitation_change: np.ndarray) -> np.ndarray:
        """Calculate Climate-Adjusted Remaining Useful Life.
        
        CA-RUL = Baseline RUL * Degradation Multiplier
        
        Degradation accelerates with:
        - Temperature increase (for pavement, bridges)
        - Precipitation extremes (for water infrastructure)
        
        Args:
            baseline_rul: Baseline RUL in years
            temperature_increase: Temperature change (°C)
            precipitation_change: Precipitation change (%)
            
        Returns:
            Climate-adjusted RUL in years
        """
        # Temperature impact: ~2-4% additional degradation per °C
        temp_factor = 1.0 - (temperature_increase * 0.03)
        
        # Precipitation impact: extremes accelerate degradation
        precip_factor = 1.0 - (abs(precipitation_change) * 0.01)
        
        ca_rul = baseline_rul * temp_factor * precip_factor
        
        return np.maximum(ca_rul, 0)  # RUL cannot be negative
    
    def calculate_ca_dscr(self, baseline_dscr: np.ndarray,
                         construction_delay_pct: np.ndarray) -> np.ndarray:
        """Calculate Construction-Adjusted DSCR.
        
        CA-DSCR accounts for satellite-observed construction delays.
        
        Args:
            baseline_dscr: Baseline DSCR
            construction_delay_pct: Construction delay (% of original schedule)
            
        Returns:
            Construction-adjusted DSCR
        """
        # Delays reduce revenue (later opening) and increase costs (extended financing)
        revenue_reduction = construction_delay_pct * 0.002  # 0.2% per 1% delay
        cost_increase = construction_delay_pct * 0.001  # 0.1% per 1% delay
        
        ca_dscr = baseline_dscr * (1 - revenue_reduction - cost_increase)
        
        return ca_dscr


def engineer_all_features(projects: pd.DataFrame,
                         macro_data: pd.DataFrame,
                         satellite_data: Dict,
                         climate_scenario: str = 'rcp45') -> pd.DataFrame:
    """Engineer all features for projects.
    
    Args:
        projects: Project data
        macro_data: Macroeconomic indicators
        satellite_data: Satellite imagery
        climate_scenario: IPCC climate scenario
        
    Returns:
        DataFrame with all engineered features
    """
    logger.info("Engineering all features...")
    
    features = projects.copy()
    
    # Financial features
    fin_engineer = FinancialFeatureEngineer()
    fin_features = fin_engineer.engineer_financial_features(features)
    
    # Geospatial features
    geo_engineer = GeospatialFeatureEngineer()
    geo_features = geo_engineer.engineer_geospatial_features(fin_features, satellite_data)
    
    # Macro features
    macro_engineer = MacroeconomicFeatureEngineer()
    macro_features_df = macro_engineer.engineer_macro_features(macro_data)
    
    # Merge macro features to project data (by country)
    geo_features = geo_features.merge(
        macro_features_df[['country', 'sovereign_risk_score', 'fiscal_stress_index']],
        on='country',
        how='left'
    )
    
    # Climate-adjusted features
    climate_engineer = ClimateAdjustedFeatureEngineer(ipcc_scenario=climate_scenario)
    geo_features['ca_rul'] = climate_engineer.calculate_ca_rul(
        baseline_rul=geo_features.get('baseline_rul', 30.0).values,
        temperature_increase=np.array([2.0] * len(geo_features)),  # Placeholder
        precipitation_change=np.array([5.0] * len(geo_features))
    )
    
    logger.info(f"Feature engineering completed: {len(geo_features.columns)} features")
    
    return geo_features


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("Feature engineering modules configured")
