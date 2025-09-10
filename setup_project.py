from template_user.resources.utils import *
import pathlib

m = load_resources()

# for path_map for find and replace
m['path_map'] = {}

# for plain text getters
m2 = {}


# rename project; immediately remove all git things;
cmd = 'rm -rf .git'
run_cmd(cmd)
cmd = f"mv ../project_template ../{m['setup_settings']['project_name']}"
run_cmd(cmd)

# adding path map entries for MN5 location

# data dir, ref dir, and figures dir are shared by all users
pref = f"{m['setup_settings']['mn5_projects']}/{m['setup_settings']['project_name']}"
data_dir = f'{pref}/data/'
ref_dir = f'{pref}/ref/'
figures_dir = f'{pref}/figures/'


def make_user_path_map_entry(username):
    m['path_map'][username] = {}
    m['path_map'][username]["\{data_dir\}"] = str(pathlib.Path(data_dir))
    m['path_map'][username]["\{ref_dir\}"] = str(pathlib.Path(ref_dir))
    m['path_map'][username]["\{figures_dir\}"] = str(pathlib.Path(figures_dir))

    # metadata dir is part of the github-stored stuff, so it's separate
    m['path_map'][username]["\{metadata_dir\}"] = str(pathlib.Path(f'{pref}/{user}/metadata/'))
    
    # these we'll use for all-purpose directory retrieval, but separate from path_map
    m2[username] = {}
    m2[username]["data_dir"] = str(pathlib.Path(data_dir))
    m2[username]["ref_dir"] = str(pathlib.Path(ref_dir))
    m2[username]["figures_dir"] = str(pathlib.Path(figures_dir))

    # metadata dir is part of the github-stored stuff, so it's separate
    m2[username]["metadata_dir"] = str(pathlib.Path(f'{pref}/{user}/metadata/'))

    return m, m2


# loop through usernames
for user, entry in m['setup_settings']['users'].items():
    m, m2 = make_user_path_map_entry(entry['mn5_username'])

# also make one for temp mn5 user
m, m2 = make_user_path_map_entry('template_user')

# adding path map entries for LOCAL location

def make_user_path_map_entry_local(user, username):
    # data dir, ref dir, and figures dir are shared by all users
    pref = f"{m['setup_settings']['users'][user]['local_path']}/{m['setup_settings']['project_name']}/"
    data_dir = f'{pref}/data/'
    ref_dir = f'{pref}/ref/'
    figures_dir = f'{pref}/figures/'

    m['path_map'][username] = {}
    m['path_map'][username]["\{data_dir\}"] = str(pathlib.Path(data_dir))
    m['path_map'][username]["\{ref_dir\}"] = str(pathlib.Path(ref_dir))
    m['path_map'][username]["\{figures_dir\}"] = str(pathlib.Path(figures_dir))
    m['path_map'][username]["\{metadata_dir\}"] = str(pathlib.Path(f'{pref}/{user}/metadata/'))
    
    
    m2[username] = {}
    m2[username]["data_dir"] = str(pathlib.Path(data_dir))
    m2[username]["ref_dir"] = str(pathlib.Path(ref_dir))
    m2[username]["\{figures_dir"] = str(pathlib.Path(figures_dir))
    m2[username]["metadata_dir"] = str(pathlib.Path(f'{pref}/{user}/metadata/'))
    

    return m, m2

# loop through usernames
for user, entry in m['setup_settings']['users'].items():
    m, m2 = make_user_path_map_entry_local(user, entry['local_username'])

# write, just append the path_map and quick-access path maps
m_append = {}
m_append['path_map'] = m['path_map']
with open('template_user/resources/resources.yml', 'a') as f:
        yaml.dump(m_append, f, default_flow_style=False)
        yaml.dump(m2, f, default_flow_style=False)

# make a copy of template user for each user
for user in m['setup_settings']['users']:
    cmd = f'cp -r template_user/ {user}'
    run_cmd(cmd)
