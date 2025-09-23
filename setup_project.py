################################## README BEFORE USAGE ##################################

# Set up settings in resources.yml and in the project directory according to what's in resources.yml setup_settings

# Usage: python setup_project.py

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
from collections import defaultdict, Counter

m = load_resources()

# verify that a new project name has been given
if m['setup_settings']['project_name'] == 'project_template':
    raise ValueError(f'Must provide a new project name in template_user/resources.yml!')

# verify that all usernames are unique, we'll have a problem
# determining the system if not
check_setup_usernames(m)

# rename project; immediately remove all git things;
cmd = 'rm -rf .git'
run_cmd(cmd)
cmd = f"mv ../project_template ../{m['setup_settings']['project_name']}"
run_cmd(cmd)

# get paths for each user in setup_settings
path_map = get_setup_settings_path_maps(m)

# also add template user under the mn5 regime
path_map['path_map']['template_user'] = get_user_system_entry_path_map(m, 'template_user', 'mn5')

# also add a users list
users_list = {}
users_list['users'] = list(m['setup_settings']['users'].keys())

# write to resources.yml, just append the path_map and quick-access path maps
path_map = {'path_map': dict(path_map)}
with open('template_user/resources/resources.yml', 'a') as f:
        yaml.dump(path_map, f, default_flow_style=False)
        yaml.dump(quick_path_map, f, default_flow_style=False)

# make a copy of template user for each user
for user, systems in m['setup_settings']['users'].items():
    cmd = f'cp -r template_user/ {user}'
    run_cmd(cmd)
