# HEADER ------------------------------------------------------------------------
if(interactive() & !rstudioapi::isAvailable()){setwd(getwd()) # WARNING: only works if run from Project_Dir/User_dir !!
}else{
  script_dir <- normalizePath(dirname(ifelse(interactive(), rstudioapi::getActiveDocumentContext()$path,
                                            gsub("--file=", "", commandArgs(trailingOnly = F)[4]))))
  script_dir <- normalizePath(ifelse(script_dir == "IRkernel::main()", getwd(), script_dir))
  setwd(script_dir)}
library(here)
setwd(here())
source(here("resources", "utils.r")) # here referes to where .here file sits (in the user dir)
config <- load_config() # to refer to files in config use config$
paths <- load_paths() # to refer to data, figs, metadata, ref, scratch use resources$
#--------------------------------------------------------------------------------

# Load libraries
library(tidyverse)
library(data.table)

# Examples of loading / parsing data (you can delete)
expand(config$data$bam, sample=c(meta_df$sample))
