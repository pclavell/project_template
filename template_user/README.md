## USAGE RULES (IMPORTANT)

* Always create a branch before starting to work by running `git pull origin <branch name>` 
* Work on your own branch, but try to merge into main as frequently as you can to avoid diverging too much from main (which will be difficult to solve)
* Maintain the .gitignore complete! Ie, should be able to run `git add -A` without accidentally pushing large / unnecessary files
* Remember to update config file with important files and directories. You only have to update [resources/config.yml](resources/config.yml). The mn5 version of it is generated automatically
* To commit your work and push, run:
```bash
git add -A; git commit -m "update"; git push origin <branch name>
```
* GitHub actions will automatically try to keep your READMEs linked and up-to-date.

## Repository content
* [metadata](metadata): Instructions / code for picking relevant datasets and getting / formatting their metadata. Final metadata tables.
* [resources](resources): R and Python files with importable functions. YML file with project settings and global variables (color schemes, paths for different systems, etc.)
* [processing](processing): Processing pipelines and code to perform cluster computation.
* [analysis](analysis): Analysis, data wrangling, plotting, and statistical testing.

## Adding / updating users information

If you add a new user to the project, or want to add another system you're working on,
simply edit [resources/resources.yml](resources/resources.yml) and run `python add_new_users.py` from this directory.

<!-- ## Other files details
* [`requirements.txt`](requirements.txt): Python libraries needed to run the code in this repo. -->

## GitHub actions

By default, when you push, GitHub actions will automatically update a few files:

* [`resources/config_mn5.yml`](resources/config_mn5.yml): Generated automatically; contains full MN5 paths to each data file. Useful when you need to share like a few files to someone without fully integrating them into the project.
* Add bullet points in READMEs for each subfolder created under analysis and processing with descriptions that can be filled in later; helpful to document your project as you go.
* Add links to all GitHub-tracked files in READMEs to make it easier to navigate your repo on the web.

GitHub actions are stored in [.github/workflows/](.github/workflows).

<!--
```bash
conda activate pt_snakemake
snakemake \
  -s Snakefile \
  -j 100 \
  --latency-wait 120 \
  --use-conda \
  --cluster \
    "sbatch \
    --nodes {resources.nodes} \
    -q gp_bscls \
    -A bsc83 \
    -c {resources.threads}  \
    --mail-user=freese@bsc.es \
    --mail-type=START,END,FAIL \
    --time=12:00:00" \
    -n

    snakemake --forceall --dag | dot -Tpdf > dag.pdf


snakemake \
  -s Snakefile \
  -j 100 \
  --latency-wait 120 \
  --use-conda \
  -n

```


# ```bash
# xargs -n 1 curl -O -L -u YJW4VXGF:zg2yps6nectvogfc < files.txt
# ``` -->
