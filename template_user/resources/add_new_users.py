
################################## README BEFORE USAGE ##################################

# This script rewrites the entries in resources.yml with paths for each user,
# finds new users, for each new user copies the user directory from the current
# user, and pulls from main in the new users' directories

#     Usage: python3 add_new_users.py # run from your user's directory!
#                                     # ie <project_name>/<user>

                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############

from pyprojroot.here import here
import sys
import argparse
import shutil
from pathlib import Path

from template_user.resources.utils import *

def main(dry_run=True,
         user_dir=None,
         resources=None):
    """
    Generate resources.yml with path_map and user list.
    Copies user's dir for each NEW user.
    Also initializes git project for each new user,
    and syncs the branch in that directory to HEAD branch
    Supports dry-run mode for safe testing.

    Parameters
    ----------
    dry_run : bool
        If True, no destructive operations are performed; operations are logged.
    user_dir : str
        Path to user's directory
    resources : dict | str | None
        Path to resources.yml or a pre-loaded dict.
    """

    # stuff to return if we're in dry run
    dry_run_outputs = []

    if not resources: resources = RESOURCES_FILE
    m = load_yml(resources)

    proj_name = m['setup_settings']['project_name']

    # if no user dir provided, infer
    user_dir = Path(user_dir) if user_dir else here()
    curr_user = user_dir.name
    project_dir = user_dir.parent.resolve()

    # list of new users
    curr_users = m['users']
    new_users = [u for u in m['setup_settings']['users'] if u not in m['users']]

    if len(new_users) == 0:
        raise ValueError('No new users found. Exiting.')

    # make sure usernames are unique
    usernames = [i2['username']
        for _, i in m['setup_settings']['users'].items()
        for _, i2 in i.items()]
    check_setup_usernames(usernames)

    # also check to make sure that the repo has commit history
    curr_user_dir = user_dir.resolve()
    project_dir = user_dir.parent.resolve()

    # determine head branch of git repo
    cmd = "git remote show origin | sed -n '/HEAD branch/s/.*: //p'"
    head = safe_run(cmd, dry_run=dry_run,
                               wd=curr_user_dir,
                               shell=True)

    # in dry run mode won't have returned anything, just assume main
    if dry_run: head = 'main'
    else: head = head.strip()

    # no remote git history detected
    if head == '(unknown)':
        raise ValueError('No remote git history detected. Please push at least once to remote before adding a user')

    path_map = generate_path_map(m['setup_settings'], proj_name)

    # also add a users list
    users_list = {'users': list(m['setup_settings']['users'].keys())}

    # for each current user, update the resources.yml
    for user_alias in curr_users:

        # load this users' resources to add the new user to
        temp_user_dir = str(Path(f'{project_dir}/{user_alias}').resolve())
        user_resources = str(Path(f'{temp_user_dir}/resources/resources.yml').resolve())

        # write path map and users to resources.yml
        if dry_run:
            # return the generated data for testing
            print(f"[DRY-RUN] Would overwrite YAML to {user_resources}")
            if dry_run:
                dry_run_outputs.append({'user_resources': user_resources,
                                        'path_map': path_map,
                                        'users': users_list})
        else:
            m = load_yml(user_resources)
            # when writing, we now need to overwrite previous entries
            m['path_map'] = path_map
            with Path(user_resources).open('w') as f:
                yaml.dump({'path_map': path_map}, f, default_flow_style=False)
                yaml.dump(users_list, f, default_flow_style=False)

    # for each new user, copy the user's directory that is carrying out
    # the change, and switch to the main branch
    for user_alias in new_users:
        new_user_dir = Path(project_dir) / user_alias


        if not dry_run:
            shutil.copytree(curr_user_dir, new_user_dir)
        else:
            print(f"[DRY-RUN] Would copy {curr_user_dir} -> {new_user_dir}")

        git_cmds = [
            "git fetch origin",
            f"git reset --hard origin/{head}",
            f"git checkout {head}"
        ]

        for cmd in git_cmds:
            safe_run(cmd, dry_run=dry_run, wd=new_user_dir)

    if dry_run: return dry_run_outputs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add new users to project."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulate the setup without making changes"
    )
    parser.add_argument(
        "--resources", type=str,
        help="Path to resources.yml file"
    )
    parser.add_argument(
        "--user_dir", type=str,
        help="User's directory to copy for new users"
    )

    args = parser.parse_args()

    main(dry_run=args.dry_run,
         resources=args.resources,
         user_dir=args.user_dir)
