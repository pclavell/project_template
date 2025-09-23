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

def load_yml(config_file=None):
    """
    Load a YAML configuration file containing project file paths.

    Parameters
    ----------
    config_file : str, optional
        Path to a YAML configuration file. If None, the function defaults
        to `../processing/config.yml` relative to the current script file.

    Returns
    -------
    dict
        Parsed configuration as a dictionary with keys corresponding to
        configuration entries and values as specified in the YAML file.
    """
    if not config_file:
        d = os.path.dirname(__file__)
        config_file = f'{d}/config.yml'

    with open(config_file) as f:
        config = yaml.safe_load(f)

    return config


def load_resources():
    """
    Load the resources YAML file containing global project settings.

    The resources file typically includes items such as color schemes,
    metadata settings, and other shared constants for the project.

    Returns
    -------
    dict
        Parsed resources as a dictionary.
    """
    d = os.path.dirname(__file__)
    config_file = f'{d}/resources.yml'
    config = load_yml(config_file)
    return config

def load_paths():
    """
    Load the relevant prefixes for paths for the current user

    Returns
    -------
    dict
        Parsed resources paths as a dictionary.
    """
    m = load_resources()
    username = getpass.getuser()
    return m[username]

def load_config(**kwargs):
    """
    Load the project configuration with absolute paths applied.

    This function modifies the entries in the configuration so that any
    file paths become absolute paths according to the system or user-specific
    path mapping.

    Parameters
    ----------
    **kwargs : dict
        Arbitrary keyword arguments passed to `get_path_map` to determine
        the system/user-specific path mapping.

    Returns
    -------
    dict
        Configuration dictionary with absolute paths applied.
    """
    config = load_yml()
    m = get_path_map(**kwargs)
    config = replace_str_dict(config, m)

    # replace all paths with their absolute pathss
    # to resolve symlinks
    config = resolve_config_symlinks(config)

    return config

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

def save_mn5_config():
    """
    Save a version of the project configuration with absolute paths for MN5.

    This function generates a copy of the configuration where paths are
    converted to absolute paths suitable for the MN5 environment and saves
    it as `config_mn5.yml` in the `../resources/` directory.

    Returns
    -------
    None
    """
    config = load_config(mn5_config=True)

    d = os.path.dirname(__file__)
    config_file = f'{d}/config_mn5.yml'

    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def get_path_map(mn5_config=False):
    """
    Return dictionary of strings to be replaced if username is recognized, otherwise
    use relative paths
    """

    username = getpass.getuser()

    # if for just updating mn5 config
    if mn5_config == True: username = 'template_user'

    resources = load_resources()

    # this is where I should adjust --- it's not likely that I need to keep both path_maps
    usernames = flatten_list([i.keys() for k, i in resources['path_map'].items()])
    if username not in usernames:
        raise ValueError(f'Username {username} not found in resources.yml. Add before proceeding')

    else:
        return resources[username]



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


def get_user_system_entry_path_map(m, user, system):
    """
    Construct a mapping of placeholder keys to canonical filesystem paths
    for a given user and system within a project configuration.

    Parameters
    ----------
    m : dict
        Project configuration dictionary, typically loaded from YAML.
        Must contain a ``setup_settings`` section with keys:
        - ``project_name`` (str): the project name
        - ``mn5_projects`` (str): base directory for MN5 projects
    user : str
        User identifier (e.g., ``"freese"``). Used to build user-specific paths.
    system : str
        System identifier (e.g., ``"mn5"``, ``"local"``).
        Determines which base path prefix to use.

    Returns
    -------
    dict of str to str
        A mapping from placeholder keys to resolved filesystem paths:

        - ``"{data_dir}"`` → project data directory
        - ``"{ref_dir}"`` → project reference directory
        - ``"{figures_dir}"`` → project figures directory
        - ``"{metadata_dir}"`` → user-specific metadata directory

    Notes
    -----
    - For the ``"mn5"`` system, the path prefix is inferred from
      ``m['setup_settings']['mn5_projects']``.
    - For all other systems, the path prefix is taken from the
      resources.yml dictionary
    - All returned paths are normalized using :class:`pathlib.Path`.
    - Placeholder-style keys (e.g., ``"{data_dir}"``) are used to
      facilitate string substitution elsewhere in the project.

    Examples
    --------
    >>> config = {
    ...     "setup_settings": {
    ...         "project_name": "test_project",
    ...         "mn5_projects": "/mnt/projects"
    ...     }
    ... }
    >>> get_user_system_entry_path_map(config, "freese", "mn5")  # doctest: +ELLIPSIS
    {
        '{data_dir}': '/mnt/projects/test_project/data',
        '{ref_dir}': '/mnt/projects/test_project/ref',
        '{figures_dir}': '/mnt/projects/test_project/figures',
        '{metadata_dir}': '/mnt/projects/test_project/freese/metadata'
    }
    """

    d = {}

    # mn5 paths
    if system == 'mn5':
        pref = f"{m['setup_settings']['mn5_projects']}/{m['setup_settings']['project_name']}"

    # any other path
    else:
        pref = f"{m['setup_settings']['users'][user][system]['path']}/{m['setup_settings']['project_name']}/"

    # print(user)
    # print(system)
    # print(pref)
    # print()

    data_dir = f'{pref}/data/'
    ref_dir = f'{pref}/ref/'
    figures_dir = f'{pref}/figures/'

    # metadata dir is part of the github-stored stuff, so it's separate
    metadata_dir = str(pathlib.Path(f'{pref}/{user}/metadata/'))

    # add all paths to dict
    d[r"\{data_dir\}"] = str(pathlib.Path(data_dir))
    d[r"\{ref_dir\}"] = str(pathlib.Path(ref_dir))
    d[r"\{figures_dir\}"] = str(pathlib.Path(figures_dir))
    d[r"\{metadata_dir\}"] = str(pathlib.Path(metadata_dir))

    return d

def flatten_list(l):
    """
    Flatten a list into 1 dimension.

    Parameters
    ----------
    l : list
    """
    return [j for i in l for j in i]

def check_setup_usernames(m):
    """
    Checks that all usernames in setup_settings in resources.yml
    are unique. Raises a value error if not.

    Parameters
    ----------
    m : dict from load_resources()
    """
    # verify that all usernames are unique, we'll have a problem
    # determining the system if not
    usernames = []
    for user, systems in m['setup_settings']['users'].items():
        for system, system_dict in systems.items():
            if 'username' in system_dict:
                usernames.append(system_dict['username'])
    dupes = [item for item, count in Counter(usernames).items() if count > 1]
    if len(dupes)>0:
        raise ValueError(f'Found duplicated username {dupes}.')

def get_setup_settings_path_maps(m):
    """
    Create dictionaries for resources.yml entries for paths for
    each user / system.

    Parameters
    ----------
    m : dict from load_resources()

    Returns
    -------
    path_map, quick_path_map
        Dictionaries of paths dict['path_map'][system][username];
        dict[username] respectively
    """
    # loop through usernames
    path_map = defaultdict(dict)
    quick_path_map = {}

    for user, systems in m['setup_settings']['users'].items():
        for system, system_dict in systems.items():

            username = system_dict['username']
            path_map[system][username] = get_user_system_entry_path_map(m, user, system)
            quick_path_map[username] = get_user_system_entry_path_map(m, user, system)

    return path_map, quick_path_map
