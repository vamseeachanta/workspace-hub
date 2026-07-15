"""RED contract tests for the retained-FD genesis launcher (issue #3544).

The launcher is intentionally absent in this TDD slice.  These tests pin the
security boundary that the implementation must satisfy; they should remain
red until the launcher and its inline broker are added.
"""

from pathlib import Path
import os
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[3]
LAUNCHER = ROOT / "scripts" / "legal" / "launch_rule_authority_genesis.sh"


def launcher_source() -> str:
    """Return launcher bytes as text, failing clearly while it is unimplemented."""
    assert LAUNCHER.is_file(), f"missing required launcher: {LAUNCHER}"
    return LAUNCHER.read_text(encoding="utf-8")


def run_launcher(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Execute the public launcher; RED until its file exists."""
    assert LAUNCHER.is_file(), f"missing required launcher: {LAUNCHER}"
    merged = os.environ.copy()
    merged.update(env or {})
    return subprocess.run(
        ["/bin/bash", str(LAUNCHER), *args],
        text=True,
        capture_output=True,
        env=merged,
        check=False,
    )


def test_genesis_launcher_is_sole_owner_only_public_entrypoint():
    source = launcher_source()
    assert source.startswith("#!/usr/bin/env bash")
    assert "LEGAL_RULE_OWNER_GENESIS" in source
    assert "GITHUB_ACTIONS" in source
    assert "builtin exec -c" in source
    assert "manage_rule_authority.py" not in source
    assert "genesis-current" in source


def test_outer_bootstrap_uses_retained_no_follow_interpreter_and_launcher_fds():
    source = launcher_source()
    assert "O_NOFOLLOW" in source
    assert "O_RDONLY" in source
    assert "/proc/self/fd/" in source
    assert "--outer-identity-fd" in source
    assert "--outer-bootstrap-sha256" in source
    assert "exec -c" in source
    assert "PATH=" in source


def test_inline_fd_broker_is_isolated_and_stdlib_only():
    source = launcher_source()
    assert 'python3' in source or '/usr/bin/python3' in source
    for flag in ("-I", "-S", "-B", "-c"):
        assert flag in source
    assert "import site" not in source
    assert "PYTHONPATH" not in source
    assert "pip" not in source
    assert "os.execve" in source or "os.execv" in source


@pytest.mark.parametrize(
    "forbidden",
    [
        "< \"$",
        "test -L",
        "readlink",
        "PATH lookup",
        "import rule_authority",
        "secrets.token",
        "os.urandom",
    ],
)
def test_pre_verifier_boundary_has_no_reopen_entropy_or_authority_import(forbidden):
    source = launcher_source()
    assert forbidden not in source


def test_broker_retains_every_private_input_and_never_reopens_pathnames():
    source = launcher_source()
    for token in ("approval", "contract", "execution_manifest", "verifier", "entry"):
        assert token in source
    assert "O_DIRECTORY" in source
    assert "fcntl" in source
    assert "F_GET_SEALS" in source
    assert "MFD_ALLOW_SEALING" in source
    assert "F_SEAL_SEAL" in source
    assert "open(" in source
    assert "open(path" not in source


def test_outer_launcher_argv_preserves_internal_identity_and_canonical_pairs():
    source = launcher_source()
    expected = (
        "--outer-identity-fd",
        "--outer-bootstrap-sha256",
        "genesis-current",
        "--tool-repo",
        "--tool-sha",
        "--out-parent",
    )
    positions = [source.index(item) for item in expected]
    assert positions == sorted(positions)
    assert "ordinary public" not in source


def test_launcher_source_has_no_shell_path_reopen_or_mutable_broker_file():
    source = launcher_source()
    assert "source " not in source
    assert " . " not in source
    assert "$(dirname" not in source
    assert "python -m" not in source
    assert "broker.py" not in source
    assert "PYTHONSTARTUP" not in source


def test_owner_and_actions_gate_rejects_untrusted_processes():
    for env in (
        {"LEGAL_RULE_OWNER_GENESIS": "", "GITHUB_ACTIONS": ""},
        {"LEGAL_RULE_OWNER_GENESIS": "wrong", "GITHUB_ACTIONS": ""},
        {"LEGAL_RULE_OWNER_GENESIS": "operator", "GITHUB_ACTIONS": "true"},
    ):
        result = run_launcher("genesis-current", env=env)
        assert result.returncode != 0
        assert "authority" not in result.stdout.lower()


def test_owner_gate_acceptance_clears_hostile_environment_before_child_exec():
    result = run_launcher(
        "genesis-current",
        "--tool-repo",
        "fixture",
        env={
            "LEGAL_RULE_OWNER_GENESIS": "operator",
            "GITHUB_ACTIONS": "",
            "BASH_ENV": "/tmp/hostile-bash-env",
            "PYTHONPATH": "/tmp/hostile-pythonpath",
            "PYTHONSTARTUP": "/tmp/hostile-python-startup",
            "PATH": "/tmp/hostile-bin",
        },
    )
    assert "hostile" not in result.stdout.lower()
    assert "hostile" not in result.stderr.lower()


def test_subprocess_contract_forwards_internal_identity_and_exact_pairs():
    result = run_launcher(
        "genesis-current",
        "--tool-repo",
        "repo",
        "--tool-sha",
        "a" * 40,
        "--out-parent",
        "/private/output",
        "--outer-identity-fd",
        "9",
        "--outer-bootstrap-sha256",
        "b" * 64,
        env={"LEGAL_RULE_OWNER_GENESIS": "operator"},
    )
    assert result.returncode != 0
    assert "unknown option" not in result.stderr.lower()


def test_pre_verifier_fixture_sentinels_are_not_executed_or_written(tmp_path):
    sentinel = tmp_path / "sentinel"
    hook = tmp_path / "python3"
    hook.write_text(f"#!/bin/sh\nprintf touched > {sentinel}\nexit 99\n", encoding="utf-8")
    hook.chmod(0o700)
    result = run_launcher(
        "genesis-current",
        env={
            "LEGAL_RULE_OWNER_GENESIS": "operator",
            "PATH": str(tmp_path),
            "PYTHONPATH": str(tmp_path),
        },
    )
    assert not sentinel.exists(), result.stderr


def test_unrelated_fd_is_closed_and_private_inputs_are_retained_no_follow(tmp_path):
    target = tmp_path / "approval.json"
    target.write_text("{}\n", encoding="utf-8")
    link = tmp_path / "approval-link.json"
    link.symlink_to(target)
    result = run_launcher(
        "genesis-current",
        "--out-parent",
        str(tmp_path),
        env={"LEGAL_RULE_OWNER_GENESIS": "operator"},
    )
    assert result.returncode != 0
    assert "symlink" in result.stderr.lower() or "follow" in result.stderr.lower()


def test_sealed_memfd_identity_requires_exact_seals_and_readback():
    result = run_launcher("genesis-current", env={"LEGAL_RULE_OWNER_GENESIS": "operator"})
    assert result.returncode != 0
    assert "seal" in result.stderr.lower() or "memfd" in result.stderr.lower()
