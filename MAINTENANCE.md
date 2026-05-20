# InfraRisk AI - Maintenance & Operations Guide

## Table of Contents

1. [Regular Maintenance Tasks](#regular-maintenance-tasks)
2. [Backup & Recovery](#backup--recovery)
3. [Monitoring & Alerts](#monitoring--alerts)
4. [Update Procedures](#update-procedures)
5. [Performance Optimization](#performance-optimization)
6. [Security Updates](#security-updates)
7. [Troubleshooting](#troubleshooting)
8. [Support Contacts](#support-contacts)

---

## Regular Maintenance Tasks

### Daily Tasks

**Morning Check (before business hours):**
```bash
# Verify system health
curl -X GET http://localhost:8000/health

# Check disk space
df -h

# Monitor system resources
top -b -n 1 | head -20
```

**Monitoring:**
- [ ] Error rate < 0.1%
- [ ] API response time < 2s (p95)
- [ ] Disk usage < 80%
- [ ] Memory usage < 85%
- [ ] No failed background jobs

### Weekly Tasks

**Database Maintenance:**
```bash
# Analyze database for optimization
psql -U infrarisk_user -d infrariskai_db -c "ANALYZE;"

# Check table sizes
psql -U infrarisk_user -d infrariskai_db -c "\dt+ public.*"

# View cache hit ratio
psql -U infrarisk_user -d infrariskai_db -c "SELECT sum(heap_blks_read) as heap_read, sum(heap_blks_hit) as heap_hit, sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio FROM pg_statio_user_tables;"
```

**Log Review:**
```bash
# Check for errors in logs
grep ERROR logs/app.log | tail -20

# Check for security events
grep SECURITY logs/app.log | tail -10

# Archive old logs
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;
```

**Data Quality Check:**
```bash
# Verify recent data ingestion
python scripts/check_data_freshness.py

# Validate data integrity
python scripts/validate_data_quality.py
```

### Monthly Tasks

**Model Performance Review:**
```bash
# Generate model performance report
python scripts/generate_model_report.py

# Check for model drift
python scripts/detect_model_drift.py

# Compare with baseline metrics
python scripts/compare_baseline.py
```

**Security Audit:**
```bash
# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image infrariskai:latest

# Check for exposed secrets
python scripts/scan_secrets.py

# Review access logs
python scripts/audit_access_logs.py
```

**Capacity Planning:**
```bash
# Analyze growth trends
python scripts/capacity_analysis.py

# Forecast resource needs
python scripts/forecast_resources.py

# Generate capacity report
python scripts/capacity_report.py
```

---

## Backup & Recovery

### Backup Strategy

**RPO (Recovery Point Objective):** 24 hours  
**RTO (Recovery Time Objective):** 4 hours

### Database Backups

**Automated Daily Backup:**
```bash
# Add to crontab (runs at 2:00 AM daily)
0 2 * * * pg_dump -U infrarisk_user infrariskai_db | gzip > /backups/db_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

**Manual Full Backup:**
```bash
# Full database backup
pg_dump -U infrarisk_user -Fc infrariskai_db > backup_full_$(date +%Y%m%d).dump

# Backup with statistics
pg_dump -U infrarisk_user -Fc --verbose infrariskai_db > backup_$(date +%Y%m%d).dump

# Backup specific tables
pg_dump -U infrarisk_user -t projects infrariskai_db > projects_backup.sql
```

**Incremental Backup (using WAL):**
```bash
# Enable WAL archiving in postgresql.conf
wal_level = archive
archive_mode = on
archive_command = 'cp %p /backups/wal_archive/%f'

# Perform base backup
pg_basebackup -h localhost -U infrarisk_user -D /backups/base_backup -Pv -Xstream
```

### Redis Backups

**Automated RDB Snapshots:**
```bash
# Configure in redis.conf
save 900 1          # Every 15 minutes if 1+ key changed
save 300 10         # Every 5 minutes if 10+ keys changed
save 60 10000       # Every 60 seconds if 10000+ keys changed

# Manual snapshot
redis-cli BGSAVE

# Backup RDB file
cp /var/lib/redis/dump.rdb /backups/redis_$(date +%Y%m%d).rdb
```

### Elasticsearch Backups

**Create Snapshot Repository:**
```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/my_backup" -H 'Content-Type: application/json' -d'{
  "type": "fs",
  "settings": {
    "location": "/backups/elasticsearch"
  }
}'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_1?wait_for_completion=true"

# List snapshots
curl -X GET "localhost:9200/_snapshot/my_backup/_all"
```

### Model & Configuration Backups

**Backup Model Files:**
```bash
# Archive all models
tar -czf /backups/models_backup_$(date +%Y%m%d).tar.gz models/

# Backup configurations
tar -czf /backups/config_backup_$(date +%Y%m%d).tar.gz config/

# Backup source code
git bundle create /backups/repo_backup_$(date +%Y%m%d).bundle --all
```

### Backup Verification

**Test Backup Integrity:**
```bash
# Database backup test
pg_restore --list backup_full_20240101.dump | head -20

# Archive integrity check
tar -tzf models_backup_20240101.tar.gz | head -20

# Verify backup size
du -h /backups/
```

### Recovery Procedures

**Database Recovery:**
```bash
# Restore full database (from dump format)
psql -U infrarisk_user infrariskai_db < backup_full_20240101.sql

# Restore from custom format
pg_restore -U infrarisk_user -d infrariskai_db backup_full_20240101.dump

# Restore specific table
pg_restore -U infrarisk_user -d infrariskai_db -t projects backup_full_20240101.dump
```

**Redis Recovery:**
```bash
# Stop Redis
redis-cli SHUTDOWN SAVE

# Restore from backup
cp /backups/redis_20240101.rdb /var/lib/redis/dump.rdb

# Start Redis
redis-server
```

**Full System Recovery:**
```bash
# 1. Restore database
pg_restore -U infrarisk_user -d infrariskai_db /backups/backup_full_20240101.dump

# 2. Restore models
tar -xzf /backups/models_backup_20240101.tar.gz

# 3. Restore configuration
tar -xzf /backups/config_backup_20240101.tar.gz

# 4. Restart all services
docker-compose restart

# 5. Verify system
curl http://localhost:8000/health
```

---

## Monitoring & Alerts

### System Metrics to Monitor

**CPU & Memory:**
- CPU utilization > 80% (warning) | > 95% (critical)
- Memory usage > 85% (warning) | > 95% (critical)
- Swap usage > 0% (warning)

**Disk:**
- Disk usage > 80% (warning) | > 95% (critical)
- Disk read/write latency > 50ms (warning)
- Inode usage > 80% (warning)

**Network:**
- Network latency > 100ms (warning)
- Packet loss > 1% (warning)
- Connection errors > 10 (warning)

**Database:**
- Query execution time > 1s (warning) | > 5s (critical)
- Connection pool > 80% (warning)
- Cache hit ratio < 70% (warning)
- Replication lag > 10s (critical)

**Application:**
- Error rate > 1% (warning) | > 5% (critical)
- Response time p95 > 2s (warning) | > 5s (critical)
- Failed requests > 10 (warning)
- Model inference time > 500ms (warning)

### Monitoring Stack Setup

**Prometheus Configuration:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'infrariskai'
    static_configs:
      - targets: ['localhost:8000']

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
```

**Alert Rules:**
```yaml
groups:
  - name: infrariskai_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m])) > 2
        for: 5m

      - alert: DiskSpaceLow
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.2
        for: 10m
```

### Alert Notification Channels

**Email Alerts:**
```
Technical Team: ops@infrariskai.com
On-Call Rotation: oncall@infrariskai.com
```

**SMS/Pager (Critical Only):**
```
Primary: +1-555-0100 (On-call engineer)
Secondary: +1-555-0101 (On-call manager)
```

**Slack Integration:**
```
Channel: #infrariskai-alerts
Mentions: @ops-team (warning), @ops-critical (critical)
Escalation: Page on-call after 15 minutes without acknowledgment
```

---

## Update Procedures

### Minor Version Update (Bug Fixes)

**Steps:**
```bash
# 1. Backup current state
pg_dump -U infrarisk_user infrariskai_db | gzip > backup_pre_update.sql.gz

# 2. Pull latest code
git fetch origin
git checkout v1.0.1

# 3. Install dependencies
pip install -r requirements_ml.txt --upgrade

# 4. Run migrations
python -m alembic upgrade head

# 5. Restart services
docker-compose restart

# 6. Verify health
curl http://localhost:8000/health
```

### Major Version Update (New Features)

**Steps (with downtime):**
```bash
# 1. Announce maintenance window (30 minutes before)
# 2. Stop all services
docker-compose down

# 3. Full database backup
pg_dump -U infrarisk_user -Fc infrariskai_db > backup_v1.0_to_v1.1.dump

# 4. Clear cache
redis-cli FLUSHDB

# 5. Pull new version
git fetch origin
git checkout v1.1.0

# 6. Run migrations
python -m alembic upgrade head

# 7. Update configurations
cp config/v1.0.yaml config/v1.0.yaml.bak
cp config/v1.1.yaml config/

# 8. Start services
docker-compose up -d

# 9. Run smoke tests
python scripts/smoke_tests.py

# 10. Announce completion
```

### Zero-Downtime Deployment (Database-Compatible Changes Only)

```bash
# 1. Deploy new code to secondary server
# 2. Run tests on secondary
# 3. Switch load balancer to secondary
# 4. Monitor metrics on new version
# 5. Upgrade primary server
# 6. Switch load balancer back
```

### Model Updates

**Update Procedure:**
```bash
# 1. Download new model weights
aws s3 cp s3://infrariskai-models/v1.0.0/new_model.h5 models/

# 2. Run validation tests
python scripts/validate_model.py models/new_model.h5

# 3. A/B test new model (optional)
# Set 10% traffic to new model, monitor metrics

# 4. Full rollout
# Update model_config.yaml to use new model

# 5. Monitor performance
python scripts/monitor_model_performance.py
```

---

## Performance Optimization

### Database Optimization

**Index Management:**
```bash
# Identify missing indices
psql -U infrarisk_user infrariskai_db -c "
  SELECT schemaname, tablename, attname
  FROM pg_stat_user_tables t
  JOIN pg_stat_user_indexes i ON t.relid = i.relid
  WHERE seq_scan > idx_scan
  ORDER BY seq_scan DESC
  LIMIT 10;"

# Create missing indices
psql -U infrarisk_user infrariskai_db -c "CREATE INDEX idx_projects_status ON projects(status);"

# Monitor index usage
psql -U infrarisk_user infrariskai_db -c "SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan DESC;"
```

**Query Optimization:**
```bash
# Analyze query plans
EXPLAIN ANALYZE SELECT * FROM projects WHERE risk_score > 0.7;

# Enable query logging for slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
SELECT pg_reload_conf();
```

**Vacuuming & Maintenance:**
```bash
# Full vacuum (maintenance window)
VACUUM FULL ANALYZE;

# Regular maintenance
VACUUM ANALYZE;

# Autovacuum configuration
ALTER SYSTEM SET autovacuum_naptime = '30s';
ALTER SYSTEM SET autovacuum_vacuum_threshold = 50;
```

### Cache Optimization

**Redis Optimization:**
```bash
# Monitor cache performance
redis-cli INFO stats

# Optimize memory usage
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Monitor key expiration
redis-cli DBSIZE
redis-cli KEYS "*" | wc -l
```

**Application Cache Tuning:**
```python
# In config/cache.py
CACHE_TIMEOUT = 3600  # 1 hour
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
CACHE_KEY_PREFIX = "infrariskai"
CACHE_ENABLE = True
```

### Model Inference Optimization

**Batch Processing:**
```python
# Use batch prediction for improved throughput
predictions = model.predict_batch(data, batch_size=32)

# Async inference for non-critical paths
async_result = async_predict.delay(project_id)
```

**Model Quantization:**
```bash
# Convert model to quantized version for faster inference
python scripts/quantize_models.py models/ --output quantized_models/
```

---

## Security Updates

### Dependency Updates

**Check for Vulnerable Dependencies:**
```bash
# Scan requirements files
safety check -r requirements_ml.txt
safety check -r requirements_nlp.txt

# Update vulnerable packages
pip install --upgrade package_name==secure_version
```

**Update All Dependencies:**
```bash
# Update pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Update all packages (test in staging first!)
pip install --upgrade -r requirements_ml.txt
```

### Security Patches

**Apply Security Patches:**
```bash
# Update base Docker image
docker pull ubuntu:20.04

# Rebuild application image
docker build --pull --no-cache -t infrariskai:latest .

# Scan image for vulnerabilities
trivy image infrariskai:latest

# Push to registry
docker push your-registry/infrariskai:latest
```

**OS Security Updates:**
```bash
# Ubuntu
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get dist-upgrade -y

# CentOS
sudo yum update -y
sudo yum security-update -y
```

### Secrets Rotation

**API Keys & Credentials:**
```bash
# 1. Generate new credentials
# 2. Update in secrets management system
# 3. Deploy to production with new secrets
# 4. Monitor for failures
# 5. Revoke old credentials

# Automated rotation script
python scripts/rotate_secrets.py
```

---

## Troubleshooting

### Common Issues & Solutions

**Issue: High Memory Usage**
```bash
# Check process memory
ps aux --sort=-%mem | head -10

# Restart problematic service
docker-compose restart web

# Check for memory leaks
python scripts/check_memory_leaks.py

# Solution: Increase memory limit or optimize code
```

**Issue: Slow Queries**
```bash
# Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

# Analyze slow queries
psql -U infrarisk_user infrariskai_db -c "
  SELECT query, mean_time, calls
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;"

# Solution: Add indices or rewrite query
```

**Issue: API Timeouts**
```bash
# Check API logs
tail -f logs/app.log | grep -i timeout

# Increase timeout
# In config: API_TIMEOUT = 30  # seconds

# Optimize slow endpoints
python scripts/profile_endpoints.py
```

**Issue: Connection Pool Exhaustion**
```bash
# Check connection status
psql -U infrarisk_user -d infrariskai_db -c "SELECT * FROM pg_stat_activity;"

# Increase pool size
# In config: SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 20}

# Kill idle connections
psql -U postgres -d infrariskai_db -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle' AND query_start < now() - interval '10 minutes';"
```

---

## Support Contacts

### Internal Support

| Role | Contact | On-Call |
|------|---------|---------|
| **Operations Lead** | ops@infrariskai.com | 24/7 |
| **Database Administrator** | dba@infrariskai.com | Business hours |
| **Security Team** | security@infrariskai.com | On-demand |
| **Development Team** | dev@infrariskai.com | Business hours |

### Escalation Path

1. **Tier 1:** Operations team (0-30 minutes)
2. **Tier 2:** On-call engineer (15-60 minutes)
3. **Tier 3:** Development team lead (30-90 minutes)
4. **Tier 4:** CTO/Principal Architect (60+ minutes)

### External Support

**Vendor Support Contacts:**
- PostgreSQL: www.postgresql.org/support
- Redis: redis.io/support
- Elasticsearch: www.elastic.co/support
- Docker: support.docker.com

### Emergency Response

**For Critical Outages:**
1. Page on-call engineer: +1-555-0100
2. Slack: @ops-critical
3. Email: ops-critical@infrariskai.com
4. Status Page: status.infrariskai.com

---

## Maintenance Checklist

**Monthly Maintenance Window (1st Sunday, 2:00 AM):**
- [ ] Full database backup and verification
- [ ] Model performance report
- [ ] Security vulnerability scan
- [ ] Capacity planning analysis
- [ ] Log archival and cleanup
- [ ] Certificate renewal check (if applicable)
- [ ] DNS and SSL record verification
- [ ] Disaster recovery drill (monthly)

**Quarterly Tasks:**
- [ ] Load testing and capacity planning
- [ ] Security penetration testing
- [ ] Model retraining evaluation
- [ ] Dependency update review
- [ ] Documentation review and updates
- [ ] Stakeholder communication and reporting

---

**Last Updated:** 2024  
**Maintenance Schedule:** Ongoing  
**Next Review:** Quarterly

---

For more information, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
