# InfraRisk AI: API Reference Guide

**Base URL**: `https://api.infrarisk.local/v1`  
**Authentication**: Bearer token (JWT)  
**Content-Type**: application/json  
**Rate Limit**: 1000 requests/hour per API key

---

## 1. Project Risk Assessment Endpoints

### 1.1 Get Project Risk Score

**Endpoint**: `GET /projects/{project_id}/risk`

**Description**: Retrieve comprehensive risk assessment for a single project including default probability, climate-adjusted metrics, and early warning signals.

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Unique project identifier (e.g., "BR-2015-001") |

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| scenario | string | "base" | Risk scenario: "base", "rcp_26", "rcp_45", "rcp_85" |
| include_forecast | boolean | false | Include 12-month revenue forecast quantiles |
| include_contagion | boolean | false | Include portfolio contagion factor |

**Request Example**:
```bash
curl -X GET "https://api.infrarisk.local/v1/projects/BR-2015-001/risk?scenario=rcp_45" \
  -H "Authorization: Bearer eyJhbGc..."
```

**Response (200 OK)**:
```json
{
  "project_id": "BR-2015-001",
  "project_name": "São Paulo Hydroelectric",
  "sector": "hydroelectric_power",
  "country": "Brazil",
  "risk_metrics": {
    "pd_base": 0.021,
    "pd_climate_adjusted": 0.038,
    "confidence_interval_95": [0.015, 0.052],
    "scenario": "rcp_45",
    "model_version": "6.0.1",
    "last_updated": "2024-01-15T09:30:00Z"
  },
  "financial_metrics": {
    "dscr": 1.63,
    "llcr": 2.14,
    "plcr": 3.82,
    "debt_outstanding": 140000000,
    "debt_currency": "USD"
  },
  "climate_metrics": {
    "rca_rul_baseline": 28.2,
    "rca_rul_2050": 24.1,
    "temperature_change_2050": 2.4,
    "precipitation_change_2050": -0.08,
    "climate_adjustment_factor": 0.800
  },
  "early_warning_flags": [
    {
      "flag_type": "climate_rul_degradation",
      "severity": "medium",
      "description": "RUL reduction >15% by 2050 under RCP 4.5"
    }
  ]
}
```

**Error Responses**:

| Status | Error Code | Message |
|--------|-----------|---------|
| 400 | INVALID_PROJECT_ID | Project ID format invalid |
| 404 | PROJECT_NOT_FOUND | Project not found |
| 403 | UNAUTHORIZED | API key invalid |
| 500 | MODEL_INFERENCE_ERROR | Backend error |

---

### 1.2 Batch Project Risk Assessment

**Endpoint**: `POST /projects/batch/risk`

**Request Body**:
```json
{
  "project_ids": ["BR-2015-001", "IN-2018-045"],
  "scenario": "rcp_45",
  "include_forecast": true
}
```

**Response (200 OK)**:
```json
{
  "batch_id": "batch_20240115_1502",
  "status": "completed",
  "total_projects": 2,
  "successful": 2,
  "results": [
    {
      "project_id": "BR-2015-001",
      "pd_base": 0.021,
      "pd_climate_adjusted": 0.038,
      "dscr": 1.63
    }
  ],
  "execution_time_ms": 1247
}
```

---

## 2. Portfolio Analysis Endpoints

### 2.1 Get Portfolio Summary

**Endpoint**: `GET /portfolios/{fund_id}/metrics`

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| scenario | string | "base" | Climate scenario |
| include_stress | boolean | false | Include stress test results |

**Response (200 OK)**:
```json
{
  "fund_id": "fund_12345",
  "fund_name": "Global Infrastructure Fund III",
  "portfolio_summary": {
    "total_projects": 47,
    "total_aum": 4200000000,
    "sector_distribution": {
      "toll_roads": 0.25,
      "power_generation": 0.35,
      "water_utilities": 0.18,
      "ports": 0.12,
      "airports": 0.10
    }
  },
  "risk_metrics": {
    "portfolio_pd_weighted": 0.032,
    "portfolio_pd_systemic": 0.048,
    "systemic_amplification_factor": 1.50,
    "average_dscr": 1.52,
    "dscr_below_1_25x": 0.06
  },
  "climate_risk": {
    "average_rul_2050_rcp_45": 19.1,
    "projects_with_>20pct_rul_decline": 8,
    "climate_risk_exposure": "medium"
  },
  "alerts": [
    {
      "alert_id": "alert_20240115_0001",
      "severity": "high",
      "project_id": "IN-2018-045",
      "alert_type": "revenue_trending_negative",
      "recommendation": "Initiate contact with sponsor"
    }
  ]
}
```

---

### 2.2 Portfolio Contagion Analysis

**Endpoint**: `POST /portfolios/{fund_id}/contagion`

**Request Body**:
```json
{
  "fund_id": "fund_12345",
  "shock_type": "project_default",
  "trigger_project_id": "BR-2015-001"
}
```

**Response (200 OK)**:
```json
{
  "fund_id": "fund_12345",
  "simulation_id": "sim_20240115_0842",
  "final_results": {
    "total_defaults_triggered": 2,
    "cascade_chain_length": 2,
    "portfolio_pd_baseline": 0.032,
    "portfolio_pd_post_shock": 0.057,
    "pd_increase_bps": 250,
    "recovery_at_risk_estimate": 78000000
  }
}
```

---

## 3. Document Processing Endpoints

### 3.1 Upload and Classify Document

**Endpoint**: `POST /documents/classify`

**Request** (multipart/form-data):
```
File: document.pdf
project_id: "BR-2015-001"
```

**Response (200 OK)**:
```json
{
  "document_id": "doc_20240115_1234",
  "project_id": "BR-2015-001",
  "confidence": 0.94,
  "extracted_terms": {
    "loan_amount": 150000000,
    "currency": "USD",
    "tenor_years": 18,
    "interest_rate_percent": 6.25,
    "dscr_covenant_minimum": 1.30,
    "step_in_rights": true
  },
  "risk_classification": {
    "category": "standard_market_terms",
    "confidence": 0.87,
    "risk_score": 0.35
  }
}
```

---

### 3.2 Named Entity Recognition

**Endpoint**: `POST /documents/{document_id}/extract-entities`

**Response (200 OK)**:
```json
{
  "document_id": "doc_20240115_1234",
  "entities": [
    {
      "entity_type": "LOAN_AMOUNT",
      "value": 150000000,
      "unit": "USD",
      "confidence": 0.99
    },
    {
      "entity_type": "DSCR_COVENANT",
      "value": 1.30,
      "confidence": 0.94
    }
  ],
  "extraction_quality_score": 0.94
}
```

---

## 4. Scenario & Stress Test Endpoints

### 4.1 Climate Scenario Analysis

**Endpoint**: `POST /scenarios/climate`

**Request Body**:
```json
{
  "project_id": "BR-2015-001",
  "scenarios": ["rcp_26", "rcp_45", "rcp_85"],
  "output_years": [2030, 2050, 2080]
}
```

**Response (200 OK)**:
```json
{
  "project_id": "BR-2015-001",
  "scenario_results": {
    "rcp_26": {
      "temperature_change_2050": 1.5,
      "rul_2050": 22.3,
      "revenue_impact_2050": -0.05,
      "dscr_stress_2050": 1.55
    },
    "rcp_45": {
      "temperature_change_2050": 2.4,
      "rul_2050": 19.1,
      "revenue_impact_2050": -0.12,
      "dscr_stress_2050": 1.38
    },
    "rcp_85": {
      "temperature_change_2050": 4.1,
      "rul_2050": 14.7,
      "revenue_impact_2050": -0.22,
      "dscr_stress_2050": 1.11
    }
  }
}
```

---

## 5. Model & Inference Endpoints

### 5.1 Get Model Version & Performance

**Endpoint**: `GET /models/active`

**Response (200 OK)**:
```json
{
  "ensemble_version": "6.0.1",
  "deployment_date": "2024-01-10T00:00:00Z",
  "models": [
    {
      "model_name": "xgboost_primary",
      "weight_in_ensemble": 0.40,
      "validation_auc": 0.915,
      "validation_gini": 0.790
    }
  ],
  "overall_ensemble_performance": {
    "validation_auc": 0.942,
    "validation_gini": 0.824,
    "brier_score": 0.019
  }
}
```

---

## 6. Authentication

### 6.1 Bearer Token Generation

**Endpoint**: `POST /auth/token`

**Request**:
```json
{
  "api_key": "sk_live_xxxxxxxxxxxxxxxx",
  "secret": "secret_xxxxxxxxxxxxx"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

## 7. Standard Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| INVALID_REQUEST | 400 | Malformed JSON |
| UNAUTHORIZED | 401 | Invalid API key |
| FORBIDDEN | 403 | Access denied |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMIT_EXCEEDED | 429 | >1000 requests/hour |
| MODEL_INFERENCE_ERROR | 500 | Backend error |
| SERVICE_UNAVAILABLE | 503 | Service offline |

---

## 8. Rate Limiting & Quotas

- **Standard Tier**: 1,000 requests/hour
- **Batch Endpoint**: 500 projects per request
- **File Upload**: 100 MB max; 50 documents/day

---

## 9. Python SDK Example

```python
from infrarisk import Client

client = Client(api_key="sk_live_xxx", api_secret="secret_xxx")

# Get project risk
risk = client.projects.get_risk("BR-2015-001", scenario="rcp_45")
print(f"PD: {risk.pd_base:.1%}, Climate: {risk.pd_climate_adjusted:.1%}")

# Portfolio analysis
portfolio = client.portfolios.get_metrics("fund_12345")
print(f"Portfolio Systemic PD: {portfolio.portfolio_pd_systemic:.1%}")

# Document classification
result = client.documents.classify("path/to/deal.pdf", project_id="BR-2015-001")
print(f"Loan amount: ${result.loan_amount:,.0f}")
```

---

## 10. Changelog

### Version 6.0.1 (2024-01-10)
- Added climate scenario endpoint
- Improved PINN RUL calculation (±0.5 year accuracy)
- Enhanced document NER (12 new entity types)

### Version 6.0 (2024-01-01)
- Portfolio contagion endpoint
- GNN systemic risk
- Rate limit: 1,000/hour
