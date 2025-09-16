from template_user.resources.utils import *
import pathlib

m = load_resources()

# verify that a new project name has been given 
if m['setup_settings']['project_name'] == 'project_template':
    raise ValueError(f'Must provide a new project name in template_user/resources.yml!')
    
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
    

# rename project; immediately remove all git things;
cmd = 'rm -rf .git'
run_cmd(cmd)
cmd = f"mv ../project_template ../{m['setup_settings']['project_name']}"
run_cmd(cmd)

# add path maps to resources.yml 

# loop through usernames
path_map = defaultdict(dict)
quick_path_map = {}

for user, systems in m['setup_settings']['users'].items():
    for system, system_dict in systems.items():
        
        username = system_dict['username']
        path_map[system][username] = get_user_system_entry_path_map(m, user, system)
        quick_path_map[username] = get_user_system_entry_path_map(m, user, system)

# also add template user under the mn5 regime
path_map['mn5']['template_user'] = get_user_system_entry_path_map(m, 'template_user', 'mn5')
quick_path_map['template_user'] = get_user_system_entry_path_map(m, 'template_user', 'mn5')

# write to resources.yml, just append the path_map and quick-access path maps
path_map = {'path_map': dict(path_map)}
with open('template_user/resources/resources.yml', 'a') as f:
        yaml.dump(path_map, f, default_flow_style=False)
        yaml.dump(quick_path_map, f, default_flow_style=False)
        
# make a copy of template user for each user
for user, systems in m['setup_settings']['users'].items():
    cmd = f'cp -r template_user/ {user}'
    run_cmd(cmd)