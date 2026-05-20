# InfraRisk AI - Architecture

## System Design

```
┌─────────────────────────────────────────────────┐
│           Streamlit Dashboard (UI)              │
│  Portfolio View | Simulation | Credit Reports  │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│         FastAPI Backend (Core Logic)            │
├─────────────────────────────────────────────────┤
│ • Project Assessment   • Portfolio Analytics    │
│ • Stress Testing      • DSCR Calculation        │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│           ML Models Layer                       │
├─────────────────────────────────────────────────┤
│ • Ensemble (XGBoost + TFT + GNN + CNN + PINN) │
│ • Credit Risk Scoring (PD/LGD)                  │
│ • Demand Forecasting                            │
│ • Construction Monitoring                       │
└─────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────┐
│        Data Layer & External APIs               │
├─────────────────────────────────────────────────┤
│ • World Bank API   • IMF WEO Forecasts         │
│ • Sentinel-2 Satellite  • Bloomberg Data        │
│ • Project Database (SQLite/PostgreSQL)          │
└─────────────────────────────────────────────────┘
```

## Components

### 1. Ensemble Credit Risk Model
- Base models: XGBoost, LightGBM, TFT, GNN, PINN
- Meta-learner: Logistic regression with sector weights
- Output: PD (0-1), Risk Rating (AAA-D)

### 2. Geospatial Construction Monitor
- Input: Sentinel-2 satellite imagery (13 bands, 10m resolution)
- Process: Atmospheric correction → Change detection → Progress estimation
- Output: Construction progress %, anomaly detection, schedule variance

### 3. Demand Forecasting
- Models: SARIMA (baseline), Temporal Fusion Transformer (SOTA)
- Outputs: Point forecast + confidence intervals (P10-P90)
- Sectors: Toll roads, power plants, ports, airports

### 4. NLP Contract Intelligence
- Input: Concession agreements, EPC contracts, PPAs
- Process: PDF parsing → Clause extraction → Risk scoring
- Output: Contract risk score, deviation flags from benchmarks

### 5. InfraRisk Lab Simulation
- Game modes: Single Deal, Portfolio Manager, Crisis Manager, Deal Structurer
- Scenarios: 20+ pre-calibrated shocks (cost overruns, demand shocks, sovereign downgrades)
- AI Opponent: Powered by ensemble model
- Scoring: 1000 points across 6 dimensions

## Data Flow

1. **Ingestion**: World Bank PPI, satellite imagery, macro data
2. **Processing**: Feature engineering (85+ features), quality validation
3. **Training**: ML models with cross-validation
4. **Inference**: Real-time project assessment, portfolio analytics
5. **Storage**: SQLite/PostgreSQL with DVC versioning

## Key Features

- ✅ End-to-end ML pipeline with CI/CD
- ✅ Multi-modal data integration (structured, satellite, NLP)
- ✅ Real-time risk monitoring
- ✅ Interactive gamified simulation
- ✅ Production-grade API
- ✅ Comprehensive documentation

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **ML**: PyTorch, XGBoost, LightGBM, Scikit-learn
- **Frontend**: Streamlit, Plotly
- **Geospatial**: GeoPandas, Rasterio, Sentinel-2
- **DevOps**: Docker, GitHub Actions, DVC
