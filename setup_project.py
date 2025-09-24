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

import argparse

from template_user.resources.utils import *

d = os.path.dirname(__file__)
CONFIG_FILE = f'{d}/template_user/resources/config.yml'
RESOURCES_FILE = f'{d}/template_user/resources/resources.yml'

def main(dry_run=True,
         resources=None,
         output_resources='template_user/resources/resources.yml'):
    """
    Generate resources.yml with path_map and user list.
    Copies template_user dir for each user.
    Supports dry-run mode for safe testing.

    Parameters
    ----------
    dry_run : bool
        If True, no destructive operations are performed; operations are logged.
    resources : dict | str | None
        Path to resources.yml or a pre-loaded dict.
    output_resources : str | Path | None
        Path to write the generated resources.yml. Defaults to
        'template_user/resources/resources.yml'.
    """
    if not resources: resources = RESOURCES_FILE
    m = load_yml(resources)
    
    # make sure project name has been changed
    proj_name = m['setup_settings']['project_name']
    verify_proj_name(proj_name)
    
    # make sure usernames are unique
    usernames = [i2['username']
        for _, i in m['setup_settings']['users'].items()
        for _, i2 in i.items()]    
    check_setup_usernames(usernames)
    
    # destructive operations
    safe_run("rm -rf .git", dry_run=dry_run)
    safe_run(f"mv ../project_template ../{proj_name}", dry_run=dry_run)

    path_map = generate_path_map(m['setup_settings'], proj_name)
    
    # also add a users list
    users_list = {'users': list(m['setup_settings']['users'].keys())}

    # write path map and users to resources.yml
    if dry_run:
        # return the generated data for testing
        print(f"[DRY-RUN] Would append YAML to {output_resources}")
        dry_run_outputs = {'path_map': path_map, 'users': users_list}
    
    else:
        with Path(output_resources).open('a') as f:
            yaml.dump({'path_map': path_map}, f, default_flow_style=False)
            yaml.dump(users_list, f, default_flow_style=False)
    
    # copy template_user for each user    
    for user_alias in m['setup_settings']['users']:
        dest = Path(user_alias)
        if dry_run:
            print(f"[DRY-RUN] Would copy template_user -> {dest}")
        else:
            shutil.copytree("template_user", dest, dirs_exist_ok=True)

    if dry_run: return dry_run_outputs
    else: return None
    
if __name__ == '__main__':
import argparse
from pathlib import Path
import shutil
import yaml
from template_user.resources.utils import (
    load_yml, verify_proj_name, check_setup_usernames,
    generate_path_map, safe_run
)

def main(dry_run=True, resources=None, output_resources='template_user/resources/resources.yml'):
    """
    Generate resources.yml with path_map and user list.
    Copies template_user dir for each user.
    Supports dry-run mode for safe testing.
    """
    
    m = load_yml(resources)
    
    # make sure project name has been changed
    proj_name = m['setup_settings']['project_name']
    verify_proj_name(proj_name)
    
    # make sure usernames are unique
    usernames = [i2['username']
        for _, i in m['setup_settings']['users'].items()
        for _, i2 in i.items()]    
    check_setup_usernames(usernames)
    
    # destructive operations
    safe_run("rm -rf .git", dry_run=dry_run)
    safe_run(f"mv ../project_template ../{proj_name}", dry_run=dry_run)

    path_map = generate_path_map(m['setup_settings'], proj_name)
    
    # also add a users list
    users_list = {'users': list(m['setup_settings']['users'].keys())}

    # write path map and users to resources.yml
    if dry_run:
        print(f"[DRY-RUN] Would append YAML to {output_resources}")
        return {'path_map': path_map, 'users': users_list}
    else:
        output_resources = Path(output_resources)
        output_resources.parent.mkdir(parents=True, exist_ok=True)
        with output_resources.open('a') as f:
            yaml.dump({'path_map': path_map}, f, default_flow_style=False)
            yaml.dump(users_list, f, default_flow_style=False)

        # copy template_user for each user
        for user_alias in m['setup_settings']['users']:
            dest = Path(user_alias)
            shutil.copytree("template_user", dest, dirs_exist_ok=True)

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set up project directories and resources.yml"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate the setup without making changes"
    )
    parser.add_argument(
        "--resources", type=str, default='template_user/resources/resources.yml',
        help="Path to resources.yml file"
    )
    parser.add_argument(
        "--output", type=str, default='template_user/resources/resources.yml',
        help="Path to write updated resources.yml"
    )

    args = parser.parse_args()
    
    main(dry_run=args.dry_run,
         resources=args.resources,
         output_resources=args.output_resources)