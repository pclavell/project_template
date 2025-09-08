import yaml
import os
import sys

# Append resources dir to path
p = os.path.dirname(os.getcwd())+'/resources/'
sys.path.append(p)

from utils import *

# add the GitHub URL to resources to allow for use
# elsewhere in the project
cmd = 'git remote -v'
s = run_cmd(cmd)
s = s.split()[1]
s = s.split(':')[1]
s = s.split('.git')[0]
s = f"http://github.com/{s}"

m = {}
m['gh_url'] = s

d = os.path.dirname(__file__)
with open(f'{d}/resources.yml', 'a') as f:
        yaml.dump(m, f, default_flow_style=False)