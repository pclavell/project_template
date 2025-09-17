################################## README BEFORE USAGE ##################################

# This contains util function for snakemake.


                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############
import pandas as pd

# function to enable the array-like behaviour in snakemake
#  (particularly when there are more start than ending files)
# it is useful for example when we start with replicates and end with a merge by sample

def get_value_from_df(df, target_column, filters, single_output=True):
    """
    Retrieve value(s) from a DataFrame given filtering conditions.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to search in.
    target_column : str
        The column name from which to extract the value(s).
    filters : dict
        Dictionary of conditions to filter the DataFrame by.
        Keys are column names, values are the expected values.
    single_output : bool, optional (default=True)
        - If True, expects exactly one unique value and returns it.
        - If False, returns all unique values as a list (length may vary).

    Returns
    -------
    object or list
        - If single_output=True → a single value (scalar).
        - If single_output=False → a list of one or more values.

    Raises
    ------
    AssertionError
        If single_output=True but the filtered DataFrame does not yield
        exactly one unique value.
    """
    filtered_df = df.copy(deep=True)

    for column, value in filters.items():
        filtered_df = filtered_df.loc[filtered_df[column] == value]

    unique_values = filtered_df[target_column].unique()

    if single_output:
        assert len(unique_values) == 1, (
            f"Expected a single value in column '{target_column}' "
            f"after filtering with {filters}, but got {len(unique_values)}: {unique_values}"
        )
        return unique_values[0]

    # Multiple values allowed → return as list
    return list(unique_values)

def wildcard_log_path(wildcards, rule_name, ext="log", job_id="%j"):
    """
    Generate a log filename including the rule name, all wildcards, and the Slurm job ID.

    Parameters
    ----------
    wildcards : object
        The wildcards object passed to the rule. Each attribute will be included in the filename.
    rule_name : str
        The name of the Snakemake rule.
    ext : str, optional
        File extension for the log file (default is "log").
    job_id : str, optional
        Slurm job ID placeholder (default is "%j"). Can be left empty for non-Slurm logs.

    Returns
    -------
    str
        A string representing the log file path.
    """
    # works with namedtuple (Snakemake wildcards) or SimpleNamespace
    parts = [f"{k}={v}" for k, v in vars(wildcards).items()]
    wc_str = "_".join(parts)
    return str(Path("smk_logs") / f"{rule_name}_{wc_str}_{job_id}.{ext}")
