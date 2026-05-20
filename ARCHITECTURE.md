# InfraRisk AI: System Architecture & Deployment

---

## 1. High-Level System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                    │
│           JWT Authentication | Rate Limiting | Logging       │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼──┐    ┌────▼────┐  ┌───▼───┐
    │Feature│    │ Models  │  │ NLP   │
    │ Store │    │ Service │  │Pipeline
    │(Cache)│    │(Inference) │       │
    └───┬──┘    └────┬────┘  └───┬───┘
        │            │           │
   ┌────▼────────────▼───────────▼────┐
   │  PostgreSQL Analytical Database   │
   │      (Timeseries + Documents)     │
   │         50GB+ capacity            │
   └────┬────────────────────────┬─────┘
        │                        │
   ┌────▼───┐  ┌──────────┐  ┌──▼──┐
   │ S3 Blob│  │Redis     │  │MLflow
   │Storage │  │Cache     │  │Model
   │(Images)│  │Layer     │  │Registry
   └────────┘  └──────────┘  └──────┘
```

---

## 2. Component Descriptions

### 2.1 API Gateway (FastAPI)
- **Framework**: FastAPI with Uvicorn (ASGI server)
- **Features**:
  - JWT-based authentication with role-based access control (RBAC)
  - Rate limiting (1,000 requests/hour per API key)
  - Request/response logging and audit trail
  - Automatic request validation via Pydantic
  - OpenAPI/Swagger documentation
- **Deployment**: Kubernetes with auto-scaling (2-10 replicas based on CPU/memory)
- **Availability**: 99.9% SLA with multi-region failover

### 2.2 Feature Store (Redis Cache Layer)
- **Purpose**: Cache computed features (financial ratios, spectral indices, macro aggregates)
- **Update Frequency**: Daily, post-pipeline completion (05:00 UTC)
- **Capacity**: 32GB (in-memory)
- **TTL**: 24 hours for features; 1 hour for real-time market data
- **Replication**: Master-replica setup for redundancy
- **Monitoring**: Eviction policy (LRU), hit/miss rates

### 2.3 Models Service (Inference Engine)
- **Deployment**: NVIDIA Triton Inference Server (GPU-accelerated)
- **Models Running**:
  1. **XGBoost**: CPU-bound, batch processing
  2. **Neural Network**: GPU-accelerated (TensorFlow 2.12)
  3. **Random Forest**: CPU-bound, parallelized
  4. **TFT (Revenue Forecasting)**: GPU-optimized
  5. **PINN (Climate-Adjusted RUL)**: GPU-intensive (JAX)
  6. **GNN (Portfolio Contagion)**: GPU-optimized (PyTorch Geometric)
- **Load Balancing**: Round-robin across 4 inference workers
- **Caching**: Model outputs cached in Redis (1-hour TTL)
- **Latency**: <200ms per project risk score (p99)

### 2.4 NLP Pipeline
- **Components**:
  - LayoutLM v2 for document layout understanding
  - Custom NER model (Legal-BERT + CRF)
  - Document classification (12-category)
- **Processing**: Asynchronous job queue (Celery with Redis backend)
- **Scaling**: 4 worker nodes; typical processing time 10-30 seconds per document

### 2.5 PostgreSQL Analytical Database
- **Instance**: AWS RDS PostgreSQL 15 (db.r5.2xlarge, 64 GB RAM)
- **Storage**: 500 GB SSD
- **Schema**:
  ```
  projects (project_id, name, sector, country, debt_outstanding...)
  risk_scores (project_id, date, pd_base, pd_climate, dscr, ...)
  climate_metrics (project_id, rca_rul_2030, rca_rul_2050, ...)
  portfolio_positions (fund_id, project_id, allocation_pct, ...)
  documents (doc_id, project_id, doc_type, extracted_terms...)
  alerts (alert_id, fund_id, project_id, severity, ...)
  ```
- **Backup**: Continuous replication to standby; daily snapshots to S3
- **Monitoring**: CloudWatch for CPU (target <70%), disk space (>20% free)

### 2.6 S3 Blob Storage
- **Use Cases**:
  - Sentinel-2 satellite imagery (TIFF format, 100MB+ per project-month)
  - PDF documents (loan agreements, concession contracts)
  - Model checkpoints and training artifacts
  - Data lake for historical project data
- **Storage Class**: S3 Standard for active data (<2 years old); S3 Glacier for archives
- **Total Capacity**: 5TB (images: 3TB, documents: 500GB, models: 1TB, archives: 500GB)
- **Versioning**: Enabled; lifecycle rules delete old versions after 90 days

### 2.7 MLflow Model Registry
- **Purpose**: Version control and tracking for all models
- **Models Tracked**:
  - XGBoost (versions: 1.0-1.7.2)
  - Neural Network (versions: 1.0-2.0.0)
  - Random Forest, SVM, TFT, PINN, GNN
- **Metadata**: Training date, dataset version, validation metrics (AUC, Gini, etc.)
- **Promotion**: Models promoted to "Production" or "Staging" stage
- **Deployment**: Auto-deploy to Triton when promoted to Production

---

## 3. Data Pipeline (Airflow DAG)

### 3.1 Ingestion Layer (02:00 UTC)
```python
DAG: daily_ingestion
├── fetch_market_data()
│   ├── interest_rates (SOFR, SONIA, EURIBOR)
│   ├── cds_spreads (100+ countries)
│   └── commodity_prices (oil, gas, agricultural)
│
├── pull_satellite_imagery()
│   ├── query ESA Copernicus API for new Sentinel-2 tiles
│   ├── download 10m RGB + NIR + SWIR bands
│   └── parallelize across 100+ projects
│
├── download_macro_updates()
│   ├── World Bank API (GDP, inflation, fiscal data)
│   ├── IMF WEO forecast (GDP projections)
│   └── National central banks (policy rates)
│
└── ingest_transaction_database()
    └── incremental load of new deal originations/updates
```

### 3.2 Feature Engineering Layer (03:00 UTC)
```python
DAG: daily_features
├── financial_feature_engineering()
│   ├── Calculate DSCR, LLCR, PLCR from debt/cash flow data
│   ├── Leverage ratios, equity IRR, DSCR volatility
│   └── Counterparty risk aggregation
│
├── geospatial_features()
│   ├── Compute NDVI, NDBI, NDMI spectral indices
│   ├── Change detection (CNN-based) for construction progress
│   ├── Flood/drought/seismic risk aggregation
│   └── Parallelize: 1,000 projects per batch on GPU cluster
│
├── macro_feature_aggregation()
│   ├── Map country-level to project-level indicators
│   ├── Sector-specific indices (traffic, power demand, etc.)
│   └── Lagged covariates (1-month lag to avoid look-ahead bias)
│
└── climate_adjusted_rul()
    ├── PINN inference: temperature + precipitation stress
    ├── Output: CA-RUL for 2030, 2050, 2080
    └── Climate scenarios: RCP 2.6, 4.5, 8.5
```

### 3.3 Model Inference Layer (04:00 UTC)
```python
DAG: daily_inference
├── ensemble_prediction()
│   ├── XGBoost + Neural Network + Random Forest + SVM
│   ├── Sector-specific weighted ensemble (Toll: 40% XGB, 30% NN, ...)
│   └── Output: PD, confidence interval, feature importance (SHAP)
│
├── tft_revenue_forecast()
│   ├── 24-month multi-horizon forecasting
│   ├── Quantile outputs: 5th, 50th, 95th percentiles
│   └── Input: Historical revenue + market covariates
│
├── gnn_systemic_risk()
│   ├── Construct portfolio graph (501 nodes, ~1,500 edges)
│   ├── Run GNN inference: centrality, contagion factors
│   └── Output: Portfolio systemic PD, node-level risk contribution
│
└── nlp_document_batch()
    ├── LayoutLM for clause extraction (new documents only)
    ├── NER: entity linking + coreference resolution
    └── Document classification (12 categories)
```

### 3.4 Output & Alert Layer (05:00 UTC)
```python
DAG: daily_output
├── write_to_postgres()
│   ├── Insert daily risk scores
│   ├── Update portfolio aggregates
│   ├── Archive historical time series
│   └── Validate data quality (NULL checks, range validation)
│
├── publish_to_api()
│   ├── Cache risk scores in Redis (1-hour TTL)
│   ├── Update portfolio metrics endpoint
│   └── Publish alert topics to message queue
│
├── generate_alerts()
│   ├── Flag projects with PD increase >500bps
│   ├── Flag revenue trending negative (>10% YoY decline)
│   ├── Flag covenant breach imminent (DSCR < covenant + 5%)
│   └── Severity: high (PD+500bps), medium, low
│
└── data_quality_report()
    ├── Missing values, outliers, drift detection
    ├── Send email report to ops team
    └── If failures >5%, trigger auto-rollback
```

**SLA**: 99.5% on-time completion (08:00 UTC target)
**Failure Handling**: Fallback to last cached results; alert ops team for manual intervention

---

## 4. Deployment Topology

### 4.1 Development Environment
```
Local Dev Machine
├── FastAPI (localhost:8000)
├── PostgreSQL (Docker, localhost:5432)
├── Redis (Docker, localhost:6379)
└── Airflow (Docker, localhost:8080)
```

### 4.2 Staging Environment
```
AWS Staging VPC
├── API Gateway: 2 replicas (t3.medium)
├── Inference Service: 2 GPU instances (g4dn.xlarge, NVIDIA T4)
├── PostgreSQL: db.t3.large (non-HA)
├── Redis: cache.t3.micro
└── Airflow: t3.small single node
```

### 4.3 Production Environment
```
AWS Production VPC (Multi-AZ)
├── API Gateway: 4-10 replicas (t3.large, auto-scaling)
│   ├── Application Load Balancer (health checks every 30s)
│   └── CloudFront CDN for geographic distribution
│
├── Inference Service: 4-8 GPU instances (g4dn.2xlarge, NVIDIA T4)
│   └── GPU Memory: 64GB total; batch size: 32 projects/batch
│
├── PostgreSQL: db.r5.2xlarge (Primary + Standby, Multi-AZ)
│   ├── Continuous replication
│   ├── Automated failover (<30s RTO)
│   └── Read replicas for analytics queries
│
├── Redis: cache.r5.large (Master + Replica)
│   ├── Redis Sentinel for automatic failover
│   └── Eviction: LRU, max memory 32GB
│
├── S3: Regional bucket (us-east-1)
│   └── Versioning, Cross-region replication to backup region
│
└── Airflow: 1 scheduler + 4 worker nodes (m5.xlarge each)
    └── Celery executor for distributed task scheduling
```

### 4.4 Monitoring & Observability

**Metrics (CloudWatch)**:
- API latency (p50, p99): target <200ms, <500ms
- Model inference time: <100ms (p99)
- GPU utilization: target 60-80%
- Database query time: <1s (p99)
- Cache hit rate: target >90%
- Airflow DAG success rate: target 99.5%

**Logging**:
- Centralized logging (AWS CloudWatch Logs)
- Request/response logging for audit trail
- Model inference logs (predictions, feature values)
- Error logs with traceback and context

**Alerting**:
- API latency >500ms (p99): auto-scaling trigger
- GPU utilization >90%: alert ops
- Database CPU >80%: scale up
- DAG failure: page on-call engineer
- Cache hit rate <80%: investigate data quality

---

## 5. Data Flows

### 5.1 Real-Time Risk Assessment Request
```
User Request (API)
    ↓
API Gateway
    ├── JWT validation
    ├── Rate limit check
    └─→ Models Service
        ├── Check Redis cache (feature store)
        ├── If miss: compute features on-the-fly (fast path)
        ├── Load ensemble models from Triton
        ├── Inference: XGBoost + NN + RF + SVM
        ├── SHAP explanation generation
        └─→ PostgreSQL (log request)
            └─→ Response to user (JSON)
```

Latency: 50-200ms (cache hit), 300-500ms (cache miss)

### 5.2 Batch Portfolio Analysis
```
Portfolio Metrics Request
    ↓
API Gateway
    ↓
Feature Store (Redis)
    ├── Fetch project risk scores (500+ projects)
    ├── Fetch climate metrics
    ├── Fetch portfolio positions
    └─→ GNN Service
        ├── Construct graph
        ├── Run systemic risk calculation
        └─→ Portfolio aggregation
            ├── Weighted average PD, DSCR
            ├── Systemic amplification factor
            ├── Sector composition
            └─→ Response to user
```

Latency: 1-3 seconds

### 5.3 Document Classification Pipeline
```
User Uploads PDF
    ↓
S3 (temporary bucket)
    ↓
Celery Job Queue
    ├── LayoutLM: clause extraction
    ├── NER: entity linking
    ├── Classification: 12-category
    └─→ PostgreSQL (documents table)
        ├── Extracted terms
        ├── Risk classification
        ├── Benchmark comparison
        └─→ Webhook to user (async notification)
```

Processing time: 10-30 seconds per document

---

## 6. Scalability Considerations

### 6.1 Horizontal Scaling
- **API Gateway**: Auto-scaling group (2-10 replicas) based on CPU/memory
- **Inference Service**: GPU cluster with dynamic batching (32 projects per batch)
- **Airflow Workers**: Task pool parallelization (up to 64 concurrent tasks)

### 6.2 Vertical Scaling
- **PostgreSQL**: Upgrade instance type (db.r5.2xlarge → db.r6i.4xlarge)
- **Redis**: Increase memory (32GB → 128GB) for larger cache
- **Inference Servers**: Upgrade GPU (T4 → A10G for higher throughput)

### 6.3 Data Partitioning
- **Projects**: Partition by country/region for faster queries
- **Time Series**: Partition by date (monthly partitions in PostgreSQL)
- **Satellite Imagery**: Distributed across S3 prefixes by country

---

## 7. Security Architecture

### 7.1 Authentication & Authorization
- JWT tokens with 1-hour expiration
- Role-based access control: admin, analyst, viewer
- API key rotation: every 90 days

### 7.2 Data Encryption
- TLS 1.3 for all data in transit
- AES-256 for data at rest (PostgreSQL, S3, Redis)
- Customer data isolated by fund_id (multi-tenancy)

### 7.3 Compliance
- GDPR: Data deletion on customer request
- SOC 2 Type II certification
- Audit logs: All API calls logged for 7 years
- PII masking: Project names, borrower names redacted in logs

---

## 8. Disaster Recovery

### 8.1 RTO/RPO Targets
- **RTO** (Recovery Time Objective): 1 hour
- **RPO** (Recovery Point Objective): 15 minutes

### 8.2 Backup Strategy
- PostgreSQL: Continuous WAL replication to standby; daily snapshots to S3
- S3: Cross-region replication to backup region (us-west-2)
- Secrets Manager: Encrypted in AWS Secrets Manager; 7-day retention

### 8.3 Failover Procedure
1. Monitor detects primary region failure (heartbeat timeout >2 minutes)
2. DNS failover to backup region
3. Promote read replica to primary
4. Restore cache from Redis persistence
5. Resume Airflow DAG execution

Estimated failover time: 5-10 minutes

---

## 9. Cost Optimization

### 9.1 Infrastructure Costs (Annual, Production)
- **Compute**: $450k (4 GPU instances, 10 API replicas, Airflow)
- **Database**: $80k (RDS Multi-AZ, read replicas)
- **Storage**: $50k (S3, Glacier archives)
- **Networking**: $30k (data transfer, CloudFront)
- **Total**: ~$610k/year

### 9.2 Cost Reduction Strategies
- Spot instances for non-critical workloads (30% savings)
- Reserved instances for baseline capacity (40% savings)
- S3 Intelligent Tiering for automatic storage class optimization
- Compress Sentinel-2 imagery (40% size reduction)

---

## 10. Future Enhancements

### Phase 6.1 (Q3 2024)
- Multi-region deployment (APAC, EMEA)
- Real-time ESG scoring integration

### Phase 6.2 (Q4 2024)
- Kubernetes migration (EKS) for improved container orchestration
- Distributed model training (federated learning across regions)

### Phase 6.3 (2025)
- Quantum computing for portfolio optimization (pilot)
- Advanced causal inference for impact attribution
