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

def load_config(config_file=None):
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
        dir = os.path.dirname(__file__)
        config_file = f'{dir}/config.yml'

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
    dir = os.path.dirname(__file__)
    config_file = f'{dir}/resources.yml'
    config = load_config(config_file)
    return config


def load_config_abs(**kwargs):
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
    config = load_config()
    m = get_path_map(**kwargs)
    config = replace_str_dict(config, m)

    return config


def save_mn5_config():
    """
    Save a version of the project configuration with absolute paths for MN5.

    This function generates a copy of the configuration where paths are
    converted to absolute paths suitable for the MN5 environment and saves
    it as `config_mn5.yml` in the `../processing/` directory.

    Returns
    -------
    None
    """
    config = load_config_abs(mn5_config=True)

    dir = os.path.dirname(__file__)
    config_file = f'{dir}/config_mn5.yml'

    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def get_path_map(mn5_config=False):
    """
    Return dictionary of strings to be replaced if username is recognized, otherwise
    use relative paths
    """

    username = getpass.getuser()

    # if for just updating mn5 config
    if mn5_config == True: username = 'template_mn5_user_do_not_remove'

    resources = load_resources()
    print(resources['path_map'][username])    # invalid username
    if username not in resources['path_map'].keys():
        raise ValueError(f'Username {username} not found in ../resources/resources.yml. Add before proceeding')

    else:
        return resources['path_map'][username]



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

def run_cmd(cmd):
    """
    Run a shell command using subprocess and return its output.

    Parameters
    ----------
    cmd : str or list
        Command to run. If a string, it is split safely into arguments.
        If a list, it is passed directly to subprocess.

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
    if isinstance(cmd, str):
        cmd = cmd.split()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error while running command:")
        print(e.stderr)
        raise
