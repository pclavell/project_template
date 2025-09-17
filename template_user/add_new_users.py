################################## README BEFORE USAGE ##################################

# Set up settings in resources.yml and in the project directory according to what's in resources.yml setup_settings; selectively add directories and init Git repos for only new users

# Usage: python add_new_users.py

                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############

from template_user.resources.utils import *
import pathlib

m = load_resources()

# list of new users
new_users = list(set(list(m['setup_settings']['users'].keys()))-set(m['users']))

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

# when writing, we now need to overwrite previous entries
path_map = {'path_map': dict(path_map)}
m['path_map'] = path_map

# quick path map
for key, item in quick_path_map.items():
    m[key] = item

# rewrite
with open('template_user/resources/resources.yml', 'w') as f:
    yaml.dump(m, f, default_flow_style=False)
    
# which one was the new user ? copy a preexisting user for them
# idea is to get also the git info 
for user in new_users:
    cmd = f"cp -r {list(m['setup_settings']['users'].keys())[0]} {user}"
    # print(cmd)
    run_cmd(cmd)
    cmd = "git fetch origin"
    run_cmd(cmd, wd=user)
    cmd = "git reset --hard origin/main"
    run_cmd(cmd, wd=user)
