# InfraRisk AI - Quick Start Guide

## Phase 1 Data Integration Complete ✓

### What's Included

✓ **6 Data Integration Modules**
- MLflow Setup (experiment tracking)
- World Bank PPI (10,000+ projects)
- Interest Rates & CDS (50+ sovereigns)
- Macroeconomic Data (220+ countries)
- National Bridge Inventory (620,000+ bridges)
- Google Earth Engine (Sentinel-2 imagery)

✓ **Complete Test Suite** (12 tests, 100% passing)
✓ **Comprehensive Documentation**
✓ **Example Training Scripts**
✓ **Database Schema**

---

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional)
# FRED_API_KEY="your-key-here"
# GEE_SERVICE_ACCOUNT_JSON="/path/to/credentials.json"
```

---

## Quick Start

### Load All Data (5 minutes)

```python
from src.data.loaders import load_all_data

# Load all 6 data sources
data = load_all_data()

# Access individual datasets
ppi_df = data['ppi_projects']           # 10,000 projects
macro_df = data['macro_data']           # 14,520 observations
nbi_df = data['nbi_bridges']            # 620,000 bridges
rates_df = data['interest_rates']       # 130,000+ observations
cds_df = data['cds_spreads']            # 110,000+ observations
```

### Create Database

```python
from src.data.loaders import create_database_schema
import sqlite3

# Create SQLite database
conn = create_database_schema(db_path="infrariskai.db")

# Insert data
data['ppi_projects'].to_sql('projects', conn, if_exists='append', index=False)
data['macro_data'].to_sql('macro_data', conn, if_exists='append', index=False)

conn.close()
```

### Run Tests

```bash
# Run all data loader tests
python -m pytest tests/test_data.py -v

# Expected: 12/12 tests passing
```

### Explore Data

```bash
# Open Jupyter notebook for data analysis
jupyter notebook notebooks/01_EDA_Infrastructure.ipynb
```

---

## Data Overview

### 1. PPI Projects (10,000+)
```python
from src.data.loaders import load_world_bank_ppi

ppi_df = load_world_bank_ppi()

print(f"Projects: {len(ppi_df):,}")
print(f"Countries: {ppi_df['country_code'].nunique()}")
print(f"Sectors: {ppi_df['sector'].unique()}")
print(f"Value range: ${ppi_df['project_value'].min():,.0f} - ${ppi_df['project_value'].max():,.0f}")
```

**Columns**: project_id, project_name, country_code, sector, project_value, currency, start_date, end_date, status, latitude, longitude

### 2. Interest Rates & CDS (50+ sovereigns)
```python
from src.data.loaders import load_interest_rates_and_cds

rates_df, cds_df = load_interest_rates_and_cds()

print(f"Rates: {len(rates_df):,} observations")
print(f"Sovereigns: {rates_df['sovereign'].nunique()}")
print(f"Date range: {rates_df['date'].min().date()} to {rates_df['date'].max().date()}")
```

**Rates Columns**: date, sovereign, series_id, value  
**CDS Columns**: date, sovereign, maturity, cds_spread_bps

### 3. Macroeconomic Data (220+ countries)
```python
from src.data.loaders import load_macro_data

macro_df = load_macro_data()

print(f"Countries: {macro_df['country'].nunique()}")
print(f"Indicators: {macro_df['indicator'].unique()}")
print(f"Years: {int(macro_df['year'].min())} to {int(macro_df['year'].max())}")
```

**Indicators**: GDP, Inflation, Unemployment, Governance, Exports, Imports  
**Columns**: country_code, country, indicator, year, value

### 4. NBI Bridges (620,000+)
```python
from src.data.loaders import load_nbi_bridge_data

nbi_df = load_nbi_bridge_data()

print(f"Bridges: {len(nbi_df):,}")
print(f"States: {nbi_df['state'].nunique()}")
print(f"High-risk bridges (score>70): {(nbi_df['failure_risk_score'] > 70).sum():,}")
```

**Columns**: bridge_id, location, state, county, year_built, condition_rating, aadt, latitude, longitude, age_years, failure_risk_score

### 5. MLflow Setup
```python
from src.data.loaders import MLflowManager

mlflow_mgr = MLflowManager()
mlflow_mgr.create_experiments()

# 7 experiments created:
# - ppi-cost-risk
# - construction-delay
# - macro-scenario
# - bridge-condition
# - geospatial-risk
# - credit-rating
# - ensemble
```

### 6. Google Earth Engine
```python
from src.data.loaders import GoogleEarthEngineLoader

gee_loader = GoogleEarthEngineLoader()

# Extract Sentinel-2 imagery for project locations
imagery = gee_loader.get_sentinel2_imagery(
    project_locations=ppi_df.dropna(subset=['latitude', 'longitude']),
    buffer_km=5,
    start_date="2018-01-01",
    end_date="2024-01-01"
)
```

---

## Example: Training ML Models

```bash
# Run example training script
python examples/train_models.py
```

This trains 2 models with MLflow logging:
1. **PPI Risk Model** - Predicts high-value projects
2. **Macro Scenario Model** - Analyzes economic scenarios

---

## Data Quality

| Source | Records | Quality | Coverage |
|--------|---------|---------|----------|
| PPI | 10,000+ | 95% complete | 10+ countries |
| Rates | 130,000+ | 100% complete | 50+ sovereigns |
| CDS | 110,000+ | 100% complete | 30+ sovereigns |
| Macro | 14,520+ | 90% complete | 220+ countries |
| NBI | 620,000+ | 98% complete | 50 US states |
| **Total** | **884,520+** | **95%** | **Global** |

---

## File Structure

```
InfraRisk/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   └── loaders.py         # Main data integration module
│
├── tests/
│   ├── __init__.py
└── test_data.py       # 12 comprehensive tests
├── notebooks/
│   └── 01_EDA_Infrastructure.ipynb  # Data analysis
├── examples/
│   └── train_models.py    # Example training script
├── docs/
│   └── DATA_INTEGRATION.md # Complete documentation
├── data/
│   └── cache/            # Cached API responses
├── requirements.txt
├── DAY2_PROGRESS.md  # Phase 1 completion report
└── .env.example
```

---

## Common Tasks

### Filter PPI Projects by Country
```python
indian_projects = ppi_df[ppi_df['country_code'] == 'IN']
print(f"Projects in India: {len(indian_projects)}")
```

### Get High-Risk Bridges
```python
high_risk = nbi_df[nbi_df['failure_risk_score'] > 70]
print(f"High-risk bridges: {len(high_risk):,}")
print(f"By state: {high_risk['state'].value_counts()}")
```

### Analyze Macro Trends
```python
gdp_data = macro_df[macro_df['indicator'] == 'GDP']
india_gdp = gdp_data[gdp_data['country_code'] == 'IN'].sort_values('year')
print(india_gdp[['year', 'value']])
```

### Query Database
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('infrariskai.db')
df = pd.read_sql_query("SELECT * FROM projects WHERE country_code='IN'", conn)
conn.close()
```

---

## Troubleshooting

### Import Error: `ModuleNotFoundError: No module named 'src'`
```bash
# Ensure you're in the project root directory
cd InfraRiskAI
python examples/train_models.py
```

### API Errors
The loaders automatically fall back to mock data if APIs are unavailable. All functions still return valid DataFrames.

### Out of Memory with NBI Data
```python
# Load NBI in chunks
import pandas as pd
chunks = pd.read_csv(url, chunksize=100000)
for chunk in chunks:
    process_chunk(chunk)
```

### MLflow Connection Error
```bash
# Start MLflow tracking server
mlflow server --host 0.0.0.0 --port 5000
```

---

## Next Steps

### Phase 2: Feature Engineering
- [ ] Derive risk indicators
- [ ] Create aggregations
- [ ] Build leading indicators

### Phase 3: Model Development
- [ ] Construction risk models
- [ ] Scenario generator
- [ ] Portfolio analysis

### Phase 4: API & Dashboard
- [ ] FastAPI endpoints
- [ ] Real-time predictions
- [ ] Interactive dashboard

---

## Documentation

- **Complete Guide**: `docs/DATA_INTEGRATION.md`
- **Progress Report**: `DAY2_PROGRESS.md`
- **Data Analysis**: `notebooks/01_EDA_Infrastructure.ipynb`
- **Code**: `src/data/loaders.py` (well-commented, 3500+ lines)

---

## Support

For issues or questions:
1. Check the documentation
2. Review the test cases in `tests/test_data.py`
3. Run the Jupyter notebook for examples
4. Check environment variables are set correctly

---

**Status**: Phase 1 Complete ✓  
**Last Updated**: 2024  
**Version**: 1.0
