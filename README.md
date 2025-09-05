# Melé lab project template directory


## Installation instructions

* Clone this repo

```bash
git clone git@github.com:pclavell/project_template.git
```

* Fill out `setup_settings` according to the example / instructions in [`template_user/resources.yml`](https://github.com/pclavell/project_template/blob/main/user1/resources/resources.yml).
  - As part of this, you must determine your local and MN5 usernames. To do so, run `echo $USER` in the system you choose


* Run the [setup script](https://github.com/pclavell/project_template/blob/main/setup_project.py) to automatically create project subdirs for each user, populate [`template_user/resources.yml`](https://github.com/pclavell/project_template/blob/main/user1/resources/resources.yml) with local and mn5 paths for each user, and to disconnect the parent repo

```bash
cd project_template
python setup_project.py
cd ../
```

## Developer to-do

* Add a template Python notebook in analysis (Fairlie)
* Skeleton READMEs (Fairlie)
* GH auto-run script
  - Update config_mn5.yml
  - Turn all paths in READMEs into links automatically
  - Add and link all subdirs in analysis/ and processing/ to the corresponding README so it's easy to add descriptions
    - also for this add nested links for all .R, .ipynb, and any other relevant things? 
