# HEADER -----------------------------------------------------------------------
library(here)
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
