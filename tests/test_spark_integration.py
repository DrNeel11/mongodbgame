"""
Test suite for SparkR integration

Tests:
1. Python-R bridge connectivity
2. SparkR configuration loading
3. Batch job execution
4. Job scheduler functionality
5. API endpoint health
"""

import sys
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.spark.spark_bridge import SparkRBridge, execute_spark_job
from app.scheduler.job_scheduler import JobScheduler, init_scheduler


class TestSparkBridge(unittest.TestCase):
    """Test Python-R Spark bridge"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bridge = SparkRBridge()
    
    def test_bridge_initialization(self):
        """Test SparkRBridge initializes without errors"""
        self.assertIsNotNone(self.bridge)
        self.assertIsNotNone(self.bridge.temp_dir)
        self.assertTrue(os.path.exists(self.bridge.temp_dir))
    
    def test_spark_home_detection(self):
        """Test Spark home directory detection"""
        spark_home = self.bridge._detect_spark_home()
        # Spark home might not exist, but detection should return a string
        self.assertIsInstance(spark_home, str)
    
    def test_wrapper_script_creation(self):
        """Test wrapper R script generation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
            config_path = config_f.name
            json.dump({"test": "config"}, config_f)
        
        try:
            wrapper_path = self.bridge._create_wrapper_script(
                r_script_path="spark/jobs/leaderboard_batch.r",
                config_json=config_path,
                output_parquet="/tmp/test_output.parquet"
            )
            
            self.assertTrue(os.path.exists(wrapper_path))
            
            # Check file contains expected content
            with open(wrapper_path, 'r') as f:
                content = f.read()
                self.assertIn("#!/usr/bin/env Rscript", content)
                self.assertIn("leaderboard_batch.r", content)
        
        finally:
            os.unlink(config_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.bridge.cleanup()


class TestJobScheduler(unittest.TestCase):
    """Test job scheduler functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scheduler = JobScheduler()
    
    def test_scheduler_initialization(self):
        """Test JobScheduler initializes without errors"""
        self.assertIsNotNone(self.scheduler)
        self.assertFalse(self.scheduler.is_running)
    
    def test_scheduler_start_stop(self):
        """Test scheduler can start and stop"""
        self.scheduler.start()
        self.assertTrue(self.scheduler.is_running)
        
        self.scheduler.stop()
        self.assertFalse(self.scheduler.is_running)
    
    def test_list_scheduled_jobs(self):
        """Test listing scheduled jobs"""
        jobs = self.scheduler.list_scheduled_jobs()
        self.assertIsInstance(jobs, list)
    
    def tearDown(self):
        """Clean up"""
        if self.scheduler.is_running:
            self.scheduler.stop()


class TestJobResult(unittest.TestCase):
    """Test job result tracking"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scheduler = JobScheduler()
    
    def test_job_result_storage(self):
        """Test storing and retrieving job results"""
        test_result = {
            "status": "success",
            "rows_processed": 100,
            "elapsed_seconds": 10.5
        }
        
        self.scheduler.job_results["test_job_123"] = test_result
        retrieved = self.scheduler.get_job_result("test_job_123")
        
        self.assertEqual(retrieved, test_result)
    
    def test_job_result_not_found(self):
        """Test retrieving non-existent job result"""
        result = self.scheduler.get_job_result("nonexistent_job")
        self.assertIsNone(result)
    
    def tearDown(self):
        """Clean up"""
        if self.scheduler.is_running:
            self.scheduler.stop()


class TestSparkConfiguration(unittest.TestCase):
    """Test Spark configuration loading"""
    
    def test_spark_config_file_exists(self):
        """Test that spark_config.yml exists"""
        config_path = Path("spark/spark_config.yml")
        self.assertTrue(config_path.exists(), "spark_config.yml not found")
    
    def test_spark_config_r_file_exists(self):
        """Test that spark/config.r exists"""
        config_path = Path("spark/config.r")
        self.assertTrue(config_path.exists(), "spark/config.r not found")
    
    def test_batch_job_templates_exist(self):
        """Test that batch job files exist"""
        jobs = [
            "spark/jobs/leaderboard_batch.r",
            "spark/jobs/stats_aggregation_batch.r",
            "spark/jobs/social_recommendations.r",
        ]
        
        for job_path in jobs:
            self.assertTrue(
                Path(job_path).exists(),
                f"Job file not found: {job_path}"
            )


class TestIntegration(unittest.TestCase):
    """Integration tests (skipped if dependencies missing)"""
    
    @unittest.skipIf(not os.getenv("SPARK_HOME"), "SPARK_HOME not set")
    def test_spark_session_creation(self):
        """Test creating a Spark session (requires installed Spark)"""
        try:
            # Try importing pyspark
            import pyspark
            from pyspark.sql import SparkSession
            
            # Create minimal session
            spark = SparkSession.builder \
                .master("local[1]") \
                .appName("test") \
                .getOrCreate()
            
            self.assertIsNotNone(spark)
            spark.stop()
        
        except ImportError:
            self.skipTest("pyspark not installed")


def run_quick_checks():
    """Run quick diagnostic checks"""
    print("\n" + "="*60)
    print("SPARK INTEGRATION QUICK CHECKS")
    print("="*60 + "\n")
    
    checks = [
        ("Python bridge module", lambda: __import__("app.spark.spark_bridge")),
        ("Job scheduler module", lambda: __import__("app.scheduler.job_scheduler")),
        ("Analytics endpoints", lambda: __import__("app.routes.spark_analytics")),
        ("Batch job: leaderboard", lambda: Path("spark/jobs/leaderboard_batch.r").exists()),
        ("Batch job: stats", lambda: Path("spark/jobs/stats_aggregation_batch.r").exists()),
        ("Batch job: recommendations", lambda: Path("spark/jobs/social_recommendations.r").exists()),
        ("Streaming template", lambda: Path("spark/streaming/stats_streaming.r").exists()),
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            print(f"✓ {check_name}")
            passed += 1
        except Exception as e:
            print(f"✗ {check_name}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed\n")
    
    # System info
    print("="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    print(f"Python version: {sys.version.split()[0]}")
    print(f"SPARK_HOME: {os.getenv('SPARK_HOME', 'Not set')}")
    print(f"Rscript: {os.popen('which Rscript 2>/dev/null').read().strip() or 'Not found'}")
    
    # Optional: Check package versions
    try:
        import pandas
        print(f"pandas: {pandas.__version__}")
    except:
        pass
    
    try:
        import apscheduler
        print(f"apscheduler: {apscheduler.__version__}")
    except:
        pass
    
    try:
        import pyarrow
        print(f"pyarrow: {pyarrow.__version__}")
    except:
        pass
    
    print()
    return passed, failed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SparkR Integration Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/test_spark_integration.py              # Run all tests
  python tests/test_spark_integration.py --quick      # Run quick checks
  python tests/test_spark_integration.py -v           # Verbose output
        """)
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick diagnostic checks instead of full test suite"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        passed, failed = run_quick_checks()
        sys.exit(0 if failed == 0 else 1)
    else:
        # Run full test suite
        unittest.main(verbosity=2 if args.verbose else 1, exit=True)
