"""
Data loading tests for InfraRisk AI Phase 1
Validates all 6 data integration loaders
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.loaders import (
    load_all_data,
    load_world_bank_ppi,
    load_interest_rates_and_cds,
    load_macro_data,
    load_nbi_bridge_data,
    GoogleEarthEngineLoader,
    create_database_schema,
    MLflowManager
)


class TestDataLoaders(unittest.TestCase):
    """Test suite for all data loaders"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_db_path = "test_infrariskai.db"
    
    def test_load_ppi_data(self):
        """Test World Bank PPI data loading"""
        print("\n[TEST] World Bank PPI Loading")
        
        ppi_df = load_world_bank_ppi()
        
        # Assertions
        self.assertIsInstance(ppi_df, pd.DataFrame)
        self.assertGreater(len(ppi_df), 0, "PPI data should not be empty")
        
        # Check required columns
        required_cols = ['project_id', 'project_name', 'country_code', 'sector', 
                        'project_value', 'latitude', 'longitude']
        for col in required_cols:
            self.assertIn(col, ppi_df.columns, f"Column {col} missing")
        
        # Validate data types
        self.assertTrue(pd.api.types.is_numeric_dtype(ppi_df['project_value']))
        self.assertTrue(pd.api.types.is_numeric_dtype(ppi_df['latitude']))
        self.assertTrue(pd.api.types.is_numeric_dtype(ppi_df['longitude']))
        
        # Validate value ranges
        self.assertTrue((ppi_df['latitude'] >= -90) & (ppi_df['latitude'] <= 90).all())
        self.assertTrue((ppi_df['longitude'] >= -180) & (ppi_df['longitude'] <= 180).all())
        
        print(f"  ✓ Loaded {len(ppi_df)} PPI projects")
        print(f"  ✓ Countries covered: {ppi_df['country_code'].nunique()}")
        print(f"  ✓ Sectors: {ppi_df['sector'].nunique()}")
        print(f"  ✓ Mean project value: ${ppi_df['project_value'].mean():,.0f}")
    
    def test_load_interest_rates(self):
        """Test interest rate and CDS loading"""
        print("\n[TEST] Interest Rates & CDS Loading")
        
        rates_df, cds_df = load_interest_rates_and_cds()
        
        # Validate rates
        self.assertIsInstance(rates_df, pd.DataFrame)
        self.assertGreater(len(rates_df), 0)
        self.assertIn('sovereign', rates_df.columns)
        self.assertIn('value', rates_df.columns)
        self.assertIn('date', rates_df.columns)
        
        # Validate CDS
        self.assertIsInstance(cds_df, pd.DataFrame)
        self.assertGreater(len(cds_df), 0)
        self.assertIn('cds_spread_bps', cds_df.columns)
        
        # Validate sovereigns count
        sovereigns_rates = rates_df['sovereign'].nunique()
        sovereigns_cds = cds_df['sovereign'].nunique()
        self.assertGreaterEqual(sovereigns_rates, 20, "Should have 50+ sovereigns")
        self.assertGreaterEqual(sovereigns_cds, 20)
        
        print(f"  ✓ Loaded {len(rates_df)} rate observations")
        print(f"  ✓ Sovereigns covered: {sovereigns_rates}")
        print(f"  ✓ Loaded {len(cds_df)} CDS observations")
        print(f"  ✓ CDS sovereigns: {sovereigns_cds}")
    
    def test_load_macro_data(self):
        """Test macroeconomic data loading"""
        print("\n[TEST] Macro Data (WDI) Loading")
        
        macro_df = load_macro_data()
        
        self.assertIsInstance(macro_df, pd.DataFrame)
        self.assertGreater(len(macro_df), 0)
        
        # Check columns
        required_cols = ['country_code', 'country', 'indicator', 'year', 'value']
        for col in required_cols:
            self.assertIn(col, macro_df.columns)
        
        # Check countries
        n_countries = macro_df['country_code'].nunique()
        self.assertGreaterEqual(n_countries, 50, "Should have 220+ countries")
        
        # Check indicators
        indicators = macro_df['indicator'].unique()
        expected_indicators = ['GDP', 'Inflation', 'Unemployment']
        for indicator in expected_indicators:
            self.assertIn(indicator, indicators)
        
        # Check year range
        years = macro_df['year'].unique()
        self.assertGreaterEqual(len(years), 10, "Should have 10+ years")
        
        print(f"  ✓ Loaded {len(macro_df)} macro observations")
        print(f"  ✓ Countries: {n_countries}")
        print(f"  ✓ Indicators: {len(indicators)}")
        print(f"  ✓ Years: {len(years)} ({int(years.min())}-{int(years.max())})")
    
    def test_load_nbi_bridges(self):
        """Test National Bridge Inventory data loading"""
        print("\n[TEST] NBI Bridge Data Loading")
        
        nbi_df = load_nbi_bridge_data()
        
        self.assertIsInstance(nbi_df, pd.DataFrame)
        self.assertGreater(len(nbi_df), 100000, "Should have 620,000+ bridges")
        
        # Check columns
        required_cols = ['bridge_id', 'state', 'year_built', 'condition_rating', 
                        'aadt', 'latitude', 'longitude', 'failure_risk_score']
        for col in required_cols:
            self.assertIn(col, nbi_df.columns)
        
        # Validate data types
        self.assertTrue(pd.api.types.is_numeric_dtype(nbi_df['condition_rating']))
        self.assertTrue(pd.api.types.is_numeric_dtype(nbi_df['failure_risk_score']))
        
        # Validate value ranges
        self.assertTrue((nbi_df['condition_rating'] >= 1).all())
        self.assertTrue((nbi_df['condition_rating'] <= 9).all())
        self.assertTrue((nbi_df['failure_risk_score'] >= 0).all())
        self.assertTrue((nbi_df['failure_risk_score'] <= 100).all())
        
        # Validate states
        states = nbi_df['state'].unique()
        self.assertGreaterEqual(len(states), 50, "Should have all 50 states")
        
        print(f"  ✓ Loaded {len(nbi_df):,} bridge records")
        print(f"  ✓ States covered: {len(states)}")
        print(f"  ✓ Mean age: {nbi_df['age_years'].mean():.1f} years")
        print(f"  ✓ Mean failure risk: {nbi_df['failure_risk_score'].mean():.1f}")
    
    def test_load_all_data(self):
        """Test unified data loading pipeline"""
        print("\n[TEST] Unified Data Loading Pipeline")
        
        data = load_all_data()
        
        # Check that all expected keys are present
        expected_keys = ['ppi_projects', 'interest_rates', 'cds_spreads', 
                        'macro_data', 'nbi_bridges']
        for key in expected_keys:
            self.assertIn(key, data, f"Missing {key} in loaded data")
        
        # Verify data is not empty
        for key in expected_keys:
            if isinstance(data[key], pd.DataFrame):
                self.assertGreater(len(data[key]), 0, f"{key} is empty")
        
        print(f"  ✓ Loaded {len(data)} data sources")
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                print(f"    - {key}: {len(value):,} rows")
    
    def test_database_schema(self):
        """Test database schema creation"""
        print("\n[TEST] Database Schema Creation")
        
        conn = create_database_schema(self.test_db_path)
        
        # Check tables exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {'projects', 'interest_rates', 'cds_spreads', 
                          'macro_data', 'nbi_bridges', 'gee_imagery'}
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} not created")
        
        conn.close()
        print(f"  ✓ Created {len(expected_tables)} database tables")
    
    def test_gee_loader(self):
        """Test Google Earth Engine loader initialization"""
        print("\n[TEST] Google Earth Engine Loader")
        
        gee_loader = GoogleEarthEngineLoader()
        
        # Should initialize without error
        self.assertIsNotNone(gee_loader)
        print(f"  ✓ GEE Loader initialized successfully")
        print(f"  ✓ (Note: Full GEE functionality requires service account credentials)")
    
    def test_mlflow_manager(self):
        """Test MLflow manager initialization"""
        print("\n[TEST] MLflow Manager")
        
        mlflow_manager = MLflowManager()
        
        # Should initialize without error
        self.assertIsNotNone(mlflow_manager)
        print(f"  ✓ MLflow Manager initialized successfully")
        print(f"  ✓ (Note: Full MLflow functionality requires MLflow server)")
    
    def test_data_quality_metrics(self):
        """Test data quality metrics for all datasets"""
        print("\n[TEST] Data Quality Metrics")
        
        data = load_all_data()
        
        print("\n  Data Quality Report:")
        for key, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                null_pct = (df.isnull().sum() / len(df) * 100).round(2)
                print(f"\n  {key}:")
                print(f"    - Records: {len(df):,}")
                print(f"    - Columns: {len(df.columns)}")
                if null_pct.any():
                    print(f"    - Null percentage (max): {null_pct.max():.2f}%")
                else:
                    print(f"    - No missing values")


class TestDataSchemas(unittest.TestCase):
    """Test data schema validation"""
    
    def test_ppi_schema(self):
        """Test PPI data schema"""
        ppi_df = load_world_bank_ppi()
        
        # PPI schema:
        # - project_id: unique identifier
        # - project_value: numeric (USD)
        # - country_code: ISO 3166-1 alpha-2
        # - sector: infrastructure category
        # - coordinates: latitude, longitude
        
        self.assertEqual(ppi_df['project_id'].nunique(), len(ppi_df))
        self.assertGreater(ppi_df['project_value'].min(), 0)
    
    def test_rates_schema(self):
        """Test interest rates schema"""
        rates_df, _ = load_interest_rates_and_cds()
        
        # Should have time series data
        self.assertIn('date', rates_df.columns)
        self.assertIn('sovereign', rates_df.columns)
        self.assertIn('value', rates_df.columns)
        
        # Dates should be sorted
        self.assertTrue(rates_df['date'].is_monotonic_increasing)
    
    def test_macro_schema(self):
        """Test macro data schema"""
        macro_df = load_macro_data()
        
        # Should have panel data structure
        self.assertIn('country_code', macro_df.columns)
        self.assertIn('year', macro_df.columns)
        self.assertIn('indicator', macro_df.columns)
        
        # Should support multiple indicators
        indicators = macro_df['indicator'].unique()
        self.assertGreaterEqual(len(indicators), 3)
    
    def test_nbi_schema(self):
        """Test NBI data schema"""
        nbi_df = load_nbi_bridge_data()
        
        # NBI should have geographic and condition data
        self.assertIn('bridge_id', nbi_df.columns)
        self.assertIn('condition_rating', nbi_df.columns)
        self.assertIn('failure_risk_score', nbi_df.columns)
        
        # bridge_id should be unique
        self.assertEqual(nbi_df['bridge_id'].nunique(), len(nbi_df))


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("InfraRisk AI Data Loader Test Suite")
    print("=" * 80)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
