####################---------------- HEADER ----------------####################

# Identify user directory to have a reference path to load the utils 
#       (assuming that it is inside one of these three dirs, at any depth level)

get_script_dir <- function() {
  script_parent_dir <- ifelse(length(commandArgs(trailingOnly = F))>2,
                              dirname(normalizePath(gsub("--file=","",commandArgs(trailingOnly = F)[4]))),
                              dirname(normalizePath(rstudioapi::getActiveDocumentContext()$path)))
  return(script_parent_dir)
}
script_dir <- get_script_dir()
user_dir <- gsub("/metadata/|/processing/|/analysis/.*", "", script_dir)

# Source all utils
source(paste0(user_dir, "/resources/utils.r"))

config <-yaml::read_yaml(paste0(user_dir, "/resources/config.yml"))
meta_df <- data.table::fread(paste0(user_dir,"/metadata/metadata.tsv"))


fread(config$example$sorted_sam)
meta_df$sample
# # load nanoplot data
# data <- list()
# for(sample in meta_df$sample){
  
#   predata <- fread(expand(config$lr$porechop$qc$nanoplot_stats,
#                                   sample=c(sample)), sep=":", fill=T)
#   data <- append(data, list(predata))
# }
expand(config$sam, sample=c(meta_df$sample))






# resources_dir <- 'resources/'
# source(file.path('resources/utils.r'))
# config <- load_config_abs(scripts_dir)
# meta_df <- load_meta(scripts_dir)
# 
# 
# 
# 
# 
# scripts_dir = file.path(dirname(getwd()), 'resources/')
# source(file.path(scripts_dir, 'utils.r'))
# # load the metadata and the config file with the 
# # absolute paths for the correct system 
# config = load_config_abs(scripts_dir)
# meta_df = load_meta(scripts_dir)
# ## Look at adapter content for a specific sample
# sample = meta_df$sample[1]
# fname = expand(config$lr$porechop$qc$nanoplot_stats,
#                sample=c(sample))
# print(sample)
# print(fname)
# df = read.table(fname, sep='\t')
# files = expand(config$lr$porechop$qc$nanoplot_stats,
#                sample=meta_df$sample)
# 
