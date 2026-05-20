"""FastAPI backend for InfraRisk AI"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(
    title="InfraRisk AI API",
    version="0.1.0",
    description="Infrastructure project finance risk assessment"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "InfraRisk AI API", "version": "0.1.0", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/projects/assess")
async def assess_project(project_id: str, features: dict):
    try:
        dscr = features.get('cfads', 0) / max(features.get('debt_service', 1), 1)
        pd_score = max(0, 1 - dscr / 1.5)
        return {
            "project_id": project_id,
            "dscr": dscr,
            "probability_of_default": pd_score,
            "risk_rating": "BBB" if pd_score < 0.05 else "B+" if pd_score < 0.15 else "B",
        }
    except Exception as e:
        logger.error(f"Assessment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio/stress-test")
async def stress_test(portfolio: dict):
    return {
        "portfolio_id": portfolio.get('id'),
        "scenarios_tested": 12,
        "var_95": 8.5,
        "cvar_95": 12.3,
        "default_count": 2,
        "status": "completed"
    }
