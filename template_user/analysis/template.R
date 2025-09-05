# scripts_dir <- 'scripts/'
# source(file.path('resources/utils.r'))
# config <- load_config_abs(scripts_dir)
# meta_df <- load_meta(scripts_dir)

# # load nanoplot data
# data <- list()
# for(sample in meta_df$sample){
  
#   predata <- fread(expand(config$lr$porechop$qc$nanoplot_stats,
#                                   sample=c(sample)), sep=":", fill=T)
#   data <- append(data, list(predata))
# }


get_script_dir <- function() {
  script_parent_dir <- ifelse(length(commandArgs(trailingOnly = F))>2,
                              dirname(normalizePath(gsub("--file=","",commandArgs(trailingOnly = F)[4]))),
                              dirname(normalizePath(rstudioapi::getActiveDocumentContext()$path)))
  # # Case 1: Running via Rscript
  # script_parent_dir <- dirname(normalizePath(gsub("--file=","",commandArgs(trailingOnly = F)[4])))
  # # Case 2: Running interactively in RStudio
  # if (requireNamespace("rstudioapi", quietly = TRUE) &&
  #     rstudioapi::isAvailable()) {
  #   script_parent_dir <- dirname(normalizePath(rstudioapi::getActiveDocumentContext()$path))}
  return(script_parent_dir)
}

# Usage:
print(get_script_dir())


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
