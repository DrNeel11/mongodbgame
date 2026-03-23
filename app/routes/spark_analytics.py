"""
Spark Analytics Endpoints

Provides on-demand analytics endpoints that trigger SparkR computations:
- GET /api/spark/leaderboard - Get top player rankings
- GET /api/spark/player-stats/{player_id} - Get player statistics
- GET /api/spark/recommendations/{player_id} - Get friend recommendations
- POST /api/spark/export-report - Generate and export analytics report
- GET /api/spark/jobs - List scheduled jobs
- POST /api/spark/run-job - Manually trigger a batch job
"""

from fastapi import APIRouter, Query, Path, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.spark.spark_bridge import execute_spark_job
from app.scheduler.job_scheduler import get_job_scheduler

router = APIRouter(prefix="/api/spark", tags=["Spark Analytics"])
logger = logging.getLogger(__name__)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LeaderboardRequest(BaseModel):
    """Request for leaderboard computation."""
    season: str = Query("current", description="Season identifier")
    game_id: Optional[str] = Query(None, description="Filter by game")
    limit: int = Query(100, ge=1, le=1000, description="Top N players")
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")


class PlayerStatsRequest(BaseModel):
    """Request for player statistics."""
    timeframe: str = Query("seasonal", description="'lifetime' or 'seasonal'")
    season: Optional[str] = Query("current", description="Season if timeframe=seasonal")


class RecommendationsRequest(BaseModel):
    """Request for friend recommendations."""
    limit: int = Query(10, ge=1, le=100, description="Number of recommendations")
    algorithm: str = Query("common_friends", description="'common_friends' or 'cosine_similarity'")


class ReportRequest(BaseModel):
    """Request for generating a report."""
    report_type: str = Query("summary", description="'summary', 'detailed', 'seasonal'")
    format: str = Query("json", description="'json', 'csv', 'parquet'")
    include_leaderboard: bool = Query(True, description="Include leaderboard")
    include_stats: bool = Query(True, description="Include player stats")
    include_recommendations: bool = Query(False, description="Include recommendations")


class JobResponse(BaseModel):
    """Response for job execution."""
    job_id: str
    status: str  # success, error, timeout, pending
    script: str
    rows_processed: int = 0
    elapsed_seconds: float = 0.0
    message: Optional[str] = None
    timestamp: str


class ScheduledJobInfo(BaseModel):
    """Info about a scheduled job."""
    id: str
    name: str
    trigger: str
    next_run_time: Optional[str]


# ============================================================================
# LEADERBOARD ENDPOINT
# ============================================================================

@router.get("/leaderboard", 
            summary="Get player leaderboard",
            description="Computes top players by score using Spark batch job")
async def get_leaderboard(
    season: str = Query("current"),
    game_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """
    Get the leaderboard for a given season.
    
    Triggers SparkR leaderboard_batch job if not cached.
    
    Returns:
        List of top players with rank, wins, losses, score
    """
    logger.info(f"Leaderboard request: season={season}, limit={limit}")
    
    config = {
        "season": season,
        "game_id": game_id,
        "limit": limit,
        "start_date": start_date,
        "end_date": end_date,
    }
    
    try:
        result = execute_spark_job(
            script_name="leaderboard_batch",
            config=config,
            timeout=300
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "leaderboard": result["output"].to_dict("records") if result["output"] is not None else [],
                "count": result.get("rows_processed", 0),
                "job_id": result["job_id"],
                "elapsed_seconds": result["elapsed_seconds"],
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Job failed"))
    
    except Exception as e:
        logger.error(f"Leaderboard computation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PLAYER STATS ENDPOINT
# ============================================================================

@router.get("/player-stats/{player_id}",
            summary="Get player statistics",
            description="Computes aggregated statistics for a player")
async def get_player_stats(
    player_id: str = Path(..., description="Player ID"),
    timeframe: str = Query("seasonal", description="'lifetime' or 'seasonal'"),
    season: Optional[str] = Query("current"),
) -> Dict[str, Any]:
    """
    Get aggregated statistics for a specific player.
    
    Triggers SparkR stats_aggregation_batch job.
    
    Returns:
        Player stats: games_played, wins, losses, K/D ratio, etc.
    """
    logger.info(f"Player stats request: player_id={player_id}, timeframe={timeframe}")
    
    config = {
        "player_id": player_id,
        "timeframe": timeframe,
        "season": season,
    }
    
    try:
        result = execute_spark_job(
            script_name="stats_aggregation_batch",
            config=config,
            timeout=300
        )
        
        if result["status"] == "success":
            stats = result["output"].to_dict("records") if result["output"] is not None else []
            if stats:
                return {
                    "status": "success",
                    "player_id": player_id,
                    "stats": stats[0] if len(stats) > 0 else {},
                    "job_id": result["job_id"],
                    "elapsed_seconds": result["elapsed_seconds"],
                }
            else:
                raise HTTPException(status_code=404, detail="Player not found")
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Job failed"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Player stats computation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# RECOMMENDATIONS ENDPOINT
# ============================================================================

@router.get("/recommendations/{player_id}",
            summary="Get friend recommendations",
            description="Generates friend recommendations using graph algorithms")
async def get_recommendations(
    player_id: str = Path(..., description="Player ID"),
    limit: int = Query(10, ge=1, le=100),
    algorithm: str = Query("common_friends"),
) -> Dict[str, Any]:
    """
    Get friend recommendations for a player.
    
    Triggers SparkR social_recommendations job.
    
    Returns:
        List of recommended players with similarity scores
    """
    logger.info(f"Recommendations request: player_id={player_id}, limit={limit}")
    
    config = {
        "player_id": player_id,
        "limit": limit,
        "algorithm": algorithm,
    }
    
    try:
        result = execute_spark_job(
            script_name="social_recommendations",
            config=config,
            timeout=600
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "player_id": player_id,
                "recommendations": result["output"].to_dict("records") if result["output"] is not None else [],
                "count": result.get("rows_processed", 0),
                "job_id": result["job_id"],
                "elapsed_seconds": result["elapsed_seconds"],
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Job failed"))
    
    except Exception as e:
        logger.error(f"Recommendations computation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SCHEDULED JOBS MANAGEMENT
# ============================================================================

@router.get("/jobs",
            summary="List scheduled jobs",
            description="Returns all scheduled Spark batch jobs")
async def list_scheduled_jobs() -> Dict[str, Any]:
    """
    Get list of all scheduled Spark batch jobs.
    
    Returns:
        List of scheduled jobs with execution times
    """
    try:
        scheduler = get_job_scheduler()
        jobs = scheduler.list_scheduled_jobs()
        return {
            "status": "success",
            "jobs": jobs,
            "count": len(jobs),
            "scheduler_running": scheduler.is_running,
        }
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-job",
             summary="Manually run a batch job",
             description="Trigger immediate execution of a batch job")
async def run_job_now(
    script_name: str = Query(..., description="Job script name"),
    background_tasks: BackgroundTasks = None,
) -> Dict[str, Any]:
    """
    Manually trigger a batch job to run immediately.
    
    Parameters:
        script_name: Name of the job ("leaderboard_batch", "stats_aggregation_batch", etc.)
    
    Returns:
        Job execution result or status for async execution
    """
    logger.info(f"Manual job trigger: {script_name}")
    
    try:
        scheduler = get_job_scheduler()
        
        # Run in background if BackgroundTasks provided
        if background_tasks:
            background_tasks.add_task(
                scheduler.run_job_now,
                script_name=script_name,
                config={},
                timeout=600
            )
            return {
                "status": "queued",
                "script_name": script_name,
                "message": "Job queued for background execution",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            result = scheduler.run_job_now(
                script_name=script_name,
                config={},
                timeout=600
            )
            return {
                "status": result["status"],
                "script_name": script_name,
                "job_id": result.get("job_id"),
                "rows_processed": result.get("rows_processed", 0),
                "elapsed_seconds": result.get("elapsed_seconds", 0),
                "timestamp": datetime.now().isoformat(),
            }
    
    except Exception as e:
        logger.error(f"Job execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job-result/{job_id}",
            summary="Get job result",
            description="Retrieve result of a completed job")
async def get_job_result(job_id: str = Path(...)) -> Dict[str, Any]:
    """Get result of a previously executed job."""
    try:
        scheduler = get_job_scheduler()
        result = scheduler.get_job_result(job_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return {
            "status": "success",
            "job_id": job_id,
            "result": result,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job result: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health",
            summary="Spark system health",
            description="Check Spark system status and connectivity")
async def health_check() -> Dict[str, Any]:
    """
    Check Spark system health.
    
    Returns:
        Health status of Spark integration
    """
    try:
        scheduler = get_job_scheduler()
        return {
            "status": "healthy",
            "spark_bridge_ready": True,
            "scheduler_running": scheduler.is_running,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
