import subprocess
import yaml
import pytest
from pathlib import Path
import pytest

import setup_project

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
                "scratch_dir": str(tmp_path / "scr"),
                "data_dir": str(tmp_path / "data"),
            }
        }
    }

def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, shell=True, check=True)

def test_verify_proj_name_called(monkeypatch, tmp_path, fake_resources):
    monkeypatch.setattr(setup_project, "load_yml", lambda x: fake_resources)
    called = {}
    monkeypatch.setattr(setup_project, "verify_proj_name", lambda name: called.setdefault("called", True))
    monkeypatch.setattr(setup_project, "check_setup_usernames", lambda users: None)
    monkeypatch.setattr(setup_project, "safe_run", lambda cmd, **kwargs: None)
    monkeypatch.setattr(setup_project, "generate_path_map", lambda s, p: {"dummy": "map"})

    setup_project.main(dry_run=True, resources="fake")
    assert called.get("called")

def test_dry_run_returns(monkeypatch, tmp_path, fake_resources):
    monkeypatch.setattr(setup_project, "load_yml", lambda x: fake_resources)
    monkeypatch.setattr(setup_project, "verify_proj_name", lambda name: None)
    monkeypatch.setattr(setup_project, "check_setup_usernames", lambda users: None)
    monkeypatch.setattr(setup_project, "safe_run", lambda cmd, **kwargs: None)
    monkeypatch.setattr(setup_project, "generate_path_map", lambda s, p: {"dummy": "map"})

    output = setup_project.main(dry_run=True, resources="fake")
    assert output["path_map"] == {"dummy": "map"}
    assert "users" in output
    assert "alice" in output["users"]

def test_setup_project_integration_dry_run(monkeypatch, tmp_path, fake_resources):
    # Patch dependencies to avoid actual destructive ops
    monkeypatch.setattr(setup_project, "load_yml", lambda x: fake_resources)
    monkeypatch.setattr(setup_project, "verify_proj_name", lambda name: None)
    monkeypatch.setattr(setup_project, "check_setup_usernames", lambda users: None)

    monkeypatch.setattr(setup_project, "safe_run", lambda cmd, **kwargs: None)
    monkeypatch.setattr(setup_project.shutil, "copytree", lambda src, dst: None)
    monkeypatch.setattr(setup_project, "generate_path_map", lambda s, p: {"dummy": "map"})

    output = setup_project.main(dry_run=True, resources="fake")
    assert output["path_map"] == {"dummy": "map"}
    assert "alice" in output["users"]
