# InfraRisk AI - Getting Started

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL or SQLite
- Docker (optional)

### Setup

1. **Clone Repository**
```bash
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk
```

2. **Install Dependencies**
```bash
pip install -r requirements-app.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run API**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Run Dashboard**
```bash
streamlit run src/dashboard/app.py
```

### Docker Setup

```bash
docker-compose up --build
# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

## Quick Start

### Assess a Project

```python
from src.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

response = client.post("/api/projects/assess", params={
    "project_id": "toll-road-001",
    "features": {
        "cfads": 30000000,
        "debt_service": 25000000
    }
})

print(response.json())
```

### Run Stress Test

```python
response = client.post("/api/portfolio/stress-test", json={
    "id": "portfolio-001"
})

print(response.json())
```

## Project Structure

```
src/
├── api/           # FastAPI backend
├── models/        # ML models (ensemble, TFT, GNN, CNN)
├── features/      # Feature engineering
├── dashboard/     # Streamlit UI
├── simulation/    # Game engine
└── nlp/          # Contract intelligence

tests/            # Unit and integration tests
notebooks/        # EDA and analysis
docs/            # Documentation
data/            # Data directory (DVC-tracked)
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Coverage report
pytest tests/ --cov=src --cov-report=html
```

## Documentation

- `docs/ARCHITECTURE.md` - System design
- `docs/API.md` - API reference
- `notebooks/` - Analysis notebooks

## Support

For issues, check GitHub Issues or contact the team.
