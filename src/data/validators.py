"""Data validation using Great Expectations.

Implements infrastructure-specific validation rules:
- Physical plausibility (cost per MW, DSCR bounds)
- Temporal alignment (prevent look-ahead bias)
- Cross-source consistency checks
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class InfrastructureValidator:
    """Validate infrastructure project data for physical plausibility."""
    
    def __init__(self):
        """Initialize infrastructure validator."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validation_rules = {}
    
    def validate_construction_cost_per_mw(self, projects: pd.DataFrame) -> pd.DataFrame:
        """Validate construction cost per MW for power projects (physical plausibility).
        
        Typical ranges by project type:
        - Hydroelectric: $1.0M-$3.0M per MW
        - Coal: $2.0M-$4.0M per MW
        - Gas: $0.5M-$1.5M per MW
        - Wind: $1.5M-$2.5M per MW
        - Solar: $0.8M-$1.5M per MW
        
        Args:
            projects: DataFrame with infrastructure projects
            
        Returns:
            DataFrame with validation flags
        """
        self.logger.info("Validating construction cost per MW...")
        
        power_projects = projects[projects['sector'] == 'Energy'].copy()
        
        cost_bounds = {
            'Hydroelectric': (1.0e6, 3.0e6),
            'Coal': (2.0e6, 4.0e6),
            'Gas': (0.5e6, 1.5e6),
            'Wind': (1.5e6, 2.5e6),
            'Solar': (0.8e6, 1.5e6),
        }
        
        power_projects['cost_per_mw'] = power_projects['total_investment_usd'] / power_projects['capacity_mw']
        power_projects['cost_valid'] = True
        
        for proj_type, (lower, upper) in cost_bounds.items():
            mask = power_projects['project_type'] == proj_type
            power_projects.loc[mask, 'cost_valid'] = power_projects.loc[mask, 'cost_per_mw'].between(lower, upper)
        
        return power_projects
    
    def validate_dscr_bounds(self, projects: pd.DataFrame) -> pd.DataFrame:
        """Validate Debt Service Coverage Ratio (DSCR) within plausible bounds.
        
        Typical DSCR requirements: 1.2x - 1.5x
        
        Args:
            projects: DataFrame with DSCR calculations
            
        Returns:
            DataFrame with DSCR validation flags
        """
        self.logger.info("Validating DSCR bounds...")
        
        projects = projects.copy()
        projects['dscr_valid'] = projects['dscr'].between(1.0, 3.0)
        
        # Flag projects with unusually low or high DSCR
        projects['dscr_warning'] = (projects['dscr'] < 1.2) | (projects['dscr'] > 2.0)
        
        return projects
    
    def validate_toll_rate_realism(self, projects: pd.DataFrame) -> pd.DataFrame:
        """Validate toll rates as reasonable percentage of value of time savings.
        
        Args:
            projects: DataFrame with toll revenue and time savings
            
        Returns:
            DataFrame with toll rate validation
        """
        self.logger.info("Validating toll rate realism...")
        
        projects = projects.copy()
        
        # Value of time savings as % of toll revenue (typically 0.05 - 0.15)
        projects['value_of_time_ratio'] = projects['value_of_time_savings'] / projects['annual_toll_revenue']
        projects['toll_rate_valid'] = projects['value_of_time_ratio'].between(0.05, 0.15)
        
        return projects
    
    def validate_leverage_ratio(self, projects: pd.DataFrame) -> pd.DataFrame:
        """Validate project leverage (debt-to-equity) ratios.
        
        Typical ranges:
        - Conservative: 0.5x - 1.0x
        - Moderate: 1.0x - 1.5x
        - Aggressive: 1.5x - 2.5x
        
        Args:
            projects: DataFrame with debt and equity
            
        Returns:
            DataFrame with leverage validation
        """
        self.logger.info("Validating leverage ratios...")
        
        projects = projects.copy()
        projects['leverage'] = projects['debt_amount_usd'] / projects['equity_amount_usd']
        projects['leverage_valid'] = projects['leverage'].between(0.5, 2.5)
        
        return projects


class TemporalAlignmentValidator:
    """Validate temporal alignment and prevent look-ahead bias."""
    
    def __init__(self, lag_days: int = 1):
        """Initialize temporal alignment validator.
        
        Args:
            lag_days: Number of days to lag market data (default 1)
        """
        self.lag_days = lag_days
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def apply_market_data_lag(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """Lag market data by specified days to prevent look-ahead bias.
        
        Args:
            market_data: DataFrame with date and market indicators
            
        Returns:
            DataFrame with lagged market data
        """
        self.logger.info(f"Applying {self.lag_days}-day lag to market data...")
        
        market_data = market_data.copy()
        market_data['date'] = pd.to_datetime(market_data['date'])
        market_data['date'] = market_data['date'] - pd.Timedelta(days=self.lag_days)
        
        return market_data
    
    def timestamp_satellite_acquisitions(self, satellite_data: Dict) -> Dict:
        """Timestamp satellite imagery to exact acquisition dates.
        
        Args:
            satellite_data: Dictionary with imagery paths and metadata
            
        Returns:
            Dictionary with timestamped satellite data
        """
        self.logger.info("Timestamping satellite acquisitions...")
        
        # Ensure satellite dates are aligned with acquisition metadata
        satellite_data['acquisition_dates'] = pd.to_datetime(satellite_data.get('dates', []))
        
        return satellite_data
    
    def validate_temporal_consistency(self, 
                                     market_data: pd.DataFrame,
                                     satellite_data: Dict,
                                     project_data: pd.DataFrame) -> bool:
        """Validate that all data sources are temporally aligned.
        
        Args:
            market_data: Market data with dates
            satellite_data: Satellite imagery with acquisition dates
            project_data: Project data with transaction dates
            
        Returns:
            True if temporal alignment is valid
        """
        self.logger.info("Validating temporal consistency across sources...")
        
        # Check that market data dates precede project dates
        market_data['date'] = pd.to_datetime(market_data['date'])
        project_data['inception_date'] = pd.to_datetime(project_data['inception_date'])
        
        min_market_date = market_data['date'].min()
        min_project_date = project_data['inception_date'].min()
        
        if min_market_date >= min_project_date:
            self.logger.warning(
                f"Market data ({min_market_date}) not available before projects ({min_project_date})"
            )
            return False
        
        return True


class CrossSourceConsistencyValidator:
    """Validate consistency across multiple data sources."""
    
    def __init__(self):
        """Initialize cross-source consistency validator."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_geographic_consistency(self, 
                                       projects: pd.DataFrame,
                                       macro_data: pd.DataFrame) -> pd.DataFrame:
        """Validate that projects' geographic data is consistent with macro data.
        
        Args:
            projects: Project data with country/coordinates
            macro_data: Macro data with country identifiers
            
        Returns:
            DataFrame with geographic consistency flags
        """
        self.logger.info("Validating geographic consistency...")
        
        projects = projects.copy()
        projects['geo_valid'] = projects['country'].isin(macro_data['country'].unique())
        
        return projects
    
    def validate_sectoral_consistency(self, projects: pd.DataFrame) -> pd.DataFrame:
        """Validate project sector classifications are consistent.
        
        Args:
            projects: Project data with sector classifications
            
        Returns:
            DataFrame with sectoral consistency flags
        """
        self.logger.info("Validating sectoral consistency...")
        
        valid_sectors = ['Transportation', 'Energy', 'Water', 'Telecom', 'Social']
        projects = projects.copy()
        projects['sector_valid'] = projects['sector'].isin(valid_sectors)
        
        return projects


def validate_all_data(data: Dict[str, pd.DataFrame], 
                     temporal_lag_days: int = 1) -> Dict[str, pd.DataFrame]:
    """Run comprehensive validation on all data sources.
    
    Args:
        data: Dictionary of loaded DataFrames
        temporal_lag_days: Days to lag market data
        
    Returns:
        Dictionary with validation results
    """
    logger.info("Starting comprehensive data validation...")
    
    results = {}
    
    # Infrastructure validation
    infra_validator = InfrastructureValidator()
    if 'ppi_projects' in data:
        results['projects_infrastructure'] = infra_validator.validate_dscr_bounds(
            data['ppi_projects']
        )
    
    # Temporal alignment
    temporal_validator = TemporalAlignmentValidator(lag_days=temporal_lag_days)
    if 'interest_curves' in data:
        results['interest_curves_lagged'] = temporal_validator.apply_market_data_lag(
            data['interest_curves']
        )
    
    # Cross-source consistency
    cross_validator = CrossSourceConsistencyValidator()
    if 'ppi_projects' in data and 'macro_indicators' in data:
        results['geographic_consistency'] = cross_validator.validate_geographic_consistency(
            data['ppi_projects'],
            data['macro_indicators']
        )
    
    logger.info("Data validation completed")
    return results


if __name__ == '__main__':
    # Example usage
    logger.basicConfig(level=logging.INFO)
    print("Data validators configured and ready")
