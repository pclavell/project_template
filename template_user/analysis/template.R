# HEADER -----------------------------------------------------------------------
script_dir <- dirname(ifelse(length(commandArgs(trailingOnly = F))>2,normalizePath(gsub("--file=","", commandArgs(trailingOnly = F)[4])),
                              normalizePath(rstudioapi::getActiveDocumentContext()$path)))
script_dir <- dirname(ifelse(script_dir == "IRkernel::main()",normalizePath(getwd()), script_dir))
setwd(script_dir)
library(here)
setwd(here())
source(here("resources", "utils.r")) # here referes to where .here file sits (in the user dir)
config <- load_config(here()) # to refer to files in config use config$
paths <- load_paths(here()) # to refer to data, figs, metadata, ref, scratch use resources$
#--------------------------------------------------------------------------------

# Load libraries
library(tidyverse)
library(data.table)

# Examples of loading / parsing data (you can delete)
expand(config$data$bam, sample=c(meta_df$sample))
fread(config$data$sorted_sam)
