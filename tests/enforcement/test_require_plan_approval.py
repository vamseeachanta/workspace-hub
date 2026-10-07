"""Retired marker gate remains callable by existing CI/commit consumers."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]

@pytest.mark.parametrize("args", [[], ["--strict"], ["--check"],
    ["--strict", "--require-issue", "2665"], ["--strict-issue"]])
def test_no_marker_blocks_authorized_implementation(tmp_path, args):
    bash = shutil.which("bash")
    if sys.platform == "win32":
        native = Path(os.environ["ProgramFiles"]) / "Git/bin/bash.exe"
        assert native.is_file(), "Native Git Bash is required for Windows hook tests"
        bash = str(native)
    env = dict(os.environ, FORCE_PLAN_GATE_STRICT="1",
               FORCE_PLAN_GATE_STRICT_ISSUE="1")
    result = subprocess.run([bash, str(ROOT / "scripts/enforcement/require-plan-approval.sh"), *args],
                            cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0
    assert "RETIRED" in result.stdout
    assert not (tmp_path / ".planning").exists()
