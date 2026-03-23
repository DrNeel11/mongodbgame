"""
Job Scheduler for SparkR Batch Jobs

Integrates APScheduler for scheduling batch jobs:
- Leaderboard calculations (daily at night)
- Stats aggregation (hourly)
- Social recommendations (daily)
- Bulk migrations (on-demand)
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from app.spark.spark_bridge import execute_spark_job

logger = logging.getLogger(__name__)


class JobScheduler:
    """
    Manages scheduled execution of SparkR batch jobs.
    
    Example:
        scheduler = JobScheduler()
        scheduler.add_job(
            job_func=run_leaderboard_batch,
            trigger=CronTrigger(hour=2, minute=0),  # Run daily at 2 AM
            job_id="leaderboard_daily"
        )
        scheduler.start()
    """
    
    def __init__(self):
        """Initialize APScheduler."""
        self.scheduler = BackgroundScheduler(
            jobstores={"default": MemoryJobStore()},
            executors={"default": ThreadPoolExecutor(max_workers=3)},
            job_defaults={
                "coalesce": True,
                "max_instances": 1,  # Prevent simultaneous runs of same job
            },
        )
        self.job_results: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
    
    def start(self) -> None:
        """Start the scheduler."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Job scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Job scheduler stopped")
    
    def add_spark_job(self,
                     job_id: str,
                     script_name: str,
                     trigger,
                     config: Optional[Dict[str, Any]] = None,
                     timeout: int = 300) -> None:
        """
        Add a SparkR job to the scheduler.
        
        Args:
            job_id: Unique job identifier
            script_name: Name of the SparkR job script (e.g., "leaderboard_batch")
            trigger: APScheduler trigger (CronTrigger, IntervalTrigger, etc.)
            config: Job configuration dict
            timeout: Job execution timeout in seconds
        
        Example:
            scheduler.add_spark_job(
                job_id="leaderboard_daily",
                script_name="leaderboard_batch",
                trigger=CronTrigger(hour=2),
                config={"season": "2024"},
                timeout=600
            )
        """
        
        def job_wrapper():
            logger.info(f"[{job_id}] Starting scheduled job")
            try:
                result = execute_spark_job(
                    script_name=script_name,
                    config=config or {},
                    timeout=timeout
                )
                self.job_results[job_id] = result
                
                if result["status"] == "success":
                    logger.info(
                        f"[{job_id}] Job completed successfully. "
                        f"Rows: {result.get('rows_processed', 'N/A')}, "
                        f"Time: {result.get('elapsed_seconds', 'N/A'):.2f}s"
                    )
                else:
                    logger.error(
                        f"[{job_id}] Job failed: {result.get('error', 'Unknown error')}"
                    )
            except Exception as e:
                logger.error(f"[{job_id}] Unexpected error: {e}", exc_info=True)
                self.job_results[job_id] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        self.scheduler.add_job(
            func=job_wrapper,
            trigger=trigger,
            id=job_id,
            name=f"SparkR: {script_name}",
            coalesce=True,
            max_instances=1,
        )
        logger.info(f"Added job: {job_id} (script: {script_name})")
    
    def add_standard_jobs(self) -> None:
        """
        Add standard batch jobs with default schedules.
        
        Schedules:
        - Leaderboard: Daily at 2 AM UTC
        - Stats Aggregation: Every 6 hours
        - Social Recommendations: Daily at 3 AM UTC
        """
        
        # Leaderboard job (daily)
        self.add_spark_job(
            job_id="leaderboard_daily",
            script_name="leaderboard_batch",
            trigger=CronTrigger(hour=2, minute=0, timezone="UTC"),
            config={
                "season": "current",
                "limit": 100,
            },
            timeout=600
        )
        
        # Stats aggregation job (every 6 hours)
        self.add_spark_job(
            job_id="stats_aggregation_6h",
            script_name="stats_aggregation_batch",
            trigger=IntervalTrigger(hours=6),
            config={
                "timeframe": "seasonal",
            },
            timeout=900
        )
        
        # Social recommendations job (daily)
        self.add_spark_job(
            job_id="social_recommendations_daily",
            script_name="social_recommendations",
            trigger=CronTrigger(hour=3, minute=0, timezone="UTC"),
            config={
                "limit": 10,
            },
            timeout=1800
        )
    
    def run_job_now(self,
                   script_name: str,
                   config: Optional[Dict[str, Any]] = None,
                   timeout: int = 300) -> Dict[str, Any]:
        """
        Execute a SparkR job immediately (not scheduled).
        
        Args:
            script_name: Name of the SparkR job script
            config: Job configuration
            timeout: Execution timeout
        
        Returns:
            Job result dictionary
        
        Example:
            result = scheduler.run_job_now(
                "leaderboard_batch",
                config={"season": "2024"},
                timeout=600
            )
        """
        job_id = f"{script_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Running job immediately: {job_id}")
        
        result = execute_spark_job(
            script_name=script_name,
            config=config or {},
            timeout=timeout
        )
        
        self.job_results[job_id] = result
        return result
    
    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get result of a completed job."""
        return self.job_results.get(job_id)
    
    def get_all_job_results(self) -> Dict[str, Dict[str, Any]]:
        """Get results of all completed jobs."""
        return self.job_results.copy()
    
    def list_scheduled_jobs(self) -> list:
        """List all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger),
                "next_run_time": job.next_run_time.isoformat() 
                    if job.next_run_time else None,
            })
        return jobs
    
    def pause_job(self, job_id: str) -> None:
        """Pause a scheduled job."""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
    
    def resume_job(self, job_id: str) -> None:
        """Resume a paused job."""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
    
    def remove_job(self, job_id: str) -> None:
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")


# Singleton instance
_scheduler_instance: Optional[JobScheduler] = None


def get_job_scheduler() -> JobScheduler:
    """Get or create singleton JobScheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = JobScheduler()
    return _scheduler_instance


def init_scheduler() -> JobScheduler:
    """
    Initialize the job scheduler with standard jobs.
    
    Call this once during app startup.
    
    Example:
        In app/main.py:
        scheduler = init_scheduler()
        scheduler.start()
    """
    scheduler = get_job_scheduler()
    scheduler.add_standard_jobs()
    return scheduler
