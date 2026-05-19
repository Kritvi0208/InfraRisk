"""API documentation with Swagger specs."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="InfraRisk API v1.0",
    description="Infrastructure Project Finance Platform",
    version="1.0.0",
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = {
        "openapi": "3.0.2",
        "info": {
            "title": "InfraRisk API",
            "version": "1.0.0",
            "description": "Infrastructure project finance AI platform",
        },
        "paths": {
            "/api/projects/predict": {
                "post": {
                    "summary": "Predict project metrics",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "project_id": {"type": "string"},
                                        "capex": {"type": "number"},
                                        "sector": {"type": "string"},
                                    },
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Predictions",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "project_id": {"type": "string"},
                                            "pd": {"type": "number"},
                                            "dscr": {"type": "number"},
                                            "risk_level": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/portfolio/optimize": {
                "post": {
                    "summary": "Optimize portfolio allocation",
                    "responses": {
                        "200": {
                            "description": "Optimized portfolio",
                        }
                    },
                }
            },
            "/api/contracts/analyze": {
                "post": {
                    "summary": "Analyze contract terms",
                    "responses": {
                        "200": {
                            "description": "Contract analysis",
                        }
                    },
                }
            },
            "/api/simulation/run": {
                "post": {
                    "summary": "Run game simulation",
                    "responses": {
                        "200": {
                            "description": "Simulation results",
                        }
                    },
                }
            },
        },
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
