################################## README BEFORE USAGE ##################################

# This file contains functions to interface with the basic setup of the template repo
# Add all the functions you want; a good rule of thumb is if you feel you are copy+pasting
# the same code over and over, make it a function! =)

                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############

# import packages
import yaml
import os
import getpass
import subprocess
import pathlib
from collections import defaultdict, Counter
import copy

d = os.path.dirname(__file__)
CONFIG_FILE = f'{d}/config.yml'
RESOURCES_FILE = f'{d}/resources.yml'
TEMPLATE_PROJECT_NAME = 'project_template'

def load_yml(file):
    """
    Load a YAML file from disk.

    Parameters
    ----------
    file : str | Path
        Path to a YAML file.

    Returns
    -------
    dict
        Parsed YAML contents.
    """
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r") as f:
        return yaml.safe_load(f)


def load_resources(resources=None):
    """
    Load the resources configuration.

    Parameters
    ----------
    resources : str | dict | None
        - str: path to a YAML file
        - dict: pre-loaded resources dictionary (useful for testing)
        - None: defaults to RESOURCES_FILE

    Returns
    -------
    dict
        Parsed resources dictionary.
    """
    if resources is None:
        resources = RESOURCES_FILE

    if isinstance(resources, dict):
        return resources

    if isinstance(resources, str):
        return load_yml(resources)

    raise TypeError(
        f"resources must be a dict, str (path), or None, got {type(resources)}"
    )


def load_paths(resources=None,
               username=None,
               mn5_user=False):
    """
    Load the relevant path mappings for the current user.

    Parameters
    ----------
    resources : str | dict | None
        Path to a resources.yml file, a dict, or None for default RESOURCES_FILE.
    username : str | None
        Username to load paths for. If None, will try system user if fallback is True.
    mn5_user : bool, default False
        If True, force use of the 'mn5_user' paths.

    Returns
    -------
    dict[str, str]
        Mapping of keys (like 'data_dir', 'ref_dir') to absolute paths.
    """
    resources = load_resources(resources)

    if mn5_user:
        username = "mn5_user"
    elif username is None:
        username = getpass.getuser()

    path_map = resources['path_map']

    if username not in path_map:
        raise ValueError(
            f"Username {username} not found in resources. "
            f"Available: {list(path_map.keys())}"
        )

    # normalize all paths as pathlib.Path w/ symlink / relative path resolution
    return {k: str(pathlib.Path(v).resolve()) for k, v in path_map[username].items()}
               
def load_config(config=None, resources=None, **kwargs):
    """
    Load the project configuration with absolute paths applied.

    Parameters
    ----------
    config : str | Path | dict | None
        - str | Path: path to a config.yml file
        - dict: pre-loaded config dictionary (useful for testing)
        - None: defaults to CONFIG_FILE
    resources : str | Path | dict | None
        - str | Path: path to a resources.yml file
        - dict: pre-loaded resources dictionary
        - None: defaults to RESOURCES_FILE
    **kwargs : dict
        Passed to get_path_map (e.g. username, mn5_user, etc.)

    Returns
    -------
    dict
        Configuration dictionary with absolute paths resolved.
    """
    # --- Load config
    if config is None:
        config = CONFIG_FILE
    if isinstance(config, dict):
        config_dict = config
    elif isinstance(config, (str, Path)):
        config_dict = load_yml(config)
    else:
        raise TypeError("config must be dict, str, Path, or None")

    # --- Load path map from resources
    path_map = get_path_map(resources=resources, **kwargs)

    # --- Apply replacements & resolve symlinks
    config_dict = replace_str_dict(config_dict, path_map)
    config_dict = resolve_config_symlinks(config_dict)

    return config_dict
               
def fmt_path_map_key(k: str) -> str:
    """Format a key for placeholder substitution in config files.
       This can be changed if we ever decide to update the format"""
    return f'./{{{k}}}'

def get_path_map(resources=None, **kwargs):
    """
    Generate a dictionary mapping template keys to absolute paths.

    Parameters
    ----------
    resources : str | Path | dict | None
        Path to a resources.yml file, a dict, or None for default RESOURCES_FILE.
    **kwargs
        Passed to load_paths (e.g., username, mn5_user, fallback_to_system_user).

    Returns
    -------
    dict[str, str]
        Mapping of placeholder keys (e.g. './{data_dir}') to absolute path strings.
    """
    paths = load_paths(resources=resources, **kwargs)

    return {fmt_path_map_key(k): str(v) for k, v in paths.items()}
               
def check_setup_usernames(usernames):
    """
    Ensure all usernames are unique.

    Parameters
    ----------
    usernames : list[str]

    Raises
    ------
    ValueError
        If duplicate usernames are found.
    """
    dupes = {u for u, count in Counter(usernames).items() if count > 1}
    if dupes:
        raise ValueError(f"Duplicate usernames found: {sorted(dupes)}")
               
def verify_proj_name(name):
    """
    Ensure the project name is not left as the template default.
    """
    if name == TEMPLATE_PROJECT_NAME:
        raise ValueError(
            f"Invalid project name: {TEMPLATE_PROJECT_NAME!r}. "
            f"Update it in template_user/resources.yml."
        )
               
def construct_templated_paths(path_map, base_path, user_alias, username, proj_name):
    """
    Generate and attach standard project-relative paths.

    Parameters
    ----------
    path_map : dict
        Mapping of usernames to their paths (modified in place).
    base_path : str | Path
        Root path where project directories are created (e.g., projects_dir/Projects).
    user_alias : str
        Name of the user (used for metadata path).
    username : str
        Username key in the path_map.
    proj_name : str
        Project name.

    Returns
    -------
    dict
        Updated path_map with templated directories added for this username.
    """
    base_path = Path(base_path)
    pref = base_path / proj_name

    # standard subdirectories
    subdirs = {
        "data_dir": pref / "data",
        "ref_dir": pref / "ref",
        "figures_dir": pref / "figures",
        "metadata_dir": pref / user_alias / "metadata",
    }

    # store them as Paths
    path_map[username].update(subdirs)

    return path_map
               
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

def generate_path_map(setup_settings, proj_name):
    """
    Build a path map for all users based on setup_settings.

    Parameters
    ----------
    setup_settings : dict
        Dictionary containing 'users' and system-specific locations.
    proj_name : str
        Name of the project.

    Returns
    -------
    dict[str, dict[str, str]]
        path_map with username keys mapping to their paths.
    """
    path_map = defaultdict(dict)

    users = setup_settings.get("users", {})
    mn5_locs = setup_settings.get("mn5_locs", {})

    for user_alias, systems in users.items():
        for system_name, system_info in systems.items():
            username = system_info["username"]
            
            # Start with paths directly supplied in the YAML for *_dir
            for k, v in system_info.items():
                if k.endswith("_dir"):
                    path_map[username][k] = Path(v)

            # Determine project base path
            if system_name == "mn5":
                base_path = Path(mn5_locs["projects_dir"]) / "Projects"
                # also store scratch_dir and projects_dir explicitly
                for k in ["projects_dir", "scratch_dir"]:
                    path_map[username][k] = Path(mn5_locs[k])
            else:
                base_path = Path(system_info["projects_dir"])

            # Add deterministic templated directories
            path_map = construct_templated_paths(
                path_map,
                base_path,
                user_alias,
                username,
                proj_name
            )

            # Optionally add a canonical mn5_user copy
            if system_name == "mn5":
                path_map["mn5_user"] = deepcopy(path_map[username])
                
        # Convert all Path objects to strings (construct_templated_paths still returns Paths)
    path_map_str = {
        user: {k: str(v) for k, v in paths.items()} for user, paths in path_map.items()
    }

    return path_map_str

def resolve_config_symlinks(d):
    """
    Recursively resolve symlinks and relative paths in the
    config dictionary.

    Parameters
    ----------
    d : dict
        Configuration dictionary

    Returns
    -------
    dict
        Configuration dictionary with symlinks and any
        relative paths resolved
    """
    if isinstance(d, dict):
        return {key: resolve_config_symlinks(item) for key, item in d.items()}
    elif isinstance(d, list):
        return [resolve_config_symlinks(item) for item in d]
    elif isinstance(d, str):
        d = str(pathlib.Path(d).resolve())
        return d
    else:
        return d

def replace_str_dict(d, m):
    """
    Recursively replace substrings in all strings within a nested data structure.

    Args:
        d (dict, list, str, or other): The data structure to process. Can be a dictionary,
            list, string, or any other type. Nested dictionaries and lists are supported.
        m (dict): A mapping of substrings to replace, where keys are substrings to find
            and values are the replacements.

    Returns:
        Same type as input `d`: A new data structure with all string occurrences of the
        keys in `m` replaced by their corresponding values. Non-string types are left unchanged.

    Example:
        >>> data = {'path': '/home/user/data', 'files': ['file1.txt', 'file2.txt']}
        >>> mapping = {'/home/user': '/mnt/data'}
        >>> replace_str_dict(data, mapping)
        {'path': '/mnt/data/data', 'files': ['file1.txt', 'file2.txt']}
    """
    if isinstance(d, dict):
        return {k: replace_str_dict(v, m) for k, v in d.items()}
    elif isinstance(d, list):
        return [replace_str_dict(item, m) for item in d]
    elif isinstance(d, str):
        for old, new in m.items():
            d = d.replace(old, new)
        return d
    else:
        return d  # leave numbers, bools, None, etc. untouched

def run_cmd(cmd, wd='.', shell=False):
    """
    Run a shell command using subprocess and return its output.

    Parameters
    ----------
    cmd : str or list
        Command to run. If a string, it is split safely into arguments.
        If a list, it is passed directly to subprocess.
    wd: str
        Directory to run process in
    shell: bool
        Whether to interpret as a shell command or not

    Returns
    -------
    str
        Captured standard output from the command.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a non-zero status, the error message
        and stderr are raised.
    """
    # Split string into args safely
    if isinstance(cmd, str) and not shell:
        cmd = cmd.split()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=wd,
            shell=shell
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error while running command:")
        print(e.stderr)
        raise

def flatten_list(l):
    """
    Flatten a list into 1 dimension.

    Parameters
    ----------
    l : list
    """
    return [j for i in l for j in i]

# Helper wrapper for shell commands
def safe_run(cmd, dry_run=True, **kwargs):
    if dry_run:
        print(f"[DRY-RUN] Would execute: {cmd}")
    else:
        return run_cmd(cmd, **kwargs)