## Data processing

Most data processing tasks that were run in parallel and / or on the cluster are here.

## Organization

In the parent directory, there are a few shared resources
* [rules](processing/rules): Rule definitions for workflow manager rules that are repeatedly used throughout the subfolder tasks.
* Each subfolder roughly contains a distinct data processing task

* For Snakemake workflows, in each subdirectory, the important files which are usually there are as follows:
  * `Snakefile`: Used to run the data processing / analysis workflow
  * `snakefile_dev.ipynb` (and other `*dev.ipynb`): Jupyter notebooks used to debug input / output Snakemake files or other tasks that are run during `Snakefile` execution.
  * Oftentimes there are additional `*.txt`, `*.md`, or `*.tsv` files that help outline additional input / output information (especially related to external dataset use) or other information / code used to run the `Snakefile`.

## Subfolder descriptions

Details for each data processing task subfolder listed here.

<!-- * [template_snakemake] -->
* [template_snakemake](processing/template_snakemake): Template Snakemake workflow with header that works with the structure of this repository.











## Snakemake calls

* Run Snakemake from within the relevant processing folder ie [processing/template_snakemake/](processing/template_snakemake)

* You can use the script `template_snakemake/submit_smk.sh` to easily lauch Snakemake or run the dryrun. We recommend always at least using `--dryrun` first.

```bash
submit_smk.sh
       -run: to start an execution
       -rerun: for failed runs that blocked the dir, runs unlock
       -dryrun: tests pipeline structure
       -graph: makes DAG png
Usage: bash submit_smk.sh {run|rerun|dryrun}
```

* Common Snakemake calls are also reproduced below:

```bash
# normal
conda activate pt_snakemake
snakemake \
  -s Snakefile \
  -j 300 \
  --latency-wait 120 \
  --use-conda \
  --cluster \
    "sbatch \
    --nodes {resources.nodes} \
    -q gp_bscls \
    -A bsc83 \
    -c {resources.threads}  \
    --time=24:00:00" \
    -n


# gpu version
snakemake \
  -s Snakefile \
  -j 100 \
  --latency-wait 120 \
  --use-conda \
  --cluster \
    "sbatch \
    --nodes {resources.nodes} \
    -q acc_bscls \
    -A bsc83 \
    -c {resources.threads}  \
    --time={resources.time}" \
    -n

# debug version
conda activate pt_snakemake
snakemake \
  -s Snakefile \
  -j 100 \
  --latency-wait 120 \
  --use-conda \
  --cluster \
    "sbatch \
    --nodes {resources.nodes} \
    -q gp_debug \
    -A bsc83 \
    -c {resources.threads}  \
    --mail-user=freese@bsc.es \
    --mail-type=START,END,FAIL \
    --time=2:00:00" \
    -n

# non-cluster version
snakemake \
  -s Snakefile \
  -j 100 \
  --latency-wait 120 -n

# plotting version
snakemake --forceall --dag | dot -Tpdf > dag.pdf
```
