import sys
from pathlib import Path
import pytest
from unittest.mock import patch
import yaml

path = str(Path(__file__).parent.parent / 'resources')
print(path)
sys.path.append(path)

import utils

@pytest.fixture
def fake_resources():
    return {
        'path_map': {
            'junior_username': {
                 'data_dir': '/test/juney/mounts/projects/kitties_proj/data',
                 'ref_dir': '/test/juney/mounts/projects/kitties_proj/ref',
                 'metadata_dir': '/test/juney/mounts/projects/kitties_proj/junior/metadata',
                 'figures_dir': '/test/juney/mounts/projects/kitties_proj/figures',
                 'random_dir': '/test/juney/bee_fuzz',
                 'projects_dir': '/test/juney/mounts/projects',
                 'scratch_dir': '/test/juney/mounts/scratch'},
            'kiki_username': {
                'data_dir': '/usr/kiki/sshfs/projects/kitties_proj/data',
                'ref_dir': '/usr/kiki/sshfs/projects/kitties_proj/ref',
                'metadata_dir': '/usr/kiki/sshfs/projects/kitties_proj/kiki/metadata',
                'figures_dir': '/usr/kiki/sshfs/projects/kitties_proj/figures',
                'random_dir': '/gpfs/juney/bee_fuzz',
                'projects_dir': '/usr/kiki/sshfs/projects',
                'scratch_dir': '/usr/kiki/sshfs/scratch'},
            'bscjuney': {
                'data_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/data',
                'figures_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/figures',
                'ref_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/ref',
                'metadata_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/juney/metadata',
                'random_dir': '/gpfs/juney/bee_fuzz',
                'projects_dir': '/gpfs/projects/bsc83/',
                'scratch_dir': '/gpfs/scratch/bsc83'},
            'bsckiki': {
                'data_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/data',
                'figures_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/figures',
                'ref_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/ref',
                'metadata_dir': '/gpfs/projects/bsc83/Projects/kitties_proj/kiki/metadata',
                'random_dir': '/gpfs/kiki/chicken',
                'projects_dir': '/gpfs/projects/bsc83/',
                'scratch_dir': '/gpfs/scratch/bsc83'}},
        'setup_settings': {
            'users': {
                'junior': {
                    'local': {
                        'username': 'junior_username',
                        'projects_dir': '/test/juney/mounts/projects',
                        'scratch_dir': '/test/juney/mounts/scratch',
                        'random_dir': '/test/juney/bee_fuzz'},
                    'mn5': {
                        'username': 'bscjuney',
                        'random_dir': '/gpfs/juney/bee_fuzz'}},
                'kiki': {
                    'local': {
                        'username': 'kiki_username',
                        'projects_dir': '/usr/kiki/sshfs/projects',
                        'scratch_dir': '/usr/kiki/sshfs/scratch',
                        'random_dir': '/usr/kiki/chicken'},
                    'mn5': {
                        'username': 'bsckiki',
                        'random_dir': '/gpfs/kiki/chicken'}}},
            'project_name': 'kitties_proj',
            'mn5_locs': {
                'projects_dir': '/gpfs/projects/bsc83/',
                'scratch_dir': '/gpfs/scratch/bsc83/'}
            }}

# def test_load_paths(fake_resources):
#     paths = utils.load_paths(resources=fake_resources, username='user1')
#     assert paths['data_dir'] == '/test/data'
#
# def test_safe_run_dry_run():
#     with patch('template_user.resources.utils.run_cmd') as mock_cmd:
#         utils.safe_run("echo test", dry_run=True)
#         mock_cmd.assert_not_called()  # dry_run=True should not call run_cmd


############# tests for load_yml
def test_load_yml_valid(tmp_path):
    # create a temporary yaml file
    yaml_content = {"foo": "bar", "num": 42}
    yaml_file = tmp_path / "test.yml"
    yaml_file.write_text(yaml.dump(yaml_content))

    # call function
    result = utils.load_yml(yaml_file)

    # check parsed content
    assert result == yaml_content

def test_load_yml_missing(tmp_path):
    # point to a file that doesn’t exist
    missing_file = tmp_path / "nope.yml"

    # check it raises the right error
    with pytest.raises(FileNotFoundError) as excinfo:
        utils.load_yml(missing_file)

    assert "YAML file not found" in str(excinfo.value)

############# tests for load_resources

# resources input as a dict
def test_load_resources_dict_input():
    data = {"foo": "bar"}
    result = utils.load_resources(data)
    assert result is data   # should return the same dict object

def test_load_resources_str_path(tmp_path):
    # create a temporary yaml file
    yaml_file = tmp_path / "resources.yml"
    yaml_file.write_text("foo: bar\n")
    result = utils.load_resources(str(yaml_file))
    assert result == {"foo": "bar"}

def test_load_resources_none(monkeypatch, tmp_path):
    # monkeypatch the RESOURCES_FILE constant to point at a tmp file
    fake_yaml = tmp_path / "fake_resources.yml"
    fake_yaml.write_text("hello: world\n")

    monkeypatch.setattr("utils.RESOURCES_FILE", str(fake_yaml))
    result = utils.load_resources(None)
    assert result == {"hello": "world"}

def test_load_resources_invalid_type():
    with pytest.raises(TypeError):
        utils.load_resources(123)   # not dict, not str, not None


############# tests for load_paths
def test_load_paths_with_username(tmp_path):
    # fake resources dict
    resources = {
        "path_map": {
            "alice": {"data_dir": tmp_path / "data", "ref_dir": tmp_path / "ref"}
        }
    }
    result = utils.load_paths(resources=resources, username="alice")
    assert set(result.keys()) == {"data_dir", "ref_dir"}
    # paths are strings and absolute
    for p in result.values():
        assert Path(p).is_absolute()

def test_load_paths_without_username(monkeypatch, tmp_path):
    fake_user = "bob"
    resources = {
        "path_map": {
            fake_user: {"data_dir": tmp_path / fake_user / "data",
                        "ref_dir": tmp_path / fake_user / "ref"},
            'alice': {"data_dir": tmp_path / 'alice' / "data",
                    "ref_dir": tmp_path / 'alice' / "ref"}
        }
    }
    # patch getpass.getuser
    monkeypatch.setattr("getpass.getuser", lambda: fake_user)
    result = utils.load_paths(resources=resources)
    assert set(result.keys()) == {"data_dir", "ref_dir"}

    # make sure it loaded the correct one
    for k, i in result.items():
        assert f'/{fake_user}/' in i

def test_load_paths_mn5_user(tmp_path):
    resources = {
        "path_map": {
            "mn5_user": {"data_dir": tmp_path / "data", "ref_dir": tmp_path / "ref"},
            "alice": {}
        }
    }
    result = utils.load_paths(resources=resources, mn5_user=True)
    assert set(result.keys()) == {"data_dir", "ref_dir"}

import pytest

def test_load_paths_user_not_found(tmp_path):
    resources = {"path_map": {"alice": {"data_dir": tmp_path / "data"}}}
    with pytest.raises(ValueError):
        utils.load_paths(resources=resources, username="bob")

############# tests for get_path_map
def test_get_path_map_key_format(tmp_path):
    resources = {
        "path_map": {
            "alice": {"data_dir": tmp_path / "data", "ref_dir": tmp_path / "ref"}
        }
    }
    result = utils.get_path_map(resources=resources, username="alice")
    expected_keys = {"./{data_dir}", "./{ref_dir}"}
    assert set(result.keys()) == expected_keys

def test_get_path_map_calls_load_paths(monkeypatch):
    fake_paths = {"path_map": {"alice": {"data_dir": "/test/data"}}}
    result = utils.get_path_map(resources=fake_paths, username="alice")
    assert result == {"./{data_dir}": "/test/data"}


############### construct_templated_paths

def test_construct_templated_paths_basic(tmp_path):
    path_map = {"alice": {}}
    base = tmp_path / "projects"
    proj = "proj1"

    result = utils.construct_templated_paths(path_map, base, "alice_alias", "alice", proj)

    # let's just check if all the correct keys are here;
    # formatting can, and probably will change
    expected = ['data_dir', 'ref_dir', 'figures_dir', 'metadata_dir']
    for k in expected:
        assert k in result['alice'].keys()

def test_preserves_existing_entries(tmp_path):
    path_map = {"alice": {"scratch_dir": "/tmp"}}
    result = utils.construct_templated_paths(path_map, tmp_path, "alias", "alice", "proj")
    assert "scratch_dir" in result["alice"]


def test_other_users_unchanged(tmp_path):
    path_map = {"alice": {}, "bob": {"custom": "/x"}}
    result = utils.construct_templated_paths(path_map, tmp_path, "alias", "alice", "proj")
    assert "custom" in result["bob"]
    assert "data_dir" not in result["bob"]

def test_returns_same_object(tmp_path):
    path_map = {"alice": {}}
    result = utils.construct_templated_paths(path_map, tmp_path, "alias", "alice", "proj")
    assert result is path_map

############# generate_path_map

def test_non_mn5_user(tmp_path):
    custom_dir = str(tmp_path / "custom")
    setup_settings = {
        "users": {
            "alice": {
                "local": {
                    "username": "alice",
                    "projects_dir": str(tmp_path / "projects"),
                    "custom_dir": custom_dir
                }
            }
        }
    }
    proj = "proj1"

    result = utils.generate_path_map(setup_settings, proj)
    alice = result["alice"]

    # preserves custom_dir
    assert alice["custom_dir"] == custom_dir

    # adds templated dirs
    expected = ['data_dir', 'ref_dir', 'figures_dir', 'metadata_dir']
    for k in expected:
        assert k in alice.keys()


def test_mn5_user(tmp_path):
    proj_dir = str(tmp_path / "mn5_projects")
    scratch_dir = str(tmp_path / "scratch")
    setup_settings = {
        "users": {
            "bob": {
                "mn5": {
                    "username": "bob",
                }
            }
        },
        "mn5_locs": {
            "projects_dir": proj_dir,
            "scratch_dir": scratch_dir
        }
    }
    proj = "proj2"

    result = utils.generate_path_map(setup_settings, proj)
    bob = result["bob"]
    mn5_user = result["mn5_user"]

    # mn5 projects_dir is special
    assert bob["projects_dir"] == proj_dir
    assert bob["scratch_dir"] == scratch_dir

    assert 'data_dir' in bob.keys()

    # mn5_user clone exists and matches bob
    assert mn5_user == bob
    assert mn5_user is not bob  # deepcopy


def test_multiple_users_and_isolation(tmp_path):
    setup_settings = {
        "users": {
            "alice": {
                "local": {
                    "username": "alice",
                    "projects_dir": str(tmp_path / "proj_alice"),
                }
            },
            "bob": {
                "mn5": {
                    "username": "bob"
                }
            }
        },
        "mn5_locs": {
            "projects_dir": str(tmp_path / "mn5p"),
            "scratch_dir": str(tmp_path / "scr")
        }
    }
    proj = "proj3"
    result = utils.generate_path_map(setup_settings, proj)

    assert "alice" in result and "bob" in result
    assert "mn5_user" in result
    assert "projects_dir" in result["bob"]

    # only mn5 gets projects and scratch dir auto added
    assert "scratch_dir" not in result["alice"]

def test_overwrites_existing_data_dir(tmp_path):
    old_data_dir = str(tmp_path / "old_data")
    setup_settings = {
        "users": {
            "alice": {
                "local": {
                    "username": "alice",
                    "projects_dir": str(tmp_path / "projects"),
                    "data_dir": old_data_dir
                }
            }
        }
    }
    proj = "proj4"
    result = utils.generate_path_map(setup_settings, proj)
    alice = result["alice"]

    # make sure the data_dir got overwritten
    assert alice["data_dir"] != old_data_dir

def test_all_paths_are_strings(tmp_path):
    setup_settings = {
        "users": {
            "alice": {
                "local": {
                    "username": "alice",
                    "projects_dir": str(tmp_path / "projects")
                }
            }
        }
    }
    proj = "proj5"
    result = utils.generate_path_map(setup_settings, proj)
    assert all(isinstance(v, str) for v in result["alice"].values())


def test_mn5_user_is_deepcopy(tmp_path):
    setup_settings = {
        "users": {
            "bob": {
                "mn5": {
                    "username": "bob"
                }
            }
        },
        "mn5_locs": {
            "projects_dir": str(tmp_path / "mn5proj"),
            "scratch_dir": str(tmp_path / "scr")
        }
    }
    proj = "proj6"
    result = utils.generate_path_map(setup_settings, proj)
    result["mn5_user"]["data_dir"] = "CHANGED"

    # bob should be unaffected
    assert result["bob"]["data_dir"] != "CHANGED"
