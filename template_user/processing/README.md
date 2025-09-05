## Data processing

Some computationally-intense data processing was done using Snakemake. Each somewhat-distinct task is in its own folder to make it possible to run several Snakemakes in parallel with one another.

## Organization

In the parent directory, there are a few shared resources
* [`config.yml`](https://github.com/fairliereese/240927_stam_lr/blob/main/processing/config.yml): Defines all the locations of the files used throughout this repo (including, notably, in the [analysis](https://github.com/fairliereese/240927_stam_lr/tree/main/analysis) folder as well).
* [`config_mn5.yml`](https://github.com/fairliereese/240927_stam_lr/blob/main/processing/config_mn5.yml): Absolute paths to files on MN5. Mirrors `config.yml`. Created automatically.
* [common](https://github.com/fairliereese/240927_stam_lr/tree/main/processing/common): Snakemake rule definitions for rules that are repeatedly used throughout the subfolder tasks.

In each subdirectory, the important files which are usually there are as follows:
* `Snakefile`: Used to run the data processing / analysis workflow
* `snakefile_dev.ipynb` (and other `*dev.ipynb`): Jupyter notebooks used to debug input / output Snakemake files or other tasks that are run during `Snakefile` execution.
* Oftentimes there are additional `*.txt`, `*.md`, or `*.tsv` files that help outline additional input / output information (especially related to external dataset use) or other information / code used to run the `Snakefile`.

## Subfolder descriptions

Subfolders that are not listed here don't contain analyses / processing for this manuscript. Folders are mentioned in order of execution, thus some outputs from earlier steps are required for later ones.

* [qc](https://github.com/fairliereese/240927_stam_lr/tree/main/processing/qc): Run QC (Nanoplot and FASTQC). Find adapter sequences, split fastqs on adapters.
* [map](https://github.com/fairliereese/240927_stam_lr/tree/main/processing/map): Map adapter-split fastqs. Filter mappings.


## Snakemake calls

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
    --mail-user=freese@bsc.es \
    --mail-type=START,END,FAIL \
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
    --mail-user=freese@bsc.es \
    --mail-type=START,END,FAIL \
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
