import sys
from pathlib import Path
import pytest
from unittest.mock import patch, Mock
import yaml

from template_user.resources import add_new_users

@pytest.fixture
def fake_resources(tmp_path):
    """Helper: build fake resources.yml contents."""
    return {
        "setup_settings": {
            "project_name": "demo_proj",
            "users": {
                "alice": {"local": {"username": "alice", "projects_dir": str(tmp_path)}},
                "bob":   {"mn5":   {"username": "bob"}}
            },
            "mn5_locs": {
                "projects_dir": str(tmp_path / "mn5p"),
                "scratch_dir": str(tmp_path / "scr")
            }
        },
        "users": ["alice", "bob"]  # already existing users
    }

def test_no_new_users_raises(fake_resources):
    # no difference between setup_settings["users"] and users
    with patch.object(add_new_users, 'load_yml', return_value=fake_resources):
        with pytest.raises(ValueError, match="No new users found"):
            add_new_users.main(dry_run=True, resources="fake")

def test_add_new_user_dry_run(fake_resources, tmp_path, monkeypatch):

    # Add an extra "charlie" in setup_settings
    fake_resources["setup_settings"]["users"]["charlie"] = {
        "local": {"username": "charlie", "projects_dir": str(tmp_path / "proj_charlie")}
    }

    monkeypatch.setattr(add_new_users, "load_yml", lambda x: fake_resources)
    monkeypatch.setattr(add_new_users, "generate_path_map", lambda s, p: {"dummy": "map"})
    monkeypatch.setattr(add_new_users, "check_setup_usernames", lambda usernames: None)
    monkeypatch.setattr(add_new_users, "safe_run", lambda cmd, **kwargs: "main")
    outputs = add_new_users.main(dry_run=True, user_dir=tmp_path, resources="fake")

    # We should have one entry for each current user ("alice","bob")
    assert isinstance(outputs, list)
    assert all("user_resources" in o for o in outputs)
    assert all("path_map" in o for o in outputs)
    assert all("users" in o for o in outputs)

    # And it should include the new user in the users list
    assert "charlie" in outputs[0]["users"]["users"]

def test_git_commands_run_for_new_user(tmp_path, fake_resources, monkeypatch):
    fake_resources["setup_settings"]["users"]["charlie"] = {
        "local": {"username": "charlie", "projects_dir": str(tmp_path / "proj_charlie")}
    }

    monkeypatch.setattr(add_new_users, "load_yml", lambda x: fake_resources)
    monkeypatch.setattr(add_new_users, "generate_path_map", lambda *args, **kwargs: {"dummy": "map"})
    monkeypatch.setattr(add_new_users, "check_setup_usernames", lambda usernames: None)
    mock_safe_run = Mock(return_value="main")
    monkeypatch.setattr(add_new_users, "safe_run", mock_safe_run)

    outputs = add_new_users.main(dry_run=True, user_dir=tmp_path, resources="fake")

    # Should have invoked git commands for new user
    git_cmds = [c[0][0] for c in mock_safe_run.call_args_list]
    assert any("git fetch origin" in c for c in git_cmds)
    assert any("git reset --hard" in c for c in git_cmds)
