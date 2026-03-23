# SparkR Configuration and Initialization
# This file contains utility functions and configuration for SparkR sessions

library(SparkR)
library(dplyr)
library(tidyr)
library(data.table)
library(jsonlite)
library(lubridate)
library(lgr)

# ============================================================================
# INITIALIZE SPARK SESSION
# ============================================================================

#' Initialize SparkR Session
#'
#' @param app_name Application name for Spark
#' @param master Spark master URL (local, yarn, mesos, etc.)
#' @param memory Executor memory (e.g., "4g")
#' @param cores Number of cores per executor
#' @param mode Deployment mode: "local", "local-cluster", "yarn-client", "yarn-cluster"
#'
#' @return SparkSession object
#'
#' @examples
#' spark <- init_spark_session("GameDB-Analytics", master="local[*]", memory="4g")

init_spark_session <- function(app_name = "GameDB-Analytics",
                              master = "local[*]",
                              memory = "4g",
                              cores = 4,
                              mode = "local") {
  
  cat("[INFO] Initializing SparkR Session...\n")
  cat("[INFO] App Name:", app_name, "\n")
  cat("[INFO] Master:", master, "\n")
  cat("[INFO] Memory:", memory, "\n")
  
  tryCatch({
    spark <- sparkR.session(
      appName = app_name,
      master = master,
      sparkConfig = list(
        "spark.executor.memory" = memory,
        "spark.driver.memory" = memory,
        "spark.cores.max" = as.character(cores),
        "spark.sql.shuffle.partitions" = "200",
        "spark.sql.adaptive.enabled" = "true",
        "spark.sql.adaptive.coalescePartitions.enabled" = "true"
      )
    )
    
    cat("[SUCCESS] SparkR Session initialized!\n")
    cat("[INFO] Spark Version:", sparkR.version(), "\n")
    
    return(spark)
    
  }, error = function(e) {
    cat("[ERROR] Failed to initialize Spark:", e$message, "\n")
    stop(e)
  })
}

# ============================================================================
# MONGODB UTILITIES
# ============================================================================

#' Read data from MongoDB into Spark DataFrame
#'
#' @param spark SparkR session
#' @param database MongoDB database name
#' @param collection MongoDB collection name
#' @param mongodb_uri MongoDB connection URI
#' @param filter_query Aggregation pipeline filter (optional)
#'
#' @return SparkR DataFrame

read_mongodb <- function(spark, 
                        database, 
                        collection,
                        mongodb_uri = "mongodb://localhost:27017",
                        filter_query = NULL) {
  
  cat("[INFO] Reading from MongoDB:", database, ".", collection, "\n")
  
  # Build MongoDB connector options
  options_list <- list(
    uri = mongodb_uri,
    database = database,
    collection = collection
  )
  
  if (!is.null(filter_query)) {
    options_list$aggregationPipeline <- filter_query
  }
  
  # Read using MongoDB connector
  df <- read.df(
    source = "mongodb",
    options = options_list
  )
  
  return(df)
}

#' Write Spark DataFrame to MongoDB
#'
#' @param df Spark DataFrame
#' @param database MongoDB database name
#' @param collection MongoDB collection name
#' @param mongodb_uri MongoDB connection URI
#' @param mode Write mode: "overwrite", "append", "ignore", "error"

write_mongodb <- function(df,
                         database,
                         collection,
                         mongodb_uri = "mongodb://localhost:27017",
                         mode = "append") {
  
  cat("[INFO] Writing to MongoDB:", database, ".", collection, "\n")
  cat("[INFO] Mode:", mode, "\n")
  
  write.df(
    df = df,
    source = "mongodb",
    mode = mode,
    path = paste0(mongodb_uri, "/", database, ".", collection),
    database = database,
    collection = collection
  )
  
  cat("[SUCCESS] Data written to MongoDB\n")
}

# ============================================================================
# PARQUET I/O FOR PYTHON-R BRIDGE
# ============================================================================

#' Read Parquet file (typically from Python via subprocess bridge)
#'
#' @param spark SparkR session
#' @param file_path Path to Parquet file
#'
#' @return SparkR DataFrame

read_parquet_bridge <- function(spark, file_path) {
  cat("[INFO] Reading Parquet from Python:", file_path, "\n")
  df <- read.parquet(spark, file_path)
  cat("[SUCCESS] Parquet loaded\n")
  return(df)
}

#' Write Parquet file (for Python to read via subprocess bridge)
#'
#' @param df Spark DataFrame
#' @param file_path Path to write Parquet file

write_parquet_bridge <- function(df, file_path) {
  cat("[INFO] Writing Parquet for Python:", file_path, "\n")
  write.parquet(df, file_path)
  cat("[SUCCESS] Parquet written\n")
}

# ============================================================================
# LOGGING UTILITIES
# ============================================================================

#' Setup structured logging for Spark jobs
#'
#' @param log_file Path to log file

setup_logging <- function(log_file = "spark_jobs.log") {
  
  lg <- get_logger("root")
  lg$set_threshold("debug")
  
  # File appender
  lg$add_appender(AppenderFile$new(file = log_file))
  
  # Console appender (info+)
  lg$add_appender(AppenderConsole$new(), name = "console")
  
  cat(sprintf("[LOGGING] Initialized at %s\n", log_file))
}

#' Log job completion
#'
#' @param job_name Name of the Spark job
#' @param start_time Start timestamp
#' @param record_count Number of records processed

log_job_completion <- function(job_name, start_time, record_count = NA) {
  elapsed <- difftime(Sys.time(), start_time, units = "secs")
  
  if (is.na(record_count)) {
    cat(sprintf(
      "[JOB COMPLETE] %s - Duration: %.2f seconds\n",
      job_name, as.numeric(elapsed)
    ))
  } else {
    throughput <- as.numeric(record_count) / as.numeric(elapsed)
    cat(sprintf(
      "[JOB COMPLETE] %s - Duration: %.2f seconds - Records: %d - Throughput: %.0f records/sec\n",
      job_name, as.numeric(elapsed), record_count, throughput
    ))
  }
}

# ============================================================================
# DATA TRANSFORMATION UTILITIES
# ============================================================================

#' Standardize DataFrame column types
#'
#' @param df Spark DataFrame
#' @param schema_map Named list mapping column names to Spark types

cast_columns <- function(df, schema_map) {
  for (col_name in names(schema_map)) {
    col_type <- schema_map[[col_name]]
    df <- withColumn(df, col_name, cast(column(col_name), col_type))
  }
  return(df)
}

#' Filter DataFrame with safe NULL handling
#'
#' @param df Spark DataFrame
#' @param condition Filter condition
#'
#' @return Filtered DataFrame

safe_filter <- function(df, condition) {
  tryCatch({
    return(filter(df, condition))
  }, error = function(e) {
    cat("[ERROR] Filter failed:", e$message, "\n")
    return(df)
  })
}

# ============================================================================
# SESSION UTILITIES
# ============================================================================

#' Stop Spark session safely
#'
#' @param spark SparkR session

stop_spark_session <- function(spark) {
  tryCatch({
    sparkR.session.stop()
    cat("[INFO] Spark session stopped\n")
  }, error = function(e) {
    cat("[WARN] Error stopping Spark:", e$message, "\n")
  })
}

#' Get Spark session info
#'
#' @return List with session details

get_spark_info <- function() {
  tryCatch({
    list(
      version = sparkR.version(),
      default_parallelism = sparkR.conf("spark.default.parallelism"),
      sql_shuffle_partitions = sparkR.conf("spark.sql.shuffle.partitions")
    )
  }, error = function(e) {
    cat("[ERROR] Could not get Spark info:", e$message, "\n")
    return(NULL)
  })
}

cat("[SUCCESS] SparkR configuration loaded\n")
