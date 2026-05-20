# InfraRisk AI - Infrastructure Risk Management Platform

A comprehensive platform for infrastructure risk assessment, combining geospatial analytics, macroeconomic modeling, engineering risk quantification, and credit risk assessment for Development Finance Institutions (DFIs) and commercial banks.

## Submission Snapshot

- Run locally: `C:\Users\kayri\anaconda3\python.exe -m streamlit run p5_streamlit_app.py`
- Run API: `C:\Users\kayri\anaconda3\python.exe -m uvicorn api_server:app --reload`
- Docker: `docker compose up --build`
- Docs: `mkdocs build`
- Notebooks: open the three files in `notebooks/`

## Project Overview

InfraRisk AI integrates multiple risk dimensions:
- **Geospatial Intelligence**: Location-based risk, terrain analysis, climate/natural disaster risk
- **Construction Risk**: Cost overrun modeling, schedule delay analysis, technical risk assessment
- **Macroeconomic Scenarios**: Interest rates, inflation, FX volatility, sovereign risk
- **Debt Structuring**: Optimal financing mix, DSCR analysis, tenor optimization
- **Portfolio Stress Testing**: Multi-scenario impact analysis across transportation, energy, and social infrastructure
- **InfraRisk Lab**: Gamified simulation of construction delays and refinancing crises
- **Credit Risk Assessment**: Bankable risk ratings for infrastructure projects

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│           InfraRisk AI Frontend (React)                  │
│  Dashboard | Scenario Builder | Lab Simulation | Reports │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│         FastAPI Backend (Core Analytics Engine)         │
├─────────────────────────────────────────────────────────┤
│ • Geospatial Analytics Module                            │
│ • Construction Risk Model                               │
│ • Macroeconomic Scenario Engine                         │
│ • Debt Structuring Optimizer                            │
│ • Portfolio Stress Testing Engine                       │
│ • Credit Risk Assessment Module                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           Data Layer & External APIs                     │
├─────────────────────────────────────────────────────────┤
│ • PostgreSQL/SQLite (Project, Scenario, Risk Data)      │
│ • World Bank API (Economic indicators)                  │
│ • IMF API (Sovereign risk, macroeconomic data)          │
│ • Open Street Map (Geospatial data)                     │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI |
| Frontend | React.js, Recharts, Leaflet |
| Data Processing | Pandas, NumPy, GeoPandas |
| ML/Analytics | Scikit-learn, XGBoost |
| Database | SQLite (Dev), PostgreSQL (Prod) |
| Deployment | Docker, GitHub |

## Project Structure

```
infrariskai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── database.py
│   │   │   ├── schemas.py
│   │   │   └── entities.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── geospatial.py
│   │   │   ├── construction_risk.py
│   │   │   ├── macroeconomic.py
│   │   │   ├── debt_structuring.py
│   │   │   ├── stress_testing.py
│   │   │   └── credit_risk.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── geospatial_service.py
│   │   │   ├── construction_service.py
│   │   │   ├── macro_service.py
│   │   │   ├── debt_service.py
│   │   │   └── risk_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── calculations.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── SCENARIO_DEFINITIONS.md
│   └── ASSUMPTIONS.md
└── docker-compose.yml
```

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## Features

### Part 1: System Architecture ✅
- Modular analytics engine
- Integrated data layer
- Scalable microservices design

### Part 2: Geospatial Intelligence 🔄
- Location risk scoring
- Terrain analysis
- Climate/natural disaster risk
- Environmental impact assessment

### Part 3: Macroeconomic Scenarios 🔄
- Interest rate modeling
- Inflation impact analysis
- FX volatility assessment
- Sovereign risk indicators

### Part 4: Debt Structuring 🔄
- Optimal debt mix calculation
- DSCR analysis
- LC/ED ratio optimization
- Tenor structuring

### Part 5: Portfolio Stress Testing 🔄
- Multi-scenario analysis
- Portfolio-level impact modeling
- Sensitivity analysis
- Risk aggregation

### Part 6: InfraRisk Lab 🔄
- Gamified simulation
- Construction delay scenarios
- Refinancing crisis modeling
- Interactive learning

### Part 7: Credit Risk Assessment 🔄
- Bankable risk ratings
- 12-scenario validation
- Real project finance modeling
- Basel III alignment

### Part 8: Documentation & Submission ⏳
- API documentation
- User guides
- Architecture diagrams
- GitHub submission

## Development Timeline

| Day | Deliverable | Status |
|-----|-------------|--------|
| 1 | Architecture + Backend Setup | 🔄 In Progress |
| 2 | Geospatial & Construction Risk | ⏳ Pending |
| 3 | Macroeconomic & Validation | ⏳ Pending |
| 4 | Debt Structuring & Stress Testing | ⏳ Pending |
| 5 | Lab, Validation & Documentation | ⏳ Pending |

## Database Schema

### Projects
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location GEOGRAPHY,
    sector VARCHAR(100),
    project_value DECIMAL,
    currency VARCHAR(3),
    created_at TIMESTAMP
);
```

### Risk Assessments
```sql
CREATE TABLE risk_assessments (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    geospatial_score FLOAT,
    construction_risk FLOAT,
    macro_risk FLOAT,
    overall_rating VARCHAR(10),
    created_at TIMESTAMP
);
```

## API Endpoints (Planned)

### Geospatial
- `POST /api/geospatial/analyze` - Analyze location risk
- `GET /api/geospatial/climate` - Climate risk data

### Construction Risk
- `POST /api/construction/estimate` - Estimate cost/schedule variance
- `GET /api/construction/benchmarks` - Industry benchmarks

### Macroeconomic
- `POST /api/macro/scenarios` - Create scenarios
- `GET /api/macro/forecasts` - Economic forecasts

### Debt Structuring
- `POST /api/debt/optimize` - Optimize financing structure
- `GET /api/debt/metrics` - Financial metrics

### Stress Testing
- `POST /api/stress/run` - Run stress test
- `GET /api/stress/results` - Test results

### Credit Risk
- `POST /api/credit/assess` - Assess credit risk
- `GET /api/credit/ratings` - Risk ratings

## Compliance & Standards

- **Credit Risk Framework**: Basel III aligned
- **Project Finance Standards**: IFC Performance Standards
- **Data Privacy**: GDPR compliant
- **Infrastructure Classification**: UNEP green infrastructure taxonomy

## Team & Support

**Project Owner**: Zetheta Algorithms Private Limited  
**Submission Deadline**: 30 days from enrollment  
**Certificate**: Certificate of Project Work Experience (15 days)

## Confidentiality Notice

⚠️ **PRIVATE & CONFIDENTIAL**
- This project and all work are strictly confidential
- GitHub repository is PRIVATE
- No public sharing of code, concepts, or implementations
- All work remains property of Zetheta Algorithms Private Limited
- Transfer ownership to @ZethetaIntern on Day 15-30 for final submission

---

**Status**: Day 1 - Architecture & Backend Setup 🚀
