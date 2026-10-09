"""Tests for the report-only repo hygiene wrapper."""

from __future__ import annotations

import subprocess
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "repo-hygiene-auto-safe.sh"


def test_wrapper_defaults_to_report_only_and_keeps_apply_manual() -> None:
    text = SCRIPT.read_text()

    assert "APPLY=0" in text
    assert "run_hygiene report" in text
    assert "run_hygiene apply" in text
    assert 'if [ "$APPLY" = 1 ]; then' in text
    assert "repo_sync_cleanup_audit.py" in text
    assert "--root" in text
    assert "EXTRA_ARGS" in text
    assert "--caches" not in text


def test_wrapper_syntax_ok() -> None:
    result = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def test_wrapper_default_run_is_report_only_and_runs_sync_audit(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace-hub"
    operations = workspace / "scripts" / "operations"
    cron = workspace / "scripts" / "cron"
    output = tmp_path / "out"
    hygiene_root = tmp_path / "ecosystem"
    operations.mkdir(parents=True)
    cron.mkdir(parents=True)
    hygiene_root.mkdir()
    wrapper = cron / "repo-hygiene-auto-safe.sh"
    wrapper.write_text(SCRIPT.read_text())
    wrapper.chmod(0o755)
    calls = tmp_path / "calls.log"
    workstation = operations / "workstation-hygiene.sh"
    workstation.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {calls}\n"
        "case \"$*\" in *'--apply'*) exit 9;; esac\n"
    )
    workstation.chmod(0o755)
    audit = operations / "repo_sync_cleanup_audit.py"
    audit.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "assert '--root' in sys.argv\n"
        "print(json.dumps({'status': 'OK'}))\n"
    )
    audit.chmod(0o755)

    env = os.environ.copy()
    env.update(
        {
            "WORKSPACE_HUB": str(workspace),
            "REPO_HYGIENE_ROOT": str(hygiene_root),
            "REPO_HYGIENE_AUTO_SAFE_OUTPUT_DIR": str(output),
            "TIMEOUT_BIN": "timeout",
        }
    )
    result = subprocess.run(
        ["bash", str(wrapper)],
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert "mode=report-only" in result.stdout
    assert "--apply" not in calls.read_text()
    assert (output / "latest-report.log").exists()
    assert (output / "latest-repo-sync-cleanup-audit.json").exists()
