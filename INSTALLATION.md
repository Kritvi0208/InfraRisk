# InfraRisk AI - Complete Installation Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Setup](#pre-installation-setup)
3. [Installation Steps](#installation-steps)
4. [Database Configuration](#database-configuration)
5. [Initial Configuration](#initial-configuration)
6. [Verification & Testing](#verification--testing)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Hardware Specifications

| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|-----------|
| **CPU Cores** | 4 | 8 | 16+ |
| **RAM** | 16 GB | 32 GB | 64 GB |
| **GPU** | Optional | NVIDIA RTX 2080+ | A100/H100 |
| **Disk Space** | 100 GB | 500 GB | 2+ TB |
| **Network** | 100 Mbps | 1 Gbps | 10 Gbps |

### Software Requirements

**Operating System:**
- Ubuntu 20.04+ / CentOS 8+ / Windows 10+ / macOS 11+

**Runtime Environments:**
```
Python 3.9+
Node.js 14+ (for dashboard)
Docker 20.10+
Docker Compose 1.29+
```

**Database Systems:**
- PostgreSQL 12+
- Redis 6+
- Elasticsearch 7.10+

**Additional Tools:**
- Git 2.30+
- pip/pip3 package manager
- virtualenv or conda

### Python Package Dependencies

Core dependencies are specified in requirements files:
- `requirements_ml.txt`: Machine learning packages
- `requirements_nlp.txt`: NLP packages
- `requirements_phase2.txt`: Phase 2 dependencies

---

## Pre-Installation Setup

### 1. System Preparation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    git \
    curl \
    wget \
    software-properties-common
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum install -y \
    gcc \
    gcc-c++ \
    python3-devel \
    python3-pip \
    git \
    curl \
    wget
```

**Windows (using PowerShell):**
```powershell
# Install Python 3.9+
# Download from https://www.python.org/downloads/

# Install Git
# Download from https://git-scm.com/download/win

# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop
```

### 2. Python Virtual Environment

**Using venv:**
```bash
python3 -m venv infrariskai-env
source infrariskai-env/bin/activate  # On Linux/macOS
# Or on Windows:
infrariskai-env\Scripts\activate
```

**Using Conda:**
```bash
conda create -n infrariskai python=3.9
conda activate infrariskai
```

### 3. Clone Repository

```bash
git clone https://github.com/yourusername/infrariskai.git
cd infrariskai
```

---

## Installation Steps

### Step 1: Install Python Dependencies

**Install ML/Data Science Packages:**
```bash
pip install -r requirements_ml.txt --no-cache-dir
```

**Install NLP Packages:**
```bash
pip install -r requirements_nlp.txt --no-cache-dir
```

**Install Additional Dependencies:**
```bash
pip install -r requirements_phase2.txt --no-cache-dir
```

**Verify Installation:**
```bash
python -c "import tensorflow, torch, sklearn, pandas; print('All imports successful!')"
```

### Step 2: Install System Services via Docker

**Pull Docker Images:**
```bash
docker pull postgres:12
docker pull redis:6
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.10.0
```

**Build Application Docker Image:**
```bash
docker build -t infrariskai:latest .
```

**Verify Docker Installation:**
```bash
docker --version
docker-compose --version
```

### Step 3: Configure Docker Compose Services

Create `.env` file with configuration:

```env
# Database Configuration
POSTGRES_USER=infrarisk_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=infrariskai_db
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PORT=6379
REDIS_PASSWORD=secure_redis_password

# Elasticsearch Configuration
ELASTICSEARCH_PORT=9200
ELASTIC_PASSWORD=secure_elastic_password

# Application Configuration
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=INFO
```

### Step 4: Initialize Docker Services

**Start Services with Docker Compose:**
```bash
docker-compose up -d
```

**Verify Services Running:**
```bash
docker-compose ps
```

Expected output:
```
NAME              STATUS          PORTS
postgres          Up (healthy)    5432/tcp
redis             Up (healthy)    6379/tcp
elasticsearch     Up (healthy)    9200/tcp
```

### Step 5: Download Pre-trained Models

**Create Models Directory:**
```bash
mkdir -p models/phase2
mkdir -p models/phase3
mkdir -p models/phase4
```

**Download Model Weights:**
```bash
# Option 1: From S3
aws s3 cp s3://infrariskai-models/v1.0.0/ models/ --recursive

# Option 2: Manual download from release page
# Download from: https://github.com/yourusername/infrariskai/releases/v1.0.0
# Extract to ./models/ directory

# Verify model files
ls -lh models/phase*
```

**Extract Model Archives (if applicable):**
```bash
cd models
tar -xzf phase2_models.tar.gz
tar -xzf phase3_models.tar.gz
tar -xzf phase4_models.tar.gz
cd ..
```

---

## Database Configuration

### 1. PostgreSQL Setup

**Create Database User (if not created):**
```bash
psql -U postgres -c "CREATE USER infrarisk_user WITH PASSWORD 'secure_password';"
psql -U postgres -c "CREATE DATABASE infrariskai_db OWNER infrarisk_user;"
```

**Set Permissions:**
```bash
psql -U postgres -d infrariskai_db -c "GRANT ALL PRIVILEGES ON SCHEMA public TO infrarisk_user;"
```

### 2. Run Database Migrations

**Initialize Database Schema:**
```bash
python -m alembic upgrade head
```

**Or using Django (if applicable):**
```bash
python manage.py migrate
```

**Load Initial Data:**
```bash
python scripts/load_initial_data.py
```

**Verify Database Connection:**
```bash
python -c "import psycopg2; conn = psycopg2.connect('dbname=infrariskai_db user=infrarisk_user'); print('Database connected!')"
```

### 3. Redis Configuration

**Redis Data Initialization:**
```bash
redis-cli PING  # Should return PONG
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

**Create Cache Keys:**
```bash
python scripts/init_cache.py
```

### 4. Elasticsearch Setup

**Create Indices:**
```bash
python scripts/setup_elasticsearch.py
```

**Verify Elasticsearch:**
```bash
curl -X GET "localhost:9200/_cat/indices?v"
```

---

## Initial Configuration

### 1. Environment Variables

**Create `.env.local` File:**
```bash
cp .env.example .env.local
```

**Edit Configuration:**
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# External APIs (Optional - for production)
FRED_API_KEY=your_fred_api_key
CENSUS_API_KEY=your_census_api_key
BOND_DATA_API_KEY=your_bond_api_key

# Feature Flags
ENABLE_NLP_PROCESSING=true
ENABLE_RISK_SCORING=true
ENABLE_SIMULATION=true
ENABLE_GAMIFICATION=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Performance
MAX_WORKERS=4
BATCH_SIZE=32
```

### 2. Model Configuration

**Create `config/models.yaml`:**
```yaml
models:
  phase2:
    primary_risk:
      model_path: models/phase2/primary_risk_model.h5
      version: 1.0.0
      threshold: 0.5
    secondary_risk:
      model_path: models/phase2/secondary_risk_model.h5
      version: 1.0.0
      threshold: 0.5
  
  phase3:
    pinn_fatigue:
      model_path: models/phase3/pinn_fatigue.pth
      version: 2.0.0
    pinn_pavement:
      model_path: models/phase3/pinn_pavement.pth
      version: 2.0.0
  
  phase4:
    legal_bert:
      model_path: models/phase4/legal_bert_classifier
      version: 1.5.0
    custom_ner:
      model_path: models/phase4/custom_ner_model
      version: 1.5.0

performance:
  batch_size: 32
  num_workers: 4
  gpu_enabled: true
```

### 3. Feature Configuration

**Create `config/features.yaml`:**
```yaml
features:
  market_features:
    enabled: true
    update_frequency: daily
    sources:
      - fred
      - census
      - bond_market
  
  structural_features:
    enabled: true
    extraction_timeout: 300
  
  environmental_features:
    enabled: true
    satellite_processing: false
  
  contract_features:
    enabled: true
    nlp_processing: true
    entity_extraction: true
```

### 4. Logging Configuration

**Logging is auto-configured** - verify setup:
```bash
python -c "import logging; logging.basicConfig(level=logging.INFO); logging.info('Logging configured successfully')"
```

Logs will be written to: `logs/app.log`

---

## Verification & Testing

### 1. Basic Installation Verification

**Run Installation Test:**
```bash
python scripts/verify_installation.py
```

Expected output:
```
✓ Python version: 3.9+
✓ Required packages installed
✓ Database connection: OK
✓ Redis connection: OK
✓ Elasticsearch connection: OK
✓ Models loaded: 17/17
✓ Installation verification complete
```

### 2. Component Testing

**Test Data Pipeline:**
```bash
python -m pytest tests/test_data_pipeline.py -v
```

**Test ML Models:**
```bash
python -m pytest tests/test_models.py -v
```

**Test API Endpoints:**
```bash
python -m pytest tests/test_api.py -v
```

**Test NLP Components:**
```bash
python -m pytest tests/test_nlp.py -v
```

### 3. System Health Check

**Start Application:**
```bash
python run_phase4_demo.py
# Or for production:
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**Health Check Endpoints:**
```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/api/v1/health/db

# Check model availability
curl http://localhost:8000/api/v1/models/status
```

### 4. Performance Verification

**Benchmark Model Inference:**
```bash
python scripts/benchmark_models.py
```

**Expected performance:**
- Single prediction: <500ms
- Batch predictions (100): <5s
- Dashboard load: <3s

### 5. Dashboard Verification

**Start Dashboard:**
```bash
C:\Users\kayri\anaconda3\python.exe -m streamlit run apps\dashboard_v2_complete.py
```

**Access Dashboard:**
- URL: http://localhost:8501
- Verify all visualizations render
- Test interactive components
- Check data export functionality

---

## Troubleshooting

### Common Installation Issues

**Issue: Python Package Installation Fails**
```bash
# Solution 1: Clear pip cache
pip cache purge
pip install -r requirements_ml.txt --no-cache-dir

# Solution 2: Use specific Python version
python3.9 -m pip install -r requirements_ml.txt

# Solution 3: Install system dependencies
sudo apt-get install python3-dev
```

**Issue: Docker Compose Services Won't Start**
```bash
# Check Docker daemon
docker info

# View Docker logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Issue: Database Connection Error**
```bash
# Test PostgreSQL connection
psql -h localhost -U infrarisk_user -d infrariskai_db -c "SELECT 1"

# Check connection string
echo $DATABASE_URL

# Reset database
docker-compose exec postgres psql -U postgres -c "DROP DATABASE infrariskai_db;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE infrariskai_db OWNER infrarisk_user;"
```

**Issue: Models Not Loading**
```bash
# Verify model files exist
ls -lh models/phase*/

# Check model paths in config
cat config/models.yaml

# Re-download models
python scripts/download_models.py

# Test model loading
python -c "from models.load import load_models; load_models()"
```

**Issue: Out of Memory Errors**
```bash
# Reduce batch size in config
# models.yaml: batch_size: 16  (reduced from 32)

# Restart application
docker-compose restart

# Monitor memory
watch -n 1 free -m
```

**Issue: Dashboard Not Responsive**
```bash
# Restart Streamlit
pkill -f streamlit
C:\Users\kayri\anaconda3\python.exe -m streamlit run apps\dashboard_v2_complete.py --logger.level=debug

# Clear cache
rm -rf ~/.streamlit/cache/
```

### Verification Commands

**Check All Services:**
```bash
docker-compose ps
python scripts/verify_installation.py
curl http://localhost:8000/health
```

**Check Logs:**
```bash
# Application logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f

# System logs
journalctl -u docker -f
```

**Performance Check:**
```bash
# CPU/Memory usage
top

# Disk usage
df -h

# Network connections
netstat -an | grep LISTEN
```

---

## Post-Installation Steps

### 1. Security Hardening

- [ ] Change all default passwords
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up API rate limiting
- [ ] Enable audit logging

### 2. Backup Configuration

- [ ] Configure automated database backups
- [ ] Test backup restoration
- [ ] Setup model artifact backups

### 3. Monitoring Setup

- [ ] Configure application monitoring
- [ ] Setup performance dashboards
- [ ] Configure alert thresholds
- [ ] Test alert notifications

### 4. User Management

- [ ] Create admin accounts
- [ ] Configure role-based access control
- [ ] Setup authentication providers
- [ ] Configure API keys for integrations

---

## Next Steps

After successful installation:

1. Review [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md) for pre-launch verification
2. Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment
3. Consult [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for advanced diagnostics
4. Read [API_REFERENCE.md](API_REFERENCE.md) for API documentation

---

## Support & Documentation

- **Installation Issues:** Check Troubleshooting section above
- **API Documentation:** See [API_REFERENCE.md](API_REFERENCE.md)
- **Architecture Overview:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Version Information

**Installation Guide Version:** 1.0.0  
**InfraRisk AI Version:** 1.0.0  
**Last Updated:** 2024  
**Python Required:** 3.9+  
**Docker Required:** 20.10+

---

**Installation Complete!** You are now ready to use InfraRisk AI. Start with the Quick Start guide or access the dashboard at `http://localhost:8501`.
