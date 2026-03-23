# Social Recommendations Batch Job
# Generates friend recommendations using graph algorithms
#
# Input config:
#   - player_id: Player to generate recommendations for
#   - limit: Number of recommendations to return
#   - algorithm: "common_friends" or "cosine_similarity"
#
# Output: DataFrame with columns: player_id, recommended_player_id, 
#         recommended_player_name, similarity_score, common_friends_count

library(SparkR)
library(dplyr)

run_job <- function(config) {
  
  start_time <- Sys.time()
  cat("[JOB] Social Recommendations Batch Job Starting\n")
  
  # Initialize Spark
  tryCatch({
    spark <- sparkR.session.getOrCreate()
  }, error = function(e) {
    spark <- sparkR.session(
      appName = "SocialRecommendationsBatch",
      master = "local[*]"
    )
  })
  
  # Extract parameters
  player_id <- config$player_id
  limit <- as.integer(config$limit %||% 10)
  algorithm <- config$algorithm %||% "common_friends"
  
  cat("[INFO] Parameters:\n")
  cat("[INFO]   player_id:", player_id, "\n")
  cat("[INFO]   limit:", limit, "\n")
  cat("[INFO]   algorithm:", algorithm, "\n")
  
  if (is.null(player_id) || is.na(player_id)) {
    cat("[ERROR] player_id is required\n")
    return(data.frame())
  }
  
  # Read social graph data
  if (!is.null(config$input_parquet) && file.exists(config$input_parquet)) {
    cat("[INFO] Reading input from Parquet\n")
    friends_data <- read.parquet(spark, config$input_parquet)
  } else {
    # Placeholder: Load from Neo4j or MongoDB
    cat("[INFO] Reading social graph from data source\n")
    friends_data <- createDataFrame(
      data.frame(
        player_id = character(0),
        friend_id = character(0),
        friend_name = character(0),
        status = character(0)
      ),
      schema = "player_id STRING, friend_id STRING, friend_name STRING, status STRING"
    )
  }
  
  cat("[INFO] Social graph loaded:", nrow(friends_data), "edges\n")
  
  # Get current friends
  current_friends <- friends_data %>%
    filter(column("player_id") == player_id & column("status") == "accepted") %>%
    select(column("friend_id"))
  
  # Find common friends (friends of friends)
  recommendations <- friends_data %>%
    filter(column("player_id") %in% current_friends) %>%
    filter(column("friend_id") != player_id) %>%
    filter(column("status") == "accepted") %>%
    groupBy("friend_id") %>%
    agg(
      common_friends_count = n(),
      friend_name = first(column("friend_name"))
    ) %>%
    withColumn("similarity_score", column("common_friends_count") / 10.0) %>%
    orderBy(desc(column("common_friends_count"))) %>%
    limit(limit)
  
  # Convert to R data frame
  recommendations_df <- collect(recommendations)
  recommendations_df$player_id <- player_id
  
  elapsed <- difftime(Sys.time(), start_time, units = "secs")
  cat("[JOB COMPLETE] Social Recommendations - Duration:", as.numeric(elapsed), "seconds\n")
  cat("[JOB COMPLETE] Recommendations generated:", nrow(recommendations_df), "\n")
  
  return(recommendations_df)
}

`%||%` <- function(x, y) {
  if (is.null(x) || is.na(x)) y else x
}
