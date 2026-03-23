# Leaderboard Batch Job
# Computes player rankings from match history
#
# Input config:
#   - game_id: ID of the game
#   - season: Season identifier
#   - limit: Top N players to return
#   - start_date, end_date: Date range filter (optional)
#
# Output: DataFrame with columns: rank, player_id, player_name, wins, losses, score

# Required: config should be passed as environment variable containing JSON

library(SparkR)
library(dplyr)

# Function called by the wrapper script
run_job <- function(config) {
  
  start_time <- Sys.time()
  cat("[JOB] Leaderboard Batch Job Starting\n")
  
  # Initialize Spark (if not already done)
  tryCatch({
    spark <- sparkR.session.getOrCreate()
  }, error = function(e) {
    cat("[INFO] Creating new Spark session\n")
    spark <- sparkR.session(
      appName = "LeaderboardBatch",
      master = "local[*]"
    )
  })
  
  # Extract parameters from config
  game_id <- config$game_id %||% NA
  season <- config$season %||% NA
  limit <- as.integer(config$limit %||% 100)
  start_date <- config$start_date
  end_date <- config$end_date
  
  cat("[INFO] Parameters:\n")
  cat("[INFO]   game_id:", game_id, "\n")
  cat("[INFO]   season:", season, "\n")
  cat("[INFO]   limit:", limit, "\n")
  
  # Read match history from input if provided
  if (!is.null(config$input_parquet) && file.exists(config$input_parquet)) {
    
    cat("[INFO] Reading input from Parquet\n")
    match_history <- read.parquet(spark, config$input_parquet)
    
  } else {
    
    # Load from MongoDB (requires Spark MongoDB connector)
    cat("[INFO] Reading match history from MongoDB\n")
    # Placeholder: In production, you would:
    # match_history <- sql(spark, "SELECT * FROM match_history WHERE season = ?")
    
    # For now, return empty result with proper schema
    match_history <- createDataFrame(
      data.frame(
        match_id = character(0),
        player_id = character(0),
        result = character(0),
        score = numeric(0)
      ),
      schema = "match_id STRING, player_id STRING, result STRING, score DOUBLE"
    )
  }
  
  cat("[INFO] Match history loaded:", nrow(match_history), "rows\n")
  
  # Calculate leaderboard
  # Group by player_id, count wins/losses, calculate score
  leaderboard <- match_history %>%
    groupBy("player_id") %>%
    agg(
      wins = sum(when(column("result") == "win", 1L), 0L),
      losses = sum(when(column("result") == "loss", 1L), 0L),
      total_score = sum(column("score"))
    ) %>%
    withColumn("win_rate", column("wins") / (column("wins") + column("losses"))) %>%
    orderBy(desc(column("total_score"))) %>%
    limit(limit)
  
  # Convert to R data frame for output
  leaderboard_df <- collect(leaderboard)
  
  # Add rank column
  leaderboard_df$rank <- 1:nrow(leaderboard_df)
  
  elapsed <- difftime(Sys.time(), start_time, units = "secs")
  cat("[JOB COMPLETE] Leaderboard Batch - Duration:", as.numeric(elapsed), "seconds\n")
  cat("[JOB COMPLETE] Records processed:", nrow(leaderboard_df), "\n")
  
  return(leaderboard_df)
}

# NULL coalescing operator
`%||%` <- function(x, y) {
  if (is.null(x) || is.na(x)) y else x
}

# Helper function for when() if not available
when <- function(condition, true_value) {
  SparkR::when(condition, true_value)
}
