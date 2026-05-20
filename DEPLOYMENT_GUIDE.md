# Deployment Guide - InfraRiskAI Platform

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Testing Framework](#testing-framework)
4. [Docker Deployment](#docker-deployment)
5. [Production Configuration](#production-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.9+ (3.10 recommended)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: 20GB for models and data

### Required Services
- PostgreSQL 12+
- Redis 6.0+
- MLflow 1.20+
- Streamlit (for dashboard)

### Development Tools
```bash
pip install -r requirements_ml.txt
pip install -r requirements_nlp.txt
pip install pytest pytest-cov pytest-xdist
```

---

## Local Development Setup

### Step 1: Clone Repository and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/your-org/InfraRiskAI.git
cd InfraRiskAI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements_ml.txt
pip install -r requirements_nlp.txt
pip install -e .
```

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

**Key Environment Variables to Configure:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `MLFLOW_TRACKING_URI`: MLflow server URL
- `SECRET_KEY`: Application secret for Flask/Streamlit
- `DEBUG`: Set to `False` for production

### Step 3: Initialize Database

```bash
# Create database tables
python -c "from src.data import initialize_db; initialize_db()"

# Run migrations (if applicable)
alembic upgrade head

# Verify connection
python -c "from src.data import validate_db_connection; validate_db_connection()"
```

### Step 4: Download Pre-trained Models

```bash
# Download models from model registry
python scripts/download_models.py

# Verify model checksums
python scripts/verify_models.py

# Expected location: ./models/
```

---

## Testing Framework

### Running Tests

#### Unit Tests Only
```bash
pytest tests/ -m unit -v
```

#### Integration Tests
```bash
pytest tests/ -m integration -v
```

#### All Tests with Coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

#### Parallel Test Execution
```bash
pytest tests/ -n auto  # Uses all CPU cores
```

#### Specific Test File
```bash
pytest tests/test_models.py::TestEnsemble::test_portfolio_prediction -v
```

### Test Coverage Report

Coverage thresholds:
- **Minimum**: 60% overall
- **Target**: 85% for core modules
- **Expected**: 88% current state

View HTML report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Continuous Testing

```bash
# Watch mode - rerun tests on file changes
pytest-watch tests/
```

---

## Docker Deployment

### Step 1: Build Docker Images

```bash
# Build main application image
docker build -t infrarisk:latest .

# Build with specific tag
docker build -t infrarisk:v1.0.0 .

# Verify image
docker images | grep infrarisk
```

### Step 2: Run with Docker Compose

```bash
# Start all services (PostgreSQL, Redis, MLflow, App)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Step 3: Initialize Docker Database

```bash
# Run initialization inside container
docker-compose exec app python -c "from src.data import initialize_db; initialize_db()"

# Verify initialization
docker-compose exec postgres psql -U postgres -d infrarisk -c "SELECT count(*) FROM information_schema.tables;"
```

### Step 4: Access Application

- **Dashboard**: http://localhost:8501
- **API**: http://localhost:5000
- **MLflow UI**: http://localhost:5000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Docker Useful Commands

```bash
# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache

# Execute command in running container
docker-compose exec app python scripts/run_model.py

# Scale services (e.g., 3 instances of worker)
docker-compose up -d --scale worker=3

# Clean up volumes and data
docker-compose down -v
```

---

## Production Configuration

### Environment-Specific Settings

#### Production Environment Variables

```bash
# Production .env
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database - use managed service
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/infrarisk

# Cache - use managed Redis
REDIS_URL=redis://:password@prod-redis.example.com:6379/0

# Tracking
MLFLOW_TRACKING_URI=https://mlflow.example.com
MLFLOW_BACKEND_STORE_URI=postgresql://user:pass@prod-db.example.com/mlflow

# Security
SECRET_KEY=<generate-strong-random-key>
ALLOWED_HOSTS=["app.example.com", "www.example.com"]

# API Keys
WORLD_BANK_API_KEY=<your-key>
EARTH_ENGINE_API_KEY=<your-key>
BLOOMBERG_API_KEY=<your-key>
```

### Security Hardening

1. **SSL/TLS Configuration**
   ```bash
   # Use Let's Encrypt with Certbot
   certbot certonly --standalone -d app.example.com
   
   # Update nginx/reverse proxy with certificate
   ```

2. **Database Security**
   ```bash
   # Use strong passwords
   # Enable SSL connections
   # Restrict network access
   # Regular backups to encrypted storage
   ```

3. **Application Security**
   ```bash
   # Enable HTTPS only
   SECURE_ONLY=True
   SESSION_COOKIE_SECURE=True
   SESSION_COOKIE_HTTPONLY=True
   ```

### Performance Optimization

```bash
# Database connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Cache TTL settings
CACHE_TTL_SHORT=300  # 5 minutes
CACHE_TTL_LONG=3600  # 1 hour

# Model inference
BATCH_SIZE=32
MODEL_CACHE_SIZE=5
```

### Scaling Considerations

- **Horizontal Scaling**: Run multiple app instances behind load balancer
- **Database**: Consider read replicas for analytics queries
- **Cache**: Use Redis cluster for high availability
- **Storage**: Use object storage (S3) for model artifacts
- **Async Tasks**: Deploy separate worker processes with Celery

---

## Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl http://localhost:5000/health

# Database connection
curl http://localhost:5000/health/db

# Cache connectivity
curl http://localhost:5000/health/cache
```

### Log Aggregation

```bash
# View application logs
docker-compose logs app --tail=100

# Export logs to file
docker-compose logs app > app_logs.txt

# Structured logging - JSONified
grep '"level":"ERROR"' app_logs.jsonl
```

### Backup Procedures

```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres infrarisk > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres infrarisk < backup.sql

# Model artifacts backup
tar -czf models_backup.tar.gz ./models/
```

### Maintenance Tasks

```bash
# Database maintenance
docker-compose exec postgres vacuumdb -U postgres infrarisk

# Cache cleanup
redis-cli FLUSHDB  # Use with caution!

# Update dependencies
pip install --upgrade -r requirements_ml.txt

# Refresh models
python scripts/update_models.py
```

---

## Troubleshooting Deployment Issues

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d infrarisk

# Check Redis connection
redis-cli ping
```

### Out of Memory Errors
```bash
# Increase Docker memory
# Edit docker-compose.yml:
# services:
#   app:
#     mem_limit: 4g
```

---

## Support & Additional Resources

- **Documentation**: See README.md and API_REFERENCE.md
- **Issue Tracker**: GitHub Issues
- **Community**: Discussions on GitHub
- **Contact**: support@example.com
