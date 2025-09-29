# Testing suite

## General information

* If you add a change in behavior to the template, to check if it will break functionality that holds the project together, we provide these tests

* Changes to test must be under [template_user](../template_user/). In other words, once you initialize your project, you won't be able to use these tests without adding the corresponding code you want to test to this directory

## Python tests

* Requires installation of [pytest](https://docs.pytest.org/en/stable/)

* To get imports to work, must run from parent directory, [project_template](../../project_template/)

* To test, run the following:
```bash
python -m pytest -v -s
```

## R tests

* Requires installation of [testthat](https://testthat.r-lib.org/)


* To test, run the following from the CLI
```bash
R -e "testthat::test_dir('template_user/tests/testthat')"
```

* Or, from within R:
```R
library(testthat)
testthat::test_dir("template_user/tests/testthat/")
```
