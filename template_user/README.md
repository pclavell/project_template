## RULES

* Work on your own branch, but try to merge into main at least 1x / week
* Maintain the `.gitignore` well! Ie, should be able to run `git add -A` without accidentally pushing large / unnecessary files
* When updating config, only update `processing/config.yml`. The mn5 version of it is generated automatically.
* To commit your work and push, run:
```bash
python resources/save_mn5_config.py; git add -A; git commit -m "update"; git push origin main
```

## Repository content
* [metadata](https://github.com/pclavell/project_template/tree/main/metadata): Instructions / code for picking relevant datasets and getting / formatting their metadata. Final metadata tables.
* [resources](https://github.com/pclavell/project_template/tree/main/resources): R and Python files with importable functions. YML file with project settings and global variables (color schemes, paths for different systems, etc.)
* [processing](https://github.com/pclavell/project_template/tree/main/processing): Processing pipelines and code to perform cluster computation.
  - [`config.yml`](https://github.com/pclavell/project_template/tree/main/resources/config.yml): Defines all the locations of the files used throughout this repo (including, notably, in the [analysis](https://github.com/pclavell/project_template/tree/main/analysis/) folder as well).
  - [`config_mn5.yml`](https://github.com/pclavell/project_template/tree/main/resources/config_mn5.yml): Absolute paths to files on MN5. Mirrors `config.yml`. Created automatically by GitHub push companion script
  <!-- todo, link script -->
  - [`resources.yml`](https://github.com/pclavell/project_template/tree/main/resources/resources.yml): Global project settings, including file paths for different systems, users, and colors for plotting.
* [analysis](https://github.com/pclavell/project_template/tree/main/analysis): Analysis, data wrangling, plotting, and statistical testing.



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


```bash
xargs -n 1 curl -O -L -u YJW4VXGF:zg2yps6nectvogfc < files.txt
``` -->
