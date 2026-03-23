# Player Statistics Aggregation Batch Job
# Calculates lifetime and seasonal player statistics
#
# Input config:
#   - player_id: Optional filter for single player
#   - season: Season for stats calculation
#   - timeframe: "lifetime" or "seasonal"
#
# Output: DataFrame with columns: player_id, player_name, games_played, wins, 
#         losses, kills, deaths, average_score, win_rate, etc.

library(SparkR)
library(dplyr)
library(lubridate)

run_job <- function(config) {
  
  start_time <- Sys.time()
  cat("[JOB] Stats Aggregation Batch Job Starting\n")
  
  # Initialize Spark
  tryCatch({
    spark <- sparkR.session.getOrCreate()
  }, error = function(e) {
    spark <- sparkR.session(
      appName = "StatsAggregationBatch",
      master = "local[*]"
    )
  })
  
  # Extract parameters
  player_id <- config$player_id
  season <- config$season %||% "current"
  timeframe <- config$timeframe %||% "seasonal"
  
  cat("[INFO] Parameters:\n")
  cat("[INFO]   player_id:", player_id, "(optional)\n")
  cat("[INFO]   season:", season, "\n")
  cat("[INFO]   timeframe:", timeframe, "\n")
  
  # Read match history
  if (!is.null(config$input_parquet) && file.exists(config$input_parquet)) {
    cat("[INFO] Reading input from Parquet\n")
    match_history <- read.parquet(spark, config$input_parquet)
  } else {
    # Placeholder: Load from MongoDB
    cat("[INFO] Reading from MongoDB\n")
    match_history <- createDataFrame(
      data.frame(
        match_id = character(0),
        player_id = character(0),
        kills = integer(0),
        deaths = integer(0),
        score = numeric(0),
        result = character(0),
        timestamp = character(0)
      ),
      schema = "match_id STRING, player_id STRING, kills INT, deaths INT, 
                score DOUBLE, result STRING, timestamp STRING"
    )
  }
  
  cat("[INFO] Match history loaded:", nrow(match_history), "rows\n")
  
  # Filter by player_id if provided
  if (!is.null(player_id) && !is.na(player_id)) {
    match_history <- filter(match_history, column("player_id") == player_id)
    cat("[INFO] Filtered to player:", player_id, "-", nrow(match_history), "matches\n")
  }
  
  # Calculate aggregated stats
  player_stats <- match_history %>%
    groupBy("player_id") %>%
    agg(
      games_played = n(),
      wins = sum(when(column("result") == "win", 1L), 0L),
      losses = sum(when(column("result") == "loss", 1L), 0L),
      total_kills = sum(column("kills")),
      total_deaths = sum(column("deaths")),
      total_score = sum(column("score")),
      average_kills = mean(column("kills")),
      average_deaths = mean(column("deaths")),
      average_score = mean(column("score"))
    ) %>%
    withColumn("win_rate", column("wins") / column("games_played")) %>%
    withColumn("kd_ratio", column("total_kills") / 
               when(column("total_deaths") > 0, column("total_deaths"), 1))
  
  # Convert to R data frame
  stats_df <- collect(player_stats)
  
  elapsed <- difftime(Sys.time(), start_time, units = "secs")
  cat("[JOB COMPLETE] Stats Aggregation - Duration:", as.numeric(elapsed), "seconds\n")
  cat("[JOB COMPLETE] Players processed:", nrow(stats_df), "\n")
  
  return(stats_df)
}

`%||%` <- function(x, y) {
  if (is.null(x) || is.na(x)) y else x
}

when <- function(condition, true_value) {
  SparkR::when(condition, true_value)
}
