####################---------------- HEADER ----------------####################

# Use always this header in your R scripts
# Identify user directory to have a reference path to load the utils 
#       (assuming that it is inside one of these three dirs, at any depth level)

get_script_path <- function() {
  script_path <- ifelse(length(commandArgs(trailingOnly = F))>2,
                              normalizePath(gsub("--file=","",
                                                 commandArgs(trailingOnly = F)[4])),
                              normalizePath(rstudioapi::getActiveDocumentContext()$path))
  return(script_path)
}
script_path <- get_script_path()
user_dir <- gsub("/metadata/|/processing/|/analysis/.*", "", script_path)

# Source all utils and set up environment
source(paste0(user_dir, "/resources/utils.r"))
config <- set_up_config(user_dir)

# Load libraries
library(tidyverse)
library(data.table)
####################----------------------------------------####################

# Paths are stored in the config file, that should be always updated
# Alternatively, files that are not of so much interest can be referred to
#   with paths relative to your user directory
config$data$sam

