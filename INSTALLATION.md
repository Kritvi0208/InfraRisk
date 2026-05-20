# InfraRisk AI - Installation Guide

## System Requirements

- Python 3.9+
- Docker 20.10+
- PostgreSQL 12+ (optional, for production)
- Redis 6+ (optional, for caching)

## Quick Installation

### 1. Clone and Setup

```bash
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements-app.txt
pip install -r requirements_ml.txt
pip install -r requirements_nlp.txt
```

### 3. Run Applications

**Dashboard:**
```bash
streamlit run p5_streamlit_app.py
```

**API Server:**
```bash
uvicorn api_server:app --reload
```

**Docker:**
```bash
docker-compose up --build
```

## Database Setup

The application uses SQLite by default. For PostgreSQL:

```bash
docker-compose up postgres
```

## Verification

```bash
python -m pytest test_final_engine.py -v
python -m pytest test_models.py -v
python -m pytest test_nlp.py -v
```

## Troubleshooting

- If imports fail: ensure `requirements_*.txt` files are installed
- If Streamlit won't start: `pip install --upgrade streamlit plotly`
- If tests fail: check Python version is 3.9+