# Working within the project template

## GIT USAGE RULES (IMPORTANT)

* Always create a branch before starting to work by running `git pull origin <branch name>`
* Work on your own branch, but try to merge into main as frequently as you can to avoid diverging too much from main (which will be difficult to solve)
* Maintain the [`.gitignore`](.gitignore) complete! Ie, should be able to run `git add -A` without accidentally pushing large / unnecessary files
* Remember to update config file with important files and directories. You only have to update [resources/config.yml](resources/config.yml). The mn5 version of it is generated automatically
* To commit your work and push, run:
```bash
git add -A; git commit -m "update"; git push origin <branch name>
```
* GitHub actions will automatically try to keep your READMEs linked and up-to-date

## Repository content

* [metadata](metadata): Instructions / code for picking relevant datasets and getting / formatting their metadata. Final metadata tables.
* [resources](resources): R and Python files with importable functions. YML file with project settings and global variables (color schemes, paths for different systems, etc.)
* [processing](processing): Processing pipelines and code to perform cluster computation.
* [analysis](analysis): Analysis, data wrangling, plotting, and statistical testing.
* [tests](tests): Code to test utilities for development purpose.

## Templates

We provide several templates to help familiarize you with how to interface with the environment
* the r template
* the python template
* the dummy snakemake workflow

## Adding / updating users information

If you add a new user to the project, or want to add another system you're working on,
simply edit [resources/resources.yml](resources/resources.yml) from YOUR user directory and run `python resources/add_new_users.py` **from the user's directory** (ie `<project_name>/<user>/`). NOT from the template_user directory

## How do I manage git, mounting, and the cluster? (EFFICIENCY TIP)

This organization framework is designed to automatically detect if you are working in local/mounting or in the cluster. It is very useful to work on the mounting because we can use IDEs and GUIs like Rstudio and VScode. However, in many cases we have mounting lag causing code loss and slowness. With this framework this is partially solved:
- as usual, mount
- instead of working in the mounted dirs, clone your project repository (created during installation) to your local filesystem
If you do it correctly, you will be able to access your code from this local directory and also from the mounted directory. The local directory is where you will work on your code, the mounted directory will be the source of the data. The advantage of this framework is that all paths will work the same. Just remember to keep using git and pull/push.

<!-- ## Other files details
* [`requirements.txt`](requirements.txt): Python libraries needed to run the code in this repo. -->

## GitHub actions

By default, when you push, GitHub actions will automatically update a few files:

* [`resources/config_mn5.yml`](resources/config_mn5.yml): Generated automatically; contains full MN5 paths to each data file. Useful when you need to share like a few files to someone without fully integrating them into the project.
* Add bullet points in READMEs for each subfolder created under [analysis](analysis) and [processing](processing) with descriptions that can be filled in later; helpful to document your project as you go.
* Add links to all GitHub-tracked files in READMEs to make it easier to navigate your repo on the web.

GitHub actions are stored in [.github/workflows/](.github/workflows).


## Filling out .yml files

There are two ymls

Instructions on filling out resources.yml setup_settings

Instructions on that everything else you want to put should go into config.yml

Demonstrate syntax of config.yml w/ path prefixes that will be system-agnoistoc

# TODO

## Structuring your directories

* Recommend using analysis and processing, but technically you can do anything

##
