# InfraRisk AI

AI-powered infrastructure project finance risk assessment platform integrating geospatial intelligence, macroeconomic modelling, construction engineering analytics, and credit risk quantification.

## Features

- **Geospatial Intelligence**: Satellite-based construction monitoring with CNN
- **Construction Risk**: Cost overrun and schedule delay quantification
- **Macroeconomic Scenarios**: Interest rates, inflation, sovereign risk modelling
- **Debt Structuring**: Optimal financing mix and DSCR optimization
- **Portfolio Stress Testing**: Multi-scenario impact analysis
- **InfraRisk Lab**: Gamified simulation for portfolio management
- **Credit Risk Assessment**: ML-driven probability of default
- **NLP Contract Intelligence**: Automated contract risk extraction

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk

# Install dependencies
pip install -r requirements-app.txt

# Run API
uvicorn src.api.main:app --reload

# Run dashboard
streamlit run src/dashboard/app.py
```

## Architecture

- `src/models/` - ML models (CNN, TFT, GNN, PINN, XGBoost)
- `src/features/` - Feature engineering pipelines
- `src/api/` - FastAPI backend
- `src/dashboard/` - Streamlit analytics dashboard
- `src/simulation/` - InfraRisk Lab game engine
- `src/nlp/` - Contract intelligence module
- `tests/` - Unit and integration tests
- `notebooks/` - EDA and analysis

## Documentation

See `docs/` for architecture, API reference, and case studies.

## License

Proprietary - Zetheta Algorithms Private Limited
