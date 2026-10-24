"""Regression examples for controlled discovery and child-process isolation."""

import os
import shlex
import subprocess

import yaml
from collector_support import (
    BASH_PATH,
    GIT_BINDINGS,
    REPO,
    bash_path,
    collector_env,
    native_path,
)


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


def test_leading_ambient_interpreter_cannot_receive_sdk_probe(tmp_path):
    """A user interpreter before system directories must never receive SDK imports."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    ambient = tmp_path / "user bin"
    ambient.mkdir()
    marker = tmp_path / "ambient-import"
    for name in ("python", "python3"):
        interpreter = ambient / name
        interpreter.write_text(
            "#!/usr/bin/env bash\n"
            f"touch {shlex.quote(bash_path(marker))}\nexit 0\n", encoding="utf-8")
        interpreter.chmod(0o755)
    env = collector_env({"WORKSPACE_HUB": str(workspace),
                         "PATH": f"{bash_path(ambient)}:{BASH_PATH}"})
    result = subprocess.run(["bash", "-c", "probe_orcaflex; probe_orcaflex_evidence"],
                            env=env, capture_output=True, text=True, check=True)
    assert not marker.exists(), "ambient interpreter received the SDK probe"
    assert result.stdout.splitlines() == ["absent", "absent"]


def test_generator_environment_selects_only_uv_from_native_path(tmp_path, monkeypatch):
    """Native PATH entries are split and converted before entering a Bash PATH."""
    import test_equality_tree_cleanliness as cleanliness

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    ambient = tmp_path / "user bin"
    ambient.mkdir()
    tool = tmp_path / "tool bin"
    tool.mkdir()
    (tool / "uv").touch()
    (tool / "uv.exe").touch()
    native_path_entries = os.environ.get("PATH", "").replace(os.pathsep, ";")
    monkeypatch.setattr(os, "pathsep", ";")
    monkeypatch.setenv("PATH", f"{ambient};{tool};{native_path_entries}")
    env = cleanliness._env(workspace, tmp_path)
    assert env["PATH"].split(":")[1:] == [*BASH_PATH.split(":"), bash_path(tool)]
