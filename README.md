# InfraRisk AI: Comprehensive Infrastructure Project Finance Platform

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Kritvi0208/InfraRisk/CI%2FCD)](https://github.com/Kritvi0208/InfraRisk/actions)
[![Test Coverage](https://img.shields.io/codecov/c/github/Kritvi0208/InfraRisk)](https://codecov.io/gh/Kritvi0208/InfraRisk)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

## 🎯 Project Overview

**InfraRisk AI** is a production-grade machine learning and deep learning platform for infrastructure project finance that integrates:

- **Geospatial Intelligence**: Multi-temporal satellite imagery analysis (Sentinel-2) with CNN-based change detection
- **Macroeconomic Modeling**: World Bank & IMF macro data integration with sovereign risk assessment
- **Construction Engineering Analytics**: Physics-Informed Neural Networks (PINNs) modeling pavement degradation, bridge fatigue, and corrosion
- **Financial Risk Quantification**: Ensemble ML models (TFT, GNN, PINN, XGBoost, LightGBM) producing bankable credit risk assessments
- **Gamified Simulation**: InfraRisk Lab platform with AI opponent, scenario engine, and 1000-point scoring framework

### 🎮 Key Features

✅ **Multi-Modal ML/DL Models**
- Siamese CNN (ResNet-50) for satellite change detection with anomaly detection head
- Temporal Fusion Transformer (TFT) with interpretable attention weights
- Physics-Informed Neural Networks (PINNs) with embedded Paris' Law & AASHTO equations
- Graph Neural Networks (GNN) for portfolio risk propagation & centrality analysis
- Stacking Ensemble with sector-weighted meta-learner
- Monte Carlo 10,000-scenario PD simulation

✅ **NLP & Contract Intelligence**
- LayoutLM document parsing with nested clause resolution
- Custom Named Entity Recognition for sponsors, lenders, milestone extraction
- Legal-BERT classification of clauses into 12 risk categories
- Automated 1-5 severity risk scoring
- 1,000+ transaction benchmark database

✅ **Gamified Simulation Platform (InfraRisk Lab)**
- Four distinct simulation engines: Time, Decision, Event, AI Opponent
- 20+ pre-calibrated scenario shocks (Pandemic, Sovereign Downgrade, Climate Events)
- RL-trained AI opponent with PD > 8% rejection rules & HHI concentration limits
- 1000-point scoring framework + 4 game modes
- Interactive Streamlit/Plotly dashboard with satellite imagery viewer

✅ **Production-Grade Architecture**
- Great Expectations data validation (infrastructure physical plausibility checks)
- Feast Feature Store with versioned feature serving
- MLflow experiment tracking & model registry
- DVC data versioning with SHA-256 reproducibility
- GitHub Actions CI/CD (flake8/black linting, pytest automation)
- 60%+ test coverage (target >90%)
- Docker deployment with docker-compose

---

## 📊 Data Sources

| Data Source | Volume | Purpose |
|------------|--------|----------|
| World Bank PPI Database | 10,000+ projects | Historical project data, baseline credit metrics |
| Interest Rate Curves | 50+ sovereigns, 10+ years | SOFR, EURIBOR, country spreads |
| World Bank WDI & IMF | 220+ countries | Macro indicators (GDP, inflation, governance) |
| National Bridge Inventory | 620,000+ records | Pavement/bridge condition, degradation patterns |
| Sentinel-2 Satellite | 50+ sites, multi-temporal | Construction progress, site activity anomalies |
| Commodity Prices | Historical series | Gas, steel, cement, oil input costs |
| Legal Contracts | 1,000+ documents | Clause analysis, risk scoring, benchmarking |

---

## 🏗️ Project Structure

```
InfraRisk/
├── src/                           # Source code
│   ├── data/                      # Data pipelines
│   │   ├── __init__.py
│   │   ├── loaders.py            # World Bank, Earth Engine, commodity data loaders
│   │   ├── validators.py         # Great Expectations rules
│   │   └── feature_store.py      # Feast integration
│   ├── models/                    # ML/DL models
│   │   ├── __init__.py
│   │   ├── cnn.py                # Siamese CNN (ResNet-50)
│   │   ├── tft.py                # Temporal Fusion Transformer
│   │   ├── pinn.py               # Physics-Informed NNs
│   │   ├── gnn.py                # Graph Neural Networks
│   │   ├── ensemble.py           # Stacking meta-learner
│   │   ├── credit_risk.py        # XGBoost/LightGBM baselines
│   │   └── monte_carlo.py        # PD simulation engine
│   ├── nlp/                       # NLP & contract analysis
│   │   ├── __init__.py
│   │   ├── document_parsing.py   # LayoutLM
│   │   ├── ner.py                # Named Entity Recognition
│   │   ├── legal_bert.py         # Legal-BERT fine-tuning
│   │   └── risk_scoring.py       # Contract risk scoring
│   ├── simulation/                # Gamified simulation
│   │   ├── __init__.py
│   │   ├── engines.py            # Time, Decision, Event, AI Opponent engines
│   │   ├── scenario.py           # 20+ scenario shocks
│   │   ├── ai_opponent.py        # RL-trained agent
│   │   └── scoring.py            # 1000-point framework
│   ├── api/                       # FastAPI backend
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   ├── endpoints.py          # Model inference endpoints
│   │   └── schemas.py            # Pydantic request/response models
│   ├── utils/                     # Utilities
│   │   ├── __init__.py
│   │   ├── logging.py            # Custom logging
│   │   ├── config.py             # Configuration management
│   │   └── constants.py          # Constants
│   └── __init__.py
│
├── notebooks/                     # Jupyter notebooks
│   ├── 01_EDA_Infrastructure.ipynb
│   ├── 02_EDA_Macroeconomic.ipynb
│   ├── 03_EDA_Satellite.ipynb
│   ├── 04_Feature_Engineering.ipynb
│   ├── 05_Model_Training.ipynb
│   └── 06_Simulation_Demo.ipynb
│
├── tests/                         # Unit & integration tests
│   ├── __init__.py
│   ├── test_data.py              # Data pipeline tests
│   ├── test_models.py            # Model tests
│   ├── test_nlp.py               # NLP module tests
│   ├── test_simulation.py        # Simulation engine tests
│   ├── test_api.py               # API endpoint tests
│   └── conftest.py               # pytest fixtures
│
├── configs/                       # Configuration files
│   ├── config.yaml               # Main configuration
│   ├── data_validation.yaml      # Great Expectations rules
│   ├── model_params.yaml         # Model hyperparameters
│   ├── scenarios.yaml            # Simulation scenarios
│   └── .env.example              # Environment variables template
│
├── docker/                        # Docker configuration
│   ├── Dockerfile                # Main application image
│   ├── Dockerfile.backend        # FastAPI backend
│   └── docker-compose.yml        # Multi-container orchestration
│
├── docs/                          # Documentation
│   ├── API.md                    # API documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── MODEL_CARDS.md            # Model documentation
│   ├── DATA_DICTIONARY.md        # Feature definitions
│   └── DEPLOYMENT.md             # Deployment guide
│
├── data/                          # Data directory (gitignored)
│   ├── raw/                      # Raw downloaded data
│   └── processed/                # Processed features
│
├── models/                        # Trained models (gitignored)
│   ├── cnn/
│   ├── tft/
│   ├── pinn/
│   ├── gnn/
│   └── ensemble/
│
├── mlruns/                        # MLflow experiment tracking (gitignored)
├── .dvc/                          # DVC configuration
├── .github/workflows/             # GitHub Actions CI/CD
│   └── ci.yml
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Poetry configuration
├── setup.py                       # Setup configuration
├── pytest.ini                     # Pytest configuration
├── .pre-commit-config.yaml        # Pre-commit hooks
├── LICENSE                        # Apache 2.0 License
├── CONTRIBUTING.md                # Contribution guidelines
└── .gitignore
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Git
- PostgreSQL 12+
- Google Earth Engine account (for satellite data)

### 1. Clone Repository
```bash
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp configs/.env.example .env
# Edit .env with your credentials (Earth Engine, database, API keys)
```

### 5. Initialize Data & Models
```bash
python scripts/init_data.py          # Download and process data
python scripts/init_mlflow.py        # Set up MLflow tracking
python scripts/init_feature_store.py # Initialize Feast feature store
```

### 6. Run Tests
```bash
pytest tests/ --cov=src --cov-report=html
```

### 7. Start Application (Local Development)
```bash
# Backend API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Dashboard (in another terminal)
streamlit run src/dashboard/app.py
```

### 8. Docker Deployment (Production)
```bash
docker-compose -f docker/docker-compose.yml up -d
```

---

## 📚 Tech Stack

### ML/DL Frameworks
- **TensorFlow 2.12+**: Deep learning, CNNs, PINNs
- **PyTorch 2.0+**: GNN, Transformer models (TFT), RL training
- **XGBoost & LightGBM**: Gradient boosting baselines
- **scikit-learn**: Preprocessing, evaluation metrics
- **Optuna**: Bayesian hyperparameter optimization

### Data & Feature Engineering
- **Pandas & Polars**: Data manipulation
- **GeoPandas & Rasterio**: Geospatial operations
- **Dask**: Distributed computing for large datasets
- **Feast**: Production feature store
- **Great Expectations**: Data validation

### NLP & Language Models
- **Transformers (Hugging Face)**: Legal-BERT, LayoutLM
- **spaCy**: Named Entity Recognition
- **PyPDF2 & Pdfplumber**: PDF parsing

### APIs & Backend
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching & feature serving

### Frontend & Visualization
- **Streamlit**: Interactive dashboard
- **Plotly & Altair**: Interactive visualizations
- **Folium**: Satellite imagery mapping

### Experiment Tracking & Versioning
- **MLflow**: Model tracking, registry, deployment
- **DVC**: Data versioning
- **GitHub Actions**: CI/CD automation
- **Coverage.py**: Test coverage reporting

### Simulation & Optimization
- **SimPy**: Discrete event simulation
- **PuLP/Gurobi**: Linear programming
- **Ray RLlib**: Reinforcement learning

---

## 📊 Model Architecture Overview

### 1. Satellite Change Detection (Siamese CNN + ResNet-50)
```
Input: Multi-temporal Sentinel-2 patches (256×256×13)
  ↓
Siamese ResNet-50 backbone (shared weights)
  ↓
├─ Regression Head → Construction progress % (MAPE < 15%)
├─ Classification Head → Construction phases (5 classes)
└─ Anomaly Head → Site abandonment, equipment removal
  ↓
Output: Progress metric, phase label, anomaly score
```

### 2. Revenue Forecasting (Temporal Fusion Transformer)
```
Input: Historical toll/energy revenue, macroeconomic series
  ↓
TFT encoder-decoder architecture
  ↓
Output: Multi-horizon quantile forecasts (P10, P50, P90) + attention weights
```

### 3. Physics-Informed Neural Networks (PINN)
```
Inputs: Material properties, load history, climate (temperature, precipitation)
  ↓
Neural network φ(x,t) predicts state variable (crack size, pavement PSI)
  ↓
Loss = MSE(φ, data) + MSE(∂φ/∂t - ODE_residuals)
       where ODE_residuals = Paris' Law or AASHTO equations
  ↓
Output: Remaining Useful Life (RUL) with confidence intervals
```

### 4. Portfolio Risk Graph Neural Network
```
Nodes: Infrastructure projects
Edges: Financial/operational dependencies
  ↓
GNN layers with graph convolution
  ↓
Centrality metrics: betweenness, eigenvector, degree
  ↓
Output: Systemic importance scores for each project
```

### 5. Credit Risk Ensemble
```
Base Models:
  - TFT revenue forecast → LGD/PD adjustment
  - GNN systemic score → correlation PD
  - PINN RUL → technical risk adjustment
  - XGBoost/LightGBM financial ratios → base PD
  ↓
Meta-Learner: Sector-weighted Logistic Regression
  ↓
Output: Final PD estimate with 95% confidence intervals
```

---

## 🎮 InfraRisk Lab Simulation

Four-engine simulation platform:

**1. Time Engine**: Quarterly progression with calendar events
**2. Decision Engine**: Deal sourcing, portfolio management, rebalancing
**3. Event Engine**: 20+ scenario shocks (macro, construction, regulatory)
**4. AI Opponent Engine**: RL-trained agent competing with learner

### Scoring Framework (1000 points)
- **PD Forecast Accuracy**: 250 pts (RMSE-based)
- **Debt Optimization**: 250 pts (coverage ratios, returns)
- **ESG Integration**: 300 pts (sustainability goals)
- **Portfolio Management**: 200 pts (diversification, sizing)

### Game Modes
1. **Single Deal**: Structure individual infrastructure project (tutorial)
2. **Portfolio Manager**: Manage 5-15 deals across sectors, respond to events
3. **Crisis Manager**: Navigate refinancing, construction delays, revenue shocks
4. **Deal Structurer**: Optimize debt instruments, tenor, guarantee structures

---

## 🚀 Quick Start: Running the Simulation

```python
from src.simulation.engines import InfraRiskLab
from src.models.ensemble import CreditRiskEnsemble

# Initialize simulation
lab = InfraRiskLab(mode='portfolio_manager', difficulty='intermediate')
lab.load_scenario('2024_economic_downturn')

# Play
while lab.is_running():
    # Get portfolio state
    portfolio = lab.get_portfolio_status()
    print(f"Quarter {lab.current_quarter}: {len(portfolio)} projects")
    
    # Get events
    events = lab.get_active_events()
    for event in events:
        print(f"⚠️ {event.description} - Impact: {event.severity}")
    
    # Make decisions
    decision = lab.make_decision(
        action='rebalance',
        target_portfolio=new_allocation
    )
    
    # Advance time
    lab.advance_quarter()

# Get score
score = lab.get_final_score()
print(f"🏆 Final Score: {score}/1000 points")
```

---

## 📈 Performance Benchmarks

| Model | Metric | Target | Status |
|-------|--------|--------|--------|
| CNN Progress | MAPE | < 15% | 🟡 In Development |
| TFT Revenue | MAE | < 5% | 🟡 In Development |
| PINN RUL | RMSE | < 2 yrs | 🟡 In Development |
| GNN Centrality | Correlation | > 0.85 | 🟡 In Development |
| Ensemble PD | AUC | > 0.90 | 🟡 In Development |
| NLP Clause Risk | Accuracy | > 95% | 🟡 In Development |

---

## 📖 Documentation

- **[API Documentation](docs/API.md)**: Complete endpoint reference
- **[Architecture Guide](docs/ARCHITECTURE.md)**: System design & components
- **[Model Cards](docs/MODEL_CARDS.md)**: Detailed model documentation with SHAP explanations
- **[Data Dictionary](docs/DATA_DICTIONARY.md)**: Feature definitions & sources
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment steps
- **[Contributing](CONTRIBUTING.md)**: How to contribute

---

## 🔐 Security & IP Protection

- All novel algorithms documented with patent-ready mathematical formulations
- Source code licensed under Apache 2.0
- Sensitive credentials stored in `.env` (never committed)
- DVC ensures data lineage and reproducibility
- GitHub Actions enforces security scanning

---

## 📞 Contact & Support

Project Lead: [Kritvi0208](https://github.com/Kritvi0208)  
Repository: [https://github.com/Kritvi0208/InfraRisk](https://github.com/Kritvi0208/InfraRisk)  
License: [Apache 2.0](LICENSE)

---

## 📝 Citation

If you use InfraRisk AI in your research or production systems, please cite:

```bibtex
@software{infrariskai2024,
  title={InfraRisk AI: Comprehensive Infrastructure Project Finance Platform},
  author={Kritvi0208},
  year={2024},
  url={https://github.com/Kritvi0208/InfraRisk}
}
```

---

**Status**: 🟡 Active Development (Day 1)  
**Last Updated**: 2026-05-15  
**Next Milestone**: Day 1 Phase 1 Completion (Data Foundation)
