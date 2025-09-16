# Melé lab project template directory


## Installation instructions

* Clone this repo

```bash
git clone git@github.com:pclavell/project_template.git
```

* Fill out `setup_settings` according to the example / instructions in [`template_user/resources/resources.yml`](template_user/resources/resources.yml).
  - As part of this, you must determine your local and MN5 usernames. To do so, run `echo $USER` in the system you choose


* Run the [setup script](setup_project.py) to automatically create project subdirs for each user, populate [`template_user/resources.yml`](template_user/resources/resources.yml) with local and mn5 paths for each user, and to disconnect the parent repo

```bash
cd project_template
python setup_project.py
cd ../
```

* Create a new GitHub repository on GitHub. In each of the user directories (ie template_user), run:
```bash
cd <project_name>/<username>
git init
git remote add origin git@github.com:<GitHub username>/<GitHub repo name>.git
git add -A
git commit -m "first commit"
```

## Other rules
* Do not remove [template_user](template_user), as it will be used to generate new users if need be

## Developer to-do

* Add a template Python notebook in analysis
* Add new user script
* Python plotting theme
* [Check for broken links in READMEs](https://github.com/tcort/github-action-markdown-link-check)
* Add snakemake and python versions to requirements.txt and see if we can automate their installation