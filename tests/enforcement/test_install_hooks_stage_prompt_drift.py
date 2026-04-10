from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_SCRIPT = REPO_ROOT / "scripts" / "enforcement" / "install-hooks.sh"
SOURCE_ENV = REPO_ROOT / "scripts" / "enforcement" / "enforcement-env.sh"
SOURCE_DRIFT = REPO_ROOT / "scripts" / "enforcement" / "require-stage-prompt-drift.sh"


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
