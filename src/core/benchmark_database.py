"""
Benchmark database module for Phase 4 NLP pipeline.
Loads comparable transactions from the local real World Bank PPI file.
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from contract_types import BenchmarkTransaction


PPI_COUNTRY_CODES = {
    6: "Argentina", 19: "Bangladesh", 26: "Brazil", 38: "Chile", 41: "China",
    45: "Colombia", 57: "Egypt", 68: "Ghana", 79: "India", 80: "Indonesia",
    93: "Kenya", 108: "Mexico", 114: "Morocco", 121: "Nigeria", 128: "Pakistan",
    130: "Peru", 131: "Philippines", 151: "South Africa", 162: "Thailand",
    166: "Turkey", 179: "Vietnam",
}

PPI_SECTOR_CODES = {1: "transport", 2: "energy", 3: "telecom", 4: "water"}
PPI_STATUS_CODES = {1: "Operational", 2: "Under Construction", 3: "Canceled", 4: "Distressed", 5: "Concluded"}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _decode_code(value, mapping: Dict[int, str], prefix: str) -> str:
    try:
        return mapping.get(int(float(value)), f"{prefix} {int(float(value))}")
    except (TypeError, ValueError):
        return str(value or "Unknown")


class BenchmarkDatabase:
    """Real benchmark database of comparable infrastructure transactions."""
    
    def __init__(self):
        """Initialize benchmark database."""
        self.transactions = self._load_ppi_transactions()
        self.indexes = self._build_indexes()
    
    def _load_ppi_transactions(self) -> List[BenchmarkTransaction]:
        """Load benchmark transactions from the local World Bank PPI CSV."""
        try:
            import pandas as pd
        except ImportError:
            return []

        path = _project_root() / "data" / "raw" / "ppi" / "ppi_projects.csv"
        if not path.exists():
            return []

        df = pd.read_csv(path, low_memory=False)
        if df.empty:
            return []

        def number(value, default: float = 0.0) -> float:
            parsed = pd.to_numeric(value, errors="coerce")
            return float(parsed) if pd.notna(parsed) else default

        investment = pd.to_numeric(df.get("investment", 0), errors="coerce")
        capacity_dollar = pd.to_numeric(df.get("CapacityDollar", 0), errors="coerce")
        df["project_value"] = investment.fillna(capacity_dollar).fillna(0.0) * 1_000_000
        df = df[df["project_value"] > 0].copy()

        debt = pd.to_numeric(df.get("debt", 0), errors="coerce").fillna(0.0) * 1_000_000
        equity = pd.to_numeric(df.get("equity", 0), errors="coerce").fillna(0.0) * 1_000_000
        debt = debt.where(debt > 0, df["project_value"] * 0.65)
        equity = equity.where(equity > 0, (df["project_value"] - debt).clip(lower=0.0))

        transactions = []
        for idx, row in df.iterrows():
            project_value = float(row["project_value"])
            debt_value = float(debt.loc[idx])
            equity_value = float(equity.loc[idx])
            debt_pct = debt_value / project_value * 100 if project_value else 0.0
            equity_pct = equity_value / project_value * 100 if project_value else 0.0
            tenor = int(number(row.get("period"), 20))
            status = _decode_code(row.get("status_n"), PPI_STATUS_CODES, "Status")
            sector = _decode_code(row.get("sector"), PPI_SECTOR_CODES, "sector").lower().replace(" ", "_")
            country = _decode_code(row.get("country"), PPI_COUNTRY_CODES, "country").lower()
            risk_score = {
                "operational": 2.0,
                "concluded": 2.2,
                "under construction": 3.0,
                "distressed": 4.2,
                "canceled": 4.8,
            }.get(status.lower(), 3.0)
            covenants = {
                "dscr_minimum": 1.25,
                "leverage_maximum": round(debt_pct / 100, 3),
                "min_liquidity_usd": project_value * 0.02,
                "interest_coverage_min": 2.0,
            }
            transactions.append(BenchmarkTransaction(
                transaction_id=f"PPI-{row.get('ID', idx)}-{idx}",
                sector=sector,
                country=country,
                project_value=project_value,
                tenor_years=tenor,
                equity_percentage=equity_pct,
                debt_percentage=debt_pct,
                key_milestones=max(1, int(number(row.get("numberb"), 1))),
                financial_covenants=covenants,
                risk_score=risk_score,
                completion_status=status,
                metadata={
                    "source": "World Bank PPI",
                    "year": int(number(row.get("IY", row.get("FCY")), 0)),
                    "name": str(row.get("name", "")),
                    "source_url": str(row.get("source_url", "")),
                }
            ))
        
        return transactions
    
    def _build_indexes(self) -> Dict[str, Dict]:
        """Build indexes for fast lookup."""
        indexes = {
            'by_sector': {},
            'by_country': {},
            'by_status': {},
            'by_risk_range': {},
        }
        
        for txn in self.transactions:
            # Index by sector
            if txn.sector not in indexes['by_sector']:
                indexes['by_sector'][txn.sector] = []
            indexes['by_sector'][txn.sector].append(txn.transaction_id)
            
            # Index by country
            if txn.country not in indexes['by_country']:
                indexes['by_country'][txn.country] = []
            indexes['by_country'][txn.country].append(txn.transaction_id)
            
            # Index by status
            if txn.completion_status not in indexes['by_status']:
                indexes['by_status'][txn.completion_status] = []
            indexes['by_status'][txn.completion_status].append(txn.transaction_id)
            
            # Index by risk range
            risk_band = int(txn.risk_score)
            key = f"risk_{risk_band}"
            if key not in indexes['by_risk_range']:
                indexes['by_risk_range'][key] = []
            indexes['by_risk_range'][key].append(txn.transaction_id)
        
        return indexes
    
    def find_similar_deals(
        self,
        sector: str,
        country: str,
        project_value: float,
        tenor_years: int,
        tolerance: float = 0.25,
        max_results: int = 10
    ) -> List[BenchmarkTransaction]:
        """Find similar deals from benchmark database."""
        candidates = []
        
        for txn in self.transactions:
            # Filter by sector
            if txn.sector != sector:
                continue
            
            # Filter by country
            if txn.country != country:
                continue
            
            # Check value tolerance (within 25% by default)
            value_diff = abs(txn.project_value - project_value) / project_value
            if value_diff > tolerance:
                continue
            
            # Check tenor tolerance (within 2 years by default)
            tenor_diff = abs(txn.tenor_years - tenor_years)
            if tenor_diff > (tolerance * 10):  # Scale tenure tolerance
                continue
            
            candidates.append(txn)
        
        # Sort by value proximity
        candidates.sort(
            key=lambda x: abs(x.project_value - project_value)
        )
        
        return candidates[:max_results]
    
    def get_sector_statistics(self, sector: str) -> Dict:
        """Get statistics for a sector."""
        sector_txns = [t for t in self.transactions if t.sector == sector]
        
        if not sector_txns:
            return {}
        
        values = [t.project_value for t in sector_txns]
        tenors = [t.tenor_years for t in sector_txns]
        equities = [t.equity_percentage for t in sector_txns]
        risks = [t.risk_score for t in sector_txns]
        
        def mean(lst):
            return sum(lst) / len(lst) if lst else 0
        
        def std(lst):
            m = mean(lst)
            return (sum((x - m) ** 2 for x in lst) / len(lst)) ** 0.5 if lst else 0
        
        return {
            'count': len(sector_txns),
            'avg_project_value': mean(values),
            'std_project_value': std(values),
            'min_project_value': min(values),
            'max_project_value': max(values),
            'avg_tenor': mean(tenors),
            'std_tenor': std(tenors),
            'avg_equity': mean(equities),
            'std_equity': std(equities),
            'avg_risk_score': mean(risks),
            'std_risk_score': std(risks),
        }
    
    def get_country_statistics(self, country: str) -> Dict:
        """Get statistics for a country."""
        country_txns = [t for t in self.transactions if t.country == country]
        
        if not country_txns:
            return {}
        
        risks = [t.risk_score for t in country_txns]
        sectors_present = set(t.sector for t in country_txns)
        
        def mean(lst):
            return sum(lst) / len(lst) if lst else 0
        
        return {
            'transaction_count': len(country_txns),
            'avg_risk_score': mean(risks),
            'max_risk_score': max(risks),
            'min_risk_score': min(risks),
            'sectors_active': list(sectors_present),
            'top_sectors': self._get_top_sectors_for_country(country, top_n=3),
        }
    
    def _get_top_sectors_for_country(self, country: str, top_n: int = 3) -> List[Tuple[str, int]]:
        """Get top sectors for a country."""
        sector_counts = {}
        
        for txn in self.transactions:
            if txn.country == country:
                sector_counts[txn.sector] = sector_counts.get(txn.sector, 0) + 1
        
        return sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_statistical_comparison(
        self,
        target_txn: BenchmarkTransaction,
        comparable_txns: List[BenchmarkTransaction]
    ) -> Dict:
        """Compare target to comparable transactions."""
        
        if not comparable_txns:
            return {'error': 'No comparable transactions found'}
        
        def mean(lst):
            return sum(lst) / len(lst) if lst else 0
        
        # Extract metrics
        comparable_values = [t.project_value for t in comparable_txns]
        comparable_tenors = [t.tenor_years for t in comparable_txns]
        comparable_equities = [t.equity_percentage for t in comparable_txns]
        comparable_risks = [t.risk_score for t in comparable_txns]
        
        # Calculate deviations
        comparison = {
            'project_value_deviation': (target_txn.project_value - mean(comparable_values)) / mean(comparable_values),
            'tenor_deviation': (target_txn.tenor_years - mean(comparable_tenors)) / mean(comparable_tenors),
            'equity_deviation': (target_txn.equity_percentage - mean(comparable_equities)) / mean(comparable_equities),
            'risk_deviation': (target_txn.risk_score - mean(comparable_risks)) / mean(comparable_risks),
            'comparable_count': len(comparable_txns),
            'metrics': {
                'avg_project_value': mean(comparable_values),
                'avg_tenor': mean(comparable_tenors),
                'avg_equity': mean(comparable_equities),
                'avg_risk_score': mean(comparable_risks),
            }
        }
        
        return comparison
    
    def detect_outliers(
        self,
        sector: str,
        country: Optional[str] = None,
        std_threshold: float = 2.0
    ) -> List[Dict]:
        """Detect outlier transactions."""
        
        # Filter transactions
        txns = [t for t in self.transactions if t.sector == sector]
        if country:
            txns = [t for t in txns if t.country == country]
        
        if len(txns) < 3:
            return []
        
        outliers = []
        
        # Check for value outliers
        values = [t.project_value for t in txns]
        mean_val = sum(values) / len(values)
        std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
        
        for txn in txns:
            z_score = abs((txn.project_value - mean_val) / std_val) if std_val > 0 else 0
            if z_score > std_threshold:
                outliers.append({
                    'transaction_id': txn.transaction_id,
                    'metric': 'project_value',
                    'value': txn.project_value,
                    'z_score': z_score,
                    'type': 'outlier'
                })
        
        # Check for risk outliers
        risks = [t.risk_score for t in txns]
        mean_risk = sum(risks) / len(risks)
        std_risk = (sum((x - mean_risk) ** 2 for x in risks) / len(risks)) ** 0.5
        
        for txn in txns:
            z_score = abs((txn.risk_score - mean_risk) / std_risk) if std_risk > 0 else 0
            if z_score > std_threshold:
                outliers.append({
                    'transaction_id': txn.transaction_id,
                    'metric': 'risk_score',
                    'value': txn.risk_score,
                    'z_score': z_score,
                    'type': 'outlier'
                })
        
        return outliers
    
    def export_database_json(self, limit: int = 100) -> str:
        """Export benchmark database as JSON."""
        output = {
            'total_transactions': len(self.transactions),
            'exported_count': min(limit, len(self.transactions)),
            'transactions': [t.to_dict() for t in self.transactions[:limit]],
        }
        
        return json.dumps(output, indent=2, default=str)
    
    def generate_database_summary(self) -> str:
        """Generate database summary report."""
        lines = ["=== BENCHMARK DATABASE SUMMARY ===\n"]
        
        lines.append(f"Total Transactions: {len(self.transactions)}")
        
        # Sector distribution
        sector_counts = {}
        for txn in self.transactions:
            sector_counts[txn.sector] = sector_counts.get(txn.sector, 0) + 1
        
        lines.append(f"\nSector Distribution ({len(sector_counts)} sectors):")
        for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = (count / len(self.transactions) * 100)
            lines.append(f"  {sector}: {count} ({pct:.1f}%)")
        
        # Country distribution
        country_counts = {}
        for txn in self.transactions:
            country_counts[txn.country] = country_counts.get(txn.country, 0) + 1
        
        lines.append(f"\nTop Countries ({len(country_counts)} countries):")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = (count / len(self.transactions) * 100)
            lines.append(f"  {country}: {count} ({pct:.1f}%)")
        
        # Risk statistics
        risk_scores = [t.risk_score for t in self.transactions]
        avg_risk = sum(risk_scores) / len(risk_scores)
        lines.append(f"\nRisk Statistics:")
        lines.append(f"  Average Risk Score: {avg_risk:.2f}/5.0")
        lines.append(f"  Min Risk Score: {min(risk_scores):.2f}")
        lines.append(f"  Max Risk Score: {max(risk_scores):.2f}")
        
        return "\n".join(lines)
