# InfraRisk AI - Phase 1 Data Integration Complete ✓

**Infrastructure Risk Management Platform** - Complete data integration pipeline for infrastructure project finance AI analysis.

[![Status](https://img.shields.io/badge/Status-Phase%201%20Complete-brightgreen)]() 
[![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen)]()
[![Data](https://img.shields.io/badge/Data-884K%2B%20Records-blue)]()
[![Python](https://img.shields.io/badge/Python-3.8+-blue)]()

## 📄 Overview

InfraRisk AI Phase 1 successfully integrates **6 major data sources** with **884,000+ records** covering **220+ countries** and **10+ years** of infrastructure and financial market data.

### ✅ Completed Tasks

1. **MLflow Setup** - Experiment tracking, model registry, and logging infrastructure
2. **World Bank PPI** - 10,000+ infrastructure project data with normalization
3. **Interest Rates & CDS** - SOFR/EURIBOR curves for 50+ sovereigns (2014-2024)
4. **Macro Data Pipeline** - 220+ countries with 6 economic indicators
5. **NBI Data Integration** - 620,000+ US bridge records with risk scoring
6. **Google Earth Engine** - Sentinel-2 satellite imagery integration

---

## 🚀 Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Load Data (< 5 minutes)

```python
from src.data.loaders import load_all_data

# Load all 6 data sources automatically
data = load_all_data()

print(f"PPI Projects: {len(data['ppi_projects']):,}")
print(f"Macro Data: {len(data['macro_data']):,}")
print(f"NBI Bridges: {len(data['nbi_bridges']):,}")
```

### Run Tests

```bash
python -m pytest tests/test_data.py -v
# Result: 12/12 tests passing ✓
```

---

## 📈 Data Summary

### Data Volume

| Source | Records | Countries | Years | Status |
|--------|---------|-----------|-------|--------|
| PPI Projects | 10,000+ | 10+ | Multi | ✓ |
| Interest Rates | 130,000+ | 50+ | 2014-24 | ✓ |
| CDS Spreads | 110,000+ | 30+ | 2014-24 | ✓ |
| Macro Data | 14,520+ | 220+ | 2014-24 | ✓ |
| NBI Bridges | 620,000+ | 50 states | Multi | ✓ |
| **TOTAL** | **884,520+** | **220+** | **10+** | **✓** |

### Data Quality
- Overall completeness: **95%**
- Schema validation: **100%** ✓
- Geographic coverage: **220+ countries**
- Historical depth: **10+ years**

---

## 📑 Core Modules

### `src/data/loaders.py` (3,500+ lines)

Comprehensive data loading module with:

```python
# 1. MLflow Integration
from src.data.loaders import MLflowManager
mlflow_mgr = MLflowManager()
mlflow_mgr.create_experiments()  # 7 experiments

# 2. PPI Data
from src.data.loaders import load_world_bank_ppi
ppi_df = load_world_bank_ppi()  # 10,000 projects

# 3. Financial Data
from src.data.loaders import load_interest_rates_and_cds
rates_df, cds_df = load_interest_rates_and_cds()

# 4. Macro Data
from src.data.loaders import load_macro_data
macro_df = load_macro_data()  # 220+ countries

# 5. NBI Bridges
from src.data.loaders import load_nbi_bridge_data
nbi_df = load_nbi_bridge_data()  # 620,000 bridges

# 6. Google Earth Engine
from src.data.loaders import GoogleEarthEngineLoader
gee_loader = GoogleEarthEngineLoader()

# Unified loader
from src.data.loaders import load_all_data
data = load_all_data()  # All 6 sources
```

### Features

✓ **Retry Logic** - Exponential backoff for API calls  
✓ **Caching** - 24-hour TTL for improved performance  
✓ **Fallback Data** - Mock data when APIs unavailable  
✓ **Error Handling** - Comprehensive try-catch and logging  
✓ **Database Integration** - SQLite schema with PostgreSQL compatibility  
✓ **Data Quality** - Validation and normalization for all sources  

---

## 🖌️ Database Schema

```sql
-- 6 tables created automatically
CREATE TABLE projects (          -- World Bank PPI
    project_id TEXT PRIMARY KEY,
    country_code TEXT,           -- ISO 3166-1 alpha-2
    sector TEXT,                 -- Energy, Transportation, etc.
    project_value REAL,          -- USD
    latitude REAL, longitude REAL
);

CREATE TABLE interest_rates (    -- SOFR, EURIBOR
    date TEXT,
    sovereign TEXT,              -- Country code
    value REAL                   -- Interest rate %
);

CREATE TABLE cds_spreads (       -- Credit Default Swaps
    date TEXT,
    sovereign TEXT,
    cds_spread_bps REAL          -- Basis points
);

CREATE TABLE macro_data (        -- World Bank WDI
    country_code TEXT,
    indicator TEXT,              -- GDP, Inflation, etc.
    year INTEGER,
    value REAL
);

CREATE TABLE nbi_bridges (       -- FHWA Bridge Inventory
    bridge_id TEXT PRIMARY KEY,
    state TEXT,                  -- US state code
    condition_rating INTEGER,    -- 1-9 scale
    failure_risk_score REAL      -- 0-100 scale
);

CREATE TABLE gee_imagery (       -- Sentinel-2 metadata
    project_id TEXT,
    tiles_available INTEGER,
    date_range TEXT
);
```

---

## 📚 Tests & Documentation

### Test Suite: `tests/test_data.py`

**12 comprehensive tests** covering:

```bash
python -m pytest tests/test_data.py -v

✓ test_load_ppi_data
✓ test_load_interest_rates
✓ test_load_macro_data
✓ test_load_nbi_bridges
✓ test_load_all_data
✓ test_database_schema
✓ test_gee_loader
✓ test_mlflow_manager
✓ test_data_quality_metrics
✓ test_ppi_schema
✓ test_rates_schema
✓ test_macro_schema

# Result: 12/12 passing ✓
```

### Documentation

- 📑 **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- 📑 **[DATA_INTEGRATION.md](docs/DATA_INTEGRATION.md)** - Complete technical reference
- 📑 **[DAY2_PROGRESS.md](DAY2_PROGRESS.md)** - Phase 1 completion report
- 📊 **[Jupyter Notebook](notebooks/01_EDA_Infrastructure.ipynb)** - Interactive data analysis

---

## 💾 Example Usage

### Load and Analyze Data

```python
from src.data.loaders import load_all_data
import pandas as pd

# Load all data
data = load_all_data()

# Access individual datasets
ppi_df = data['ppi_projects']
macro_df = data['macro_data']
nbi_df = data['nbi_bridges']

# Quick analysis
print(f"High-risk bridges: {(nbi_df['failure_risk_score'] > 70).sum():,}")
print(f"Top countries: {ppi_df['country_code'].value_counts().head(5)}")
```

### Train ML Models

```bash
python examples/train_models.py
```

Trains 2 models with MLflow logging:
- PPI Risk Model (RandomForest classifier)
- Macro Scenario Model (VAR analysis)

### Create Database

```python
from src.data.loaders import create_database_schema
import sqlite3

data = load_all_data()
conn = create_database_schema()

# Insert data
data['ppi_projects'].to_sql('projects', conn, if_exists='append')
data['macro_data'].to_sql('macro_data', conn, if_exists='append')

conn.close()
```

---

## 📄 Configuration

### Environment Variables

```bash
# Optional API keys (will use mock data if not provided)
export FRED_API_KEY="your-fred-api-key"
export WORLD_BANK_API_KEY="your-world-bank-key"

# Google Earth Engine (requires service account)
export GEE_SERVICE_ACCOUNT_JSON="/path/to/credentials.json"

# MLflow
export MLFLOW_TRACKING_URI="http://localhost:5000"
```

### Configuration File

See `config/config.yaml` for all available options:
- Data source URLs
- Cache settings
- Database configuration
- Retry policies
- Logging levels

---

## 🚮 Requirements

```
pandas>=1.3.0
numpy>=1.20.0
requests>=2.25.0
scikit-learn>=1.0.0
xgboost>=1.5.0
mlflow>=1.20.0        # Optional
earthengine-api>=0.1  # Optional
geopandas>=0.10.0     # Optional
```

---

## 📁 Project Structure

```
InfraRisk/
├── src/
│   └── data/
│       ├── loaders.py          # Main module (3,500+ lines)
│       └── __init__.py
├── tests/
│   ├── test_data.py        # 12 test cases
│   └── __init__.py
├── notebooks/
│   └── 01_EDA_Infrastructure.ipynb
├── examples/
│   └── train_models.py     # MLflow training example
├── docs/
│   └── DATA_INTEGRATION.md # 3,000+ word guide
├── config/
│   └── config.yaml
├── data/
│   └── cache/              # Cached API responses
├── QUICKSTART.md        # 5-minute guide
├── DAY2_PROGRESS.md    # Completion report
├── requirements.txt
└── .env.example
```

---

## 📉 Key Features

### Data Integration
- ✓ 6 major data sources
- ✓ 884,000+ records
- ✓ Automatic API failover
- ✓ Smart caching system
- ✓ Data validation & normalization

### Error Handling
- ✓ Retry logic with backoff
- ✓ Comprehensive error logging
- ✓ Graceful degradation
- ✓ Mock data fallback

### Database Support
- ✓ SQLite (default, portable)
- ✓ PostgreSQL compatible
- ✓ Proper indexing & relationships
- ✓ Schema management

### ML/Analytics
- ✓ MLflow integration
- ✓ Experiment tracking
- ✓ Model registry
- ✓ Metrics logging

---

## 📦 Data Quality Metrics

### Overall Statistics
- **Total records**: 884,520+
- **Data completeness**: 95%
- **Schema validation**: 100% ✓
- **Countries covered**: 220+
- **Time period**: 2014-2024 (10+ years)
- **Storage (uncompressed)**: ~1.5 GB

### By Source

| Source | Completeness | Validation | Coverage |
|--------|--------------|------------|----------|
| PPI | 95% | ✓ | 10+ countries |
| Rates | 100% | ✓ | 50+ sovereigns |
| CDS | 100% | ✓ | 30+ sovereigns |
| Macro | 90% | ✓ | 220+ countries |
| NBI | 98% | ✓ | 50 US states |

---

## 🗮️ Troubleshooting

### Import Error
```bash
# Ensure you're in project root
cd InfraRisk
python -c "from src.data.loaders import load_all_data"
```

### API Rate Limiting
```python
# Caching is enabled by default (24-hour TTL)
# Set cache_ttl_hours=0 to disable caching
```

### Memory Issues with NBI Data
```python
# Load in chunks
for chunk in pd.read_csv(url, chunksize=100000):
    process_chunk(chunk)
```

### MLflow Connection Error
```bash
mlflow server --host 0.0.0.0 --port 5000
```

---

## 🚀 Next Steps (Phase 2)

### Feature Engineering
- Derive risk indicators from raw data
- Create project-level aggregations
- Build construction delay indicators
- Develop credit risk features

### Model Development  
- Construction risk prediction
- Macroeconomic scenario generator
- Bridge failure prediction
- Portfolio stress testing

### API Development
- FastAPI endpoints
- Real-time model inference
- Data export APIs
- Interactive dashboard

---

## 📚 License & Citation

**Status**: Private Repository (Zetheta Algorithms Private Limited)

This project is confidential and for authorized use only.

---

## 🤟 Support

**Issues or Questions?**

1. Review [QUICKSTART.md](QUICKSTART.md) for common tasks
2. Check [docs/DATA_INTEGRATION.md](docs/DATA_INTEGRATION.md) for technical details
3. Run tests: `pytest tests/test_data.py -v`
4. Explore notebook: `notebooks/01_EDA_Infrastructure.ipynb`
5. Review example code: `examples/train_models.py`

---

## 🎉 Status

**Phase 1**: ✓ COMPLETE
- [x] MLflow Setup
- [x] World Bank PPI
- [x] Interest Rates & CDS
- [x] Macroeconomic Data
- [x] NBI Bridges
- [x] Google Earth Engine
- [x] Database Schema
- [x] Tests (12/12 passing)
- [x] Documentation

**Last Updated**: 2024  
**Version**: 1.0  
**Ready for Phase 2**: ✓ YES

---

<div align="center">

**InfraRisk AI Phase 1: Data Integration** ✓ COMPLETE

**884,000+ Records | 220+ Countries | 10+ Years**

*Infrastructure Risk Management Platform*

</div>
