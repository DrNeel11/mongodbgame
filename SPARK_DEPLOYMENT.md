# SparkR Analytics Deployment Guide

## Quick Start: 5 Minutes to First Job

### Prerequisites

- Python 3.8+
- FastAPI application running
- Optional: Local Spark installation (auto-detects)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Quick check
python tests/test_spark_integration.py --quick

# Expected output:
# ✓ Python bridge module
# ✓ Job scheduler module
# ✓ Analytics endpoints
# ✓ All batch job templates
# 4 passed, 0 failed
```

### 3. Start API and Jobs

```bash
# Terminal 1: Start FastAPI
uvicorn app.main:app --reload --port 8000

# Terminal 2: Monitor scheduler (optional)
# Check http://localhost:8000/api/spark/jobs
```

### 4. Test an Endpoint

```bash
# Get leaderboard (triggers Spark job)
curl "http://localhost:8000/api/spark/leaderboard?season=current&limit=10"
```

Expected response (after ~10-30 seconds):
```json
{
  "status": "success",
  "leaderboard": [...],
  "count": 10,
  "job_id": "20240322_102330",
  "elapsed_seconds": 15.3
}
```

---

## Detailed Deployment

### Option 1: Local Development

Perfect for testing and development.

#### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install R (if not present)
windows: Download from https://cran.r-project.org/bin/windows/base/
macOS: brew install r
linux: sudo apt-get install r-base

# 3. Install R packages
Rscript r_env/requirements.R

# 4. Start application
uvicorn app.main:app --reload --port 8000
```

#### Configuration

Edit `spark/spark_config.yml` for local mode:
```yaml
spark:
  master: "local[*]"          # Use all cores
  driver:
    memory: "2g"              # Adjust for your machine
  executor:
    cores: 2
```

#### Limitations

- Single machine only
- Memory-limited to available RAM
- For datasets >1GB, upgrade to cluster mode

---

### Option 2: Docker Compose (Recommended for Dev)

Provides isolated R environment and reproducible setup.

#### Setup

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  # Python FastAPI application
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SPARK_LOCAL_IP=127.0.0.1
      - R_LIBS_USER=/usr/local/lib/R/site-library
    volumes:
      - .:/app
      - spark_shared:/tmp/spark_shared
    depends_on:
      - spark
      - mongo
      - neo4j

  # Spark master
  spark:
    image: bitnami/spark:3.5.0
    ports:
      - "7077:7077"
      - "8080:8080"
    environment:
      - SPARK_MODE=master
    volumes:
      - spark_shared:/tmp/spark_shared

  # MongoDB
  mongo:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  # Neo4j
  neo4j:
    image: neo4j:5.17
    ports:
      - "7687:7687"
      - "7474:7474"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  spark_shared:
  mongo_data:
  neo4j_data:
```

#### Start

```bash
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

---

### Option 3: Kubernetes Cluster (Production)

For production with auto-scaling.

#### Prerequisites

- Kubernetes cluster (1.20+)
- Helm package manager
- Spark 3.5+ cluster running

#### Deploy

```bash
# 1. Create namespace
kubectl create namespace gamedb

# 2. Create ConfigMap for Spark config
kubectl create configmap spark-config \
  --from-file=spark/spark_config.yml \
  -n gamedb

# 3. Create Secret for credentials
kubectl create secret generic db-credentials \
  --from-literal=mongodb_uri=... \
  --from-literal=neo4j_password=... \
  -n gamedb

# 4. Apply deployment
kubectl apply -f k8s/deployment.yaml

# 5. Expose service
kubectl expose deployment gamedb-api --type=LoadBalancer -n gamedb
```

Example `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gamedb-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gamedb-api
  template:
    metadata:
      labels:
        app: gamedb-api
    spec:
      containers:
      - name: api
        image: gamedb-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: SPARK_MASTER
          value: "spark://spark-master:7077"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

---

## Monitoring

### View Scheduler Status

```bash
curl http://localhost:8000/api/spark/jobs
```

Response:
```json
{
  "status": "success",
  "jobs": [
    {
      "id": "leaderboard_daily",
      "name": "SparkR: leaderboard_batch",
      "trigger": "cron[hour='2', minute='0', timezone='UTC']",
      "next_run_time": "2024-03-23T02:00:00+00:00"
    },
    ...
  ],
  "scheduler_running": true
}
```

### View Job Results

```bash
# List all results
curl http://localhost:8000/api/spark/job-results

# Get specific result
curl http://localhost:8000/api/spark/job-result/{job_id}
```

### Logs Location

- FastAPI logs: `STDERR` (console)
- Spark logs: `/tmp/spark_*.log` (local mode)
- APScheduler logs: Can be configured in `app/config.py`

---

## Performance Tuning

### For Small Datasets (<100MB)

```yaml
spark:
  master: "local[2]"
  driver:
    memory: "1g"
  sql:
    shuffle_partitions: 50
```

### For Medium Datasets (100MB-1GB)

```yaml
spark:
  master: "local[*]"           # All cores
  driver:
    memory: "4g"
  sql:
    shuffle_partitions: 200
```

### For Large Datasets (>1GB)

Use cluster mode with multiple executors:

```yaml
spark:
  master: "yarn"
  executor:
    instances: 8
    cores: 4
    memory: "8g"
  sql:
    shuffle_partitions: 1000
```

### Job Timeout

Increase timeout for long-running jobs:

```python
result = execute_spark_job(
    script_name="stats_aggregation_batch",
    config={"season": "2024"},
    timeout=1800  # 30 minutes
)
```

---

## Troubleshooting

### "Job timeout after 300 seconds"

- **Cause**: Job takes longer than configured timeout
- **Solution**: Increase timeout or optimize Spark job

### "Rscript: command not found"

- **Cause**: R not installed or not in PATH
- **Solution**: Install R, or set `R_BINARY` environment variable

```bash
export R_BINARY=/usr/local/bin/Rscript
# or on Windows:
set R_BINARY="C:\Program Files\R\R-4.3.2\bin\Rscript.exe"
```

### "SPARK_HOME not set"

- **Cause**: Spark environment variable missing
- **Solution**: Set SPARK_HOME

```bash
export SPARK_HOME=/path/to/spark
# Verify:
echo $SPARK_HOME
```

### Job produces no output

- **Cause**: R script not returning data frame
- **Solution**: 
  1. Check R script returns data frame via `return(df)`
  2. Add debug logging: `cat("[DEBUG] Returning", nrow(df), "rows\n")`
  3. Check job logs: `curl http://localhost:8000/api/spark/job-result/{job_id}`

---

## Scaling Strategy

### Phase 1: Development (Current)
- Local Spark mode
- Single machine
- In-memory job storage

### Phase 2: Production (Months 2-3)
- Local cluster Spark (3 worker nodes)
- Job result persistence (Redis)
- Monitoring dashboard

### Phase 3: Enterprise (Months 4+)
- Full Kubernetes cluster
- YARN/Spark cluster manager
- Real-time streaming with Kafka
- Advanced monitoring and alerting

---

## Support & Resources

- [Spark Documentation](https://spark.apache.org/)
- [SparkR Guide](https://spark.apache.org/docs/latest/sparkr.html)
- [APScheduler](https://apscheduler.readthedocs.io/)
- [Project README](README.md)
- [Implementation Guide](SPARK_IMPLEMENTATION.md)

