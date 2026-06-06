FROM python:3.11

WORKDIR /app

# COPY deliverables/requirements_ml.txt .

# RUN pip install -r requirements_ml.txt
COPY deliverables/requirements_ml.txt /tmp/requirements_ml.txt

RUN pip install -r /tmp/requirements_ml.txt

COPY . .

EXPOSE 8000

# CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["uvicorn", "src.core.api_server:app", "--host", "0.0.0.0", "--port", "8000"]