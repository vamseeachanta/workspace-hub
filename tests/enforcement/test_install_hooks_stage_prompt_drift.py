from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "install-hooks.sh"
SOURCE_ENV = REPO_ROOT / "scripts" / "enforcement" / "enforcement-env.sh"
SOURCE_DRIFT = REPO_ROOT / "scripts" / "enforcement" / "require-stage-prompt-drift.sh"
SOURCE_REVIEW = REPO_ROOT / "scripts" / "enforcement" / "require-review-on-push.sh"


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    hooks_dir = repo / ".git" / "hooks"
    scripts_dir = repo / "scripts" / "enforcement"
    hooks_dir.mkdir(parents=True)
    scripts_dir.mkdir(parents=True)

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    shutil.copy2(SOURCE_SCRIPT, scripts_dir / "install-hooks.sh")
    shutil.copy2(SOURCE_ENV, scripts_dir / "enforcement-env.sh")
    shutil.copy2(SOURCE_DRIFT, scripts_dir / "require-stage-prompt-drift.sh")
    shutil.copy2(SOURCE_REVIEW, scripts_dir / "require-review-on-push.sh")

    (hooks_dir / "pre-commit").write_text("#!/usr/bin/env bash\nexport PATH=\"$PATH\"\n", encoding="utf-8")
    (hooks_dir / "pre-push").write_text("#!/usr/bin/env bash\nset -euo pipefail\n", encoding="utf-8")
    (hooks_dir / "post-commit").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    return repo


def test_install_hooks_wires_stage_prompt_drift_into_pre_push(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = subprocess.run(
        ["bash", "scripts/enforcement/install-hooks.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    pre_push = (repo / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8")
    assert "require-stage-prompt-drift.sh" in pre_push
    assert "stage prompt drift guard" in pre_push.lower()


def test_install_hooks_dry_run_does_not_modify_pre_push(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    before = (repo / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8")

    result = subprocess.run(
        ["bash", "scripts/enforcement/install-hooks.sh", "--dry-run"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    after = (repo / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8")
    assert after == before
    assert "Would wire stage prompt drift guard into pre-push" in result.stdout


# ── #2128: pre-push chain completeness tests ─────────────────────────────


def test_install_hooks_wires_enforcement_env_into_pre_push(tmp_path: Path) -> None:
    """Pre-push must source enforcement-env after install (#2128)."""
    repo = make_repo(tmp_path)

    result = subprocess.run(
        ["bash", "scripts/enforcement/install-hooks.sh"],
        cwd=repo, check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    pre_push = (repo / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8")
    assert "enforcement-env" in pre_push, (
        f"Pre-push must source enforcement-env, got:\n{pre_push}"
    )


def test_install_hooks_wires_review_on_push_into_pre_push(tmp_path: Path) -> None:
    """Pre-push must invoke require-review-on-push.sh after install (#2128)."""
    repo = make_repo(tmp_path)

    result = subprocess.run(
        ["bash", "scripts/enforcement/install-hooks.sh"],
        cwd=repo, check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    pre_push = (repo / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8")
    assert "require-review-on-push.sh" in pre_push, (
        f"Pre-push must invoke require-review-on-push.sh, got:\n{pre_push}"
    )


def test_install_hooks_pre_push_chain_ordering(tmp_path: Path) -> None:
    """Pre-push chain must be: enforcement-env -> review-gate -> drift-gate (#2128)."""
    repo = make_repo(tmp_path)

    result = subprocess.run(
        ["bash", "scripts/enforcement/install-hooks.sh"],
        cwd=repo, check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr

    pre_push = (repo / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8")
    env_pos = pre_push.find("enforcement-env")
    review_pos = pre_push.find("require-review-on-push.sh")
    drift_pos = pre_push.find("require-stage-prompt-drift.sh")

    assert env_pos != -1, "enforcement-env not found in pre-push"
    assert review_pos != -1, "require-review-on-push.sh not found in pre-push"
    assert drift_pos != -1, "require-stage-prompt-drift.sh not found in pre-push"
    assert env_pos < review_pos < drift_pos, (
        f"Wrong ordering: enforcement-env@{env_pos}, review@{review_pos}, drift@{drift_pos}. "
        f"Expected: enforcement-env < review < drift"
    )


def test_install_hooks_idempotent_pre_push_chain(tmp_path: Path) -> None:
    """Running install-hooks twice must not duplicate pre-push blocks (#2128)."""
    repo = make_repo(tmp_path)

    for _ in range(2):
        result = subprocess.run(
            ["bash", "scripts/enforcement/install-hooks.sh"],
            cwd=repo, check=False, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr

    pre_push = (repo / ".git" / "hooks" / "pre-push").read_text(encoding="utf-8")
    assert pre_push.count("require-review-on-push.sh") == 1, (
        f"require-review-on-push.sh duplicated on re-run:\n{pre_push}"
    )
    assert pre_push.count("require-stage-prompt-drift.sh") == 1, (
        f"require-stage-prompt-drift.sh duplicated on re-run:\n{pre_push}"
    )
