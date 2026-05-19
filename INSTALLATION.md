# Installation

## Quick Setup

```bash
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ --cov=src

# Start dashboard
streamlit run src/simulation/dashboard.py
```

## Docker Deployment

```bash
docker-compose up -d
```

## Configuration

Edit `config/config.yaml` for data sources, model parameters, deployment settings.
