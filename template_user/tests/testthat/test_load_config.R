# test_load_config.R
library(testthat)
library(yaml)
library(here)
setwd(here())
source(here("resources", "utils.r"))

# -------------------------
# Fixtures
# -------------------------
fake_resources <- function() {
  list(
    path_map = list(
      alice = list(
        data_dir = normalizePath("/test/data", mustWork = FALSE),
        ref_dir  = normalizePath("/test/ref", mustWork = FALSE)
      )
    )
  )
}

is_absolute <- function(path) {
  path <- as.character(path)
  if (.Platform$OS.type == "windows") {
    grepl("^[A-Za-z]:\\\\", path)  # C:\foo
  } else {
    startsWith(path, "/")           # /foo
  }
}

fake_config <- function(tmp_dir) {
  config_dict <- list(
    data_path = "./{data_dir}/file.txt",
    nested    = list(ref_path = "./{ref_dir}/ref.fasta")
  )
  config_file <- file.path(tmp_dir, "config.yml")
  yaml::write_yaml(config_dict, config_file)
  list(config_dict = config_dict, config_file = config_file)
}

# -------------------------
# Tests
# -------------------------
test_that("load_config with pre-loaded config list", {

  config_dict <- list(file = "./{data_dir}/myfile")
  out <- load_config(config = config_dict, resources = fake_resources(), username = "alice")

  # print("test_load_config_with_dict"); browser()


  expect_equal(out$file, file.path(fake_resources()$path_map$alice$data_dir, "myfile"))
})

test_that("load_config with config file path", {
  tmp_dir <- tempdir()
  cfg <- fake_config(tmp_dir)

  out <- load_config(config = cfg$config_file, resources = fake_resources(), username = "alice")

  # print("test_load_config_with_file"); browser()

  expect_equal(out$data_path, file.path(fake_resources()$path_map$alice$data_dir, "file.txt"))
  expect_equal(out$nested$ref_path, file.path(fake_resources()$path_map$alice$ref_dir, "ref.fasta"))
})

test_that("load_config with nested replacement", {

  config_dict <- list(level1 = list(level2 = list(file = "./{data_dir}/data.txt")))
  out <- load_config(config = config_dict, resources = fake_resources(), username = "alice")
  expected <- file.path(fake_resources()$path_map$alice$data_dir, "data.txt")
  # print("test_load_config_nested_replacement"); browser()

  expect_equal(out$level1$level2$file, expected)
})

test_that("load_config resolves relative paths to absolute", {
  
  # Create a dummy file in a temp dir under template_user
  tmp_dir <- file.path(here(), "temp_test_dir")
  dir.create(tmp_dir, showWarnings = FALSE)
  dummy_file <- file.path(tmp_dir, "dummy.txt")
  writeLines("hello", dummy_file)

  # Ensure cleanup happens at the end
  on.exit({
    if (file.exists(dummy_file)) file.remove(dummy_file)
    if (dir.exists(tmp_dir)) unlink(tmp_dir, recursive = TRUE)
  }, add = TRUE)

  # Provide relative path in config
  config_dict <- list(rel = file.path("temp_test_dir", "dummy.txt"))

  out <- load_config(config = config_dict, resources = fake_resources(), username = "alice")
  # print("test_load_config_absolute_paths"); browser()

  # Check that the path is now absolute and points to the same file
  expect_true(normalizePath(out$rel) == normalizePath(dummy_file))
})


test_that("load_config raises error for invalid types", {
  # print("test_load_config_invalid_types"); browser()

  expect_error(load_config(config = 123, resources = list()), "must be a list")
  expect_error(load_config(config = list(), resources = 123), "must be a list")
})

test_that("load_config forwards kwargs to get_path_map", {

  config_dict <- list(file = "./{data_dir}/myfile")
  out <- load_config(config = config_dict, resources = fake_resources(), username = "alice")
  expected <- file.path(fake_resources()$path_map$alice$data_dir, "myfile")
  # print("test_load_config_kwargs_forwarding"); browser()


  expect_equal(out$file, expected)
})

test_that("load_config uses default CONFIG_FILE and RESOURCES_FILE", {

  tmp_dir <- tempdir()
  fake_config_file <- file.path(tmp_dir, "config.yml")
  fake_resources_file <- file.path(tmp_dir, "resources.yml")

  config_dict <- list(file = "./{data_dir}/myfile")
  resources_dict <- list(
    path_map = list(
      alice  = list(data_dir = "/test/data"),
      junior = list(data_dir = "/test/junior/data")
    )
  )

  # Write fake files
  yaml::write_yaml(config_dict, fake_config_file)
  yaml::write_yaml(resources_dict, fake_resources_file)

  # Temporarily override global defaults
  old_config <- CONFIG_FILE
  old_resources <- RESOURCES_FILE
  CONFIG_FILE <<- fake_config_file
  RESOURCES_FILE <<- fake_resources_file

  out <- load_config(username = "junior")
  # print("test_load_config_defaults"); browser()

  expect_equal(out$file, "/test/junior/data/myfile")

  # Restore
  CONFIG_FILE <<- old_config
  RESOURCES_FILE <<- old_resources
})
