"""Spark integration utilities for FastAPI.

- spark_bridge.py: Python-R subprocess bridge for executing SparkR jobs
"""

from .spark_bridge import SparkRBridge, get_spark_bridge, execute_spark_job

__all__ = ["SparkRBridge", "get_spark_bridge", "execute_spark_job"]
