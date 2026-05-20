# API Reference

## Base URL
`http://localhost:8000`

## Endpoints

### Health Check
```
GET /health
Response: {"status": "healthy"}
```

### Project Assessment
```
POST /api/projects/assess?project_id=string&features=object

Request:
{
  "project_id": "toll-road-001",
  "features": {
    "cfads": 30000000,
    "debt_service": 25000000,
    "debt": 300000000,
    "capex": 500000000
  }
}

Response:
{
  "project_id": "toll-road-001",
  "dscr": 1.42,
  "probability_of_default": 0.024,
  "risk_rating": "A"
}
```

### Portfolio Stress Test
```
POST /api/portfolio/stress-test

Request:
{
  "id": "portfolio-001",
  "projects": [...],
  "scenarios": ["rate_shock", "demand_shock", "sov_downgrade"]
}

Response:
{
  "portfolio_id": "portfolio-001",
  "scenarios_tested": 12,
  "var_95": 8.5,
  "cvar_95": 12.3,
  "default_count": 2,
  "status": "completed"
}
```

## Error Handling

All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad request
- 404: Not found
- 500: Server error

Error responses:
```json
{
  "detail": "Error description",
  "status": 500,
  "timestamp": "2024-05-20T11:45:00Z"
}
```
