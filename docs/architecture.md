# Architecture

InfraRisk AI uses a small local stack for submission:

- `api_server.py` exposes FastAPI endpoints
- `p5_streamlit_app.py` provides the dashboard and simulation UI
- `final_engine.py` handles portfolio, export, and scoring logic
- `data/processed/infrarisk.db` stores lightweight persistence

## Runtime Flow

1. Streamlit loads the dashboard.
2. Users trigger simulation or portfolio actions.
3. The API serves reusable portfolio and export endpoints.
4. Results are written to the local SQLite store when needed.