# Identify user directory to have a reference path to load the utils
#       (assuming that it is inside one of these three dirs, at any depth level)

get_script_path <- function() {
  script_path <- ifelse(length(commandArgs(trailingOnly = F))>2,
                              normalizePath(gsub("--file=","",
                                                 commandArgs(trailingOnly = F)[4])),
                              normalizePath(rstudioapi::getActiveDocumentContext()$path))
   # fallback if running in IRkernel / notebook
  if (script_path == "IRkernel::main()") {
    script_path <- normalizePath(getwd())
  }

  script_path <- paste0(script_path, "/")
    
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

# Examples of loading / parsing data 
meta_df <- data.table::fread(config$metadata)
expand(config$data$bam, sample=c(meta_df$sample))
fread(config$data$sorted_sam)
meta_df$sample


