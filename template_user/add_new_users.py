from pathlib import Path
import re
import os
import sys

script_path = Path.cwd()
user_dir = re.sub(r"/(metadata|processing|analysis)/.*$", "", str(script_path))
sys.path.append(user_dir)

from resources.utils import *

# user carrying out the user addition
curr_user = str(Path(user_dir).name)

# load resources from curr_user to get the 
# current users
m = load_resources()

# list of new users
curr_users = m['users']
new_users = list(set(list(m['setup_settings']['users'].keys()))-set(curr_users))

if len(new_users) == 0: 
    raise ValueError('No new users found. Exiting.')

# verify that all usernames are unique, we'll have a problem 
# determining the system if not
check_setup_usernames(m)

# get paths for each user in setup_settings
path_map, quick_path_map = get_setup_settings_path_maps(m)

# also add template user under the mn5 regime
path_map['mn5']['template_user'] = get_user_system_entry_path_map(m, 'template_user', 'mn5')
quick_path_map['template_user'] = get_user_system_entry_path_map(m, 'template_user', 'mn5')

# also add a users list 
quick_path_map['users'] = list(m['setup_settings']['users'].keys())

# path_map from default dict to normal dict (defaultdict
# doesn't save nicely in yaml)
path_map = {'path_map': dict(path_map)}

# for each current user, update the resources.yml
for user in curr_users:
    
    # load this users' resources to add the new user to
    user_cfg = f'../{user}/resources/resources.yml'
    m = load_config(user_cfg)
    
    # when writing, we now need to overwrite previous entries
    m['path_map'] = path_map

    # quick path map
    for key, item in quick_path_map.items():
        m[key] = item
        
    # rewrite
    with open(user_cfg, 'w') as f:
        yaml.dump(m, f, default_flow_style=False)
        
# for each new user, copy the user's directory that is carrying out 
# the change, and switch to the main branch
curr_user_dir = str(Path(user_dir))
for user in new_users:
    cmd = f"cp -r {curr_user_dir} {user}"
    print(cmd)
    # run_cmd(cmd)
    cmd = "git fetch origin"
    print(cmd)
    # run_cmd(cmd, wd=user)
    cmd = "git reset --hard origin/main"
    print(cmd)
    # run_cmd(cmd, wd=user)