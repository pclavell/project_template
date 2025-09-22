# Melé lab project template directory


## Installation instructions

* **Repository cloning**: Go to the dir where you want the project to sit (probably in Projects) and run:
Enter to MareNostrum5 login4 (or your HPC cluster node with internet connection) and move to `cd /gpfs/projects/bsc83/Projects` (if you are in another HPC cluster, choose where you want the project to be located)
```bash
git clone https://github.com/pclavell/project_template.git
```

* **Settings personalization**:
  1) Determine your local and MN5 usernames. To do so, run `echo $USER` in each system
  2) Check your mounting structure. We recommend two dirs, one for `/gpfs/projects/bsc83` (aka projects) and another for `/gpfs/scratch/bsc83` (aka scratch). You can do it as follows (recommend to add it in the `~/.bashrc` as a function, as follows:
```bash
sudo vim ~/.bashrc # you can also use nano or manually edit it with a GUI
```
Copy the following functions within `~/.bashrc` (remember to manually replace `<bscuser>`, `<projects_target_directory>` (where projects will be mounted to) and `<scratch_target_directory>` (where scratch will be mounted to):
```bash
mountprojects(){
echo "-Trying to mount MareNostrum5: Projects"
sshfs -o workaround=rename <bscuser>@transfer1.bsc.es:/gpfs/projects/bsc83/ <projects_target_directory> # replace with your bsc user and your target directory (eg. /home/pclavell/mounts/projects)
echo "MareNostrum5 Projects mounted.
}
mountscratch(){
echo "Trying to mount MareNostrum5: Scratch"
sshfs -o workaround=rename <bscuser>@transfer1.bsc.es:/gpfs/scratch/bsc83/ <scratch_target_directory> # replace with your bsc user and your target directory (eg. /home/pclavell/mounts/scratch)
echo "MareNostrum5 Scratch mounted. 
}
mountall(){
mountprojects()
mountscratch()
}
```
  3) Create `<projects_target_directory>` and `<scratch_target_directory>`:
```bash
cd ~
mkdir <projects_target_directory>
mkdir <scratch_target_directory>
```
  5) Open [`template_user/resources/resources.yml`](template_user/resources/resources.yml) and fill out the fields under `setup_settings` according to the MareNostrum5 structure and the local mounting structure that oyu have just build. Notice that there is an example and instructions indicated in the same `resources.yml` file.
  6) Run the [setup script](setup_project.py). It will automatically:
     * create project subdirs for each user
     * populate [`template_user/resources.yml`](template_user/resources/resources.yml) with local and mn5 paths for each user
     * disconnect the parent repo (project_template) (this is a cleaning step because you will no longer need it).

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

<!-- ## Developer to-do -->

* Python plotting theme
* [Check for broken links in READMEs](https://github.com/tcort/github-action-markdown-link-check)
* Add snakemake and python versions to template_user/requirements.txt and see if we can automate their installation
* Fix snakemake launch script to work with any combination of wildcards
* Add Nextflow template
