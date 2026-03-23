# SparkR Integration Implementation Guide

## Overview

This document describes the complete implementation of Apache Spark with R (SparkR) into the MongoDB Game Backend project.

## Architecture

### Components

1. **Spark Configuration** (`spark/config.r`, `spark/spark_config.yml`)
   - R utility functions for SparkR session management
   - Configuration files for different deployment modes
   - MongoDB/Neo4j connector setup

2. **Python-R Bridge** (`app/spark/spark_bridge.py`)
   - Subprocess-based execution of R scripts
   - Data exchange via Parquet/Arrow files
   - Error handling and job tracking

3. **Job Scheduler** (`app/scheduler/job_scheduler.py`)
   - APScheduler-based scheduling of batch jobs
   - Standard job templates (leaderboard, stats, recommendations)
   - On-demand job execution

4. **Batch Jobs** (`spark/jobs/`)
   - `leaderboard_batch.r` - Calculate player rankings
   - `stats_aggregation_batch.r` - Aggregate player statistics
   - `social_recommendations.r` - Generate friend recommendations

5. **Streaming Jobs** (`spark/streaming/`)
   - `stats_streaming.r` - Real-time stats updates (stub)

6. **Analytics Endpoints** (`app/routes/spark_analytics.py`)
   - REST API endpoints for on-demand analytics
   - Scheduled job management interface
   - Job result retrieval

## Setup & Installation

### 1. Install Python Dependencies

```bash
cd mongodbgame
pip install -r requirements.txt
```

New packages added:
- `pyspark` - Python API for Spark
- `pyarrow` - Parquet file support
- `apscheduler` - Job scheduling framework
- `pyyaml` - YAML configuration parsing

### 2. Install R & SparkR

#### Option A: Using Conda (Recommended)

```bash
# Create R environment
conda install -c conda-forge r-base r-sparkr

# Activate and install SparkR packages
Rscript r_env/requirements.R
```

#### Option B: Manual R Installation

Windows:
```powershell
# Download R from https://cran.r-project.org/bin/windows/base/
# Install R
# Then install packages:
Rscript r_env/requirements.R
```

Linux:
```bash
sudo apt-get install r-base
# Then:
Rscript r_env/requirements.R
```

### 3. Set Environment Variables

```bash
# Required
export SPARK_HOME=/path/to/spark
export RSCRIPT=/path/to/Rscript

# Optional
export NEO4J_PASSWORD=your_neo4j_password
```

### 4. Verify Installation

```bash
# Test Python bridge
python -c "from app.spark.spark_bridge import get_spark_bridge; print('OK')"

# Test R/SparkR
Rscript spark/config.r
```

## Usage

### 1. Starting the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On startup:
- FastAPI initializes MongoDB and Neo4j connections
- Job scheduler initializes with standard batch jobs
- Scheduler starts in background

### 2. Testing Endpoints

#### Health Check
```bash
curl http://localhost:8000/api/spark/health
```

Response:
```json
{
  "status": "healthy",
  "spark_bridge_ready": true,
  "scheduler_running": true,
  "timestamp": "2024-03-22T10:30:00"
}
```

#### Get Leaderboard
```bash
curl "http://localhost:8000/api/spark/leaderboard?season=current&limit=10"
```

#### Get Player Stats
```bash
curl "http://localhost:8000/api/spark/player-stats/player123?timeframe=seasonal"
```

#### Get Recommendations
```bash
curl "http://localhost:8000/api/spark/recommendations/player123?limit=10"
```

#### List Scheduled Jobs
```bash
curl http://localhost:8000/api/spark/jobs
```

#### Manually Run a Job
```bash
curl -X POST "http://localhost:8000/api/spark/run-job?script_name=leaderboard_batch"
```

#### Get Job Result
```bash
curl "http://localhost:8000/api/spark/job-result/leaderboard_batch_20240322_102330"
```

### 3. Programmatic Usage

Python:
```python
from app.spark.spark_bridge import execute_spark_job

result = execute_spark_job(
    script_name="leaderboard_batch",
    config={
        "season": "2024",
        "limit": 100,
    },
    timeout=600
)

if result["status"] == "success":
    leaderboard = result["output"]  # pandas DataFrame
    print(f"Processed {result['rows_processed']} players")
```

FastAPI Route:
```python
from app.scheduler.job_scheduler import get_job_scheduler

scheduler = get_job_scheduler()
result = scheduler.run_job_now(
    script_name="stats_aggregation_batch",
    config={...},
    timeout=300
)
```

## Job Schedules

By default, these jobs run on schedule:

| Job | Trigger | Details |
|-----|---------|---------|
| `leaderboard_daily` | Daily at 2 AM UTC | Compute top 100 players |
| `stats_aggregation_6h` | Every 6 hours | Aggregate player statistics |
| `social_recommendations_daily` | Daily at 3 AM UTC | Generate friend suggestions |

Modify schedules in `app/scheduler/job_scheduler.py` `add_standard_jobs()` method.

## File Structure

```
mongodbgame/
├── spark/                          # Spark jobs and utilities
│   ├── config.r                   # SparkR session and utilities
│   ├── spark_config.yml           # Configuration for different modes
│   ├── jobs/
│   │   ├── leaderboard_batch.r
│   │   ├── stats_aggregation_batch.r
│   │   ├── social_recommendations.r
│   │   └── __init__.py
│   ├── streaming/
│   │   ├── stats_streaming.r
│   │   └── __init__.py
│   └── __init__.py
├── r_env/
│   ├── requirements.R             # R package installation script
│   └── install_sparkr.r           # (future) SparkR-specific setup
├── app/
│   ├── spark/
│   │   ├── spark_bridge.py        # Python-R subprocess bridge
│   │   └── __init__.py
│   ├── scheduler/
│   │   ├── job_scheduler.py       # APScheduler integration
│   │   └── __init__.py
│   ├── routes/
│   │   ├── spark_analytics.py     # FastAPI analytics endpoints
│   │   └── ... (existing routes)
│   ├── main.py                    # (updated) Added Spark initialization
│   └── ... (existing app structure)
└── requirements.txt               # (updated) Added Spark dependencies
```

## Data Flow

### On-Demand Analytics Flow

```
FastAPI Request
    ↓
/api/spark/leaderboard endpoint
    ↓
execute_spark_job(script_name="leaderboard_batch", config={...})
    ↓
SparkRBridge.execute_job()
    ↓
Create wrapper R script + config JSON
    ↓
Execute: Rscript wrapper.r
    ↓
R script executes leaderboard_batch.r::run_job()
    ↓
Run Spark computations
    ↓
Write output to Parquet file
    ↓
Read Parquet in Python
    ↓
Return DataFrame to client (JSON response)
```

### Scheduled Job Flow

```
APScheduler trigger (e.g., daily at 2 AM)
    ↓
JobScheduler.job_wrapper()
    ↓
execute_spark_job(...)
    ↓
[Same as on-demand flow above]
    ↓
Store result in JobScheduler.job_results
    ↓
Available via /api/spark/job-result/{job_id}
```

## Performance Considerations

### Local Mode (Development)

- All cores on single machine
- Suitable for <100M records
- Memory-limited to available RAM

Configuration:
```yaml
master: "local[*]"  # Use all cores
memory: "4g"        # Adjust as needed
```

### Cluster Mode (Production/Scale)

- Distributed across multiple nodes
- Suitable for >100M records
- Requires YARN, Kubernetes, or Mesos cluster

Configuration:
```yaml
master: "yarn"                    # YARN cluster
executor:
  instances: 16                  # Number of executors
  cores: 8
  memory: "16g"
```

### Parquet Exchange Overhead

- Parquet I/O is efficient but adds latency for small datasets
- For <1MB: Direct in-memory exchange might be faster
- For >1GB: Consider direct MongoDB read in Spark

### Caching Results

Redis cache results of scheduled jobs:
```python
# Save result to Redis with TTL
redis_client.setex(
    f"analytics:leaderboard:2024",
    3600,  # 1 hour TTL
    json.dumps(result["output"].to_dict("records"))
)
```

## Troubleshooting

### Issue: "spark_bridge_ready": false

**Cause**: SparkRBridge not properly initialized

**Solution**:
```bash
# Check Spark installation
echo $SPARK_HOME
which Rscript

# Test bridge
python app/spark/spark_bridge.py
```

### Issue: Job timeout after 300 seconds

**Cause**: Job takes longer than timeout

**Solution**:
```python
# Increase timeout
result = execute_spark_job(
    script_name="stats_aggregation_batch",
    timeout=900  # 15 minutes
)
```

### Issue: Parquet file not found

**Cause**: Output Parquet path not properly written

**Solution**:
```bash
# Check temp directory permissions
ls -la /tmp/spark_bridge_*

# Run with debug logging
PYTHONVERBOSE=2 python -c "..."
```

### Issue: R script fails to source config.r

**Cause**: Path mismatch in wrapper script

**Solution**:
1. Verify `spark/config.r` exists
2. Check absolute path in wrapper
3. Add debug output in wrapper script:
   ```r
   cat("Working dir:", getwd(), "\n")
   cat("Script exists:", file.exists("spark/config.r"), "\n")
   ```

## Next Steps

### Phase 3: Real-Time Streaming

1. Implement MongoDB Change Streams connector
2. Set up Kafka topics for match events
3. Configure Redis sink for cache

### Phase 4: Monitoring & Dashboards

1. Add Spark UI integration
2. Create monitoring dashboard in React
3. Job failure alerts

### Phase 5: Production Deployment

1. Docker image with Spark + R environment
2. Kubernetes deployment configuration
3. Cluster auto-scaling setup

## Further Reading

- [Apache Spark Documentation](https://spark.apache.org/docs/)
- [SparkR User Guide](https://spark.apache.org/docs/latest/sparkr.html)
- [APScheduler Docs](https://apscheduler.readthedocs.io/)
- [PyArrow Parquet Guide](https://arrow.apache.org/docs/python/parquet.html)
