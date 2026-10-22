"""Regression examples for controlled discovery and child-process isolation."""

import os
import subprocess

import yaml
from collector_support import GIT_BINDINGS, REPO, bash_path, collector_env, native_path


def test_solver_roots_are_fixture_owned(tmp_path):
    """Independent truth table: empty roots -> absent; a configured directory -> present.

    No physical coefficient or acceptance threshold is used; discovery semantics
    are specified in scripts/readiness/lib/probe-solvers.sh, output contract.
    """
    workspace = tmp_path / "workspace with spaces"
    workspace.mkdir()
    env = collector_env({"WORKSPACE_HUB": str(workspace), "PATH": "/usr/bin:/bin"})
    def collect():
        result = subprocess.run(
            ["bash", bash_path(REPO / "scripts/readiness/collect-equality.sh"),
             "--stdout", "--machine", "fixture"], env=env, cwd=tmp_path,
            capture_output=True, text=True, check=True,
        )
        return {row["name"]: row for row in
                yaml.safe_load(result.stdout)["dimensions"]["solvers"]}

    assert all(row["status"] == "absent" for row in collect().values())
    installs = native_path(env["TEST_INSTALL_ROOT"])
    (installs / "orcawave").mkdir()
    solvers = collect()
    assert {name: row["status"] for name, row in solvers.items()} == {
        "orcaflex": "absent", "orcawave": "present", "aqwa": "absent", "ansys": "absent"}
    assert solvers["orcawave"]["evidence"] == "root"
    assert not list(workspace.iterdir())


def test_environment_clears_repository_bindings_and_owns_temporary_files(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    env = collector_env({"WORKSPACE_HUB": str(workspace), "PATH": "/usr/bin:/bin",
                         **{name: "unrelated" for name in GIT_BINDINGS}})
    assert not set(GIT_BINDINGS).intersection(env)
    result = subprocess.run(["bash", "-c", 'mktemp; printf "%s" "$HOME"'],
                            env=env, cwd=workspace, capture_output=True,
                            text=True, check=True)
    temporary, home = result.stdout.splitlines()
    assert temporary.startswith(bash_path(tmp_path) + "/")
    assert home.startswith(bash_path(tmp_path) + "/")
    assert not list(workspace.iterdir())
    assert os.environ.get("GIT_DIR") != "unrelated"


def test_installed_sdk_cannot_execute_in_collector_fixture(tmp_path):
    """A synthetic SDK would leave a marker on import; discovery shall not import it."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    marker = tmp_path / "imported"
    (tmp_path / "OrcFxAPI.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n", encoding="utf-8")
    env = collector_env({"WORKSPACE_HUB": str(workspace), "PATH": "/usr/bin:/bin",
                         "PYTHONPATH": str(tmp_path)})
    result = subprocess.run(
        ["bash", bash_path(REPO / "scripts/readiness/collect-equality.sh"),
         "--stdout", "--machine", "fixture"], env=env, cwd=tmp_path,
        capture_output=True, text=True, check=True,
    )
    assert all(row["status"] == "absent" for row in
               yaml.safe_load(result.stdout)["dimensions"]["solvers"])
    assert not marker.exists()


def test_fixture_does_not_require_ambient_temporary_directory(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.delenv("TMPDIR", raising=False)
    env = collector_env({"WORKSPACE_HUB": str(workspace), "PATH": "/usr/bin:/bin"})
    assert native_path(env["TMPDIR"]).is_relative_to(tmp_path)
