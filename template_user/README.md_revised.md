## RULES

* Work on your own branch, but try to merge into main at least 1x / week
* Maintain the [`.gitignore`](.gitignore) well! Ie, should be able to run `git add -A` without accidentally pushing large / unnecessary files
* When adding files to the config, only update [`resources/config.yml`](resources/config.yml). The mn5 version of it is generated automatically.
* To commit your work and push, run:
```bash
python resources/save_mn5_config.py; git add -A; git commit -m "update"; git push origin main
```

## Repository content
* [metadata](metadata): Instructions / code for picking relevant datasets and getting / formatting their [metadata](metadata). Final [metadata](metadata) tables.
* [resources](resources): R and Python files with importable functions. YML file with project settings and global variables (color schemes, paths for different systems, etc.)
* [processing](processing): Processing pipelines and code to perform cluster computation.
* [analysis](analysis): Analysis, data wrangling, plotting, and statistical testing.

## Other files details
* [requirements.txt](requirements.txt): Python libraries needed to run the code in this repo.

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
