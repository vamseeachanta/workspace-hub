from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_STATUS = REPO_ROOT / "scripts" / "enforcement" / "stage-prompt-drift-status.sh"
SOURCE_DRIFT = REPO_ROOT / "scripts" / "enforcement" / "require-stage-prompt-drift.sh"


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    hooks_dir = repo / ".git" / "hooks"
    scripts_dir = repo / "scripts" / "enforcement"
    hooks_dir.mkdir(parents=True)
    scripts_dir.mkdir(parents=True)

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    shutil.copy2(SOURCE_STATUS, scripts_dir / "stage-prompt-drift-status.sh")
    shutil.copy2(SOURCE_DRIFT, scripts_dir / "require-stage-prompt-drift.sh")
    return repo


def run_status(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "scripts/enforcement/stage-prompt-drift-status.sh"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def test_status_reports_active_when_hook_and_script_are_present(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / ".git" / "hooks" / "pre-push").write_text(
        "#!/usr/bin/env bash\n"
        "STAGE_PROMPT_DRIFT_GATE=\"$PWD/scripts/enforcement/require-stage-prompt-drift.sh\"\n"
        "bash \"$STAGE_PROMPT_DRIFT_GATE\"\n",
        encoding="utf-8",
    )

    result = run_status(repo)

    assert result.returncode == 0
    assert "stage-prompt-drift guard status: ACTIVE" in result.stdout
    assert "guard script present: yes" in result.stdout
    assert "pre-push hook present: yes" in result.stdout
    assert "pre-push references guard: yes" in result.stdout


def test_status_reports_inactive_when_pre_push_hook_is_missing(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = run_status(repo)

    assert result.returncode == 1
    assert "stage-prompt-drift guard status: INACTIVE" in result.stdout
    assert "pre-push hook present: no" in result.stdout
    assert "pre-push references guard: no" in result.stdout
    assert "remediation: run bash scripts/enforcement/install-hooks.sh" in result.stdout


def test_status_reports_inactive_when_hook_does_not_reference_guard(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / ".git" / "hooks" / "pre-push").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")

    result = run_status(repo)

    assert result.returncode == 1
    assert "pre-push hook present: yes" in result.stdout
    assert "pre-push references guard: no" in result.stdout


def test_status_reports_inactive_when_guard_script_is_missing(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo / ".git" / "hooks" / "pre-push").write_text(
        "#!/usr/bin/env bash\n"
        "bash scripts/enforcement/require-stage-prompt-drift.sh\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "enforcement" / "require-stage-prompt-drift.sh").unlink()

    result = run_status(repo)

    assert result.returncode == 1
    assert "guard script present: no" in result.stdout
    assert "pre-push references guard: yes" in result.stdout
