from pyprojroot.here import here
import sys
import pandas as pd
import pathlib
from collections import defaultdict, Counter
import copy


sys.path.append(str(here()))

from resources.utils import *

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
    dict[str, pathlib.Path]
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
    return {k: pathlib.Path(v).resolve() for k, v in path_map[username].items()}
               
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




               
#                def check_setup_usernames(usernames):
#     """
#     Checks that all usernames are unique. 
#     Raises a value error if not.

#     Parameters
#     ----------
#     usernames : list of usernames
#     """
#     dupes = [item for item, count in Counter(usernames).items() if count > 1]
#     if len(dupes)>0:
#         raise ValueError(f'Found duplicated username {dupes}.')
        
# def verify_proj_name(name):
#     """
#     Checks if name is still the template name
#     Raises a value error if it is

#     Parameters
#     ----------
#     name : str
#     """
#     if name == 'project_template':
#         raise ValueError(f'Must provide a new project name in template_user/resources.yml!')
               
# # change this if we ever decide we want to use a different
# # format for the things in config.yml
# def fmt_path_map_key(k):
#     return r'./{'+f'{k}'+r'}'

# # get path map should
# # 1. user load_paths to get user paths
# # 2. transform them into the format that is expected (ie ./{data_dir}; 
# # so that this will be auto-replaced
# def get_path_map(**kwargs):
#     """
#     Return dictionary of strings to be replaced 
#     """
#     paths = load_paths(**kwargs)

#     # transform each dir key into format that is expected by config
#     paths = dict([(fmt_path_map_key(k), i) for k,i in paths.items()])

#     return paths



               
               
               
# def load_config(config_file=None,
#                 resources_file=None,
#                 **kwargs):
#     """
#     Load the project configuration with absolute paths applied.

#     This function modifies the entries in the configuration so that any
#     file paths become absolute paths according to the system or user-specific
#     path mapping.

#     Parameters
#     ----------
#     **kwargs : dict
#         Arbitrary keyword arguments passed to `get_path_map` to determine
#         the system/user-specific path mapping.

#     Returns
#     -------
#     dict
#         Configuration dictionary with absolute paths applied.
#     """
#     config = load_yml(config_file=config_file)
#     m = get_path_map(config_file=resources_file, **kwargs)
#     config = replace_str_dict(config, m)

#     # replace all paths with their absolute pathss
#     # to resolve symlinks
#     config = resolve_config_symlinks(config)

#     return config

# def load_paths(config_file=None, username=None, mn5_user=False):
#     """
#     Load the relevant prefixes for paths for the current user.
#     Optionally specify which user / config file to read

#     Returns
#     -------
#     dict
#         Parsed resources paths as a dictionary.
#     """
#     m = load_resources(config_file)
#     if mn5_user: username = 'mn5_user'
#     elif not username: username = getpass.getuser()
    
#     # check if username in the map
#     usernames = list(m['path_map'].keys())
#     if username not in usernames:
#         raise ValueError(f'Username {username} not found in resources.yml. Add before proceeding')
#     else:
#         return m['path_map'][username]
    
# # is there a way to make the behavior if a config_file is
# # passed more tight between load_resources and load_yml?
# # maybe chatgpt has some ideas
# def load_resources(config_file=None):
#     """
#     Load the resources YAML file containing global project settings.

#     The resources file typically includes items such as color schemes,
#     metadata settings, and other shared constants for the project.

#     Returns
#     -------
#     dict
#         Parsed resources as a dictionary.
#     """
#     if not config_file:
#         d = os.path.dirname(__file__)
#         config_file = f'{d}/resources.yml'

#     config = load_yml(config_file)
#     return config

# def load_yml(config_file=None):
#     """
#     Load a YAML configuration file containing project file paths.

#     Parameters
#     ----------
#     config_file : str, optional
#         Path to a YAML configuration file. If None, the function defaults
#         to `../processing/config.yml` relative to the current script file.

#     Returns
#     -------
#     dict
#         Parsed configuration as a dictionary with keys corresponding to
#         configuration entries and values as specified in the YAML file.
#     """
#     if not config_file:
#         d = os.path.dirname(__file__)
#         config_file = f'{d}/config.yml'

#     with open(config_file) as f:
#         config = yaml.safe_load(f)

#     return config





# def construct_templated_paths(path_map, path, user, username, proj_name):
#     """
#     Generate the paths that we can systematically infer
#     to make the user input minimal.
#     1. all paths relative to the project (ref/, figures/, data/, user/metadata)
#     2. for mn5, links to scratch and projects
    
#     This implementation, in theory makes this easy for mn5 users,
#     while also allowing for use on other systems as well, if the user
#     puts all the *_dir paths in their setup
#     """
    
#     pref = f"{path}/{proj_name}/"

#     data_dir = f'{pref}/data/'
#     ref_dir = f'{pref}/ref/'
#     figures_dir = f'{pref}/figures/'

#     # metadata dir is part of the github-stored stuff, so it's separate
#     metadata_dir = str(pathlib.Path(f'{pref}/{user}/metadata/'))

#     # add all paths to dict
#     path_map[username]['data_dir'] = str(pathlib.Path(data_dir))
#     path_map[username]['ref_dir'] = str(pathlib.Path(ref_dir))
#     path_map[username]['figures_dir'] = str(pathlib.Path(figures_dir))
#     path_map[username]['metadata_dir'] = str(pathlib.Path(metadata_dir))
    
#     return path_map


# def generate_path_map(m, proj_name):
#     """
#     Parse the setup_settings dictionary.
    
#     Returns
#     --------
#     path_map : dict, {username: [list of paths the user cares about],
#                       users: [list of user aliases]}
#     """
    
#     # create the path map entries automatically
#     path_map = defaultdict(dict)
#     for user, entry in m['setup_settings']['users'].items():
#         for system, entry2 in entry.items():
#             # import pdb; pdb.set_trace()

#             for k, i in entry2.items():
#                 if k.endswith('_dir'):
#                     path_map[entry2['username']][k] = i
            
#             # for both of these, append /Projects/ so we don't have to keep track of both
#             # /gpfs/projects/bsc83/ and /gpfs/projects/bsc83/Projects
#             if system == 'mn5':
#                 # for mn5, we record the projects path already in the config
#                 path = f"{m['setup_settings']['mn5_locs']['projects_dir']}/Projects/"
#                 # as well as the default projects and scratch dirs
#                 for mn5_dir in ['projects_dir', 'scratch_dir']:
#                     path_map[entry2['username']][mn5_dir] = m['setup_settings']['mn5_locs'][mn5_dir]
#             else:
#                 path = f"{m['setup_settings']['users'][user][system]['projects_dir']}"

#             # add the templated directories -- ones we know where to find either
#             # 1. relative to the project or 
#             # 2. based on abs. paths on mn5
#             path_map = construct_templated_paths(path_map,
#                                       path,
#                                       user, 
#                                       entry2['username'],
#                                       proj_name)
            
#             # if mn5, also add all these paths as mn5 user
#             if system == 'mn5':
#                 # import pdb; pdb.set_trace()
#                 path_map['mn5_user'] = copy.deepcopy(path_map[entry2['username']])
            
#     path_map = dict(path_map)

#     return path_map

    





# def save_mn5_config():
#     """
#     Save a version of the project configuration with absolute paths for MN5.

#     This function generates a copy of the configuration where paths are
#     converted to absolute paths suitable for the MN5 environment and saves
#     it as `config_mn5.yml` in the `../resources/` directory.

#     Returns
#     -------
#     None
#     """
#     config = load_config(mn5_config=True)

#     d = os.path.dirname(__file__)
#     config_file = f'{d}/config_mn5.yml'

#     with open(config_file, 'w') as f:
#         yaml.dump(config, f, default_flow_style=False)
