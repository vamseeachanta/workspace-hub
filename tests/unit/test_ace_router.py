"""
ABOUTME: Unit tests for ace CLI routing logic and error paths
ABOUTME: Tests prefix resolution, subprocess delegation, and error handling
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from src.ace.router import (
    ROUTES,
    list_routes,
    resolve_command_argv,
    resolve_repo_python,
    route,
    workspace_root,
)


# ---------------------------------------------------------------------------
# workspace_root
# ---------------------------------------------------------------------------


class TestWorkspaceRoot:
    def test_workspace_root_returns_path(self):
        """workspace_root() returns a Path object."""
        result = workspace_root()
        assert isinstance(result, Path)

    def test_workspace_root_is_directory(self):
        """workspace_root() points to an existing directory."""
        result = workspace_root()
        assert result.is_dir()

    def test_workspace_root_contains_pyproject(self):
        """workspace_root() contains pyproject.toml (workspace-hub root marker)."""
        result = workspace_root()
        assert (result / "pyproject.toml").exists()


# ---------------------------------------------------------------------------
# ROUTES table
# ---------------------------------------------------------------------------


class TestRoutesTable:
    def test_routes_is_non_empty(self):
        """ROUTES must contain at least one entry."""
        assert len(ROUTES) > 0

    def test_routes_contains_dm(self):
        """dm prefix maps to digitalmodel."""
        assert "dm" in ROUTES
        assert ROUTES["dm"]["repo"] == "digitalmodel"

    def test_routes_contains_wed(self):
        """wed prefix maps to worldenergydata."""
        assert "wed" in ROUTES
        assert ROUTES["wed"]["repo"] == "worldenergydata"

    def test_routes_contains_ah(self):
        """ah prefix maps to assethold."""
        assert "ah" in ROUTES
        assert ROUTES["ah"]["repo"] == "assethold"

    def test_each_route_has_required_keys(self):
        """Every route must define repo, command, and description."""
        required_keys = {"repo", "command", "description"}
        for prefix, info in ROUTES.items():
            missing = required_keys - set(info.keys())
            assert not missing, f"Route '{prefix}' missing keys: {missing}"

    def test_route_descriptions_are_non_empty(self):
        """All route descriptions must be non-empty strings."""
        for prefix, info in ROUTES.items():
            assert isinstance(info["description"], str), (
                f"Route '{prefix}' description is not a string"
            )
            assert info["description"].strip(), (
                f"Route '{prefix}' has an empty description"
            )

    def test_route_prefixes_are_lowercase(self):
        """All route prefixes must be lowercase."""
        for prefix in ROUTES:
            assert prefix == prefix.lower(), (
                f"Prefix '{prefix}' contains uppercase characters"
            )


# ---------------------------------------------------------------------------
# resolve_repo_python
# ---------------------------------------------------------------------------


class TestResolveRepoPython:
    def test_returns_path_object(self, tmp_path):
        """resolve_repo_python returns a Path."""
        result = resolve_repo_python(tmp_path)
        assert isinstance(result, Path)

    def test_falls_back_to_sys_executable_when_no_venv(self, tmp_path):
        """Falls back to sys.executable when no .venv is present."""
        result = resolve_repo_python(tmp_path)
        assert result == Path(sys.executable)

    def test_returns_venv_python_when_present(self, tmp_path):
        """Returns .venv/bin/python when it exists."""
        venv_python = tmp_path / ".venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.touch()
        venv_python.chmod(0o755)

        result = resolve_repo_python(tmp_path)
        assert result == venv_python

    def test_returns_venv_python3_when_python_absent(self, tmp_path):
        """Returns .venv/bin/python3 when python3 exists but python does not."""
        venv_python3 = tmp_path / ".venv" / "bin" / "python3"
        venv_python3.parent.mkdir(parents=True)
        venv_python3.touch()
        venv_python3.chmod(0o755)

        result = resolve_repo_python(tmp_path)
        assert result == venv_python3


# ---------------------------------------------------------------------------
# resolve_command_argv
# ---------------------------------------------------------------------------


class TestResolveCommandArgv:
    def _make_route(self, command: str) -> dict:
        return {"repo": "testrepo", "command": command, "description": "test"}

    def test_uses_venv_script_when_present(self, tmp_path):
        """Uses venv-installed script when it exists."""
        command = "mycommand"
        script = tmp_path / ".venv" / "bin" / command
        script.parent.mkdir(parents=True)
        script.touch()
        script.chmod(0o755)

        argv, cwd = resolve_command_argv(self._make_route(command), tmp_path, ["--help"])
        assert argv[0] == str(script)
        assert "--help" in argv
        assert cwd == tmp_path

    def test_uses_repo_script_when_present(self, tmp_path):
        """Uses a script at <repo>/<command> when it exists."""
        command = "mycommand"
        script = tmp_path / command
        script.touch()

        argv, cwd = resolve_command_argv(self._make_route(command), tmp_path, ["arg1"])
        assert argv[0] == str(Path(sys.executable))
        assert argv[1] == str(script)
        assert "arg1" in argv
        assert cwd == tmp_path

    def test_falls_back_to_module_invocation(self, tmp_path):
        """Falls back to `python -m <module>` when no script found."""
        command = "my-command"
        argv, cwd = resolve_command_argv(
            self._make_route(command), tmp_path, ["--version"]
        )
        assert argv[1] == "-m"
        assert argv[2] == "my_command"
        assert "--version" in argv
        assert cwd == tmp_path  # always repo_dir for consistent environment

    def test_hyphen_to_underscore_in_module_name(self, tmp_path):
        """Module fallback converts hyphens to underscores for `python -m`."""
        command = "asset-utils-devtools"
        argv, _ = resolve_command_argv(self._make_route(command), tmp_path, [])
        assert argv[2] == "asset_utils_devtools"

    def test_extra_args_appended(self, tmp_path):
        """Extra args are always appended to the argv list."""
        command = "cmd"
        extra = ["sub", "--flag", "value"]
        argv, _ = resolve_command_argv(self._make_route(command), tmp_path, extra)
        assert argv[-3:] == extra


# ---------------------------------------------------------------------------
# list_routes
# ---------------------------------------------------------------------------


class TestListRoutes:
    def test_list_routes_returns_string(self):
        """list_routes() returns a string."""
        result = list_routes()
        assert isinstance(result, str)

    def test_list_routes_contains_all_prefixes(self):
        """list_routes() output contains every known prefix."""
        result = list_routes()
        for prefix in ROUTES:
            assert prefix in result, f"Prefix '{prefix}' not found in list output"

    def test_list_routes_contains_repo_names(self):
        """list_routes() output contains each repo name."""
        result = list_routes()
        for info in ROUTES.values():
            assert info["repo"] in result

    def test_list_routes_contains_usage_hint(self):
        """list_routes() output includes a usage example."""
        result = list_routes()
        assert "ace" in result.lower()


# ---------------------------------------------------------------------------
# route() — happy path
# ---------------------------------------------------------------------------


class TestRouteHappyPath:
    def test_route_delegates_via_subprocess(self, tmp_path):
        """route() invokes subprocess.run with the correct argv."""
        prefix = list(ROUTES.keys())[0]  # use first route
        repo_name = ROUTES[prefix]["repo"]
        command = ROUTES[prefix]["command"]

        # Stub the repo dir inside tmp_path
        fake_root = tmp_path
        fake_repo_dir = fake_root / repo_name
        fake_repo_dir.mkdir()
        fake_venv_script = fake_repo_dir / ".venv" / "bin" / command
        fake_venv_script.parent.mkdir(parents=True)
        fake_venv_script.touch()
        fake_venv_script.chmod(0o755)

        with (
            patch("src.ace.router.workspace_root", return_value=fake_root),
            patch(
                "src.ace.router.subprocess.run",
                return_value=SimpleNamespace(returncode=0),
            ) as mock_run,
        ):
            result = route(prefix, ["--help"])

        assert result == 0
        called_argv = mock_run.call_args[0][0]
        assert str(fake_venv_script) in called_argv
        assert "--help" in called_argv

    def test_route_returns_subprocess_exit_code(self, tmp_path):
        """route() propagates the subprocess exit code."""
        prefix = list(ROUTES.keys())[0]
        repo_name = ROUTES[prefix]["repo"]
        command = ROUTES[prefix]["command"]

        fake_root = tmp_path
        fake_repo_dir = fake_root / repo_name
        fake_repo_dir.mkdir()
        fake_script = fake_repo_dir / ".venv" / "bin" / command
        fake_script.parent.mkdir(parents=True)
        fake_script.touch()

        with (
            patch("src.ace.router.workspace_root", return_value=fake_root),
            patch(
                "src.ace.router.subprocess.run",
                return_value=SimpleNamespace(returncode=42),
            ),
        ):
            result = route(prefix, [])

        assert result == 42


# ---------------------------------------------------------------------------
# route() — error paths
# ---------------------------------------------------------------------------


class TestRouteErrorPaths:
    def test_unknown_prefix_returns_2(self):
        """Unknown prefix returns exit code 2."""
        result = route("zzz_unknown_prefix", [])
        assert result == 2

    def test_unknown_prefix_prints_to_stderr(self, capsys):
        """Unknown prefix prints an error message to stderr."""
        route("zzz_unknown_prefix", [])
        captured = capsys.readouterr()
        assert "unknown subcommand" in captured.err.lower()
        assert "zzz_unknown_prefix" in captured.err

    def test_missing_repo_dir_returns_3(self, tmp_path):
        """Returns exit code 3 when the repo directory does not exist."""
        prefix = list(ROUTES.keys())[0]

        with patch("src.ace.router.workspace_root", return_value=tmp_path):
            result = route(prefix, [])

        assert result == 3

    def test_missing_repo_dir_prints_to_stderr(self, tmp_path, capsys):
        """Prints a helpful message when the repo directory is absent."""
        prefix = list(ROUTES.keys())[0]

        with patch("src.ace.router.workspace_root", return_value=tmp_path):
            route(prefix, [])

        captured = capsys.readouterr()
        assert "not found" in captured.err.lower() or "submodule" in captured.err.lower()

    def test_command_not_found_returns_4(self, tmp_path):
        """Returns exit code 4 when the resolved command raises FileNotFoundError."""
        prefix = list(ROUTES.keys())[0]
        repo_name = ROUTES[prefix]["repo"]

        fake_root = tmp_path
        (fake_root / repo_name).mkdir()

        with (
            patch("src.ace.router.workspace_root", return_value=fake_root),
            patch(
                "src.ace.router.subprocess.run",
                side_effect=FileNotFoundError("not found"),
            ),
        ):
            result = route(prefix, [])

        assert result == 4

    def test_permission_error_returns_5(self, tmp_path):
        """Returns exit code 5 when subprocess raises PermissionError."""
        prefix = list(ROUTES.keys())[0]
        repo_name = ROUTES[prefix]["repo"]

        fake_root = tmp_path
        (fake_root / repo_name).mkdir()

        with (
            patch("src.ace.router.workspace_root", return_value=fake_root),
            patch(
                "src.ace.router.subprocess.run",
                side_effect=PermissionError("denied"),
            ),
        ):
            result = route(prefix, [])

        assert result == 5


# ---------------------------------------------------------------------------
# route() — known prefixes exist in workspace
# ---------------------------------------------------------------------------


class TestKnownPrefixesInWorkspace:
    """Integration-style checks that known repos actually exist in the workspace."""

    @pytest.mark.parametrize("prefix,info", ROUTES.items())
    def test_repo_dir_present_in_workspace(self, prefix, info):
        """Every registered repo directory exists in the workspace-hub root."""
        root = workspace_root()
        repo_dir = root / info["repo"]
        assert repo_dir.is_dir(), (
            f"Repo '{info['repo']}' for prefix '{prefix}' not found at {repo_dir}. "
            f"Ensure the submodule is checked out."
        )
