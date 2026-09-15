# Project Coding Guidelines

This document outlines the coding standards and conventions for this repository. Adherence to these guidelines ensures consistency across the codebase, especially when working across local and cluster (MN5) environments.

**IMPORTANT:** Always read `vault/GEMINI.md` for knowledge base/vault conventions and `processing/GEMINI.md` for Snakemake-specific guidelines before starting work in those directories.

## 0. Critical Style Overrides
These rules take precedence over standard conventions (like PEP8) and are foundational mandates for this codebase.

* **Internal Comments:** NEVER use capital letters or formal punctuation in internal logic comments. Use a lowercase, narrative "pseudocode" style.
  * **BAD:** `# Filter the dataframe by assay type.`
  * **GOOD:** `# filter dataframe by assay type`
* **R Assignment:** Use `=` for assignment, NEVER `<-`.
* **MN5 Config Generation:** NEVER generate or modify `resources/config_mn5.yml` yourself (e.g., NEVER run `save_mn5_config()`). A GitHub Action automatically generates and updates `config_mn5.yml` upon every push.

## 1. General Formatting
* **Indentation:** Use 4 spaces per indentation level.
* **Naming:**
  * `snake_case` for functions and variables (e.g., `load_config`, `user_alias`).
  * `UPPER_CASE` for constants (e.g., `RESOURCES_FILE`, `TEMPLATE_PROJECT_NAME`).
  * `PascalCase` for classes.
* **Strings:** Always use **single quotes (`'`)** for strings when possible. Only use double quotes (`"`) if the string contains a single quote or for docstrings.
* **R Assignment:** Always use the equals sign (`=`) for assignment. **Never** use the arrow operator (`<-`).
* **Headers:** Include the standard ASCII art cat header and a "README BEFORE USAGE" block at the top of shared utility or script files.

```python
################################## README BEFORE USAGE ##################################
# <Brief description of the file's purpose>

                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############
```

## 2. Documentation
* **Docstrings:** Use **NumPy/SciPy style** for all functions.
  * Include sections for `Parameters`, `Returns`, and (if applicable) `Raises`.
  * Ensure every public function has a clear, descriptive summary.

## 3. Path Management
* **Pathlib:** Always use `pathlib.Path` for file and directory manipulations. Avoid raw string concatenation.
* **Resolving Paths:** Use `.resolve()` to normalize paths and handle symlinks, ensuring compatibility between local mounts and the cluster.
* **Project Root:** Use `pyprojroot.here` to anchor paths to the project root:
  ```python
  from pyprojroot.here import here
  import sys
  sys.path = [str(here())]+sys.path
  ```

## 4. Imports
* **Order:** Standard library first, then third-party packages, then local project modules.
* **Consistency:** Maintain the `sys.path` manipulation pattern at the top of scripts to ensure stable imports from the `resources` directory.

## 5. Script Structure
* **Modularity:** Encapsulate logic in a `main()` function.
* **Entry Points:** Use the `if __name__ == "__main__":` block.
* **Arguments:** Use `argparse` for CLI tools.
* **Safety:** Implement a `--dry-run` flag for any script performing destructive operations (file writes, directory moves, git commands).

## 6. Logic & Inline Comments
* **Lowercase & Narrative:** Write internal logic comments in all lowercase without formal punctuation.
* **Block-Style Explanations:** For complex logic, use multi-line comment blocks immediately preceding the code.
* **"Step-by-Step" Flow:** Comments should act like a conversational "pseudocode" overlaying the implementation.
* **Vertical Spacing:** Place a single empty line before a new comment block to separate it from preceding code.

```python
# if we're dealing with a new ic file,
# update the ic novelty and source name
# otherwise, retain the labels already given
if source != 'cerberus':
    temp['source'] = source
    if ref:
        nov = 'Known'
    else:
        nov = 'Novel'
    temp['novelty'] = nov
```

## 7. Error Handling
* Use descriptive, user-friendly error messages in `raise` statements.
* For shell commands, use a wrapper (like `run_cmd`) that captures and reports `stderr` on failure.

## 8. Snakemake
* Whenever possible, use rules already written in `processing/rules`
* In Snakefiles for different tasks and using rules from `processing/rules/*`, name the rule with a unique prefix per file plus the name of the rule from the original file. For instance,
```python
# rule from processing/rules
rule wget:
  run:
    """
    wget {params.link} -O {output.fname}
    """

# rule from a separate Snakefile in folder called "mapping"
use rule wget as mapping_wget with:
```

This is explicitly to enable the chaining of separate `Snakefile`s down the line to aggregate the workflow across different tasks and ensure that the names of the rules are unique

## 9. Change Documentation
* **Changelog:** Maintain a `CHANGELOG.md` in the root directory.
* **Datestamps:** All entries must be datestamped (e.g., `YYYY-MM-DD`).
* **Content:** Document all significant changes, including new features, bug fixes, and architectural shifts, to maintain a clear history of the project's evolution.

## 11. Plotting Preferences
* **Sentence Case:** Use sentence case for all plot titles, axis labels, and legends. Only the first character of the entire string should be uppercase (e.g., "Number of genes per organ model", not "Number Of Genes Per Organ Model"). Exceptions are made for specific acronyms (e.g., "DNA", "RNA"), gene names, or proper nouns (e.g., "GTEx", "Pearson r").
* **Organ Names:** Always use human-readable organ names (with spaces) instead of underscore-separated internal names in final visualizations.
* **Themes:** Prefer the `my_theme()` wrapper from `resources.plotting` for consistent sizing and aesthetics.
* **Rotated Labels:** NEVER use `hjust` when rotating labels by 90 degrees (e.g., `element_text(rotation=90)`). It causes misalignment between the text and the axis ticks. Only use `hjust` for other rotations (like 45 degrees) if explicitly necessary.

## 12. Source Control
* **Syncing:** Always run `git pull` before `git push` to ensure your local branch is up-to-date with remote changes and to resolve potential conflicts early.

## 11. Project Roadmap
The strategic vision and detailed [analysis](analysis) plan for this project are maintained in the Obsidian [vault](vault), mirrored by [processing](processing) task.
* **QTL Mapping Roadmap:** See `vault/qtl_mapping/roadmap.md`
* **Workflow Reference:** See `vault/literature/ramdhani_2020_tensor_decomposition.md` for the underlying methodology.

## 13. Environment Constraints
* **Conda/Execution Environment:** The AI agent does not have access to the environment where the user runs Snakemake workflows (it is hosted on a completely different system). Do not attempt to run or validate the Snakemake workflows locally on the agent's machine, as dependencies like `plotnine` and others are not present.

