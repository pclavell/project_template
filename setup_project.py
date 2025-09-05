from user1.resources.utils import *

# requires you to provide users, usernames, project name
users = ['pclavell', 'freese']
usernames = ['bsc083549', 'bsc083001']
project_name = 'fetal_dev'

# clones this dir
cmd = 'git clone git@github.com:Mele-Lab/project_template.git'

# rename project; immediately remove all git things;
cmd = 'cd project_template'
cmd = 'rm -rf . git'

# adds entries to resources.yml for mn5
m = load_resources()

# make a copy of template user for each user
for user in users:
    cmd = f'cp user1/ {user}/'

# run git init in the different user folders
