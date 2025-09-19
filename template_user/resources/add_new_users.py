from pathlib import Path
import re
import os
import sys

from utils import *

m = load_resources()

user_dir = Path.cwd()
curr_user = str(Path(user_dir).name)


# list of new users
curr_users = m['users']
new_users = list(set(list(m['setup_settings']['users'].keys()))-set(curr_users))

if len(new_users) == 0: 
    raise ValueError('No new users found. Exiting.')

# verify that all usernames are unique, we'll have a problem 
# determining the system if not
check_setup_usernames(m)

# also check to make sure that the repo has commit history 
curr_user_dir = str(Path(user_dir).resolve())
project_dir = str(Path(user_dir).parent.resolve())

cmd = "git remote show origin | sed -n '/HEAD branch/s/.*: //p'"
main_branch = run_cmd(cmd, wd=curr_user_dir, shell=True).strip()
if main_branch == '(unknown)':
    raise ValueError('No remote git history detected. Please push at least once to remote before adding a user')

# get paths for each user in setup_settings
path_map, quick_path_map = get_setup_settings_path_maps(m)

# also add template user under the mn5 regime
path_map['mn5']['template_user'] = get_user_system_entry_path_map(m, 'template_user', 'mn5')
quick_path_map['template_user'] = get_user_system_entry_path_map(m, 'template_user', 'mn5')

# also add a users list 
quick_path_map['users'] = list(m['setup_settings']['users'].keys())

# path_map from default dict to normal dict (defaultdict
# doesn't save nicely in yaml)
path_map =  dict(path_map)

# for each current user, update the resources.yml
for user in curr_users:
    
    # load this users' resources to add the new user to
    temp_user_dir = new_user_dir = str(Path(f'{project_dir}/{user}').resolve())
    user_resources = str(Path(f'{temp_user_dir}/resources/resources.yml').resolve())
    print(f'user resources yml: {user_resources}')
    
    m = load_config(user_resources)
    
    # when writing, we now need to overwrite previous entries
    m['path_map'] = path_map

    # quick path map
    for key, item in quick_path_map.items():
        m[key] = item
        
    # rewrite
    with open(user_cfg, 'w') as f:
        yaml.dump(m, f, default_flow_style=False)

new_users = ['test']
main_branch = 'test_branch'

# for each new user, copy the user's directory that is carrying out 
# the change, and switch to the main branch
for user in new_users:
    temp_user_dir = new_user_dir = str(Path(f'{project_dir}/{user}').resolve())
    print(f'current loop user dir: {temp_user_dir}')
        
    cmd = f"cp -r {curr_user_dir} {new_user_dir}"
    print(cmd)
    run_cmd(cmd)
    
    cmd = "git fetch origin"
    print(cmd)
    run_cmd(cmd, wd=new_user_dir)
    
    cmd = "git remote show origin | sed -n '/HEAD branch/s/.*: //p'"
    print(cmd)
    main_branch = run_cmd(cmd, wd=new_user_dir, shell=True).strip()
    
    cmd = f"git reset --hard origin/{main_branch}"
    print(cmd)
    run_cmd(cmd, wd=new_user_dir)
    
    cmd = f"git checkout {main_branch}"
    print(cmd)
    run_cmd(cmd, wd=new_user_dir)
    
    