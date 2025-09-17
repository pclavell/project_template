# Melé lab project template directory


## Installation instructions

* **Repository cloning**: Go to the dir where you want the project to sit (probably in Projects) and run:

```bash
git clone https://github.com/pclavell/project_template.git
```

* **Settings personalization**:
  1) Determine your local and MN5 usernames. To do so, run `echo $USER` in each system
  2) Open [`template_user/resources/resources.yml`](template_user/resources/resources.yml) and fill out the fields under `setup_settings` according to the example and instructions indicated in the same file.
  3) Run the [setup script](setup_project.py). It will automatically create project subdirs for each user, populate [`template_user/resources.yml`](template_user/resources/resources.yml) with local and mn5 paths for each user, and to disconnect the parent repo (cleaning step because you will no longer need it).

```bash
cd project_template
python setup_project.py
cd ../
```
* **Building the GitHub repository**
  1) Create a [new GitHub repository](https://github.com/new) on GitHub to get the repo link used      below
  2) In *each* of the user directories (ie template_user), run:

```bash
cd <project_name>/<username>
git init
git remote add origin git@github.com:<GitHub username>/<GitHub repo name>.git
git add -A
git commit -m "define dir structure"
```
  iii) After running the setup script and GitHub initialization, copy the whole directory to each system you need it on. For example, if initialized on MN5 and copying to local, run:
```bash
cd ../.. # go to parent dir where project sits
scp -r <bsc_username>@transfer1.bsc.es:/gpfs/projects/bsc83/Projects/ <project_name>
```


## Adding / updating users information

If you add a new user to the project, please see [this section](template_user/#adding--updating-users-information).

<!-- ## Other rules
* Do not remove [template_user](template_user), as it will be used to generate new users if need be -->

## Developer to-do

* Python plotting theme
* [Check for broken links in READMEs](https://github.com/tcort/github-action-markdown-link-check)
* Add snakemake and python versions to template_user/requirements.txt and see if we can automate their installation
* Fix snakemake launch script to work with any combination of wildcards
* Add Nextflow template
