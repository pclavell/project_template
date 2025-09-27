import sys
from pathlib import Path
import pytest
from unittest.mock import patch
import yaml

from template_user.resources import utils

# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def fake_resources(tmp_path):
    """Fake resources dict for testing."""
    return {
        "path_map": {
            "alice": {
                "data_dir": "/test/data",
                "ref_dir": "/test/ref"
            }
        }
    }

@pytest.fixture
def fake_config(tmp_path):
    """Fake config dict and file for testing."""
    config_dict = {
        "data_path": "./{data_dir}/file.txt",
        "nested": {"ref_path": "./{ref_dir}/ref.fasta"}
    }
    # Write as yaml file
    config_file = tmp_path / "config.yml"
    with config_file.open("w") as f:
        yaml.dump(config_dict, f)
    return config_dict, config_file

# -------------------------
# Tests
# -------------------------
def test_load_config_with_dict(fake_resources):
    config_dict = {"file": "./{data_dir}/myfile"}
    out = utils.load_config(config=config_dict, resources=fake_resources, username="alice")
    # Placeholders should be replaced
    assert out["file"] == str(Path(fake_resources["path_map"]["alice"]["data_dir"]).resolve() / "myfile")

def test_load_config_with_file(fake_resources, fake_config):
    _, config_file = fake_config
    out = utils.load_config(config=config_file, resources=fake_resources, username="alice")
    assert out["data_path"] == str(Path(fake_resources["path_map"]["alice"]["data_dir"]).resolve() / "file.txt")
    assert out["nested"]["ref_path"] == str(Path(fake_resources["path_map"]["alice"]["ref_dir"]).resolve() / "ref.fasta")

def test_load_config_nested_replacement(fake_resources):
    config_dict = {
        "level1": {"level2": {"file": "./{data_dir}/data.txt"}}
    }
    out = utils.load_config(config=config_dict, resources=fake_resources, username="alice")
    expected = str(Path(fake_resources["path_map"]["alice"]["data_dir"]).resolve() / "data.txt")
    assert out["level1"]["level2"]["file"] == expected

def test_load_config_absolute_paths(fake_resources):
    # Relative paths in config should be resolved to absolute
    config_dict = {"rel": "some/relative/path"}
    out = utils.load_config(config=config_dict, resources=fake_resources, username="alice")
    assert Path(out["rel"]).is_absolute()

def test_load_config_invalid_types():
    # config type
    with pytest.raises(TypeError):
        utils.load_config(config=123, resources={})
    # resources type
    with pytest.raises(TypeError):
        utils.load_config(config={}, resources=123)

def test_load_config_kwargs_forwarding(fake_resources):
    # tests forwarding of kwargs
    config_dict = {"file": "./{data_dir}/myfile"}
    out = utils.load_config(config=config_dict, resources=fake_resources, username="alice")
    expected = str(Path(fake_resources["path_map"]["alice"]["data_dir"]).resolve() / "myfile")
    assert out["file"] == expected

def test_load_config_defaults(tmp_path, monkeypatch):
    """Test that default CONFIG_FILE and RESOURCES_FILE are used."""
    fake_config_file = tmp_path / "config.yml"
    fake_resources_file = tmp_path / "resources.yml"
    config_dict = {"file": "./{data_dir}/myfile"}
    resources_dict = {"path_map": {"alice": {"data_dir": "/test/data"},
                                   "junior": {"data_dir": "/test/junior/data"}}}

    # Write fake files
    with fake_config_file.open("w") as f:
        yaml.dump(config_dict, f)
    with fake_resources_file.open("w") as f:
        yaml.dump(resources_dict, f)

    # Monkeypatch defaults
    monkeypatch.setattr("template_user.resources.utils.CONFIG_FILE", str(fake_config_file))
    monkeypatch.setattr("template_user.resources.utils.RESOURCES_FILE", str(fake_resources_file))

    out = utils.load_config(username="junior")
    assert out["file"] == "/test/junior/data/myfile"
