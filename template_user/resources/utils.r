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

# #' Load Snakemake config YAML as a list
# #'
# #' @param config_file Optional path to config.yml file. If NULL, must provide utils_file_path.
# #' @param utils_file_path Path to the utils.R file (used to find config.yml relative to it).
# #' @return A named list parsed from YAML config file.
# load_config <- function(config_file = NULL, utils_file_path = NULL) {
#   if (is.null(config_file)) {
#     if (is.null(utils_file_path)) {
#       stop("Must provide utils_file_path if config_file is NULL")
#     }
#     d <- dirname(normalizePath(utils_file_path))
#     od <- file.path(d, "snakemake")
#     config_file <- file.path(od, "config.yml")
#   }

#   config <- yaml::read_yaml(config_file)
#   return(config)
# }

#' Load Snakemake config YAML as a list
#'
#' @param config_file Optional path to config.yml file. If NULL, must provide utils_file_path.
#' @param utils_file_path Path to the utils.R file (used to find config.yml relative to it).
#' @return A named list parsed from YAML config file.
load_config <- function(config_file = NULL, utils_file_path = NULL) {
  if (is.null(config_file)) {
    if (is.null(utils_file_path)) {
      stop("Must provide utils_file_path if config_file is NULL")
    }
    d <- dirname(normalizePath(utils_file_path))
    od <- file.path(d, "snakemake")
    config_file <- file.path(od, "config.yml")
  }

  config <- yaml::read_yaml(config_file)
  return(config)
}




#' Load resources YAML as a list
#'
#' @param utils_file_path Path to the utils.R file (used to find resources.yml relative to it).
#' @return A named list parsed from YAML resources file.
load_resources <- function(utils_file_path = NULL) {
  if (is.null(utils_file_path)) {
    stop("Must provide utils_file_path to locate resources.yml")
  }

  d <- dirname(normalizePath(utils_file_path))
  od <- file.path(d, "resources")
  config_file <- file.path(od, "resources.yml")

  config <- yaml::read_yaml(config_file)
  return(config)
}

#' Get path replacement map for current user
#'
#' Returns a named list of strings to replace in configs for the current user.
#' If the username is not recognized in `resources.yml`, an error is raised.
#' Optionally, the username can be forced to a specific value for mn5 config.
#'
#' @param utils_file_path Path to the utils.R file (used to locate resources.yml).
#' @param mn5_config Logical; if TRUE, force username to "bsc083001".
#' @return Named list of string replacements for absolute paths.
#' @examples
#' \dontrun{
#' get_path_map(utils_file_path = "scripts/utils.R")
#' get_path_map(utils_file_path = "scripts/utils.R", mn5_config = TRUE)
#' }
get_path_map <- function(utils_file_path, mn5_config = FALSE) {
  # Get current username
  username <- Sys.info()[["user"]]
  
  # Override username if mn5_config is TRUE
  if (mn5_config) {
    username <- "bsc083001"
  }

  # Load resources
  resources <- load_resources(utils_file_path)

  # Check if username exists in path_map
  if (!(username %in% names(resources$path_map))) {
    stop(paste0("Username '", username, "' not found in resources.yml path_map. ",
                "Add it before proceeding."))
  }

  # Return the path mapping for the user
  return(resources$path_map[[username]])
}


#' Recursively replace substrings in strings within a nested list
#'
#' @param d A nested list or atomic value to perform replacements in.
#' @param m Named list of substrings to replace (names are old substrings, values are replacements).
#' @return The input structure with all applicable string replacements applied.
replace_str_dict <- function(d, m) {
  if (is.list(d)) {
    if (!is.null(names(d))) {
      for (name in names(d)) {
        d[[name]] <- replace_str_dict(d[[name]], m)
      }
      return(d)
    } else {
      return(lapply(d, function(x) replace_str_dict(x, m)))
    }
  } else if (is.character(d) && length(d) == 1) {
    for (old in names(m)) {
      new <- m[[old]]
      d <- gsub(old, new, d, fixed = TRUE)
    }
    return(d)
  } else {
    return(d)
  }
}


#' Load absolute-path config by replacing relative paths based on user
#'
#' @param utils_file_path Path to the utils.R file (used for config and resources locating).
#' @param mn5_config Logical; if TRUE, use mn5 user replacement paths.
#' @return Named list config with relative paths replaced by absolute paths when possible.
load_config_abs <- function(utils_file_path, mn5_config=FALSE) {
  config <- load_config(utils_file_path = utils_file_path)
  m <- get_path_map(utils_file_path = utils_file_path, mn5_config = mn5_config)

  if (!identical(m, "unknown")) {
    config <- replace_str_dict(config, m)
  }

  return(config)
}

#' Load project metadata from the path specified in config.yml
#'
#' This function reads a metadata TSV file whose path is defined in the
#' Snakemake configuration (`config.yml`). It uses the `utils_file_path` to 
#' determine the relative location of the config and metadata directories.
#'
#' @param utils_file_path Full path to the R script calling this function (e.g., "scripts/utils.R").
#'        Used to resolve paths relative to the project structure.
#'
#' @return A tibble containing the metadata.
#' @examples
#' load_meta(utils_file_path = "scripts/utils.R")
load_meta <- function(utils_file_path) {
  # Directory of utils.R
  d <- dirname(normalizePath(utils_file_path))
  od <- file.path(d, "snakemake", "map")
  
  # Load config.yml
  config <- load_config(utils_file_path = utils_file_path)
  
  # Compose full metadata file path
  meta_path <- file.path(od, config$lr$fmt_meta)
  print(meta_path)
  
  # Read TSV metadata file
  df <- readr::read_tsv(meta_path)
  
  return(df)
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
