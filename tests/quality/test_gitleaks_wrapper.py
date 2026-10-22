"""Wrapper regressions independent of the availability of Gitleaks.

Expected outcomes are specified by issues 3552 and 4069: explicit configuration,
nonzero status for findings or configuration errors, and no raw match output.
The fake executable records arguments and supplies controlled process statuses;
it does not stand in for the live detection tests.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _wrapper_fixture(tmp_path: Path) -> tuple[Path, dict[str, str], Path]:
    repo = tmp_path / "repository"
    security = repo / "scripts/security"
    security.mkdir(parents=True)
    (repo / "scripts/lib").mkdir()
    (repo / "config").mkdir()
    (repo / "config/tier1-python-repos.txt").write_text("example\n", encoding="utf-8")
    for relative in ["scripts/security/secrets-scan.sh", "scripts/lib/tier1-repos.sh"]:
        shutil.copyfile(ROOT / relative, repo / relative)
    shutil.copyfile(ROOT / ".gitleaks.toml", repo / ".gitleaks.toml")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    tool = bin_dir / "gitleaks"
    tool.write_text(
        '#!/usr/bin/env bash\n'
        'printf "%s\\n" "$@" > "$SCANNER_TEST_ARGUMENTS"\n'
        'echo "raw diagnostic must stay private"\n'
        'echo "raw diagnostic must stay private" >&2\n'
        'exit "$SCANNER_TEST_STATUS"\n',
        encoding="utf-8",
    )
    tool.chmod(0o700)
    argv = tmp_path / "arguments.txt"
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_", "GITLEAKS_", "TIER1_"))}
    env.update({"PATH": str(bin_dir) + os.pathsep + env["PATH"],
                "SCANNER_TEST_ARGUMENTS": str(argv), "SCANNER_TEST_STATUS": "0"})
    return repo, env, argv


def _run_wrapper(repo: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(repo / "scripts/security/secrets-scan.sh"), "--repo", "workspace-hub"],
        capture_output=True, text=True, env=env, check=False,
    )


@pytest.mark.parametrize("status", ["0", "1", "2"])
def test_wrapper_preserves_scan_status_and_withholds_output(tmp_path: Path, status: str) -> None:
    """Zero means clean; finding/error statuses must fail without diagnostic text.

    Exit 1 is the wrapper's explicit --exit-code argument. Exit 2 is an
    independently selected process error to ensure errors cannot become PASS.
    """
    repo, env, _ = _wrapper_fixture(tmp_path)
    env["SCANNER_TEST_STATUS"] = status
    result = _run_wrapper(repo, env)
    assert (result.returncode == 0) == (status == "0")
    output = result.stdout + result.stderr
    assert "raw diagnostic must stay private" not in output
    assert ("RESULT: PASS" in output) == (status == "0")


def test_wrapper_requires_config_before_invoking_scanner(tmp_path: Path) -> None:
    """Missing config must fail even if the detector would otherwise return zero."""
    repo, env, argv = _wrapper_fixture(tmp_path)
    (repo / ".gitleaks.toml").rename(repo / "withheld.toml")
    result = _run_wrapper(repo, env)
    assert result.returncode != 0
    assert "configuration" in result.stderr.lower()
    assert not argv.exists()


def test_wrapper_supplies_config_history_mode_and_full_redaction(tmp_path: Path) -> None:
    """Command contract: pinned README redaction and existing history invocation."""
    repo, env, argv = _wrapper_fixture(tmp_path)
    assert _run_wrapper(repo, env).returncode == 0
    args = argv.read_text(encoding="utf-8").splitlines()
    assert args == ["detect", "--source", str(repo), "--config", str(repo / ".gitleaks.toml"),
                    "--exit-code", "1", "--redact=100"]


def test_wrapper_malformed_config_error_cannot_pass(tmp_path: Path) -> None:
    """Simulate the parser's nonzero exit; real parsing has a separate live test."""
    repo, env, argv = _wrapper_fixture(tmp_path)
    (repo / ".gitleaks.toml").write_text("[extend\n", encoding="utf-8")
    env["SCANNER_TEST_STATUS"] = "2"
    result = _run_wrapper(repo, env)
    assert result.returncode != 0
    assert "RESULT: PASS" not in result.stdout
    args = argv.read_text(encoding="utf-8").splitlines()
    assert args[args.index("--config") + 1] == str(repo / ".gitleaks.toml")


def test_wrapper_preserves_baseline_argument(tmp_path: Path) -> None:
    repo, env, argv = _wrapper_fixture(tmp_path)
    quality = repo / "config/quality"
    quality.mkdir()
    baseline = quality / "secrets-baseline-workspace-hub.json"
    baseline.write_text("[]\n", encoding="utf-8")
    assert _run_wrapper(repo, env).returncode == 0
    args = argv.read_text(encoding="utf-8").splitlines()
    assert args[args.index("--baseline-path") + 1] == str(baseline)


@pytest.mark.skipif(shutil.which("gitleaks") is None,
                    reason="NOT_EVALUATED: gitleaks binary absent; real parser required")
def test_wrapper_rejects_malformed_config_with_real_gitleaks(tmp_path: Path) -> None:
    repo, env, _ = _wrapper_fixture(tmp_path)
    # Use the real executable, not the argument-recording stand-in.
    env["PATH"] = os.environ["PATH"]
    git_env = {key: value for key, value in env.items() if not key.startswith("GIT_")}
    subprocess.run(["git", "init", "--quiet", str(repo)], env=git_env,
                   capture_output=True, check=True)
    (repo / ".gitleaks.toml").write_text("[extend\n", encoding="utf-8")
    result = _run_wrapper(repo, env)
    assert result.returncode != 0
    assert "RESULT: PASS" not in result.stdout
    assert "[extend" not in result.stdout + result.stderr
