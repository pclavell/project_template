# test_utils.R
library(testthat)
library(yaml)
library(here)
setwd(here())
source(here("resources", "utils.r"))

############# load_yml
test_that("load_yml reads a valid YAML file", {
  # create a temporary YAML file
  tmp <- tempfile(fileext = ".yml")
  yaml_content <- list(foo = "bar", num = 42)

  # write YAML to file
  writeLines(as.yaml(yaml_content), tmp)

  # call the function
  result <- load_yml(tmp)

  # check that it parsed correctly
  expect_equal(result, yaml_content)
})

test_that("load_yml errors if file is missing", {
  # create a non-existent path
  missing_file <- tempfile(fileext = ".yml")

  # should throw an error
  expect_error(
    load_yml(missing_file),
    regexp = "YAML file not found"
  )
})

################### load_resources
test_that("resources input as a list returns same object", {
  data <- list(foo = "bar")
  result <- load_resources(data)
  expect_identical(result, data)  # should return the same object
})

test_that("resources input as a YAML file path", {
  tmp_file <- tempfile(fileext = ".yml")
  writeLines("foo: bar", tmp_file)

  result <- load_resources(tmp_file)
  expect_equal(result, list(foo = "bar"))
})

test_that("resources=NULL uses RESOURCES_FILE", {
  # Create a temporary fake RESOURCES_FILE
  tmp_file <- tempfile(fileext = ".yml")
  writeLines("hello: world", tmp_file)

  # Save old RESOURCES_FILE from the environment of load_resources
  old_res <- get("RESOURCES_FILE", envir = environment(load_resources))

  # Temporarily override RESOURCES_FILE in the function's environment
  assign("RESOURCES_FILE", tmp_file, envir = environment(load_resources))

  # Call function
  result <- load_resources(NULL)
  expect_equal(result, list(hello = "world"))

  # Restore original RESOURCES_FILE
  assign("RESOURCES_FILE", old_res, envir = environment(load_resources))
})


test_that("resources invalid type raises error", {
  expect_error(load_resources(123), "Resources must be a list, character")
})

################### load_paths
library(testthat)
library(here)

# Helper: fake resources for tests
make_fake_resources <- function(tmp_path, usernames = c("alice", "bob", "mn5_user")) {
  path_map <- lapply(usernames, function(u) {
    list(
      data_dir = file.path(tmp_path, u, "data"),
      ref_dir  = file.path(tmp_path, u, "ref")
    )
  })
  names(path_map) <- usernames
  list(path_map = path_map)
}

test_that("load_paths with explicit username", {
  tmp_path <- tempdir()
  resources <- make_fake_resources(tmp_path, c("alice"))
  result <- load_paths(resources = resources, username = "alice")

  # print('hload_paths with explicit usernameere3'); browser()
  expect_setequal(names(result), c("data_dir", "ref_dir"))
  # paths are absolute
  for (p in result) {
    expect_true(file.path(p) == normalizePath(p, mustWork = FALSE))
  }
})

test_that("load_paths without username uses system user", {
  tmp_path <- tempdir()
  fake_user <- "bob"
  resources <- make_fake_resources(tmp_path, c("alice", fake_user))

  # temporarily override Sys.info()[["user"]]
  old_user <- Sys.info()[["user"]]
  assign("Sys.info", function() list(user = fake_user), envir = .GlobalEnv)

  result <- load_paths(resources = resources)
  # print('load_paths without username uses system user'); browser()

  expect_setequal(names(result), c("data_dir", "ref_dir"))
  for (p in result) {
    expect_true(grepl(paste0("/", fake_user, "/"), p))
  }

  # restore original Sys.info
  assign("Sys.info", base::Sys.info, envir = .GlobalEnv)
})

test_that("load_paths mn5_user forces mn5_user paths", {
  tmp_path <- tempdir()
  resources <- make_fake_resources(tmp_path, c("alice", "mn5_user"))
  result <- load_paths(resources = resources, mn5_user = TRUE)

  # print('load_paths mn5_user forces mn5_user paths'); browser()

  expect_setequal(names(result), c("data_dir", "ref_dir"))
  for (p in result) {
    expect_true(grepl("/mn5_user/", p))
  }
})

test_that("load_paths raises error if username not found", {
  tmp_path <- tempdir()
  resources <- make_fake_resources(tmp_path, c("alice"))
  # print('load_paths raises error if username not found'); browser()

  expect_error(
    load_paths(resources = resources, username = "bob"),
    "Username bob not found in resources"
  )
})

################### get_path_map

test_that("get_path_map formats keys correctly", {
  # Fake resources list
  tmp_dir <- tempdir()
  resources <- list(
    path_map = list(
      alice = list(
        data_dir = file.path(tmp_dir, "data"),
        ref_dir = file.path(tmp_dir, "ref")
      )
    )
  )

  result <- get_path_map(resources = resources, username = "alice")

  expected_keys <- c("./{data_dir}", "./{ref_dir}")
  # print('get_path_map formats keys correctly'); browser()

  expect_setequal(names(result), expected_keys)
})

test_that("get_path_map returns expected values", {
  # Monkeypatch load_paths by defining a local function
  fake_load_paths <- function(resources = NULL, ...) {
    list(data_dir = "/test/data")
  }

  # Temporarily override load_paths
  old_load_paths <- load_paths
  assign("load_paths", fake_load_paths, envir = environment(get_path_map))

  # print('get_path_map returns expected values'); browser()

  result <- get_path_map(resources = NULL, username = "alice")
  expect_equal(result, list("./{data_dir}" = "/test/data"))

  # Restore original load_paths
  assign("load_paths", old_load_paths, envir = environment(get_path_map))
})
