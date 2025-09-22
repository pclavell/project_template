################################## README BEFORE USAGE ##################################

# This file contains functions to interface with the basic setup of the template repo
# Add all the functions you want; a good rule of thumb is if you feel you are copy+pasting
# the same code over and over, make it a function! =)

                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############

#' Set Up Configuration with User-Specific Resource Paths
#'
#' This function loads a configuration file and a resources file from a user
#' directory, then adjusts resource paths based on the current user and
#' machine. It returns a fully substituted configuration object for use in
#' downstream workflows.
#'
#' @param user_dir Character string. Path to the user directory containing the
#'   \code{resources/config.yml} and \code{resources/resources.yml} files.
#'
#' @details
#' The function performs the following steps:
#' \enumerate{
#'   \item Reads the main configuration from \code{config.yml}.
#'   \item Reads the resource mappings from \code{resources.yml}.
#'   \item Determines the current system username via \code{Sys.info()[["user"]]}.
#'   \item Filters the resource mappings to those specific to the current user.
#'   \item Flattens the nested resource mappings into a named vector.
#'   \item Substitutes placeholders in the configuration with absolute paths
#'         from the resource mappings using \code{replace_str_dict()}.
#' }
#'
#' @return A configuration object (typically a list) with all resource paths
#'   substituted and adjusted for the current user.
#'
#' @examples
#' \dontrun{
#' # Example directory containing resources:
#' user_dir <- "/home/alice/project"
#'
#' # Run setup
#' config <- set_up_config(user_dir)
#'
#' # Access values from the returned config
#' config$data_dir
#' }
#'
#' @seealso [yaml::read_yaml()], [Sys.info()], [replace_str_dict()]
#'
#' @export

load_config <- function(user_dir){
  #setwd
  setwd(user_dir)
  # read config file
  config_file <-yaml::read_yaml(paste0(user_dir, "/resources/config.yml"),  readLines.warn=FALSE)
  # read resources yml file
  resources_yml <- yaml::read_yaml(paste0(user_dir, "/resources/resources.yml"), readLines.warn=FALSE)
  # get username
  username <- Sys.info()[["user"]]
  # filter resources yml file depending on the user and machine
  resources_yml <- resources_yml[[username]]
  # Flatten resources yml to a named vector for substitution
  resources_vec <- unlist(resources_yml, use.names = TRUE)
  # Creation of proper absolute paths depending on machine and user
  config <-replace_str_dict(config_file, resources_vec)
  # Resolve all relative paths and symlinks
  config <- resolve_config_symlinks(config)

  return(config)
}

load_resources <- function(user_dir){
  #setwd
  setwd(user_dir)
  # read resources yml file
  resources_yml <- yaml::read_yaml(paste0(user_dir, "/resources/resources.yml"))
  # get username
  username <- Sys.info()[["user"]]
  # filter resources yml file depending on the user and machine
  resources <- resources_yml[[username]]
  names(resources) <- gsub("^\\\\\\{|\\\\\\}$", "", names(resources))
  return(resources)
}


replace_str_dict <- function(d, m) {
  #' Recursively replace substrings in all strings within a nested data structure.
  #'
  #' @param d A nested data structure: list, vector, or string.
  #' @param m A named character vector mapping substrings to replace
  #'   (names are patterns, values are replacements).
  #'
  #' @return The same type as input `d`, with replacements applied.
  #'
  #' @examples
  #' data <- list(path = "/home/user/data", files = c("file1.txt", "file2.txt"))
  #' mapping <- c("/home/user" = "/mnt/data")
  #' replace_str_dict(data, mapping)
  #' # $path
  #' # [1] "/mnt/data/data"
  #' #
  #' # $files
  #' # [1] "file1.txt" "file2.txt"

  if (is.list(d)) {
    # Handle named or unnamed lists recursively
    return(lapply(d, replace_str_dict, m = m))

  } else if (is.character(d) && length(d) == 1) {
    # Single string: apply replacements
    for (old in names(m)) {
      d <- gsub(old, m[[old]], d, fixed = TRUE)
    }
    return(d)

  } else if (is.character(d) && length(d) > 1) {
    # Character vector: apply replacements elementwise
    return(vapply(d, function(x) replace_str_dict(x, m), character(1)))

  } else {
    # Leave numbers, logicals, NULL, etc. untouched
    return(d)
  }
}

resolve_config_symlinks <- function(d) {
  #' Recursively resolve symlinks and relative paths in the config dictionary
  #'
  #' @param d A nested data structure: list, vector, or string.
  #'
  #' @return The same type as input `d`, with
  #'         symlinks and relative paths resolved'.
  #'

  if (is.list(d)) {
    # Handle named or unnamed lists recursively
    return(lapply(d, resolve_config_symlinks))

  } else if (is.character(d) && length(d) == 1) {
    # Single string: apply replacements
    d <- normalizePath(d, mustWork=FALSE)
    return(d)

  } else if (is.character(d) && length(d) > 1) {
    # Character vector: apply replacements elementwise
    return(vapply(d, function(x) resolve_config_symlinks(x), character(1)))

  } else {
    # Leave numbers, logicals, NULL, etc. untouched
    return(d)
  }
}




#' Expand a pattern with all combinations of variables
#'
#' Generates a vector of strings by substituting placeholders in a pattern
#' with all possible combinations of provided variables.
#'
#' @param pattern A character string containing placeholders in curly braces,
#'   e.g., "{x}", "{y}".
#' @param ... Named arguments, each being a vector of values to substitute into
#'   the pattern. All combinations of these values will be generated.
#'
#' @return A character vector of strings with placeholders replaced by the
#'   values from all combinations of the provided variables.
#'
#' @examples
#' expand("file_{x}_{y}.txt", x = 1:2, y = c("a", "b"))
#' # Returns: "file_1_a.txt" "file_2_a.txt" "file_1_b.txt" "file_2_b.txt"
#'
#' expand("path/{folder}/{file}.csv", folder = c("data", "results"), file = 1:2)
#'
#' @export
expand <- function(pattern, ...) {
  vars <- list(...)
  combos <- do.call(expand.grid, vars)

  result <- apply(combos, 1, function(row) {
    res <- pattern
    for (varname in names(vars)) {
      res <- gsub(paste0("\\{", varname, "\\}"), row[[varname]], res)
    }
    res
  })

  return(result)
}


#' Capture and Assign Command-Line Arguments (When using Rscript myscript.R)
#'
#' This function retrieves a specified number of command-line arguments and
#' assigns them to variable names in the global environment.
#'
#' @param num Integer. The number of command-line arguments to capture (1–10).
#' @param arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10
#'   Character strings. The names of variables to which the corresponding
#'   command-line arguments will be assigned.
#'
#' @details
#' The function uses \code{commandArgs(trailingOnly = TRUE)} to obtain
#' command-line arguments passed to the R script. Up to 10 arguments can be
#' captured and assigned. For each argument:
#' \itemize{
#'   \item If \code{num >= k} and at least \code{k} arguments are supplied,
#'   the \code{k}-th command-line argument is assigned to the variable name
#'   provided in \code{argk} within the global environment.
#' }
#'
#' Arguments beyond the number provided by the user or exceeding \code{num}
#' are ignored.
#'
#' @return
#' This function does not return a value. Instead, it assigns variables
#' in the global environment.
#'
#' @examples
#' \dontrun{
#' # Suppose the script is called with:
#' # Rscript myscript.R input.txt output.txt
#'
#' catch_args(2, "infile", "outfile", NA, NA, NA, NA, NA, NA, NA, NA)
#'
#' # After running, two variables will be available in the global environment:
#' # infile  -> "input.txt"
#' # outfile -> "output.txt"
#' }
#'
#' @seealso [commandArgs()]
#'
#' @export
catch_args <- function(num, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10) {
  if (num > 0) {
    args <- commandArgs(trailingOnly = TRUE)

    if (num >= 1 && length(args) >= 1) {
      first <- args[1]
      assign(arg1, first, envir = .GlobalEnv)
    }
    if (num >= 2 && length(args) >= 2) {
      second <- args[2]
      assign(arg2, second, envir = .GlobalEnv)
    }
    if (num >= 3 && length(args) >= 3) {
      third <- args[3]
      assign(arg3, third, envir = .GlobalEnv)
    }
    if (num >= 4 && length(args) >= 4) {
      fourth <- args[4]
      assign(arg4, fourth, envir = .GlobalEnv)
    }
    if (num >= 5 && length(args) >= 5) {
      fifth <- args[5]
      assign(arg5, fifth, envir = .GlobalEnv)
    }
    if (num >= 6 && length(args) >= 6) {
      sixth <- args[6]
      assign(arg6, sixth, envir = .GlobalEnv)
    }
    if (num >= 7 && length(args) >= 7) {
      seventh <- args[7]
      assign(arg7, seventh, envir = .GlobalEnv)
    }
    if (num >= 8 && length(args) >= 8) {
      eighth <- args[8]
      assign(arg8, eighth, envir = .GlobalEnv)
    }
    if (num >= 9 && length(args) >= 9) {
      ninth <- args[9]
      assign(arg9, ninth, envir = .GlobalEnv)
    }
    if (num >= 10 && length(args) >= 10) {
      tenth <- args[10]
      assign(arg10, tenth, envir = .GlobalEnv)
    }
  }
}



# R theme
library(ggplot2)

# mytheme version for publication based on Nature Genetics guidelines

mythemep <- function() {
  list(
    theme_minimal(),
    theme(
      axis.text = element_text(color = "black"),
      axis.ticks = element_line(linewidth = 0.2),
      axis.title = element_text(size=7, vjust = -0.5),
      legend.title = element_text(size = 7, face = "bold"),
      legend.margin = margin(r = 0, l = 0, t = 0, b = 0),
      legend.text = element_text(margin = margin(l = 0)),
      legend.key = element_rect(color=NA, fill=FALSE),
      legend.box.margin = margin(r = 0, l = 5, t = 0, b = 0),
      legend.key.size= unit(4, "mm"),
      # legend.key.spacing.y= unit(-1, "mm"),
      legend.box.spacing = margin(r = 0, l = 0, t = 0, b = 0),
      panel.border = element_rect(linewidth = 0.2, fill = NA),
      panel.background = element_rect(color = "black", fill = NA, linewidth = 0.2),
      panel.grid = element_line(linewidth =0.05, color="grey"),
      panel.grid.minor = element_blank(),
      plot.margin = margin(t = 1, r = 10, b = 1, l = 1),
      plot.title = element_text(face="bold", hjust=0.5),
      strip.text = element_text(size=7, face="bold"),
      strip.background = element_blank(),
      text = element_text(family = "Helvetica", color="black", size=7),
    ),
    guides(color = guide_legend(override.aes = list(shape = 16, size = 3, alpha=0.9)),
            fill  = guide_legend(override.aes = list(shape = 1, size = 2.5)),
            shape = guide_legend(override.aes = list(shape = 1, size = 2.5, color = NA, fill = NULL))
    )
  )
}

# mytheme version for exploration
mytheme <- function() {
  list(
    theme_minimal(),
    theme(
      axis.text = element_text(color = "black"),
      axis.ticks = element_line(linewidth = 0.2),
      axis.title = element_text(vjust = -0.5),
      legend.title = element_text(face = "bold"),
      legend.margin = margin(r = 0, l = 0, t = 0, b = 0),
      legend.text = element_text(margin = margin(l = 0)),
      legend.key = element_rect(color=NA, fill=FALSE),
      legend.box.margin = margin(r = 0, l = 5, t = 0, b = 0),
      legend.key.size= unit(4, "mm"),
      # legend.key.spacing.y= unit(-1, "mm"),
      legend.box.spacing = margin(r = 0, l = 0, t = 0, b = 0),
      panel.border = element_rect(linewidth = 0.2, fill = NA),
      panel.background = element_rect(color = "black", fill = NA, linewidth = 0.2),
      panel.grid = element_line(linewidth =0.05, color="grey"),
      panel.grid.minor = element_blank(),
      plot.margin = margin(t = 10, r = 10, b = 10, l = 10),
      plot.title = element_text(face="bold", hjust=0.5),
      strip.text = element_text( face="bold"),
      strip.background = element_blank(),
      text = element_text(family = "Helvetica", color="black"),
    ),
    guides(color = guide_legend(override.aes = list(shape = 16, size = 3, alpha=0.9)),
            fill  = guide_legend(override.aes = list(shape = 1, size = 2.5)),
            shape = guide_legend(override.aes = list(shape = 1, size = 2.5, color = NA, fill = NULL))
    )
  )
}

# Function to display sample size in a ggplot
n_fun <- function(x, y){
  print("USAGE: stat_summary(fun.data = n_fun, geom = \"text\", fun.args = list(y=200), vjust=0.5, size=6*0.35)")
  return(data.frame(y = y, label = paste0("n = ",length(x))))
}

# Cheatsheet how to save a ggplot
ggsaveinfo <- function(){
  print("ggsave(filename,  dpi=500, width = 45, height = 45,  units = \"mm\")")}
