from pyprojroot.here import here
import sys
import pandas as pd
import pathlib
from collections import defaultdict, Counter
import copy


sys.path.append(str(here()))

from resources.utils import *

def check_setup_usernames(usernames):
    """
    Checks that all usernames are unique. 
    Raises a value error if not.

    Parameters
    ----------
    usernames : list of usernames
    """
    dupes = [item for item, count in Counter(usernames).items() if count > 1]
    if len(dupes)>0:
        raise ValueError(f'Found duplicated username {dupes}.')
        
def verify_proj_name(name):
    """
    Checks if name is still the template name
    Raises a value error if it is

    Parameters
    ----------
    name : str
    """
    if name == 'project_template':
        raise ValueError(f'Must provide a new project name in template_user/resources.yml!')

def construct_templated_paths(path_map, path, user, username, proj_name):
    """
    Generate the paths that we can systematically infer
    to make the user input minimal.
    1. all paths relative to the project (ref/, figures/, data/, user/metadata)
    2. for mn5, links to scratch and projects
    
    This implementation, in theory makes this easy for mn5 users,
    while also allowing for use on other systems as well, if the user
    puts all the *_dir paths in their setup
    """
    
    pref = f"{path}/{proj_name}/"

    data_dir = f'{pref}/data/'
    ref_dir = f'{pref}/ref/'
    figures_dir = f'{pref}/figures/'

    # metadata dir is part of the github-stored stuff, so it's separate
    metadata_dir = str(pathlib.Path(f'{pref}/{user}/metadata/'))

    # add all paths to dict
    path_map[username]['data_dir'] = str(pathlib.Path(data_dir))
    path_map[username]['ref_dir'] = str(pathlib.Path(ref_dir))
    path_map[username]['figures_dir'] = str(pathlib.Path(figures_dir))
    path_map[username]['metadata_dir'] = str(pathlib.Path(metadata_dir))
    
    return path_map


def generate_path_map(m, proj_name):
    """
    Parse the setup_settings dictionary.
    
    Returns
    --------
    path_map : dict, {username: [list of paths the user cares about],
                      users: [list of user aliases]}
    """
    
    # create the path map entries automatically
    path_map = defaultdict(dict)
    for user, entry in m['setup_settings']['users'].items():
        for system, entry2 in entry.items():
            # import pdb; pdb.set_trace()

            for k, i in entry2.items():
                if k.endswith('_dir'):
                    path_map[entry2['username']][k] = i
            
            # for both of these, append /Projects/ so we don't have to keep track of both
            # /gpfs/projects/bsc83/ and /gpfs/projects/bsc83/Projects
            if system == 'mn5':
                # for mn5, we record the projects path already in the config
                path = f"{m['setup_settings']['mn5_locs']['projects_dir']}/Projects/"
                # as well as the default projects and scratch dirs
                for mn5_dir in ['projects_dir', 'scratch_dir']:
                    path_map[entry2['username']][mn5_dir] = m['setup_settings']['mn5_locs'][mn5_dir]
            else:
                path = f"{m['setup_settings']['users'][user][system]['projects_dir']}/Projects/"

            # add the templated directories -- ones we know where to find either
            # 1. relative to the project or 
            # 2. based on abs. paths on mn5
            path_map = construct_templated_paths(path_map,
                                      path,
                                      user, 
                                      entry2['username'],
                                      proj_name)
            
            # if mn5, also add all these paths as mn5 user
            if system == 'mn5':
                # import pdb; pdb.set_trace()
                path_map['mn5_user'] = copy.deepcopy(path_map[entry2['username']])
            
    path_map = dict(path_map)

    return path_map

def load_config(config_file=None,
                resources_file=None,
                **kwargs):
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
    config = load_yml(config_file=config_file)
    m = get_path_map(config_file=resources_file, **kwargs)
    config = replace_str_dict(config, m)

    # replace all paths with their absolute pathss
    # to resolve symlinks
    config = resolve_config_symlinks(config)

    return config

def load_paths(config_file=None, username=None, mn5_user=False):
    """
    Load the relevant prefixes for paths for the current user.
    Optionally specify which user / config file to read

    Returns
    -------
    dict
        Parsed resources paths as a dictionary.
    """
    m = load_resources(config_file)
    if mn5_user: username = 'mn5_user'
    elif not username: username = getpass.getuser()
    
    # check if username in the map
    usernames = list(m['path_map'].keys())
    if username not in usernames:
        raise ValueError(f'Username {username} not found in resources.yml. Add before proceeding')
    else:
        return m['path_map'][username]
    
# change this if we ever decide we want to use a different
# format for the things in config.yml
def fmt_path_map_key(k):
    return r'./{'+f'{k}'+r'}'

# get path map should
# 1. user load_paths to get user paths
# 2. transform them into the format that is expected (ie ./{data_dir}; 
# so that this will be auto-replaced
def get_path_map(**kwargs):
    """
    Return dictionary of strings to be replaced 
    """
    paths = load_paths(**kwargs)

    # transform each dir key into format that is expected by config
    paths = dict([(fmt_path_map_key(k), i) for k,i in paths.items()])

    return paths