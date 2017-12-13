###########################################################################
#
# Project: Historical Census Data
#
# Script purpose: Extract appropriate fields from Social Explorer tables
#
# Notes:
#
###########################################################################

library(tidyverse)

get_one_year <- function(year, variable_table) {
  
  get_column <- function(var) {
    if (keys[[var]] != '') { df[[paste0("SE_", keys[[var]])]] } 
    else { NA }
  }
  
  get_base_df <- function(df, keys, year) {
    new_df <- df %>% select(one_of(unlist(keys[2:4])))
    names(new_df) <- names(keys[2:4])
    cbind("g_yr" = year, new_df)
  }
  
  df <- read.csv(paste0('data/variables_', year, '.csv')) %>% 
    mutate(g_yr = year)
  keys <- variable_table %>% filter(g_yr == year) %>%  as.list
  
  dat <- get_base_df(df, keys, year)
  for (var in names(keys[5:length(keys)])) {
    dat[[var]] <- get_column(var)
  }
  
  # Make specific adjustments for specific years
  if (year == 2010) {
    acs <- read.csv("data/variables_2010_acs.csv")
    income_var <- filter(variable_table, g_yr == '2010_acs')[["I"]] %>%
      paste0("SE_", .)
    dat[["I"]] <- acs[[income_var]]
  }
  if (is.na(dat[['t_h_wh']][1])) {
    dat[['t_h_wh']] <- dat[['t_h_wh_fm']] + dat[['t_h_wh_nf']]
    dat[['t_h_or']] <- dat[['t_h_or_fm']] + dat[['t_h_or_nf']]
  }
  
  # remove unnecessary columns
  dat <- select(dat, -one_of(c('t_h_wh_fm', 't_h_wh_nf', 't_h_or_fm', 't_h_or_nf')))
  dat
}

get_list_of_dfs <- function() {
  vt <- read.csv("data/variable_names.csv", stringsAsFactors = FALSE)
  all_dfs <- plyr::llply(as.character(seq(1940, 2010, 10)), get_one_year, 
                         variable_table = vt)
  names(all_dfs) <- as.character(seq(1940, 2010, 10))
  all_dfs
}
