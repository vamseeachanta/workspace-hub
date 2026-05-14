"""Tests for scripts/enforcement/require-plan-approval.sh (#2665 strict-issue mode).

Exercises the script as a subprocess against a tmp git repo so the staged-files
detection and find-newer-than-STATE checks reflect real behavior.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "require-plan-approval.sh"


def _init_repo(tmp_path: Path) -> None:
    """Initialize a minimal git repo with planning skeleton."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "test"], check=True)
    (tmp_path / ".planning").mkdir()
    state = tmp_path / ".planning" / "STATE.md"
    state.write_text("# state\n", encoding="utf-8")
    (tmp_path / ".planning" / "plan-approved").mkdir()
    # Commit so HEAD exists for diff --cached operations
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "-m", "init", "--no-verify"], check=True)


def _run_script(tmp_path: Path, *args: str, env_overrides: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def _stage_impl_file(tmp_path: Path, rel_path: str = "src/app.py", content: str = "print('hi')\n") -> None:
    (tmp_path / rel_path).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / rel_path).write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", rel_path], check=True)


# ────────────────────────────────────────────────────────────────────────────
# Plan-named tests
# ────────────────────────────────────────────────────────────────────────────


def test_require_plan_approval_rejects_unrelated_issue_marker_in_strict_issue_mode(tmp_path):
    """Existing broad pre-commit approval evidence cannot be satisfied by another
    issue marker. Issue A is staged, but marker exists only for issue B → fail.
    """
    _init_repo(tmp_path)
    # Marker for unrelated issue B
    (tmp_path / ".planning" / "plan-approved" / "1111.md").write_text(
        "Issue: #1111\nPlan: docs/plans/foo.md\nApproved by: test\n",
        encoding="utf-8",
    )
    _stage_impl_file(tmp_path, "src/issue_a_impl.py")

    # Strict-issue mode, requiring issue 2222 (not 1111)
    result = _run_script(tmp_path, "--strict", "--require-issue", "2222")

    assert result.returncode == 1, f"expected fail-closed; stdout={result.stdout!r} stderr={result.stderr!r}"
    assert "2222" in result.stdout or "2222" in result.stderr


def test_require_plan_approval_strict_mode_fails_when_issue_mapping_ambiguous(tmp_path):
    """Strict-issue mode without an explicit --require-issue must fail closed
    and tell the user to set it explicitly.
    """
    _init_repo(tmp_path)
    # ANY marker exists (broad approval evidence) — should NOT save us in strict-issue mode
    (tmp_path / ".planning" / "plan-approved" / "5555.md").write_text(
        "Issue: #5555\nPlan: docs/plans/bar.md\nApproved by: test\n",
        encoding="utf-8",
    )
    _stage_impl_file(tmp_path, "src/some_impl.py")

    result = _run_script(
        tmp_path, "--strict",
        env_overrides={"FORCE_PLAN_GATE_STRICT_ISSUE": "1"},
    )
    assert result.returncode == 1
    diagnostic = (result.stdout + result.stderr).lower()
    assert "require-issue" in diagnostic, (
        f"diagnostic should ask for explicit --require-issue; got: {diagnostic!r}"
    )


def test_require_plan_approval_strict_issue_mode_passes_with_matching_marker(tmp_path):
    """Sanity check: strict-issue with --require-issue NNN passes when that
    specific marker exists.
    """
    _init_repo(tmp_path)
    (tmp_path / ".planning" / "plan-approved" / "2665.md").write_text(
        "Issue: #2665\nPlan: docs/plans/2026-05-12-issue-2665-foo.md\n"
        "Approved by: vamsee\nApproval source: cli\n",
        encoding="utf-8",
    )
    _stage_impl_file(tmp_path, "src/kanban.py")

    result = _run_script(tmp_path, "--strict", "--require-issue", "2665")

    assert result.returncode == 0, f"strict + matching marker should pass; stdout={result.stdout!r}"
    assert "PASS" in result.stdout


def test_require_plan_approval_strict_issue_mode_fails_when_only_unrelated_marker_present(tmp_path):
    """The plan's primary defect: broad recent-marker evidence satisfied
    unrelated issue commits. Strict-issue mode must reject.
    """
    _init_repo(tmp_path)
    # Recent marker for unrelated issue
    (tmp_path / ".planning" / "plan-approved" / "9999.md").write_text(
        "Issue: #9999\n", encoding="utf-8",
    )
    _stage_impl_file(tmp_path, "src/different_issue.py")

    result = _run_script(tmp_path, "--strict", "--require-issue", "2665")

    assert result.returncode == 1
    assert "2665" in (result.stdout + result.stderr)


def test_require_plan_approval_advisory_mode_unchanged_by_strict_issue_flag(tmp_path):
    """When --strict is NOT set, advisory mode behavior is unchanged.

    This ensures the new flag doesn't accidentally enforce in advisory contexts.
    """
    _init_repo(tmp_path)
    _stage_impl_file(tmp_path, "src/something.py")

    # No --strict, no markers, just --require-issue → still advisory exit 0
    result = _run_script(tmp_path, "--require-issue", "2665")
    assert result.returncode == 0


def test_require_plan_approval_low_risk_files_skip_gate(tmp_path):
    """Existing low-risk-file behavior (scripts/, docs/, tests/) must keep
    passing without an approval marker.
    """
    _init_repo(tmp_path)
    _stage_impl_file(tmp_path, "scripts/helper.py")  # scripts/ is allow-listed

    result = _run_script(tmp_path, "--strict", "--require-issue", "2665")

    assert result.returncode == 0, "scripts/ files should not need plan approval"
    assert "PASS" in result.stdout
