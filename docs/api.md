# API Reference

The backend API is implemented in `src/api/backend.py` and exposed through FastAPI.

## Main endpoints

- `GET /health` - service health probe.
- `POST /api/v1/projects/predict` - project-level PD and DSCR prediction.
- `POST /api/v1/portfolio/metrics` - portfolio-level metrics and risk summary.
- `POST /api/v1/contracts/analyze` - contract upload and clause analysis.
- `POST /api/v1/simulation/run` - Monte Carlo simulation stub for stress testing.
- `GET /api/v1/models/status` - model readiness summary.

## Local usage

Start the service with:

```bash
uvicorn src.api.backend:app --reload
```

Then open:

- FastAPI Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

For a lightweight documentation helper, see [api_swagger.py](api_swagger.py).
