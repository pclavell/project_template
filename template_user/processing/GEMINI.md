# Snakemake Guidelines

This document defines the conventions for building and executing Snakemake workflows within the `processing/` directory.

## 1. Modular Structure
* **Workflow Entry:** The main `Snakefile` for a specific analysis **must** be located in its own subdirectory at the path `processing/*/Snakefile`. This ensures that all analytical logic is contained within a predictable entry point.
* **Rule Modules:** Global or reusable rule definitions must be stored in `processing/rules/` as `.smk` files.
* **Automatic Inclusion:** Always anchor `rules_dir` using `pyprojroot.here` so rules can be loaded consistently whether running from a task subdirectory, from `processing/`, or from the repository root:
  ```python
  from pyprojroot.here import here

  rules_dir = f'{here()}/processing/rules/'
  for f in sorted(os.listdir(rules_dir)):
      if f.endswith('.smk'):
          include: f'{rules_dir}{f}'
  ```

## 2. Dynamic Path Resolution
* **No Relative Paths:** Never hardcode relative paths (e.g., `../../data/file.txt`) in [`rules`](rules).
* **Environment-Agnostic Config:** Use `load_config()` from `resources.utils` to resolve path placeholders into absolute strings based on the current user's system (local vs. MN5).
* **Config Management:**
  * All new configuration keys **must** be added to `resources/config.yml`.
  * **Never** modify or generate `resources/config_mn5.yml` directly (do NOT run `save_mn5_config()`), as a GitHub Action automatically generates and updates it on every push.
  * Use shorthand paths (e.g., `./{data_dir}/`, `./{proj_data_dir}/`) for all file paths. This allows the boilerplate logic to correctly resolve paths regardless of whether the workflow is running on a local machine or the MN5 cluster.
  ```python
  from resources.utils import load_config
  config = load_config() # all paths like './{proj_data_dir}/...' are now absolute
  ```
* **Rule I/O:** Always reference the `config` object for inputs and outputs.
* **Wildcard Injection:** When filling in variables/wildcards into paths loaded from `config.yml`, **always** use Snakemake's built-in `expand()` function. Do **not** use Python's `.format()` or `.replace()` methods, as `expand()` is designed to integrate cleanly with Snakemake's DAG evaluation and handles lists natively.
```python
# GOOD:
input: expand(config['data']['my_file'], sample=SAMPLES)

# BAD:
input: [config['data']['my_file'].format(sample=s) for s in SAMPLES]
```
* **Single Path Resolution from Lists:** Since `expand()` always returns a list (even if it resolves to a single file path), index the list with `[0]` directly inside the `input:` or lambda definition if the rule/tool expects a single file string rather than a list of paths.
```python
# GOOD:
input:
    my_file = lambda wc: expand(config['data']['my_file'], sample=wc.sample)[0]
```
* **Lambda Formatting:** When using lambda functions in rules (e.g., for `input:` or `params:`), always use the abbreviation `wc` instead of `wildcards` to maintain concise and readable code.
```python
# GOOD:
params: prefix = lambda wc, output: ...

# BAD:
params: prefix = lambda wildcards, output: ...
```
* **Full File Paths:** Always store the **full file path** (including all extensions/suffixes) in `resources/config.yml`. Avoid constructing paths using string concatenation within Snakefiles.
* **Dynamic Prefixes:** For tools that require an output prefix (like PLINK or samtools), derive the prefix dynamically from the output path in the `params:` block using `lambda` functions and the utility functions in `resources.smk_utils` (e.g., `get_odir_and_pref_from_fname`).
```python
params:
    prefix = lambda wc, output: get_odir_and_pref_from_fname(output.vcf, sep='.')
```
```python
input: bam = config['data']['sample_bam']
output: vcf = config['results']['sample_vcf']
```

## 3. Rule Implementation Style
* **Wildcard Constraints:** Always define global `wildcard_constraints:` at the top of your `Snakefile` wherever possible. This prevents ambiguous rule matching and provides a layer of validation for variables like sample IDs, tissues, or numeric levels before DAG evaluation begins.
```python
wildcard_constraints:
    organ="[a-zA-Z0-9_]+",
    level="\d+",
    strategy="intersection|zero_fill"
```
* **Base Rules:** Define general [`rules`](rules) in `.smk` files using wildcards (e.g., `{sample}`).
* **Rule Inheritance:** In your specific `Snakefile`, use the `use rule ... as ... with:` syntax to specialize base [`rules`](rules) for your metadata.
* **Resource Management:** Every rule **must** specify `runtime` (in minutes), `threads`, and `nodes` within the `resources:` block. This is mandatory for the Snakemake scheduler to correctly interface with the cluster's Slurm manager and allocate the appropriate hardware.
  ```python
  resources:
      runtime = 60,
      threads = 1,
      nodes = 1
  ```
  * **Single-Node Mandate (`nodes = 1`):** Non-MPI rules (Python, R, PLINK2, samtools, bcftools, minimap2, etc.) **must always set `nodes = 1`**. Never request `nodes > 1` to get more memory. On MareNostrum 5, multi-node requests automatically trigger exclusive node mode (112 cores per node), causing jobs to sit in the queue indefinitely under `QOSGrpNodeLimit` and burning excessive core-hour budget. Furthermore, non-distributed software cannot access RAM across nodes over the network.
  * **Memory Scaling via `threads`:** On MN5 standard GPP nodes, Slurm assigns memory proportionally to cores (~2 GB of RAM per core). To allocate more memory for a rule, **keep `nodes = 1` and scale `threads`** (which maps to `-c` / `--cpus-per-task`):
    * Small / summary jobs (~8–16 GB RAM): `threads = 4` to `8`
    * Medium jobs (~32 GB RAM): `threads = 16`
    * Large memory jobs (~64 GB RAM): `threads = 32`
    * Very large memory jobs (~128 GB RAM): `threads = 64`
    * Full standard node (~220 GB RAM): `threads = 112`
    * Jobs requiring >224 GB RAM: keep `nodes = 1` and request high-memory nodes via `#SBATCH --constraint=highmem` (only 216 highmem nodes exist on MN5, so use sparingly).
* **Embedded Python Logic:** For small, task-specific data wrangling or analysis steps within a pipeline (e.g., parsing a specific file format, running a basic sklearn calculation), prefer embedding the Python code directly inside the rule using the `run:` directive. This reduces file clutter and keeps the pipeline logic centralized. Only create external scripts in `resources/` if the logic is highly complex, reusable across multiple entirely different snakefiles, or requires extensive unit testing.
```python
rule compute_similarity:
    input: mat1="mat1.csv", mat2="mat2.csv"
    output: out="sim.csv"
    run:
        import pandas as pd
        # ... logic ...
        df.to_csv(output.out)
```
  * Use `module load <tool>` within shell blocks to ensure compatibility with the cluster environment.
  * When activating a conda environment from within a `shell` block, **always** include the `conda: 'base'` directive in the rule. This ensures that the shell is correctly initialized for conda commands on the cluster.
    ```python
    rule my_rule:
        conda: 'base'
        shell:
            """
            conda activate /path/to/env
            my_tool --args
            """
    ```

<!-- ## 4. Metadata Handling
*   **Centralized Metadata:** Load your metadata TSV using the path from `config['metadata']`.
*   **Utility Functions:** Use `resources.smk_utils.get_value_from_df` for complex input mapping (e.g., replicates to merged samples). -->


## 5. Logging & Debugging
* **Standardized Logs:** Use the `wildcard_log_path` utility.
* **Log Location:** All logs should be written to a local `smk_logs/` directory.

## 6. Project-Wide Rule Uniqueness
* **Unique Naming:** All [`rules`](rules) must have unique names across the **entire project**. This ensures that multiple Snakefiles can be chained together into a "master" workflow without naming conflicts.
* **Base Rule Specialization:** When specializing a base rule from `processing/rules/` in a task-specific `Snakefile`, always use the `use rule ... as <prefix>_<original_name>` syntax.
* **Local Rules:** Single-purpose [`rules`](rules) defined directly within a specific `Snakefile` are permitted for non-reusable logic. However, they **must** also be prefixed with the task name (e.g., `rule map_custom_cleanup:`) to maintain project-wide uniqueness.
* **Prefix Choice:** Use a short, descriptive prefix related to the directory or task (e.g., `map`, `filt`, `quant`).

**Example:**
```python
# In processing/rules/example.smk:
rule wget:
    ...

# In processing/mapping/Snakefile:
use rule wget as map_wget with:
    ...

# In processing/filtering/Snakefile:
use rule wget as filt_wget with:
    ...
```

## 7. Formatting
* **Naming:** Rule names must be `snake_case`.
* **Comments:** Use the lowercase narrative style (from the root `GEMINI.md`) to explain the data flow within [`rules`](rules).
* **Strings:** Use single quotes `'` for strings and double quotes `"` only for docstrings or strings containing single quotes.

## 8. Snakefile Template
Every `processing/*/Snakefile` must begin with the standard ASCII art cat header and the standard import block to ensure consistency and correct path resolution.

**Required Template:**
```python
################################## README BEFORE USAGE ##################################

# This is an snakemake example, please do the following:

#  1) Adapt the CONFIGURATION section where you see this symbols: !!! (details below)
#  2) Adapt the FIRST RULE depending on your data (detail below)
#  3) Add all the rules you want =)

                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############





######################################## SETTINGS ########################################
# import packages
import pandas as pd
import sys
import os
from pyprojroot.here import here

sys.path = [str(here())]+sys.path

from resources.utils import *
from resources.smk_utils import *

# load project configuration
config = load_config()

# include global rules
rules_dir = f'{here()}/processing/rules/'
for f in sorted(os.listdir(rules_dir)):
    if f.endswith('.smk'):
        include: f'{rules_dir}{f}'
```
