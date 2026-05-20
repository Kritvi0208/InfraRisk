"""Integration tests"""
import pytest
from src.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_assess_project():
    response = client.post("/api/projects/assess", params={
        "project_id": "test-001",
        "features": {"cfads": 30, "debt_service": 25}
    })
    assert response.status_code == 200
    data = response.json()
    assert "dscr" in data
    assert "risk_rating" in data

def test_stress_test():
    response = client.post("/api/portfolio/stress-test", json={
        "id": "portfolio-001"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
