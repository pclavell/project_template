from pathlib import Path
import yaml

output_resources = '/Users/fairliereese/Desktop/test.yml'
path_map = {'kiki': 'fuzzy', 'junior': 'lovey'}
users_list = ['beans', 'baynz']

with Path(output_resources).open('a') as f:
      f.write('\n')
      yaml.dump({'path_map': path_map}, f, default_flow_style=False)
      yaml.dump(users_list, f, default_flow_style=False)
