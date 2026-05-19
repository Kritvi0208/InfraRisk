#!/bin/bash
set -e
echo "Starting InfraRisk Lab..."
pip install -q -r requirements.txt
mkdir -p data/raw/{ppi,worldbank,nbi} data/cache
echo "Starting API backend (port 8000)..."
python -m uvicorn src.api.backend:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "Starting dashboard (port 8501)..."
streamlit run src/simulation/dashboard_enhanced.py --logger.level=warning &
DASH_PID=$!
echo "Dashboard: http://localhost:8501"
echo "API: http://localhost:8000/docs"
trap "kill $API_PID $DASH_PID" EXIT
wait