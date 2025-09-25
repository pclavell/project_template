# import subprocess
# import yaml
# import pytest
# from pathlib import Path
# import setup_project
#
# # these are not working for w/e reason
# # pytestmark = pytest.mark.slow  # can skip by default
# # @pytest.mark.integration
#
# def run(cmd, cwd):
#     subprocess.run(cmd, cwd=cwd, shell=True, check=True)
#
# def test_setup_project_real(tmp_path):
#
#     user_dir = tmp_path
#     repo_dir = tmp_path / TEMPLATE_PROJECT_NAME
#
#     # --- Git clone this repo to test
#     run("git clone git@github.com:pclavell/project_template.git", cwd=user_dir)
#
#     # # --- Create a fake repo for one user ---
#     # run("git init -b main", cwd=user_dir)
#     # (user_dir / "file.txt").write_text("hello")
#     # run("git add .", cwd=user_dir)
#     # run("git commit --allow-empty -m 'init'", cwd=user_dir)
#
#     # --- Create fake resources.yml ---
#     resources = {
#         "setup_settings": {
#             "project_name": "proj_demo",
#             "users": {
#                 "alice": {"local": {"username": "alice", "projects_dir": str(tmp_path / 'proj_alice')}},
#                 "bob":   {"local": {"username": "bob",   "projects_dir": str(tmp_path / 'proj_bob')}}
#             }
#         }
#     }
#
#     res_file = tmp_path / "resources.yml"
#     with res_file.open("w") as f:
#         yaml.dump(resources, f)
#
#     # --- Run setup_project with dry_run=False ---
#     setup_project.main(dry_run=False, resources=res_file, output_resources=str(tmp_path / "output_resources.yml"))
#
#     # --- Check output_resources.yml was written ---
#     out_res_file = tmp_path / "output_resources.yml"
#     assert out_res_file.exists()
#     content = yaml.safe_load(out_res_file.read_text())
#
#     # Path map should include both users
#     assert "alice" in content["path_map"]
#     assert "bob" in content["path_map"]
#
#     # Users list should include both
#     assert content["users"] == ["alice", "bob"]
#
#     # Template directories should exist in the filesystem
#     for user in ["alice", "bob"]:
#         user_dir_path = tmp_path / user
#         assert user_dir_path.exists()
#         expected_dirs = ['data', 'ref', 'figures', 'metadata']
#         for d in expected_dirs:
#             # metadata dir is under user alias
#             if d == "metadata":
#                 dir_path = user_dir_path / user / "metadata"
#             else:
#                 dir_path = user_dir_path / "proj_demo" / d
#             assert dir_path.parent.exists()  # at least the parent folder exists
