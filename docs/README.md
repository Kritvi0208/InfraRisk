# InfraRisk Documentation

This folder is the documentation home for the submission.

## What to read first

1. [Technical Report](TECHNICAL_REPORT.md) - implementation status, data provenance, validation, and remaining gaps.
2. [Data Integration Guide](DATA_INTEGRATION.md) - loader behavior, data contracts, and source handling.
3. [API Reference](api.md) - backend endpoints and how to launch the interactive API docs.

## Build the docs site

```bash
pip install mkdocs
mkdocs serve
```

## Interactive API docs

Run the FastAPI backend and open `/docs`, or launch the helper in [api_swagger.py](api_swagger.py).
