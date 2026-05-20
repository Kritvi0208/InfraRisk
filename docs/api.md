# InfraRisk AI - API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Portfolio Management

#### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

#### `POST /portfolio/recalculate`
Recalculate portfolio metrics and risk.

**Request:**
```json
{
  "deals": [
    {
      "deal_id": "SOLAR-IN-001",
      "name": "Gujarat Solar Farm",
      "sector": "Energy",
      "country": "India",
      "capex": 150000000,
      "revenue_annual": 28000000,
      "opex_annual": 7500000,
      "debt_amount": 95000000,
      "equity_amount": 55000000,
      "coupon_rate": 0.075,
      "tenor_years": 18,
      "probability_of_default": 0.045
    }
  ],
  "persist": true
}
```

**Response:**
```json
{
  "deal_results": [...],
  "sector_concentration": {...},
  "country_concentration": {...},
  "pd_rejections": [],
  "gnn_propagation": {...},
  "recommendations": [...],
  "game_score": {...},
  "shap_explanations": {...}
}
```

### Contract Analysis

#### `POST /contract/benchmark`
Get benchmark comparison for a contract.

**Request:**
```json
{
  "sector": "Energy",
  "country": "India",
  "project_value": 150000000,
  "tenor_years": 18
}
```

## Error Handling

API returns standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 500: Internal Server Error

Error responses:
```json
{
  "detail": "Error message"
}
```

## Authentication

No authentication required for demo version.
Production deployment should add JWT token authentication.

## Rate Limiting

No rate limiting in current version.
Recommended: 100 requests/minute per client.

## Versioning

Current API version: 1.0.0