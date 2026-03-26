from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "skills-curation.sh"


def _write_fake_claude(tmp_path: Path) -> Path:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_claude = fake_bin / "claude"
    fake_claude.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$@\" > \"$CLAUDE_ARGS_FILE\"\n",
        encoding="ascii",
    )
    fake_claude.chmod(fake_claude.stat().st_mode | stat.S_IEXEC)
    return fake_bin


def test_skills_curation_invokes_claude_with_explicit_print_flag(tmp_path: Path) -> None:
    fake_bin = _write_fake_claude(tmp_path)
    args_file = tmp_path / "claude-args.txt"

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["CLAUDE_ARGS_FILE"] = str(args_file)
    env["WORKSPACE_HUB"] = str(REPO_ROOT)

    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert args_file.exists(), "wrapper did not invoke claude"

    args = args_file.read_text(encoding="utf-8").splitlines()
    assert args[:2] == ["--dangerously-skip-permissions", "--print"]
    assert len(args) == 3
    assert "Archive stale skills" in args[2]
    assert ".claude/skills/" in args[2]


def test_skills_curation_dry_run_does_not_invoke_claude(tmp_path: Path) -> None:
    fake_bin = _write_fake_claude(tmp_path)
    args_file = tmp_path / "claude-args.txt"

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["CLAUDE_ARGS_FILE"] = str(args_file)
    env["WORKSPACE_HUB"] = str(REPO_ROOT)

    result = subprocess.run(
        ["bash", str(SCRIPT), "--dry-run"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not args_file.exists(), "dry-run should not invoke claude"
    assert "--print" in result.stdout
    assert "Archive stale skills" in result.stdout
