# Melé lab project template directory

This github contains a framework to set up and mantain a project directory aiming at: 
1) Making easy interuser script reproducibility (with completely automatic path managing)
2) Allowing all users to share the same data directories
3) Easy data sharing thanks to a config file pointing to important files
4) Git tracking allowing all users to work in the same project structure and different computers while tracking the versions

PLEASE read carefully all the instructions in this README and in the [`template_user/README`](template_user/)

## Installation instructions


* **Repository cloning**:
Enter to MareNostrum5 login4 (or your HPC cluster node with internet connection) and move to `cd /gpfs/projects/bsc83/Projects` (if you are in another HPC cluster, choose where you want the project to be located)
```bash
git clone https://github.com/pclavell/project_template.git
```

* **Dependencies**:

You'll need to install at minimum, the following Python packages:
* [pyprojroot](https://anaconda.org/conda-forge/pyprojroot)
* [PyYaml](https://anaconda.org/conda-forge/pyyaml/)

And for R, the following:
* [here](https://cran.r-project.org/web/packages/here/vignettes/here.html)
* [yaml](https://cran.r-project.org/web/packages/yaml/index.html)

* **Settings personalization**:
  1) Determine your local and MN5 usernames. To do so, run `echo $USER` in each system
  2) Open [`template_user/resources/resources.yml`](template_user/resources/resources.yml) and fill out the fields under `setup_settings` according to the MareNostrum5 structure and the local mounting structure that you have just build. Notice that there is an example and instructions indicated in the same `resources.yml` file.
  <!-- TODO : add a link to the section on the mounting and philosophy -->
  3) Run the [setup script](setup_project.py). It will automatically:
     * create project subdirs for each user
     * populate [`template_user/resources.yml`](template_user/resources/resources.yml) with local and mn5 paths for each user.
     * disconnect the parent repo (project_template) (this is a cleaning step because you will no longer need it).

```bash
cd project_template
python setup_project.py
cd ../
```

* **Building the project GitHub repository**
  1) Create a [new GitHub repository](https://github.com/new) on GitHub to get the repo link (used below)
  2) In *each* of the user directories (ie template_user), run:

```bash
cd <project_name>/<username>
git init
git remote add origin git@github.com:<GitHub username>/<GitHub repo name>.git
git add -A
git commit -m "define dir structure"
```
  3) We also recommend creating a local copy of the GitHub project, so you can edit code locally. On your local machine, run

```bash
git clone git@github.com:<GitHub username>/<GitHub repo name>.git
```

  <!-- The following step is *heavily discouraged* and unnecessary. However, users lacking mounting might want to copy the whole directory to each system you need it on. For example, if initialized on MN5 and copying to local, run:
```bash
cd ../.. # go to parent dir where project sits
scp -r <bsc_username>@transfer1.bsc.es:/gpfs/projects/bsc83/Projects/<project_name> <project_name>
``` -->

## Adding / updating users information

If you add a new user to the project, please see [this section](template_user/#adding--updating-users-information).

<!-- # Other recommendations

## Managing mounting

* **Set up local mounting structure**:
Mountings are a way to access remote filesystems (eg. HPC cluster) as they were integrated into our local filesystem (as if they were inside our computer).
We recommend having two directoriess, one for `/gpfs/projects/bsc83` (aka projects) and another for `/gpfs/scratch/bsc83` (aka scratch).
You can do it as follows (recommendation: add it in the `~/.bashrc` as a function):
```bash
sudo vim ~/.bashrc # you can also use nano or manually edit it with a GUI
```
Copy the following functions within `~/.bashrc` (remember to manually replace `<bscuser>`, `<projects_target_directory>` (where projects will be mounted to) and `<scratch_target_directory>` (where scratch will be mounted to):
```bash
mountprojects(){
echo "-Trying to mount MareNostrum5: Projects"
sshfs -o workaround=rename <bscuser>@transfer1.bsc.es:/gpfs/projects/bsc83/ <projects_target_directory> # replace with your bsc user and your target directory (eg. /home/pclavell/mounts/projects)
echo "MareNostrum5 Projects mounted"
}

mountscratch(){
echo "Trying to mount MareNostrum5: Scratch"
sshfs -o workaround=rename <bscuser>@transfer1.bsc.es:/gpfs/scratch/bsc83/ <scratch_target_directory> # replace with your bsc user and your target directory (eg. /home/pclavell/mounts/scratch)
echo "MareNostrum5 Scratch mounted"
}

mountall(){
mountprojects
mountscratch
}
```

Create `<projects_target_directory>` and `<scratch_target_directory>`:

```bash
cd ~
mkdir <projects_target_directory>
mkdir <scratch_target_directory>
```

## Advice for managing git, mounting, and cluster

This organization framework is designed to automatically detect if you are working in local/mounting or in the cluster. It is very useful to work on the mounting because we can use IDEs and GUIs like Rstudio and VScode. However, in many cases we have mounting lag causing code loss and annoying lagginess. With this framework this is partially solved:
- mount as usual (it will be used as source of the data and for outputs)
- instead of working in the mounted dirs, clone your project repository (created during installation) to your local filesystem.

If you do it correctly, you will be able to access your code from this local directory and also from the mounted directory. The local directory is where you will work on your code, the mounted directory will be the source of the data. The advantage of this framework is that all paths will work the same. Just remember to keep using git and pull/push.
![framework_visualization](dev/framework_visualization.jpg) -->
