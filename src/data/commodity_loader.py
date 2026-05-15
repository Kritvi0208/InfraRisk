"""
Commodity price loader with mock historical data.

This module provides realistic synthetic commodity pricing data for
gas, steel, cement, and oil over the last 10 years with trend fitting.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import json


class CommodityLoader:
    """Load and manage historical commodity price data."""

    # Mock base prices (2014-01-01 reference)
    BASE_PRICES = {
        'gas_usd_mmbtu': 4.5,      # USD per MMBtu
        'steel_usd_ton': 500.0,     # USD per metric ton
        'cement_usd_ton': 80.0,     # USD per metric ton
        'oil_usd_barrel': 95.0,     # USD per barrel
    }

    def __init__(self, start_year: int = 2014, end_year: int = 2024):
        """
        Initialize the commodity loader.

        Args:
            start_year: Start year for data generation (default 2014)
            end_year: End year for data generation (default 2024)
        """
        self.start_year = start_year
        self.end_year = end_year
        self.data: Dict[str, pd.DataFrame] = {}
        self._generate_mock_data()

    def _generate_mock_data(self) -> None:
        """Generate realistic mock commodity price data."""
        date_range = pd.date_range(
            start=f'{self.start_year}-01-01',
            end=f'{self.end_year}-12-31',
            freq='D'
        )

        for commodity, base_price in self.BASE_PRICES.items():
            prices = self._generate_commodity_prices(
                base_price, len(date_range), commodity
            )
            self.data[commodity] = pd.DataFrame({
                'date': date_range,
                'price': prices,
                'commodity': commodity,
            })

    def _generate_commodity_prices(
        self,
        base_price: float,
        num_days: int,
        commodity: str
    ) -> np.ndarray:
        """
        Generate realistic commodity price trends with volatility.

        Args:
            base_price: Starting price
            num_days: Number of days to generate
            commodity: Commodity type for variance adjustment

        Returns:
            Array of daily prices
        """
        # Volatility adjustment by commodity
        volatility_map = {
            'gas_usd_mmbtu': 0.35,
            'steel_usd_ton': 0.25,
            'cement_usd_ton': 0.15,
            'oil_usd_barrel': 0.40,
        }
        volatility = volatility_map.get(commodity, 0.25)

        # Trend components
        time_index = np.arange(num_days)
        years_elapsed = time_index / 365.25

        # Global trend (slight upward over 10 years)
        trend = base_price * (1 + 0.02 * years_elapsed)

        # Cyclical component (3-year business cycle)
        cycle = base_price * 0.15 * np.sin(2 * np.pi * years_elapsed / 3.0)

        # Seasonal component (annual seasonality)
        seasonality = base_price * 0.08 * np.sin(2 * np.pi * years_elapsed)

        # Random walk (Brownian motion)
        random_shocks = np.cumsum(
            np.random.normal(0, base_price * volatility / np.sqrt(252), num_days)
        )

        prices = trend + cycle + seasonality + random_shocks
        prices = np.maximum(prices, base_price * 0.3)  # Floor at 30% of base
        return prices

    def get_commodity_data(
        self,
        commodity: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve commodity price data for a specific commodity.

        Args:
            commodity: Commodity type (gas_usd_mmbtu, steel_usd_ton, etc.)
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)

        Returns:
            DataFrame with date and price columns

        Raises:
            ValueError: If commodity not found
        """
        if commodity not in self.data:
            raise ValueError(f"Commodity {commodity} not found")

        df = self.data[commodity].copy()

        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]

        return df.reset_index(drop=True)

    def get_all_commodities(self) -> Dict[str, pd.DataFrame]:
        """
        Get all commodity data.

        Returns:
            Dictionary mapping commodity names to DataFrames
        """
        return {k: v.copy() for k, v in self.data.items()}

    def fit_trend(self, commodity: str, days: int = 252) -> Tuple[float, float]:
        """
        Fit a simple linear trend to recent commodity prices.

        Args:
            commodity: Commodity type
            days: Number of recent days to fit (default 252 trading days)

        Returns:
            Tuple of (slope, intercept) for linear trend
        """
        if commodity not in self.data:
            raise ValueError(f"Commodity {commodity} not found")

        df = self.get_commodity_data(commodity).tail(days)
        x = np.arange(len(df))
        y = df['price'].values

        # Linear regression
        slope = np.polyfit(x, y, 1)[0]
        intercept = np.polyfit(x, y, 1)[1]

        return slope, intercept

    def get_price_stats(self, commodity: str) -> Dict[str, float]:
        """
        Calculate price statistics for a commodity.

        Args:
            commodity: Commodity type

        Returns:
            Dictionary with min, max, mean, std, cv
        """
        if commodity not in self.data:
            raise ValueError(f"Commodity {commodity} not found")

        prices = self.data[commodity]['price'].values
        return {
            'min': float(np.min(prices)),
            'max': float(np.max(prices)),
            'mean': float(np.mean(prices)),
            'median': float(np.median(prices)),
            'std': float(np.std(prices)),
            'cv': float(np.std(prices) / np.mean(prices)),  # Coefficient of variation
        }

    def export_csv(self, commodity: str, filepath: str) -> None:
        """
        Export commodity data to CSV.

        Args:
            commodity: Commodity type
            filepath: Output filepath
        """
        df = self.get_commodity_data(commodity)
        df.to_csv(filepath, index=False)

    def export_json(self, filepath: str) -> None:
        """
        Export all commodities to JSON.

        Args:
            filepath: Output filepath
        """
        export_data = {}
        for commodity, df in self.data.items():
            export_data[commodity] = {
                'dates': df['date'].dt.strftime('%Y-%m-%d').tolist(),
                'prices': df['price'].tolist(),
                'stats': self.get_price_stats(commodity),
            }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)


if __name__ == '__main__':
    # Example usage
    loader = CommodityLoader()

    # Print statistics for each commodity
    for commodity in ['gas_usd_mmbtu', 'steel_usd_ton', 'cement_usd_ton', 'oil_usd_barrel']:
        stats = loader.get_price_stats(commodity)
        print(f"\n{commodity}:")
        print(f"  Mean: ${stats['mean']:.2f}")
        print(f"  Std Dev: ${stats['std']:.2f}")
        print(f"  CV: {stats['cv']:.2f}")
        slope, intercept = loader.fit_trend(commodity)
        print(f"  Recent Trend: ${slope:.4f}/day")

    # Export example
    loader.export_json('commodity_data.json')
    print("\nData exported to commodity_data.json")
