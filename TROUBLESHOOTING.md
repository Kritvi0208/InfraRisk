# Troubleshooting Guide - InfraRiskAI Platform

This guide covers common issues, error messages, and solutions for the InfraRiskAI platform.

---

## Table of Contents

1. [Installation & Setup Issues](#installation--setup-issues)
2. [Runtime Errors](#runtime-errors)
3. [Database Problems](#database-problems)
4. [Model & ML Issues](#model--ml-issues)
5. [Performance & Scalability](#performance--scalability)
6. [Docker & Deployment](#docker--deployment)
7. [API Issues](#api-issues)
8. [Frequently Asked Questions](#frequently-asked-questions)

---

## Installation & Setup Issues

### Issue: Python Version Incompatibility

**Error Message**:
```
python: command not found
or
Python 3.8 not supported
```

**Solution**:
- InfraRiskAI requires Python 3.9+
- Check version: `python --version`
- Install correct version from python.org or using package manager
- Create virtual environment with correct Python: `python3.10 -m venv venv`
- Alternatively, use pyenv for multiple Python versions

**Verification**:
```bash
python --version  # Should show 3.9 or higher
which python3.10  # Locate specific version
```

---

### Issue: Missing Dependencies

**Error Message**:
```
ModuleNotFoundError: No module named 'torch'
or
ImportError: cannot import name 'TFT' from 'src.models'
```

**Solution**:
```bash
# Reinstall all dependencies
pip install --upgrade pip
pip install -r requirements_ml.txt
pip install -r requirements_nlp.txt

# For specific issues with PyTorch (GPU):
# CPU version (smaller, for dev/test):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU version (CUDA 11.8):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verification**:
```bash
python -c "import torch; print(torch.__version__)"
python -c "from src.models import TFT; print('TFT model loaded')"
```

---

### Issue: Virtual Environment Not Activated

**Symptoms**:
- `pip install` fails or installs to system Python
- Module imports fail
- Commands not found

**Solution**:
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
which python  # Should point to venv directory
```

---

### Issue: Environment Variables Not Loading

**Error Message**:
```
KeyError: 'DATABASE_URL'
or
Failed to connect to database: NoneType
```

**Solution**:
```bash
# Check if .env file exists
ls -la .env

# Load environment variables
export $(cat .env | xargs)

# Or use python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DATABASE_URL'))"

# For interactive shell
source .env
env | grep DATABASE
```

---

## Runtime Errors

### Issue: Out of Memory Error

**Error Message**:
```
MemoryError: Unable to allocate X GB
or
CUDA out of memory
```

**Solution**:
```bash
# Reduce batch size
export BATCH_SIZE=8  # Default 32

# Reduce model cache
export MODEL_CACHE_SIZE=2  # Default 5

# Clear cache before running
python -c "import torch; torch.cuda.empty_cache()"

# Check available memory
free -h  # Linux
vm_stat  # macOS
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory  # Windows

# Monitor during execution
watch -n 1 nvidia-smi  # GPU memory
```

---

### Issue: Data Loading Failure

**Error Message**:
```
FileNotFoundError: data/raw/climate_data.csv not found
or
IOError: Cannot read parquet file
```

**Solution**:
```bash
# Verify data structure
ls -R data/

# Download required data
python scripts/download_data.py

# Verify file integrity
python -c "import pandas as pd; df = pd.read_parquet('data/raw/climate_data.parquet'); print(f'Loaded {len(df)} rows')"

# Check file permissions
chmod 644 data/raw/*

# Convert between formats if needed
python scripts/convert_data_format.py --from csv --to parquet
```

---

### Issue: Model Loading Error

**Error Message**:
```
RuntimeError: Error(s) in loading state_dict
or
torch.serialization.PicklingError
```

**Solution**:
```bash
# Verify model file exists and is valid
python -c "import torch; torch.load('models/tft_model.pth')"

# Check model checksum
sha256sum models/tft_model.pth

# Redownload model if corrupted
python scripts/download_models.py --force --model tft

# If compatibility issue:
# Update PyTorch version to match model's training version
pip install torch==2.0.1
```

---

### Issue: NLP Model Fails During Inference

**Error Message**:
```
RuntimeError: CUDA runtime error
or
transformers.modeling_utils.ContextManagersError
```

**Solution**:
```bash
# Use CPU for NLP models
export DEVICE=cpu

# Or specify in code:
from src.nlp import BertClassifier
classifier = BertClassifier(device='cpu')

# Update transformers library
pip install --upgrade transformers

# Clear model cache
rm -rf ~/.cache/huggingface/transformers/
```

---

## Database Problems

### Issue: Database Connection Refused

**Error Message**:
```
psycopg2.OperationalError: could not connect to server
or
Connection refused (111)
```

**Solution**:
```bash
# Check PostgreSQL is running
systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS
services.msc  # Windows - look for PostgreSQL

# Verify connection details in .env
psql -h localhost -U postgres -d postgres -c "SELECT 1;"

# Test with explicit credentials
psql -h 127.0.0.1 -p 5432 -U postgres -W -c "\l"

# Restart database
sudo systemctl restart postgresql  # Linux
brew services restart postgresql  # macOS

# Check if port is already in use
lsof -i :5432
netstat -an | grep 5432  # Windows
```

---

### Issue: Database Initialization Fails

**Error Message**:
```
ERROR: relation "assets" already exists
or
column "id" does not exist
```

**Solution**:
```bash
# Drop and recreate database (development only!)
dropdb infrarisk
createdb infrarisk
python -c "from src.data import initialize_db; initialize_db()"

# If using migrations:
alembic downgrade base
alembic upgrade head

# Check current database state
psql -d infrarisk -c "SELECT table_name FROM information_schema.tables;"

# Backup data before operations
pg_dump infrarisk > backup.sql
```

---

### Issue: Migration Issues

**Error Message**:
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution**:
```bash
# Check migration status
alembic current

# View available migrations
alembic history

# Upgrade to latest
alembic upgrade head

# Downgrade to specific version
alembic downgrade <revision>

# If stuck, reset to base
alembic downgrade base
alembic upgrade head
```

---

## Model & ML Issues

### Issue: Training Takes Too Long

**Problem**:
- Model training exceeds expected time
- GPU not being utilized

**Solution**:
```bash
# Enable GPU
python scripts/train_model.py --device cuda

# Verify GPU availability
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"

# Monitor GPU usage
nvidia-smi -l 1  # Refresh every 1 second

# Reduce training parameters
export EPOCHS=50  # Instead of 100
export LEARNING_RATE=0.01

# Use distributed training
python -m torch.distributed.launch --nproc_per_node=2 scripts/train_model.py
```

---

### Issue: Poor Model Accuracy

**Symptoms**:
- Model predictions not matching expected accuracy
- Validation loss not decreasing

**Solution**:
```bash
# Verify training data quality
python scripts/validate_training_data.py

# Check for data leakage
python -c "from src.data import check_data_leakage; check_data_leakage()"

# Examine feature distributions
python scripts/analyze_features.py --plot

# Verify model is using correct features
python -c "from src.models import TFT; m = TFT(); print(m.feature_names)"

# Retrain with original hyperparameters
python scripts/train_model.py --config config/model_tft.yaml --resume-from checkpoint_best.pt

# Check for overfitting
python scripts/plot_learning_curves.py
```

---

### Issue: Prediction Results Are NaN

**Error Message**:
```
RuntimeWarning: invalid value encountered in log
or
Output contains NaN values
```

**Solution**:
```bash
# Check input data for NaN
python -c "import pandas as pd; df = pd.read_csv('test_data.csv'); print(df.isnull().sum())"

# Handle missing values
python scripts/impute_missing_values.py

# Check for division by zero in features
grep -r "/ 0" src/features/

# Normalize features to valid range
python -c "from src.data import normalize_features; normalize_features()"

# Use preprocessing to clip values
python scripts/preprocess_data.py --clip-values
```

---

## Performance & Scalability

### Issue: Slow API Responses

**Symptoms**:
- API endpoint takes >500ms
- Timeouts on large batch requests

**Solution**:
```bash
# Profile API endpoint
python -m cProfile -s cumulative scripts/run_api.py

# Check database query performance
python -c "from src.data import analyze_slow_queries; analyze_slow_queries()"

# Enable caching
export CACHE_ENABLED=True
export CACHE_TTL=300

# Reduce model inference batch size if VRAM limited
export INFERENCE_BATCH_SIZE=8

# Check API logs for bottlenecks
tail -f logs/api.log | grep "duration"
```

---

### Issue: High Memory Usage

**Symptoms**:
- Memory grows unbounded during execution
- Eventually causes OOM crash

**Solution**:
```bash
# Monitor memory usage
python -m memory_profiler scripts/run_inference.py

# Clear model cache periodically
python -c "from src.models import clear_cache; clear_cache()"

# Use generators instead of loading full datasets
# Convert list comprehension to generator expressions
# Check for circular references in objects

# Profile memory
import tracemalloc
tracemalloc.start()
# ... run code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Peak: {peak / 1024 / 1024:.1f}MB")
```

---

### Issue: CPU Constantly at 100%

**Symptoms**:
- High CPU usage even when idle
- Fan noise increases

**Solution**:
```bash
# Identify high-CPU process
top  # Linux/macOS
tasklist /v | sort /+65  # Windows

# Check for runaway threads
python -c "import threading; print(threading.enumerate())"

# Reduce number of workers
export NUM_WORKERS=2

# Check for infinite loops in code
python -m pdb scripts/run_app.py

# Profile CPU usage
python -m cProfile -s cumulative scripts/run_app.py > profile.txt
```

---

## Docker & Deployment

### Issue: Container Fails to Start

**Error Message**:
```
docker: Error response from daemon: OCI runtime error
or
Container exited with code 1
```

**Solution**:
```bash
# Check logs
docker-compose logs app

# Run container interactively to debug
docker-compose run --rm app bash

# Rebuild container
docker-compose down
docker-compose build --no-cache

# Check Docker daemon
systemctl status docker
docker system info

# Increase Docker resource limits
# Edit docker-compose.yml:
# services:
#   app:
#     mem_limit: 4g
#     cpus: 2
```

---

### Issue: Port Already in Use

**Error Message**:
```
ERROR: for app  Cannot start service app: Ports are not available
```

**Solution**:
```bash
# Find process using port
lsof -i :5000  # Linux/macOS
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Or use different port
docker-compose -f docker-compose.yml -p infrarisk_alt up

# Or modify port in docker-compose.yml
# ports:
#   - "5001:5000"
```

---

### Issue: Docker Volume Permission Denied

**Error Message**:
```
Permission denied: '/app/data'
or
cannot open directory for reading: Permission denied
```

**Solution**:
```bash
# Fix volume permissions
sudo chmod 755 /path/to/volume

# Or use docker user
# Add to Dockerfile:
# RUN useradd -m appuser
# USER appuser

# Or explicitly set ownership
docker-compose exec app chown -R app:app /app/data
```

---

## API Issues

### Issue: Authentication Failure

**Error Message**:
```
401 Unauthorized
or
Invalid API key
```

**Solution**:
```bash
# Verify API key is set
echo $API_KEY

# Check credentials in .env
grep API_KEY .env

# Regenerate API key
python scripts/generate_api_key.py

# Pass API key correctly
curl -H "Authorization: Bearer $API_KEY" http://localhost:5000/api/assets
```

---

### Issue: CORS Issues

**Error Message**:
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**:
```bash
# Add to .env
ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com

# Or in code:
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])

# For debugging, log CORS headers
curl -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://localhost:5000/api/assets -v
```

---

## Frequently Asked Questions

### Q: How do I update models without downtime?

**A**: Use blue-green deployment:
```bash
# Deploy new version to alternate endpoint
docker-compose -f docker-compose.green.yml up -d

# Test new version
curl http://localhost:5001/health

# Switch load balancer to new version
# nginx config: upstream backend { server green:5000; }

# Remove old version
docker-compose -f docker-compose.blue.yml down
```

---

### Q: Can I use InfraRiskAI on Windows without WSL?

**A**: Limited support. Recommended:
- Use WSL2 for native Linux environment
- Or run only via Docker
- Or develop on native Windows but deploy on Linux

---

### Q: What's the typical response time for predictions?

**A**: 
- Single asset: 145ms average
- Batch of 100 assets: 2-3 seconds
- Large portfolio (10,000 assets): 3-5 minutes (async job)

---

### Q: How often should models be retrained?

**A**: 
- Climate models: Monthly (new weather data)
- Financial models: Weekly
- Network models: As needed (when topology changes)
- Full retraining cycle: Quarterly

---

### Q: What's the minimum hardware for production?

**A**: 
- **CPU**: 4 cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB SSD
- **Database**: Managed PostgreSQL service recommended

---

### Q: How do I debug a failing model prediction?

**A**: 
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Trace prediction through model
python scripts/trace_prediction.py --asset-id <id> --verbose

# Check intermediate outputs
python -c "from src.models import debug_prediction; debug_prediction('asset_123')"
```

---

## Getting Additional Help

- Check application logs: `docker-compose logs -f`
- Review error stack traces carefully
- Search existing issues: GitHub Issues
- Contact support: support@example.com
- Community discussions available on GitHub

---

**Last Updated**: 2024
**Version**: 1.0
