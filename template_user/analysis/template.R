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




scripts_dir = file.path(dirname(getwd()), 'resources/')
source(file.path(scripts_dir, 'utils.r'))
# load the metadata and the config file with the 
# absolute paths for the correct system 
config = load_config_abs(scripts_dir)
meta_df = load_meta(scripts_dir)
## Look at adapter content for a specific sample
sample = meta_df$sample[1]
fname = expand(config$lr$porechop$qc$nanoplot_stats,
               sample=c(sample))
print(sample)
print(fname)
df = read.table(fname, sep='\t')
files = expand(config$lr$porechop$qc$nanoplot_stats,
               sample=meta_df$sample)