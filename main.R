###########################################################################
#
# Project: Historical Census Data
#
# Script purpose:
#
# Notes:
#
###########################################################################

source("R/compile_historical_census_data.R")

# Raw datasets (no pct or change calculated)
all_dfs <- get_list_of_dfs()
for (df in all_dfs) {
  f <- paste0("output/intermediary/raw_data_", df$g_yr[1], ".csv")
  write.csv(df, f)
}
