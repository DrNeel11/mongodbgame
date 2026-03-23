# SparkR and dependencies installation script
# Run this once to set up the R environment

# Install SparkR from CRAN
install.packages("SparkR", repos="https://cran.r-project.org")

# Data processing and utilities
install.packages(c(
  "dplyr",           # Data manipulation
  "tidyr",           # Data tidying
  "tidyverse",       # Meta package for data science
  "data.table",      # Fast data operations
  "foreach",         # Parallel iteration
  "doParallel",      # Parallel backend
  "itertools"        # Iterator tools
))

# JSON/MongoDB connectivity
install.packages(c(
  "jsonlite",        # JSON serialization
  "mongolite",       # MongoDB driver
  "neo2r"            # Neo4j driver (optional)
))

# Time series and analytics
install.packages(c(
  "lubridate",       # Date/time handling
  "zoo",             # Time series
  "forecast"         # Forecasting (optional)
))

# Arrow/Parquet support
install.packages(c(
  "arrow",           # Apache Arrow for fast I/O
  "parquet"          # Parquet file format
))

# Logging and utilities
install.packages(c(
  "lgr",             # Logging framework
  "futile.logger",   # Alternative logging
  "devtools"         # Development tools
))

# Optional: Graph processing (if using GraphX)
install.packages("igraph")

cat("All R packages installed successfully!\n")
