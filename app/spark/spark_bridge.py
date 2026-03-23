"""
Python-R Bridge for Spark Integration

This module provides utilities to execute SparkR jobs from Python (FastAPI)
using subprocess and Parquet file exchange. It handles:
- Launching R scripts with environment configuration
- Data transfer via Parquet/Arrow
- Error handling and logging
- Job status tracking
"""

import subprocess
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import pandas as pd
import pyarrow.parquet as pq

# Configure logging
logger = logging.getLogger(__name__)


class SparkRBridge:
    """
    Bridge for communicating between Python and SparkR via subprocess.
    
    Data exchange format: Parquet files
    Communication: JSON config files + subprocess
    """
    
    def __init__(self, spark_home: str = None, r_binary: str = "Rscript"):
        """
        Initialize the Spark-R bridge.
        
        Args:
            spark_home: Path to Spark installation (auto-detect if None)
            r_binary: Path to Rscript executable
        """
        self.r_binary = r_binary
        self.spark_home = spark_home or self._detect_spark_home()
        self.temp_dir = tempfile.mkdtemp(prefix="spark_bridge_")
        self.job_id = None
        self.job_log = []
        
        logger.info(f"SparkRBridge initialized. Temp dir: {self.temp_dir}")
        logger.info(f"R binary: {self.r_binary}")
        logger.info(f"Spark home: {self.spark_home}")
    
    def _detect_spark_home(self) -> str:
        """Auto-detect Spark installation directory."""
        spark_home = os.environ.get("SPARK_HOME")
        if spark_home:
            logger.info(f"Found SPARK_HOME: {spark_home}")
            return spark_home
        
        # Common locations on different OSes
        common_paths = [
            "/opt/spark",
            "/usr/local/spark",
            "C:\\spark",
            os.path.expanduser("~/spark"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found Spark at: {path}")
                return path
        
        logger.warning("Could not auto-detect SPARK_HOME. Set SPARK_HOME environment variable.")
        return ""
    
    def execute_job(self,
                   script_path: str,
                   input_data: Optional[pd.DataFrame] = None,
                   config: Optional[Dict[str, Any]] = None,
                   timeout: int = 300) -> Dict[str, Any]:
        """
        Execute a SparkR job from Python.
        
        Args:
            script_path: Path to R script (e.g., "spark/jobs/leaderboard_batch.r")
            input_data: Optional pandas DataFrame to pass to R
            config: Optional configuration dict for the job
            timeout: Execution timeout in seconds
        
        Returns:
            Dict with results, status, and metadata
        
        Example:
            result = bridge.execute_job(
                script_path="spark/jobs/leaderboard_batch.r",
                config={"season": "2024", "limit": 100},
                timeout=600
            )
        """
        self.job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        start_time = datetime.now()
        
        logger.info(f"[{self.job_id}] Starting job: {script_path}")
        
        try:
            # Prepare input/output file paths
            input_parquet = None
            output_parquet = os.path.join(self.temp_dir, f"output_{self.job_id}.parquet")
            config_json = os.path.join(self.temp_dir, f"config_{self.job_id}.json")
            log_file = os.path.join(self.temp_dir, f"job_{self.job_id}.log")
            
            # Write input data if provided
            if input_data is not None:
                input_parquet = os.path.join(self.temp_dir, f"input_{self.job_id}.parquet")
                input_data.to_parquet(input_parquet)
                logger.info(f"Input data written: {input_parquet} ({len(input_data)} rows)")
            
            # Write config
            if config is None:
                config = {}
            config.update({
                "input_parquet": input_parquet,
                "output_parquet": output_parquet,
                "log_file": log_file,
                "job_id": self.job_id,
            })
            
            with open(config_json, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            logger.info(f"Config written: {config_json}")
            
            # Build R command
            r_script = self._create_wrapper_script(script_path, config_json, output_parquet)
            
            # Execute R script
            logger.info(f"Executing R script: {r_script}")
            result = self._run_r_script(r_script, timeout, log_file)
            
            # Read output if exists
            output_data = None
            if os.path.exists(output_parquet):
                output_data = pd.read_parquet(output_parquet)
                logger.info(f"Output data read: {len(output_data)} rows")
            
            # Read job log
            job_log_content = ""
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    job_log_content = f.read()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "job_id": self.job_id,
                "script": script_path,
                "output": output_data,
                "output_path": output_parquet,
                "config": config,
                "log": job_log_content,
                "elapsed_seconds": elapsed,
                "rows_processed": len(output_data) if output_data is not None else 0,
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"[{self.job_id}] Job timeout after {timeout} seconds")
            return {
                "status": "timeout",
                "job_id": self.job_id,
                "script": script_path,
                "error": f"Job exceeded {timeout} second timeout",
                "elapsed_seconds": (datetime.now() - start_time).total_seconds(),
            }
        
        except Exception as e:
            logger.error(f"[{self.job_id}] Job failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "job_id": self.job_id,
                "script": script_path,
                "error": str(e),
                "elapsed_seconds": (datetime.now() - start_time).total_seconds(),
            }
    
    def _create_wrapper_script(self,
                              r_script_path: str,
                              config_json: str,
                              output_parquet: str) -> str:
        """
        Create a wrapper R script that:
        1. Sources the main job script
        2. Loads config from JSON
        3. Executes the job
        4. Saves output to Parquet
        """
        # Ensure script path is absolute
        if not os.path.isabs(r_script_path):
            r_script_path = os.path.abspath(r_script_path)
        
        wrapper_path = os.path.join(self.temp_dir, f"wrapper_{self.job_id}.r")
        
        wrapper_code = f"""#!/usr/bin/env Rscript
# Auto-generated wrapper script
# Generated: {datetime.now().isoformat()}
# Job ID: {self.job_id}

# Load required libraries
library(SparkR)
library(data.table)
library(jsonlite)
library(arrow)

# Source SparkR config utilities
tryCatch({{
  source("{self._get_config_r_path()}")
}}, error = function(e) {{
  cat("[WARN] Could not source config.r:", e$message, "\\n")
}})

# Load job configuration
config <- fromJSON("{config_json}")
cat("[INFO] Configuration loaded\\n")

# Source the main job script
tryCatch({{
  source("{r_script_path}")
}}, error = function(e) {{
  cat("[ERROR] Failed to source job script:", e$message, "\\n")
  stop(e)
}})

cat("[INFO] Job script sourced\\n")

# Execute main job function (expected to be defined in the job script)
tryCatch({{
  result <- run_job(config)
  cat("[SUCCESS] Job completed\\n")
  
  # Save result to Parquet
  if (is.data.frame(result) || inherits(result, "SparkDataFrame")) {{
    write.parquet(result, "{output_parquet}")
    cat("[INFO] Result saved to {output_parquet}\\n")
  }}
}}, error = function(e) {{
  cat("[ERROR] Job execution failed:", e$message, "\\n")
  stop(e)
}})

cat("[DONE]\\n")
"""
        
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_code)
        
        logger.info(f"Wrapper script created: {wrapper_path}")
        return wrapper_path
    
    def _get_config_r_path(self) -> str:
        """Get path to spark/config.r"""
        # This should be relative to the project root
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "spark",
            "config.r"
        )
        return config_path
    
    def _run_r_script(self,
                     script_path: str,
                     timeout: int,
                     log_file: str) -> None:
        """Execute R script via subprocess."""
        
        env = os.environ.copy()
        if self.spark_home:
            env["SPARK_HOME"] = self.spark_home
        
        cmd = [self.r_binary, script_path]
        
        logger.info(f"Command: {' '.join(cmd)}")
        
        with open(log_file, 'w') as log_f:
            process = subprocess.Popen(
                cmd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
                env=env,
                cwd=os.path.dirname(script_path) or "."
            )
            
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                raise
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Error cleaning up temp directory: {e}")


# Singleton instance
_bridge_instance: Optional[SparkRBridge] = None


def get_spark_bridge() -> SparkRBridge:
    """Get or create singleton SparkRBridge instance."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = SparkRBridge()
    return _bridge_instance


def execute_spark_job(script_name: str,
                     input_data: Optional[pd.DataFrame] = None,
                     config: Optional[Dict[str, Any]] = None,
                     timeout: int = 300) -> Dict[str, Any]:
    """
    Execute a SparkR job with given parameters.
    
    Args:
        script_name: Name of the job (e.g., "leaderboard_batch")
        input_data: Optional input DataFrame
        config: Optional job configuration
        timeout: Execution timeout in seconds
    
    Returns:
        Job result dictionary
    
    Example:
        result = execute_spark_job(
            script_name="leaderboard_batch",
            config={"season": "2024"},
            timeout=600
        )
        if result["status"] == "success":
            df = result["output"]
        else:
            print(f"Error: {result['error']}")
    """
    bridge = get_spark_bridge()
    script_path = f"spark/jobs/{script_name}.r"
    return bridge.execute_job(script_path, input_data, config, timeout)


if __name__ == "__main__":
    # Test bridge setup
    logger.basicConfig(level=logging.INFO)
    bridge = SparkRBridge()
    print(f"Bridge initialized. Temp dir: {bridge.temp_dir}")
    print(f"R binary: {bridge.r_binary}")
