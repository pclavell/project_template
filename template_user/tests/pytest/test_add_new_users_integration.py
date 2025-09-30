import subprocess
import yaml
import pytest
from pathlib import Path

from template_user.resources import add_new_users

# these are not working for w/e reason
# pytestmark = pytest.mark.slow  # can skip by default
# @pytest.mark.integration

def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, shell=True, check=True)

def test_add_users_real_git(tmp_path):
    # Create fake repo
    user_dir = tmp_path / "alice"
    user_dir.mkdir()
    run("git init -b main", cwd=user_dir)
    (user_dir / "file.txt").write_text("hello")
    run("git add .", cwd=user_dir)
    run("git commit --allow-empty -m 'init'", cwd=user_dir)
    run("git remote add origin git@github.com:fairliereese/extract_explosions_old.git", cwd=user_dir)

    # resources.yml with one current user (alice) and one new (bob)
    resources = {
        "setup_settings": {
            "project_name": "proj1",
            "users": {
                "alice": {"local": {"username": "alice", "projects_dir": "/alice/proj/"}}},
            },
        "users": ['alice']
    }
    res_dir = tmp_path / "alice" / "resources"
    res_dir.mkdir()
    alice_res_file = res_dir / "resources.yml"
    with alice_res_file.open("w") as f:
        yaml.dump(resources, f)

    resources['setup_settings']['users']['bob'] = {"local": {"username": "bob", "projects_dir": "/bobuser/projects/"}}
    res_file = tmp_path / "resources.yml"
    with res_file.open("w") as f:
        yaml.dump(resources, f)

    # Run main with dry_run=False
    add_new_users.main(dry_run=False, user_dir=user_dir, resources=res_file)

    # Check new user dir exists
    new_user_dir = tmp_path / "bob"
    assert new_user_dir.exists()

    # Check resources.yml inside bob got updated with users list
    bob_res_file = new_user_dir / "resources/resources.yml"
    assert bob_res_file.exists()
    content = yaml.safe_load(bob_res_file.read_text())
    assert "users" in content
    assert "bob" in content["users"]

    # make sure that each of the users has the correct directories
    expected = ['data_dir', 'ref_dir', 'figures_dir', 'metadata_dir']
    users = ['bob', 'alice']
    for user in users:
        for k in expected:
            assert k in content['path_map'][user].keys()
