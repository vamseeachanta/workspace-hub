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
    # The fixture pre-push must carry the extension point. install-hooks.sh no
    # longer appends past the end of the file: appended blocks land below the
    # terminal exit and never run, which is what #3781 was. It now INSERTS at
    # this marker and refuses outright when the marker is absent, so a
    # sentinel-less fixture exercises the refusal path, not the wiring path.
    # The refusal itself is covered by
    # tests/hooks/test_install_hooks_extension_point.py::test_refuses_without_sentinel.
    (hooks_dir / "pre-push").write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "OVERALL_EXIT=0\n"
        "# <<INSTALL_HOOKS_EXTENSION_POINT>>\n"
        "\n"
        'exit "$OVERALL_EXIT"\n',
        encoding="utf-8",
    )
    (hooks_dir / "post-commit").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    return repo


def test_install_hooks_leaves_stage_prompt_drift_to_ci(tmp_path: Path) -> None:
    """The drift guard must NOT be wired into pre-push (#3781).

    Renamed from ...wires_stage_prompt_drift_into_pre_push: it now asserts the
    opposite, and a test whose name contradicts its assertion is worse than no
    test at all.
    """
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
    # Inverted deliberately (#3781). The stage-prompt drift guard is NOT wired
    # into pre-push: .github/workflows/enforcement-gate.yml already enforces it,
    # and the checker measured 206s -- a 3.4-minute push gate is the defect
    # #3780 removed. CI owns it; the hook must stay fast.
    assert "require-stage-prompt-drift.sh" not in pre_push, (
        "drift guard re-wired into pre-push; it costs ~206s per push and is "
        "already covered by enforcement-gate.yml"
    )
    assert "require-review-on-push.sh" in pre_push, (
        "the installer must still wire the gates it does own"
    )


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
    # The drift guard is no longer among the wired blocks (#3781); dry-run now
    # reports on the blocks the installer does own.
    assert "Would wire" in result.stdout


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
    """Pre-push chain must be: enforcement-env -> review-gate (#2128, #3781).

    The drift gate was formerly third in this chain; it is now CI-owned.
    """
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
    # drift is CI-owned and intentionally absent from the chain (#3781)
    assert env_pos < review_pos, (
        "enforcement-env must precede the review gate: it exports "
        "REVIEW_GATE_STRICT=1 and the review wrapper defaults it to 0, so a "
        "later source leaves review enforcement advisory (#3781)"
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
    assert pre_push.count("require-stage-prompt-drift.sh") == 0, (
        f"require-stage-prompt-drift.sh duplicated on re-run:\n{pre_push}"
    )
