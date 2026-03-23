# Player Stats Streaming Job
# Real-time updates of player statistics from match events
# Using SparkR Structured Streaming
#
# Streaming source: MongoDB Change Streams or Kafka
# Streaming sink: Redis cache + MongoDB upsert
# Micro-batch interval: 60 seconds
#
# Input: Match result events (streaming)
#   - match_id, player_id, result, kills, deaths, score, timestamp
#
# Output: Updated player_stats collection in MongoDB

library(SparkR)
library(dplyr)

run_job <- function(config) {
  
  start_time <- Sys.time()
  cat("[JOB] Stats Streaming Job Starting\n")
  
  # Initialize Spark with streaming support
  tryCatch({
    spark <- sparkR.session.getOrCreate()
  }, error = function(e) {
    spark <- sparkR.session(
      appName = "StatsStreaming",
      master = "local[*]",
      sparkConfig = list(
        "spark.sql.streaming.schemaInference" = "true"
      )
    )
  })
  
  cat("[INFO] Spark session initialized (streaming enabled)\n")
  
  # Extract streaming parameters
  trigger_interval <- config$trigger_interval_seconds %||% 60
  checkpoint_path <- config$checkpoint_path %||% "/tmp/spark_streaming_checkpoint"
  
  cat("[INFO] Streaming configuration:\n")
  cat("[INFO]   Trigger interval:", trigger_interval, "seconds\n")
  cat("[INFO]   Checkpoint path:", checkpoint_path, "\n")
  
  # ============================================================================
  # Define streaming source
  # ============================================================================
  # This is a placeholder. In production, you would:
  # 1. Use Kafka source with: readStream("kafka", subscribePattern="match_results")
  # 2. Use MongoDB Change Streams with appropriate connector
  # 3. Use file source for testing: readStream("parquet", path="/incoming/matches")
  
  # For now, create a mock streaming DataFrame with proper schema
  schema <- structType(
    structField("match_id", "string"),
    structField("player_id", "string"),
    structField("result", "string"),
    structField("kills", "integer"),
    structField("deaths", "integer"),
    structField("score", "double"),
    structField("timestamp", "long")  # Unix timestamp in milliseconds
  )
  
  # In production, replace with actual streaming source:
  # stream_df <- readStream(spark, source="kafka", ...)
  
  cat("[INFO] Streaming schema defined\n")
  cat("[WARN] Using mock data - implement real streaming source in production\n")
  
  # ============================================================================
  # Define streaming transformation
  # ============================================================================
  
  # Aggregate stats over time windows (if needed)
  # This example uses micro-batch (no time window)
  
  # Transformation: group by player and calculate incremental stats
  # (In production, you'd join with existing player_stats and update)
  
  stats_stream <- "stub_data"  # Placeholder
  
  cat("[INFO] Streaming transformations defined\n")
  
  # ============================================================================
  # Define streaming sink (output)
  # ============================================================================
  
  # Option 1: Write to console (for testing)
  # writeStream(stats_stream, "console", outputMode = "update", checkpointLocation = checkpoint_path)
  
  # Option 2: Write to MongoDB (production)
  # writeStream(stats_stream, "mongodb", 
  #            outputMode = "update",
  #            options = list(uri = config$mongodb_uri, collection = "player_stats"),
  #            checkpointLocation = checkpoint_path)
  
  # Option 3: Write to Redis cache (fast, for realtime dashboard)
  # writeStream(stats_stream, "redis",
  #            outputMode = "complete",
  #            checkpointLocation = checkpoint_path)
  
  cat("[INFO] Streaming sink configured (console output for testing)\n")
  cat("[WARN] Connection to MongoDB/Redis sink not yet implemented\n")
  
  # For now, don't actually start streaming (requires proper setup)
  # In production:
  # query <- writeStream(...)
  # awaitTermination(query)
  
  elapsed <- difftime(Sys.time(), start_time, units = "secs")
  cat("[JOB] Stats Streaming Job - Initialization completed in", 
      as.numeric(elapsed), "seconds\n")
  cat("[JOB] Note: Streaming job should run continuously. Consider running as background task.\n")
  
  return(data.frame(
    status = "initialized",
    trigger_interval = trigger_interval,
    checkpoint_path = checkpoint_path,
    ready_for_production = FALSE
  ))
}

`%||%` <- function(x, y) {
  if (is.null(x) || is.na(x)) y else x
}

# Additional helper function for streaming management (future use)
get_streaming_status <- function() {
  cat("[INFO] Streaming status check - not yet implemented\n")
  return(list(
    active_queries = 0,
    total_rows_processed = 0,
    latency_ms = NA
  ))
}
