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

library(here)
CONFIG_FILE <- here("resources/config.yml")
RESOURCES_FILE <- here("resources/resources.yml")

#' Load a YAML file
#'
#' @description
#' Reads a YAML file from disk and returns its contents as an R list.
#'
#' @param file Character string or [base::Path]-like object.
#'   Path to a YAML file.
#'
#' @return A named list containing the parsed YAML contents.
#' @examples
#' \dontrun{
#'   cfg <- load_yml("resources/config.yml")
#' }
#' @export
load_yml <- function(file) {
  # ensure input is character
  file <- as.character(file)

  if (!file.exists(file)) {
    stop(sprintf("YAML file not found: %s", file), call. = FALSE)
  }

  yaml::read_yaml(file, readLines.warn = FALSE)
}

#' Load the resources configuration
#'
#' Load the resources configuration from a YAML file or use a pre-loaded list.
#'
#' @param resources str | list | NULL
#'   - str: path to a YAML file
#'   - list: pre-loaded resources list (useful for testing)
#'   - NULL: defaults to RESOURCES_FILE
#'
#' @return list
#'   Parsed resources list
#'
#' @examples
#' load_resources(NULL)
load_resources <- function(resources = NULL) {
  if (is.null(resources)) {
    resources <- RESOURCES_FILE
  }

  if (is.list(resources)) {
    return(resources)
  }

  if (is.character(resources)) {
    return(load_yml(resources))
  }

  stop(sprintf(
    "Resources must be a list, character str (path), or NULL, got %s",
    class(resources)
  ))
}

#' Load the relevant path mappings for the current user
#'
#' @param resources character | list | NULL
#'   Path to a resources.yml file, a pre-loaded list, or NULL to use RESOURCES_FILE.
#' @param username character | NULL
#'   Username to load paths for. If NULL, will use the system user unless mn5_user is TRUE.
#' @param mn5_user logical, default FALSE
#'   If TRUE, force use of the 'mn5_user' paths.
#'
#' @return named list
#'   Mapping of keys (like 'data_dir', 'ref_dir') to absolute paths.
#'
#' @examples
#' \dontrun{
#' load_paths(resources = NULL, username = "alice")
#' load_paths(resources = "resources.yml", mn5_user = TRUE)
#' }
load_paths <- function(resources = NULL, username = NULL, mn5_user = FALSE) {
  # load resources configuration
  resources <- load_resources(resources)

  # determine which user to use
  if (mn5_user) {
    username <- "mn5_user"
  } else if (is.null(username)) {
    username <- Sys.info()[["user"]]
  }

  path_map <- resources$path_map

  if (!(username %in% names(path_map))) {
    stop(sprintf(
      "Username %s not found in resources. Available: %s",
      username,
      paste(names(path_map), collapse = ", ")
    ))
  }

  # normalize all paths
  user_paths <- path_map[[username]]
  user_paths <- lapply(user_paths, function(d) normalizePath(d, mustWork = FALSE))

  return(user_paths)
}

#' Generate a mapping of template keys to absolute paths
#'
#' @param resources list | character | NULL
#'   Path to a resources.yml file, a pre-loaded list, or NULL for default RESOURCES_FILE.
#' @param ... Additional arguments passed to `load_paths()`, e.g., `username`, `mn5_user`.
#'
#' @return Named list
#'   Mapping of placeholder keys (like './{data_dir}') to absolute path strings.
#'
#' @examples
#' # resources <- list(path_map = list(alice = list(data_dir = "/tmp/data")))
#' # get_path_map(resources, username="alice")
get_path_map <- function(resources = NULL, ...) {
  # Load user paths
  paths <- load_paths(resources = resources, ...)

  # Map keys to formatted template keys
  res <- setNames(
    lapply(names(paths), function(k) paths[[k]]),
    vapply(names(paths), fmt_path_map_key, character(1))
  )

  return(res)
}

# Helper: format keys the same way as Python's fmt_path_map_key
fmt_path_map_key <- function(key) {
  paste0("./{", key, "}")
}

#' Load Project Configuration with Absolute Paths
#'
#' This function loads a configuration (`config.yml`) and resources (`resources.yml`)
#' and applies user-specific path mappings. Placeholders in the configuration are
#' replaced by absolute paths from the resources.
#'
#' @param config Character string or list. Path to config.yml file or pre-loaded config list.
#'   If NULL, defaults to CONFIG_FILE.
#' @param resources Character string or list. Path to resources.yml file or pre-loaded resources list.
#'   If NULL, defaults to RESOURCES_FILE.
#' @param ... Additional arguments passed to `get_path_map()` (e.g., username, mn5_user).
#'
#' @return A list representing the fully substituted configuration with absolute paths.
#' @export
load_config <- function(config = NULL, resources = NULL, ...) {

  # --- Load config
  if (is.null(config)) {
    config <- CONFIG_FILE
  }
  if (is.list(config)) {
    config_dict <- config
  } else if (is.character(config)) {
    config_dict <- load_yml(config)
  } else {
    stop(sprintf(
      "Config must be a list, character str (path), or NULL, got %s",
      class(resources)
    ))
  }

  # --- Load path map from resources
  path_map <- get_path_map(resources = resources, ...)

  # --- Apply replacements & resolve symlinks
  config_dict <- replace_str_dict(config_dict, path_map)
  config_dict <- resolve_config_symlinks(config_dict)

  return(config_dict)
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

#' Generate All Combinations of a Pattern with Variables
#'
#' Creates a character vector by substituting placeholders in a pattern with all
#' combinations of provided variables.
#'
#' @param pattern Character string with placeholders in curly braces, e.g., "{x}", "{y}".
#' @param ... Named arguments, each a vector of values to substitute into the pattern.
#'
#' @return Character vector of strings with placeholders replaced.
#'
#' @examples
#' expand("file_{x}_{y}.txt", x = 1:2, y = c("a", "b"))
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

#' Capture Command-Line Arguments for Rscript
#'
#' Assigns command-line arguments to variables in the global environment.
#'
#' @param num Integer: number of command-line arguments to capture (1–10).
#' @param arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,arg10 Character:
#'   names of variables to assign arguments to.
#'
#' @details
#' Uses \code{commandArgs(trailingOnly = TRUE)}. Only the first \code{num} arguments
#' are assigned to provided variable names; excess arguments are ignored.
#'
#' @return None. Variables are created in the global environment.
#'
#' @examples
#' \dontrun{
#' # Rscript myscript.R input.txt output.txt
#' catch_args(2, "infile", "outfile", NA, NA, NA, NA, NA, NA, NA, NA)
#' # infile  -> "input.txt"
#' # outfile -> "output.txt"
#' }
#'
#' @export
catch_args <- function(num, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10) {
  if (num > 0) {
    args <- commandArgs(trailingOnly = TRUE)
    if (num >= 1 && length(args) >= 1) assign(arg1, args[1], envir = .GlobalEnv)
    if (num >= 2 && length(args) >= 2) assign(arg2, args[2], envir = .GlobalEnv)
    if (num >= 3 && length(args) >= 3) assign(arg3, args[3], envir = .GlobalEnv)
    if (num >= 4 && length(args) >= 4) assign(arg4, args[4], envir = .GlobalEnv)
    if (num >= 5 && length(args) >= 5) assign(arg5, args[5], envir = .GlobalEnv)
    if (num >= 6 && length(args) >= 6) assign(arg6, args[6], envir = .GlobalEnv)
    if (num >= 7 && length(args) >= 7) assign(arg7, args[7], envir = .GlobalEnv)
    if (num >= 8 && length(args) >= 8) assign(arg8, args[8], envir = .GlobalEnv)
    if (num >= 9 && length(args) >= 9) assign(arg9, args[9], envir = .GlobalEnv)
    if (num >= 10 && length(args) >= 10) assign(arg10, args[10], envir = .GlobalEnv)
  }
}

#' Publication-Quality ggplot2 Theme (Nature Genetics Style)
#'
#' Returns a list of theme modifications and legend guides for consistent
#' publication figures.
#'
#' @return List suitable for addition to a ggplot object.
#'
#' @examples
#' ggplot(mtcars, aes(mpg, wt, color = factor(cyl))) +
#'   geom_point() +
#'   mythemep()
#'
#' @export
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
      legend.box.spacing = margin(r = 0, l = 0, t = 0, b = 0),
      panel.border = element_rect(linewidth = 0.2, fill = NA),
      panel.background = element_rect(color = "black", fill = NA, linewidth = 0.2),
      panel.grid = element_line(linewidth =0.05, color="grey"),
      panel.grid.minor = element_blank(),
      plot.margin = margin(t = 1, r = 10, b = 1, l = 1),
      plot.title = element_text(face="bold", hjust=0.5),
      strip.text = element_text(size=7, face="bold"),
      strip.background = element_blank(),
      text = element_text(family = "Helvetica", color="black", size=7)
    ),
    guides(
      color = guide_legend(override.aes = list(shape = 16, size = 3, alpha=0.9)),
      fill  = guide_legend(override.aes = list(shape = 1, size = 2.5)),
      shape = guide_legend(override.aes = list(shape = 1, size = 2.5, color = NA, fill = NULL))
    )
  )
}


#' Exploratory ggplot2 Theme
#'
#' Lightweight theme for data exploration with clear text and minimal decorations.
#'
#' @return List of ggplot2 theme modifications.
#'
#' @examples
#' ggplot(mtcars, aes(mpg, wt)) + geom_point() + mytheme()
#'
#' @export
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
      legend.box.spacing = margin(r = 0, l = 0, t = 0, b = 0),
      panel.border = element_rect(linewidth = 0.2, fill = NA),
      panel.background = element_rect(color = "black", fill = NA, linewidth = 0.2),
      panel.grid = element_line(linewidth =0.05, color="grey"),
      panel.grid.minor = element_blank(),
      plot.margin = margin(t = 10, r = 10, b = 10, l = 10),
      plot.title = element_text(face="bold", hjust=0.5),
      strip.text = element_text(face="bold"),
      strip.background = element_blank(),
      text = element_text(family = "Helvetica", color="black")
    ),
    guides(
      color = guide_legend(override.aes = list(shape = 16, size = 3, alpha=0.9)),
      fill  = guide_legend(override.aes = list(shape = 1, size = 2.5)),
      shape = guide_legend(override.aes = list(shape = 1, size = 2.5, color = NA, fill = NULL))
    )
  )
}


#' Display Sample Size as ggplot Annotation
#'
#' Returns a data frame with sample size label for use with stat_summary().
#'
#' @param x Numeric vector for which sample size is calculated.
#' @param y Numeric value giving vertical placement.
#'
#' @return Data frame with columns \code{y} and \code{label}.
#'
#' @examples
#' ggplot(mtcars, aes(mpg, wt)) +
#'   stat_summary(fun.data = n_fun, geom = "text", fun.args = list(y = 200), vjust = 0.5, size = 6*0.35)
#'
#' @export
n_fun <- function(x, y){
  print("USAGE: stat_summary(fun.data = n_fun, geom = \"text\", fun.args = list(y=200), vjust=0.5, size=6*0.35)")
  return(data.frame(y = y, label = paste0("n = ",length(x))))
}


#' Reminder for Saving ggplots
#'
#' Prints standard usage for saving a ggplot with specific DPI and dimensions.
#'
#' @return None
#'
#' @examples
#' ggsaveinfo()
#'
#' @export
ggsaveinfo <- function(){
  print("ggsave(filename,  dpi=500, width = 45, height = 45,  units = \"mm\")")
}
