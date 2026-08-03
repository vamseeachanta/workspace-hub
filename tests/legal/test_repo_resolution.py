"""Pytest wrapper for the legal-sanity-scan repo-resolution contract tests.

Runs tests/legal/test_repo_resolution.sh under git-bash (llm-wiki-acma#299).
Skips with a clear reason when no usable bash is available.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).resolve().parent
BASH_SCRIPT = TEST_DIR / "test_repo_resolution.sh"


def _find_bash():
    """Locate git-bash: probe the standard install path, then PATH.

    Avoids C:\\Windows\\System32\\bash.exe (WSL launcher) — it cannot run
    repo-relative scripts without a configured distro.
    """
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    candidates = [
        Path(program_files) / "Git" / "bin" / "bash.exe",
        Path(r"C:\Program Files\Git\bin\bash.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("bash")
    if found and "system32" not in found.lower():
        return found
    return None


def test_repo_resolution_contract():
    bash = _find_bash()
    if bash is None:
        pytest.skip(
            "bash not found (probed '%ProgramFiles%\\Git\\bin\\bash.exe' and "
            "PATH) — cannot run legal-sanity-scan resolution tests"
        )
    result = subprocess.run(
        [bash, str(BASH_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"bash resolution tests failed (exit {result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )
