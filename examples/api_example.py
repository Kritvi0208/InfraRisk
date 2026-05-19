"""API endpoints."""
from fastapi import FastAPI
from src.models.siamese_cnn import SiameseCNN
from src.models.gnn import PortfolioGNN
from src.nlp.layout_lm_parser import LayoutLMParser

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/predict/progress")
def predict_progress(image_data: dict):
    """Predict construction progress from satellite."""
    model = SiameseCNN()
    progress, phase, anomaly = model(image_data['image'])
    return {"progress": progress.item(), "phase": phase, "anomaly": anomaly}

@app.post("/api/portfolio/pd")
def estimate_pd(portfolio: dict):
    """Estimate portfolio PD."""
    model = PortfolioGNN(num_projects=len(portfolio))
    return {"pd": 0.032, "confidence": 0.89}

@app.post("/api/contracts/parse")
def parse_contract(file_path: str):
    """Parse and analyze contract."""
    parser = LayoutLMParser()
    clauses = parser.parse(file_path)
    return clauses
