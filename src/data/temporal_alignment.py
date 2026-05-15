"""
Temporal alignment module for market data and satellite observations.

Implements 1-day market data lag protocol to prevent look-ahead bias
and tracks satellite timestamp accuracy for cross-source alignment.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class DataSource(str, Enum):
    """Data source types with their typical update lag."""
    MARKET = "market"  # 1-day lag
    SATELLITE = "satellite"  # Variable lag, tracked
    WEATHER = "weather"  # 1-hour lag
    ECONOMIC = "economic"  # 1-week lag
    GEOSPATIAL = "geospatial"  # Real-time


@dataclass
class TemporalMetadata:
    """Metadata for temporal alignment of a data point."""
    observation_date: datetime
    data_date: datetime  # Actual date the data represents
    source_date: datetime  # When data was published/recorded
    source_type: DataSource
    lag_days: float
    satellite_confidence: float = 1.0  # For satellite data accuracy (0-1)
    look_ahead_bias_risk: bool = False


class TemporalAligner:
    """Align temporal data across multiple sources with lag protocol."""

    # Standard data lags by source (in days)
    STANDARD_LAGS = {
        DataSource.MARKET: 1.0,        # Market data 1 day behind
        DataSource.SATELLITE: 0.5,     # Satellite 12 hours typical
        DataSource.WEATHER: 0.04,      # Weather 1 hour
        DataSource.ECONOMIC: 7.0,      # Economic data weekly
        DataSource.GEOSPATIAL: 0.0,    # Geospatial real-time
    }

    # Satellite data quality by type
    SATELLITE_CONFIDENCE = {
        'optical': 0.85,              # Optical imagery
        'sar': 0.90,                  # Synthetic Aperture Radar (all-weather)
        'thermal': 0.75,              # Thermal imagery
        'multispectral': 0.88,        # Multispectral
        'hyperspectral': 0.92,        # Hyperspectral
    }

    def __init__(self):
        """Initialize temporal aligner."""
        self.alignment_log: List[TemporalMetadata] = []
        self.misalignments: List[Tuple[str, str, float]] = []  # source1, source2, lag_diff

    def apply_market_lag(
        self,
        reference_date: datetime,
        days_ahead: int = 1
    ) -> datetime:
        """
        Apply 1-day market data lag protocol.

        Ensures market data used on day T represents data from day T-1,
        preventing look-ahead bias.

        Args:
            reference_date: Current analysis date
            days_ahead: Market lag in days (default 1)

        Returns:
            Date to use for market data lookups
        """
        market_date = reference_date - timedelta(days=days_ahead)
        return market_date

    def track_satellite_timestamp(
        self,
        satellite_date: datetime,
        observation_date: datetime,
        satellite_type: str = 'optical',
        quality_flag: str = 'good'
    ) -> TemporalMetadata:
        """
        Track satellite data timestamp and confidence.

        Args:
            satellite_date: Date of satellite observation
            observation_date: Date when satellite image was acquired
            satellite_type: Type of satellite data (optical, SAR, thermal, etc.)
            quality_flag: Data quality assessment

        Returns:
            TemporalMetadata with tracking information
        """
        lag = (observation_date - satellite_date).total_seconds() / 86400.0
        confidence = self.SATELLITE_CONFIDENCE.get(satellite_type, 0.80)

        # Adjust confidence based on quality
        if quality_flag == 'poor':
            confidence *= 0.7
        elif quality_flag == 'degraded':
            confidence *= 0.85

        metadata = TemporalMetadata(
            observation_date=observation_date,
            data_date=satellite_date,
            source_date=observation_date,
            source_type=DataSource.SATELLITE,
            lag_days=lag,
            satellite_confidence=confidence,
            look_ahead_bias_risk=False
        )

        self.alignment_log.append(metadata)
        return metadata

    def align_to_market_protocol(
        self,
        df: pd.DataFrame,
        date_column: str,
        reference_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Align DataFrame to 1-day market lag protocol.

        Args:
            df: DataFrame with temporal data
            date_column: Column name containing dates
            reference_date: Reference date for alignment (default today)

        Returns:
            DataFrame with lag-adjusted dates
        """
        if reference_date is None:
            reference_date = datetime.now()

        df_aligned = df.copy()
        df_aligned['market_lag_date'] = pd.to_datetime(
            df_aligned[date_column]
        ) - timedelta(days=1)
        df_aligned['original_date'] = df_aligned[date_column]
        df_aligned[date_column] = df_aligned['market_lag_date']

        return df_aligned.drop(columns=['market_lag_date'])

    def detect_misalignment(
        self,
        source1_dates: pd.Series,
        source2_dates: pd.Series,
        source1_name: str,
        source2_name: str,
        tolerance_days: float = 1.0
    ) -> List[Tuple[int, float]]:
        """
        Detect temporal misalignment between two data sources.

        Args:
            source1_dates: Date series from first source
            source2_dates: Date series from second source
            source1_name: Name of first source
            source2_name: Name of second source
            tolerance_days: Tolerance for acceptable lag (default 1 day)

        Returns:
            List of (index, lag_days) for misaligned records
        """
        misaligned = []
        s1 = pd.to_datetime(source1_dates)
        s2 = pd.to_datetime(source2_dates)

        lag_days = (s1 - s2).dt.total_seconds() / 86400.0
        misaligned_mask = np.abs(lag_days) > tolerance_days
        misaligned_indices = np.where(misaligned_mask)[0]

        for idx in misaligned_indices:
            misaligned.append((int(idx), float(lag_days.iloc[idx])))
            self.misalignments.append(
                (source1_name, source2_name, float(lag_days.iloc[idx]))
            )

        return misaligned

    def create_time_window(
        self,
        start_date: datetime,
        end_date: datetime,
        market_lag_days: int = 1,
        satellite_confidence_min: float = 0.8
    ) -> Dict[str, datetime]:
        """
        Create aligned time window across all data sources.

        Args:
            start_date: Window start date
            end_date: Window end date
            market_lag_days: Market data lag in days
            satellite_confidence_min: Minimum satellite confidence threshold

        Returns:
            Dictionary with aligned dates for each source
        """
        return {
            'market_data': start_date - timedelta(days=market_lag_days),
            'market_data_end': end_date - timedelta(days=market_lag_days),
            'satellite_data': start_date,
            'satellite_data_end': end_date,
            'weather_data': start_date,
            'weather_data_end': end_date,
            'economic_data': start_date - timedelta(days=7),
            'economic_data_end': end_date - timedelta(days=7),
            'geospatial_data': start_date,
            'geospatial_data_end': end_date,
        }

    def validate_temporal_consistency(
        self,
        data_dict: Dict[str, pd.DataFrame],
        date_column: str = 'date',
        max_lag_days: float = 1.0
    ) -> Tuple[bool, List[str]]:
        """
        Validate temporal consistency across multiple data sources.

        Args:
            data_dict: Dictionary of DataFrames from different sources
            date_column: Column name for dates
            max_lag_days: Maximum acceptable lag between sources

        Returns:
            Tuple of (is_consistent, list of issues)
        """
        issues = []
        sources = list(data_dict.keys())

        for i, source1 in enumerate(sources):
            for source2 in sources[i+1:]:
                df1 = data_dict[source1]
                df2 = data_dict[source2]

                if len(df1) == 0 or len(df2) == 0:
                    continue

                misaligned = self.detect_misalignment(
                    df1[date_column],
                    df2[date_column],
                    source1,
                    source2,
                    tolerance_days=max_lag_days
                )

                if misaligned:
                    issues.append(
                        f"{source1} and {source2}: {len(misaligned)} misaligned records"
                    )

        return len(issues) == 0, issues

    def get_alignment_report(self) -> Dict[str, any]:
        """
        Generate temporal alignment report.

        Returns:
            Dictionary with alignment statistics
        """
        if not self.alignment_log:
            return {'status': 'No alignment data collected'}

        lags = [log.lag_days for log in self.alignment_log]
        confidences = [log.satellite_confidence for log in self.alignment_log]

        return {
            'total_records': len(self.alignment_log),
            'look_ahead_bias_risk': sum(
                1 for log in self.alignment_log if log.look_ahead_bias_risk
            ),
            'avg_lag_days': float(np.mean(lags)),
            'max_lag_days': float(np.max(lags)),
            'avg_satellite_confidence': float(np.mean(confidences)),
            'misalignments_detected': len(self.misalignments),
        }
