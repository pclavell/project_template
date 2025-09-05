from user1.resources.utils import *
import pathlib

m = load_resources()
m['path_map'] = {}

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

    return m


# loop through usernames
for user, entry in m['setup_settings']['users'].items():
    m = make_user_path_map_entry(entry['mn5_username'])

# also make one for temp mn5 user
m = make_user_path_map_entry('template_mn5_user_do_not_remove')
m['path_map']['template_mn5_user_do_not_remove']


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

    return m

# loop through usernames
for user, entry in m['setup_settings']['users'].items():
    m = make_user_path_map_entry_local(user, entry['local_username'])

# write, just append the path_map
m_append = {}
m_append['path_map'] = m['path_map']
with open('user1/resources/resources.yml', 'a') as f:
        yaml.dump(m_append, f, default_flow_style=False)

# make a copy of template user for each user
for user in m['setup_settings']['users']:
    cmd = f'cp -r user1/ {user}'
    run_cmd(cmd)
