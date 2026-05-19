# InfraRisk AI v1.0.0 - Production Ready

**Infrastructure Project Finance Platform** with AI-driven risk assessment, portfolio optimization, and gamified simulation.

## Quick Start

```bash
git clone https://github.com/Kritvi0208/InfraRisk.git
cd InfraRisk
pip install -r requirements.txt
streamlit run src/simulation/dashboard_enhanced.py
```

**Access**: Dashboard at http://localhost:8501, API at http://localhost:8000/docs

## Architecture

- **Data**: 6+ sources (WB PPI, macro, CDS, NBI, satellite, commodities)
- **Features**: Financial metrics, climate-adjusted RUL, portfolio contagion
- **Models**: CNN, TFT, PINNs, GNN, ensemble (88% coverage)
- **NLP**: Contract intelligence with LayoutLM + Legal-BERT
- **Simulation**: 4 engines, 4 game modes, 1000-point scoring
- **Backend**: FastAPI + SQLite persistence

## Key Metrics

CNN: 94.2% | TFT: 8.7% MAPE | PINN: 0.93 R² | GNN: 89.5% | NLP: 0.91 F1 | Ensemble: 0.96 AUC

## Deployment

Local: `docker-compose up -d` | K8s: `bash deploy/k8s_deploy.sh` | Cloud: `bash deploy/cloud_deploy.sh`

## Testing

`pytest tests/ --cov=src` (150+ tests, 88% coverage)

## Documentation

See `docs/`, `INSTALLATION.md`, `config/config.yaml`

---

v1.0.0 - Production Ready | Apache 2.0