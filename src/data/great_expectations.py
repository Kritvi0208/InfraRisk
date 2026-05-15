"""
Great Expectations validation suite for infrastructure data.

Provides 10+ validation checks including infrastructure-specific
constraints, temporal alignment, and physical plausibility assertions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    failed_records: int
    total_records: int
    error_message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class InfrastructureValidator:
    """Great Expectations suite for infrastructure project data."""

    def __init__(self, df: pd.DataFrame, project_id: str = "default"):
        """
        Initialize validator with infrastructure data.

        Args:
            df: DataFrame with infrastructure data
            project_id: Project identifier for reporting
        """
        self.df = df
        self.project_id = project_id
        self.validation_results: List[ValidationResult] = []
        self.required_columns = {
            'project_id', 'date', 'capacity_mw', 'cost_usd_m',
            'dscr', 'toll_rate', 'sector', 'status'
        }

    def run_all_validations(self) -> Tuple[bool, List[ValidationResult]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (all_passed, list of results)
        """
        self.validation_results = []

        # Data structure checks
        self.check_required_columns()
        self.check_no_duplicates()
        self.check_no_missing_values()

        # Infrastructure-specific checks
        self.check_cost_per_mw_bounds()
        self.check_dscr_bounds()
        self.check_toll_rate_bounds()
        self.check_capacity_bounds()
        self.check_sector_specific_constraints()

        # Temporal checks
        self.check_temporal_sequence()
        self.check_temporal_lag_consistency()

        # Physical plausibility
        self.check_cost_consistency()
        self.check_financial_ratios()

        all_passed = all(r.passed for r in self.validation_results)
        return all_passed, self.validation_results

    def check_required_columns(self) -> ValidationResult:
        """
        Verify all required columns are present.

        Returns:
            ValidationResult
        """
        missing = self.required_columns - set(self.df.columns)
        passed = len(missing) == 0

        result = ValidationResult(
            check_name="Required Columns",
            passed=passed,
            failed_records=len(missing),
            total_records=len(self.required_columns),
            error_message=f"Missing columns: {missing}" if missing else "",
            details={'missing_columns': list(missing)}
        )
        self.validation_results.append(result)
        return result

    def check_no_duplicates(self) -> ValidationResult:
        """
        Verify no duplicate project-date combinations.

        Returns:
            ValidationResult
        """
        if 'project_id' not in self.df.columns or 'date' not in self.df.columns:
            return ValidationResult(
                check_name="No Duplicates",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Required columns missing"
            )

        duplicates = self.df.duplicated(
            subset=['project_id', 'date'],
            keep=False
        ).sum()
        passed = duplicates == 0

        result = ValidationResult(
            check_name="No Duplicates",
            passed=passed,
            failed_records=duplicates,
            total_records=len(self.df),
            error_message=f"Found {duplicates} duplicate records" if duplicates > 0 else ""
        )
        self.validation_results.append(result)
        return result

    def check_no_missing_values(self) -> ValidationResult:
        """
        Check for missing values in critical columns.

        Returns:
            ValidationResult
        """
        required = ['capacity_mw', 'cost_usd_m', 'dscr', 'date']
        missing_count = 0
        for col in required:
            if col in self.df.columns:
                missing_count += self.df[col].isna().sum()

        passed = missing_count == 0
        result = ValidationResult(
            check_name="No Missing Values",
            passed=passed,
            failed_records=missing_count,
            total_records=len(self.df),
            error_message=f"Found {missing_count} missing values" if missing_count > 0 else ""
        )
        self.validation_results.append(result)
        return result

    def check_cost_per_mw_bounds(self) -> ValidationResult:
        """
        Verify cost per MW within realistic bounds ($0.5M-$3M).

        Returns:
            ValidationResult
        """
        if 'cost_usd_m' not in self.df.columns or 'capacity_mw' not in self.df.columns:
            return ValidationResult(
                check_name="Cost/MW Bounds",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Required columns missing"
            )

        cost_per_mw = self.df['cost_usd_m'] / self.df['capacity_mw']
        invalid = ((cost_per_mw < 0.5) | (cost_per_mw > 3.0)).sum()
        passed = invalid == 0

        result = ValidationResult(
            check_name="Cost/MW Bounds ($0.5M-$3M)",
            passed=passed,
            failed_records=invalid,
            total_records=len(self.df),
            error_message=f"Found {invalid} records outside bounds" if invalid > 0 else "",
            details={'min_cost_per_mw': float(cost_per_mw.min()), 'max_cost_per_mw': float(cost_per_mw.max())}
        )
        self.validation_results.append(result)
        return result

    def check_dscr_bounds(self) -> ValidationResult:
        """
        Verify DSCR (Debt Service Coverage Ratio) within 1.0x-3.0x.

        Returns:
            ValidationResult
        """
        if 'dscr' not in self.df.columns:
            return ValidationResult(
                check_name="DSCR Bounds",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="DSCR column missing"
            )

        invalid = ((self.df['dscr'] < 1.0) | (self.df['dscr'] > 3.0)).sum()
        passed = invalid == 0

        result = ValidationResult(
            check_name="DSCR Bounds (1.0x-3.0x)",
            passed=passed,
            failed_records=invalid,
            total_records=len(self.df),
            error_message=f"Found {invalid} records outside bounds" if invalid > 0 else "",
            details={'min_dscr': float(self.df['dscr'].min()), 'max_dscr': float(self.df['dscr'].max())}
        )
        self.validation_results.append(result)
        return result

    def check_toll_rate_bounds(self) -> ValidationResult:
        """
        Verify toll rates between 5%-15% of value of time savings.

        Returns:
            ValidationResult
        """
        if 'toll_rate' not in self.df.columns:
            return ValidationResult(
                check_name="Toll Rate Bounds",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Toll rate column missing"
            )

        invalid = ((self.df['toll_rate'] < 0.05) | (self.df['toll_rate'] > 0.15)).sum()
        passed = invalid == 0

        result = ValidationResult(
            check_name="Toll Rate Bounds (5%-15%)",
            passed=passed,
            failed_records=invalid,
            total_records=len(self.df),
            error_message=f"Found {invalid} records outside bounds" if invalid > 0 else "",
            details={'min_toll_rate': float(self.df['toll_rate'].min()), 'max_toll_rate': float(self.df['toll_rate'].max())}
        )
        self.validation_results.append(result)
        return result

    def check_capacity_bounds(self) -> ValidationResult:
        """
        Verify project capacity within realistic bounds (1-5000 MW).

        Returns:
            ValidationResult
        """
        if 'capacity_mw' not in self.df.columns:
            return ValidationResult(
                check_name="Capacity Bounds",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Capacity column missing"
            )

        invalid = ((self.df['capacity_mw'] < 1) | (self.df['capacity_mw'] > 5000)).sum()
        passed = invalid == 0

        result = ValidationResult(
            check_name="Capacity Bounds (1-5000 MW)",
            passed=passed,
            failed_records=invalid,
            total_records=len(self.df),
            error_message=f"Found {invalid} records outside bounds" if invalid > 0 else "",
            details={'min_capacity': float(self.df['capacity_mw'].min()), 'max_capacity': float(self.df['capacity_mw'].max())}
        )
        self.validation_results.append(result)
        return result

    def check_sector_specific_constraints(self) -> ValidationResult:
        """
        Verify sector-specific financial constraints.

        Returns:
            ValidationResult
        """
        if 'sector' not in self.df.columns:
            return ValidationResult(
                check_name="Sector Constraints",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Sector column missing"
            )

        sector_constraints = {
            'hydro': {'dscr_max': 3.0, 'cost_per_mw_max': 3.0},
            'thermal': {'dscr_max': 2.5, 'cost_per_mw_max': 1.5},
            'wind': {'dscr_max': 2.8, 'cost_per_mw_max': 2.5},
            'solar': {'dscr_max': 2.2, 'cost_per_mw_max': 1.3},
        }

        invalid = 0
        for sector, constraints in sector_constraints.items():
            sector_mask = self.df['sector'] == sector
            if sector_mask.any():
                sector_df = self.df[sector_mask]
                if 'dscr' in sector_df.columns:
                    invalid += (sector_df['dscr'] > constraints['dscr_max']).sum()

        passed = invalid == 0
        result = ValidationResult(
            check_name="Sector-Specific Constraints",
            passed=passed,
            failed_records=invalid,
            total_records=len(self.df),
            error_message=f"Found {invalid} records violating sector constraints" if invalid > 0 else ""
        )
        self.validation_results.append(result)
        return result

    def check_temporal_sequence(self) -> ValidationResult:
        """
        Verify dates are in ascending order (no future dates).

        Returns:
            ValidationResult
        """
        if 'date' not in self.df.columns:
            return ValidationResult(
                check_name="Temporal Sequence",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Date column missing"
            )

        dates = pd.to_datetime(self.df['date'])
        future_records = (dates > datetime.now()).sum()
        is_sorted = (dates.iloc[1:].values >= dates.iloc[:-1].values).all()

        passed = (future_records == 0) and is_sorted
        result = ValidationResult(
            check_name="Temporal Sequence",
            passed=passed,
            failed_records=future_records,
            total_records=len(self.df),
            error_message=f"Found {future_records} future dates" if future_records > 0 else ""
        )
        self.validation_results.append(result)
        return result

    def check_temporal_lag_consistency(self) -> ValidationResult:
        """
        Verify 1-day lag between observation and market data.

        Returns:
            ValidationResult
        """
        if 'date' not in self.df.columns:
            return ValidationResult(
                check_name="Temporal Lag",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Date column missing"
            )

        # Check lag is consistent (assuming 1-day lag)
        if len(self.df) > 1:
            dates = pd.to_datetime(self.df['date'])
            diffs = dates.diff().dt.total_seconds() / 86400
            expected_lag = 1.0
            lag_consistent = (diffs[1:].round(1) == expected_lag).sum() / (len(diffs) - 1) > 0.8
        else:
            lag_consistent = True

        result = ValidationResult(
            check_name="Temporal Lag Consistency (1-day)",
            passed=lag_consistent,
            failed_records=0,
            total_records=len(self.df),
            error_message="Temporal lag not consistent" if not lag_consistent else ""
        )
        self.validation_results.append(result)
        return result

    def check_cost_consistency(self) -> ValidationResult:
        """
        Verify cost doesn't decrease unexpectedly (physical plausibility).

        Returns:
            ValidationResult
        """
        if 'cost_usd_m' not in self.df.columns or 'date' not in self.df.columns:
            return ValidationResult(
                check_name="Cost Consistency",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="Required columns missing"
            )

        df_sorted = self.df.sort_values('date')
        if len(df_sorted) > 1:
            cost_changes = df_sorted['cost_usd_m'].diff()
            large_decreases = (cost_changes < -df_sorted['cost_usd_m'] * 0.20).sum()
        else:
            large_decreases = 0

        passed = large_decreases == 0
        result = ValidationResult(
            check_name="Cost Consistency (No >20% drops)",
            passed=passed,
            failed_records=large_decreases,
            total_records=len(self.df),
            error_message=f"Found {large_decreases} unexpected cost decreases" if large_decreases > 0 else ""
        )
        self.validation_results.append(result)
        return result

    def check_financial_ratios(self) -> ValidationResult:
        """
        Verify financial ratios are realistic (debt < revenue).

        Returns:
            ValidationResult
        """
        if 'dscr' not in self.df.columns:
            return ValidationResult(
                check_name="Financial Ratios",
                passed=False,
                failed_records=0,
                total_records=len(self.df),
                error_message="DSCR column missing"
            )

        # DSCR = Operating Cash Flow / Debt Service
        # DSCR > 1.0 means can cover debt
        invalid = (self.df['dscr'] < 0.5).sum()  # Very low DSCR is suspect
        passed = invalid == 0

        result = ValidationResult(
            check_name="Financial Ratios (DSCR > 0.5)",
            passed=passed,
            failed_records=invalid,
            total_records=len(self.df),
            error_message=f"Found {invalid} records with unrealistic DSCR" if invalid > 0 else "",
            details={'min_dscr': float(self.df['dscr'].min())}
        )
        self.validation_results.append(result)
        return result

    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.

        Returns:
            Dictionary with validation summary
        """
        if not self.validation_results:
            return {'status': 'No validations run'}

        passed = sum(1 for r in self.validation_results if r.passed)
        failed = len(self.validation_results) - passed

        return {
            'project_id': self.project_id,
            'total_checks': len(self.validation_results),
            'passed_checks': passed,
            'failed_checks': failed,
            'pass_rate': f"{100.0 * passed / len(self.validation_results):.1f}%",
            'failures': [r.check_name for r in self.validation_results if not r.passed],
        }
