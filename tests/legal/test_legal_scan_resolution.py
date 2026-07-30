"""Pytest wrapper driving the legal-sanity-scan resolver bash tests via git-bash.

TDD group 23 (llm-wiki-acma#299): nested-wins / sibling-fallback /
env-override-wins / not-found exit 2 listing candidates / --all
empty-enumeration exit 2 (+ walk-up and --all env-roots coverage).

Each bash test builds throwaway fixtures (fake git-init'd repos under
mktemp -d) — real repos are never scanned. Skips with a reason when git-bash
is absent.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent

_PROBED: list[str] = []


def _find_bash() -> str | None:
    """Probe for git-bash: the contract-specified locations first, then a
    git-derived / PATH fallback (never WSL's System32 bash)."""
    candidates = [Path(r"C:\Program Files\Git\bin\bash.exe")]
    program_files = os.environ.get("ProgramFiles")
    if program_files:
        candidates.append(Path(program_files) / "Git" / "bin" / "bash.exe")

    # Fallback: derive from the git.exe install root (covers user-level Git
    # installs, e.g. %LOCALAPPDATA%\Programs\Git), then a plain PATH probe.
    git_exe = shutil.which("git")
    if git_exe:
        git_root = Path(git_exe).resolve().parent.parent  # <root>/{cmd,mingw64/bin}/git.exe
        if git_root.name in ("mingw64", "mingw32"):
            git_root = git_root.parent
        candidates.append(git_root / "bin" / "bash.exe")
        candidates.append(git_root / "usr" / "bin" / "bash.exe")
    path_bash = shutil.which("bash")
    if path_bash:
        candidates.append(Path(path_bash))

    for candidate in candidates:
        _PROBED.append(str(candidate))
        # Exclude WSL's bash shim — it is not git-bash.
        if "system32" in str(candidate).lower():
            continue
        if candidate.is_file():
            return str(candidate)
    return None


BASH = _find_bash()

BASH_TESTS = sorted(p.name for p in HERE.glob("test_*.sh"))


def test_bash_tests_present() -> None:
    """The suite must never silently pass because the bash scripts vanished."""
    assert BASH_TESTS, f"no test_*.sh scripts found in {HERE}"


@pytest.mark.parametrize("script", BASH_TESTS)
def test_legal_scan_resolution(script: str) -> None:
    if BASH is None:
        pytest.skip(
            "git-bash not found (probed: " + "; ".join(_PROBED) + ")"
        )
    env = dict(os.environ)
    # Tests manage LEGAL_SCAN_REPO_ROOTS themselves; a stray value from the
    # host environment must not leak in.
    env.pop("LEGAL_SCAN_REPO_ROOTS", None)
    script_posix = (HERE / script).as_posix()
    proc = subprocess.run(
        [BASH, script_posix],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=300,
    )
    assert proc.returncode == 0, (
        f"{script} failed (rc={proc.returncode})\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
    )
    assert "PASS:" in proc.stdout, f"{script} produced no PASS line:\n{proc.stdout}"
