# InfraRisk AI - System Architecture

## High-Level Architecture

```
┌─────────────────────────┐
│ Frontend (Streamlit Dashboard)      │
│ - Portfolio Overview               │
│ - Risk Dashboard                   │
│ - Game Simulation                  │
└─────────────────────────┘
           │
           │
┌─────────────────────────┐
│ API Layer (FastAPI)                 │
│ - /portfolio/recalculate          │
│ - /contract/benchmark             │
│ - /export/*                       │
└─────────────────────────┘
           │
           │
┌─────────────────────────┐
│ Core Engines                       │
│ - Final Risk Engine                │
│ - NLP Contract Module              │
│ - ML Models (CNN, TFT, PINN, GNN) │
└─────────────────────────┘
           │
           │
┌─────────────────────────┐
│ Data Layer                         │
│ - SQLite/PostgreSQL                │
│ - Benchmark Database               │
│ - File Storage                     │
└─────────────────────────┘
```

## Key Components

### Final Engine
- Portfolio recalculation
- Risk aggregation
- Covenant validation
- Refinancing risk assessment
- Recommendation generation

### NLP Module
- Document parsing (LayoutLM)
- Named entity recognition (spaCy)
- Clause classification (Legal-BERT)
- Risk scoring
- Benchmark comparison

### ML Models
- **Siamese CNN**: Satellite change detection
- **TFT**: Revenue forecasting
- **PINN**: Bridge fatigue and pavement degradation
- **GNN**: Portfolio contagion analysis
- **XGBoost/LightGBM**: Credit risk baseline

## Data Flow

1. User submits portfolio via Streamlit or API
2. Final Engine processes deals
3. NLP module analyzes contracts (if provided)
4. ML models make predictions
5. Results aggregated and displayed
6. Recommendations generated
7. Results stored in database

## Deployment

### Development
```bash
streamlit run p5_streamlit_app.py
uvicorn api_server:app --reload
```

### Production
```bash
docker-compose up --build
```